"""Narrow provenance-only references; only removes files in this export staging."""
from pathlib import Path
from collections import Counter
import json
import re

package=Path(__file__).resolve().parents[1]
if not str(package).startswith('\\\\?\\'):package=Path('\\\\?\\'+str(package))
project=package/'project'
rows=json.loads((package/'audit/source-manifest.json').read_text('utf-8'))
excluded=json.loads((package/'audit/excluded-files.json').read_text('utf-8'))
kept=[]
for row in rows:
    name=row['source_path'];parts=Path(name).parts;reason=None
    if parts[0] in {'web','mobile','ui-rebuild','归档','运营资料','.orchestration'}:
        reason='文档溯源链接指向无关产品/八字/运营；非六壬本机流程依赖'
    elif parts[0]=='排盘存档' and name!='排盘存档/README.md':
        reason='真实排盘记录；合成样例另供'
    elif parts[0]=='课程写作' and not name.startswith('课程写作/整理本/毕法赋全解/'):
        reason='课程产物；不参与本机占断'
    elif name=='tools/verify-domestic-entry.py':
        reason='网站服务器运维，非本机流程'
    elif parts[0]=='output':
        folder=parts[1].lower() if len(parts)>1 else ''
        if any(x in folder for x in ('website','网站','imagegen','server','payment','问衡','课程','公众号','portable','case-index','experience-index','codex-liuren','liuren-computations','liuren-flow-state','liuren-adjudication-requests')):
            reason='历史链接进入无关业务、运行缓存、客户任务或环境'
        elif any(re.match(r'(?:acceptance-run|synthetic-run|live-run|real-run|run-\d)',x) for x in parts):
            reason='历史生成运行会话缓存；源码与合成验收另供'
        elif Path(name).name in {'session.json','context.json','evidence-packet.json','reads.json','state.json'} and '/before/' not in name:
            reason='历史生成运行状态；不需要复制来还原机制'
        elif '/before/' not in name and Path(name).suffix.lower() in {'.png','.jpg','.jpeg','.webp','.mp4','.pdf','.gif'}:
            reason='历史渲染或无关媒体；必要原书与知识源在source目录保留'
    if reason:
        p=project/name
        # No live file is ever touched. Validate the absolute target before unlink.
        if not p.resolve().is_relative_to(project.resolve()):raise ValueError('unsafe export target')
        p.unlink(missing_ok=True);excluded.append({'path':name,'reason':reason})
    else:kept.append(row)
(package/'audit/source-manifest.json').write_text(json.dumps(kept,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(package/'audit/excluded-files.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trans=json.loads((package/'audit/transformations.json').read_text('utf-8'))
names={r['path'] for r in kept}
(package/'audit/transformations.json').write_text(json.dumps([r for r in trans if r['path'] in names],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'files':len(kept),'bytes':sum(r['bytes'] for r in kept),'excluded_records':len(excluded),'by_root':dict(Counter(r['source_path'].split('/')[0] for r in kept))}
(package/'audit/scope-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
