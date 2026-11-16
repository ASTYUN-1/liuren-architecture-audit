"""Produce the authoritative 201-source package, excluding all 42 no-answer records."""
import collections
import copy
import hashlib
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / '资料来源/qq-homework-20261018/batch_20261019'
STAGE = SOURCE / 'stage1_ready_v1'
WORK = ROOT / 'output/qqwb20261019-repair-20261019'
DEST = ROOT / 'docs/初级案例整理/初级案例资料/qqwb20261019-有效201例-修订版'
OLD = ROOT / 'docs/初级案例整理/初级案例资料/qqwb20261019-分流-20261019'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonlines(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in values), encoding='utf-8')


def setfield(md, name, value):
    new, count = re.subn(r'^- ' + re.escape(name) + r'：[^\n]*', lambda _: f'- {name}：{value}', md, count=1, flags=re.M)
    assert count == 1, name
    return new


def main():
    if DEST.exists():
        raise SystemExit('拒绝覆盖已存在的修订包，请先检查上次运行产物。')
    original_manifest = read(STAGE / 'analysis_manifest.json')
    records = [json.loads(l) for l in (SOURCE / 'raw/records.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    by_seq = {r['seq']: r for r in records}
    images = [json.loads(l) for l in (SOURCE / 'raw/images.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    all_reviews = read(WORK / 'reviewed_images.json')
    reviews = collections.defaultdict(list)
    for review in all_reviews:
        reviews[review['seq']].append(review)
    valid = {r['seq'] for r in records if r.get('mofan_kind') == 'mofan'}
    discarded = [r for r in records if r['seq'] not in valid]
    assert len(valid) == 201 and len(discarded) == 42
    source_inventory = [{'file': str(SOURCE/'raw/records.jsonl'), 'sha256': digest(SOURCE/'raw/records.jsonl')}]
    source_inventory.extend({'file': str(SOURCE/i['file']), 'sha256': digest(SOURCE/i['file'])} for i in images)
    rows, report, calendar_notes = [], [], []
    corrected_images = []
    copies = []

    def copyfile(source, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        assert digest(source) == digest(destination)
        copies.append({'source': str(source), 'output': destination.relative_to(DEST).as_posix(), 'sha256': digest(destination)})

    for original in original_manifest['cases']:
        seq = int(original['case_id'].rsplit('-', 1)[1]) - 1
        if seq not in valid:
            continue
        cid, alias = original['case_id'], original['task_alias']
        private = read(STAGE / original['private_path'])
        assert private['逐份作答'] and original['has_assignment_reference'], cid
        md = (STAGE / original['case_file']).read_text(encoding='utf-8')
        original_raw = md.split('## 7. 完整原文\n', 1)[1]
        question = re.search(r'^## 3\..*?\n(.*?)^## 4\.', md, re.M | re.S).group(1).strip()
        people = re.search(r'^- 人物与年命原文：(.*)$', md, re.M).group(1)
        source_images = [i for i in images if i['seq'] == seq]
        local_reviews = sorted(reviews[seq], key=lambda r: r['file'])
        chart_entries = []
        if local_reviews:
            for index, review in enumerate(local_reviews, 1):
                chart = read(WORK / 'charts' / (pathlib.Path(review['file']).stem + '.json'))
                assert chart['usable_for_batch_analysis'] and chart['source_chart_validation']['ok']
                name = cid + (f'-p{index}' if len(local_reviews) > 1 else '') + '.json'
                target = DEST / 'charts/v8' / name
                chart['staging_only'] = True
                chart['calendar_alignment_verified'] = chart['reconstruction_method'].startswith('retained')
                chart['validation']['source_core_chart_matches_image'] = True
                write(target, chart)
                role = '本题原盘'
                if seq == 96:
                    role = '第一盘：决赛开始时，原题允许选用' if index == 1 else '第二盘：出题时，原题允许选用'
                elif seq == 180:
                    role = '仅用于甲申日租房加价问题' if index == 1 else '仅用于丙申日视频面试问题'
                chart_entries.append({'chart_id': f'chart-{index}', 'role': role, 'chart_file': f'charts/v8/{name}', 'chart_sha256': digest(target), 'chart': chart})
                corrected = dict(review['original_transcription'])
                corrected.update({'ganzhi_raw': ' '.join(review['printed_pillars']), 'effective_casting_hour_branch': review['effective_casting_hour_branch'], 'source_review': review})
                corrected_images.append(corrected)
            reviewed_files = {r['file'] for r in local_reviews}
            corrected_images.extend(i for i in source_images if i['file'] not in reviewed_files)
            first = local_reviews[0]
            md = setfield(md, '题干原载课式信息', '；'.join(f"盘{n}四柱：{' '.join(r['printed_pillars'])}；月将：{r['month_general']}；有效占时：{r['effective_casting_hour_branch']}" for n, r in enumerate(local_reviews, 1)))
            method = '；'.join(r['correction_note'] for r in local_reviews)
            if len(local_reviews) > 1:
                method += '；' + '；'.join(e['role'] for e in chart_entries)
            md = setfield(md, '报数等其他起课信息', method)
            if seq == 3:
                people = '盘图：本命甲戌，行年庚子；性别盘图未注明。题面人物声明见第3节。'
            elif seq == 159:
                people = '盘图两人分别为：丁巳命、癸未行年、女；甲寅命、庚辰行年、女。人物对应按题面，禁止合并。'
            elif seq == 180:
                people = '第一题未注明年命；第二题题面原文：77年男。原文未明确世纪，不自行换算干支或出生年份。'
            elif seq == 237:
                people = '题面称男子无年命；盘图载男甲子命、丁未行年。来源声明冲突，暂不以盘图年命作决定性判断。'
            md = setfield(md, '人物与年命原文', people)
            if seq == 63:
                md = setfield(md, '时间缺失项', '公历日期与分钟；只见四柱及卯时，不推算日期。')
            elif seq == 237:
                md = setfield(md, '时间缺失项', '分钟；原图有2026/03/30与癸亥时，不补造时分。')
                md = setfield(md, '可直接规范化的时间', '2026-03-30（日期精度；时辰亥，分钟缺失）')
            if seq == 239:
                md = md.replace('课体：涉害 间传 极阴 九五', '课体：涉害 间传 极阴 九丑')
            section6 = ['已核对原始抓取数据与盘图；修正依据见修订记录。', method,
                        '原始文字与图片均保留；本轮未验证优秀作答正确性，不作为正式经验入库。']
            if any(e['chart']['reconstruction_method'].startswith('manual') for e in chart_entries):
                section6.append('按来源四柱将时重建；与民用时默认历法不一致之处未据此证明原因，不自行把参考显示日期当作真实占课日期。')
            if seq == 237:
                section6.append('题面称本月最后一天、无年命，与图载日期及年命存在表述差异，保留原文；禁止自动裁定。')
            md = re.sub(r'^## 6\. 待核事项\n.*?(?=^## 7\.)', '## 6. 待核事项\n' + '\n'.join(f'{i}. {t}' for i, t in enumerate(section6, 1)) + '\n\n', md, flags=re.M | re.S)
            report.append({'case_id': cid, 'seq': seq, '原异常已核查': True, '修订说明': method, '盘数': len(chart_entries), '原图': [r['file'] for r in local_reviews], '核心盘面核对': '四课、三传及天将全部匹配'})
        else:
            chart = read(STAGE / original['chart_file'])
            assert chart['usable_for_batch_analysis'] and chart['validation']['ok'], cid
            target = DEST / 'charts/v8' / (cid + '.json')
            copyfile(STAGE / original['chart_file'], target)
            chart_entries.append({'chart_id': 'chart-1', 'role': '本题原盘', 'chart_file': f'charts/v8/{cid}.json', 'chart_sha256': digest(target), 'chart': chart})
            corrected_images.extend(source_images)

        # One confirmed splitting error: a teacher-position statement became the next author.
        if seq == 180:
            card = next(c for c in private['逐份作答'] if c['作者'] == '同意了，面试没过')
            assert card['正文'].startswith('溪斜山遮\n')
            card['作者'] = '溪斜山遮'
            card['正文'] = card['正文'].removeprefix('溪斜山遮\n')
            private['未标注来源的结果式陈述'].append({'原文': '同意了，面试没过', '位置': '上一份模范作业徽章之后、下一作者溪斜山遮之前', '身份': '疑似老师评语或结果式陈述，原文无反馈标记，不提升为明确现实反馈'})
            md = md.replace('- 作者：同意了，面试没过\n- 内容原文：\n溪斜山遮\n', '- 作者：溪斜山遮\n- 内容原文：\n', 1)
            md = md.replace('## 6. 待核事项\n', '## 6. 待核事项\n- 原作答页「同意了，面试没过」位于徽章与下一作者之间，已单列为疑似评语或未标注结果式陈述，不认定真实反馈。\n', 1)

        assert md.split('## 7. 完整原文\n', 1)[1] == original_raw
        case_path = DEST / original['case_file']
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(md, encoding='utf-8')
        for image in source_images:
            copyfile(SOURCE / image['file'], DEST / image['file'])

        def assumptions(entry):
            c = entry['chart']
            review = c.get('source_review')
            result = {
                'calculation_mode': c.get('reconstruction_method', 'datetime_engine_under_recorded_assumptions'),
                'settings': c.get('input', {}).get('settings') or c.get('effective_settings'),
                'engine_algorithm_modified': False,
                'source_core_visually_verified': bool(c.get('source_chart_validation', {}).get('ok')),
                'calendar_alignment_verified': c.get('calendar_alignment_verified', False),
                'rule': '直接使用程序facts进行初判；不得自行重起课。手工四柱模式的参考日期不代表已验证历史日期。',
            }
            if review:
                result.update({'source_printed_time': review['original_transcription']['time_raw'],
                               'source_clock_datetime': review['original_transcription']['time_norm'] or None,
                               'source_printed_pillars': review['printed_pillars'],
                               'effective_casting_hour_branch': review['effective_casting_hour_branch'],
                               'source_time_and_method_notes': re.findall(r'[^；]*(?:真太阳时|活时)[^；]*', review['original_transcription'].get('note', '')),
                               'time_missing': '公历日期与分钟' if seq == 63 else '分钟' if seq == 237 else '无'})
                if c['reconstruction_method'].startswith('manual'):
                    result['month_general_input'] = review['month_general']
                    result['month_general_policy'] = '月将按原图显式传入；手工四柱模式不会使用settings.yuejiang重新换将。'
                    result['source_declared_month_general_rule'] = '日躔换将（题面明示）' if seq == 2 else '规则未全部明示，按图载月将复现'
            else:
                result['policy'] = c.get('policy')
                result['conventions'] = {k: v for k, v in (c.get('conventions') or {}).items() if k not in ['native_input_before', 'native_input_after']}
            return result

        missing = []
        if people == '未注明':
            missing.append('题面与盘图未载人物年命')
        if seq == 63:
            missing.append('缺公历日期与分钟；可按原盘分析，不输出无依据的绝对公历应期')
        if seq == 237:
            missing.extend(['缺分钟，已有日期与癸亥时', '题面与盘图年命声明冲突，禁止自行裁定', '题面本月最后一天与图载日期表述有差异，保留不猜改'])
        public = {'schema': 'case-public-input-v1', 'task_alias': alias, 'question': question,
                  'people_declared_in_question': people, 'missing_inputs': missing}
        if len(chart_entries) == 1:
            public.update({'facts': chart_entries[0]['chart']['facts'], 'chart_assumptions': assumptions(chart_entries[0])})
        else:
            public['schema'] = 'case-public-input-multichart-v1'
            public['charts'] = [{'chart_id': e['chart_id'], 'applies_to': e['role'], 'facts': e['chart']['facts'], 'chart_assumptions': assumptions(e)} for e in chart_entries]
            public['analysis_instructions'] = ('两盘对应同一组问题，原题允许任选；明确采用哪盘，或分别分析，不把两盘当独立验证样本。' if seq == 96 else '这是两个独立事件：第一题租房只能用chart-1，第二题面试只能用chart-2，分别给判断与依据；共享作答只在初判冻结后提供。')
        public_path = f'analysis-ready/public/{alias}.json'
        private_path = f'analysis-ready/private/{alias}.json'
        write(DEST / public_path, public)
        private['起课信息'] = {
            '起课时间原文': re.search(r'^- 起课时间原文：(.*)$', md, re.M).group(1),
            '规范化': re.search(r'^- 可直接规范化的时间：(.*)$', md, re.M).group(1),
            '来源盘面': [{k: v for k, v in e.items() if k != 'chart'} for e in chart_entries],
            '说明': '原图打印四柱、钟表时间与实际占时分开记录；未补造缺失日期和分钟。',
        }
        private['来源定位']['case_file'] = original['case_file']
        private['来源定位']['case_file_sha256'] = digest(case_path)
        private['来源定位']['chart_file'] = chart_entries[0]['chart_file'] if len(chart_entries) == 1 else None
        private['来源定位']['chart_sha256'] = chart_entries[0]['chart_sha256'] if len(chart_entries) == 1 else None
        private['来源定位']['charts'] = [{k: v for k, v in e.items() if k != 'chart'} for e in chart_entries]
        private['完整原文定位'] = {'records_file': 'raw/records.jsonl', 'seq': seq, 'case_file': original['case_file'], '盘图': [i['file'] for i in source_images]}
        if local_reviews:
            private['待核事项'] = ['原异常核查已完成，修订说明见review/修订记录.json；现实结果和作答正确性未核验。'] + missing
            private['修订记录'] = report[-1]
        write(DEST / private_path, private)
        rows.append({**original, 'seq': seq, 'case_sha256': digest(case_path), 'public_path': public_path,
                     'private_path': private_path, 'public_sha256': digest(DEST/public_path), 'private_sha256': digest(DEST/private_path),
                     'chart_file': chart_entries[0]['chart_file'] if len(chart_entries) == 1 else None,
                     'chart_sha256': chart_entries[0]['chart_sha256'] if len(chart_entries) == 1 else None,
                     'charts': [{k: v for k, v in e.items() if k != 'chart'} for e in chart_entries],
                     'ready_for_first_analysis': True, 'has_assignment_reference': True, 'blocking_reasons': [],
                     'input_schema': public['schema'], 'required_capabilities': ['multichart'] if len(chart_entries)>1 else [],
                     'source_core_visually_verified_this_run': bool(local_reviews), '限制说明': missing,
                     '分流状态': '已修订可分析' if local_reviews else '有作答可分析', 'library_status': '未入正式库'})

    assert len(rows) == 201
    jsonlines(DEST/'raw/records.jsonl', [r for r in records if r['seq'] in valid])
    jsonlines(DEST/'raw/images.jsonl', corrected_images)
    jsonlines(DEST/'raw/images_original_transcription.jsonl', [i for i in images if i['seq'] in valid])
    ledger = read(STAGE/'image_ledger.json')
    write(DEST/'image_ledger.json', {**ledger, 'images': [i for i in ledger['images'] if i['seq'] in valid]})
    write(DEST/'review/reviewed_images.json', all_reviews)
    write(DEST/'review/修订记录.json', report)
    write(DEST/'review/已剔除无作答42例.json', [{'case_id': f"raw-qqwb20261019-{r['seq']+1:04d}", 'seq': r['seq'], '抓取状态': r.get('mofan_kind'), '原因': {'none':'未获取作答','detail':'作答入口重复返回题面','other':'返回内容不是有效作答'}[r.get('mofan_kind')]} for r in discarded])
    write(DEST/'review/来源指纹.json', source_inventory)
    counts = {'来源记录':243,'无作答剔除':42,'有效有作答来源':201,'本轮核查修正来源':31,'本轮逐图核对':33,'可分析来源':201,'单盘输入':199,'多盘输入':2,'程序盘数量':sum(len(r['charts']) for r in rows),'未入正式库':201}
    write(DEST/'analysis_manifest.json', {'schema':'analysis-manifest-v2','batch':'qqwb20261019','counts':counts,
          'usage':'仅使用本修订版；201份来源含两个多盘输入，需按input_schema处理。先public初判，冻结后再private。', 'cases':rows})
    write(DEST/'review_queue.json', {'schema':'review-queue-v1','blocking_items':[], 'nonblocking_limitations':[{'case_id':r['case_id'],'限制说明':r['限制说明']} for r in rows if r['限制说明']]})
    lines = ['# 有效201例清单','','已剔除42例无实际作答资料；编号保留原编号，不重新编号。','','| 案例 | 状态 | 盘数 | 输入 |','|---|---|---|---|']
    lines.extend(f"| [{r['case_id']}]({r['case_file']}) | {r['分流状态']} | {len(r['charts'])} | [初判]({r['public_path']}) |" for r in rows)
    (DEST/'清单.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    reportlines=['# 原异常核查与修订','','原57例异常：26例属于本次剔除的无作答资料，余31例核查33张原图。','','| 案例 | 修订说明 |','|---|---|']
    reportlines.extend(f"| [{r['case_id']}](../cases/{r['case_id']}.md) | {r['修订说明']} |" for r in report)
    (DEST/'review/修订说明.md').write_text('\n'.join(reportlines)+'\n',encoding='utf-8')
    (DEST/'说明.md').write_text('''# QQ有效201例修订包

本目录替代旧分流包。243份抓取中，201份确有作答，42份无作答已剔除。

- [201例清单](清单.md)
- [31例异常核查修订记录](review/修订说明.md)
- [调度清单](analysis_manifest.json)

本轮对31份有效来源的33张盘图逐图核对。四柱（打印时柱与活时另存）、月将、有效占时、四课三传及天将均已与程序输出匹配。其余170份沿用原结构检查通过的程序盘，未宣称逐图复核。

0097是同一组问题的两个可选课盘；0181是租房与面试两个独立事件，分别绑定各自课盘。两份公开包采用case-public-input-multichart-v1；不得被旧单盘读取器静默选首盘。来源总数201，程序盘203。

0064保留缺公历日期、分钟；0238保留缺分钟及题面/盘图年命声明矛盾。使用完整原载四柱、月将、占时重建，可作原盘判断；不补造历史日期、分钟或自动换算绝对公历应期。子时、换将等差异明确按来源原盘复现，不把“复现成功”等同于已经证明所有历法差异原因。

初判只给analysis-ready/public，冻结后再给private。优秀作答保留其参考质量与徽章来源，不能冒充出题者的明确现实反馈。资料均未入正式案例库与经验库。

原始抓取目录保留以便追溯；当前有效包及旧分流副本均剔除42例的案例、公开包、私有包、盘面和图片。旧分流包停止调度，以本目录为准。
''',encoding='utf-8')
    write(DEST/'review/复制校验.json',{'文件数':len(copies),'files':copies})
    # Stop old scheduling and remove the explicitly discarded records' local copies.
    previous = read(OLD/'analysis_manifest.json')
    removed_files = []
    for row in previous['cases']:
        seq = int(row['case_id'].rsplit('-',1)[1])-1
        if seq in valid:
            continue
        targets = [OLD/row[k] for k in ['case_file','chart_file','private_path','public_path','held_original_public_path'] if row.get(k)]
        group_root = OLD/row['分流状态']
        targets.extend(group_root/i['file'] for i in images if i['seq']==seq)
        for target in set(targets):
            assert target.resolve().is_relative_to(OLD.resolve())
            if target.is_file():
                target.unlink()
                removed_files.append(str(target.relative_to(OLD)))
    for base in [OLD, OLD/'正常可用', OLD/'异常待核']:
        path=base/'analysis_manifest.json'
        old=read(path)
        old['cases']=[r for r in old['cases'] if int(r['case_id'].rsplit('-',1)[1])-1 in valid]
        for row in old['cases']:
            row['ready_for_first_analysis']=False
            row['blocking_reasons']=['旧分流包已停用，请使用qqwb20261019-有效201例-修订版']
        old['counts']={'cases':len(old['cases']),'ready_for_first_analysis':0,'已剔除无作答':42 if base==OLD else None}
        old['superseded_by']=str(DEST)
        write(path,old)
        for name in ['records','images']:
            file=base/'raw'/f'{name}.jsonl'
            if file.exists():
                data=[json.loads(l) for l in file.read_text(encoding='utf-8').splitlines() if l.strip()]
                jsonlines(file,[v for v in data if v['seq'] in valid])
        file=base/'image_ledger.json'
        if file.exists():
            oldledger=read(file);oldledger['images']=[i for i in oldledger['images'] if i['seq'] in valid];write(file,oldledger)
        for name in ['说明.md','清单.md']:
            file=base/name
            if file.exists():
                file.write_text('# 旧分流包已停用\n\n42例无作答资料已剔除；其余资料已在新包重新整理。\n\n请使用：['+DEST.name+']('+str(DEST).replace('\\','/')+'/说明.md)。\n',encoding='utf-8')
    write(WORK/'旧副本剔除记录.json', {'removed_files':removed_files,'count':len(removed_files)})
    entry=DEST.parent/'qqwb20261019-当前入口.md'
    entry.write_text('# QQ批次当前入口\n\n当前使用[有效201例修订包](qqwb20261019-有效201例-修订版/说明.md)。\n\n旧分流包已停用；42例无作答已剔除。\n',encoding='utf-8')
    print(json.dumps({'output':str(DEST),**counts,'旧副本已删除文件':len(removed_files)},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
