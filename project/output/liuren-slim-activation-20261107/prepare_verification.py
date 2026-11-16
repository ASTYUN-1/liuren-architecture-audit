from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
CAND=ROOT/'output/liuren-slim-candidate-20261107'
text=(CAND/'integration_check.mjs').read_text('utf-8')
text=text.replace("const root=path.join(folder,'candidate');","const root=project;")
text=text.replace("'./candidate/","'../../")
text=text.replace('候选','活动精简版')
(OUT/'integration_check.mjs').write_text(text,encoding='utf-8',newline='')
text=(CAND/'validate_skill_entry.mjs').read_text('utf-8')
text=text.replace("path.join(out,'candidate/.opencode/skills/liuren',name,'SKILL.md')","path.join(project,'.opencode/skills/liuren',name,'SKILL.md')")
(OUT/'validate_skill_entry.mjs').write_text(text,encoding='utf-8',newline='')
