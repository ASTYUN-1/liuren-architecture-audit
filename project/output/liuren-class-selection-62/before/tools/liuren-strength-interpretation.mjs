// User-adopted interpretation, separate from unchanged numerical mechanics.
export const STRENGTH_BANDS=Object.freeze([
 {range:'0',label:'本模型计算下限'},
 {range:'0<E<1',label:'极衰'},
 {range:'1≤E<2.5',label:'衰弱'},
 {range:'2.5≤E<5',label:'偏弱至中等'},
 {range:'5≤E<7.5',label:'较旺'},
 {range:'7.5≤E≤10',label:'强旺'}
].map(Object.freeze));
export const STRENGTH_INTERPRETATION=Object.freeze({
 id:'liuren-strength-meaning-58',origin:'用户确认的本地判断约定；不是预测校准或古籍数值阈值',
 bands:STRENGTH_BANDS,reference:5,
 unified_rule:'本题相关的日干、关键类神、官鬼及凶神统一喜旺恶衰：越旺，吉的倾向越强；越衰，凶的倾向越强。官鬼凶神旺默认不以侵害为主，衰败则凶态显；不得反向解释为鬼旺伤害大、鬼弱无害。',
 score_is_usability:false,low_score_means_harmless:false,zero_means_harmless:false,
 high_ghost_score_means_more_harm:false,control_delta_is_event_harm:false,
 applicability:'先核本题职责、对象、位置与真实作用通路；不把无关旺神拼成成功证据。',
 usability:'能否实际作用另核位置、通路、受制及先后，不设低分失用开关；低分、零或null均不能自动证明官鬼无害或制救成功。null是缺计算。',
 control:'克关系的负增量只表示计算中受者旺衰下降，不是侵害概率、现实伤害量或考试失败量。不得用鬼高、身分下降直接推出失败；须依喜旺恶衰解释双方性质及本问实际作用。',
 rescue:'制救须解释实际解除哪一阻碍，不能把压低官鬼指数本身当成救成；泄耗先核去向，泄干而生本题主类可体现付出，不默认等于失败。',
 scope:'这是综合取舍所用的旺衰倾向，不是整件事的成败分数；保留空墓、刑合、时序和兑现条件。数量修正4至6不增不减的分段不用于本项。',
 legacy_coefficients:'不使用旧harm_tendency/favorable_tendency小数作为本轮吉凶裁决依据；计算系数和数值算法未改。'
});
