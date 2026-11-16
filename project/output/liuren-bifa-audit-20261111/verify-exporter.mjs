// Reproduce selected witnesses through the actual hash-bound page exporter.
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url));
const out=fileURLToPath(new URL('./',import.meta.url));
const rows=JSON.parse(fs.readFileSync(out+'engine-720-geometries.json','utf8'));
const cases=[['乙巳','巳'],['甲子','寅'],['乙卯','寅'],['乙卯','申'],['辛卯','申'],['癸未','卯'],['壬寅','辰'],['辛未','丑']];
const z=[...'子丑寅卯辰巳午未申酉戌亥'];
const results=[];
for(const [day,upper] of cases){
 const geometry=rows.find(x=>x.day===day&&x.day_upper===upper);
 const native_input={yuejiang:'中气换将',guiren:'甲戊庚牛羊',zhouye:'昼贵',shehai:'孟仲季',user:[],cundang:{ws:'',dy:'',fk:'',tag:'bifa-audit-export'},Date:'2026-11-11',Time:'12:00',zhenghuoshi:'四柱',sizhu:{yg:'丙',yz:'午',mz:'亥',dg:day[0],dz:day[1],hz:z[(12-geometry.shift)%12],yuejiang:'子'}};
 const p=spawnSync(process.execPath,['tools/liuren-direct/legacy-engine-worker.mjs'],{cwd:root,input:JSON.stringify({native_input}),encoding:'utf8',env:{...process.env,TZ:'Asia/Shanghai'},timeout:60000,maxBuffer:5_000_000,windowsHide:true});
 if(p.status!==0)throw Error(p.stdout||p.stderr||p.error);
 const reply=JSON.parse(p.stdout);
 if(!reply.ok||reply.result.raw.bifa!==geometry.bifa)throw Error('Exporter differs: '+day+upper);
 results.push({day,day_upper:upper,request:{native_input},raw:reply.result.raw,lookup_matches_page_export:true});
}
fs.writeFileSync(out+'exporter-reproductions.json',JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify({verified:results.length,all_lookup_matches_page_export:results.every(x=>x.lookup_matches_page_export)}));
