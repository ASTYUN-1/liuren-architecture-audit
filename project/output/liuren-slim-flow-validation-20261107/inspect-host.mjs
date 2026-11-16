import fs from 'node:fs';
const file='C:/Users/QLMa_/AppData/Local/Programs/@opencode-aidesktop/resources/app.asar/out/main/chunks/node-B5zR-pPr.js';
const text=fs.readFileSync(file,'utf8');
console.log('SERVER_CHUNK',text.length,text.slice(0,400));
const folder=file.slice(0,file.lastIndexOf('/'));
let hits=0;
for(const name of fs.readdirSync(folder)){
 if(!/\.js$/.test(name))continue;
 const s=fs.readFileSync(folder+'/'+name,'utf8');
 for(const term of ['permission:"read"', 'permission: "read"', 'The user has specified a rule which prevents', 'permission: "external_directory"']){
  const at=s.indexOf(term);
  if(at>=0){console.log('MATCH',name,term,s.slice(Math.max(0,at-180),at+550));hits++;}
 }
}
console.log('MATCHES',hits);
let pos=0;
for(let i=0;i<5;i++){
 const at=text.indexOf('new DeniedError',pos);if(at<0)break;
 console.log('DENIAL_CHECK',text.slice(at-850,at+220));pos=at+15;
}
for(const m of text.matchAll(/Wildcard(?:\d+)?\.match/g)){
 const around=text.slice(m.index-100,m.index+200);
 if(/pattern|permission|rule/i.test(around))console.log('WILDCARD',around);
}
const at=text.indexOf('The user has specified a rule which prevents');
for(const term of ['function evaluate3','function match8','evaluate3 =','function fromConfig']){
 const at=text.indexOf(term);if(at>=0)console.log('EXACT',term,text.slice(at,at+1400));
}
const section=text.slice(at-35000,at);
for(const term of ['function evaluate', 'Wildcard.match', 'wildcardMatch', 'normalizePath', 'pattern2']){
 const start=section.lastIndexOf(term);
 if(start>=0)console.log('PERMISSION',term,section.slice(Math.max(0,start-140),start+650));
}
