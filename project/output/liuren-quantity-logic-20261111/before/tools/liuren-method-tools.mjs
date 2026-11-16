// Source-bound deterministic methods. Applicability and final interpretation stay with AI.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildFacts,calculate,seasonal,element,hash,ZHI} from './liuren-deterministic.mjs';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
export const METHOD_REGISTRY=JSON.parse(fs.readFileSync(new URL('./liuren-method-registry.json',import.meta.url),'utf8'));
const fail=m=>{throw Error('LIUREN_METHOD: '+m);};
export function methodCatalog(q){
 if(!q||!['quantity','imagery'].includes(q.kind)||Object.keys(q).some(k=>!['kind','id'].includes(k)))fail('methods requires kind=quantity/imagery and optional id');
 const entries=METHOD_REGISTRY[q.kind].filter(m=>!q.id||m.id===q.id);
 if(!entries.length)fail('unknown method '+q.id);
 return {schema:'liuren-method-catalog-v1',kind:q.kind,methods:entries};
}
function method(kind,id,root){
 const m=METHOD_REGISTRY[kind].find(x=>x.id===id);if(!m)fail('unknown '+kind+' method; query action=methods first');
 const raw=fs.readFileSync(path.join(root,m.source.path));
 if(hash(raw.toString('utf8'))!==m.source.sha256)fail('registered source changed '+m.source.path);
 return m;
}
function targetNode(c,id){
 if(!/^T:[子丑寅卯辰巳午未申酉戌亥]$/.test(id??''))fail('target must be T:支');
 const d=buildFacts(c),n=d.nodes.find(n=>n.symbol===id.slice(2));
 if(!n)fail('target not in chart');return {d,n};
}
function fiveState(n,c,q){
 if(!['four-seasons','quarter-earth'].includes(q.season_profile)||typeof q.basis!=='string'||!q.basis.trim())fail('explicit season_profile and applicability basis required');
 return seasonal(n.symbol,c.month_branch,q.season_profile);
}
const num=(table,symbol)=>({table,symbol:['sheng','cheng'].includes(table)?element(symbol):symbol}),val=value=>({value}),op=(type,...args)=>({op:type,args});
const GEN={贵人:8,螣蛇:4,腾蛇:4,朱雀:9,六合:6,勾陈:5,青龙:7,天空:5,白虎:7,太常:8,玄武:4,太阴:6,天后:9};
export function methodQuantity(c,q,{root=ROOT}={}){
 if(!q||Object.keys(q).some(k=>!['id','target','season_profile','basis','number_table','unit'].includes(k)))fail('unknown quantity_method fields');
 const m=method('quantity',q.id,root),{n}=targetNode(c,q.target);
 if(typeof q.basis!=='string'||!q.basis.trim())fail('method applicability basis required');
 if(q.unit!==undefined&&(typeof q.unit!=='string'||!q.unit.trim()||q.unit.length>40))fail('invalid unit');
 const needsSeason=['CY501-use-ground','WY242-generated-base','LF3329-class-ground'].includes(q.id);
 if(!needsSeason&&q.season_profile!==undefined)fail('this method does not use a seasonal multiplier');
 if(q.id!=='WY244-month'&&q.number_table!==undefined)fail('number_table only used by WY244-month');
 if(!['WY67-shenjiang-base','LF3329-class-ground'].includes(q.id)&&!c.transmissions.some(t=>t.diZhi===n.symbol))fail('this method target must be present in transmissions');
 let state,expression,candidates,stage='method-number',facts={target:q.target,ground:n.ground,general:n.general};
 if(q.id==='CY501-use-ground'){
  if(c.transmissions[0].diZhi!==n.symbol)fail('CY501 requires actual initial transmission as use');
  state=fiveState(n,c,q);const a=num('branch',n.symbol),b=num('branch',n.ground);
  if(state==='旺'){
   expression=op('multiply',a,b);const base=calculate(expression).value;
   candidates=[base*10,base*100];stage='source-scale-candidates';
  }else expression=state==='相'?op('multiply',a,b,val(2)):['囚','死'].includes(state)?op('divide',op('add',a,b),val(2)):op('add',a,b);
 }else if(q.id==='LF3329-class-ground'){
  state=fiveState(n,c,q);const a=num('branch',n.symbol),b=num('branch',n.ground);
  expression=['旺','相'].includes(state)?op('multiply',a,b):['囚','死'].includes(state)?op('divide',op('add',a,b),val(2)):op('add',a,b);
  if(state==='旺')stage='base-only'; // Source gives 倍进 without a resolved multiplier.
 }else if(q.id==='WY67-shenjiang-base'){
  if(!GEN[n.general])fail('general not in WY67 named table');
  expression=op('multiply',num('branch',n.symbol),val(GEN[n.general]));stage='base-only';
  facts.general_number=GEN[n.general];
 }else if(q.id==='WY244-month'){
  if(c.transmissions[0].diZhi!==n.symbol)fail('WY244 requires actual initial transmission as use');
  if(!['branch','sheng','cheng'].includes(q.number_table))fail('WY244 requires number_table=branch/sheng/cheng chosen by source application');
  const b=c.month_branch,broken=ZHI[(ZHI.indexOf(b)+6)%12],factor=n.symbol===b?2:n.symbol===broken?0.5:1;
  expression=op('multiply',num(q.number_table,n.symbol),val(factor));facts.month=b;facts.factor=factor;
 }else if(q.id==='WY242-generated-base'){
  state=fiveState(n,c,q);const table=['旺','相'].includes(state)?'cheng':'sheng';
  expression=num(table,n.symbol);facts.number_table=table;stage='base-only';
 }else fail('method implementation missing');
 const calculated=calculate(expression),unresolved=['量级未由本算式确定'];
 if(!q.unit)unresolved.push('单位');
 if(stage==='base-only')unresolved.push('仅完成本法基础取数，后续步骤未执行');
 if(q.id==='LF3329-class-ground'&&state==='旺')unresolved.push('本段旺气倍进的幅度未定，不自动十倍或百倍');
 if(candidates)unresolved.push('原文350或3500类量级分支，不能择有利值');
 return {schema:'liuren-method-quantity-v1',method:q.id,stage,facts,...(state?{seasonal:state}:{}),
  value:candidates?null:calculated.value,...(candidates?{candidates,base_value:calculated.value}:{}),unit:q.unit??null,unresolved,
  source:m.source,calculation:{expression:calculated.expression,exact_fraction:calculated.exact_fraction},basis:q.basis,
  calculation_scope:{
   included:{seasonal_state:state??null,month_build_break_factor:q.id==='WY244-month'?facts.factor:null,source_formula:q.id},
   composite_strength_index_read:false,void_quantity_adjustment_applied:false,reality_scale_resolved:false,
   next_review:'核综合旺衰、空亡等是否另需有据数量修正；本次未执行不等于本案不需要。另用quantity expression并保留依据，不能同层重复折减。'
  }};
}
export function methodImagery(c,q,{root=ROOT}={}){
 if(!q||Object.keys(q).some(k=>!['id','target','basis','season_profile','reference'].includes(k)))fail('unknown imagery fields');
 const m=method('imagery',q.id,root),{n}=targetNode(c,q.target);
 if(typeof q.basis!=='string'||!q.basis.trim())fail('imagery requires applicability basis');
 if(q.id!=='DF449-growth'&&q.reference!==undefined)fail('reference only used by DF449-growth');
 const matches=[],facts={target:q.target,ground:n.ground,general:n.general};
 if(q.id==='MG104-material'){
  if(q.reference!==undefined)fail('material method does not use reference');
  if(c.transmissions[0].diZhi!==n.symbol)fail('MG104 requires actual initial transmission');
  const state=fiveState(n,c,q),e=element(n.symbol);facts.seasonal=state;facts.element=e;
  const text=e==='木'&&['旺','相'].includes(state)?'木物':e==='木'&&['囚','死'].includes(state)?'草果':e==='金'&&state==='旺'?'五金':e==='金'&&state==='囚'?'石':e==='土'&&['休','囚','死'].includes(state)?'灰尘':null;
  if(text)matches.push({attribute:'材质',candidate:text});
 }else if(q.id==='DF449-growth'){
  if(q.season_profile!==undefined)fail('growth imagery uses named growth, not seasonal score');
  if(!['ground','yin'].includes(q.reference))fail('growth requires reference=ground/yin');
  const s=n.growth[q.reference];facts.reference=q.reference;facts.place=q.reference==='ground'?n.ground:n.direct_yin;facts.growth=s;
  const text={长生:'新小',沐浴:'光泽',冠带:'颜色结扎拷（原文）',临官:'新壮',帝旺:'近贵'}[s];
  if(text)matches.push({attribute:'阶段或外观',candidate:text});
  else if(['衰','病','死','墓','绝','胎','养'].includes(s))matches.push({attribute:'新旧',candidate:'废旧（本段专项取象）'});
 }else if(q.id==='DF75-void'){
  if(q.season_profile!==undefined)fail('void imagery does not use seasonal score');
  facts.self_void=n.void_self;facts.sitting_void=n.void_ground;facts.transmission_slots=n.transmission_slots;
  // Source does not equate sitting void with the transmitted branch itself empty.
  if(n.void_self&&n.transmission_slots.length)matches.push({attribute:'空实',candidate:'空虚或孔窍',positions:n.transmission_slots.map(i=>i===2?'内空':'上空（原文）')});
 }else fail('imagery implementation missing');
 return {schema:'liuren-imagery-v1',method:q.id,facts,matches,source:m.source,basis:q.basis};
}
