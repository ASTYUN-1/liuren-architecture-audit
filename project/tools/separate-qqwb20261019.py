"""Copy the reviewed QQ batch into usable and held packages; never edit source."""
import collections
import hashlib
import json
import pathlib
import re
import shutil

SOURCE = pathlib.Path(__file__).resolve().parents[1] / '资料来源/qq-homework-20261018/batch_20261019'
STAGE = SOURCE / 'stage1_ready_v1'
DEST = pathlib.Path(__file__).resolve().parents[1] / 'docs/初级案例整理/初级案例资料/qqwb20261019-分流-20261019'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists():
        raise SystemExit(f'拒绝覆盖已有分流目录：{DEST}')
    manifest = read_json(STAGE / 'analysis_manifest.json')
    records = {r['seq']: r for r in read_jsonl(SOURCE / 'raw/records.jsonl')}
    images = read_jsonl(SOURCE / 'raw/images.jsonl')
    ledger = read_json(STAGE / 'image_ledger.json')
    by_seq = collections.defaultdict(list)
    for image in images:
        by_seq[image['seq']].append(image)
    file_checks, grouped, reason_counts = [], collections.defaultdict(list), collections.Counter()
    grouped_records, grouped_images = collections.defaultdict(list), collections.defaultdict(list)
    all_rows, index_rows = [], []

    def copy(source, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            assert sha(source) == sha(destination), destination
            return
        shutil.copy2(source, destination)
        digest = sha(source)
        assert digest == sha(destination), destination
        file_checks.append({'source': str(source), 'output': destination.relative_to(DEST).as_posix(), 'sha256': digest})

    for original in manifest['cases']:
        row = dict(original)
        seq = int(row['case_id'].rsplit('-', 1)[1]) - 1
        record = records[seq]
        private = read_json(STAGE / row['private_path'])
        chart = read_json(STAGE / row['chart_file'])
        assert sha(STAGE / row['case_file']) == row['case_sha256']
        assert sha(STAGE / row['chart_file']) == row['chart_sha256']
        reasons, details = [], []
        if not row['ready_for_first_analysis']:
            reasons.append('原清单盘面或时间待核')
            details.extend(row['blocking_reasons'])
        if record.get('mofan_kind') != 'mofan' and (row['has_assignment_reference'] or private['逐份作答']):
            reasons.append('题面误作参考作答')
            details.append('作答入口未成功获取，却仍生成逐份作答并标记有作答参考；本包保留原文件供修复，禁止作为学习参照。')
        pans = [i for i in by_seq[seq] if i['type'] == '课盘']
        if len({i.get('time_norm') for i in pans if i.get('time_norm')}) > 1:
            reasons.append('多盘与问题对应未处理')
            details.extend(f"{i['file']}：{i.get('time_norm')}" for i in pans)
        if seq == 180:
            reasons.append('不同事件未拆分')
            details.append('租房与面试是不同事件，当前一份公开包只带一张程序盘。')
        active = [i for i in pans if re.search(r'活时(?:起课|[：:])', i.get('note', ''))]
        if active:
            reasons.append('活时起课约定未传递')
            details.extend(f"{i['file']}：{i['note']}" for i in active)
        solar = [i for i in pans if any('未知' not in segment for segment in re.findall(r'真太阳时[^；。\n]*', i.get('note', '')))]
        if solar:
            reasons.append('真太阳时约定待核')
            details.extend(f"{i['file']}：{i['note']}" for i in solar)
        if seq == 11:
            reasons.append('已确认年柱转录错误')
            details.append('已目视核对 pan/011_1.jpg：年柱乙巳，案例转录为乙丑。')
        if seq == 201:
            reasons.append('已确认程序盘与原图不同')
            details.append('已目视核对 pan/201_1.jpg：活时寅时，原图三传丑卯巳；程序按正时辰时生成亥未丑。')

        held = bool(reasons)
        group = '异常待核' if held else '正常可用'
        root = DEST / group
        if not held:
            assert row['ready_for_first_analysis'] and chart['usable_for_batch_analysis'] and chart['validation']['ok']
            public = read_json(STAGE / row['public_path'])
            assert public['facts'] == chart['facts']
        for field in ['case_file', 'chart_file', 'private_path']:
            copy(STAGE / row[field], root / row[field])
        original_public = row.get('public_path')
        if original_public:
            public_dest = pathlib.Path(original_public)
            if held:
                public_dest = pathlib.Path('analysis-ready/原公开包_禁止调度') / public_dest.name
            copy(STAGE / original_public, root / public_dest)
            row['held_original_public_path'] = public_dest.as_posix() if held else None
        for image in by_seq[seq]:
            copy(SOURCE / image['file'], root / image['file'])
        row['original_ready_for_first_analysis'] = row['ready_for_first_analysis']
        row['ready_for_first_analysis'] = not held
        row['public_path'] = None if held else original_public
        row['分流状态'] = group
        row['异常类别'] = reasons
        row['异常详情'] = details
        row['blocking_reasons'] = details if held else []
        row['source_batch_root'] = str(SOURCE)
        row['reference_material_usable'] = not held
        grouped[group].append(row)
        grouped_records[group].append(record)
        grouped_images[group].extend(by_seq[seq])
        reason_counts.update(reasons)
        combined = dict(row)
        for field in ['case_file', 'chart_file', 'private_path', 'public_path', 'held_original_public_path']:
            if combined.get(field):
                combined[field] = f"{group}/{combined[field]}"
        all_rows.append(combined)
        index_rows.append((row['case_id'], group, '；'.join(reasons) or '未发现当前规则覆盖的异常'))

    for group in ['正常可用', '异常待核']:
        root = DEST / group
        rows = grouped[group]
        write_json(root / 'analysis_manifest.json', {
            'schema': 'analysis-manifest-v1', 'batch': 'qqwb20261019-分流-20261019',
            'counts': {'cases': len(rows), 'ready_for_first_analysis': sum(r['ready_for_first_analysis'] for r in rows)},
            'usage': '仅正常可用包允许调度。异常包原公开输入只供排错，禁止派发。', 'cases': rows,
        })
        write_json(root / 'image_ledger.json', {**ledger, 'images': [i for i in ledger['images'] if i['seq'] in {r['seq'] for r in grouped_records[group]}]})
        for name, data in [('records', grouped_records[group]), ('images', grouped_images[group])]:
            path = root / 'raw' / f'{name}.jsonl'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in data), encoding='utf-8')
        lines = ['# ' + group + '清单', '', '| 案例 | 异常类别 |', '|---|---|']
        lines.extend(f"| [{r['case_id']}]({r['case_file']}) | {'；'.join(r['异常类别']) or '未发现当前规则覆盖的异常'} |" for r in rows)
        (root / '清单.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    assert len(all_rows) == len(records) == 243
    assert len({r['case_id'] for r in all_rows}) == 243
    assert len(grouped['正常可用']) + len(grouped['异常待核']) == 243
    for row in all_rows:
        for field in ['case_file', 'chart_file', 'private_path']:
            assert (DEST / row[field]).is_file(), row[field]
        if row['ready_for_first_analysis']:
            assert (DEST / row['public_path']).is_file()
        else:
            assert row['public_path'] is None
    counts = {'来源总数': 243, '正常可用': len(grouped['正常可用']), '异常待核': len(grouped['异常待核']), '异常类别计数_可重叠': dict(reason_counts)}
    write_json(DEST / 'analysis_manifest.json', {'schema': 'analysis-manifest-v1', 'counts': counts, 'cases': all_rows})
    write_json(DEST / '复制与分流校验.json', {'通过': True, 'counts': counts, '文件哈希核对数量': len(file_checks), 'files': file_checks})
    lines = ['# QQ新批次案例分流', '', f"正常可用 {counts['正常可用']} 个；异常待核 {counts['异常待核']} 个；合计243份来源记录。", '',
             '- [正常可用清单](正常可用/清单.md)', '- [异常待核清单](异常待核/清单.md)', '',
             '正常可用表示通过现有结构检查且未命中本轮已识别异常，不代表已逐图核完全部四课三传，也不代表作答正确或已入正式库。', '',
             '异常包按完整流程保守隔离：仅作答错误的案例也暂缓；真太阳时约定待核不等于已确认错盘。原因会重叠，不能直接加总。', '',
             '初判模型只读正常可用/analysis-ready/public；冻结初判后再提供对应private。异常包ready_for_first_analysis全部为false，public_path为空。', '',
             '保留源目录原样，复制案例、盘面、公开/私有包、原始记录和图片；复制内容逐文件SHA256核对。异常原公开包放在原公开包_禁止调度目录。', '',
             '原包JSON内的来源定位文字保持原样；分流包内对应材料可按analysis_manifest.json与raw/定位。', '', '| 异常类别 | 数量（可重叠） |', '|---|---|']
    lines.extend(f'| {reason} | {count} |' for reason, count in reason_counts.items())
    (DEST / '说明.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(DEST), **counts, '已核对复制文件': len(file_checks)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
