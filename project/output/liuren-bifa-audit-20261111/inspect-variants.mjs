// Audit evidence only. Original engine files and runtime remain untouched.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
const OUT=path.dirname(fileURLToPath(import.meta.url));
const read=rel=>fs.readFileSync(path.join(ROOT,rel),'utf8');
const noop=()=>{};
const ctx=vm.createContext({console:{log:noop,warn:noop,error:noop},window:{addEventListener:noop,indexedDB:{open:()=>({})}},document:{addEventListener:noop},setTimeout:noop,clearTimeout:noop,setInterval:noop,clearInterval:noop,vm_glob:{USER_ALL_DATA:{pages_config:{zhuti_config:{zhuti_bord_clor:'#cccccc'}}}}});
for(const name of ['js/lunar.js','js/data.js','js/hexin.js','js/api.js','js/guize.js','js/paipan.js'])vm.runInContext(read('排盘工具魔改/'+name),ctx,{filename:name,timeout:15000});
const index=read('排盘工具魔改/index.js');
const start=index.indexOf('function getCurrentSolarTerm('),end=index.indexOf('function enterFullscreenElement(',start);
vm.runInContext(index.slice(start,end),ctx,{timeout:15000});
const GAN=[...'甲乙丙丁戊己庚辛壬癸'],ZHI=[...'子丑寅卯辰巳午未申酉戌亥'];
const homes={甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'};
const base={yuejiang:'中气换将',guiren:'甲戊庚牛羊',zhouye:'昼贵',shehai:'孟仲季',user:[],cundang:{ws:'',dy:'',fk:'',tag:'bifa-audit'},Date:'2026-11-11',Time:'12:00',zhenghuoshi:'四柱',sizhu:{yg:'丙',yz:'午',mz:'亥',dg:'甲',dz:'子',hz:'子',yuejiang:'子'}};
const rows=[];
for(let i=0;i<60;i++)for(const day_upper of ZHI)for(const mode of ['昼贵','夜贵']){
 const day=GAN[i%10]+ZHI[i%12],shift=(ZHI.indexOf(day_upper)-ZHI.indexOf(homes[day[0]])+12)%12;
 ctx.__input={...base,zhouye:mode,sizhu:{...base.sizhu,dg:day[0],dz:day[1],hz:ZHI[(12-shift)%12]}};
 vm.runInContext('__input=JSON.parse(JSON.stringify(__input)); __p=LiuRenPaiPan(__input)',ctx,{timeout:20000});
 const p=ctx.__p;
 if(p.sike[0][1]!==day_upper)throw Error('day upper mismatch');
 rows.push(JSON.parse(JSON.stringify({day,day_upper,mode,engine_mode:p.zhouye_type,sike:p.sike,sanchuan:p.sanchuan,shenpan:p.shenpan,bifa:p.BiFa})));
}
fs.writeFileSync(path.join(OUT,'engine-day-night-1440.json'),JSON.stringify(rows,null,2)+'\n');
console.log(JSON.stringify({count:rows.length,modes:[...new Set(rows.map(x=>x.engine_mode))],sample:rows.slice(0,2)},null,2));
