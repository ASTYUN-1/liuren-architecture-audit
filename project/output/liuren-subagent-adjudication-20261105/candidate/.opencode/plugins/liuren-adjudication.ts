import type { Plugin } from '@opencode-ai/plugin';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { AGENT, MODEL, validateInput, validateOutput, parseTaskOutput } from '../../tools/liuren-adjudication-contract.mjs';

// Published at .opencode/plugins; the relative import resolves within that project.
const plugin: Plugin = async ({directory}) => {
  const pending = new Map<string, any>();
  return {
    'chat.params': async (input, output) => {
      if(input.agent!==AGENT)return;
      if(input.model.providerID+'/'+input.model.id!==MODEL)throw new Error('LIUREN_ADJUDICATION_MODEL_MISMATCH');
      output.options.reasoningEffort='high';
      // OpenCode 1.18 defaults to 32,000 shared reasoning/output tokens.
      // Keep high effort while leaving room for the visible contract result.
      output.maxOutputTokens=65536;
    },
    'tool.execute.before': async (input, output) => {
      if(input.tool!=='task'||output.args?.subagent_type!==AGENT)return;
      const pointer=JSON.parse(await readFile(resolve(directory,'.opencode/liuren-active.json'),'utf8'));
      if(pointer.adjudication?.agent!==AGENT)throw new Error('LIUREN_ADJUDICATION_INACTIVE');
      if(output.args.task_id)throw new Error('LIUREN_ADJUDICATION_FRESH_SESSION_REQUIRED: 不复用已有裁决会话');
      if(output.args.background===true)throw new Error('LIUREN_ADJUDICATION_FOREGROUND_REQUIRED');
      const packet=validateInput(JSON.parse(output.args.prompt));
      // Description carries no parent's candidate ranking or judgment.
      output.args.description='大六壬独立裁决';
      output.args.prompt=JSON.stringify(packet);
      pending.set(input.sessionID+':'+input.callID,packet);
    },
    'tool.execute.after': async (input, output) => {
      const key=input.sessionID+':'+input.callID;
      const packet=pending.get(key);
      if(!packet)return;
      pending.delete(key);
      try {
        const result=validateOutput(parseTaskOutput(output.output),packet);
        output.output=JSON.stringify(result);
        output.metadata={...output.metadata,liurenAdjudication:{agent:AGENT,model:MODEL,variant:'high',request_id:packet.request_id,status:result.status,contractChecked:true}};
      } catch(error) {
        output.output=JSON.stringify({schema:'liuren-adjudication-error-v1',request_id:packet.request_id,status:'invalid_output',error:String(error),action:'本轮裁决未完成。仅修复契约缺项后新建裁决；不得改由主智能体代裁。'});
        output.metadata={...output.metadata,liurenAdjudication:{request_id:packet.request_id,status:'invalid_output',contractChecked:false}};
      }
    }
  };
};
export default plugin;
