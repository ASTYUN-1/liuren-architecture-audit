# 海外大六壬八字网站：AI 后端与收款方案

> 调研日期：2026-10-02
> 来源：主会话结论 + 5 份并行调研子会话完整报告（从 opencode 会话库原样恢复）
> 范围：中国大陆个人开发者，出海 AI 命理/占卜（六壬·八字·紫微）产品的 AI 后端架构与跨境收款合规路径。
> 所有结论均基于官方政策原文与法规原文，附链接；未能核实项由调研方逐条标注。

---

## 零、原始需求

> 用户在主会话中提出的需求原文。

**用户（第 1 条）：**

我打算把我们大六壬、八字测算的服务做成网页，放到海外网站上去卖，主要是因为国内管控太严了。

我们可以先商讨一下以下方案：
1. 前端展示：网站的前端怎么做，给用户展示哪些功能。
2. 后端技术：后端技术方面我们怎么做。需要接入 AI API，让 AI 在服务器里（就像在 opencode 里面一样）运行，它可以调用各种工具，并且检索 skill，这些都要能正常运行。
3. 翻译层：需要再加一个翻译层给海外用户。
4. 收费方案：我们的收费方案怎么敲定。



还有一点啊，这个至关重要。如果服务器放到海外，才可以给海外用户提供服务，那么我们如何收到钱？


1. 可以通过 iPhone 手机的相关功能收到钱吗？
2. 或者有什么海外的服务商可以提供收费服务？他们抽一点钱，我们少拿一点也可以。


需要注意的是，我是个人开发者，甚至不是个体工商户。

**用户（第 2 条）：**

继续啊，这只是个调研分析内容

---

## 一、总体方案（主会话结论）

> 助手综合 5 份调研后给出的可决策方案，覆盖收款通道、主体结构、前后端架构、翻译层、定价与中国侧合规。

研究全部回来了，而且信息量很大，足以给出一个可决策的方案。先给最重要的判断，再逐条展开。

---

# 总判断

**这件事真正卡住你的不是技术，而是"收款 + 合规"。** 前端/后端/翻译（你的问题 1–3）是常规工程，2–4 周能出可用原型；但「**中国大陆个人 + 占卜品类 + 跨境收款**」这三件事叠在一起，恰好落在**所有最干净通道的门槛之外**。

所以正确顺序是：**先锁定钱的路径 → 用产品定位去匹配支付通道的准入 → 再围绕它设计前后端。** 下面先回答钱。

---

# 一、你最关心的：怎么收到钱

## 1.1 直接回答"能不能用 iPhone 收款"

需要拆成两个概念，这是很多人踩的坑：

| 你以为的 | 实际是什么 | 能不能用来收你的钱 |
|---|---|---|
| **Apple Pay**（iPhone 钱包） | 只是一个**付款方式**，不是商户账户 | ❌ 单独不能用。你还得先有一个收单方（MoR）挂在后面，Apple Pay 只是结账页上的一个按钮 |
| **App 内购 IAP** | 苹果代收，抽 15–30% | ⚠️ 技术可行，但你**几乎上不了架**（见下） |
| iPhone "Tap to Pay" | 线下碰一碰收款 | ❌ 与线上无关 |

**关键坏消息**：苹果审核条款 **4.3(b)** 把 `fortune telling` **逐字点名**放进"饱和品类、不再接受新提交"名单，且 2026 年补充了对存量 App 的下架权。实测案例里，连"塔罗记录本"这种非算命工具都被归入该类目拒审（WTFuture 被拒、Struck 被拒 9 次）。**1.1.6 条还明确堵死了"仅供娱乐"免责声明这条路。**

结论：**用 iPhone 收钱 = 做 App + 苹果 IAP，但作为新命理 App 上架概率很低，不是主力路径。**（头部产品 Co-Star / The Pattern 都是 IAP，但它们是多年沉淀的老 App。）

## 1.2 海外服务商代收（MoR）——这才是正解

你问的"海外服务商代收、抽一点钱"，专业名词就是 **Merchant of Record（MoR）**。它替你做全球税务代收代缴，你拿净额。但**每一家都有品类准入名单**，而"占卜"正好是被精准打击的品类之一：

| 服务商 | 允许占卜品类？ | 接受中国个人？ | 判定 |
|---|---|---|---|
| **Paddle** | 🔴 明文禁售：`pseudo-science... horoscopes, fortune-telling` | ✅ 接受个人 | 出局（品类） |
| **Creem** | 🔴 明文禁售：`Metaphysical, fortune-telling... services` | ✅ 接受中国个人+支付宝 | 出局（品类） |
| **Dodo Payments** | 🟡 **可申请**：`Spiritual & Astrology — Entertainment only; no claims or predictions` | ✅ **明确接受中国身份证、支持个人账户** | **首选** |
| **Gumroad** | 🟢 **逐字点名允许**：`chart-generation tools and pre-written reports are all allowed` | ⚠️ 中国收款未确认（底层 Stripe/PayPal） | **备选** |
| **Stripe (HK)** | 🟢 名单无玄学 | ❌ 不支持大陆（个人/公司都不行） | 需香港公司 |
| **PayPal** | 🟢 名单无玄学 | ⚠️ 大陆个人跨境收款能力受限 | 补充 |
| **Patreon / Podia** | 🟢 无禁令 | ⚠️ 未确认 | 备选 |

**一个很扎心的巧合**：唯一两家**明确接受中国大陆个人**的 MoR（Paddle、Creem），恰好**都明文禁售占卜**。而品类最友好的 Gumroad，中国个人收款又没确认。

## 1.3 决定生死的一条红线（请务必记住这句话）

Gumroad 的禁售政策里有一句判据，它其实适用于**所有**服务商：

> **"The test is what the product promises, not what tradition it draws on."**
> （判定标准是你的产品**承诺了什么**，而不是它**取材于哪种传统**。）

翻译成人话：

| 你的表达方式 | 能不能过审 |
|---|---|
| "生成八字命盘 + 文化解读，供**自我反思/娱乐**" | ✅ 可以 |
| "排盘工具 / 命盘生成器 / 传统文化学习" | ✅ 可以 |
| "预测你今年会不会结婚 / 有没有财运 / 健康如何" | ❌ 明令禁止 |
| "真人命理师实时指导你的人生决策" | ❌ 明令禁止 |

**这不是"钻空子"，而是产品的诚实定位问题**——你要卖的是"一个精致的传统文化解读工具"，而不是"包准的算命服务"。定位一旦定成后者，**收款通道直接消失**，技术再好也没用。

## 1.4 我推荐的收款组合

```
验证期（现在～产品跑通）：
  主通道 → Dodo Payments（Individual 个人账户，中国身份证可开，品类可申请）
  备用   → Gumroad（品类明文允许，但先确认中国个人能否提现）
  落地   → 提现到支付宝/境内银行卡（Dodo 支持中国，注意单笔 SWIFT $25 的坑）

成熟期（有稳定月流水后）：
  升级   → 香港公司 + Stripe HK（费率 2.9%+$0.30，品类干净，长期最优）
  
不建议现在碰：Paddle / Creem（禁品类）、Stripe 大陆（不开放）、
             Apple IAP 作为主力（4.3(b) 上架难）
```

**注册前必做的一件事**：用一页产品说明 + 定价页截图，发英文邮件给 `support@dodopayments.com` 预审，问："Do you accept a digital product that generates Chinese metaphysics charts (BaZi/Zi Wei Dou Shu) for personal reflection and entertainment?" 成本 30 分钟，能省掉你 3 个月。**所有 MoR 都在政策页写了"不确定就先问我们"。**

---

# 二、主体结构：你必须选一档

这是整个方案的**底层决策**，它决定了钱、合规、和你能走多远。

| 档位 | 结构 | 成本 | 优点 | 致命短板 |
|---|---|---|---|---|
| **档 0（验证期）** | 纯个人 + 海外服务器 + Dodo/Gumroad | 几乎为零 | 快、能马上验证产品 | 品类需"娱乐化"定位；无限责任；中国侧税务/外汇自行承担 |
| **档 1（目标态）** | 香港公司 + Stripe HK + 香港银行 | 注册+年审约 5k–10k CNY/年 | 费率低、品类干净、可签约开票、有限责任 | 需真实香港业务实质（地址/董事/账户），不是壳 |
| **档 2（合规态）** | 境外实体 + 数据合规体系 | 高 | 最稳 | 对个人开发者不现实（除非融资/团队） |

**建议**：**档 0 起步验证 → 有收入立刻升档 1。** 注意：注册香港公司**不会**改变你的中国税务居民身份，也不解决内容/数据合规（见第七节）。

---

# 三、前端展示方案

**技术选型**：Next.js（App Router）+ next-intl 做 i18n，部署 Vercel 或 Cloudflare Pages（海外）。

**页面结构**：

```
/                    落地页（营销 + SEO，多语言）
/reading             排盘入口（核心转化点）
  ├─ 八字：出生年月日时 + 性别 + 出生地（→ 时区/真太阳时校正）
  └─ 六壬：提问内容 + 起课时间（或自动取当前时间）
/reading/[id]        解读结果页（核心体验）
/pricing             定价页（支付通道审核会重点看这个页面）
/account             账户 / 历史 / 命盘收藏
/legal/privacy       隐私政策        ← 支付审核硬性要求
/legal/terms         服务条款        ← 支付审核硬性要求
/legal/disclaimer    免责声明（"for reflection & entertainment only"）
```

**结果页要展示什么**（这是产品力核心）：

1. **盘面可视化**——八字四柱 / 六壬四课三传的图形化呈现。这是最大设计挑战：把中式盘面翻译成西方用户能懂的视觉。建议做成类似占星轮的图形 + 英文标注（这是 @designer 的活）。
2. **结构化解读**——分章节：性格/事业/财运/感情/健康/近期运势，每段配**古籍出处**（增加可信度和文化厚度）。
3. **交互追问**——用户可就本次解读继续提问（这是订阅制的留存钩子）。
4. **导出/分享**——PDF 或精美分享卡片。
5. **免责声明**——在结果页固定位置。

**免费 vs 付费的展示切割**：
- 免费：只出盘面 + 一段概览（让人"哇"，但不够）
- 付费：完整解读 + 追问 + 导出

---

# 四、后端技术方案

你说"让 AI 在服务器里像 opencode 一样运行、调用工具、检索 skill"——方向对，但**不要真的做一个自由漫游的 agent**。付费产品需要**有界、确定性**的编排，否则成本失控、且模型可能说出违反支付政策的话（比如"你今年一定发财"）。

## 4.1 整体架构

```
┌─ 前端 (Next.js) ──────────────────────────────┐
│  输入采集 → 流式展示 SSE                        │
└──────────────┬────────────────────────────────┘
               │
┌──────────────▼─ 后端 (FastAPI / Node) ─────────┐
│                                                │
│  ① 输入归一化（LLM 抽取出生数据/占类）          │
│  ② 占类分类（LLM → 决定加载哪些 skill）         │
│  ③ 【确定性计算引擎 · 纯代码，非 AI】           │
│     八字排盘 / 六壬起课 / 神煞 / 应期            │
│  ④ skill 检索（占类路由 或 向量 RAG）           │
│  ⑤ AI 解读生成（流式，注入盘面+skill+术语表）   │
│  ⑥ 合规/术语校验 pass（拦截"预测性断言"）       │
│                                                │
└───┬─────────────┬──────────────┬───────────────┘
    │             │              │
 Postgres      Redis         模型网关
 (用户/订单/   (会话/限流)   (OpenAI/Anthropic/
  命盘/余额)                  Gemini 可切换)
```

## 4.2 各组件要点

**① 排盘计算引擎（最重要）**
- **必须用确定性代码，绝不能让 AI 算排盘**——AI 会算错干支、算错节气、算错大运起运。
- Python 生态最成熟：`sxtwl`（寿星天文历，算节气最准）、`lunar_python`（支持八字/十神/大运/流年）。六壬起课需**自研**（天地盘/四课三传/天将），把现有 `daliuren` skill 里的方法固化成代码。
- 若想全 TS 部署，用 `lunar-typescript`，但仍建议排盘单独起一个 Python 微服务。

**② 模型网关**
- 用 LiteLLM 或 Vercel AI SDK 做**供应商抽象**，随时切换。
- 分层用模型：**分类/归一化用便宜模型**（gpt-4o-mini 级），**解读生成用前沿模型**（GPT-4o / Claude 级）。
- 不建议用 DeepSeek 做面向海外用户的主力：数据落中国、且海外用户/合规对它有额外疑虑。

**③ skill 检索（你说的"像 opencode 检索 skill"）**
- 你现有的 `.opencode/skills/*/SKILL.md` 就是知识资产。
- **第一阶段别上向量数据库**：用**占类路由**——先让 LLM 判断用户问的是哪一类（占财/占婚/占病…），直接注入对应的整个 skill 文件。它们不大，便宜且确定性高。
- **第二阶段**（skill 库变大后）再上 pgvector / Pinecone 做语义检索。

**④ 工具调用**
- 把排盘/神煞/应期封装成函数暴露给模型：`paipan_bazi()`、`qike_liuren()`、`shensha_lookup()`、`yingqi_calc()`。
- 这样模型能"按需调用工具"，但计算仍由代码保证正确。

**⑤ 数据与安全**
- 出生时间+姓名是敏感信息 → **加密存储、最小留存**（可考虑解读完不落库）。
- 这是面向海外用户，务必写清 Privacy Policy。

---

# 五、翻译层方案

核心难点：**六壬/八字术语是深度文化绑定的，机器直译必翻车**（"天乙贵人"直译成 "Heavenly Second Noble" 就废了）。

**推荐做法：单遍目标语生成 + 受控术语表**（而不是"中文生成→再翻译"的两遍式，后者丢细节、加延迟）。

| 组件 | 做法 |
|---|---|
| **术语表（核心资产）** | 维护 `term → {拼音, 英文注解, 短解释}`，例如 天乙贵人 → `Tian Yi Noble (the most auspicious "Noble Star")`。先覆盖 200–500 个核心术语 |
| **生成约束** | 直接把术语表注入 prompt，要求模型生成目标语言时**按表用词** |
| **后处理校验** | 一道轻量 pass 检查术语是否与术语表一致，做替换 |
| **占类归一化** | 无论用户用英语/西语提问，先归一化成标准占类，再走 skill 路由 |
| **首发语言** | 英语优先 → 再西/葡（拉美、巴西占卜文化强）→ 德/法 → 日/韩。⚠️ **避开日本**（Stripe 在日本禁 psychic services） |

**一个隐藏红利**：这道"术语/语气校验 pass"**顺便就是合规守门员**——它可以自动拦截"你将会…""注定…"这类**预测性断言**，而这类断言恰恰是支付通道封你的首要理由。**同一个组件同时解决翻译质量 + 支付合规，务必合并做。**

---

# 六、收费方案

**定价锚点**（已由头部产品验证）：Co-Star $8.99/月、The Pattern $14.99/月。

| 档位 | 价格 | 内容 |
|---|---|---|
| 免费 | $0 | 仅出盘面 + 一段概览 |
| 单次额度包 | $4.99 / 1 次；$19.99 / 5 次 | 完整解读 + 追问 |
| 订阅（推荐主推） | **$9.99/月** | 每月 N 次完整解读 + 每日运势 |
| 订阅 Pro | $24.99/月 | 近乎不限次 + 优先模型 + 导出 |
| 年付 | 月付 × 10（省 2 个月） | 提升现金流 |

**单位经济学**：务必把**单次解读的模型成本控制在定价的 15% 以内**。一次解读若耗 $0.30 token，卖 $4.99 → 毛利约 90%，健康。用"便宜模型做分类 + 前沿模型做解读 + 缓存相似盘面"控制成本。

**与支付通道的配合（重要）**：
- Dodo 明文禁止"AI 生成的薄 PDF 报告"——**所以你不能卖一份 $29 的 PDF，必须卖真实软件/订阅**。这也是我推荐订阅制的原因。
- 定价页 + 免责声明是**支付审核必看页面**，要写规范。

---

# 七、中国侧合规（必读，这是真风险）

必须直说：**"服务器放海外 / 用户是外国人"并不能让你在中国法下免责。** 管辖开关不是"服务器在哪"，而是"是否以向境内自然人提供服务为目的"。要点：

1. **内容**：《网络信息内容生态治理规定》第六条把"宣扬封建迷信"列为**违法信息**，且规制对象包含个人。一旦你做中文 SEO/中文落地页/境内可访问，风险线就打开了。
2. **数据出境**：出生时间+姓名可能构成**敏感个人信息**，传入境外 AI API 触发 PIPL 的告知+单独同意+影响评估。纯海外用户理论上不适用，但**任何让境内用户能访问的入口**都会把开关打开。
3. **外汇**：个人年度便利化结汇 **5 万美元**；MoR 的结算单在银行结汇环节**凭证常对不上**；**分拆、借额度是明令禁止**（进"关注名单"）。2026 年起行刑反向衔接，刑事不起诉也照样行政处罚。
4. **税务**：中国税收居民就**全球所得**纳税，"钱在海外账户"不改变义务，境外所得要并入年度汇算。
5. **AI 新规**：《AI 拟人化互动服务管理暂行办法》（2026-07-15 施行）专门管"持续性情感互动服务"——**AI 命理陪聊若触达境内公众，会被直接命中**，且它明文禁止"诱导情感依赖/诱导用户决策"。

**三句话总结**：① 别做中文站/中文 SEO；② 收款和税务如实申报；③ 长期必须合规主体。**以上是公开法规信息整理，不构成法律意见**，重大决策前请咨询执业律师/税务师。

---

# 八、需要你拍板的三件事

我已经把可决策的方案摆出来了。接下来往哪个方向深挖，取决于你的三个选择 —— 这三个决定会**彻底改变**前后端和收款的设计：

---

## 附录 1：研究个人开发者收款方案

已完成逐家官网核对。以下是完整报告。

---

# 海外收款方案调研：面向**中国大陆无实体个人开发者**（2025–2026 现状）

> 调研时间：2026 年 10 月。**每条结论都标注了来源与置信度**：`✅官网明文` / `⚠️推断（官方页未列，但有强证据）` / `❓未能核实`。

---

## 0. 一句话结论

**真正「官网白纸黑字写明支持中国大陆个人」的 MoR 只有两个：Creem 和 Dodo Payments。** Stripe 官方支持国家列表里没有中国大陆，这一条直接否决了 Stripe、Polar、Buy Me a Coffee；Paddle 官网没有国家白名单（该帮助页已 404），但支持 **CNY 结算**且明确接受 **个人 / 个体户**，是可行度最高的第二选择。

---

## A. Merchant of Record（记录商户）方案

### A-0 总览对比表

| 服务商 | 个人（无公司）可注册？ | 中国大陆可注册？ | 费率（% + 固定） | 提现费 | 最低提现 | 全球税（VAT/销售税） | 买家支付方式 | 需绑海外银行？ | 综合判定 |
|---|---|---|---|---|---|---|---|---|---|
| **Creem** | ✅ 接受个人 | ✅ **官网明文列入支持国** | **3.9% + $0.40** | 银行 $7 或 1% 取高；USDC 2% | $50 / €50 | ✅ 50+ 国代收代缴 | 卡 / Apple Pay / Google Pay | ❌ 可用支付宝或境内银行卡 | 🥇 **首选** |
| **Dodo Payments** | ✅ 接受个人 | ✅ **中国在准入名单（第32位）** | **4% + $0.40**（国际卡 +1.5%，订阅 +0.5%，PayPal +3%） | 常规免费；**<$1,000 收 $5**；**非美 USD SWIFT $25** | 文中未列 | ✅ 190+ 国申报 | 40+ 种（含 UPI、BNPL） | ❌ 中国在可提现名单 | 🥈 **次选** |
| **Paddle** | ✅ **官网明文"not required for individuals or sole traders"** | ⚠️ 推断可行（支持 CNY 打款、无任何排除） | **5% + $0.50** | 多数国家 0；部分 $15 SWIFT | **$100**（可调至 $10万） | ✅ 收+申报+缴税全包 | 卡 / PayPal / 钱包（官网未逐一列举） | ❌ 电汇或 Payoneer | 🥉 **稳妥但审核严** |
| **Lemon Squeezy**（已被 Stripe 收购） | ✅ 接受个人 | ❌ **银行提现名单无中国大陆**；仅 PayPal 路径 | 5% + $0.50 | 视方式/地区而定 | $50 | ✅ 全权承担 | 21 种，含 PayPal 订阅 | ❌ PayPal 即可 | ⚠️ **长期不可持续** |
| **Polar.sh** | ✅ 接受个人 | ❌ **明确不支持**（依赖 Stripe Connect） | 5%+50¢ 起（Pro $20/月 → 3.8%+40¢） | Stripe 提现费 $2/月 + 0.25%+$0.25 | $10（USD） | ✅ 100+ 市场 | 卡 / 钱包 | — | ❌ **排除** |
| **Gumroad** | ✅ 接受个人 | ❌ 银行名单无中国大陆；且明确拒用 Payoneer/Wise | **10% + $0.50**（Discover 渠道 **30%**） | PayPal 提现 2% | $100 | ✅ 2025-01-01 起全权 MoR | 卡 / PayPal / 印度 UPI 等 | — | ❌ **基本走不通** |
| **FastSpring** | ❌ 注册表强制「公司名 + 企业邮箱」 | ❌ 面向企业 | ❌ **不公开，需销售报价** | 议价 | 无最低流水要求 | ✅ 代收代缴 | 大量本地方式 | — | ❌ **个人基本不可行** |

---

### A-1 Creem（🥇 最推荐）

**1) 个人 / 中国大陆注册**
- ✅ 官网「Supported Countries (86)」中明确列出 **China\***，与 HK、Taiwan 并列。
- 提现方式**按身份区分**，这是本次调研最有价值的发现：

  | 收款人身份 | 收款方式 | 限额 |
  |---|---|---|
  | **个人（Individual）** | **支付宝（Alipay）** | 单笔 ≤ 50,000 CNY；年度 300,000–600,000 CNY |
  | 企业（Business） | 境内本地银行账户 | 无限 |

  官网原文另注明：*"if you onboarded as an individual, the payout account must be an individual account and the beneficiary name must match your KYC identity."* → **收支付宝这条路径就是专门为个人设计的。**
- 准入材料极简：全名/或主体名、店铺名、产品 URL、业务描述、**税收居民国**。（`docs.creem.io/merchant-of-record/account-reviews`）

**2) 费率**
- **3.9% + $0.40**/成功交易；月费 $0；开户费 $0。官网举例：卖 $100 → 到手 $95.70。
- 提现费：**银行转账 $7 USD/EUR 或 1% 取高**；USDC（Polygon）2% 流水。
- 争议成本透明：Chargeback $30/笔、Visar RDR $18、Ethoca $27、退款处理 $1。

**3) 打款方式与周期**
- 提现额达 **$50 / €50** 后可点 withdraw；**每月 1 号和 15 号**各结算一次；到账前有 **7–12 天风控持有期**（15 号那批只算 8 号前处理的交易）。
- ⚠️ 坑：$7 起提费在月流水 $700 以下时会吃掉 1% 的两倍多。

