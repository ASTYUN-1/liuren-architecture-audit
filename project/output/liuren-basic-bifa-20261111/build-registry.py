"""Source-preserving condition registry; universal-newline line numbering."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda x:(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
old=ROOT/'tools/liuren-bifa-source-rules.json'
registry=json.loads(old.read_text('utf-8'))
registry['line_convention']='universal-newlines：CRLF及剩余CR各转LF；适配原TXT的CR-CR-LF，不等于原刻影印验校'
# Repair prior empty TXT quotes caused by CR-CR-LF being stripped instead of
# interpreted under the line-number convention used by the original readings.
before=OUT/'audit-source-rules-before.json'
if not before.exists():before.write_bytes(old.read_bytes())
for s in registry['sources']:
 data=(ROOT/s['path']).read_bytes();assert sha(data)==s['sha256']
 lines=(ROOT/s['path']).read_text('utf-8-sig').split('\n')
 s['line_mode']='universal-newlines; CRLF and remaining CR each become LF'
 for e in s['excerpts']:
  e['quote']='\n'.join(lines[e['line_start']-1:e['line_end']]);assert e['quote'].strip()
old.write_bytes(encode(registry))
specs={
 'D':[(2,13027,13037),(21,13247,13267),(22,13269,13285),(26,13311,13319),
      (27,13321,13329),(31,13363,13365),(32,13375,13377),(37,13421,13435),
      (41,13479,13481),(47,13521,13523),(51,13555,13557),(52,13559,13561),
      (61,13605,13611),(69,13713,13717),(70,13719,13721),(77,13791,13799)],
 'B':[(6,676,680),(16,1353,1359),(23,1795,1803),(31,2125,2139),(32,2154,2164),
      (37,2404,2412),(69,3441,3449),(83,4176,4184),(85,4267,4277),
      (86,4332,4338),(91,4526,4536)]}
sources=[]
for tag,s in zip(['D','B'],registry['sources']):
 lines=(ROOT/s['path']).read_text('utf-8-sig').split('\n')
 sources.append({k:s[k] for k in ['path','sha256','role','line_mode']}|{'excerpts':[
  {'id':f'BF-{tag}{law:02d}','line_start':a,'line_end':b,'quote':'\n'.join(lines[a-1:b])}
  for law,a,b in specs[tag]]})
rows=[
 ('02-boundary',2,'首尾相见','BF-D02','干支上神分见同旬旬首、旬尾，方向分别注明'),
 ('02-return',2,'回环结构','BF-D02','三传各支均见四课上神'),
 ('05-yang',5,'课传全阳','BF-B06','四课上神、三传皆阳支'),
 ('06-yin',6,'课传全阴','BF-B06','四课上神、三传皆阴支'),
 ('16-empty',16,'空上乘空','BF-B16','天空所乘支旬空且见四课上神或三传'),
 ('21-cross',21,'交车六合','BF-D21 BF-D22','干上与支六合、支上与干寄宫六合；干支同宫暂不自动采用'),
 ('22-main',22,'上下皆合主格','BF-D22','干支上神六合且干寄宫与日支六合'),
 ('22-vertical',22,'上下俱合格（大全）','BF-D22','干寄宫与干上六合且日支与支上六合'),
 ('22-upper',22,'独干支上神六合','BF-D22','干支上神六合，仅报告这一层'),
 ('23-to-stem',23,'支传干','BF-B23','初传为支上、末传为干上；两上相同不强分方向'),
 ('24-to-branch',24,'干传支','BF-B23','初传为干上、末传为支上；两上相同不强分方向'),
 ('26-ding',26,'财乘旬丁','BF-D26','日财旬遁丁，且见四课上神或三传'),
 ('26-horse',26,'财乘日驿马','BF-D26','日财兼日支驿马，且见四课上神或三传'),
 ('27-drain',27,'三传合局脱干','BF-D27','三传三合局且日干生该局；只是传脱分支'),
 ('31-chain',31,'三传递生','BF-B31 BF-D31','初生中生末或末生中生初；另核终点是否生日干'),
 ('32-chain',32,'三传递克','BF-B32 BF-D32','初克中克末或末克中克初；另核终点是否克日干'),
 ('37-assist',37,'末生初','BF-B37 BF-D37','末传生初传；按初对日干关系分等'),
 ('41-luma',41,'干支逢禄马','BF-D41','干上为日支驿马且支上为日干禄'),
 ('47-prison',47,'贵临辰戌','BF-D47','实际昼夜贵人临地盘辰戌；临身、入宅与普通入狱分列'),
 ('51-gate',51,'魁度天门发用','BF-D51','戌加亥且戌为初传'),
 ('52-gate',52,'罡塞鬼户','BF-D52','辰加寅，不要求入传'),
 ('61-tomb',61,'墓虎加干','BF-D61','白虎乘日五行墓神且临干寄宫；不涉及未给年命的旁格'),
 ('69-hidden',69,'虎乘遁鬼','BF-D69 BF-B69','白虎所乘支旬遁干克日干且见课传'),
 ('69-plain-hidden',69,'干明支暗二鬼','BF-D69','干上神克日干、支上旬遁干克日干'),
 ('69-hidden-plain',69,'干暗支明二鬼','BF-B69','干上旬遁干克日干、支上神克日干'),
 ('70-two',70,'鬼临三四','BF-D70','第三、四课上神均为日鬼'),
 ('77-cross',77,'互生结构','BF-D77','干上生日支且支上生日干'),
 ('77-each',77,'俱生结构','BF-D77','干上生日干且支上生日支'),
 ('83-call',83,'三六相呼','BF-B83','三传三合局且局中神与干上或支上六合'),
 ('85-clamp',85,'初遭夹克','BF-B85','初传同时受地盘与所乘天将五行克'),
 ('86-internal',86,'将逢内战','BF-B86','地盘克天盘支、天盘支克所乘将，且该支见课传'),
 ('91-tiger',91,'虎乘日鬼','BF-B91 BF-D61','白虎乘日鬼且见课传；临干、发用、入传位置分列'),
]
rules=[{'id':'BF'+id,'law_number':law,'name':name,'evidence_ids':refs.split(),'definition':definition}
       for id,law,name,refs,definition in rows]
evidence={e['id'] for s in sources for e in s['excerpts']}
assert all(set(r['evidence_ids'])<=evidence for r in rules)
bundle={'schema':'liuren-basic-bifa-rules-v1','release':'20261111-basic-bifa-42',
 'scope':'已核基本结构；不宣称百法所有正变类格齐备','line_mode':'universal-newlines',
 'law22':'用户指定依《大全》，上下俱合采用纵向两组六合',
 'sources':sources,'rules':rules,
 'deferred':['未核原引擎标签','贵在干前后算法争点','太常日本旁格','须年命、月令、占事才足以定义的偏僻类格'],
 'policy':'按实际昼夜盘独立扫描，不信任原引擎毕法候选；结构成立不自动采用标题吉凶。空亡不抹掉关系，效力另依U规则。'}
(ROOT/'tools/liuren-bifa-basic-rules.json').write_bytes(encode(bundle))
print('rules',len(rules),'laws',len({r['law_number'] for r in rules}),'source spans',sum(len(s['excerpts']) for s in sources))
