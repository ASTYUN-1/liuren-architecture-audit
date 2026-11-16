"""Export bounded source passages; never modify books or active rules.

LF spans locate earlier readings. Evidence coordinates and quotes use the
original decoded text's splitlines(), as required by the knowledge convention.
This checks text provenance, not semantics or predictive performance.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "source_reader", ROOT / "output/liuren-expert-adjudication-study-20261105/read_sources.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

# ID, source, LF start/end, source identity, topic.
SPANS = [
    ("E01", "BHL", 1063, 1075, "北海《理法简易》正文，内引《壬归》另辨", "察天、察地、看人"),
    ("E02", "BHL", 353, 359, "北海《理法简易》正文", "关系、十二长生及参照对象"),
    ("E03", "BHL", 390, 410, "北海《理法简易》正文", "空、墓、合、生扶与贪生贪合"),
    ("E04", "BHL", 411, 425, "北海《理法简易》正文", "衰旺、生克并存、刑冲与令星"),
    ("E05", "BHL", 433, 449, "北海《理法简易》正文，内引《毕法》", "制鬼位置、受制与生鬼"),
    ("E06", "BHL", 453, 459, "北海《理法简易》正文", "递生、扶鬼与财旺身弱"),
    ("E07", "BHL", 2451, 2463, "北海正文与所引《壬归》交错，须逐段辨别", "出行占：鬼禁日、凶类并聚与仕庶"),
    ("E08", "RG", 106, 128, "《壬归》本地文本，作者依目录为佚名", "作用对象、五气、所临之地与鬼受制"),
    ("E09", "RG", 138, 146, "《壬归》本地文本", "神将关系、夹克夹生与末制凶用"),
    ("E10", "RG", 218, 230, "《壬归》本地文本", "墓冲、三传始终与制救"),
    ("E11", "RG", 277, 277, "《壬归》本地文本", "天五气、地十二气及身类参照"),
    ("E12", "RG", 285, 295, "《壬归》求财章", "类将类神、内外战、十二气、阴神"),
    ("E13", "RG", 299, 323, "《壬归》求财章", "身财比较、身强定义、取与受伤"),
    ("E14", "RG", 405, 413, "《壬归》干人章", "彼我、生助者自身受制"),
    ("E15", "RG", 759, 765, "《壬归》出行章", "制鬼须有力、旺鬼禁日及仕宦例外"),
    ("E16", "TY", 139, 163, "《献给六壬天一群的六壬笔记》正文", "月令五气与权柄，四纲为本书方法"),
    ("E17", "TY", 191, 209, "《献给六壬天一群的六壬笔记》正文", "五气、死火克不动旺金"),
    ("E18", "TY", 381, 389, "《献给六壬天一群的六壬笔记》正文", "十二长生以日干为准的口径"),
    ("E19", "TY", 455, 465, "《献给六壬天一群的六壬笔记》正文", "刑冲破害、四纲强语、弱者受冲"),
    ("E20", "ZNZ", 487, 495, "《六壬指南注解》本地文本，赋文与注解分辨；注者身份未另核", "旺鬼贪荣与相刑例外"),
]

FORMAL_SPANS = [
    ("E21", "书籍库/北海闲人/毕法赋全解-正式整理本.md", 1233, 1245,
     "北海《毕法赋全解》本地正式整理本，非扫描原件", "第十三法鬼贼当时无畏忌"),
    ("E22", "书籍库/北海闲人/六壬金针_修正版.md", 2689, 2695,
     "北海《六壬金针》本地修正版，有OCR残损，例证现实化解释属作者", "占讼：制鬼、化官、旺败"),
]

def make_row(eid, path, encoding, start, end, identity, topic, **extra):
    raw = (ROOT / path).read_bytes()
    lines = raw.decode(encoding).splitlines()
    assert 1 <= start <= end <= len(lines)
    return dict(id=eid, path=path, encoding=encoding, line_start=start,
                line_end=end, quote="\n".join(lines[start-1:end]),
                sha256=hashlib.sha256(raw).hexdigest(), source_identity=identity,
                topic=topic, **extra)

def build():
    rows = []
    for eid, key, a, b, identity, topic in SPANS:
        located = reader.passage(key, a, b)
        rows.append(make_row(eid, located["path"], located["encoding"],
                            located["formal_start"], located["formal_end"],
                            identity, topic, lf_locator=[a, b]))
    for eid, path, a, b, identity, topic in FORMAL_SPANS:
        rows.append(make_row(eid, path, "utf-8", a, b, identity, topic))
    return dict(schema="liuren-bounded-source-study-v1", date="2026-11-05",
                scope="仅本轮所列连续选段；非全书审查；未接入活动规则",
                independent_predictive_validation_count=0, evidence=rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = HERE / "原文证据.json"
    data = build()
    if args.check:
        saved = json.loads(target.read_text(encoding="utf-8"))
        assert saved == data, "Source or exported evidence changed"
        print(json.dumps(dict(text_provenance_ok=True, passages=len(data["evidence"]),
                              source_files=len({r["path"] for r in data["evidence"]}),
                              predictive_validation_count=0), ensure_ascii=False))
        return
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    parts = ["# 裁决依据：原文选段", "", "本文件由 export_evidence.py 生成。行号为原始解码文本 splitlines() 的一基闭区间；原书不改写。证据身份见每段说明。文本核对不等于方法效果验证。", ""]
    for row in data["evidence"]:
        parts += [f'## {row["id"]} {row["topic"]}', "",
                  f'来源：{row["path"]}，正式行 {row["line_start"]}–{row["line_end"]}。',
                  f'身份：{row["source_identity"]}。', f'SHA256：`{row["sha256"]}`', "", "```text", row["quote"], "```", ""]
    (HERE / "原文选段.md").write_text("\n".join(parts), encoding="utf-8")
    print(json.dumps(dict(exported=True, passages=len(data["evidence"]),
                          source_files=len({r["path"] for r in data["evidence"]})), ensure_ascii=False))

if __name__ == "__main__":
    main()
