// Maintained shensha calculation/export layer for the current chart engine.
// The legacy engine stays byte-identical for source-bound historical replay.
export function correctEngineShensha(facts, policy, resolution) {
  const output=structuredClone(facts);
  const managed=new Set([...policy.rules.flatMap(r=>r.aliases),...policy.disabled]);
  const changes=[];
  const ruleById=new Map(policy.rules.map(r=>[r.id,r]));
  const rawRows=facts.heaven_earth||[];
  for(const row of output.heaven_earth||[]) {
    row.shensha=(row.shensha||[]).filter(name=>!managed.has(name));
  }
  for(const item of resolution.items) {
    if(item.status!=='resolved')continue;
    const rule=ruleById.get(item.id);
    // Only 小耗 needs explicit year/month names: per-palace legacy arrays erase group identity.
    const names=item.id==='S08'?['岁小耗']:item.id==='S08M'?['月天鼠小耗']:
      [...new Set([rule.aliases[0],...rule.aliases.filter(a=>rawRows.some(r=>r.shensha?.includes(a)))])];
    const old=[...new Set(rawRows.filter(r=>r.shensha?.some(n=>rule.aliases.includes(n))).map(r=>r.tian))];
    const target=item.places.map(p=>p.tian);
    if(old.length!==target.length || target.some(b=>!old.includes(b))) changes.push({id:item.id,name:rule.name,
      original_heaven_branches:old,corrected_heaven_branches:target});
    for(const place of item.places) {
      const row=output.heaven_earth.find(r=>r.tian===place.tian);
      if(!row || row.di!==place.di)throw new Error('神煞所属天盘支/所临地盘不一致，停止导出');
      for(const name of names)if(!row.shensha.includes(name))row.shensha.push(name);
    }
  }
  return {facts:output,changes};
}

export function correctedRawExport(originalRaw, correctedFacts) {
  const raw=structuredClone(originalRaw);
  if(!Array.isArray(raw.tiandipan))throw new Error('原始引擎缺少完整天地盘');
  for(const row of raw.tiandipan) {
    const corrected=correctedFacts.heaven_earth.find(r=>r.tian===row.tian && r.di===row.di);
    if(!corrected)throw new Error('原始导出与修正版坐标不一致');
    row.shensha=[...corrected.shensha];
  }
  // Preserve the original summary's name coverage, rebuilding positions from 天盘 only.
  const wanted=new Set((raw.keyShensha||[]).map(r=>r.name));
  raw.keyShensha=[];
  for(const row of raw.tiandipan)for(const name of row.shensha)if(wanted.has(name))raw.keyShensha.push({name,at:row.tian});
  return raw;
}