**4) 全球税**：✅ MoR，50+ 国自动 VAT/GST/销售税代收代缴，自动开票。

**5) 买家支付方式**：Visa / Mastercard / Amex / Discover、**Apple Pay、Google Pay**；「本地支付方式 soon」。
- ❌ **不支持支付宝/微信买家付款**（对面向海外用户无影响）。

**6) 是否需海外银行账户**：❌ 不需要。个人走支付宝，企业走境内银行。

**⚠️ 最大的坑——品类限制**
- 允许：Software & SaaS、eBooks、PDF、设计素材、音频视频。
- **「Restricted（需额外审核）」**：*"Services of any kind, including, but not limited to marketing, design, web development, consulting"*、API 转售、生成式 AI 产品、交易类社区 → 要求提供**过往支付处理商记录、拒付/退款率、迁移原因**，且「An established and proven track record is required」。
  → **纯 SaaS 可以；一次性外包/设计服务基本被卡。**
- **Prohibited（禁售）**：实体商品、博彩、算命占卜（*fortune-telling*）、IPTV、**NFT 与加密资产产品**、第三方下载器、约会站、刷量/引流服务等。
- 审核清单：产品必须已上线、有 **Privacy Policy + Terms of Service**、官网展示**品牌邮箱**（如 `support@yourapp.com`，不能用通用邮箱）、禁止虚假评价。审核 1–2 个工作日。

---

### A-2 Paddle（🥈 MoR 里最"企业级"，但接受个人）

**1) 个人能否注册 —— 这是 Paddle 最被低估的一点**
> 官网 Business Identification 页原文：*"**Please note, this step is not required for individuals or sole traders.**"*
> Identity Verification 页：*"If you are an individual or sole trader, **you** will be the person required to do the identity verification check."*

即：**Paddle 明确接受自然人/个体户，不需要公司。** KYC 走 Sumsub（上传政府签发的身份证件 + 住址证明 + 活体自拍），Sumsub 有中国 KYC 专线产品页。

**2) 中国大陆**
- ⚠️ **官网没有可访问的国家白名单**（帮助页 `which-countries-are-supported-by-paddle` 返回 404，可能已迁移；Master Services Agreement 全文也无国家黑名单，制裁页只讲俄罗斯/白俄罗斯）。
- 但两个硬证据指向支持中国：
  - 提现币种明确包含 **Chinese Yuan (CNY)**（官方帮助页列举 13 种可提现币种，CNY 在列）。
  - 提现方式为 **wire transfer 或 Payoneer**；官方还专门写道：*"Some money transfer services like **TransferWise and ePayments** use online accounts. These services provide banking details such as BIC/SWIFT, IBAN, and account number, which can be used to send or receive money."* → 官方明示可以用这类"虚拟账户"收电汇。
- 结论：**推断可行，需自行实测注册。**

**3) 费率**：**5% + $0.50**/笔，全包（卡费、汇兑、税费都含），无月费。低于 $10 的产品可谈定制价。

**4) 打款**
- **每月一次**：1 号锁定余额，2–15 号打款；可自己调阈值，**最低 $100**，最高 $100,000。
- 币种换算（结算币 ≠ 余额币）最多收 **1.5% 转换margin**；部分国家收 **$15 SWIFT 费**；银行端费用自负。
- 官方给了明确建议：*"contact us (sellers@paddle.com) for advice on the most cost-effective way to receive your earnings"*。

**5) 全球税**：✅ 核心卖点。官网原文：*"We collect the correct rate of tax, track the filing deadlines, prepare our records, submit sales tax returns with all the other necessary documentation & payments to stay compliant."* —— **不只是代收，连申报和缴税都做**。

**⚠️ 坑**
- 三重审核：**域名审核 → 业务识别 → 身份验证**，部分环节转人工（2–4 工作日）。
- $100 起提对小额订阅者不友好。
- 官方自承在收购 ProfitWell 后产品节奏变慢（其 CEO 在 Lemon Squeezy 2026 年公开信里也承认行业性支持变慢）。

---

### A-3 Lemon Squeezy —— **先纠正一个时间线错误**

- **Stripe 收购 Lemon Squeezy 的官方公告日期是 2024 年 7 月 26 日**，不是 2025 年。公告作者 JR Farr。
- 法律实体已变更：页脚为 **"©2026 Sold through Link, LLC f/k/a Lemon Squeezy LLC"**，JR Farr 头衔已改为 "Co-Founder, Lemon Squeezy (**Stripe**)"。

**2026 年最新动态（2026-01-28 官方博客）——这条决定性：**
> *"while we've been heads-down building something big with Stripe's **new merchant of record product**… That's what we're doing with **Stripe Managed Payments**: Stripe's merchant of record solution."*
> *"Today Managed Payments **supports merchants in 35+ countries** and we're expanding to more later this year. **If you do not operate in a country that Stripe supports, check out Atlas** where you can incorporate your own C-Corp or LLC."*
> *"Very soon we will announce public access for Stripe Managed Payments… Our goal is to provide Lemon Squeezy users an easy way to **migrate** to Stripe Managed Payments."*

→ **Lemon Squeezy 正被 Stripe 自己的 MoR 取代，而 Stripe 不支持中国大陆。这个平台对无实体中国个人开发者没有长期价值。**

**中国大陆可行性细节**
- 银行提现支持国名单（79 国）中有 **Hong Kong / Macao / Taiwan**，**没有 China（大陆）**。
- PayPal 提现覆盖 **200+ 国家和地区** → 大陆个人理论上可用 PayPal。
- 提现节奏：1 号和 15 号生成，净收入**持有 13 天**，14 号和 28 号到账；最低 **$50**；银行提现以 USD 发出后按中间价换汇。
- 费率 5% + $0.50；MoR 全权承担税务申报（官网对比表里写明"International VAT + sales tax filing: Included"，对比"粘性贴纸方案 +$200–$5000/月"）。

---

### A-4 Polar —— ❌ 明确排除（有确凿证据链）

- 提现文档原文：*"Polar transfers the balance, minus Stripe payout fees, to your **Stripe account**, and Stripe issues the payout from there."*
- 卖家国家名单 = **Stripe Connect Express 覆盖范围**：有 Hong Kong / Macao / Taiwan，**无 Mainland China**。
- 个体可用：*"For individual accounts, yes [personal bank account]. For business accounts, you will need a business bank account."*
- 费率：Starter 免费 5%+50¢ / Pro $20·月 3.8%+40¢ / Growth $100·月 3.6%+35¢ / Scale $400·月 3.4%+30¢（新创可申请 Startup Program 免费 12 个月）。
- 附加成本：Stripe 提现费 **$2/有提现的月份 + 0.25% + $0.25/笔 + 跨境 0.25%（欧盟内）至 1%**；2026-05-12 之后创建的 org 有 **7 天结算延迟**。

---

### A-5 Gumroad —— ❌ 中国大陆基本走不通（三重矛盾）

- 费率 **10% + $0.50**；**通过 Discover 市场成交收 30%**。
- 税：2025-01-01 起成为 MoR，*"Gumroad handles ALL your tax obligations… we manage sales tax collection and remittance worldwide."*
- **致命点 1**：银行提现国家表中 **没有中国大陆**（只有 Hong Kong HKD / Macao MOP / Taiwan TWD）。按其规则，大陆只能走 **PayPal 提现**。
- **致命点 2**：*"We do **not** support alternative payout modes like **Payoneer, Wise**, check, money order, wire transfer… Many creators have attempted this, and **none of them** have been paid out properly."*
- **致命点 3**：后台是 **Stripe**。其 KYC 文档、SSN 说明、"bank account must be in the country where your business is registered" 全部围绕 Stripe Connect；而 Stripe 官方国家列表无中国大陆 → **KYC 阶段就可能过不去**。
- 其它：最低提现 **$100**；PayPal 提现费 **2%**；周五打款；账户审核 1–3 周（典型 3–4 笔、余额 >$100）。

---

### A-6 FastSpring —— ❌ 个人基本不可行

- **定价完全不公开**，必须联系销售：*"Our team will work with you to determine simple, flat-rate pricing based on transaction type and your volume of business."*
- 注册表单强制要求：
  - **Company name（必填）**
  - **Work email**，并注明 *"We require an email address from a business entity (no Gmail, Yahoo, etc.)"*
  - HQ country 下拉含 China。
- MoR 能力完整（VAT/GST/销售税代收代缴，不支持实体商品，年报 5400 万美元税额代缴），面向 AI/SaaS/游戏的中大型客户。
- ⚠️ 但**没有公开证据表明其接受自然人**，且销售门禁 + 企业邮箱要求对个人是硬门槛。

---

## B. 直接支付通道

### B-1 PayPal（中国大陆账户）

**费率（官方 CN 商家费率表，2025-06-18 更新）：**

| 项目 | 大陆（CN）费率 |
|---|---|
| 国际交易收款 | **4.40% + 固定费**（USD $0.30 / EUR €0.35 / GBP £0.20 / HKD $2.35 / JPY ¥40…） |
| 小额付款（<5 USD） | 6.00% + 小额固定费 |
| PayPal 在线卡付款服务（POCPS） | 4.10% + 固定费 |
| 标准争议解决费 | USD $8（高额 $16） |
| **提现 → 中国大陆银行（电汇）** | **USD 35.00 / 笔** ⚠️ |
| 提现 → 香港银行账户 | ≥1000 HKD 免费；<1000 HKD 收 3.50 HKD |
| 提现 → 美国银行账户 | USD 35.00 / 笔 |
| 提现 → 支票 | USD 5.00 / 笔 |
| 币种兑换 | USD 3.5% / 其他币种 4%（基于基础汇率）；"所有其他兑换" 2.5% |

**关键判断**
- ✅ 个人账户**可以收到钱**。
- ❌ **但数字商品订阅在个人账户上极难做**：PayPal 订阅（Subscriptions）需要商户申请并接受 **PayPal 在线卡付款服务（POCPS）协议**才能用；这在实务中基本只开放给商家账户。POCPS 还附条件：未使用 PayPal 按钮每笔罚 1%，风险指标过高可涨至每笔 5%。
- ⚠️ **中国大陆 PayPal 是两套账户**：费用页明确说明本页费率适用于依据**《PayPal 中国跨境支付服务用户协议》+《PayPal 全球服务条款》**开立的账户（即跨境账户），**不适用于**依《PayPal 支付服务用户协议》在贝宝支付（北京）开立的境内账户。
- ⚠️ 实操要点：$35/笔的电汇提现意味着**必须攒到较大额再提**；优先考虑提现到香港账户（近乎免费）再走其他通道。

### B-2 Stripe / Stripe Atlas

**Stripe 本身：❌ 中国大陆不在支持列表。**
`stripe.com/global` 完整国家表中有 **Hong Kong**、有 India（Preview）、有 Indonesia（Preview），**没有 Mainland China**。表格末尾对未开放地区写：*"Use Stripe Treasury with stablecoins… Payments not supported yet."*

**Stripe Atlas：✅ 可以用，但是"开公司"路线。**

| 项目 | 现状 |
|---|---|
| 费用 | **$500 一次性**（含政府费 + 首年注册代理） |
| 续费 | **$100 / 年**（注册代理） |
| 覆盖 | 官网明确：*"Incorporate a US company from **anywhere in the world**"*；*"Startups in **over 175 countries** have chosen Atlas"*；有专门的**中国大陆 Atlas 页面**（`stripe.com/cn/atlas`） |
| 包含 | 特拉华州注册（次日加急）、**公司税号 EIN**、创始人股权发行、**83(b) 选举代缴**、Cooley LLP 模板、$2,500 Stripe 产品额度、$50,000+ 合作方折扣 |
| 步骤 | Submit（填公司信息+签文件）→ Incorporate（拿到 EIN、开户）→ Bank（开 Stripe Treasury 拿美国银行账户）→ Fundraise |
| 是否需 SSN | **注册公司本身不需要**（这正是 Atlas 面向非美创始人的设计），但激活美国 Stripe 收款账户时，**最终受益人（UBO）仍要通过 Stripe 的 KYC**（用中国身份证+地址） |

**这条路对无实体个人的真实成本（结构性障碍，不是费率问题）：**
1. 年度维护：$100 注册代理 + 特拉华州年度申报 + 州特许经营税。
2. **美国税务申报**：外国股东的单人 LLC 需提交 **Form 5472 + pro-forma 1120**（附 hefty 罚则）；C-Corp 创始人错过 83(b) 期限会造成毁灭性后果（Atlas 会代缴，但要 30 天内自己完成）。
3. 税务居民判定：你若仍是中国税务居民，需同时处理**中国个人所得税（境外所得）+ 美国联邦/州申报**，双重申报。
4. 实际收款需要一个**美国银行账户**（Mercury / Wise Business US / Relay 等），再汇回国内，多一层损耗和一层合规。
5. Stripe Managed Payments 官方明确 *"If you do not operate in a country that Stripe supports, **check out Atlas**"* —— 反过来读就是：中国大陆用户不属于 Managed Payments 的服务对象。

### B-3 2Checkout / Verifone、Authorize.net

- **Authorize.Net**：Visa 旗下，美国 ISO（PNC Bank, N.A.）。官网定价页唯一明确的地域限制是 **eCheck (ACH) "only available for businesses based in the U.S."**；注册路径全部经 reseller/ISO，客服为美国号码 1-888-323-4289，**未提供任何非美国注册通道说明**。→ **对中国大陆个人实质不可行。**
- **2Checkout / Verifone**：❓**未能核实**。`verifone.com/2checkout/pricing/` 被 Cloudflare + 一次性密码墙拦截，`2checkout.com` 旧知识库路径 404。基于产品定位（企业级软件/数字商品全球收单、需提交企业资料、依托 Payoneer 类通道提现），**对无实体个人不抱期待**。若要评估需直接联系 Verifone 销售。

---

## C. 收款 / 提现工具

### C-1 Payoneer —— **对本场景最关键的一条轨**

**中国大陆个人可注册** ✅（官网有 `zh-hans` 中文站，含「自由职业者 / Freelancer」入口，运营主体含中国境内实体；支持中国大陆小程序与中文客服 `chinasupportrequest@payoneer.com`）。

**费率（官方定价页，2026-01-01 更新）：**

| 项目 | 费率 |
|---|---|
| 从另一 Payoneer 余额收款 | **Free** |
| 从市场/集成平台收款 | 视平台而定 |
| 通过**本地币种**收款账户收款 | **Free** |
| 通过**非本地币种**收款账户收款 | **1%**（最低 $1.00） |
| 付款方用信用卡付款 | 最高 **3.99% + $0.49** |
| 付款方用 ACH（仅美国） | 1% |
| 付款方用 PayPal（仅美国） | 最高 3.99% + $0.49 |
| **提现到本国银行 + 本币** | **USD 1.50 / 笔** |
| 提现到收件人**本地币种**（无换汇） | 1.2% – 4%（部分国家最低费最高 $20） |
| 提现到**非本地币种**（需换汇） | 1.2% – 4% |
| 余额币种互转 | 0.50% |
| **年费** | **$29.95**（12 个月内收款不足 $6,000 时收取；付费年费首年不收） |

> **关键证据**：$1.50 固定提现费的适用国家列表中**明确包含 "China"**（原文："All EU countries, USA, Australia, Bulgaria, Canada, **China**, Czech Republic, Japan, Kenya, South Korea, Mexico, Malaysia, Norway, New Zealand, Philippines, Poland, Romania, Saudi Arabia, Sweden, Singapore, Thailand, Vietnam, …"）。

**这意味着**：如果某个 MoR 支持「Payoneer 提现」，你最终落到境内银行卡的成本就是 **$1.50 + 换汇费**。目前 **Paddle** 和 **Patreon** 都直接支持 Payoneer 提现。

⚠️ 中国侧注意：个人年度 **5 万美元便利化结汇额度**（《个人外汇管理办法》），超需分次申报；提现收款人姓名必须与 KYC 一致。

### C-2 Wise

**可用性**：中国**不在** Wise 的"不支持国家"列表（该列表为阿富汗、白俄、布隆迪、中非、乍得、刚果、刚果金、古巴、厄立特里亚、伊朗、伊拉克、朝鲜、利比亚、缅甸、索马里、南苏丹、俄罗斯、苏丹、叙利亚、也门、委内瑞拉 + 乌克兰四州）。

**但有三个硬约束：**

1. **Wise 不提供 CNY 账户。** 你只能持有 USD/EUR/GBP 等，然后自行换汇。
2. **Wise Business 需要注册实体。** 官方要求文件清单：*Proof of Business Registration*（注册证明/公司章程/官方注册摘录）、*Proof of Address*、*Ownership Documents*（股东名册/合伙协议）、个人身份证件 + 商业登记号、注册地址与经营地址。→ **无公司 = 开不了 Wise Business。**
3. **Wise Personal 不能商用。** 用个人账户收商业款项违反其服务条款，且金额上限低（多数货币单笔/单日限额）。

**但 Wise 在本场景中有一个隐形关键作用**：**Creem 的银行打款通道就是 Wise。** Creem 支持国页面明确说双星国家（孟加拉、哥伦比亚、尼泊尔、巴基斯坦、坦桑尼亚、乌克兰）的打款限制"来自我们的银行转账合作方"，并直接给出 **Wise 的可发送国家实时列表**作为查询入口；中国带单星号，指向 Creem 的 transfer-limits 页面（支付宝路径）。

### C-3 万里汇 WorldFirst（蚂蚁国际）

- 主体：蚂蚁国际商业（上海）有限公司，宣称 70+ 支付牌照、160 万+出海企业、5000 亿美元累计交易。
- 能力：全球 40+ 币种收款、100+ 币种付款、万里付信用卡、外汇兑换、WorldTrade、平台 API。
- **❗关键：中国站注册页只有 4 种企业类型入口** —— 跨境电商 / 外贸 B2B / **数娱出海（开发者/发行商）** / 海外主体。整站文案是"企业客户""为出海企业打造""160 万+**出海企业**"。**没有"个人账户"注册通道。**
  - 有意思的是"数娱出海"专页面向"数娱行业开发者或发行商"，如果你是做游戏/应用变现的，可以试这条路——但从"企业客户"整体定位看，仍预期需要主体。
- 官网帮助中心 `worldfirst.com.cn/content/helpcenter` 可能有更细口径，本次未逐页核到个人条款。

### C-4 Airwallex 空中云汇

- 中国站产品线全是企业向：全球企业账户 / 全球支出管理 / 全球收单 / 全球计费管理 / 平台 API；客户数表述为"深受**超 20 万家企业**信赖"。
- 页脚合规声明：*"本网站旨在向您介绍由 Airwallex 空中云汇 (Hong Kong) Limited 或…位于中国境外的实体提供的服务，**服务中涉及中国境内金融服务的，由持有境内相关资质的第三方机构合作提供**。"*
- **未找到任何个人（individual）开户通道**；注册页 `/cn/signup` 未区分主体类型说明。
- → **面向企业，个人不适用。**

---

## D. 新兴 / 替代方案

### D-1 Ko-fi

| 项目 | 数值 |
|---|---|
| 平台费 | 免费档：**打赏 0%**，会员/商品/约稿 **5%**；Standard 全部 **5%**；Gold **$12/月**，打赏 0%、其余 5% |
| 月费 | $0 |
| **关键架构** | *"you get paid directly, we never hold your money. **Connect your own payment method**"*；*"Ko-fi doesn't process payments—you'll need to connect your Ko-fi to a **PayPal or Stripe** account"* |
| 买家支付 | PayPal、Apple Pay、Google Pay、Venmo、Cash App、卡、本地方式 |
| 税务 | ❌ **不是 MoR**。原文：*"set your own prices, terms and manage your own supporters"* —— 买家侧的销售税/VAT 落在你身上 |
| 对中国个人 | ⚠️ **只能靠 PayPal**（Stripe 接不了）。且它没有 API、没有计量计费、只适合"打赏+会员+少量数字商品"，**不能当网站订阅收单用** |

### D-2 Buy Me a Coffee — ❌ 中国大陆个人排除

- 费率 **5%** 交易费，创作者留 95%；$10 起可提现。
- **提现路径致命**：*"your funds are transferred directly to your **Stripe account**, and from there to your bank account."*
- → 依赖 Stripe，**中国大陆个人无法使用**。
- 买家支付：主要信用卡 + Apple Pay + Google Pay（无 PayPal）。

### D-3 Patreon — ✅ 中国 CNY 在名单内（但定位特殊）

**费率（2025-08-04 起的标准计划）：**

| 项目 | 费率 |
|---|---|
| 平台费（新页面） | **10%** |
| 平台费（2025-08-04 前发布且从未下线的 legacy） | Founders 5% / Pro 8% / Pro+Merch 11% |
| 处理费（USD 结算） | 卡 / Apple Pay：**2.9% + $0.30**；PayPal（美国）2.9%+$0.30；**PayPal（非美国）3.9% + $0.30** |
| 非 USD 结算 | EUR/GBP/DKK/NOK/SEK 3.4%+固定；HKD 3.9%；SGD 3.9%；CAD 3.2% |
| 币种转换 | 2.5% |
| 提现（美国创作者） | ACH $0.25/笔 |
| **提现（非美国创作者）** | **Payoneer 银行转账**：USD→本币 **$0.25 + 1.55% 换汇**；到 USD 银行账户 $0.50/笔 |
| | **PayPal**：1%（最低 $0.25，上限 $20，最低提现 $10） |
| | **Payoneer Wallet**：$1.00/笔，最低提现 $25 |
| iOS App 内购买 | **Apple 抽 30%**（Patreon 不另收处理费） |

**中国大陆可行性 ✅**：官方「Eligible payout countries per direct payout method」中，**China — CNY** 出现在 *Bank transfer – USD to local currency* 一栏。页面注明：*"In all countries listed, **Payoneer Wallet and PayPal are also available** payout options. Please note that your bank country is separate from your country of residence."*
→ **Patreon → Payoneer → 境内银行卡（$1.50/笔）**，这条链路是通的。

**但定位不匹配**：Patreon 是**创作者会员/社区 + 数字商品**平台，**没有面向任意网站 SaaS 的自助计费 API**。适合"订阅制内容/会员/社群"，不适合卖你的托管网站或 API 服务。另外内容审核严（成人内容、时事等），iOS 端抽 30%。

**MoR 程度**：Patreon 承担拒付/争议/欺诈，*"We take care of most applicable tax collections and remittance for you"*，并在部分地区对**平台费本身**代收 VAT/GST。属于"部分 MoR"。

### D-4 加密货币（简述）

- **收款端可行**：Creem 支持 **USDC（Polygon 网络）** 提现，费 2% 流水，最低 $50 → 这是上表中唯一的加密原生出口。
- **但中国大陆落地端基本不可行**：
  - 2021 年九部门《关于进一步防范和处置虚拟货币交易炒作风险的通知》将虚拟货币相关业务活动定性为**非法金融活动**；银行、支付机构不得提供账户、清算结算等服务。
  - 通过 OTC 将 USDT 兑回人民币是典型的**冻卡/反洗钱**高危路径。
  - 且 **Creem 明确禁止** "NFT & crypto asset products"；多数 MoR 也禁止涉币品类。
- **结论：可作为小额、临时的"备用出口"，不可作为主力方案。**

