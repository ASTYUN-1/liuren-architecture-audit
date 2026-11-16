state={'main':0,'calls':0,'childReadCalls':0,'childPages':0,'finished':False,'archive':None,'receipt':None}
events=[];failures=[];expected=[];checks=[];wire=[]
report='# 合成流程验收正文\n\n本报告只验工具与交接，不提供预测。日期：2026-11-03辛巳；计算：8×6=48。\n来源与限制完整保留。'
question='电脑维修能否完成？何时修好？费用多少？本次仅作工具流程测试，不提供真实反馈，不验证预测。'
def content(m):
 v=m.get('content','');return v if isinstance(v,str) else '\n'.join(x.get('text','') for x in v if isinstance(x,dict))
def parsed(m):
 text=content(m)
 try:return json.loads(text)
 except ValueError:
  a=text.find('{');b=text.rfind('}')
  if a<0:raise ValueError('Expected JSON tool receipt: '+text[:1500])
  return json.loads(text[a:b+1])
def call(name,args):
 state['calls']+=1
 return {'id':'slim_native_'+str(state['calls']),'type':'function','function':{'name':name,'arguments':json.dumps(args,ensure_ascii=False)}}
def emit(calls):
 global expected
 expected=[(c['id'],c['function']['name']) for c in calls]
 return calls,None
def consume(messages):
 results={m.get('tool_call_id'):m for m in messages if m.get('role')=='tool'}
 all_values={}
 for ident,name in expected:
  assert ident in results,('Missing tool response',name)
  text=content(results[ident])
  assert not text.startswith(('Error:','Tool execution failed')), (name,text[:1500])
  all_values.setdefault(name,[]).append(results[ident])
 return {**{name:results[ident] for ident,name in expected},'_all':all_values}
def valid_schema(v):
 if isinstance(v,dict):
  assert '$ref' not in v,'Host dropped a referenced schema definition'
  for x in v.values():valid_schema(x)
 elif isinstance(v,list):
  for x in v:valid_schema(x)
