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
 
 if child:assert not any(k in payload for k in ['max_tokens','max_completion_tokens','max_output_tokens']), 'Client output cap still transmitted'
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
   state['childReadCalls']+=1;state['childPages']+=v.get('page_end',v['page'])-v['page']+1
   if v.get('next_call'):return [call(v['next_call']['tool'],v['next_call']['arguments'])],None
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
  v=parsed(values['liuren_tool_help']);assert v['tool_contract']=='liuren-tools-25';assert 'shensha-use' in v['readiness']['missing']
  checks.append('工具契约及8项路由自说明正常')
  return emit([call('liuren_chart',{'datetime':'2026-10-18T13:22','label':'流程合成验收','participants':[{'sex':'女','birth_year':2001}]})])
 if stage==3:
  v=parsed(values['liuren_chart']);assert v['ok'] and v.get('program_facts') and v.get('archive'),list(v)
  state['archive']=v['archive'];state['day_stem']=v['facts']['day_stem']
  assert str(project) in state['archive']['path'],'Chart archive escaped isolated project'
  checks.append('真实排盘工具、独立Node运行时与归档正常')
  return emit([call('liuren_materials',{'action':'method','modules':['positioning','liqi','structure','void']})])
 if stage in [4,5,6]:
  assert content(values['liuren_materials']).count('LIUREN_METHOD_BEGIN ')==4,content(values['liuren_materials'])[:1500]
  if stage==4:return emit([call('liuren_materials',{'action':'method','modules':['shensha-use','movement','adjudication','finance']})])
  if stage==5:return emit([call('liuren_materials',{'action':'method','modules':['timing','quantity','quantity-sources','nianming']})])
  checks.append('三组真实全文合批及准备回执正常')
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
  p={'schema':'liuren-adjudication-input-v2','request_id':'20261107-host-chain','questions':[{'id':'Q1','text':'电脑维修能否完成？何时修好？费用多少？','subject':'维修事项','domain':'finance','stage':'合成测试','deadline':'未限定','success_criteria':'只验工具传输','alternatives':[],'tasks':['outcome','timing','quantity'],'task_basis':[{'task':t,'origin':'user_requested','request_quote':q,'reason':'测试原问明确要求'} for t,q in [('outcome','能否完成'),('timing','何时修好'),('quantity','费用多少')]]}],'chart':{'source':'合成工程验收所用程序盘','archive':state['archive']},'facts':[],'entities':[{'id':'S1','question_ids':['Q1'],'referent':'测试对象','branch':state['day_stem'],'mapping_basis':'合成接口取用，不构成专业结论'}],'observations':[],'method_materials':[],'method_modules':['positioning','liqi','structure','void','shensha-use','movement','finance','timing','quantity','quantity-sources','nianming'],'focus_issues':[],'unknowns':[]}
  return emit([call('liuren_adjudication_packet',{'packet':p})])
 if stage==10:
  v=parsed(values['liuren_adjudication_packet']);assert v.get('task_prompt'),v
  checks.append('真实packet按archive及已读模块装配并保存')
  return emit([call('task',{'description':'精简流程合成验收','subagent_type':'liuren-adjudicator','prompt':v['task_prompt']})])
 if stage==11:
  v=parsed(values['task']);assert v['status']=='invalid_output',v
  state['receipt']=v;checks.append('真实length无正文未被误认作报告，未要求失败的task_result')
  assert v['next_call']['tool']=='liuren_adjudication_result',v
  return emit([call('liuren_adjudication_result',{'action':'read','task_id':v['task_id']})])
 if stage==12:
  v=parsed(values['liuren_adjudication_result']);assert v['recovery_available'] is True,v
  checks.append('无正文诊断与原子会话恢复next_call正常')
  return emit([call(v['next_call']['tool'],v['next_call']['arguments'])])
 if stage==13:
  v=parsed(values['liuren_adjudication_result']);assert v['status']=='completed' and v['result']==report,v
  checks.append('官方session.prompt在同一子会话完成submit；high且请求不含max_tokens')
  return emit([call('liuren_materials',{'action':'method','module':'report'})])
 if stage==14:
  assert 'LIUREN_METHOD_BEGIN' in content(values['liuren_materials'])
  return emit([call('liuren_adjudication_result',{'action':'deliver','task_id':state['receipt']['task_id']})])
 v=parsed(values['liuren_adjudication_result']);assert v['report_markdown']==report,v
 state['finished']=True;checks.append('原报告完整交付，未重建子会话、未提取reasoning')
 (OUT/'host-report.md').write_text(v['report_markdown'],'utf-8')
 return None,'LOCAL_CHAIN_COMPLETED'