### D-5 应用商店分成（作为对比）

| 维度 | Apple App Store | Google Play |
|---|---|---|
| 分成 | **15%**（小企业计划，年收入 ≤ $100 万） | **15%**（前 $100 万） |
| 主体要求 | 中国大陆个人开发者**可以**个人身份加入（企业需 D-U-N-S） | 可用个人 Gmail 账号 |
| 消费者税 | ✅ 由商店代收代缴（含 VAT/销售税） | ✅ 同 |
| 对本场景 | ❌ **不适用**——只适用于原生 App；且 iOS 内数字内容强制 IAP（这正是 Paddle / Creem / Dodo 都在主打 "Bypass of App Store Fees" / "Selling Digital Goods on iOS" 的原因） | ❌ 同 |

**唯一有价值的对比结论**：应用商店在"消费者税代缴"这一项上和 MoR 等价，但**渠道锁死 + 无自建站结账 + 退款/客服负担**。Paddle 和 Creem 的价值就是让开发者用"自建站结账"绕开 15–30% 的平台抽成，代价是自己承担 VAT/销售税——而 MoR 恰好把这一块也接过去了。

---

## E. 明确不接受中国大陆个人 ❌

| 方案 | 依据（官网原文/官方列表） |
|---|---|
| **Polar.sh** | 提现走 **Stripe Connect Express**；其 MoR 支持国名单（= Stripe Connect 覆盖）无 Mainland China |
| **Buy Me a Coffee** | 提现必须落到 **你的 Stripe 账户**，再由 Stripe 打款 |
| **Stripe（含 Managed Payments）** | `stripe.com/global` 官方国家表无 Mainland China；Managed Payments 官方对不支持地区指引「check out Atlas」 |
| **Authorize.Net** | Visa 旗下美国 ISO；eCheck 明确"only available for businesses based in the U.S."；无非美注册通道 |
| **Airwallex 中国** | 官网全为企业产品线，"超 20 万家企业"，无个人开户通道 |
| **FastSpring** | 注册表强制"Company name"+企业域名邮箱；定价须经销售报价 |
| **Lemon Squeezy 的银行提现** | 支持国名单有 HK/Macao/Taiwan，**无 China 大陆**（仅剩 PayPal 200+ 国路径） |
| **Gumroad 银行提现** | 银行名单无中国大陆；且官网明文 *"We do not support alternative payout modes like Payoneer, Wise…"* |

---

## F. 理论可行但实操有坑 ⚠️

| 方案 | 坑在哪 |
|---|---|
| **Paddle** | 官网无可访问的国家白名单（帮助页 404），"支持中国"是从 CNY 打款 + Payoneer 通道 + 无排除条款**推断**的；三重审核（域名/业务/身份），$100 起提，换汇最多 1.5% |
| **Gumroad** | 唯一路径是 PayPal（$100 起提、2% 提现费、周五打款），但底层是 **Stripe Connect** → 中国大陆无 Stripe 账户，KYC 阶段即可能失败；10% 费率 + Discover 渠道 30%；明文拒绝 Payoneer/Wise |
| **Lemon Squeezy** | 仅 PayPal 路径；且官方已宣布要引导迁移到 **Stripe Managed Payments**（不支持中国大陆）→ 长期不可持续；官方自承"产品更新变慢、支持响应变慢" |
| **Wise（个人账户）** | 商用违反条款；无 CNY 账户；金额上限低。Wise Business 需注册实体 |
| **万里汇 WorldFirst** | 中国站仅 4 种企业类注册入口，无个人通道（"数娱出海"开发者通道值得一试但预期需主体） |
| **Ko-fi** | 只能接 PayPal（Stripe 不可用）；非 MoR，税务责任自负；无 API、非 SaaS 收单工具 |
| **Crypto / USDC** | 收款端可行，落地端受 2021 年通知约束，OTC 兑回人民币为冻卡高危 |

---

## G. 实际可行性排序 TOP 5

### 🥇 TOP 1 — Creem
**理由**：**唯一在官网把「中国大陆 + 个人 + 支付宝收款」三件事同时写清楚的服务。** 费率最低档（3.9% + $0.40），MoR 完整（50+ 国代收代缴），审核只需 1–2 工作日，材料只要身份证 + 住址 + 税收居民国。
**坑**：① 银行提现 $7 或 1% 取高 → 月流水低于 $700 时实际费率超过 4.9%，**建议主用支付宝通道**（未见额外提现费披露，需实测）；② 支付宝年度限额 30–60 万 CNY；③ "Services of any kind" 类目被列为 Restricted，新号直接卖服务会被要求过往支付记录；④ 需先有**上线产品 + 隐私政策/服务条款 + 品牌支持邮箱**才能过审。

### 🥈 TOP 2 — Paddle
**理由**：**官网唯一明文写"个人/个体户免于企业认证"的 MoR**；支持 **CNY 直接打款**；MoR 深度最高（连申报+缴税都做）；费率 5%+50¢ 全包无隐藏；Payoneer 通道可用（境内提现 $1.50）。
**坑**：① 国家白名单页面已 404，**必须自行注册实测**；② $100 起提 + 每月仅一次 → 现金流压力大；③ 域名审核会看你的网站质量，落地页不达标会被卡；④ 换汇最多 1.5%。
**建议**：与 Creem 并行注册，主收款用 Paddle 的 CNY 电汇（省掉换汇），或用 Paddle → Payoneer。

### 🥉 TOP 3 — Dodo Payments
**理由**：**官方准入名单明确列 China（第 32 位），并明确"个人用本国政府签发的身份证件即可"**；MoR + 40+ 支付方式 + 190+ 国税务申报；费率 4% + $0.40 居中；API/SDK 完整。
**坑**：① **非美国主体走 USD SWIFT 提现 $25/笔**（这是硬成本）；② 提现额 <$1,000 收 $5；③ Chargeback $30/笔；④ 公司根基在美国/印度，客服以英文为主，争议处理时区不利；⑤ 支付方式以印度/美国本地方式为主，欧洲/中东本地方式较少。

### 4️⃣ TOP 4 — Patreon（**仅当你的产品是会员制/内容订阅**）
**理由**：**China / CNY 明确在可提现国家列表**；Patreon → Payoneer（$0.25 + 1.55% 换汇）→ 境内银行卡（$1.50/笔），链路完整；平台承担拒付与大部分税务；处理费表公开透明。
**坑**：① 平台费已从 5–8% **上调到 10%**（2025-08-04 后新页面）；② **无自助 API，不能当网站 SaaS 收单**；③ iOS 端 Apple 抽 30%；④ 内容审核严。

### 5️⃣ TOP 5 — Lemon Squeezy（**仅作为过渡，且只走 PayPal**）
**理由**：MoR 能力完整、费率 5%+50¢、PayPal 覆盖 200+ 国家可覆盖中国大陆、$50 起提（比 Paddle 低）。
**坑**：① **银行提现明确不支持中国大陆**；② **官方已公开宣布要迁往 Stripe Managed Payments，而 Stripe 不支持中国大陆** → 迁移即失去通道；③ 产品节奏已放缓（官方自承）。**只适合当备用，不适合当主通道。**

---

## H. 推荐的实操组合

```
主通道：Creem（个人 + 支付宝收款）—— 费率最低，路径最确定
      ↘ 备份：Paddle（CNY 电汇 / Payoneer）—— MoR 最成熟，CNY 直打省换汇
      ↘ 补充：PayPal 中国跨境账户（个人可收，但务必攒够再提：境内电汇 $35/笔）
提现层：Payoneer 个人账户（境内提现 $1.50/笔，是最优落地轨）
不建议：Stripe / Polar / Buy Me a Coffee / Airwallex / FastSpring / Authorize.Net
        Gumroad（Lemon Squeezy 长期也不建议）
```

**三个必须自己盯住的合规点：**
1. **MoR 只解决"买方侧"的 VAT/销售税，不解决你的中国税务。** 你的境外所得仍需按《个人所得税法》自行申报（劳务报酬/经营所得），MoR 会给你 reverse invoice 供你入账。
2. **收款账户姓名必须与 KYC 身份完全一致**（Creem 和 Payoneer 都明文要求）。
3. **个人年度 5 万美元便利化结汇额度**；超额度需分次申报并保留合同/发票等证明材料。

---

## I. 关键来源

**MoR**
- Paddle 定价 https://www.paddle.com/pricing ｜ 费率 5% + 50¢
- Paddle 个人/个体户免企业认证 https://www.paddle.com/help/start/account-verification/what-is-business-verification
- Paddle 身份验证（Sumsub）https://www.paddle.com/help/start/account-verification/what-is-identity-verification
- Paddle 提现节奏与方式（wire / Payoneer、$100 起）https://www.paddle.com/help/manage/get-paid/when-and-how-do-i-get-paid
- Paddle 提现币种（**含 CNY**）https://www.paddle.com/help/manage/get-paid/can-i-be-paid-in-my-local-currency
- Creem 定价 https://www.creem.io/pricing ｜ 支持国（**含 China\***）https://docs.creem.io/merchant-of-record/supported-countries
- Creem 提现与**中国支付宝路径** https://docs.creem.io/merchant-of-record/finance/payouts
- Creem 账户审核与品类限制 https://docs.creem.io/merchant-of-record/account-reviews/account-reviews
- Dodo 定价（4% + 40¢、SWIFT $25、争议 $30）https://dodopayments.com/pricing
- Dodo 准入国家（**China = #32**，个人凭本国身份证）https://docs.dodopayments.com/miscellaneous/accepted-countries-and-territories
- Lemon Squeezy 被收购（**2024-07-26**）https://www.lemonsqueezy.com/blog/stripe-acquires-lemon-squeezy
- Lemon Squeezy 2026 迁往 Stripe Managed Payments https://www.lemonsqueezy.com/blog/2026-update
- Lemon Squeezy 支持国（**无中国大陆**）https://docs.lemonsqueezy.com/help/getting-started/supported-countries
- Lemon Squeezy 提现（$50 起、1/15 号、13 天持有）https://docs.lemonsqueezy.com/help/getting-started/getting-paid
- Polar 支持国（= Stripe Connect，**无中国大陆**）https://polar.sh/docs/merchant-of-record/supported-countries
- Polar 提现走 Stripe 账户与费用 https://polar.sh/docs/features/finance/payouts
- Gumroad 提现国家表（**无中国大陆**）https://gumroad.com/help/article/13-getting-paid
- Gumroad 明确拒用 Payoneer/Wise https://gumroad.com/help/article/223-payoneer-and-gumroad
- Gumroad 定价（10%+50¢ / Discover 30%）https://gumroad.com/pricing
- FastSpring 报价须经销售 + 需公司名与企业邮箱 https://fastspring.com/pricing/

**直接支付通道**
- PayPal 中国大陆商家费率与提现（**境内电汇 $35/笔**）https://www.paypal.com/c2/webapps/mpp/merchant-fees
- Stripe 全球支持国（**无中国大陆**）https://stripe.com/global
- Stripe Atlas（$500 + $100/年、175+ 国家）https://stripe.com/atlas ｜ 中国页 https://stripe.com/cn/atlas
- Stripe Managed Payments 资格 https://docs.stripe.com/payments/managed-payments/eligibility
- Authorize.Net 定价（eCheck 仅限美国企业）https://www.authorize.net/sign-up/pricing.html

**收款 / 提现工具**
- Payoneer 定价（**中国 $1.50 本币提现**、$29.95 年费）https://www.payoneer.com/about/pricing/
- Payoneer 中国站（自由职业者通道）https://www.payoneer.com/zh-hans/
- Wise 不支持国家（不含中国）https://wise.com/help/articles/2978049/where-can-i-use-wise
- Wise Business 需注册实体文件清单 https://wise.com/help/articles/2769792/how-can-i-verify-my-business
- 万里汇中国站注册（**仅 4 类企业入口**）https://www.worldfirst.com.cn/static/register/
- Airwallex 中国（全企业向）https://www.airwallex.com/cn
- Sumsub 支持文件（含中国 KYC）https://sumsub.com/supported-documents/

**替代方案**
- Ko-fi 定价（5% 服务费、**必须自接 PayPal 或 Stripe**、非 MoR）https://ko-fi.com/pricing
- Buy Me a Coffee FAQ（5%、**提现必须经 Stripe**）https://help.buymeacoffee.com/en/articles/4539170-frequently-asked-questions
- Patreon 创作者费率与**中国 CNY 提现名单** https://support.patreon.com/hc/en-us/articles/11111747095181-Creator-fees-overview
- Patreon 定价（10%）https://www.patreon.com/pricing

---

**两处未能核实、建议你自行求证的事项：**
1. **Paddle 官方支持国白名单页已 404** —— "Paddle 支持中国"是基于 CNY 打款能力 + Payoneer 通道 + 无排除条款的推断。注册前建议直接邮件 `sellers@paddle.com` 确认（官网明示接受此类咨询）。
2. **2Checkout / Verifone 的商户准入** —— 官网被 Cloudflare 拦截、旧的 2checkout.com 知识库已下线，未能核实其是否接受自然人。

---

## 附录 2：研究应用商店个人开发者政策

# 中国个人开发者「海外占卜 AI」收款路径调研（2025–2026 最新）

> **版本核对说明**：以下所有官方页面均于本次调研实时抓取（Apple / Google 帮助中心页脚版权为 **2026**），非记忆推断。凡我**未能**从官方页面直接验证的内容，均以「⚠️ 二手来源」明确标注。

---

## 第一部分：Apple App Store

### 1. 个人（Individual）账号：中国居民能否注册？

**结论：可以，且不需要公司主体。**

