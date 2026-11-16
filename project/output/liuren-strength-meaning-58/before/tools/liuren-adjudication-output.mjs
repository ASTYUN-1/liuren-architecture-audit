// Report transport only. Professional reasoning is not a submission schema.
export const ENTITY_PATTERN=/^(?:[甲乙丙丁戊己庚辛壬癸]|[子丑寅卯辰巳午未申酉戌亥]{1,12}|[甲乙丙丁戊己庚辛壬癸][（(]寄宫[子丑寅卯辰巳午未申酉戌亥][）)])$/;
export const MAX_REPORT_BYTES=1024*1024;
export const SUBMISSION_GUIDE='优先提交{result:完整Markdown正文字符串}；也兼容自由JSON对象。不要传value，不把整个工具参数转成JSON字符串；JSON报错只修对应引号/括号，保持原报告，不重新权衡。原样保存，不要求固定分析字段；依据、反证、条件题、应期取数按本问自然说明。新协议只要求读完核心，参考按具体缺口查证，不要求逐项读完；旧文件仍完整读原文件。成功后只回小回执。程序接收不代表专业判断正确。';
export function createOutputSchema(s){
 return s.union([s.string().min(1),s.record(s.string(),s.unknown())]).describe(SUBMISSION_GUIDE);
}
export function parseSubmissionText(raw){
 let value=String(raw??'').trim();
 const wrapped=value.match(/<task_result>\s*([\s\S]*?)\s*<\/task_result>/);
 if(wrapped)value=wrapped[1].trim();
 const fenced=value.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/);
 try{return JSON.parse(fenced?fenced[1]:value);}catch{return value;}
}
export function checkSubmission(root,raw,p){
 // Never mutate, complete or interpret professional report fields here.
 const bad=expected=>({ok:false,issues:[{path:'/result',code:'report_transport',expected}],repairs:[]});
 if(typeof raw==='string'?!raw.trim():!raw||typeof raw!=='object'||Array.isArray(raw)||!Object.keys(raw).length)return bad('非空正文字符串或自由JSON对象');
 let encoded;
 try{encoded=JSON.stringify(raw);}catch{return bad('可保存为JSON的正文或对象');}
 if(Buffer.byteLength(encoded,'utf8')>MAX_REPORT_BYTES)return bad('报告传输上限1 MiB；缩短重复内容，保留实际判断');
 return {ok:true,status:raw?.status==='needs_input'?'needs_input':'completed',result:structuredClone(raw),issues:[],repairs:[],validationScope:'transport-only',professionalContentChecked:false};
}
export function reportMarkdown(r){
 if(typeof r==='string')return r;
 return '```json\n'+JSON.stringify(r,null,2)+'\n```';
}
