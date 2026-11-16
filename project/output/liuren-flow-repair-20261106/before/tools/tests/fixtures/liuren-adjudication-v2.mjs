// Synthetic interface fixture. This is not a professional or prediction test.
import {resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
export const codeRoot=resolve(process.env.LIUREN_TEST_CODE_ROOT??fileURLToPath(new URL('../../../',import.meta.url)));
export const moduleURL=path=>pathToFileURL(resolve(codeRoot,path)).href;
export function packet(){
  const branches=[...'子丑寅卯辰巳午未申酉戌亥'];
  return {
    schema:'liuren-adjudication-input-v2',request_id:'synthetic_v2',
    questions:[{id:'Q1',text:'合成接口问题',subject:'测试对象',stage:'测试',deadline:'未限定',success_criteria:'只检查接口',alternatives:[]}],
    chart:{source:'合成测试盘，禁止用于专业判断',facts:{
      schema:'liuren-chart-facts-v1',pillars:['丙午','丙申','庚戌','癸未'],day_stem:'庚',day_branch:'戌',month_branch:'申',hour_branch:'未',month_general:'午',void_branches:['寅','卯'],
      heaven_earth:branches.map(b=>({di:b,tian:b,tianjiang:'贵人'})),
      lessons:branches.slice(0,4).map((b,i)=>({index:i+1,tianpan:b,dizhi:b,tianjiang:'贵人'})),
      transmissions:branches.slice(0,3).map((b,i)=>({index:i+1,diZhi:b,tianjiang:'贵人',liuqin:'父母'}))}},
    facts:[],entities:[{id:'S1',question_ids:['Q1'],referent:'测试对象',branch:'子',position:'测试位置',mapping_basis:'合成映射'}],
    observations:[{id:'O1',entity_ids:['S1'],kind:'relation',statement:'合成关系，未验证作用',reference:'S1自身',source:'合成盘',verification:'unverified'}],
    method_materials:[],focus_issues:[{id:'C1',question_ids:['Q1'],entity_ids:['S1'],observation_ids:['O1'],question:'该关系是否有效影响本问？'}],unknowns:[]};
}
export function result(){return {
  schema:'liuren-adjudication-output-v2',request_id:'synthetic_v2',status:'completed',
  scope_review:{question_ids:['Q1'],mapping_status:'confirmed',added_entity_ids:[],corrections:[],omission_check:'合成查漏记录，仅测字段'},
  entity_checks:[{id:'S1',referent:'测试对象',branch:'子',position:'测试位置',mapping_review:'合成取用复核',five_qi:'合成状态',twelve_states:'合成十二气参照',site_yin:'合成位置',shenjiang:'合成神将',limits:[]}],
  relation_checks:[{id:'R1',from:'S1',to:'S1',relation:'合成关系',validity:'limited',basis_ids:['O1'],reason:'合成作用摘要，不构成专业规则',effect_scope:['接口测试']}],
  issue_resolutions:[{issue_id:'C1',status:'resolved',relation_ids:['R1'],resolution:'合成取舍',limits:[]}],
  answers:[{question_id:'Q1',verdict:'接口测试通过',precision:'direction',decisive_relation_ids:['R1'],counter_relation_ids:[],counter_resolution:'合成反证检查',process:'不适用',timing:'不适用',conditions:[],limits:[]}],
  source_conflicts:[],missing_inputs:[]};}