def response(payload):
 messages=payload['messages'];names=[x['function']['name'] for x in payload.get('tools',[])]
 if not names:return None,'Local tool chain validation'
 child='liuren_adjudication_read' in names and 'liuren_adjudication_packet' not in names
 events.append({'who':'child' if child else 'main','stage':state['main'],'tools':names,'model':payload.get('model'),'reasoning_effort':payload.get('reasoning_effort')})
 for definition in payload.get('tools',[]):valid_schema(definition['function']['parameters'])
 if not child and not wire:wire.extend({'name':x['function']['name'],'parameters':x['function']['parameters']} for x in payload.get('tools',[]) if x['function']['name'].startswith('liuren_'))
 if child:
  recovering=any('LIUREN_ADJUDICATION_REPORT_CONTINUATION_V1' in content(m) for m in messages if m.get('role')=='user')
  assert all(n in names for n in ['liuren_adjudication_read','liuren_adjudication_submit','liuren_compute','liuren_tool_help']),names
  tools=[m for m in messages if m.get('role')=='tool']
  if not tools:
   raw=next(content(m) for m in messages if m.get('role')=='user' and 'LIUREN_ADJUDICATION_FILE_V1' in content(m))
   lines=raw[raw.index('LIUREN_ADJUDICATION_FILE_V1'):].splitlines()
   return [call('liuren_adjudication_read',{'file_path':lines[1].strip(),'sha256':lines[2].strip(),'page':1,'page_count':4})],None
  v=parsed(tools[-1])
  if v.get('schema')=='liuren-adjudication-file-page-v1':
   assert v['view']=='core';state['reference_args']={'file_path':v['file_path'],'sha256':v['sha256']};state['childReadCalls']+=1;state['childPages']+=v.get('page_end',v['page'])-v['page']+1
   if v.get('next_call'):return [call(v['next_call']['tool'],v['next_call']['arguments'])],None
   return [call('liuren_adjudication_read',{**state['reference_args'],'module':'liqi','page':1,'page_count':4})],None
  if v.get('schema')=='liuren-adjudication-reference-page-v1':
   assert v['required_for_submit'] is False
   state['references_read']=state.get('references_read',[])+[v['id']]
   if v.get('next_call'):return [call(v['next_call']['tool'],v['next_call']['arguments'])],None
   if v['id']=='liqi':return [call('liuren_adjudication_read',{**state['reference_args'],'material_id':'E01','page':1,'page_count':4})],None
   return [call('liuren_compute',{'action':'calendar','calendar':{'start':'2026-11-03','end':'2026-11-03','timezone':'Asia/Shanghai','day_boundary':'civil-midnight'}})],None
  if v.get('schema')=='liuren-adjudication-receipt-v1':
   assert v['status']=='completed',v
   return None,json.dumps(v,ensure_ascii=False)
  if not recovering:return None,'__LENGTH_WITH_REASONING__'
  return [call('liuren_adjudication_submit',{'result':report})],None
 stage=state['main'];state['main']+=1
 required=['skill','liuren_chart','liuren_materials','liuren_tool_help','liuren_compute','liuren_adjudication_packet','task','task_result','liuren_adjudication_result','read']
 assert all(n in names for n in required),('Unavailable tools',[n for n in required if n not in names],names)
 values=consume(messages) if expected else {}
 if stage==0:return emit([call('skill',{'name':'daliuren'})])
 if stage==1:
  assert '大六壬占事' in content(values['skill'])
  checks.append('真实skill入口可加载')
  return emit([call('liuren_tool_help',{'topic':'workflow','domains':['finance']})])
 if stage==2:
  v=parsed(values['liuren_tool_help']);assert v['tool_contract']=='liuren-tools-31';assert 'judgment-core' in v['readiness']['missing'];assert v['execution_health']['ready'];assert v['features']['core_handoff'] and v['features']['on_demand_sources']
  checks.append('工具契约31、进程源码及核心路线自说明正常')
  return emit([call('liuren_chart',{'datetime':'2026-10-18T13:22','label':'流程合成验收','participants':[{'sex':'女','birth_year':2001}]})])
 if stage==3:
  v=parsed(values['liuren_chart']);assert v['ok'] and v.get('program_facts') and v.get('archive'),list(v)
  state['archive']=v['archive'];state['day_stem']=v['facts']['day_stem']
  assert str(project) in state['archive']['path'],'Chart archive escaped isolated project'
  checks.append('真实排盘工具、独立Node运行时与归档正常')
  return emit([call('liuren_materials',{'action':'method','modules':['judgment-core','adjudication','finance']})])
 if stage==4:
  assert content(values['liuren_materials']).count('LIUREN_METHOD_BEGIN ')==3
  state['main']=7;checks.append('准备阶段只读共用规范、交接与本问专项')
  return emit([call('liuren_tool_help',{'topic':'workflow','domains':['finance']}),call('liuren_materials',{'action':'shensha','path':state['archive']['path']})])
 if stage==7:
  assert parsed(values['liuren_tool_help'])['readiness']['ready'] is True
  assert content(values['liuren_materials'])
  checks.append('完整神煞读取与准备缺项清零')
  return emit([call('liuren_compute',{'action':'chart','archive':state['archive'],'symbols':['庚','丑']}),call('liuren_materials',{'action':'book_search','book':'LF','query':'死火克不动旺金','limit':1}),call('read',{'filePath':(project/pointer['runtime']/'methods/positioning.md').as_posix()})])
 if stage==8:
  assert '原问、对象与取用' in content(values['read'])
  assert content(values['liuren_compute']) and content(values['liuren_materials'])
  checks.append('程序计算、三书检索和原生read权限正常')
  return emit([call('liuren_compute',{'action':'quantity','expression':{'op':'multiply','args':[{'value':8},{'value':6}]}}),call('liuren_materials',{'action':'book_outline','book':'RG'}),call('liuren_compute',{'action':'life','archive':state['archive'],'life':{'age':21,'sex':'女','age_basis':'虚岁-已核'}}),call('liuren_compute',{'action':'lookup','archive':state['archive'],'lookup':{'subject':'朱雀','place':'巳','reference':'乙'}}),call('liuren_compute',{'action':'source','source':{'id':'M_NATIVE_SOURCE','title':'应期方法全文','source_path':pointer['runtime']+'/methods/timing.md'}})])
 if stage==9:
  computed=[parsed(item) for item in values['_all']['liuren_compute']]
  assert any(v.get('value')==48 for v in computed),computed
  assert any(v.get('xingnian')=='壬子' for v in computed),computed
  assert any(v.get('growth')=='临官' and v.get('kin')=='子孙' for v in computed),computed
  assert any('竞争轮次' in v.get('quote','') for v in computed),computed
  assert content(values['liuren_materials'])
  checks.append('取数、年命、查表、来源装配及原书目录分支正常')
  p={'schema':'liuren-adjudication-input-v2','request_id':'20261107-host-chain','questions':[{'id':'Q1','text':'电脑维修能否完成？何时修好？费用多少？','subject':'维修事项','domain':'finance','stage':'合成测试','deadline':'未限定','success_criteria':'只验工具传输','alternatives':[],'tasks':['outcome','timing','quantity'],'task_basis':[{'task':t,'origin':'user_requested','request_quote':q,'reason':'测试原问明确要求'} for t,q in [('outcome','能否完成'),('timing','何时修好'),('quantity','费用多少')]]}],'chart':{'source':'合成工程验收所用程序盘','archive':state['archive']},'facts':[],'entities':[{'id':'S1','question_ids':['Q1'],'referent':'测试对象','branch':state['day_stem'],'mapping_basis':'合成接口取用，不构成专业结论'}],'observations':[],'method_materials':[],'method_modules':['liqi'],'focus_issues':[],'unknowns':[]}
  return emit([call('liuren_adjudication_packet',{'packet':p})])
 if stage==10:
  v=parsed(values['liuren_adjudication_packet']);assert v.get('task_prompt'),v;assert v['reading']['view']=='core';state['reading']=v['reading']
  checks.append('真实packet按archive及已读模块装配并保存')
  return emit([call('task',{'description':'精简流程合成验收','subagent_type':'liuren-adjudicator','prompt':v['task_prompt']})])
 if stage==11:
  v=parsed(values['task']);assert v['status']=='invalid_output',v
  state['receipt']=v;checks.append('核心读完后模拟length，按回执进入同子会话恢复')
  return emit([call('liuren_adjudication_result',{'action':'recover','task_id':v['task_id']})])
 if stage==12:
  v=parsed(values['liuren_adjudication_result']);assert v['status']=='completed';assert v['task_id']==state['receipt']['task_id'];assert v['next_call']['tool']=='liuren_materials',v
  checks.append('可见子会话ID及task_result领取与next_call正常')
  return emit([call('liuren_materials',{'action':'method','module':'report'})])
 if stage==13:
  assert 'LIUREN_WORKFLOW_CONTINUATION ' in content(values['liuren_materials'])
  return emit([call('liuren_adjudication_result',{'action':'deliver','task_id':state['receipt']['task_id']})])
 v=parsed(values['liuren_adjudication_result']);assert v['report_markdown']==report,v
 checks.append('report门禁、完整deliver及原文一致正常');state['finished']=True
 (OUT/'host-report.md').write_text(v['report_markdown'],'utf-8')
 return None,'LOCAL_CHAIN_COMPLETED'
