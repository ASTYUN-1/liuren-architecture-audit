import test from 'node:test';
import assert from 'node:assert/strict';
import tool from '../../.opencode/tools/liuren_materials.ts';

const context = { sessionID: 'three-book-search-transport', abort: new AbortController().signal };

test('existing native material tool returns original passages in one call', async () => {
  const result = JSON.parse(await tool.execute({action:'book_search',query:'死火 旺金'}, context));
  assert.equal(result.hits[0].book, 'TY');
  assert.ok(result.hits[0].text.includes('死火克不动旺金'));
  assert.equal(result.hits[0].section_complete, true);
  assert.equal(result.coverage.cases_searched, false);
});

test('existing native tool supports batched disputes and chapter outline', async () => {
  const batch = JSON.parse(await tool.execute({action:'book_search',queries:['死火 旺金','神将互换'],limit:2}, context));
  assert.ok(batch.literal_query_coverage.every(q => q.returned_hits > 0));
  const outline = JSON.parse(await tool.execute({action:'book_outline',book:'RG'}, context));
  assert.equal(outline.books[0].id, 'RG');
  assert.ok(outline.books[0].sections.some(s => s.title.includes('察用神之生克')));
});

test('book search never accepts arbitrary source paths or disabled libraries', async () => {
  await assert.rejects(() => tool.execute({action:'book_search',query:'空亡',book:'../docs'}, context));
  await assert.rejects(() => tool.execute({action:'scan',library:'cases',query:'空亡'}, context));
  await assert.rejects(() => tool.execute({action:'read',path:'opencode.json'}, context));
});

test('action-specific limits fail locally with the exact field instead of triggering a broad retry',async()=>{
 await assert.rejects(()=>tool.execute({action:'book_search',query:'空亡',limit:13},context),/liuren_materials.limit.*1\.\.12/);
 await assert.rejects(()=>tool.execute({action:'retrieve',query:'空亡',limit:51},context),/liuren_materials.limit.*1\.\.50/);
});

test('native material schema and execution accept each newly registered book',async()=>{
 for(const [book,query] of [['QA','症候'],['KN','类神'],['TR','应聘'],['KE','禄为工作']]){
  const result=JSON.parse(await tool.execute({action:'book_search',book,query,limit:1},context));
  assert.ok(result.hits.length,book);
  assert.equal(result.hits[0].book,book);
  const outline=JSON.parse(await tool.execute({action:'book_outline',book},context));
  assert.equal(outline.books[0].id,book);
 }
});
