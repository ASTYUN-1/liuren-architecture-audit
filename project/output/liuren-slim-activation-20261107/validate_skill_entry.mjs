// Fallback for missing Python PyYAML: parse real YAML with the existing host dependency.
// This does not claim the Python quick_validate script passed.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const out=path.dirname(fileURLToPath(import.meta.url));
const project=path.resolve(out,'../..');
const require=createRequire(path.join(project,'.opencode/package.json'));
const YAML=require('yaml');const checks=[];
for(const name of ['daliuren','liuren-cases','liuren-extract']){
 const file=path.join(project,'.opencode/skills/liuren',name,'SKILL.md');
 const text=(await fs.readFile(file,'utf8')).replaceAll('\r\n','\n');const match=/^---\n([\s\S]*?)\n---/.exec(text);
 assert.ok(match,'YAML frontmatter required');
 const document=YAML.parseDocument(match[1],{uniqueKeys:true});assert.deepEqual(document.errors,[]);
 const value=document.toJS();assert.equal(typeof value,'object');assert.ok(!Array.isArray(value));
 assert.deepEqual(Object.keys(value).sort(),['description','name']);assert.equal(value.name,name);
 assert.match(name,/^[a-z0-9]+(?:-[a-z0-9]+)*$/);assert.ok(name.length<=64);
 assert.equal(typeof value.description,'string');assert.ok(value.description.length<=1024);
 assert.ok(!/[<>]/.test(value.description));assert.ok(!/^\s*\[TODO:/m.test(text));
 checks.push({skill:name,passed:true,parser:'existing Node yaml; independent fallback, not Python quick_validate'});
}
await fs.writeFile(path.join(out,'skill-validation.json'),JSON.stringify({officialQuickValidate:{passed:false,reason:'ModuleNotFoundError: yaml; attempted with system and bundled Python'},fallbackChecks:checks},null,2)+'\n');
console.log(JSON.stringify({passed:checks.length,officialScriptPassed:false,checks},null,2));
