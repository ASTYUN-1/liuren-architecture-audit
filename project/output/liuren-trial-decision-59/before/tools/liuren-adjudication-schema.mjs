// Shared native/contract scalar limits. IDs refer to records, not divination roles.
export const ID_PATTERN=/^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
export const OBSERVATION_KINDS=['five_qi','twelve_states','relation','void','shenjiang','shensha','structure','movement','special_method'];
export const OBSERVATION_VERIFICATIONS=['method_interpretation','unverified'];
export const PACKET_ID_HELP='所有数组的id全局唯一：questions用Q_、facts用F_、entities用S_、observations用O_、method_materials保留工具handoff的M_/B_、focus_issues用I_；不要把事实和争点都编号F01。E数字和D_留给程序。';
// Validate in execute as well as advertising the schema: hosts/providers may
// hand malformed arguments directly to custom tools. Never rely on publication.
export function parsePacketArguments(schema,args){
 const parsed=schema.safeParse(args),issues=[];
 if(!parsed.success)for(const issue of parsed.error.issues)issues.push({
  path:'/'+issue.path.join('/'),code:issue.code,message:issue.message,
  ...(issue.values?{allowed:issue.values}:{})
 });
 const p=args?.packet,seen=new Map();
 for(const field of ['questions','facts','entities','observations','method_materials','focus_issues']){
  if(!Array.isArray(p?.[field]))continue;
  for(const [i,row] of p[field].entries())if(typeof row?.id==='string'){
   const at='/packet/'+field+'/'+i+'/id';
   if(seen.has(row.id))issues.push({path:at,code:'duplicate_id',received:row.id,conflicts_with:seen.get(row.id),message:PACKET_ID_HELP});
   else seen.set(row.id,at);
  }
 }
 if(issues.length)throw new Error('LIUREN_PACKET_ARGUMENTS: '+JSON.stringify({issues,action:'一次修正所列字段并保留其余材料；同步修改受影响的结构化ID引用。不删材料试探、不换课盘hash、不重新分析。参数不明用liuren_tool_help topic=packet。'}));
 return parsed.data;
}
export function contractScalars(s){
 const text=(max=6000)=>s.string().min(1).max(max).regex(/\S/,'must contain non-whitespace text');
 return {text,id:()=>s.string().regex(ID_PATTERN),texts:()=>s.array(text()).max(100)};
}

// Only normalize an unambiguous transport envelope, never review content.
export function parseResultArguments(schema,args){
 const value=structuredClone(args);
 if(value?.action==='review'&&(value.report_sha256!==undefined||value.checks!==undefined)){
  if(value.review!==undefined)throw Error('LIUREN_RESULT_ARGUMENTS: review与顶层report_sha256/checks不能同时给出；使用{action:"review",task_id,review:{report_sha256,checks}}');
  value.review={report_sha256:value.report_sha256,checks:value.checks};delete value.report_sha256;delete value.checks;
 }
 const parsed=schema.safeParse(value);
 if(!parsed.success)throw Error('LIUREN_RESULT_ARGUMENTS: '+JSON.stringify({issues:parsed.error.issues.map(e=>({path:'/'+e.path.join('/'),code:e.code,message:e.message})),help:{tool:'liuren_tool_help',arguments:{topic:'result',...(args?.task_id?{task_id:args.task_id}:{})}}}));
 const data=parsed.data;
 if(data.action==='review'&&!data.review||data.action==='recheck'&&!data.findings)throw Error('LIUREN_RESULT_ARGUMENTS: action='+data.action+'须填写同名'+(data.action==='review'?'review对象':'findings数组')+'；参数见liuren_tool_help(topic="result")');
 if(data.action!=='review'&&data.review!==undefined||data.action!=='recheck'&&data.findings!==undefined||data.action!=='deliver'&&data.report_sha256!==undefined||data.checks!==undefined)throw Error('LIUREN_RESULT_ARGUMENTS: 含当前action不使用的字段；read/locate只填action及task_id，review填review，recheck填findings，deliver可带当前报告hash。');
 return data;
}