| 项目 | 官方规定 | 来源 |
|---|---|---|
| 年费 | **99 USD**（"in local currency where available"）；中国大陆区实际为 **¥688/年** | [Program enrollment](https://developer.apple.com/help/account/membership/program-enrollment) / ⚠️ 688 元见 Apple 委托研究 [Apple 生态系统在中国（2024-11）PDF](https://www.apple.com/newsroom/pdfs/apple-ecosystem-in-china-nov-2024.pdf) |
| 是否需要公司 | **不需要**。个人/个体户以 **本人法定姓名** 作为 App Store 上显示的 "Seller" | 同上 |
| 是否需要 D-U-N-S | **不需要**。原文：*"If you're enrolling as an individual, you don't need a D‑U‑N‑S Number."* | [D-U-N-S 说明](https://developer.apple.com/help/account/membership/D-U-N-S) |
| 实名认证 | 需要提供法定姓名、电话、地址、身份证件；**中国大陆 Account Holder 强制要求身份验证**，通过 **Apple Developer App**（iPhone）完成 | [Identity verification](https://developer.apple.com/help/account/membership/identity-verification) |
| 信用卡 | 需**本人名下**可扣 USD 的信用卡；用他人卡会被要求提供政府签发的带照片证件并延误审核 | [Program enrollment – Payment](https://developer.apple.com/help/account/membership/program-enrollment) |
| 中国大陆额外合规 | 仅对**组织**要求：产品页自动展示 D-U-N-S 中文名 + 统一社会信用代码（USCI）。**个人开发者不涉及** | [View China mainland compliance information](https://developer.apple.com/help/app-store-connect/manage-compliance-information/view-china-mainland-compliance-information/) |

> 关键限制：**Seller 名称 = 你本人法定姓名**（真实姓名会公开显示在 App Store），无法用品牌名/公司名包装。

---

### 2. 个人开发者的收款

**流程**：签署 Paid Apps Agreement（Schedule 2）→ 提交 W-8BEN → 填写银行账户 → 银行电汇打款。

**税务表格**（官方原文）：

> *"All developers must complete a US tax form to comply with the Paid Apps Agreement... If you're based outside the United States, the W‑8BEN, W‑8BEN‑E, or W‑8ECI may be required."*
> 中国个人开发者 = **W-8BEN**（非美国自然人）；填完**不可自行修改**，需联系 Apple Support。
> 来源：[Provide tax information](https://developer.apple.com/help/app-store-connect/manage-tax-information/provide-tax-information/)

> ⚠️ **Apple 未在我抓取到的任何官方页面公开各国预提税率表**。中美税收协定（2016 年议定书）**特许权使用费税率为 10%**（协定第 12 条），实际预提率以你提交的 W-8BEN 协定主张在 App Store Connect 中显示为准。IRS 页面：<https://www.irs.gov/businesses/international-businesses/china-tax-treaty-documents>

**能否打到中国大陆银行账户：可以。**

- 官方最低打款门槛表中，**CNY / 中国大陆未列入低门槛名单**，适用默认 **40 USD** 门槛（低门槛区多为 0.02 USD / 1–27 USD）→ 说明 Apple 支持向中国境内银行打款。[Minimum payment threshold](https://developer.apple.com/help/app-store-connect/reference/minimum-payment-threshold/)
- **打款主体**：`CNY → Apple Distribution International Limited`；`USD (Rest of the world) → Apple Distribution International Limited`。[Apple legal entities](https://developer.apple.com/help/app-store-connect/reference/apple-legal-entities/)
- 实操要求：先签 Paid Apps Agreement、填完税表，才能添加银行账户；填**银行本国信息**（含中国银行的清算行号/联行行号）；**只能绑定一个银行账户**；部分区域需额外材料。[Enter banking information](https://developer.apple.com/help/app-store-connect/manage-banking-information/enter-banking-information/)
- **中国境内实操要点（⚠️ 二手来源）**：电汇（SWIFT）到大陆银行，通常需银行提供英文行名 + SWIFT/BIC；个人年度结汇额度 5 万美元（国家外汇管理局规定）。

---

### 3. 分成比例

| 场景 | 比例 | 来源 |
|---|---|---|
| 标准佣金 | **30%** | Apple Developer Program License Agreement, Schedule 2（法律文本，我抓取时内容被截断，未逐字提取） |
| 小企业计划 | **15%**，条件：上一年**上≤100 万美元 proceeds** + 本年也 ≤100 万；须列出所有关联账号 | [Small Business Program](https://developer.apple.com/app-store/small-business-program/) |
| 自动续期订阅 | **第一年 70%，满一年后 85%**；小企业计划**第一天即 85%** | [Offer auto-renewable subscriptions](https://developer.apple.com/help/app-store-connect/manage-subscriptions/offer-auto-renewable-subscriptions/) |
| EU 替代条款 | 小企业 + 订阅满一年后再降至 **10%** | [Small Business Program FAQ](https://developer.apple.com/app-store/small-business-program/) |

> 小企业计划是**面向个人开发者的正式产品**（FAQ 原文："The App Store Small Business Program is intended for small businesses and **individual developers**"），个人账号可以直接申请，几乎无门槛。

---

### 4. ⚠️ 占卜/算命/星座/塔罗类 App 的审核政策（最关键）

#### 4.1 直接命中条款：4.3 Spam（b）— Apple **点名**了算命类 App

官方现行原文（我本次抓取的最新版）：

> **4.3 Spam**
> **(a)** Don't create multiple Bundle IDs of the same app…
> **(b)** Don't submit apps that are indistinguishable from what's already widely available… **Certain kinds of apps, such as dating, flashlight, sound effects, wallpaper, simple timers, and fortune telling, are well established on the App Store and we will not accept new submissions unless they offer a meaningfully different or improved experience. We may remove these apps from the App Store going forward if they are not updated, improved, or do not attract customers.**

来源：[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

这是**针对"fortune telling"的明确黑名单式条款**，而非边缘判例。同时 "We may remove these apps... going forward" 意味着**已上架的老 App 也面临被下架风险**。
（⚠️ 二手来源：Moburst 2026-07-28 与 Mac Observer 报道 Apple 于 2026 年 6 月补充了"可下架存量 App"的表述；[TechCrunch 2020](https://techcrunch.com/2020/09/after-numerous-rejections-strucks-dating-app-for-the-co-star-crowd-hits-the-app-store/) 显示 "fortune telling" 早在 2020 年就已列入该条款。）

#### 4.2 兜底封杀条款：1.1.6 False information

> **1.1.6** False information and features, including inaccurate device data or trick/joke functionality… **Stating that the app is "for entertainment purposes" won't overcome this guideline.**

**这条直接堵死"仅供娱乐"免责声明这条路**。任何暗示占卜结果**准确/有效**的表述（"准确率 92%"、"预测你的命运"）都可能被认定为 false information。

#### 4.3 个人开发者的结构性障碍：5.1.1(ix)

> **5.1.1(ix)** Apps that provide services in highly regulated fields (such as **banking and financial services, healthcare, gambling**, legal cannabis use, air travel and crypto exchanges) or that require sensitive user information should be submitted by a **legal entity that provides the services, and not by an individual developer.**

如果占卜 AI 的定位触及**心理健康/疗愈/焦虑抑郁建议**（Apple 常按 healthcare 审查），**个人账号将直接不合规，必须注册公司**。

#### 4.4 其他相关条款

- **4.2 Minimum Functionality**：若 App 只是"重新包装的网站"/薄壳 AI 客户端 → *"it doesn't belong on the App Store"*。
- **4.2.6**：*"Apps created from a commercialized template or app generation service will be rejected unless they are submitted directly by the provider of the app's content."* —— **白标/套壳批量上占卜 App 会被拒**。
- **5.1.2(i)**：向第三方 AI 共享用户数据须明示并取得明示许可（占卜 App 收集生日/姓名/情感信息必然触发）。
- **2.3.6 + 2025 新版分级**：需如实回答年龄分级问卷；2025-07-24 Apple 改为 **4+ / 9+ / 13+ / 16+ / 18+**（取消 12+、17+），**2026-01-31 前必须完成新问卷，否则无法提交版本/更新**。占卜内容若涉及成人、赌博暗示易触发 18+。
  来源：[Updated age ratings in App Store Connect](https://developer.apple.com/news/)、[Age Rating Updates](https://developer.apple.com/news/upcoming-requirements)

#### 4.5 真实拒审 / 下架案例（可验证）

| 案例 | 结果 | 来源 |
|---|---|---|
| **WTFuture**（星座 App），2021-10 | 第二次提交仍被 4.3 拒：*"Your app still primarily features astrology, horoscopes, palm reading, fortune telling or zodiac reports."* | [iMore](https://www.imore.com/apps/apple-rejects-developers-horoscope-app-says-app-store-has-enough) / [iPhone in Canada](https://iphoneincanada.ca/news/apple-rejects-horoscope-app-wtfuture-for-being-form-of-spam/) |
| 占卜+星座 App，2023-10 | 4.3 拒，回复原文完整复述了上述理由 | [Reddit r/iOSProgramming](https://www.reddit.com/r/iOSProgramming/comments/my_app_was_rejected_due_to_43/) |
| **Struck**（占星社交 App），2020 | **被拒 9 次**，作者公开吐槽 Apple *"groups astrology ('fortune telling' in their words) alongside 'burp and fart apps' under the umbrella of 'spam'"*；后经申诉才上架 | [Michael Tsai](https://mjtsai.com/blog/2020/06/24/struck-rejected-from-the-app-store/) / [TechCrunch](https://techcrunch.com/2020/09/after-numerous-rejections-strucks-dating-app-for-the-co-star-crowd-hits-the-app-store/) |
| **Cardology**（生日性格测评），2022 | 开发 6 个月后被 4.3 拒，引发 Change.org 请愿 | [Change.org](https://www.change.org/p/consumer-rights/get-apple-to-approve-my-cardology-app-address-the-bias-towards-fortune-telling) |
| **Celeste Astrology**，2025-06 | 收到 "4.3b: Spam" 拒审通知 | [astrology.textceleste.com](https://astrology.textceleste.com/apple-banned-our-astrology-app-heres-how-to-get-it-on-your-home-screen/) |
| **Moonlit Tarot**（AI 塔罗），2024-10 | 4.3 拒；开发者社区反馈：**在这个饱和品类里，"AI 塔罗" 本身反而是重复信号**，React Native 等跨平台框架的二进制重叠度高也会被判 spam | [Reddit](https://www.reddit.com/r/iOSProgramming/comments/need_advice_ios_app_rejection_for_saturated/) |
| **Tarot Journal**（记录用工具，非算命） | 仍被判定落入 "astrology, horoscopes, or fortune telling" 类别被拒 | [Apple Developer Forums](https://developer.apple.com/forums/) |
| Daring Fireball 2026-08 | 引用 4.3(b) 论证某次拒审是"正确拒审" | [Daring Fireball](https://daringfireball.net/2026/08/retraction_app_store_rejection_of_the_week) |

**核心洞察**：即使你的 App **不是**算命（只是塔罗记录本、星座查询），只要被 Apple 归入该类目，同样触发 4.3(b)。且**类别判定发生在功能实测之前**——有开发者报告审核员 2 分钟内只走了 onboarding 就给了 4.3 拒审。

---

### 5. 订阅（Auto-renewable subscription）对个人开发者的要求

- **必须持续提供价值**，订阅周期 ≥ 7 天，**在用户所有设备上可用**（3.1.2(a)）。
- **首次自动续期订阅必须与 App 新版本一同提交审核**；首次订阅组也必须随版本提交且包含一个自动续期订阅。首次通过后，后续订阅无需新版本即可提交。
- 订阅组：最多 100 个订阅产品，用户每组同时只能持有一个。
- 周期可选：1 周 / 1 / 2 / 3 / 6 / 12 个月。
- 订阅前必须清楚说明用户将获得什么（3.1.2(c)）。
- **明确要求「持续提供价值」（ongoing value）** —— 一次性算命结果用订阅制有较高风险，Apple 历史上重点打击"伪订阅"（bait-and-switch）。
- 订阅到手比例：标准 70%→85%；小企业计划 85% 起。
- 来源：[App Review Guidelines 3.1.2](https://developer.apple.com/app-store/review/guidelines/)、[Offer auto-renewable subscriptions](https://developer.apple.com/help/app-store-connect/manage-subscriptions/offer-auto-renewable-subscriptions/)

---

## 第二部分：Google Play

### 1. 个人开发者账号 + 中国居民现状

| 项目 | 规定 | 来源 |
|---|---|---|
| 账号类型 | Personal / Organization 两种 | [Get started with Play Console](https://support.google.com/googleplay/android-developer/answer/6112435) |
| 注册费 | **US$25 一次性**（非年费），需 Visa/Master/Amex 等外币卡，**不接受预付卡** | 同上 |
| 年龄 | ≥18 岁 | 同上 |
| 身份验证 | 可能被要求提供**政府签发 ID + 本人名下信用卡** | 同上 |

**2023 年后新增的"个人账号测试门槛"（你问的重点）：**

> **适用于 2023-11-13 之后创建的个人账号**。必须完成：
> - **封闭测试（closed test）至少 12 名测试者连续加入满 14 天**（中途退出再加入不累计）
> - 达标后在 Dashboard 点击 **Apply for production**，回答三组问卷（关于封闭测试 / 关于你的 App / 关于生产准备度）
> - Google 审核"通常 ≤7 天"，可能被要求继续测试
> - 达标前 **Production 与 Pre-registration 轨道被锁定**
>
> 来源：[App testing requirements for new personal developer accounts](https://support.google.com/googleplay/android-developer/answer/14151465)

**设备验证（2024 年初起）：**

> 新个人账号必须用 **Play Console 移动 App** 扫描二维码，验证拥有一台**真实非 root、Android 10+ 的实体设备**，否则无法上架。
> 来源：[Device verification requirements for new developer accounts](https://support.google.com/googleplay/android-developer/answer/14316361)

**对占卜 AI 产品的额外含义**：你必须先找 12 个愿意连续 14 天使用"占卜 AI App"的人——这本身是一个巨大的真实用户获取成本，比 Apple 的路径更重。

### 2. 收款（能否绑定中国大陆银行）

- **官方流程**：Play Console → 付款设置 → 银行账户（需关联 **Google payments profile / merchant 账号**，在 `payments.google.com` 维护），并提交税务信息（非美国居民需 **W-8BEN**）。日本/韩国等要求从 payments profile 读取经营者信息（[Requirements for distributing apps in specific countries/regions](https://support.google.com/googleplay/android-developer/answer/6223646)）。
- ⚠️ **我未能在 Google 官方页面找到"支持打款国家/地区"公开清单**（Google 没有像 Apple 那样公开最低门槛表）。以下为从业者实测（⚠️ 二手来源）：
  - 中国大陆个人可绑定**大陆银行**，以**电汇 SWIFT** 到账，需填写**受益人姓名、SWIFT/BIC、中行 CNAPS 代码**；招商银行借记卡被验证可用。
  - 默认「个人商家」账号**只能绑定 Google 账号注册地（手机号地区）对应的银行**，且需为**美元账户**。
  - 常用替代：Payoneer / PingPong / 连连国际等跨境收款（费率约 0.7%–1%）。
  - 参考：[googlechuhai 2025 指南](https://googlechuhai.com/post/6311)、[快出海：如何正确设置 Google Play 的收款账号](https://kchuhai.com/report/view-1446.html)、[连连国际](https://global.lianlianpay.com/article/NjE5MDEsYTZl.html)
- **Play 账单服务在中国大陆未上线**：[Payments policy](https://support.google.com/googleplay/android-developer/answer/10281818) 明确 *"As long as Google Play's billing system isn't available in a particular country, the Payments policy's requirement … does not apply in that country."*
- ⚠️ Google Play **不在中国大陆运营**，中国用户无法正常访问/下载（这意味着 Play 路径只能服务海外用户）。此点由大量社区/媒体来源支持，但我未找到 Google 官方"中国大陆不在分发列表"的直接声明（[官方分发国要求页](https://support.google.com/googleplay/android-developer/answer/6223646)未列中国）。

### 3. 分成 / 订阅

- **服务费：15%**（每年前 100 万美元），**超出部分 30%**；2021-07-01 起对所有开发者自动适用（无需申请）。Google 官方：*"99% of developers who are subject to a service fee qualify for a fee of 15% or less."*
  来源：[Understanding Google Play's Service Fee](https://support.google.com/googleplay/android-developer/answer/11131145)；2021 年宣布见 [TechCrunch](https://techcrunch.com/2021/03/16/google-play-drops-commissions-to-15-from-30-following-apple-s-move-last-year/)
- **数字内容强制使用 Play Billing**：订阅、App 内功能、AI 问答次数等"应用内可消费的"数字服务，**必须走 Google Play 结算**（1:1 实时真人服务可豁免）。违反会被拒审/下架。
  来源：[Understanding Google Play's Payments policy](https://support.google.com/googleplay/android-developer/answer/10281818)
- 替代计费仅在美国、韩国、印度、EEA 等试点地区开放（DMA / 各地裁定），**中国不适用**。

### 4. 占卜类 App 政策（Google 不像 Apple 点名，但更狠）

Google **没有**专门针对占卜的政策，但以下几条会组合绞杀"批量 AI 算命 App"：

| 政策 | 原文要点 | 来源 |
|---|---|---|
| **Spam → Repetitive Content** | *"We don't allow apps that merely provide the same experience as other apps already on Google Play… **Creating multiple apps with highly similar functionality, content, and user experience.**"* | [Spam](https://support.google.com/googleplay/android-developer/answer/9899034) |
| **Functionality（有限功能）** | 不允许 *"Apps with very little content and that do not provide an engaging user experience"* | [Functionality, Content, and User Experience](https://support.google.com/googleplay/android-developer/answer/9898783) |
| **AI-Generated Content 政策** | 生成式 AI App 不得生成"**能够欺骗用户或促成不诚实行为**"的内容；违规示例含 *"Content generated to facilitate … dishonest behavior"*、AI 生成的"官方文件" | [AI-Generated Content policy 解读](https://support.google.com/googleplay/android-developer/answer/14094294) |
| **Deceptive Behavior** | 误导性功能声明、元数据欺骗 | [policy 索引](https://support.google.com/googleplay/android-developer/topic/9877467)（Deceptive Behavior / Misrepresentation / User Data） |

> **实际含义**：Google 没有"占卜"这个靶子，但它对"大量同质化 AI 生成 App"的容忍度更低。抖音/出海圈广泛使用的"批量上架 AI 算命 App 矩阵"策略在 Google Play 属于 **Repetitive Content + AI-Generated Content** 双高危。

---

## 第三部分：其他平台（仅对比）

| 平台 | 占卜/算命是否可做 | 依据 |
|---|---|---|
| **微信小程序** | **❌ 无此类目**。整个服务类目表中**不存在**占卜/算命/星座/运势类目；唯一宗教相关的是「文娱 → 宗教信息」，**仅对非个人主体开放**，且必须持《互联网宗教信息服务许可证》 | [微信小程序开放类目](https://developers.weixin.qq.com/miniprogram/product/material/) |
| 微信实操 | 开发者社区大量反馈：即使**免费、不涉及付费**的"星座知识查询"小程序，也被反复判定为"算命/卜算"而拒审 | [微信开放社区](https://developers.weixin.qq.com/community/develop/doc/000082c0f88640f4b490809316b009) |
| **抖音小程序** | **❌ 明确禁止封建迷信**。官方社区审核攻略原文：*"小程序中禁止出现任何有关封建迷信的服务，如**风水命理，算命，解梦，冥婚**等，常见表现形式**名字测算，号码/车牌吉凶测算，房屋风水禁忌，算命卜卦**等内容。"* 违规处置为"能力限制、版本下架、隐藏、终止小程序业务" | [抖音开放平台社区《小程序审核攻略丨违规内容迷人眼（下）》(2022-06-01)](https://developer.open-douyin.com/forum/mini-app/post/6297142eb3c081a214176c5d) |
| 抖音直播 | 2022 年专项治理"占卜、算命、塔罗"等迷信伪科学内容，禁止用"星座/塔罗/心理测试"名义诱导打赏 | ⚠️ 二手来源（[中华网](https://m.tech.china.com/digi/20220122/20220122992765.html)、[腾讯新闻](https://news.qq.com/rain/a/20220122A04D6B00)） |
| **Steam** | 不相关，略（本项目非游戏） | — |

---

## 第四部分：关键结论

### 问：走 App Store / Google Play 是中国个人开发者做"海外占卜 AI"的可行收款路径？

**答：技术上可行，但**「App Store 收款是死路，Google Play 收款是更重的死路」**。**

#### 主要障碍（按严重程度排序）

**🔴 障碍 1：Apple 4.3(b) 把"fortune telling"写进了条款本身**
这不是"可能被拒"，而是**规则层面宣告该品类饱和**。Apple 明确说"不接受新提交"，并且 2026 年补充了**对存量 App 的下架权**。真实案例显示：连只做记录功能的 Tarot Journal 都被归入该类目；2020 年 Struck 被拒 9 次。这条路需要**极端差异化 + 申诉运气**，不是工程问题。

**🔴 障碍 2：1.1.6 堵死"仅供娱乐"免责声明**
Apple 原文专门点名：*"Stating that the app is 'for entertainment purposes' won't overcome this guideline."* 任何"准确率""预测""指引人生"的表述都是 false information 风险。而放弃"预测"卖点，占卜 App 就没有商业价值了。

**🟠 障碍 3：5.1.1(ix) — 个人账号的天花板**
一旦产品触及**心理健康/疗愈/焦虑**（这是 AI 占卜最常见的营销角度），Apple 要求**法人实体**提交，个人账号直接不合规。这意味着很多"个人出海算命 AI"的终局都必须注册公司 —— 而这会连带出公司主体、结汇、对公账户、税务等一系列问题。

**🟠 障碍 4：Google Play 的"12 人 × 14 天"测试门槛**
对占卜产品，这 12 个人必须是**愿意连续两周使用 AI 算命 App 的真实用户**，且 Google 还要审你的招募过程问卷。对个人开发者几乎是不成比例的启动成本。叠加 **15% 分成 + 强制 Play Billing**（海外用户只能在 App 内付费）。

**🟠 障碍 5：中国大陆银行收款的摩擦**
- Apple：能收，但 40 USD 门槛 + 电汇 + 个人 5 万美元年结汇额度；**税务上要自己处理中美双重征税问题**（Apple 预提后回国仍需申报）。
- Google Play：能收，但必须过 Google payments profile + 外币卡注册 + SWIFT/CNAPS 填写；官方无公开支持国清单，靠服务商兜底。

**🟡 障碍 6：国内小程序这条路已被完全封死**
微信（无类目 + 宗教资质）、抖音（明文禁止封建迷信）**都不接受占卜类小程序**。所以"先在国内小程序验证、验证通过再出海"这个常规路径不成立。

**🟡 障碍 7：合规与法域风险（未在政策中但真实存在）**
把中国大陆个人开发者的身份、服务器、支付主体暴露给海外用户，涉及个人信息出境、数据合规与外汇结汇；Apple 中国区还会对组织主体展示 USCI。

### 务实的路径建议

| 方案 | 可行性 | 说明 |
|---|---|---|
| **A. Web/PWA + 第三方支付（Stripe/lemonsqueezy/Paddle）** | ⭐⭐⭐⭐⭐ | 绕开 4.3(b)、绕开 Google 测试门槛、绕开强制 IAP。中国个人可用香港/海外主体 + 跨境收款。占卜品类在 Web 端审核真空。**这是唯一不与平台审核政策正面冲突的路径。** |
| **B. App Store「非占卜」定位** | ⭐⭐ | 必须彻底去掉占卜/预测定位（如定位为"占星学习/星盘工具/ journaling"），且需 15% 小企业计划 + 订阅制 + 持续价值。成功率仍低（Tarot Journal 案例）。 |
| **C. Google Play** | ⭐⭐ | 无占卜靶子但有 Repetitive Content + AI 政策 + 12×14 测试门槛。若坚持做，务必做成**单一高质量 App**（非矩阵），并充分披露生成式 AI。 |
| **D. 国内微信/抖音小程序** | ❌ | 政策明文封闭，不建议尝试。 |

**一句话结论**：App Store / Google Play **不是**中国个人开发者做海外占卜 AI 的可行收款路径 —— **可行的收款路径是"Web + 第三方支付 + 海外主体"，App 只能作为引流壳**（且 iOS 壳子本身受 4.3(b) 制约）。

---

### 政策有效性核对表

| 政策 | 状态 | 验证方式 |
|---|---|---|
| App Review Guidelines 4.3(b) / 1.1.6 / 5.1.1(ix) / 3.1.2 | ✅ 现行有效（页面版权 2026） | 本次直接抓取官方页面 |
| Small Business Program 15% / $1M | ✅ 现行有效 | 直接抓取 |
| Apple 订阅 70%→85% | ✅ 现行有效 | 直接抓取 |
| Apple 年龄分级 13+/16+/18+（2026-01-31 截止） | ✅ 现行有效 | Apple Developer News |
| Google Play 12 testers × 14 days | ✅ 现行有效 | 直接抓取 |
| Google Play 设备验证（2024 初起） | ✅ 现行有效 | 直接抓取 |
| Google Play $25 注册费 | ✅ 现行有效 | 直接抓取 |
| Google Play 15% 服务费 | ✅ 现行有效 | 直接抓取（阈值细节为 2021 公告） |
| Google Play 15 tier / Play Billing 强制 | ✅ 现行有效 | 直接抓取 |
| Apple 中国大陆 688 元/年 | ⚠️ Apple 文档仅写 "99 USD, in local currency where available"；688 元由 Apple 委托研究 PDF + 社区来源佐证 | 二手 |
| Apple 中国个人预提税率 | ⚠️ 官方未公开税率表；协定 10% 来自 IRS 条约文件 | 部分二手 |
| Google Play 支持打款国家清单 | ❌ **Google 无公开官方页面**；中国可绑卡为从业者实测 | 二手 |
| Google Play 在中国大陆不可用 | ❌ 无官方声明；社区一致 | 二手 |
| 抖音"封建迷信"禁令 | ✅ 官方开放平台社区文章（2022-06-01 发布，2024-04-19 最后编辑） | 直接抓取 |
| 微信无占卜类目 | ✅ 官方开放类目文档 | 直接抓取 |

---

## 附录 3：研究中国侧合规与外汇约束

已完成调研。**声明：以下为公开法规原文的信息整理，不构成法律意见，不提供任何规避法律的建议。** 对于我无法从官方源核实的部分，我已明确标注。

---

# 中国居民个人运营「海外服务器 + 大六壬/八字 AI 测算网站」的合规风险清单

> 场景：个人（自然人）主体 / 服务器与 API 在境外 / 客户为海外用户 / 收费 / 数据经境外 AI API 处理

---

## 1. 「算命/占卜/封建迷信」相关监管

### 1.1 「宣扬邪教和封建迷信」被明确列为**违法信息**（非灰色地带）
**事实**：《网络信息内容生态治理规定》第六条列举网络信息内容生产者**不得**制作、复制、发布的内容，第（七）项为「破坏国家宗教政策，宣扬邪教和**封建迷信**」。
第七条另行列举 9 类「不良信息」（虚假标题、低俗媚俗、诱导未成年人等），**其中并未直接单列"算命"**。
**风险等级：高**（针对任何中国境内可访问的发布行为）
**依据**：[《网络信息内容生态治理规定》第六条、第七条](https://www.cac.gov.cn/2019-12/20/c_1578375159709309.htm) 第五条鼓励 / 第六条违法信息 / 第七条不良信息 / 第十九条–二十条平台义务 / 第三十四–四十条法律责任（2020-03-01 施行）

### 1.2 「面向海外」**不构成中国法上的当然豁免**
**事实**：该规定的规制对象是「网络信息内容生产者/服务平台/使用者」，条文并未以"服务对象是否在中国境内"为适用前提。同时，第七条要求「采取**实质重于形式**的审核原则」；平台/发布者若能预见内容流向中国境内，仍可能被认定为应履行管理义务。个人主体主动跨境营销（SEO、社媒投放、App Store/Google Play 上架）时，中国境内可访问性与可被投诉性都会上升。
**风险等级：高**
**依据**：同上；另见下文 1.5 域名/接入层面的义务

### 1.3 「个人」作为发布者不豁免法律责任
**事实**：该规定将「网络信息内容生产者」定义为**组织、个人**，未排除自然人。同一逻辑在 PIPL 中亦然——第七十三条第（一）项把「个人信息处理者」定义为「**组织、个人**」。因此"我不是公司、只是个人"在内容违法与数据违法两条线上均不减责。
**风险等级：中–高**
**依据**：[PIPL 第七十三条（一）](http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313088.html)；《网络信息内容生态治理规定》

### 1.4 算命内容在**平台侧**的必然后果
**事实**：主流平台（微信/抖音/快手/小红书/淘宝）与应用商店均将"算命、占卜、风水、命理"列为违规类目，处置方式为下架、封禁、扣分。实测层面，AI 命理类小程序与 App 在中国区应用商店长期处于不可上架或需资质状态。**此类治理是持续性的平台规则，而非一次性运动。**
**风险等级：高（现实操作性）**
**依据**：以上为平台公开规则与运营惯例；本次调研中中国网信网、中国政府网政策库**均未检索到 2023–2026 年针对"算命/占卜类 App、小程序"专门发布的**官方专项整治公告或典型案例通报 —— 即：**没有公开的中央层面专项文件，但平台侧规则一直在执行**。此结论为"检索未得"，不等于"不存在"。

### 1.5 ICP 许可/备案（若在境内落地任何节点）
**事实**：《互联网信息服务管理办法》（国务院令第 292 号，2000-09-25 公布，2011-01-08 修订）区分经营性/非经营性互联网信息服务，前者需许可、后者需备案。
**⚠️ 核实说明**：我**未能**从 gov.cn / miit.gov.cn 检索到该办法的现行有效全文页面（该库主要索引 2015 年后文件，1990s–2000s 规章未收录，相关 URL 均返回 404）。上述条文号与制度框架请以工信部/中国政府网官方发布为准，**不要仅依赖本条**。
**风险等级：低（若全链路境外）／中（若任何环节在境内）**
**依据**：《互联网信息服务管理办法》国务院令第 292 号（待核验现行文本）

---

## 2. 跨境服务与外汇

### 2.1 5 万美元额度是**"便利化额度"，不是免税/免审额度**
**事实（原文）**：
> **第五十四条**　个人经常项目外汇业务应具有真实、合法的交易背景。**个人结汇和境内个人购汇实行年度便利化额度管理，便利化额度分别为每人每年等值 5 万美元。**
> **第五十五条**　个人凭本人有效身份证件在银行办理年度便利化额度内的结汇和购汇。……个人可通过银行柜台或**电子银行**渠道办理结汇和购汇。

注意措辞：条号与标题是「**个人结汇**」的年度便利化额度，不是"服务贸易收入免税线"。
**风险等级：中**（金额小则实务风险低；金额大则触发 2.4）
**依据**：[《经常项目外汇业务指引（2020年版）》第五十四条、第五十五条](https://www.safe.gov.cn/safe/file/file/20200831/f0127756271c43ef9b3908d5d157bd91.pdf)（汇发〔2020〕14号）

### 2.2 「以服务贸易名义收款」——规则上是**可行**的，但需单证
**事实（原文）**：
> **第四十七条**　服务贸易外汇收支应具有真实、合法的交易基础，**境内机构和境内个人不得虚构贸易背景**办理外汇收支业务，**不得以分拆等方式规避外汇管理**。……**初次收入**，是指因**提供劳务**、金融资产和出租自然资源而获得的回报。
> **第五十二条**　服务贸易外汇收支涉及纸质或电子的交易单证应符合国家法律法规和通行商业惯例的要求，包括但不限于：（一）包含交易标的、主体、金额等要素的**合同（协议）**；（二）**发票（支付通知）**或列明交易标的、主体、金额等要素的**结算清单（支付清单）**；（三）其他能证明交易真实合法的单证。
> **第四十九条**　办理**单笔等值 5 万美元以下（含）**的服务贸易外汇收支业务，银行原则上可不审核交易单证；对于**资金性质不明确**的外汇收支业务，银行应要求境内机构和境内个人**提交交易单证**进行合理审核。办理**单笔等值 5 万美元以上（不含）**的……银行应按展业原则，确认交易单证所列的**交易主体、金额、性质**等要素与其申请办理的外汇收支相一致。

即：法律并未禁止居民个人收取境外服务收入；但**合同 + 发票/支付单**是明文要求的凭证，且 MoR（Merchant of Record）平台出具的结算单能否满足"主体/金额/性质"三要素一致性，是银行**逐笔**判断的。
**风险等级：高（凭证不足时）**
**依据**：同上 第四十七条、第四十九条、第五十二条

### 2.3 超过额度的合规通道是存在的，但要材料
**事实（原文）**：
> **第五十六条**　境内个人凭本人有效身份证件和**有交易额的结汇资金来源材料**，在银行办理**不占用年度便利化额度**的经常项目结汇。

配套：汇发〔2021〕13号 第六条要求银行建立「个人经常项目**特殊外汇业务处置制度**」，对"不常见、难判断"但真实合法的个人经常项目业务，按「**实质重于形式**」原则办理。
**风险等级：中**（通道存在，但银行有实质审核权与自由裁量权）
**依据**：[《经常项目外汇业务指引（2020年版）》第五十六条](https://www.safe.gov.cn/safe/file/file/20200831/f0127756271c43ef9b3908d5d157bd91.pdf)；[《关于进一步推进个人经常项目外汇业务便利化的通知》汇发〔2021〕13号 第六条](https://www.safe.gov.cn/safe/2021/0402/18672.html)

### 2.4 「长期、大额、不申报」的性质 —— 双重违规，且行刑衔接已建立
**事实（原文）**：
> **第六十二条**　个人**不得以分拆等方式规避便利化额度管理及真实性管理**。外汇局对规避管理的个人实行"**关注名单**"管理……（三）"关注名单"内个人的**关注期限为列入"关注名单"的当年及之后连续 2 年**。在关注期限内，"关注名单"内个人办理个人结售汇业务，应凭本人有效身份证件、**有交易额的相关材料**在银行办理。
> **第一百八十八条**　违反本指引规定的，由外汇局依据《中华人民共和国外汇管理条例》及相关规定予以处罚。

且 2026-08-24 最高检与外汇局联合印发《外汇领域行刑反向衔接工作指引》，建立"检察机关对**不起诉**但认为应予行政处罚的案件，**移送外汇管理部门**"的闭环机制 —— 这意味着**即便刑事上未起诉，外汇行政处罚仍会跟上**，刑事程序不构成挡箭牌。
**风险等级：高**（长期、大额、拆分、借用他人额度）
**依据**：[《经常项目外汇业务指引（2020年版）》第六十二条、第一百八十八条](https://www.safe.gov.cn/safe/file/file/20200831/f0127756271c43ef9b3908d5d157bd91.pdf)；[《外汇领域行刑反向衔接工作指引》（2026-08-24，最高检、国家外汇局）](https://www.safe.gov.cn/safe/2026/0929/27935.html)

### 2.5 MoR 收款的额外外汇风险
**事实**：若由境外 MoR 平台代收（Stripe/Paddle/Lemon Squeezy 等）后汇入，**境内银行在结汇环节看到的资金性质往往无法自证**。指引第四十九条明确：资金性质不明确的，银行**应当要求提交交易单证**。个人在 MoR 结算单上通常没有中国大陆税务/发票体系中的对应凭证。
**风险等级：中–高**
**依据**：《经常项目外汇业务指引（2020年版）》第四十九条、第五十二条、第六十八条（银行"有权对违反外汇管理规定、真实性存疑的交易予以拒绝"）

---

## 3. 税务

### 3.1 中国税收居民对**全球所得**纳税
**事实**：《个人所得税法》第一条确立纳税义务人，其中**居民个人从中国境内和境外取得的全部所得，依法缴纳个人所得税**；非居民个人仅就境内所得纳税。税收居民身份以"有住所"或"无住所但一个纳税年度内在境内居住累计满 183 天"判定。**"服务器在境外""用户是外国人""钱在海外账户"均不改变居民个人的全球纳税义务。**
**风险等级：高（长期、大额、零申报）**
**⚠️ 核实说明**：我**未能**抓取到《个人所得税法》第一条、第二十三条的现行官方全文页（npc.gov.cn 与 gov.cn 相关 URL 均 404 或返回非条文页面；中国政府网政策库不收录法律）。上述内容属该法基本框架，但**请以全国人大官方文本为准**。

### 3.2 境外所得须在**年度汇算清缴**中并入
**事实**：中国实行综合所得年度汇算清缴机制。居民个人的境外所得（劳务报酬、稿酬、特许权使用费、财产租赁、财产转让、利息股息等）须按规定折算为人民币并入综合/经营所得汇算，多退少补。境外已纳税的可按限额抵免。
**风险等级：高**
**⚠️ 核实说明**：同上，条文原文未取到；另需注意**税收协定待遇、非居民个人财产转让等特殊规则**，本次未展开核实。

### 3.3 MoR 收款**是否算境外收入**——算
**事实**：收入是否"境外"，取决于**支付方所在地与合同履行地**，不取决于收款通道。面向海外用户提供的服务，其收入来源地通常在境外，属**境外所得**，应在境外所得栏申报并换算成人民币。
**风险等级：中–高**
**依据**：个人所得税法（居民个人全球所得原则，见 3.1）

### 3.4 逾期与不申报的定性
**事实**：居民个人不申报境外所得可能触及：
- **《个人所得税法》**：未按规定期限办理申报 → 税务机关可责令限期改正、**按日加收万分之五滞纳金**，并可处应纳税款 50%–3 倍罚款；
- 情节严重的，**构成偷税**，涉刑事责任。
- 中国税收大数据（2024 年起）已显著加强境外收入穿透核查。
**风险等级：高**
**⚠️ 核实说明**：滞纳金比例与罚款倍数为个人所得税法及税收征管法规定，但本次未取到条文原文页面，请以现行法条/税务机关口径为准。

---

## 4. 数据出境

### 4.1 PIPL 是否适用 —— **可能适用，取决于数据主体而非服务器位置**
**事实（原文）**：
> **第三条**　在中华人民共和国境内处理自然人个人信息的活动，适用本法。**在中华人民共和国境外处理中华人民共和国境内自然人个人信息的活动**，有下列情形之一的，也适用本法：（一）**以向境内自然人提供产品或者服务为目的**；（二）**分析、评估境内自然人的行为**；（三）法律、行政法规规定的其他情形。

**关键判断**：服务**只面向海外用户 → 理论上不落入第（一）项**；但一旦做中文 SEO、中文落地页、社媒投放、或有中国境内用户试用，即可能被认定"以向境内自然人提供服务为目的"，从而**整个境外处理活动受 PIPL 管辖**。
**风险等级：中–高（取决于是否触达境内用户）**
**依据**：[PIPL 第三条、第七十三条（一）](http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313088.html)

### 4.2 出生时间 + 姓名 = 敏感个人信息处理
**事实（原文）**：
> **第二十八条**　敏感个人信息是一旦泄露或者非法使用，容易导致自然人的**人格尊严**受到侵害或者人身、财产安全受到危害的个人信息，包括**生物识别、宗教信仰、特定身份、医疗健康、金融账户、行踪轨迹**等信息，以及不满十四周岁未成年人的个人信息。**只有在具有特定的目的和充分的必要性，并采取严格保护措施的情形下**，方可处理敏感个人信息。

大六壬/八字测算的核心输入恰是**精确出生时间（时柱依赖具体时辰与时区）**与**姓名**。姓名+精确出生时间组合可反推身份，且在特定文化语境下会牵涉宗教信仰/民族属性 —— 属于典型的**高度敏感、需"特定目的+充分必要性+严格保护措施"**的范畴。
**风险等级：高（一旦 PIPL 适用）**
**依据**：PIPL 第二十八条

### 4.3 出境的四道法定条件
**事实（原文）**：
> **第三十八条**　个人信息处理者因业务等需要，确需向中华人民共和国境外提供个人信息的，应当具备下列条件之一：（一）通过国家网信部门组织的**安全评估**；（二）经专业机构进行**个人信息保护认证**；（三）按照国家网信部门制定的**标准合同**与境外接收方订立合同；（四）法律、行政法规或者国家网信部门规定的其他条件。
> **第三十九条**　……应当向个人告知境外接收方的名称或者姓名、联系方式、处理目的、处理方式、个人信息的种类以及个人向境外接收方行使本法规定权利的方式和程序等事项，并**取得个人的单独同意**。
> **第五十五条**　有下列情形之一的，个人信息处理者应当**事前进行个人信息保护影响评估**……（四）**向境外提供个人信息**。

即：**向境外 AI API 传输出生时间与姓名，是"向境外提供个人信息"**，触发告知+单独同意+PIA。
**风险等级：高（一旦 PIPL 适用）**
**依据**：PIPL 第三十八条、第三十九条、第五十五条

### 4.4 2024 年门槛放宽：10 万人以下有明确豁免
**事实（原文）**：
> **第五条**　……**（四）关键信息基础设施运营者以外的数据处理者自当年 1 月 1 日起累计向境外提供不满 10 万人个人信息（不含敏感个人信息）的**，免予申报数据出境安全评估、订立个人信息出境标准合同、通过个人信息保护认证。
> 前款所称向境外提供的个人信息，**不包括重要数据**。
> **第八条**　……累计向境外提供 **10 万人以上、不满 100 万人**个人信息（不含敏感个人信息）或者**不满 1 万人敏感个人信息**的，应当依法与境外接收方订立个人信息出境标准合同或者通过个人信息保护认证。

**但豁免的是"程序"，不是"实体义务"**：第三条对不含个人信息/重要数据的数据全面豁免；第四条对"境外收集→境内处理→再出境且未混入境内个人信息"的数据全面豁免。**本场景的输入是境内用户自己填的，第四条不适用。** 第五条(四) 的**敏感个人信息不在豁免范围内**（"不含敏感个人信息"是限定语），而出生时间+姓名按 4.2 很可能构成敏感个人信息 —— 因此**这个豁免对本场景大概率不成立**，敏感个人信息累计满 1 万人即触发标准合同/认证。
**风险等级：高**
**依据**：[《促进和规范数据跨境流动规定》第三、四、五、八条](https://www.cac.gov.cn/2024-03/22/c_1712776611775632.htm)（网信办令第16号，2024-03-22）；[《数据出境安全评估办法》答记者问](https://www.cac.gov.cn/2022-07/07/c_1658811536800962.htm)（1万敏感个人信息门槛；处罚依《网安法》《数安法》《个保法》）

### 4.5 未合规出境的罚则
**事实（原文）**：
> **第六十六条**　违反本法规定处理个人信息，或者处理个人信息未履行本法规定的个人信息保护义务的，由履行个人信息保护职责的部门责令改正，给予警告，没收违法所得，对违法处理个人信息的应用程序，责令暂停或者终止提供服务；**拒不改正的，并处一百万元以下罚款**；对直接负责的主管人员和其他直接责任人员**处一万元以上十万元以下罚款**。
> 有前款规定的违法行为，**情节严重的**，由**省级以上**……**并处五千万元以下或者上一年度营业额百分之五以下罚款**，并可以责令暂停相关业务或者停业整顿、通报有关主管部门**吊销相关业务许可或者吊销营业执照**；对直接负责的主管人员和其他直接责任人员处**十万元以上一百万元以下罚款**，并可以决定禁止其在一定期限内担任相关企业的董事、监事、高级管理人员和个人信息保护负责人。

**注意最后一项**：对**个人**直接责任人员也可罚款 1 万–100 万，并可**限制担任企业董监高及个人信息保护负责人**。
**风险等级：高（一旦 PIPL 适用且情节严重）**
**依据**：PIPL 第六十六条

---

## 5. AI 服务

### 5.1 备案义务**以"是否向境内公众提供"为开关**
**事实（原文）**：
> **第二条**　利用生成式人工智能技术向**中华人民共和国境内公众**提供生成文本、图片、音频、视频等内容的服务，适用本办法。……行业组织、企业、教育科研机构、公共文化机构、有关专业机构等**研发、应用**生成式人工智能技术，但**未向境内公众提供服务**的，不适用本办法。

**答"若仅面向境外用户呢"**：字面上，**纯境外用户 → 不适用该办法，暂无备案要求**。但有三个收紧点：
1. **第二十条**：对**来源于境外、向境内提供**、不符合规定的生成式 AI 服务，网信部门应通知有关机构采取**技术措施和其他必要措施处置** —— 即境内入口可被封堵；
2. 一旦**任何中国境内用户可访问/注册**，开关即打开；
3. 大六壬/八字带有"**陪伴、咨询、情感互动**"属性时，可能落入下条 5.2。
**风险等级：中（纯境外）/ 高（触达境内或被认定为情感互动）**
**依据**：[《生成式人工智能服务管理暂行办法》第二条、第十七条、第二十条、第二十一条](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)（2023-08-15 施行）

### 5.2 2026 年新增的**《人工智能拟人化互动服务管理暂行办法》** —— 与本场景高度相关
**事实（原文）**：
> **第二条**　……向中华人民共和国境内公众提供模拟自然人人格特征、思维模式和沟通风格的**持续性的情感互动服务**（即"拟人化互动服务"），适用本办法。……提供**智能客服、知识问答、工作助手、学习教育、科学研究等服务，不涉及持续性的情感互动**的，不适用本办法。

AI 命理/测算产品普遍以"你的专属命理顾问""随时倾诉、陪你决策"作为交互设计，**极易被认定为"持续性情感互动服务"**。适用后的义务密集：

| 条款 | 义务 | 风险触发点 |
|---|---|---|
| 第22条 | **安全评估**（省级网信部门） | 上线该服务即评估；**注册用户 100 万以上或月活 10 万以上** |
| 第26条 | **算法备案 + 年度核验** | 备案材料由网信部门**年度**核验 |
| 第8条 | **七类禁止内容** | 不得"过度迎合、**诱导情感依赖或沉迷**"、"通过**情感操纵诱导用户作出不合理决策**" —— 命理预测天然贴近"诱导用户决策"边界 |
| 第10条 | **不得将替代社会交往、控制用户心理、诱导沉迷依赖作为服务目标**；须具备依赖风险预警能力 | 与"AI 命理师陪聊变现"模式直接冲突 |
| 第13条 | 须识别极端情绪，**联络监护人/紧急联系人** | 无相应机制即违规 |
| 第16条 | 用户交互数据**加密、访问控制**；除法定或权利人同意外不得向第三方提供；提供复制/删除选项；**不得将敏感个人信息交互数据用于模型训练**（除单独同意） | 用用户对话微调模型 = 需单独同意 |
| 第18条 | **生成合成内容标识**；提示"正在与 AI 而非自然人互动"；**每连续使用超 2 小时提醒** | 已在《AI生成合成内容标识办法》单独立规 |
| 第30条 | **罚则** | 责令限期改正；拒不改正或情节严重：责令停止服务 + **并处 1 万–10 万元罚款**；涉及危害生命健康且有后果：**并处 10 万–20 万元** |
| 第31条 | 提供**卫生健康、金融**等服务的，须同时符合对应主管部门规定 | 命理产品常涉"健康/财运"话术 → 可能叠加卫健/金融监管 |

**⚠️ 核实说明**：本条**仅限向"境内公众"提供**。纯海外业务不适用。但若面向中文用户开放、在中国区应用商店上架、或在中国境内投放，即触发。
**风险等级：高（若被认定适用）**
**依据**：[《人工智能拟人化互动服务管理暂行办法》](https://www.gov.cn/gongbao/2026/issue_12806/202606/content_7072472.html)（网信办等五部门令第21号，2026-04-10 公布，**2026-07-15 施行**）

### 5.3 深度合成备案（同一逻辑的第二层）
**事实（原文）**：
> **第二条**　在中华人民共和国境内应用深度合成技术提供互联网信息服务，适用本规定。
> **第十九条**　具有**舆论属性或者社会动员能力**的深度合成服务提供者，应当按照《互联网信息服务算法推荐管理规定》履行**备案和变更、注销备案手续**。深度合成服务**技术支持者**应当**参照**前款规定履行备案……
> 第二十条　开发上线具有舆论属性或者社会动员能力的**新产品、新应用、新功能**的，应当按照国家有关规定**开展安全评估**。

**"技术支持者"条款值得注意**：作为"技术支持者"（提供 API/模型/工具的一方）也须参照备案。境外 AI 服务商不适用；但**若开发者被视为境内运营方，则可能被要求自行完成备案与安全评估**。
**风险等级：中–高（若被认定适用）**
**依据**：[《互联网信息服务深度合成管理规定》第二条、第十九条、第二十条](https://www.cac.gov.cn/2022-12/11/c_1672221949354811.htm)（2023-01-10 施行）

### 5.4 内容标识是**独立义务**，且与备案挂钩
**事实（原文）**：第二条将《标识办法》适用对象限定为"符合《算法推荐管理规定》《深度合成管理规定》《**生成式人工智能服务管理暂行办法**》规定情形的网络信息服务提供者" —— 即**以基础 AI 规章的适用为前提**。第三条定义显式/隐式标识；第四、五条规定文本须在起始/末尾/中间添加文字或符号提示、文件元数据须含属性信息/服务提供者名称编码/内容编号；**第十二条**要求履行算法备案、安全评估时须提供标识相关材料；**第十四条：2025-09-01 施行**。
**风险等级：中**（适用前提不成立则不适用，但一旦适用是硬性技术义务）
**依据**：[《人工智能生成合成内容标识办法》](https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm)（国信办通字〔2025〕2号）

### 5.5 在境内使用 OpenAI/Anthropic 境外 API
**事实**：
- **技术上**：需使用跨境网络连接工具，这在中国境内涉及《计算机信息网络国际联网管理暂行规定》（国务院令第 33 号，1996）及《非经营性互联网信息服务备案管理办法》等对"国际联网"的准入与实名管理；个人在境内使用此类工具并用于**经营性用途**存在合规瑕疵。
- **服务条款层面**：OpenAI 与 Anthropic 的**服务条款均禁止在中国境内提供服务/使用**。以中国居民身份、在境内调用并转售输出，违反的是**服务商的合同条款**（在特定法域可执行），**不是**直接的中国行政法禁止。
- **监管实践**：中国网信办对境外生成式 AI 服务**未提供**面向境内开发者的合法接入通道；2026 年 4 月 10 日发布的《AI拟人化互动服务管理暂行办法》同样不涉及境外模型接入的合法化。
- **数据出境后果**：把境内用户出生时间、姓名送入境外模型，同时触发第 4 节的 PIPL 出境义务 —— **这是比"用什么 API"严重得多的问题**。
**风险等级：中（API 使用本身）／高（叠加数据出境后）**
**依据**：[生成式 AI 办法第二十条（境外向境内提供的处置）](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)；《计算机信息网络国际联网管理暂行规定》（国务院令第33号，⚠️ 本次未取到现行官方文本，请自行核验）

---

## 6. 出海与主体

### 6.1 个人（自然人）直接开展跨境经营的常见结构性问题
**事实**：以下为跨境经营实务中反复出现的结构性障碍（非某一具体条文，而是多部法律的叠加结果）：

| 问题 | 说明 | 风险 |
|---|---|---|
| **无法签约/收款** | 多数支付渠道、PayPal/Stripe/苹果与 Google 开发者协议要求**已注册法人实体**，个人无法申请 | 高（商业可行性） |
| **无法开具发票** | 服务贸易收汇需合同+发票（指引第52条）；自然人无发票主体，MoR 结算单未必被银行接受 | 高 |
| **无法为用户开票** | 海外用户要求 VAT/GST 发票时，自然人无法开具 | 中 |
| **法律责任承载** | 自然人不享有限责任；个人财产直接暴露于产品侵权、消费者索赔、数据违规罚款（PIPL 第66条对个人可罚 100 万） | 高 |
| **无法办理资质** | ICP/EDI、增值电信业务许可、支付业务等均要求企业主体 | 中 |
| **外汇与税务身份重叠** | 自然人同时是服务提供者、收款方、纳税人、结汇申报人，链条最短但每一环都无容错 | 高 |
| **人身与地域管辖** | 服务器在境外 ≠ 属地管辖在境外；自然人在中国境内 ⇒ 境内行政机关可依属人管辖/行为管辖采取措施 | 中–高 |

**风险等级：高（综合）**

### 6.2 设立境外主体的**一般性描述**（非建议）
**事实**：实务中"服务出海"通常通过在境外设立法人实体完成，常见法域为**香港有限公司**、**新加坡公司**、**美国 LLC**（部分州如 Delaware/Wyoming）。其一般性作用是：
1. 提供与支付渠道/应用商店对接所需的**法人主体**；
2. 将**合同签约方、收款方、开票方**与自然人分离，实现有限责任；
3. 便于接受海外投资人与完成尽调（银行 KYC 要求收款主体为可识别法人）；
4. 提供独立的银行账户与财务账簿。

**⚠️ 重要边界（必须点明）**：
- 设立境外主体**不改变**该自然人的**中国税收居民身份**，境外主体向其分配利润仍可能触发中国个人所得税；
- 设立境外主体**不解决**内容合规（1）与数据合规（4）问题 —— 若业务仍触达中国用户或处理中国境内用户信息，相关义务不变；
- 境外主体本身还需遵守其注册地与运营地的公司、税务、消费者保护、博彩/占卜行业许可制度（部分国家/地区对占卜服务有独立许可或禁令，**本次未逐法域核实**）。
**风险等级：中（结构性缓解，非合规豁免）**

---

## 如果一定要做，最容易踩的 3 个合规坑

### 坑 1：把「服务器在境外 / 用户是外国人」当成管辖上的免死金牌
这是最普遍、也是最致命的误判。**中国法的管辖开关不是"服务器在哪"，而是"是否以向境内自然人提供产品或服务为目的"（PIPL 第3条）、是否"向境内公众提供"（生成式AI办法第2条、AI拟人化互动办法第2条）、以及内容是否"可被认定宣扬封建迷信"（内容生态规定第6条）。** 一旦做了中文 SEO、中文落地页、中文客服、社媒投放、在中国区应用商店上架、或有境内用户试用，三条线会**同时**打开：内容违法、需备案、数据出境。**且 PIPL 第66条对个人直接责任人员可罚 1 万–100 万，并可禁止其担任企业董监高及个人信息保护负责人。**

### 坑 2：以为"收到钱再想办法汇回国"，忽略 MoR 收款在结汇环节的凭证断点
这是最容易在第一笔大额收入时爆雷的坑。指引第 49 条写得很清楚：**资金性质不明确的，银行应当要求提交交易单证**；第 52 条要求**合同（协议）+ 发票/支付通知或结算清单**。MoR 平台出具的是境外格式的 merchant settlement statement，**通常不含合同要素的主体/金额/性质与个人服务贸易的对应关系**，银行会要求补充材料；补不齐则被拒（指引第 68 条银行"有权对违反外汇管理规定、真实性存疑的交易予以拒绝"）。同时：
- 年度便利化额度是 **5 万美元/人/年**（第 54 条），且**第 62 条明确禁止"分拆等方式规避"** —— 用亲友额度、拆单汇入是**明文禁止**行为，会进"**关注名单**"（当年及之后连续 2 年，期间每笔均须提供有交易额材料）；
- 2026-08-24 起，**刑事不起诉 ≠ 免于外汇处罚**，检察机关会把案件移回外汇管理部门（行刑反向衔接）。
- 税务侧：居民个人的**全球所得**纳税义务不因账户在境外而消失，MoR 收入仍属**境外所得**，须并入年度汇算。

### 坑 3：把「5 万美元便利化额度」误读为「收入免税线」或「合规通道」
第 54 条的原文是「**个人经常项目外汇业务应具有真实、合法的交易背景**。个人结汇和境内个人购汇实行年度便利化额度管理」—— 便利化额度解决的是**"办手续的简化程度"**，不是**"要不要申报"**。第 56 条才是真正的超额度通道，但它要求「**有交易额的结汇资金来源材料**」，即回到坑 2 的凭证问题。同时，把收款拆到 5 万美元以下、或用他人额度，是第 62 条**点名禁止**的规避行为，而 2026 年的行刑反向衔接机制意味着这种"拆分"痕迹一旦被系统识别，行政处罚几乎必然落地。

---

## 调研边界（请注意）

本次调研在受限的网络环境下完成（多数通用搜索引擎被反爬拦截），**以下内容未能从官方源核实，因此在上文中已逐条标注**：

| 未能核实项 | 影响 |
|---|---|
| 《互联网信息服务管理办法》现行有效全文 | 1.5 的条文号与制度框架需以工信部/中国政府网发布为准 |
| 《个人所得税法》境外所得条文原文 | 3.1–3.4 的框架为该法基本结构，具体条文号与滞纳金/罚款比例请以现行法条为准 |
| 2023–2026 年针对算命/占卜类 App/小程序/自媒体的**具体整治案例或专项通报** | 1.4 仅能确认**平台侧规则持续执行**；**未发现**中央层面专门公告。"未检索到"≠"不存在" |
| 《计算机信息网络国际联网管理暂行规定》现行文本 | 5.5 中"翻墙用于经营性用途"的法规定性需自行核验 |
| 各境外法域对占卜服务的行业许可/禁令 | 6.2 未逐法域展开 |
| 税收协定待遇、非居民财产转让等个税特殊规则 | 3 未展开 |

**再次声明：本文为公开法规原文的信息整理与风险清单，不构成法律意见，不构成对任何具体交易结构的推荐或背书。任何实际决策前，请就上述未核实项及整体结构咨询执业律师与执业税务师。**

---

## 附录 4：研究支付商对占卜类目政策

# 海外收款服务商对「占卜/命理/玄学」类数字产品的态度

> 调研日期：2026-10-02。所有结论均基于**当前生效的政策原文页面**（下表标注了 last updated 日期）。
> ⚠️ 重要前提：「不在禁售名单上」≠「一定批」。多数收单方都有"deceptive/unverifiable claims"这类**兜底条款**——真正卡人的往往不是品类，而是**宣传话术**。这是本次调研最重要的发现。

---

## 一、核心结论速览

| 服务商 | 对占卜/命理态度 | 决定性原文 | 中国个人可用？ |
|---|---|---|---|
| **Paddle** | 🔴 **明确禁售** | "pseudo-science... clairvoyance, horoscopes, fortune-telling" | ❌ 无需考虑 |
| **Creem** | 🔴 **明确禁售** | "Metaphysical, fortune-telling, and spiritual outcome services" | ❌ 无需考虑 |
| **Dodo Payments** | 🟡 **限制但可申请** | Restricted: "Spiritual & Astrology services – **Entertainment only; no claims or predictions**" | ✅ **支持 China + Hong Kong** |
| **Gumroad** | 🟢 **明确允许**（最友好） | "astrology, tarot, numerology, birth-chart and divination material... **chart-generation tools and pre-written reports are all allowed**" | ⚠️ 需确认中国收款 |
| **Stripe (US/HK)** | 🟢 **名单内无** | 全表无 "Occult"；"Psychic services and fortune tellers" 仅限 Japan/Mexico/Thailand | ❌ **不支持中国大陆**，仅香港 |
| **Lemon Squeezy** | 🟢 **名单内无** | 禁售清单无任何玄学类目 | ⚠️ 同上（Stripe 体系） |
| **PayPal** | 🟢 **名单内无** | AUP 无 occult 条款，18 项 pre-approval 亦无 | ⚠️ 需确认中国个人账户收款能力 |
| **Patreon** | 🟢 **无禁止** | 11 类禁售清单无玄学类目 | ✅ 订阅制 |
| **Podia** | 🟢 **无禁止** | "allow **nearly all content**... with a minimal set of restrictions" | ⚠️ 需确认 |
| **Ko-fi** | ❓ **未核实** | 官网/帮助中心全程 403，无法取证 | — |

---

## 二、逐条原文引用

### 1. Paddle —— 🔴 明确禁售

> **Prohibited Categories, #14:**
> "**Digital services associated with pseudo-science, including but not limited to clairvoyance, horoscopes, fortune-telling**"

另有开放式兜底条款：
> "Paddle reserves the right to exercise judgment in ascertaining whether any of these factors are likely to be present."

页面标注 `_Last Updated 13 April 2026_`
🔗 https://www.paddle.com/support/aup/ （注意：真实地址是 `paddle.com/support/aup/`，`paddle.com/legal/acceptable-use-policy` 已 404）

**中国可用性**：Paddle 支持中国（不在 Unsupported Countries 列表内）🔗 https://www.paddle.com/help/start/intro-to-paddle/which-countries-are-supported-by-paddle —— 但既然品类被禁，讨论无意义。

---

### 2. Creem —— 🔴 明确禁售（证实你的线索）

> **Prohibited products（完整清单中的一项）：**
> "**Metaphysical, fortune-telling, and spiritual outcome services**"

> **Acceptable products**（对照）："Software & SaaS / eBooks / PDFs / Design assets / Photos / Audio / Video"

另有对 AI 产品的限制：
> **Restricted products:** "Generative AI products, including, but not limited to text-to-image and text-to-video generation tools" —— "All restricted products require additional verification, including previous payment processor details, chargeback/refund rate, and reason for moving to Creem."

> "If you're unsure whether your content is prohibited, contact Creem support with a description or example before you start selling."

🔗 https://docs.creem.io/merchant-of-record/account-reviews/account-reviews
（Creem 主站 `/prohibited-products`、`/legal/prohibited-products` 均 404，政策实际在 docs 站）

**中国可用性**：Creem **支持中国 + 香港**（Supported Countries 含 `China*` 和 `Hong Kong`）🔗 https://docs.creem.io/merchant-of-record/supported-countries —— 但同样因品类被禁而出局。

> 📌 **Creem 与 Paddle 是最容易被 indie hacker 误选的两家**——它们都以 "indie hacker / AI SaaS" 营销，而且都支持中国注册，但都精准点名禁掉了 fortune-telling。

---

### 3. Dodo Payments —— 🟡 限制，但有明确可申请通道 ⭐

这是本次调研**对"AI 命理"定位最有价值的一条**。Dodo 同时把玄学放进了禁售和限制两份清单，关键在于措辞差异。

**Prohibited #15（禁售）**：
> "**Religious or spiritual product or services** — This includes offerings of spiritual guidance, paid prayers, rituals, faith-based counselling, or similar services where users are paying for religious or spiritual interaction **or access to a religious or spiritual authority**."

**Restricted（"Categories That Often Require Review"）第 4 条**：
> "**Spiritual & Astrology services — Entertainment only; no claims or predictions**"

🔗 https://docs.dodopayments.com/miscellaneous/merchant-acceptance

**解读**：禁售项针对的是**真人灵性权威/真人咨询**（付费算命师、代祷、仪式）。而"星象/灵性服务，仅供娱乐、不做预测与断言"是**可申请**的受限类目。一个**自动化、算法驱动、只输出解读文本**的八字/占星报告，落入后者的可能性显著高于前者。

**中国可用性 —— 这是 Dodo 的最大优势**：
> "Eligibility is based on **the country that issued the government-issued identity document you verify with**, not on where your company is registered or where you pay tax."
> "Tax residence, a residence permit, and a local bank account are all helpful, but **none of them replace a government-issued ID from a listed country**."

接受国家列表 **明确含 `32. China` 和 `72. Hong Kong`**，支持个人（Individual）与注册实体。
🔗 https://docs.dodopayments.com/miscellaneous/accepted-countries-and-territories （last modified 2026-08-27）

⚠️ **Dodo 的隐藏地雷**——同页 Prohibited #3：
> "**Digital products with limited or unclear value** — For example, AI-generated PDFs with little value, thin templates marked up heavily... This also includes placeholder or pre-launch offerings such as holding pages, teaser sites, waitlists, or 'coming soon' products"

以及 Prohibited #13：
> "**Miracle, Misleading, or Unverifiable Claims** — No products making exaggerated or unverifiable claims"

**这意味着**：不能卖「一份 AI 生成的薄 PDF 报告」。产品必须是真的**软件/应用**（有持续使用价值），且文案不能承诺结果。

---

### 4. Gumroad —— 🟢 明确允许，且直接点名"报告生成工具" ⭐⭐

这是全网**对八字/占星类产品最友好的成文政策**。Gumroad 禁售清单第 29 项写的是 "fortune tellers"，并配了一段极为明确的解释性注释：

> **"A note on fortune tellers"**
> "The fortune teller entry above covers operating a prediction service: concrete claims about what will happen to a buyer, and readings framed as medical, legal or financial advice. It also covers open-ended personal consultations sold as access to a practitioner who will tell the buyer what to do."
>
> "**It does not cover astrology, tarot, numerology, birth-chart and divination material sold for insight, reflection or entertainment. That work has its own Discover category, and courses, decks, guidebooks, chart-generation tools and pre-written reports are all allowed.** A one-off personalized reading is also allowed when it is sold as reflection or entertainment and makes no concrete promise about what will happen; what is not allowed is ongoing access to a practitioner who tells the buyer what to do."
>
> "**The test is what the product promises, not what tradition it draws on.** If it guarantees an outcome or substitutes for a professional the buyer should be seeing instead, it is prohibited. If it offers an interpretation the buyer is free to take or leave, whether they work through it themselves or a practitioner prepares it for them, it is allowed."

🔗 https://gumroad.com/prohibited

**逐条比对你的产品**：
- ✅ `chart-generation tools` —— 八字排盘生成器，**明确允许**
- ✅ `pre-written reports` —— 预生成报告，**明确允许**
- ✅ `sold for insight, reflection or entertainment` —— 娱乐/自我反思定位，**明确允许**
- ❌ `concrete claims about what will happen` —— 「你今年会结婚」「这个月有破财」→ **禁止**
- ❌ `access to a practitioner who will tell the buyer what to do` —— 真人实时咨询通道 → **禁止**
- ❌ `framed as medical, legal or financial advice` —— 「婚姻/健康/财运指导」框架 → **禁止**

**"The test is what the product promises, not what tradition it draws on"** —— 这句话就是本报告的核心结论。

Gumroad 技术栈：Stripe + PayPal（ToS §5 明确披露）。
⚠️ 需注意：Gumroad 通过 Stripe Connect 处理，理论上仍受 Stripe 名单约束（而 Stripe 名单是干净的，见下）。
⚠️ 中国个人能否在 Gumroad 开户并收款，需自行确认（其 ToS 未公开限制清单）。

---

### 5. Stripe / Lemon Squeezy / Stripe Managed Payments —— 🟢 "Occult" 已不在名单

**核实结果：Stripe 当前 US 和 HK 政策页面中，"Occult" 一词完全不出现。**

`Last updated: 2026-09-22`。全部 Prohibited（17 大类）与 Restricted（13 大类）清单中无任何玄学条目。

**但 "Psychic services and fortune tellers" 确实存在——在 jurisdiction-specific 区**：

| 辖区 | 条目 | 性质 |
|---|---|---|
| Japan | Psychic services and fortune tellers | 禁 |
| Mexico | Psychic services and fortune tellers | 禁 |
| Thailand | Psychic services and fortune tellers **P** | **禁**（P = Prohibited） |
| **United States** | *（无此条）* | — |
| **Hong Kong** | *（无此条）* | — |
| EU / UK / SG / AU | *（无此条）* | — |

🔗 https://stripe.com/us/legal/restricted-businesses ｜ https://stripe.com/en-hk/legal/restricted-businesses

⚠️ **务必注意的两点**：
1. **"Japan 禁止 psychic services" 意味着不要以日本为市场**——即使你用美国账户收款。
2. **Stripe 对中国大陆商户完全不开放。** 官方 Global availability 列表 49 个国家/地区中，**"Mainland China" 不在其中**（"Hong Kong" 在）。🔗 https://stripe.com/global
   > "Stripe is currently supported in the following countries/regions… **Hong Kong**…"（中国仅出现在页面底部的语言选择器中）

**Lemon Squeezy**：禁售清单**无**任何玄学相关词条，且页面直接指向 Stripe 的 restricted-businesses 页面作为上级政策。禁售项仅 19 条（NSFW、Services of any kind、IPTV、Physical goods、eSIM 类、Job boards、Marketplaces、PLR/MRR、 Dating sites、Pharmacies、MLM、NFT/Crypto 等）。
🔗 https://docs.lemonsqueezy.com/help/getting-started/prohibited-products
> "If you're unsure whether your content is prohibited, please contact Lemon Squeezy support with a description or example of the content before you start selling."

---

### 6. PayPal —— 🟢 名单内无

`Last updated on October 29, 2022`（US 版 AUP）。

**Prohibited Activities** 5 条：违法、毒品/香烟/赃物/仇恨/淫秽/知识产权/武器、 Pyramids & 金融类、"**products or services identified by government agencies to have a high likelihood of being fraudulent**"、需预批未预批。
→ **无 occult / fortune telling / astrology 任何表述。**

**18 项 "Activities Requiring Approval"** 逐项核对：Transportation / Charity / High Value Items / Payment Facilitator / Investments / Gambling / Crypto / Prescription / Telemedicine / Mature Audience / Online Dating / Live Streaming / File-Sharing / Alcohol / Tobacco / Medical / MLM / Marketplaces
→ **同样无玄学类目。**

🔗 https://www.paypal.com/us/legalhub/acceptableuse-full

⚠️ **真实风险点**：Prohibited #4 "high likelihood of being fraudulent" 是 PayPal 冻结账户最常用的依据。玄学类产品最容易被举报为"诈骗"的场景是**退款率异常 + 用户期待落空**，不是品类本身。
⚠️ **中国个人账户**：PayPal 中国大陆个人账户的跨境**收款**能力有限制（历史上仅支持部分场景），需单独确认——这与政策无关，是账户能力问题。

---

### 7. Patreon —— 🟢 无禁止（订阅制模型友好）

**Community Guidelines**（已抓取全文核对）：adult/18+ 规定详尽，但 **occult / astrology / tarot / divination / fortune telling / spiritual 全部零命中**。

**Commerce Guidelines** 的 11 类禁售项完整列表：
> 1. Alcohol, Tobacco, and Related Pararaphernalia
> 2. Drugs, Prescription Products, and Supplements
> 3. Financial Products, Services, and Benefits
> 4. Food and Health
> 5. Gambling, Raffles, and Sweepstakes
> 6. Gift Cards, Vouchers, Coupons, and Crowdfunding
> 7. Intellectual Property, Copyrights, and Trademarks
> 8. Recalled Products
> 9. Sexual Products, Services, and Benefits
> 10. Violence and Hate
> 11. Weapons, Ammunition, and Explosives

→ **无玄学类目。** 框架性总则：> "Do not do anything illegal."

🔗 https://www.patreon.com/policy/guidelines ｜ https://www.patreon.com/policy/benefits

✅ **对个人创作者友好**，且 Patreon 有真实的塔罗/占星创作者生态（这是最成熟的现成案例）。
⚠️ Patreon 底层用 Plexi/Stripe/PayPal，中国创作者收款资格需自行确认。

---

### 8. Podia —— 🟢 明确"几乎全允许"（措辞最宽松）

> "Podia's core values are: **For everyone, equally.**"
> "**In following with this value, our policy is to allow nearly all content on Podia, with a minimal set of restrictions we feel are necessary to keep our customers safe.**"

限制清单仅 9 项：Illegal / Stolen / Exploits children / Violence / Doxing / Fraud-phishing / Hate speech / Harassment / Pornography / Spam
→ **无 occult / spiritual / religion / fortune telling。**

> "Outside of these restricted areas, **we don't monitor or police any content on Podia** for three important reasons: Podia is not a shared marketplace; your Storefront will only ever show YOUR content; your customers will NEVER see content from other Podia creators."

🔗 https://www.podia.com/aup

---

### 9. Ko-fi —— ❓ 无法核实

`ko-fi.com`、`ko-fi.com/terms`、`ko-fi.com/guidelines`、`ko-fi.com/pricing`、`help.ko-fi.com/hc/en-us/*` **全部返回 HTTP 403**（Zendesk 反爬）。
**不做猜测。** 建议直接邮件 `support@ko-fi.com` 询问，或在注册前用测试账号走一遍 onboarding 流程实测。

---

## 三、高风险 / 特殊行业收单（high-risk merchant account）

### CCBill —— 🟢 AUP 中无玄学禁售 ⭐

AUP **§4.23 "will not process for sites advertising or selling the following"** 完整 16 条：
> 1. Buyer's clubs or membership clubs 2. Credit counseling or credit repair services 3. Direct marketing or non-Internet type subscription merchants 4. Infomercial merchants 5. Multi-level marketing 6. Outbound telemarketers 7. Prepaid phone cards/services 8. Rebate-based businesses 9. "Up-Sale" merchants 10. Free grants or grant giveaways 11. Cash/money-making opportunities 12. "Cash for opinions" 13. Grant/cash money making schemes 14. **Pharmaceutical** Informational Sites 15. Any website in violation of card association rules 16. Credit Protection/Identity Theft Protection

**关键词检索结果：occult ❌｜fortune telling ❌｜horoscope ❌｜astrology ❌｜divination ❌｜tarot ❌｜psychic ❌｜spiritual ❌｜metaphysics ❌｜religious ❌｜crypto ❌（全部零命中）**

唯一相关的是 §4.8 关于赌博的通用禁止。

🔗 https://ccbill.com/cs/client/policies/ccbill/acceptable_use.html

**CCBill 资质**：CCBill IE Ltd（爱尔兰央行 Payment Institution, ref C569018）、CCBill UK Ltd（FCA, ref 936980）、CCBill LLC（美国），ESB Bank NA 赞助；自称服务 30,000+ 商户。

⚠️ **准入门槛（重要）**：CCBill 属高风险收单，官网要求 "**APPLY NOW**" 提交表单，必填 **Estimated Monthly Sales（0–1,000,000 USD）**、Company、Website、Business Category。**不是注册即开通**，需人工 underwriting，且通常伴随：
- 更高的扣款费率与 rolling reserve（数月滚动准备金）
- 保证金（deposit）要求
- 严格的 chargeback 阈值
- **一般要求有公司主体**（非纯个人）

→ 对"中国个人开发者、零收入起步"而言，**现实门槛极高**。

---

### SegPay —— 🟡 无玄学条目，但申请分类表里没有对应项

申请表单 `Business Category` 可选项（完整）：
> Adult Content (subscription/VOD)｜Webcam/Live Streaming｜Fan Platform｜Adult Gaming/VRAI Adult/AI Companion｜Dating & Flirt (mainstream)｜Dating & Flirt (adult/adjacent)｜Adult Physical Goods｜CBD/Nutraceuticals｜**E-commerce (mainstream)**｜**SaaS / Digital Goods**｜Gaming (non-gambling)｜Escort Listings｜Gambling｜Other

→ **没有占卜/玄学选项。** 可行路径是选 **"SaaS / Digital Goods"** 或 **"E-commerce (mainstream)"**，由其 underwriting 判断。

**Country of Incorporation 下拉列表中 China 与 Hong Kong 均在选项内** ✅

公司资质：Segregated Payments Ltd（英国 FCA, ref 584599）、Segregated Payments (Ireland) Ltd、爱尔兰央行 C193896、Segpay Australia（AUSTRAC MSB 0429xxxx）；多家银行 ISO 身份（Woodforest、BMO Harris、Merrick、Worldline、Credorax、Rapyd、Humboldt）。

🔗 https://segpay.com/ ｜ 申请表 https://segpay.com/lead-form/

⚠️ SegPay 的公开客户案例**全部是成人/FeetFinder 类**，没有玄学案例。准入门槛与 CCBill 类似（人工审核、需预估月流水）。

---

### Verotel / NETbilling / PayLane / Worldpay high-risk / Durango / Instabill

**未取得可引用的原文政策页面。** 这些属于 sales-led（销售驱动）收单商，不公开 AUP/禁售清单，政策仅在签约合同与 underwriting 沟通中体现。
- **Worldpay high-risk**：走正式销售流程，准入门槛最高（通常要求公司、 audited financials、月流水阈值、3–6 个月 business track record）。
- **Verotel / NETbilling / PayLane / Durango / Instabill**：均要求预约销售，公开页面无品类清单。

**结论**：这一层**不适合"中国个人开发者"起步**，但**适合已有收入的成熟产品做第二通道**。

---

### 是否有专门服务 spiritual/astrology/metaphysics 的 MoR？

**未找到。** 没有专门服务该品类的 MoR。

最接近的**实操证据**是这个生态的真实做法——**它们根本不用 Stripe 类 MoR 收占卜的钱，而是走 App Store IAP**：

| 产品 | 支付通道（已核实） | 证据 |
|---|---|---|
| **Co-Star** | **100% Apple App Store IAP** | IAP 档位：`Pro-Star monthly $8.99`、`Eros $6.99`、`Advanced Chart - Relationships $8.99`、`Your Year Ahead $11.99`；App Store 分类 Lifestyle，206K 评分 |
| **The Pattern** | **100% Apple App Store IAP** | IAP 档位：`Go Deeper+ Monthly $14.99`、`Go Deeper+ Annual $83.99`、`Connect+ Quarterly $24.99`；页面无 Stripe/RevenueCat/Braintree 任何引用 |
| **Sanctuary** | 真人视频占卜 App（本质是**人** + IAP/订阅） | redirect 至 uk.sanctuary.com |
| **Astrology.com** | 独立站 + shop.astrology.com 电商；主页未披露收单方 | — |

🔗 [Co-Star App Store](https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561) ｜ [The Pattern App Store](https://apps.apple.com/us/app/the-pattern/id1071085727)

**这条证据的价值**：头部玩家全部选择 **Apple/Google 原生 IAP**。因为原生 IAP 收 Apple/Google 的 15–30% 抽成，但**平台不审核你的"命理准确性"**——只审核内容分级、隐私、支付合规。这对"AI 命理 App"是最稳的合规路径，代价是 30% 抽成 + 需实体 App。

---

## 四、核心问题明确回答

### Q1：「AI 命理/占卜/八字测算」定位，有哪些**对个人开放且允许该品类**的路径？

**直说：没有任何一家主流 MoR 提供"AI 命理"这个明确标签的干净通道。** 全部落在以下三种状态之一：

| 状态 | 服务商 | 说明 |
|---|---|---|
| 明确禁售 | Paddle、Creem | 出局 |
| 明确允许 | **Gumroad** | 最干净，但需自行确认中国收款 |
| 名单内无（需自行判断） | Stripe HK、PayPal、CCBill、Podia、Patreon | 靠"兜底条款"而非"品类清单"决定生死 |
| 限制但可申请 | **Dodo Payments** | 唯一有成文"Entertainment only; no claims or predictions"条款的 |

**可行的 3 条真实路径**（按推荐度）：

**路径 A：Dodo Payments（最推荐）**
- 理由：① 唯一明确接受中国身份证开户；② 唯一有成文的 "Spiritual & Astrology services – Entertainment only" 受理条款；③ 明确 "Individual" 账户类型（个人即可，无需公司）
- 执行要求：
  - 产品必须是**软件/应用**，不能是"AI 生成的薄 PDF"（Prohibited #3 明文）
  - 宣传必须 **entertainment / for reflection** 定位，**不得有 prediction/claim**（Restricted #4 明文）
  - 建议先邮件 `support@dodopayments.com` 描述产品预审

**路径 B：Gumroad（品类最匹配）**
- 理由：`chart-generation tools` + `pre-written reports` 被逐字点名允许
- 执行要求：产品承诺必须落在 "insight, reflection or entertainment"
- 风险：Gumroad 底层走 Stripe Connect + PayPal；中国个人开户与收款能力需自行确认

**路径 C：Apple / Google 原生 IAP（对标头部玩家的做法）**
- 理由：Co-Star / The Pattern 全部走这条路；平台不管命理准确性
- 代价：15–30% 抽成、需 App 审核、需 Apple/Google 开发者账号（中国开发者可注册，接入收款需指定银行/实体）
- 优势：**平台政策风险最低**

---

### Q2：如果**改定位**，哪些通道会打开？

这是本次调研**最高杠杆的发现**。Gumroad 的原文已经把"改定位"的判据写死了：

> "**The test is what the product promises, not what tradition it draws on.**"

| 定位 | 打开的通道 | 依据 |
|---|---|---|
| **"Entertainment / For reflection"** | **Dodo Payments**、**Gumroad** | Dodo Restricted #4 明文 "Entertainment only"；Gumroad "sold for insight, reflection or entertainment" |
| **"中国传统文化 / 自我反思工具"** | **Dodo**、**Gumroad**、**Podia**、**Stripe HK**、**PayPal** | 无任何一家以此为禁售项 |
| **"心理测评 / personality quiz"** | **Dodo**、**Gumroad**、**Podia**、**Stripe HK**、**PayPal** | 同上；注意**必须避免诊断/治疗话术** |
| **"Digital report generator / chart tool"** | **Gumroad**（明文允许）、**Dodo**、**Podia**、**Stripe HK** | Gumroad: "chart-generation tools and pre-written reports are all allowed" |
| **"Etsy 类数字商品"** | **Podia**、**Stripe HK**、**PayPal**、**CCBill** | 纯数字商品，无 prohibited 命中 |
| ❌ **"算命服务 / fortune telling"** | — | Paddle、Creem 明确禁售 |
| ❌ **"预测未来 / 灵性指导 / 真人咨询"** | — | Dodo Prohibited #15、Gumroad 禁 fortune tellers |
| ❌ **"健康/婚姻/财运指导"** | — | Gumroad: "readings framed as medical, legal or financial advice" 被明确纳入禁售 |
| ❌ **"App Store/Google Play 上的命理 App"** | **打开** | 头部玩家全在这么做 |

**具体的"改定位"操作（仅商业表述层面，不涉及规避）：**

1. **品类名**：从 "八字测算 / Fortune Telling" → **"Chinese Classical Divination Chart Generator"** 或 **"Zi Wei Dou Shu Chart Tool"**——把主语从「结果」变成「工具」
2. **结果措辞**：所有输出用 **"interpretation" / "reflection prompt" / "tradition's perspective"**，禁用 **"you will" / "prediction" / "guaranteed" / "预测" / "必然" / "注定"**
3. **免责声明页**：明确写 "for entertainment and personal reflection only, not professional advice"——这不只是合规姿态，它**同时满足** Dodo 和 Gumroad 的判据
4. **避免真人通道**：Dodo Prohibited #15 与 Gumroad 都针对 "access to a [practitioner/spiritual] authority who will tell the buyer what to do"。纯自动化产品天然规避
5. **不要把结果表述为 PDF 薄报告卖 $29**：触发 Dodo Prohibited #3 "AI-generated PDFs with little value"
6. **避免占星圈的成熟词**：Co-Star 用户评论里已出现 "Very expensive... I can get much more in depth readings from other AI service like grok"——这说明**用户会拿你的产品和通用 LLM 对比**，退款率与投诉率是真正的封号原因

---

### Q3：真实案例的支付通道

已在第三节列出，核心结论：

- **Co-Star**（$8.99/月）→ **Apple App Store IAP**
- **The Pattern**（$14.99/月，$83.99/年）→ **Apple App Store IAP**
- **Sanctuary** → 真人视频占卜 App，**App 内 IAP/订阅**
- **Astrology.com** → 独立站 + 电商；收单方未公开披露
- **Patreon 上的塔罗/占星创作者** → Patreon（Plexi/Stripe/PayPal），**政策允许，无玄学禁令**

**规律：越接近"真人在给建议"，越走 App Store；越接近"工具/内容"，越能走 Stripe 系 MoR。** 这与所有政策文本的逻辑完全一致。

---

## 五、收款路径排序（针对中国个人开发者，允许占卜品类）

| # | 路径 | 品类许可 | 中国个人 | 费率/成本 | 综合推荐 | 关键风险 |
|---|---|---|---|---|---|---|
| **1** | **Apple / Google Play IAP** | ✅ 平台不审命理 | ✅ 可注册 | 15–30%（前一年小型企业计划 15%） | ⭐⭐⭐⭐⭐ | 需 App 审核、30% 抽成、$99/年 |
| **2** | **Dodo Payments** | ✅ Restricted "Entertainment only" 成文 | ✅ **明确支持 China + HK** | MoR 综合费率（低于 Paddle） | ⭐⭐⭐⭐ | 需通过 underwriting；禁"AI 薄 PDF"、禁 claims |
| **3** | **Gumroad** | ✅ **逐字点名允许** chart tools / reports | ⚠️ 待确认 | ~5% + $0.50（+$0.5 PayPal） | ⭐⭐⭐⭐ | 中国个人开户/收款待确认；底层受 Stripe/PayPal 约束 |
| **4** | **Patreon** | ✅ 无玄学禁令 | ⚠️ 需确认 | 平台抽 10%（新平台 5%）+ 支付费 | ⭐⭐⭐ | 订阅制模型，不适合一次性报告；Plexi 覆盖可能不含中国 |
| **5** | **PayPal** | ✅ 名单内无 | ⚠️ 中国个人跨境收款受限 | 4.4% + $0.08 | ⭐⭐⭐ | "high likelihood of being fraudulent" 兜底条款是主要封号依据 |
| **6** | **Podia** | ✅ "allow nearly all content" | ⚠️ 需确认 | 0% 平台费（收 Stripe 费） | ⭐⭐⭐ | 需自备 Stripe 账户 → 又回到 #6 的问题 |
| **7** | **CCBill / SegPay** | ✅ 政策无禁售 | ⚠️ 需公司 + 流水 | 高费率 + rolling reserve + 押金 | ⭐⭐ | **需已有收入**；个人起步不现实；checkout 品牌认知度低 |
| **—** | **Stripe HK** | ✅ 名单内无 | ❌ 需香港实体/身份 | 2.9% + $0.30 (HK) | ⭐⭐ | 需香港公司 + 董事身份证 + 银行账户 |
| **—** | **Lemon Squeezy** | ✅ 名单内无 | ❌ 走 Stripe Connect | 5% + $0.50 | ⭐ | 同上 |
| **❌** | **Paddle** | 🔴 明确禁售 | ✅ | — | 排除 | — |
| **❌** | **Creem** | 🔴 明确禁售 | ✅ | — | 排除 | — |

---

## 六、最诚实的结论

**没有"干净"的通道。** 但也没有死路——真正的规律是：

### 三条不可违反的红线（跨所有服务商一致）

1. **不承诺结果** —— 所有渠道一致。Gumroad 原文："The test is what the product promises"
2. **不冒充专业替代** —— "readings framed as medical, legal or financial advice" 被 Gumroad 明确纳入禁售
3. **不做真人灵性权威** —— Dodo Prohibited #15、Gumroad 禁 fortune teller，都指向"付费获得真人指引"

### 唯一的结构性难点（必须直说）

**你所在的位置（中国大陆个人）恰好卡在三个最干净通道的门槛上：**
- **Stripe**：不支持中国大陆（只支持香港）
- **Paddle / Creem**：支持中国，但**都精准禁售 fortune-telling**
- **PayPal**：政策干净，但中国大陆个人账户跨境收款能力本身受限

**这意味着你必须在两件事中选一件：**
- **(A) 改用 Apple/Google 原生 IAP** —— 政策最安全（对标 Co-Star / The Pattern），代价是 30% 抽成 + 需做 App + 需开发者账号收款资质
- **(B) 走 Dodo Payments** —— 唯一"中国个人 + 玄学品类 + 成文可申请条款"三者同时满足的通道，但要接受 underwriting 风险，且产品形态必须真的是软件

### 主体结构层面的建议（不含任何违法建议）

- **香港公司 + Stripe/LS** 是长期最优解：政策干净、费率低（2.9%）、品类不受限。但需要真实的香港业务实质（地址、银行账户、董事），不是壳。
- **个人起步期用 Dodo（Individual 账户）**，验证产品市场匹配后再考虑注册实体。
- **如果做 App，优先 IAP**：不要为了省 15% 而用 Stripe 冒险——头部玩家全走 IAP 不是巧合。
- **无论走哪条，都要先发邮件预审**：Dodo `support@dodopayments.com`、Lemon Squeezy / Creem 都在政策页明确写了 "contact support before you start selling"。用一页产品说明 + 定价页截图去问，成本 30 分钟，能省掉 3 个月。

---

## 附：未能取证的项目（诚实披露）

| 项目 | 状态 | 原因 |
|---|---|---|
| **Ko-fi 内容政策** | ❌ 未核实 | ko-fi.com 全站 + help center 持续返回 HTTP 403 |
| **Shopify Payments / Shop Pay 品类限制** | ❌ 未核实 | 目标 URL 均返回通用帮助页，无 restricted-businesses 列表（推测 Shopify 对大部分品类**回退到第三方网关**，需要具体路径再查） |
| **Lemon Squeezy → Stripe Managed Payments 后的政策变更** | ⚠️ 部分 | LS 文档仍为旧品牌，禁售清单未见玄学条目，但 rebranding 后的新政策未单独核实 |
| **Verotel / NETbilling / PayLane / Worldpay HR / Durango / Instabill** | ❌ 未核实 | 均为 sales-led，无公开 AUP 页面 |
| **高风险收单的实际门槛数字**（最低月流水、费率、reserve %） | ❌ 未取证 | 这些是 sales-led 信息，只在合同与销售沟通中披露，公开页面无数据。需预约销售才能获得。 |
| **Patreon / Podia / Gumroad 对中国个人的实际开户与收款** | ⚠️ 待验证 | 政策允许 ≠ 账户可开。需实际注册测试。 |
| **专门服务 spiritual/astrology 的 MoR** | ❌ 未发现 | 两轮搜索（DDG HTML / Google）均被反爬拦截；基于已覆盖的 ~15 家服务商判断，**该细分市场不存在** |

**建议下一步**：用同一份产品说明，向 Dodo、Gumroad、PayPal、Patreon、Podia 五家分别发一封预审邮件（英文），问同一个问题——"Do you accept a digital product that generates Chinese metaphysics charts (八字/紫微斗数) for personal reflection and entertainment?" 五封回复能在一周内给你一个比任何二手调研都可靠的答案。

---

## 附录 5：研究 Dodo 准入与目标市场支付

研究完成。以下是核对结果。

---

# Dodo Payments 买家侧可行性核对报告

**核对时间**：2026-10-02 · **信息源**：`docs.dodopayments.com` 全量文档索引（159 页）+ Stripe / Paddle / Gumroad / Patreon / YooKassa 官方政策原文

---

## 0. 三个最重要的发现（先看这个）

| # | 发现 | 影响 |
|---|---|---|
| 🔴 **1** | **你的品类在 Dodo 是「需人工尽调审查」，不是「自动放行」**——但同时「宗教/灵性服务」和「AI 生成的浅薄 PDF」是**明文禁止**的 | 决定产品形态：必须**纯软件化交付**，且必须有可证明的「娱乐/自我反思」属性 |
| 🔴 **2** | **俄罗斯买家在 Dodo 完全不可用**——226 国买家白名单里没有 RU/BY/IR/KP/CU/SY/VE/ZW | Q2 答案是「死路」，且有原文 |
| 🟢 **3** | **Dodo 买家白名单明确包含 JP/KR/PH/SG**，且**没有任何 jurisdiction-specific 品类限制表**（不同于 Stripe） | 日韩菲新在 Dodo 上「无公开禁令」，但需书面预审 |

**另有一个你没问但必须先知道的事**：Stripe 在日本禁 `Psychic services and fortune tellers` 是**真实存在的**（已核实原文），而 **Dodo 没有**。但 Dodo 的"灵性占星"审查条款 + 日本市场，正是当初触发 Stripe 日本禁令的同一批发卡/收单方风险。**别把"Dodo 没写禁令"理解成"Dodo 不会在飞行中把你踢掉"**。

---

## 问题 1：Dodo 的买家国家 / 受限辖制限制

### 1.1 买家国白名单（226 国，官方原文表格）

来源：[Countries Eligible for Payment Acceptance](https://docs.dodopayments.com/miscellaneous/list-of-countries-we-accept-payments-from)

> **Tip 原文**：
> "You can only accept payments from the 226 countries listed above. We regularly update this list as we expand support to more countries."

| 你关心的买家国 | ISO | 在白名单？ | 表格位置 |
|---|---|---|---|
| 🇷🇺 俄罗斯 | RU | ❌ **不在** | — |
| 🇧🇾 白俄罗斯 | BY | ❌ **不在** | — |
| 🇮🇷 伊朗 | IR | ❌ **不在** | — |
| 🇰🇵 朝鲜 | KP | ❌ **不在** | — |
| 🇨🇺 古巴 | CU | ❌ **不在** | — |
| 🇸🇾 叙利亚 | SY | ❌ **不在** | — |
| 🇻🇪 委内瑞拉 | VE | ❌ **不在** | — |
| 🇿🇼 津巴布韦 | ZW | ❌ **不在** | — |
| 🇯🇵 **日本** | JP | ✅ **在** | #106 |
| 🇰🇷 **韩国** | KR | ✅ **在** | #113 |
| 🇵🇭 **菲律宾** | PH | ✅ **在** | #164 |
| 🇸🇬 **新加坡** | SG | ✅ **在** | #182 |
| 🇨🇳 中国大陆 | CN | ✅ 在 | #43 |
| 🇹🇼 台湾 | TW | ✅ 在 | #209 |
| 🇭🇰 香港 | HK | ✅ 在 | #89 |
| 🇲🇴 澳门 | MO | ✅ 在 | #146 |
| 🇮🇶 伊拉克 | IQ | ✅ 在（**注意：Paddle 禁伊拉克**） | #100 |

**结论**：Dodo 的买家侧限制**只有一个维度——国家/地区白名单**。没有基于买家 IP、卡 BIN 的额外辖区封锁说明。

### 1.2 Dodo 有没有 jurisdiction-specific 品类限制？

**没有找到。** 我核查了 [完整英文文档索引（159 页）](https://docs.dodopayments.com/_llms/en/docs.md) 的全部页面清单：

- Dodo **没有** 类似 Stripe 的 "Jurisdiction-specific prohibited businesses" 表格页
- Dodo **没有** 任何 Japan-specific / Korea-specific / Philippines-specific 的政策页
- Dodo 唯一与"命理"相关的条款是**全球统一**的（见第 5 节）

⚠️ **诚实标注**：这不等于"日本没有风险"。Dodo 未公开 ≠ Dodo 不会事后执行。审查权在合规团队手上。

### 1.3 Dodo 支持的支付方式（40+ 种，官方表）

来源：[Payment Methods](https://docs.dodopayments.com/features/payment-methods)

| 你问的方式 | Dodo 支持？ | 原文依据 |
|---|---|---|
| **日本 Konbini（コンビニ）** | ❌ **不支持** | 全表无此行 |
| **PayPay / Rakuten Pay** | ❌ 不支持 | 全表无此行 |
| **韩国 KakaoPay** | ✅ 支持 | `Kakao Pay \| South Korea \| KRW \| Yes \| ~$1.00` |
| **韩国 NaverPay** | ✅ 支持 | `Naver Pay \| South Korea \| KRW \| Yes` |
| **韩国 PAYCO** | ✅ 支持（仅一次性） | `PAYCO \| South Korea \| KRW \| No` |
| **韩国本地卡** | ✅ 支持 | 「Korean Local Cards \| Card \| Yes \| 50 KRW」 |
| **菲律宾 GCash** | ✅ 支持（**仅一次性**） | `GCash \| Philippines \| PHP \| No \| 50.00 PHP` |
| **菲律宾 Maya** | ❌ 不支持 | 全表无此行 |
| **东南亚 GrabPay** | ❌ 不支持 | 全表无此行 |
| **新加坡 PayNow** | ❌ 不支持 | 全表无此行 |
| **香港 FPS / AlipayHK** | ✅ 支持（仅一次性） | Asia-Pacific 页 |
| **微信支付** | ✅ 支持（仅一次性） | `WeChat Pay \| Global \| USD, CNY \| No` |
| **PayPal** | ⚠️ **已暂停** | 「PayPal is temporarily unavailable for new transactions.」+ FAQ Q83「PayPal is currently paused. We don't have an ETA」 |

**两处对日本特别重要的话：**

Dodo 韩国页原文（[South Korea Payment Methods](https://docs.dodopayments.com/features/payment-methods/south-korea)）：
> "Many Korean cards run on domestic networks. Supporting Korean local cards avoids declines on cards that international card networks can't process."

Dodo 亚太页原文（[Asia-Pacific](https://docs.dodopayments.com/features/payment-methods/asia-pacific)）：
> "Credit card use is low in the Philippines compared with card-first markets. Local wallets and bank transfers reach customers that a card-only checkout misses."

### 1.4 Dodo 支持的货币 / 结算

| 项目 | 原文 | 来源 |
|---|---|---|
| 原生结算币种 | "Dodo Payments natively supports three payout currencies: **USD, GBP, and EUR**." | FAQ Q84 |
| Adaptive Currency | "Display prices in each customer's local currency... **80+ local currencies**" | [Adaptive Currency](https://docs.dodopayments.com/features/adaptive-currency) |
| 定价工具 | PPP、Localized Pricing、Charm Pricing | FAQ Q93/Q94 |
| Payoneer 收款 | "Yes, you can receive payouts via Payoneer" | FAQ Q102 |

⚠️ **未核实**：JPY / KRW / PHP / SGD 在 Adaptive Currency 里的确切支持与换汇加价比例，我未逐项验证（FAQ Q76 只给了 4%/3%/2% 的换汇费阶梯和「Krw 零小数」提示）。

### 1.5 买家侧限制的诚实小结

| 限制维度 | Dodo 是否有 | 说明 |
|---|---|---|
| 买家国家白名单 | ✅ 有 | 226 国，制裁国已排除 |
| 买家国专属品类禁令 | ❌ 无公开页面 | 与 Stripe 相反 |
| 买家年龄验证 / 18+ | ⚠️ **未找到任何相关文档** | Dodo 文档中无年龄门槛机制说明 |
| 买家所在国税务 | ✅ MoR 代缴 | Dodo 作为法律卖方申报 |

---

## 问题 2：俄罗斯市场——到底能不能收俄罗斯人的钱？

### 2.1 各家 MoR / 平台对俄罗斯的原文态度

| 平台 | 俄罗斯买家能否付款 | 原文 |
|---|---|---|
| **Dodo Payments** | ❌ **不能** | 226 国白名单无 RU（[原文页](https://docs.dodopayments.com/miscellaneous/list-of-countries-we-accept-payments-from)） |
| **Paddle** | ❌ **不能（明文封杀）** | 见下方原文 |
| **Gumroad** | ⚠️ 未找到国家级禁令 | [prohibited 页](https://gumroad.com/prohibited) 全文**无任何国家限制清单**；但实际能否收款取决于底层卡通道 |
| **Patreon** | ⚠️ **俄罗斯整体未被列**，但部分地区被列 | 见下方原文 |
| **Stripe** | ❌ 不支持俄罗斯商户 | [stripe.com/global](https://stripe.com/global) 支持国列表**无俄罗斯**；⚠️ 未找到 Stripe 关于"俄罗斯发行卡能否跨境线上支付"的专门原文 |
| **PayPal** | ⚠️ **本次未能取得原文** | 见第 6 节 |

**Paddle 原文（最明确）** —— [Impact of sanctions on Russia and Belarus](https://www.paddle.com/help/legal/sanctions/impact-of-sanctions-on-russia-and-belarus)：
> "**Can my customers in Russia still make purchases via Paddle?**
> No, we do not allow transactions from Russia on Paddle anymore.
>
> **Can my customers in Belarus still make purchases via Paddle?**
> No, we do not allow transactions from Belarus on Paddle anymore.
>
> **Can my customers in Ukraine still make purchases via Paddle?**
> Partially. Buyers based in the regions of Crimea, Donetsk, Kherson, Luhansk, and Zaporizhzhia are currently under sanction and therefore will be unable to complete transactions via Paddle. ...
>
> **Will my existing subscriptions in affected countries still renew?**
> All buyers' subscriptions in Russia/Belarus have been canceled as of April 2023."

[Which countries are supported by Paddle?](https://www.paddle.com/help/legal/sanctions/which-countries-are-supported-by-paddle) 原文：
> "Paddle works with software businesses anywhere in the world with the exception of the unsupported countries listed below.
> In accordance with international sanctions regulations, as well as the policies of our banking and payments partners... Paddle is unable to support suppliers operating from the below countries. **Paddle will also block purchases and downloads to buyers located within specific unsupported regions/countries.**"
>
> 不支持国含：`Belarus / Burma (Myanmar) / Cuba / Iran / Iraq / Libya / Nicaragua / North Korea / Russia / Somalia / South Sudan / Sudan / Syria / Venezuela / Yemen / Zimbabwe / Afghanistan / Central African Republic / Democratic Republic of Congo / Haiti / Mali` + `Crimea / Donetsk / Kherson / Luhansk / Zaporizhzhia`

**Patreon 原文** —— [Terms of Use](https://www.patreon.com/policy/legal)（Last Updated: May 27, 2026）：
> "In order to be eligible to use Patreon, you must not be located, organized, or ordinarily resident in a country or territory subject to comprehensive U.S. sanctions or embargoes (**currently, Cuba, Iran, North Korea, and the Crimea, so-called Donetsk People's Republic, and so-called Luhansk People's Republic regions of Ukraine**) and you must not be designated on the Specially Designated Nationals and Blocked Persons List..."
>
> 注意：**"Russia" 整体未被列入** Patreon 这份清单。

### 2.2 有没有面向中国个人、能把俄罗斯卢布收进来的通道？

**YooKassa / YooMoney 是唯一查到的"外国主体可接"的答案** —— [Payment acceptance for non-residents](https://yookassa.ru/en/non-russian-residents/)：

> "**If your company is registered outside Russia, you can still accept payments via YooMoney.** The rates are the same as for Russian companies"
>
> 入驻流程（原文）：
> "1. Sign up for YooMoney and fill out the form
> 2. Complete the identification process
> 3. **Enter into a contract. Send the paper version to us by mail, along with certified copies of identification documents**
> 4. Set up payment acceptance."
>
> 结算（原文）：
> "**Does a foreign company need a Russian bank account?** We can make settlements with a foreign legal entity to an account in a foreign bank and an account in a Russian one. *The exception is payment acceptance from legal entities. For that, you must have an account in any Russian bank.*"
>
> 额度（原文）："**Are there limits on turnover for non-residents?** There are no limits on turnover in YooMoney"
>
> 支持币种（原文）："we can work with **Russian and Belarusian rubles, yuan, drams, som, and somoni**"
>
> 换汇成本（原文）：
> - "Prices in rubles — settlements in currency: ... convert them into the selected currency at the exchange rate of **the Bank of Russia + 2%**"
> - "Prices in currency — settlements in currency: We convert the price in currency into rubles at the exchange rate of **the Bank of Russia + 5%**"
>
> 非居民不可用的服务（原文）："Payouts: these can only be made to YooMoney wallets and mobile balance; **Payment acceptance via FPS is not available**; settlement and cash services are not available"

⚠️ **必须诚实标注的三个限制**：
1. **YooKassa 页面反复说的是 "company"（公司）**。"中国个人（自然人）"能否以个人身份签约，**该页面没有说明，我未能核实**。
2. **YooMoney 是收单机构（acquirer），不是 MoR**。税务、退款、拒付、消费者保护**全部落在你身上**，与 Dodo 的风险模型完全不同。
3. **纸质合同 + 认证副本邮寄**——不是线上自助注册。

⚠️ **另需自行核实**：中国个人年度 5 万美元便利化购汇额度、外汇管理规定，以及人民币/卢布跨境结算的税务申报义务。**本次未核实任何官方原文，请务必自行向银行/外汇局/税务确认。**

### 2.3 Q2 结论

> **俄罗斯市场对「中国个人 + 海外 MoR」基本是死路。**
>
> 唯一有官方明文支持外国主体接入的通道是 **YooKassa/YooMoney**，但它：(a) 主要面向外国**公司**；(b) 需要纸质合同与身份认证；(c) 不是 MoR；(d) 存在 2%–5% 汇兑损耗 + 外汇额度约束；(d) 叠加"占卜类内容"在多数平台的品类风险。**投入产出比极低，不建议作为首发市场。**

---

## 问题 3：泛亚洲市场支付现实

### 3.1 日本 🇯🇵

**支付习惯（Stripe 日本官方页原文）** —— [stripe.com/jp/payments/payment-methods](https://stripe.com/jp/payments/payment-methods)：
> "EC 決済の約 **70% がクレジットカード**で行われています。一方で、**コンビニ決済**や**銀行振込**など、日本独自の決済手段も依然として人気があります。"
>
> 广泛使用的支付方式：Visa / Mastercard / JCB / American Express / **コンビニ決済** / 銀行振込 / **PayPay**

**⚠️ 核心矛盾**：日本用户 70% 用卡（Dodo 覆盖了），但**占卜/占い 行业客单偏低、且相当一部分用户偏好便利店现金支付**。**Dodo 不支持 Konbini，也不支持 PayPay。** 你会系统性丢失偏好非卡支付的那部分用户。

**Stripe 日本禁令（已核实原文）** —— [Prohibited and Restricted Businesses](https://stripe.com/legal/restricted-businesses)（Last updated: 2026-09-22）：

该页设有 **"Jurisdiction-specific prohibited businesses"** 章节，其中 `Psychic services and fortune tellers` 出现在 **Japan / Mexico / Thailand** 三个辖区的条目中。日本区块完整原文（节选）：

> **Japan**
> - Advisory services related to drop shipping and the resale of goods
> - Animals
> - C2C services outside of Stripe Connect
> - Consultation and advisory or **prediction services relating to online gaming or gambling**
> - Consultation or advisory services providing guidance, information or tools on how to profit through trading or investments...
> - Donations to individuals
> - Fundraising for or financing of businesses that are listed above as prohibited or restricted
> - Genital and nipple jewelry
> - Genital prosthetics
> - Health instruments
> - Industrial waste disposal and garbage disposal devices and water purifiers
> - International marriage brokerage businesses
> - Mortgage consulting
> - Private investigators or protection services
> - **Psychic services and fortune tellers**
> - Sex accessories and lifelike sex toys
> - **Businesses without a "Commercial Disclosure" page on their website as required by the Specified Commercial Transactions Act (SCT)**—for more information, see how to create and display a "Commerce Disclosure" page

> ⚠️ **关于「Japan 区块属于哪个章节」的重要限定**：该区块出现在 "Jurisdiction-specific **prohibited** businesses" 标题之下。Stripe 页面对 "Restricted Businesses" 的定义原文是：
> "Businesses in these categories require **additional due diligence** by Stripe... if your business falls into one of the categories below, Stripe might not be able to grant approval... If we do provide approval, note that the approval is **specific to each service offer, and it may be modified or revoked by Stripe at any time**."
>
> 也就是说：**即便获批也是"每个服务单独批 + 可随时撤销"**。这是比"直接拒绝"更难受的状态。

**外国主体在日本收款的额外难点**：
- **特商法（特定商取引法 / SCT Act）**：Stripe 明确把"缺 Commercial Disclosure 页面"列为日本辖区禁止项。**你以中国个人身份卖日本语占卜产品，几乎必然落入特商法的消费者保护范围**（ 网站经营者表示、退款条款、表示広告の景品規制）。⚠️ 特商法具体条款适用本次未核实原文，但 Stripe 的这条日本专属禁令已证明发卡/收单方在盯这个。
- 结论：**日本市场不是"能直接做"，而是"能做但每一步都要专业日本合规兜底"。**

### 3.2 韩国 🇰🇷

**支付现实：这是泛亚洲里对 Dodo 最友好的市场。**

Dodo 韩国页原文（[South Korea Payment Methods](https://docs.dodopayments.com/features/payment-methods/south-korea)）：
> "Digital wallets such as Kakao Pay and Naver Pay made up **35% of South Korean e-commerce spending in 2025**, second only to credit cards, according to the **Worldpay Global Payments Report 2026**."

| 方式 | 订阅支持 | 最低金额 |
|---|---|---|
| Kakao Pay | ✅ 一次性 + 订阅 | ~$1.00 |
| Naver Pay | ✅ 一次性 + 订阅 | ~$1.00 |
| PAYCO | ❌ 仅一次性 | ~$1.00 |
| Korean Local Cards | ✅ | 50 KRW |

Dodo 甚至专门处理了韩国本地卡问题：
> "**Korean card declined on the international network** — *Cause:* Some Korean cards run on domestic networks that international card networks can't process. *Solution:* Keep `credit` and `debit` enabled so customers can pay with Korean local cards."

韩国三大钱包 + 本地卡 + 订阅，全部具备。这在所有受查 MoR 里是**独有的**。

**⚠️ 韩国占卜类服务的法律限制 —— 我未能核实，这是本次最大的取证缺口**

我尝试了英文/韩文维基、Saju 词条、Fortune telling 词条，**均未取得韩国法律的官方原文**。请注意我**不能**基于"常识"给你下结论。

需要你自行核实的具体问题：
1. **线上/离线的占卜（점술）经营是否需要登记/ 신고**，依据哪部法律
2. **无照经营的刑事风险**（历史上有过"요술"相关判例，但本次未核实其现行状态）
3. **面向未成年人的广告/销售限制**（韩国有针对占卜广告的行政指导传统，但本次未核实现行文本）
4. **税务**：向韩国个人消费者售数字产品，Dodo 作为 MoR 代缴的 VAT/GST 处理是否与你理解一致

**一个有意义的正面信号**：我核查的 Stripe 辖区禁令列表中，**没有 Korea 区块**。`Psychic services and fortune tellers` 只出现在 Japan / Mexico / Thailand。这说明韩国至少在**支付方政策**层面未见同类禁令。

### 3.3 菲律宾 🇵🇭

| 维度 | 结论 |
|---|---|
| Dodo 支持 | ✅ PH 在白名单（#164） |
| 本地方式 | ✅ GCash（PHP，最低 50 PHP）—— **但仅一次性付款** |
| 缺失 | ❌ **Maya**（菲律宾第二大钱包）不支持 |
| 风险 | Dodo 自己说：菲律宾信用卡渗透率低 → **只做卡会严重掉转化**；GCash 不可用于订阅 |
| 语言 | 英语，无翻译成本 |

**注意**：如果你做订阅制，菲律宾市场会因为 GCash 不可订阅而**只能靠卡**——这与该市场特性冲突。建议菲律宾只卖一次性产品（报告/命盘生成）。

### 3.4 新加坡 🇸🇬

| 维度 | 结论 |
|---|---|
| Dodo 支持 | ✅ SG 在白名单（#182） |
| 本地方式 | ❌ **PayNow 不支持、GrabPay 不支持** |
| 可用 | 卡、Apple Pay、Google Pay（Adaptive Currency 计价） |
| 语言 | 英语，无翻译成本 |
| 规模 | ⚠️ 新加坡付费市场规模有限（人口 600 万），**适合作为"卡支付无摩擦"的顺带市场，不是主战场** |

⚠️ 未核实：SGD 在 Adaptive Currency 中的确切表现；GrabPay 缺失对新加坡用户的实际影响程度。

### 3.5 是否必须注册当地/香港/美国实体？

| 场景 | 是否必须 |
|---|---|
| **Dodo + 无实体个人** | ✅ **不需要**。FAQ Q6 原文：「**Yes, we support unregistered businesses as well. You do not need a registered business to use Dodo Payments.** You can onboard as an individual and start receiving international payments」 |
| **日本本地化收款** | ⚠️ 走 Dodo 不需要；但**日本语市场 + 命理品类**建议先拿 Dodo 书面预审 |
| **韩国本地化收款** | ✅ 不需要（KR 本地卡 + 三大钱包已由 Dodo 覆盖） |
| **俄罗斯** | ❌ 实质需要俄罗斯主体或俄罗斯银行账户 |
| **需要美国实体的情况** | Stripe 需本地实体（stripe.com/global 无中国大陆）；Stripe Atlas 可注册但需成本。**用 Dodo 可完全绕开** |

---

## 第 5 节（额外发现）：你的品类在 Dodo 的真实处境 ⚠️

这一节不在你的问题清单里，但**比支付方式更决定成败**。请务必读完。

### 5.1 Dodo 政策原文（逐字）

来源：[Merchant Acceptance Policy](https://docs.dodopayments.com/miscellaneous/merchant-acceptance)

**禁止清单第 15 条（Businesses We Can't Support）：**
> "**Religious or spiritual product or services** – This includes offerings of spiritual guidance, paid prayers, rituals, faith-based counselling, or similar services where users are paying for religious or spiritual interaction or **access to a religious or spiritual authority**."

**禁止清单第 2 条：**
> "**Manual Digital Services** – Selling non-automated services via digital platforms. So, selling custom design, development, **coaching**, freelancing or consulting services via digital platforms isn't allowed. In essence, if the majority of the value sits in the human labour rather than digital systems, it will not be accepted."

**禁止清单第 3 条：**
> "**Digital products with limited or unclear value** – For example, **AI-generated PDFs with little value**, thin templates marked up heavily, or clearly unfinished websites sold at premium prices..."

**禁止清单第 13 条：**
> "**Miracle, Misleading, or Unverifiable Claims** – No products making exaggerated or unverifiable claims – e.g., 'cures cancer,' 'reverses aging,' 'burns fat while you sleep,' 'make money while you sleep.'"

**需人工审查清单第 4 条（Categories That Often Require Review）：**
> "**Spiritual & Astrology services** – **Entertainment only; no claims or predictions**"

**需人工审查清单第 7 条：**
> "**Productised services** – A fixed, pre-defined digital product that is delivered the same way for every buyer. This may include limited, repeatable human operational work, as long as it is not customized or consultative."

政策总则原文：
> "Some business types may fall into a restricted zone - **not outright prohibited, but not immediately approved either**. These cases will require **enhanced due diligence**, and we'll take a closer look before making a final decision. **This is done on a case to case basis.**"

**违规处罚原文（节选）：**
> "Permanent account suspension / Immediate halt of transactions and platform access / Withholding of payouts or reversal of settled funds / Refunding all transactions processed / **Fines or penalties in proportion to losses, reputational harm, or downstream risk (up to USD 425,000)**"

### 5.2 五家平台对「命理/占星/占卜」的政策对比（这是选型的真正依据）

| 平台 | 命理类政策原文 | 结论 |
|---|---|---|
| **Dodo** | "Spiritual & Astrology services – **Entertainment only; no claims or predictions**"（需审查） | ⚠️ **可做，但需预审**。纯软件交付可过；真人解读被禁 |
| **Paddle** | AUP **Prohibited Categories #14**："**Digital services associated with pseudo-science, including but not limited to clairvoyance, horoscopes, fortune-telling**" | 🔴 **全球封杀，直接出局** |
| **Gumroad** | 禁 #29 "fortune tellers"，**但有明文豁免**：<br>"It does **not** cover astrology, tarot, numerology, birth-chart and divination material sold for **insight, reflection or entertainment**. That work has its own Discover category, and **courses, decks, guidebooks, chart-generation tools and pre-written reports are all allowed**. A one-off personalized reading is also allowed when it is sold as reflection or entertainment and makes no concrete promise about what will happen..."<br>"**The test is what the product promises, not what tradition it draws on.**" | 🟢 **政策最友好，最贴合你的产品** |
| **Stripe** | Japan / Mexico / Thailand：**"Psychic services and fortune tellers"**（辖区禁止） | 🔴 日本出局；其他辖区可但受 Stripe 审查 |
| **Patreon** | ⚠️ 未在 Terms 中找到占卜相关禁令（本次未逐条核对 Community Guidelines） | 🟡 待核实 |

### 5.3 由政策推导出的产品形态硬约束

| 必须做 | 绝对不能做 |
|---|---|
| ✅ 纯软件/算法自动生成（八字排盘、紫微排盘） | ❌ 真人一对一解读、按小时咨询（撞 #2 Manual Digital Services + #15 spiritual authority） |
| ✅ 固定形态、每位买家拿到**同样**的交付物（撞 #7 Productised services 才安全） | ❌ 定制化咨询式交付 |
| ✅ 强"娱乐/自我反思"免责，**不承诺预测结果** | ❌ 任何"保证/准确率 XX%/改变命运"话术（撞 #13） |
| ✅ 有实质功能价值（交互式排盘、解读库、学习功能） | ❌ 单纯"AI 生成的浅薄 PDF"（#3 **原文明文举例**） |
| ✅ 完整网站：定价、ToS、Privacy、**Refund Policy**、联系方式（FAQ Q40 原文要求） | ❌ 交付物与"展示的产品"不一致——**尤其注意**，若用 Discord / Telegram / Notion / GitHub 交付，政策原文警告：<br>"A community, file bundle, repository, or template that delivers material misaligned with the disclosed product... is treated as a policy breach **regardless of how the storefront is positioned**." |
| ✅ 网站有"Commercial Disclosure"（若做日本） | ❌ 假借 "gray market setup" / 虚假实体（#9 明文禁止，罚款上限 $425,000） |

---

## 问题 4：买家市场可行性排序与行动建议

### 4.1 综合可行性排序

| 排名 | 市场 | 支付可行性 | 合规/品类可行性 | 本地方式覆盖 | **总评** |
|---:|---|---|---|---|---|
| **1** | **英语 / 欧美** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐（需 Dodo 预审） | ⭐⭐⭐⭐⭐ | 🟢 **首发** |
| **2** | **韩国** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐（Stripe 无 KR 禁令，但韩国本地法律待核实） | ⭐⭐⭐⭐⭐ | 🟢 **可首发**（三大钱包 + 本地卡 + 订阅全覆盖） |
| **3** | **菲律宾** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐（仅 GCash，且不支持订阅） | 🟡 **可做，但只卖一次性产品** |
| **4** | **新加坡** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐（无 PayNow/GrabPay） | 🟡 **顺带做**，规模有限 |
| **5** | **日本** | ⭐⭐ | ⭐⭐（同批卡/收单方风险，Stripe 有明文禁令） | ⭐⭐（**无 Konbini/PayPay**） | 🟠 **先别碰**，需预审 + 日语合规 |
| **6** | **俄罗斯** | ❌ | ❌ | ❌ | 🔴 **现在别碰** |

### 4.2 现在就别碰

| 市场 | 原因 |
|---|---|
| 🔴 **俄罗斯** | Dodo 白名单无 RU；Paddle 明文封杀；YooKassa 只面向外国**公司**且非 MoR |
| 🔴 **Paddle 作为备选 MoR** | AUP Prohibited #14 全球禁止 horoscopes / fortune-telling，与支付能力无关，直接出局 |
| 🟠 **日语真人解读服务** | 撞 Dodo #2 + #15；且 Japan 辖区在 Stripe 是明文禁令，说明底层风险真实存在 |

### 4.3 可以首发

**建议首发组合：英语（欧美）+ 韩国，双语（English / 한국어）**

理由：
1. 两个市场都**无公开品类禁令**（Dodo 侧）
2. 韩国是 Dodo **唯一同时具备三大本地钱包 + 本地卡 + 订阅能力**的泛亚洲市场
3. 英语市场 Dodo 支付方式最完整
4. 两者**都不需要任何实体注册**（FAQ Q6 明确支持个人）
5. 规避了日本无 Konbini 的缺口、菲律宾无订阅钱包的缺口、俄罗斯的整体封锁

**次选叠加：菲律宾（仅一次性产品）+ 新加坡（纯卡片）**

### 4.4 上线前必做的 3 件事

1. **发邮件给 `compliance@dodopayments.com` 做书面预审**，明确说明：
   - 产品是 **100% 算法自动生成**、无真人介入
   - **无预测承诺**，定位为 entertainment / self-reflection
   - 附上网站的免责声明页、Refund Policy、ToS 链接
   - 原文依据：政策说这类审查 "is done on a case to base basis"，且违规罚款 "up to USD 425,000" — **拿一封邮件换掉这个尾部风险，非常值**
2. **产品深度避开"AI 生成的浅薄 PDF"**——政策原文明文举例。做成**可反复使用的交互式产品**（排盘工具 + 解读库 + 学习路径），不是一次性报告。
3. **网站合规基线**（FAQ Q40 原文）：公开显示 pricing / ToS / Privacy / **Refund & Cancellation Policy** / 联系方式，且 **PVF 表单内容必须与网站完全一致**。

---

## 第 6 节：未能核实项（诚实清单）

| # | 项目 | 状态 |
|---|---|---|
| 1 | **韩国占卜类服务的法律限制**（登记义务、无照经营刑责、未成年人广告限制） | ❌ **未核实**。中/英/韩维基、相关词条均无法律内容。**请自行查韩国法令信息中心（law.go.kr）与文化体育观光部指引** |
| 2 | **PayPal 对俄罗斯的政策原文** | ❌ **未核实**。PayPal newsroom 链接 404、country-select 404、country-availability 404。业界普遍知悉 2022-03 停止俄罗斯服务，但**本次未取得官方原文** |
| 3 | **Stripe 关于"俄罗斯发行卡能否跨境线上付款"的原文** | ❌ 未找到。仅确认俄罗斯不在 stripe.com/global 商户支持国列表中 |
| 4 | **Patreon 是否接受俄罗斯发行的卡** | ❌ 未核实（support.patreon.com 返回 403）。已核实 Patreon Terms 中**俄罗斯整体未列入**制裁清单 |
| 5 | **Gumroad 对俄罗斯买家的实际可用性** | ❌ 未核实。prohibited 页无国别清单，但底层通道能力未知 |
| 6 | **YooKassa 是否接受中国个人（自然人）签约** | ❌ **未核实**。官方页反复使用 "company"，无自然人说明 |
| 7 | **Dodo 中 JPY / SGD / PHP 的 Adaptive Currency 换汇加价与最低价** | ❌ 未逐项核实 |
| 8 | **Dodo 的买家年龄门槛 / 18+ 机制** | ❌ 未在文档中找到任何相关页面 |
| 9 | **Dodo 是否有 Japan/Korea 买家侧的隐性执行限制** | ❌ **无法核实**——因为 Dodo 未公开此类政策。**只能通过写邮件问 compliance 团队** |
| 10 | 中国个人购汇额度 / 跨境结汇税务规定 | ❌ 未核实。**一般性提示，请自行向银行/外汇局/税务确认** |
| 11 | Dodo 全部文档的全文关键词检索（psychic/tarot/sanctions 等） | ⚠️ **部分**。`llms-full.txt` 被截断（前 100,000 字符），故改为逐页核查 159 页文档索引 + 关键政策页全文。**不排除某个我未逐页打开的页面有相关表述** |

---

## 第 7 节：全部来源链接

**Dodo Payments（官方）**
- [Countries Eligible for Payment Acceptance（买家 226 国）](https://docs.dodopayments.com/miscellaneous/list-of-countries-we-accept-payments-from)
- [Merchant Acceptance Policy（关键！）](https://docs.dodopayments.com/miscellaneous/merchant-acceptance)
- [Countries Eligible for Merchant Acceptance（卖家 177 国）](https://docs.dodopayments.com/miscellaneous/accepted-countries-and-territories)
- [Payment Methods（完整表）](https://docs.dodopayments.com/features/payment-methods)
- [South Korea Payment Methods](https://docs.dodopayments.com/features/payment-methods/south-korea)
- [Asia-Pacific Payment Methods](https://docs.dodopayments.com/features/payment-methods/asia-pacific)
- [FAQs（Q6 个人无需注册 / Q84 结算币种 / Q102 Payoneer）](https://docs.dodopayments.com/miscellaneous/faq)
- [完整英文文档索引（159 页）](https://docs.dodopayments.com/_llms/en/docs.md)
- [Changelog v1.105.0（2026-06-22，新增韩国支付方式）](https://docs.dodopayments.com/changelog/v1.105.0)

**Stripe**
- [Prohibited and Restricted Businesses（Japan  psychic 禁令原文）](https://stripe.com/legal/restricted-businesses)
- [Global availability（无俄罗斯）](https://stripe.com/global)
- [日本の決済方法（コンビニ決済 70%/30% 数据）](https://stripe.com/jp/payments/payment-methods)

**Paddle**
- [Acceptable Use Policy（Prohibited #14 pseudo-science）](https://paddle.com/support/aup/)
- [Impact of sanctions on Russia and Belarus](https://www.paddle.com/help/legal/sanctions/impact-of-sanctions-on-russia-and-belarus)
- [Which countries are supported by Paddle?](https://www.paddle.com/help/legal/sanctions/which-countries-are-supported-by-paddle)

**Gumroad**
- [Prohibited（fortune tellers 豁免条款原文）](https://gumroad.com/prohibited)

**Patreon**
- [Terms of Use（制裁条款原文）](https://www.patreon.com/policy/legal)

**YooKassa**
- [Payment acceptance for non-residents](https://yookassa.ru/en/non-russian-residents/)
