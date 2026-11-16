import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('builder', Path(__file__).resolve().parents[1] / 'build-knowledge-release.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class KnowledgeBuildTests(unittest.TestCase):
    def test_candidate_requires_explicit_current_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'requires explicit'):
                builder.build(Path(tmp), Path(tmp) / 'new', liuren_runtime=Path(tmp) / 'candidate')

    def test_index_conflicts_encoding_and_complete_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'source'
            def put(name, text, encoding='utf-8'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(text.encode(encoding))
            for name in builder.EXPANDED:
                put(f'.opencode/skills/{name}/SKILL.md', 'original rule\n')
                put(f'books/beihai-xianren/{name}/SKILL.md', 'original rule\nreviewed expansion\n')
            put('.opencode/skills/daliuren/SKILL.md', 'newer mandatory root rules')
            put('案例项目库/_metadata_index.md', '<!-- META: 占类=失物占 | 编号=case-023 | 三传=卯酉 | 日干=丁 | 反馈=验 -->')
            put('案例项目库/失物占/case-023-测试.md', '<!-- META: 占类=失物占 | 三传=卯酉卯 | 反馈=❌ -->\nsource truth')
            put('经验日志/_metadata_index.md', '<!-- META: 文件=提取-大六壬应期断诀窍.md | 类别=古籍提取 -->')
            put('经验日志/提取-大六壬应期断诀窍.md', '# 应期原文\n无首行元数据也必须可发现')
            book = '中文原文\r\n' * 3000 + '最后一字'
            put('书籍库/经典古籍/测试古籍.txt', book, 'gb18030')
            put('书籍库/现代著作/重复.txt', book, 'gb18030')
            put('书籍库/八字书籍/排除.txt', 'out of scope')
            output = Path(tmp) / 'resources'
            m = builder.build(root, output)
            case = next(d for d in m['documents'] if d['kind']=='case')
            self.assertEqual(case['meta']['日干'], '丁')
            self.assertEqual(case['metadataOrigins']['日干'], 'index')
            self.assertEqual(case['meta']['三传'], '卯酉卯')
            self.assertEqual(case['provenance']['feedback'], 'disproved')
            self.assertEqual(len(case['metadataConflicts']), 2)
            parts = [d for d in m['documents'] if d['source'].startswith('书籍库/')]
            self.assertEqual(''.join((output/d['file']).read_bytes().decode() for d in parts), book)
            self.assertEqual(parts[-1]['provenance']['decodedByteEnd'], len(book.encode()))
            self.assertTrue(all(len((output/d['file']).read_bytes())<=6000 for d in parts))
            self.assertEqual(len(m['books']), 1)
            self.assertEqual(m['books'][0]['encoding'], 'gb18030')
            self.assertTrue(any('exact duplicate' in x['reason'] for x in m['excluded']))
            self.assertTrue(any(d['kind']=='reference' and d['source'].startswith('经验日志') for d in m['documents']))
            self.assertEqual((output/'.opencode/skills/daliuren/SKILL.md').read_bytes(), (root/'.opencode/skills/daliuren/SKILL.md').read_bytes())
            with self.assertRaises(FileExistsError): builder.build(root, output)

    def test_unicode_long_line_and_partial_feedback(self):
        text = '😀𠮷\r\n' + '三' * 19000 + '\n尾'
        parts = list(builder.sections(text))
        self.assertEqual(''.join(parts), text)
        self.assertTrue(all(len(p.encode())<=6000 for p in parts))
        self.assertEqual(builder.feedback('**部分验**（耗财验）'), 'partial')

if __name__ == '__main__': unittest.main()
