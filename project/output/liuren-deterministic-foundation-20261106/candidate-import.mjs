// Candidate overlay supplies changed files only. Reuse this unchanged dependency
// from the real workspace rather than pretending the overlay is a full checkout.
import {registerHooks} from 'node:module';
const overlay=new URL('./candidate-live/tools/liuren-shensha.mjs',import.meta.url).href;
const installed=new URL('../../tools/liuren-shensha.mjs',import.meta.url).href;
registerHooks({resolve(specifier,context,next){
 if(context.parentURL&&(specifier.startsWith('.')||specifier.startsWith('file:'))&&new URL(specifier,context.parentURL).href===overlay)return next(installed,context);
 return next(specifier,context);
}});
