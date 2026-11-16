// Inventory, deduplicate against the local corpus, then export only missing books.
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const OUT=path.join(ROOT,'output/engine-books-export-20261109');
const DEST=path.join(ROOT,'书籍库/排盘引擎内置资料');
const sha=b=>createHash('sha256').update(b).digest('hex');
const read=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const norm=s=>s.normalize('NFKC').replace(/[^\p{L}\p{N}]/gu,'');
const rel=p=>path.relative(ROOT,p).replaceAll('\\','/');
const safe=s=>s.replace(/[<>:"/\\|?*\u0000-\u001f]/g,'').replace(/[《》]/g,'').trim();
async function save(file,bytes){
 await fs.mkdir(path.dirname(file),{recursive:true});
 try{await fs.writeFile(file,bytes,{flag:'wx'});}catch(e){if(e.code!=='EEXIST'||!Buffer.from(await fs.readFile(file)).equals(Buffer.from(bytes)))throw Error('拒绝覆盖已有不同内容 '+file);}
}
const json=(file,value)=>save(file,JSON.stringify(value,null,2)+'\n');
async function walk(p){
 const rows=[];for(const e of await fs.readdir(p,{withFileTypes:true})){const f=path.join(p,e.name);if(e.isDirectory())rows.push(...await walk(f));else if(/\.(txt|md)$/i.test(f))rows.push(f);}return rows;
}
const engine=path.join(ROOT,'排盘工具魔改/js/data.js'),bytes=await fs.readFile(engine),engineHash=sha(bytes);
const ctx=vm.createContext({console:{log(){},warn(){},error(){}}});
vm.runInContext(bytes.toString('utf8'),ctx,{filename:'engine-data.js',timeout:15000});
const raw=JSON.parse(vm.runInContext('JSON.stringify(ZiLiao)',ctx,{timeout:5000}));
if(!Array.isArray(raw)||raw.some(x=>typeof x.title!=='string'||typeof x.zhengwen!=='string'))throw Error('engine book schema changed');
// Python stdlib HTMLParser decodes named/numeric entities and preserves paragraph/table order.
const books=JSON.parse(execFileSync(process.env.LIUREN_PYTHON??'python',['-X','utf8',path.join(ROOT,'tools/liuren_engine_book_text.py')],
 {input:JSON.stringify(raw),encoding:'utf8',maxBuffer:32*1024*1024,timeout:30000,windowsHide:true}));
const manifest=await read(path.join(ROOT,'output/liuren-knowledge-20261102/manifest.json'));
const localFiles=new Set((await walk(path.join(ROOT,'书籍库'))).filter(p=>!p.startsWith(DEST+path.sep)));
for(const a of manifest.assets.filter(a=>a.kind==='book_text'))localFiles.add(path.resolve(ROOT,a.path));
const local=[],missingRegistered=[];
for(const f of [...localFiles].sort()){
 if(!f.startsWith(ROOT)||f.startsWith(DEST+path.sep))continue;
 let b;try{b=await fs.readFile(f);}catch(e){if(e.code!=='ENOENT')throw e;missingRegistered.push(rel(f));continue;}
 let text,encoding='utf-8';
 try{text=new TextDecoder('utf-8',{fatal:true}).decode(b);}catch{try{text=new TextDecoder('gb18030',{fatal:true}).decode(b);encoding='gb18030';}catch{throw Error('本地书籍编码无法确认 '+f);}}
 local.push({path:rel(f),sha256:sha(b),encoding,chars:text.length,normalized:norm(text),title:norm(path.basename(f))});
}
// Known title aliases are book-level decisions: the user asked to skip books
// already held, rather than exporting every engine edition and every volume.
const aliases=[
 [/六壬大全/,'书籍库/经典古籍/明代/六壬大全-明-郭载騋.txt'],
 [/管辂神书/,'书籍库/经典古籍/唐宋/六壬管辂神书-三国-管辂.txt'],
 [/括囊赋/,'书籍库/经典古籍/佚名/六壬括囊赋略疏--.txt'],
 [/灵觉经/,'书籍库/经典古籍/佚名/六壬灵觉经--佚名.txt'],
 [/六壬秘本/,'书籍库/经典古籍/清代/六壬秘本-清-金正音.txt'],
 [/苗公射覆鬼撮脚/,'书籍库/经典古籍/佚名/六壬苗公射覆鬼撮脚-utf8.txt'],
 [/玉藻金英/,'书籍库/经典古籍/大六壬玉藻金英.txt'],
 [/六壬存验/,'书籍库/经典古籍/清代/六壬存验-清-吴师青.txt'],
 [/六壬粹言/,'书籍库/经典古籍/清代/六壬粹言-清-刘赤江.txt'],
 [/六壬金铰剪/,'书籍库/经典古籍/佚名/六壬金铰剪--徐养浩.txt'],
 [/六壬经纬/,'书籍库/经典古籍/清代/六壬经纬-清-京江铁瓮子.txt'],
 [/六壬论命秘要/,'书籍库/经典古籍/佚名/六壬论命秘要--佚名.txt'],
 [/六壬神定经/,'书籍库/经典古籍/唐宋/六壬神定经-宋-扬维德.txt'],
 [/六壬银河櫂/,'书籍库/经典古籍/佚名/六壬银河櫂-utf8.txt'],
 [/六壬直指御定|御定六壬直指/,'书籍库/经典古籍/清代/六壬直指御定-清-佚名.txt'],
 [/^壬归$/,'书籍库/经典古籍/佚名/壬归.txt'],
 [/壬学琐记/,'书籍库/经典古籍/清代/壬学琐记-清-程树勋.txt'],
 [/集成五要权衡/,'书籍库/经典古籍/佚名/六壬集成五要权衡--佚名.txt'],
 [/六壬断案/,'书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt'],
 [/六壬神课金口诀古本/,'书籍库/经典古籍/佚名/六壬神课金口诀古本--佚名.txt'],
 [/六壬指南/,'书籍库/经典古籍/明代/六壬指南-明-陈公献.txt'],
 [/一字玉连环/,'书籍库/经典古籍/唐宋/六壬一字诀玉连环-宋-徐汶滨.txt'],
 [/大六壬心境/,'书籍库/经典古籍/唐宋/六壬心镜-唐-徐道符.txt'],
 [/六十四课经/,'书籍库/北海闲人/北海闲人-大六门64课经精讲解注.txt']
];
const rows=[];
for(const [i,b]of books.entries()){
 const title=b.title.trim(),key=norm(title),n=norm(b.text);
 const samples=[...new Set(Array.from({length:24},(_,i)=>n.slice(Math.floor(Math.max(0,n.length-64)*i/23),Math.floor(Math.max(0,n.length-64)*i/23)+64)).filter(x=>x.length>=40))];
 const ranked=local.map(l=>({path:l.path,hits:samples.filter(s=>l.normalized.includes(s)).length,total:samples.length})).sort((a,b)=>b.hits-a.hits);
 const best=ranked[0],alias=aliases.find(([rx])=>rx.test(key)),matched=alias?local.find(l=>l.path===alias[1]):null;
 if(alias&&!matched)throw Error('已知别名的本地来源不存在 '+alias[1]);
 const duplicate=matched?.path??(samples.length>=8&&best?.hits===samples.length?best.path:null);
 rows.push({index:i,id:b._id,title,source_html_sha256:sha(b.zhengwen),text_sha256:sha(b.text),text_chars:b.text.length,images:b.images,
  decision:duplicate?'skip_existing':'export',existing:duplicate,
  basis:matched?'本地已持有同书或收录该书正文的注本；按用户要求不另出引擎版本':duplicate?'规范化正文所有取样均匹配本地来源；只作重复筛查，不宣称逐字校勘':'本地文件名、已登记书籍全文及正文取样未发现同书全文；片段引用不作为已有全书',
  best_content_matches:ranked.filter(x=>x.hits>0).slice(0,3),
  output:duplicate?null:rel(path.join(DEST,safe(title)+'.txt'))});
}
await json(path.join(OUT,'本地书籍核查.json'),{existing:local.map(({normalized,title,...x})=>x),missing_registered:missingRegistered});
await json(path.join(OUT,'引擎书目与去重决定.json'),{source:rel(engine),source_sha256:engineHash,records:rows});
if(!process.argv.includes('--export')){console.log(JSON.stringify({mode:'inventory-only',local:local.length,engine:rows.length,export:rows.filter(r=>r.decision==='export').map(r=>({index:r.index,title:r.title,matches:r.best_content_matches})),skip:rows.filter(r=>r.decision==='skip_existing').length},null,2));process.exit(0);}
for(const r of rows.filter(r=>r.decision==='export')){
 const b=books[r.index];
 const text=r.title+'\n来源：本机排盘引擎内置资料；正文原样转为纯文本，未校勘。\n'+
  (r.images.length?'含'+r.images.length+'处原文图片；TXT仅标出图片位置，未转录图中课式。\n':'')+'\n'+b.text;
 await save(path.join(ROOT,r.output),text);r.output_sha256=sha(text);
}
for(const l of local)if(sha(await fs.readFile(path.join(ROOT,l.path)))!==l.sha256)throw Error('本地原书发生变化 '+l.path);
if(sha(await fs.readFile(engine))!==engineHash)throw Error('引擎源发生变化');
await json(path.join(OUT,'导出验收.json'),{source_sha256:engineHash,local_books_checked:local.length,engine_records:rows.length,
 exported:rows.filter(r=>r.decision==='export'),skipped:rows.filter(r=>r.decision==='skip_existing'),source_and_existing_books_unchanged:true,
 active_workflow_changed:false,images_transcribed:false,semantic_full_book_review:false});
console.log(JSON.stringify({exported:rows.filter(r=>r.decision==='export').length,skipped:rows.filter(r=>r.decision==='skip_existing').length,destination:DEST}));
