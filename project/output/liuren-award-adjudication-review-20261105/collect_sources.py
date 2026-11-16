"""Record inspected local source passages; no active edits or model requests."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCES=[
 ('BH-FOCUS','书籍库/北海闲人/北海闲人，特训班讲义.txt','gb18030',[(14,16),(43,51),(193,198),(357,367),(463,469),(477,482)]),
 ('BH-LIQI','书籍库/北海闲人/理法简易.txt','utf-8',[(515,518),(697,708),(1064,1076),(1487,1489),(1565,1567),(1695,1706),(1966,1974)]),
 ('BH-BIFA','书籍库/北海闲人/毕法赋全解-正式整理本.md','utf-8',[(455,469)]),
 ('RG','书籍库/经典古籍/佚名/壬归.txt','utf-8',[(90,104),(138,146),(355,363),(383,389),(417,421)]),
 ('TY','书籍库/现代著作/献给六壬天一群的六壬笔记-2023年.txt','utf-8',[(1055,1071),(1123,1137),(1249,1261),(1409,1421)]),
 ('DQ','书籍库/经典古籍/明代/六壬大全-明-郭载騋.txt','utf-8',[(3750,3751)]),
 ('CY','书籍库/经典古籍/清代/六壬粹言-清-刘赤江.txt','utf-8',[(63,66)]),
]
records=[]
for key,relative,encoding,spans in SOURCES:
    raw=(ROOT/relative).read_bytes()
    text=raw.decode(encoding)
    lf=text.replace('\r\n','\n').split('\n')
    formal=text.splitlines()
    offsets=[]
    pos=0
    for piece in text.splitlines(keepends=True):
        offsets.append(pos)
        pos+=len(piece)
    import bisect
    for start,end in spans:
        quote='\n'.join(lf[start-1:end])
        start_offset=sum(len(line)+1 for line in text.split('\n')[:start-1])
        end_offset=start_offset+len('\n'.join(text.split('\n')[start-1:end]))
        fs=bisect.bisect_right(offsets,start_offset)
        fe=bisect.bisect_right(offsets,max(start_offset,end_offset-1))
        records.append(dict(source=key,path=relative,encoding=encoding,
            fileSha256=hashlib.sha256(raw).hexdigest(),lfStart=start,lfEnd=end,
            formalSplitlinesStart=fs,formalSplitlinesEnd=fe,quote=quote,
            status='selected passages read; source text is not predictive validation'))
(HERE/'source-excerpts.json').write_text(json.dumps(dict(lineConvention='LF line labels match rg; formal splitlines mapping supplied separately, do not interchange',passages=records,activeChanged=False,modelCalls=0),ensure_ascii=False,indent=2)+'\n','utf-8')
parts=['# 奖学金等级裁决：所核原文\n','这些是本轮选段核读记录，不表示整书审完。LF行号与工作台splitlines行号分别记录；GB18030讲义保持原字节。原书断语、作者案例断语、原载反馈与本轮解释不能混同。\n']
for row in records:
    parts.append(f"## {row['source']}：{row['path']}，LF{row['lfStart']}–{row['lfEnd']}\n\n正式splitlines定位：{row['formalSplitlinesStart']}–{row['formalSplitlinesEnd']}；文件SHA256：`{row['fileSha256']}`。\n\n```text\n{row['quote']}\n```\n")
(HERE/'所核原文.md').write_text('\n'.join(parts),'utf-8')
print(json.dumps(dict(sourceFiles=len(SOURCES),readPassages=len(records),activeChanged=False,modelCalls=0)))
