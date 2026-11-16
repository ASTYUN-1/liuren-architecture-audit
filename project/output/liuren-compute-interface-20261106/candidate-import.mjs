// Changed-file overlay: reuse only these verified unchanged dependencies.
import {registerHooks} from 'node:module';
const dependencies=['liuren-deterministic.mjs','liuren-deterministic-io.mjs','liuren-shensha.mjs'];
const routes=new Map(dependencies.map(name=>[new URL('./candidate-live/tools/'+name,import.meta.url).href,new URL('../../tools/'+name,import.meta.url).href]));
registerHooks({resolve(specifier,context,next){
 if(context.parentURL&&(specifier.startsWith('.')||specifier.startsWith('file:'))){const target=routes.get(new URL(specifier,context.parentURL).href);if(target)return next(target,context);}
 return next(specifier,context);
}});
