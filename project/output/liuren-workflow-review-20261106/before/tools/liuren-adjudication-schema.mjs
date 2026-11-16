// Shared native/contract scalar limits. IDs refer to records, not divination roles.
export const ID_PATTERN=/^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
export function contractScalars(s){
 const text=(max=6000)=>s.string().min(1).max(max).regex(/\S/,'must contain non-whitespace text');
 return {text,id:()=>s.string().regex(ID_PATTERN),texts:()=>s.array(text()).max(100)};
}
