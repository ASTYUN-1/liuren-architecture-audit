"""Visual observations made against original downloaded images, not assignments."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / '资料来源/qq-homework-20261018/batch_20261019'
OUT = ROOT / 'output/qqwb20261019-repair-20261019'
# file | four displayed pillars | month general | effective casting hour |
# lessons in order: upper, lower, general abbreviation | ordered transmissions | generals
OBSERVATIONS = '''
002_1.jpg|丙午 癸巳 丙申 己亥|酉|亥|卯丙空 丑卯勾 午申玄 辰午虎|丑亥酉|勾雀贵
003_1.jpg|丙午 丙申 庚申 丙戌|午|戌|辰庚玄 子辰龙 辰申玄 子辰龙|子申辰|龙蛇玄
011_1.jpg|乙巳 癸未 己卯 癸酉|未|酉|巳己合 卯巳龙 丑卯虎 亥丑玄|丑亥酉|虎玄后
022_1.jpg|丙午 丙申 乙丑 丙戌|午|戌|子乙勾 申子贵 酉丑蛇 巳酉玄|巳丑酉|玄龙蛇
027_1.jpg|丙午 甲午 己巳 壬申|申|申|未己虎 未未虎 巳巳龙 巳巳龙|巳申寅|龙常雀
033_1.jpg|丙午 辛卯 戊寅 辛酉|亥|酉|未戊贵 酉未阴 辰寅合 午辰蛇|辰午申|合蛇后
036_1.jpg|丙午 甲午 丙辰 己亥|申|亥|寅丙龙 亥寅雀 丑辰勾 戌丑蛇|亥申巳|雀后常
043_1.jpg|丙午 丙申 戊午 壬子|午|子|亥戊勾 巳亥阴 子午龙 午子后|午子午|后龙后
054_1.jpg|丙午 癸巳 壬寅 辛亥|申|亥|申壬虎 巳申阴 亥寅勾 申亥虎|巳寅亥|阴蛇勾
057_1.jpg|丙午 乙未 甲辰 壬申|午|申|子甲后 戌子玄 寅辰蛇 子寅后|戌申午|玄虎龙
063_1.jpg|丙午 乙未 丁未 癸卯|午|卯|戌丁蛇 丑戌阴 戌未蛇 丑戌阴|亥戌戌|贵蛇蛇
071_1.jpeg|丙午 乙未 乙巳 丙子|午|子|戌乙雀 辰戌常 亥巳合 巳亥玄|巳亥巳|玄合玄
074_1.jpeg|丙午 甲午 戊午 庚申|申|申|巳戊勾 巳巳勾 午午龙 午午龙|巳申寅|勾虎蛇
077_1.jpg|乙巳 庚辰 庚午 甲申|酉|申|酉庚常 戌酉玄 未午空 申未虎|戌未酉|玄空常
096_1.jpg|丙午 乙未 乙未 戊寅|未|寅|酉乙蛇 寅酉空 子未勾 巳子玄|巳戌卯|玄雀虎
096_2.jpg|丙午 乙未 乙未 庚辰|未|辰|未乙龙 戌未雀 戌未雀 丑戌后|未戌丑|龙雀后
099_1.jpg|丙午 乙未 乙酉 丙子|未|子|亥乙合 午亥阴 辰酉常 亥辰合|亥午丑|合阴龙
121_1.jpeg|乙巳 己丑 乙酉 丁丑|丑|丑|辰乙勾 辰辰勾 酉酉后 酉酉后|辰酉卯|勾后龙
129_1.jpg|乙巳 己丑 乙酉 乙酉|丑|酉|申乙贵 子申勾 丑酉龙 巳丑玄|申子辰|贵勾常
153_1.jpg|乙巳 丙戌 甲子 乙丑|辰|丑|巳甲阴 申巳蛇 卯子常 午卯后|申亥寅|蛇勾虎
159_1.jpg|丙午 甲午 辛亥 乙未|申|未|亥辛虎 子亥空 子亥空 丑子龙|丑寅卯|龙勾合
180_1.jpg|丙午 癸巳 甲申 己巳|酉|巳|午甲虎 戌午合 子申蛇 辰子玄|辰申子|玄龙蛇
180_2.jpg|乙巳 辛巳 丙申 丁酉|申|酉|辰丙龙 卯辰空 未申雀 午未合|卯寅丑|空虎常
181_1.jpg|乙巳 丁亥 乙巳 甲申|寅|申|戌乙雀 辰戌常 亥巳蛇 巳亥虎|巳亥巳|虎蛇虎
201_1.jpg|乙巳 乙酉 己亥 戊辰|辰|寅|酉己后 亥酉玄 丑亥虎 卯丑龙|丑卯巳|虎龙合
203_1.jpg|丙午 壬辰 戊寅 壬子|酉|子|寅戊龙 亥寅常 亥寅常 申亥后|寅亥申|龙常后
205_1.jpg|丙午 庚寅 己酉 癸酉|子|酉|戌己阴 丑戌虎 子酉常 卯子龙|卯午酉|龙雀后
215_1.jpg|丙午 壬辰 乙丑 癸未|酉|未|午乙空 申午勾 卯丑玄 巳卯虎|申戌子|勾雀贵
218_1.jpg|乙巳 己丑 甲辰 己巳|子|巳|酉甲勾 辰酉玄 亥辰雀 午亥虎|午丑申|虎贵龙
229_1.png|丙午 庚寅 丙子 戊子|子|子|巳丙勾 巳巳勾 子子玄 子子玄|巳申寅|勾蛇虎
235_1.jpg|丙午 壬辰 己巳 乙亥|酉|亥|巳己合 卯巳龙 卯巳龙 丑卯虎|丑亥酉|虎玄后
237_1.png|丙午 辛卯 癸卯 癸亥|戌|亥|子癸玄 亥子常 寅卯后 丑寅阴|丑子亥|阴玄常
239_1.jpg|丙午 壬辰 乙卯 丙子|戌|子|寅乙空 子寅常 丑卯虎 亥丑玄|丑亥酉|虎玄后
'''
GENERAL = dict(zip('贵蛇雀合勾龙空虎常玄阴后', ['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后']))
NOTES = {
  3: '题面明确日躔换将；原图月将酉，保留原将，不默认改成中气将。',
  4: '原图含公历与农历两行；公历解析与本命甲戌、行年庚子一并补回。',
  12: '年柱乙丑改为乙巳。',
  34: '完整时间与排盘选项照原图保留，另建引擎输入；原文为卯昼酉夜。',
  44: '23时来源日柱戊午保留；不将子时差异静默改成程序默认日柱。',
  58: '日柱甲申改甲辰；原图中央也写甲辰日。',
  64: '原图日期行已裁切，日期和分钟继续为空；完整四柱将时可按手工四柱重建，不推算历史日期。',
  72: '23时原图乙巳日保留，按来源四柱重建。',
  78: '活时申时明确保留；不因与钟表时辰相同而丢掉起课方法。',
  97: '保留两个课盘：决赛开始时、出题时；原题允许任选，必须分别注明采用哪盘。',
  100: '23时原图乙酉日保留，按来源四柱重建。',
  122: '活时丑时与钟表20:03分离；不能按戌时重排。',
  130: '保留秒02及冬字原文，引擎输入单独取18:55分钟；非交节临界分钟。',
  154: '北京时间00:55与真太阳时01:17跨时辰；原图乙丑时，按原将时重建，不按民用子时覆盖。',
  160: '日期前公历标签不属于格式错误；年命两人分别保留。',
  181: '按甲申日租房与丙申日面试分别绑定两盘，不能选首盘回答两事。',
  182: '年柱乙亥改乙巳。',
  202: '原图打印时柱戊辰与活时寅时分开保存；有效占时寅；原图三传丑卯巳。',
  204: '23时原图戊寅日保留，按来源四柱重建。',
  206: '北京时间与真太阳时均酉时；同时保留两行，按原四柱将时核对。',
  216: '日柱乙未改乙丑；原图中央为乙丑日。',
  230: '原图月将子、日柱丙子，与民用时程序默认不同；明确按来源原盘复现，历史历法差异不冒充已解释。',
  238: '原图有公历日期、癸亥时，缺分钟；不补分钟，改用已载完整四柱将时重建。',
  240: '23时原图乙卯日保留；课体原文九丑，旧转录九五有误。',
}


def main():
    images = {i['file']: i for i in map(json.loads, (SOURCE/'raw/images.jsonl').read_text(encoding='utf-8').splitlines())}
    reviews = []
    for line in OBSERVATIONS.strip().splitlines():
        file, pillars, month_general, hour, lessons, transmissions, generals = line.split('|')
        original = images['pan/' + file]
        number = original['seq'] + 1
        reviews.append({
            'case_id': f'raw-qqwb20261019-{number:04d}', 'seq': original['seq'],
            'file': 'pan/' + file, 'sha256': hashlib.sha256((SOURCE/'pan'/file).read_bytes()).hexdigest(),
            'reviewed_by': 'Codex direct visual inspection of original downloaded image',
            'printed_pillars': pillars.split(), 'month_general': month_general,
            'effective_casting_hour_branch': hour,
            'lessons': [{'tianpan': x[0], 'dizhi': x[1], 'tianjiang': GENERAL[x[2]]} for x in lessons.split()],
            'transmissions': [{'diZhi': branch, 'tianjiang': GENERAL[general]} for branch, general in zip(transmissions,generals)],
            'original_transcription': original,
            'correction_note': NOTES.get(number, '保留民用时与真太阳时原始双行，以原图四课三传及天将确认重建结果。'),
            'not_verified': ['现实结果真实性', '优秀作答正确性', '所有神煞与长生逐项一致性'],
        })
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'reviewed_images.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(reviews)}张原图，{len(set(r["case_id"] for r in reviews))}份有效来源')


if __name__ == '__main__':
    main()
