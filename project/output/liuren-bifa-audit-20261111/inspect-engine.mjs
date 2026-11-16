// Read-only engine inspection; do not alter the engine, active runtime or rules.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
const OUT=path.dirname(fileURLToPath(import.meta.url));
const read=rel=>fs.readFileSync(path.join(ROOT,rel),'utf8');
const write=(name,v)=>fs.writeFileSync(path.join(OUT,name),JSON.stringify(v,null,2)+'\n');
const noop=()=>{};
const ctx=vm.createContext({console:{log:noop,warn:noop,error:noop},window:{addEventListener:noop,indexedDB:{open:()=>({})}},
 document:{addEventListener:noop},setTimeout:noop,clearTimeout:noop,setInterval:noop,clearInterval:noop,
 vm_glob:{USER_ALL_DATA:{pages_config:{zhuti_config:{zhuti_bord_clor:'#cccccc'}}}}});
for(const name of ['js/lunar.js','js/data.js','js/hexin.js','js/api.js','js/guize.js','js/paipan.js'])vm.runInContext(read('排盘工具魔改/'+name),ctx,{filename:name,timeout:15000});
const index=read('排盘工具魔改/index.js');
const start=index.indexOf('function getCurrentSolarTerm('),end=index.indexOf('function enterFullscreenElement(',start);
vm.runInContext(index.slice(start,end),ctx,{timeout:15000});
const GAN=[...'甲乙丙丁戊己庚辛壬癸'],ZHI=[...'子丑寅卯辰巳午未申酉戌亥'];
const days=Array.from({length:60},(_,i)=>GAN[i%10]+ZHI[i%12]);
const entries=[];
for(const day of days)for(const day_upper of ZHI)entries.push({day,day_upper,text:ctx.GetBiFa(day,day_upper)??null});
write('engine-bifa-lookup-720.json',entries);
fs.writeFileSync(path.join(OUT,'GetBiFa-source.js'),vm.runInContext('GetBiFa.toString()',ctx));
const inp={yuejiang:'中气换将',guiren:'甲戊庚牛羊',zhouye:'自动选择',shehai:'孟仲季',user:[],cundang:{ws:'',dy:'',fk:'',tag:'bifa-audit'},
 Date:'2026-11-11',Time:'12:00',zhenghuoshi:'四柱',sizhu:{yg:'丙',yz:'午',mz:'亥',dg:'甲',dz:'子',hz:'子',yuejiang:'子'}};
ctx.__auditInput=inp;
vm.runInContext('__auditInput=JSON.parse(JSON.stringify(__auditInput)); __auditP=LiuRenPaiPan(__auditInput)',ctx,{timeout:20000});
const P=ctx.__auditP;
const keys=Object.keys(P);
const selected=JSON.parse(JSON.stringify(Object.fromEntries(['sizhu','sike','sanchuan','tianpan','shenpan','BiFa','KeJing','ZhiZhi'].map(k=>[k,P[k]]))));
write('engine-sample-native.json',{keys,selected});
const bookMeta=vm.runInContext('ZiLiao.filter(x=>/毕法/.test(x.title)).map(x=>({title:x.title,id:x._id,chars:x.zhengwen.length}))',ctx);
write('engine-book-metadata.json',bookMeta);
const homes={甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'};
const geometry=[];
for(const day of days)for(const day_upper of ZHI){
 const shift=(ZHI.indexOf(day_upper)-ZHI.indexOf(homes[day[0]])+12)%12;
 ctx.__auditInput={...inp,sizhu:{...inp.sizhu,dg:day[0],dz:day[1],hz:ZHI[(12-shift)%12]}};
 vm.runInContext('__auditInput=JSON.parse(JSON.stringify(__auditInput)); __auditP=LiuRenPaiPan(__auditInput)',ctx,{timeout:20000});
 const p=ctx.__auditP;
 if(p.sike[0][1]!==day_upper||p.BiFa!==ctx.GetBiFa(day,day_upper))throw Error('Lookup argument mismatch '+day+day_upper);
 geometry.push(JSON.parse(JSON.stringify({day,day_upper,shift,sizhu:p.sizhu,sike:p.sike,sanchuan:p.sanchuan,tianpan:p.tianpan,shenpan:p.shenpan,xunkong:p.xunkong,
  xungan:p.xungan,richangsheng:p.richangsheng,branch_growth:p._zi_cs,shensha:p.shensha_list,bifa:p.BiFa})));
}
write('engine-720-geometries.json',geometry);
console.log(JSON.stringify({bookMeta,lookup_entries:entries.length,nonempty:entries.filter(x=>x.text).length,unique_texts:new Set(entries.map(x=>x.text)).size,
 geometry_count:geometry.length,lookup_argument_verified:'GetBiFa(日柱,干上神) for all 720',sample:entries.find(x=>x.text)},null,2));
