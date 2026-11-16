"""Create a new versioned inventory, preserving the earlier35 snapshot."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent.parent
old=ROOT/'output/shensha-audit-20261109'
s=(old/'inventory.mjs').read_text('utf-8')
s=s.replace('32个常用编号族，加6条细分规则','原32个常用编号族及6条细分规则，另增S33关神')
s=s.replace('不是40条规则','名称/别名数不等于规则数')
s=s.replace('没有修改引擎、活动表、冻结包或历史盘。','本脚本只读取已生效36版，不修改引擎、活动表、冻结包或历史盘；本轮新增关神的接入另见接入说明。')
s=s.replace('本轮38条','本轮39条').replace('当前38条','当前39条')
(OUT/'inventory.mjs').write_text(s,'utf-8')
s=(old/'classify.py').read_text('utf-8').replace("'关神、四废、天车", "'四废、天车")
s=s.replace('132','131').replace('== 100','== 99').replace("'classified_meaning_names':100","'classified_meaning_names':99")
s=s.replace('现行38条规则已覆盖的40个','现行39条规则已覆盖的41个').replace('100名按现有','99名按现有')
s=s.replace('本轮为整理分类，沿用现有释义记录；没有将分类写入活动规则，没有重新校勘全部原典。','关神已另行接入S33并从本表移除。本表其他项沿用现有释义记录，没有据分类新增规则或重新校勘全部原典。')
(OUT/'classify.py').write_text(s,'utf-8')
print('Created36 inventory scripts; previous35 snapshot unchanged')
