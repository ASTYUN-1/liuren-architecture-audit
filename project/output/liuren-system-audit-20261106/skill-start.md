# Plugin Eval Start Here: daliuren

## At a Glance
- Recommended path: Evaluate Skill
- Benchmark config present: no
- Usage log present: no
- Quick local entrypoint: `plugin-eval start ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --request '审查本机大六壬Skill与工具及完整主子流程的适配，排查调用失败、重复和规则冲突' --format markdown`
- First local command: `plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown`

## Why It Matters
- Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.
- Plugin Eval recommended Evaluate Skill from the current local state for this skill.

## Fix First
- Start with the recommended path before branching into secondary workflows.

## Recommended Next Step
- Evaluate Skill
- Why: Plugin Eval recommended Evaluate Skill from the current local state for this skill.
- Chat request: "审查本机大六壬Skill与工具及完整主子流程的适配，排查调用失败、重复和规则冲突"
- Local command: `plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown`

## Details
<details>
<summary>Full local sequence</summary>

- plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown
</details>
<details>
<summary>Other chat requests</summary>

- Full Skill Analysis: "Give me a full analysis of this skill, including benchmark setup." -> plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown
- Evaluate Skill: "Evaluate this skill." -> plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown
- Explain Token Budget: "Explain the token budget for this skill." -> plugin-eval explain-budget ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown
- Measure Real Token Usage: "Measure the real token usage of this skill." -> plugin-eval init-benchmark ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren
- Benchmark With Starter Scenarios: "Help me benchmark this skill." -> plugin-eval init-benchmark ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren
- Start Here: "What should I run next?" -> plugin-eval analyze ~/Documents/六壬八字测算/.opencode/skills/liuren/daliuren --format markdown
</details>
