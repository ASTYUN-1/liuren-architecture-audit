# 51版：旺衰与取数的结合

本规则依用户本轮授权采用；分清北海原法、其他原书专法与本项目实验参数。原书定向核查见strength-quantity-evidence；书中没有给现代0—10指数的统一数量换算。本页不构成预测验证。

## 先固定对象，再固定算法

依本问的分类、阶段及数量含义取主类，不能沿用前问的成败类神而不复核。先明确总额/实得/净额、分数/过关、件数/排名等区别。天将类象须定位所乘天盘支，quantity_adjustment的target为T:支；日干与其他J/S对象可列入strength核施受，但不能以“天将没有自身支空”漏掉承载支旬空。是否得财或考试通过不由数量系数裁决。

有直接适用且条件明确的原书数法，优先沿该法；不同原书分支不拼接。方法缺步或条件不适用时，可以转本项目实验路径，但要说明转用理由，不同时计算多路再挑最像答案的数字。没有目录条目不等于不能取数；有源算式仍可用expression计算并说明来源与适用条件。

## 两条路径互斥

**source：按所选原法。** LF3329等已经按旺相休囚死选择乘、加、半，登记base_factors.qi=source_adjusted；不再乘实验强弱系数。WY244等月建月破倍半同样已经用过气态，不能冒充raw。其他专法使用何种数表、取哪对位置、是否另倍进依其原段。源法旺气进位不明确时不能凭一个“旺”自动进十百，CY旺多候选不可直接当单一value：有理由选定后用expression实际计算并登记source_adjusted，理由不足保留具体缺步。

**experimental：原始本数加一次数量修正。** 只接受尚未纳入旺衰和空减的expression基数；明确数表和位置，以稳定规则先确定本数。拒绝把已用季节分支的具名数法再塞入分段函数；也不得先因弱把乘法改加法，又把所得声明为raw继续打折。使用与本问同范围的真实无空重算指数，不用含空指数倒除、不手填分数。

实验系数固定为：E≤2.5取0.5；2.5<E<4按0.5+(E−2.5)/3连续过渡到1；4≤E≤6取1；6<E<7.5按1+(E−6)×0.2/1.5过渡到1.2；E≥7.5取1.2。E来自quantity_basis.rows中本主类的without_void。此为quantity-band-experiment-51研究参数，非北海原文；5是程序模型基准，不是已校准的“中气十足”。未经盲测/预测校准，不能称提高准确率。0不自动是整件事失败；强旺不自动是个人所得更多。

## 旺衰事实及作用范围

strength返回原有含空结果及quantity_basis：相同月令表、相同对象及已声明关系，把所有数值空减移除后重新解算without_void；保留实际空位、墓与生克事实，不是把原分除系数。single_palace仍仅单宫；selected_relations仅所选有效关系，未选关系、三合等数值不声称已算。取用后核实际生扶、阻碍、制救及施受能力，必要时补关系再算；事实关系不自动升级为有效作用，原五气和十二气系数不改。

数量对象的旺、整体气势大、财源规模大和自己能拿到钱分别解释。彩票中财旺可能是购买者众，股票行情好不等于本人收益大；这类语义依分类与原法判断，不另加一个所谓全局倍率。弱仍可作用，程序不以2.5/5设失用或成败门槛。

## 空亡只在数量上处理一次

基数已含数量空减则base_factors.void=true，void.status=already_in_base，禁止再半。experimental的指数本身排除了所有数值空减，故数量主类本身旬空、在所判阶段应减量时，可独立一次apply_half；其origin明确标user_research，不冒充原法。状态尚未落实、未来有具体解除或所求量含义特殊时，说明exception及阶段依据。

source路径不再执行50版“一切实量见空默认再半”的宽规则。原法明确另半则apply_half并标source；原法没说清，必须明确自己采用项目研究/估计补充，或说明exception而保留本数，不能假称已找到北海通则。无论路径，apply_half只适用于本数量主类的自身旬空；坐空、将空、身空不自动同义。折半来源需显式origin。序数、日期和编号禁止套实验倍率及空半，沿相应专法估计。

## 量级、单位和现实边界另定

magnitude.exponent只负责10的幂，0表示已在所求单位内；basis说明已知因、交易规模、工资/借款约定、奖级等依据，不由旺衰函数自动进位。分数给已知满分作upper_bound（未知不杜撰）；满分不能按E/10反推成绩。金额区分总额与净得，彩票已知彩种/票数/奖级时先受奖金规则约束。没有上限仍可给有据最佳估计，标明量级为模型估计及其理由；不能只凭“财旺”在20/200/2000间换档。

超上下限时程序报错，先复核数法、单位或量级依据，不能删掉已知上限强行通过，也不自动截满分。舍入由rounding指定小数位和依据，实际算式保留，不能暗改尾数。量级与强弱用途不得混为一个倍率。

## 最终运算与一条回执

51版新任务的consistency_policy.quantity_coupling_required=true。先算base及strength，再action=quantity、quantity_adjustment={route,target,kind,base_receipt_sha256,strength_receipt_sha256,base_factors,magnitude,void,basis,rounding?}。三种quantity输入expression/quantity_method/quantity_adjustment三选一。quantity_adjustment只在绑定任务中消费本任务回执；旧任务和主会话不混用。基数已是51版最终结果时禁止再次作为基数重扣。

kind为amount/score/count/distance/weight/ordinal/date/identifier。base_factors含qi(raw/source_adjusted)、void布尔及basis。magnitude含exponent、unit、basis及可选lower_bound/upper_bound。void含status(apply_half/already_in_base/not_applicable/exception)、basis，实际折半再给origin(source/user_research/model_estimate)。rounding含decimals(0—6)和basis。

工具返回value、完整算式、单位、所用强弱范围、已含因素及review。audit.quantity_reviews复制review，补question_id、final_receipt_sha256、report_quote即可；保留本数也走同接口，不用任意expression冒充最终数。正文只需主类与取法→本数→量级与实际修正→最终数，不必输出长表。没有可辩护估计时，在实际尝试后登记unresolved及具体缺步，沿47版交付；不编数过关，不增裁决轮次。

程序核回执归属、实际算术、路径冲突、重复修正、上下限和附件一致性；取用正确性、跨宫作用适用性、量级理由及预测效果仍须专业核对。本规则不把字段或测试通过当成术理验收。
