from __future__ import annotations

import copy
import hashlib
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


SCRIPT_DIR = Path(__file__).resolve().parent
NOTES_ROOT = SCRIPT_DIR.parent
REVISION_ROOT = NOTES_ROOT.parent
SOURCE_DOCX = next((REVISION_ROOT / "v2修改稿留底" / "v2c").glob("*.docx"))
OUTPUT_DOCX = SCRIPT_DIR / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx"
OUTPUT_LOG = SCRIPT_DIR / "docx_generation_log_0419_1528.md"


REPLACEMENTS = [
    (
        "政务服务数字化改革如何重塑PPP项目推进结构？",
        "政务服务数字化改革与PPP项目推进结构重组",
    ),
    (
        "——基于政策文本量化、省级面板与治理过程的条件关联证据",
        "——基于政策文本量化与省级面板的条件关联证据",
    ),
    (
        "围绕政务服务数字化改革与PPP治理之间的关系，本文聚焦一个更具公共管理含义而非纯技术含义的问题",
        "本文关注的核心问题不是数字化改革是否立即全面提升PPP治理质量，而是它是否首先与PPP项目推进结构重组相关。基于地方政府PPP政策文本、统一口径的省级主面板以及项目级风险底表，本文将政策文本量化结果转化为治理能力测度变量，并以treat_share为唯一主识别中的核心处理变量，在地区和年份固定效应框架下估计政务服务数字化改革暴露强度与PPP项目推进结构、治理表现之间的平均条件关联。结果显示，在基准TWFE规格下，treat_share与exec_share显著正相关（系数0.3556），与proc_share显著负相关（系数-0.4023）；在同一262个正式估计观测上补充构造的执行/采购对数比率指标也给出同向支持（系数3.1916，p = 0.0277）。相比之下，综合治理质量指标ppp_quality_zindex虽有正向信号，但统计上不够稳定，不能承担全文主结论。进一步的趋势调整型DID显示，proc_share在加入省份线性趋势后仍为负且p = 0.0485，exec_share仅保持正向但p = 0.1945；wild cluster bootstrap下两项主结果的p值分别为0.0761和0.1221，提示推断强度较标准聚类结果更敏感。考虑到A/B/C/D维度与treat_share都依托政策文本工程，本轮将相关结果统一降格为“政策文本证据线索”，仅用于说明数字治理接口、数据协同与前端规范环节更可能率先响应，而不再将其写作独立的强机制检验。项目级高低风险识别仍只构成治理辅助识别的扩展分析，不改变本文以多期DID/TWFE为唯一主识别的研究结构。本文据此将数字化改革在PPP领域的经验结果界定为过程性、方向性的条件关联证据：其更接近于改善政府内部协同、前端规范和审批执行衔接，而非即时、全面地提升所有治理质量指标。",
    ),
    (
        "根据第5.1节并表工作簿中的“省份处理时点”工作表",
        "根据第5.1节并表工作簿中的“省份处理时点”工作表，当前口径下多数进入处理的省份首次处理年份为2016年，西藏为2017年；海南、青海和新疆生产建设兵团在当前口径下未进入处理。从文本工程到正式估计样本的流转为：1472份政策文本全文池，经统一筛选保留1307份正式DID文本文档样本，进一步聚合为288个省—年文本单元，再与正式V3主面板对接形成266个省—年观察值，其中262个进入正式回归样本，另有10000个项目级扩展观察值用于第5.7节。更谨慎地说，treat_share在正文中的含义应表述为由城市处理状态聚合形成的省级政策暴露强度，而不是单个城市层面的标准ATT处理指示。本轮修订随附附录A，补充提供province-year层面的treat_share重构表、处理时点表、266→262删样清单以及处理变量精确定义，以增强当前稿件的可复核性；但城市级处理名单和原始阈值底表未在当前仓库显式落地，因此本文只能将这一部分说明为省级重构意义上的复核材料，而不夸大为完整城市级复现包。",
    ),
    (
        "Y_pt = β TreatShare_pt + γ'X_pt + μ_p + λ_t + ε_pt",
        "Y_pt = β treat_share_pt + γ'X_pt + μ_p + λ_t + ε_pt",
    ),
    (
        "其中，Y_pt分别表示exec_share、proc_share和ppp_quality_zindex等省级结果变量",
        "其中，Y_pt分别表示exec_share、proc_share和ppp_quality_zindex等省级结果变量；treat_share_pt表示省份p在年份t所对应的数字化改革暴露强度；X_pt为正式主面板中统一口径的控制变量；μ_p和λ_t分别表示地区固定效应与年份固定效应；标准误在省级层面聚类。之所以将这一设定作为唯一主识别，原因有二：一是当前正式结果和写作总控文档都明确将treat_share多期DID/TWFE设定为全文唯一主模型；二是这一模型与本文“改革冲击—治理过程变化—推进结构调整”的问题结构最为契合。",
    ),
    (
        "这一模型的识别含义，并不是比较单一政策是否发生",
        "这一模型中的β更稳妥地应解释为：在控制地区固定效应、年份固定效应和一组正式主面板控制变量后，省级数字化改革暴露强度与PPP推进结构或治理结果之间的平均条件关联，而不是严格意义上的单一处理平均效应。原因在于，treat_share是连续暴露强度变量，处理批次又高度集中在2016年前后，did_any与did_intensity只能承担替代处理口径和诊断功能。就当前样本而言，正式主面板覆盖2014—2022年、31个省级单元与新疆生产建设兵团，共266个省—年观察值，其中262个进入正式主识别样本；后文所有主结果均以这一口径为基准锚点。",
    ),
    (
        "需要强调的是，本文对识别强度的处理是克制的。考虑到错位处理时点下TWFE动态系数的解释存在额外边界",
        "需要强调的是，本文对识别强度的处理是克制的。事件研究在本文中只用于说明动态路径和识别边界，不用于声称平行趋势已经成立。考虑到错位处理时点下TWFE动态系数的解释存在额外边界，趋势调整型DID、逐省剔除和wild cluster bootstrap共同承担主识别防守功能；did_any与did_intensity仅作为连续处理变量的替代口径；stack DID、cohort ATT、PSM-DID、DML、候选工具变量和其他替代估计只保留为边界诊断，不改变主识别结构（Sun & Abraham, 2021）。",
    ),
    (
        "从公共管理研究的角度看，这样的识别安排意味着本文并不试图用更复杂的方法覆盖一切疑问",
        "从公共管理研究的角度看，这样的识别安排意味着本文并不试图用更复杂的方法覆盖一切疑问，而是将不同证据放在各自恰当的位置上：主识别回答“改革是否首先改善了推进结构”，政策文本证据线索回答“改革首先改动了哪些治理接口与制度表达”，稳健性检验回答“主结果是否在更严格设定下仍可防守”，扩展分析回答“文本与结构变量是否还能服务于项目级辅助识别”。这种分层安排，构成了后文实证分析的基本结构。",
    ),
    (
        "同时需要说明，机制与异质性部分主要依托当前项目归档中的既有正式辅助结果",
        "同时需要说明，机制与异质性部分主要依托当前项目归档中的既有正式辅助结果，其任务在于补充解释和提示适用边界，而不与表4主识别处于同一证据层级。尤其是A/B/C/D维度与treat_share都来自政策文本工程，故其更适合被理解为制度表达和治理重心重分布的文本证据线索，而不是与表4并列的第二套识别体系。本文因此不将这些结果写成第二主识别，而只在其能够支持的范围内作辅助性讨论。",
    ),
    (
        "表4报告了基准多期DID/TWFE结果。结果显示",
        "表4报告了基准多期DID/TWFE结果。结果显示，在地区和年份固定效应框架下，treat_share对exec_share的估计系数为0.3556，在1%水平上显著；对proc_share的估计系数为-0.4023，同样在1%水平上显著。两者共同指向同一个结论：在基准TWFE规格下，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组。更稳妥地说，这里识别到的是推进结构重组的平均条件关联，而不是数字化改革已经对PPP治理产生全面、稳定因果改善的证明。",
    ),
    (
        "为回应份额型因变量的加总约束，本文进一步在与表4相同的262个正式估计观测上补充构造执行/采购对数比率指标",
        "为回应份额型因变量的加总约束，本文进一步在与表4相同的262个正式估计观测上补充构造执行/采购对数比率指标log((exec_share+c)/(proc_share+c))。考虑到样本中存在零份额情形，本轮补充估计以执行阶段与采购阶段最小正份额的一半作为连续性修正，取c = 0.0034。在与表4一致的地区固定效应、年份固定效应、省级聚类和控制变量设定下，treat_share对该对数比率的估计系数为3.1916，标准误为1.4500，正态近似p = 0.0277。这一结果表明，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组；同时，将c改为最小正份额或固定值0.01、0.001后，系数方向均保持为正。鉴于该结果属于本轮新增补充估计，本文将其理解为份额型结果处理下的构成性补强，而不是替代正式主规格的第二主模型。",
    ),
    (
        "5.4 机制分析",
        "5.4 政策文本证据线索与阶段性传导",
    ),
    (
        "在确认数字化改革暴露强度与PPP推进结构重组存在稳定条件关联之后",
        "在确认数字化改革暴露强度与PPP推进结构重组存在稳定条件关联之后，进一步的问题是：这一变化更可能通过哪些治理环节显现。根据第三部分提出的理论框架，这里的核心不是寻找一条完整闭合的强中介链条，而是判断改革是否优先作用于数字治理接口和前端规范环境，并是否存在阶段性传导。考虑到A/B/C/D维度与treat_share都依托政策文本工程，本节不再将相关结果写成独立的“机制检验”，而改写为政策文本证据线索：其任务是说明制度表达和治理重心如何随改革推进而调整，而不是提供与表4并列的第二套因果识别。",
    ),
    (
        "表5汇总了机制检验的核心结果。首先",
        "表5汇总了这组文本证据线索。首先，treat_share对A维度指数的影响显著，表明数字治理接口与数据协同确实是最先响应的治理环节，这与理论部分提出的“接口优先”判断一致。其次，B维度和C维度对应的文本治理表达也出现联动变化，说明前端准入、采购安排和执行衔接的制度重心随着改革推进而发生了重分布。需要注意的是，这里的经验含义应理解为治理表达结构变化和制度重心转移，而不宜机械理解为所有单项指标均线性改善。尤其对B维度而言，相关系数的方向含义必须结合指标定义解释，正文不宜直接把它翻译为“前端规范显著增强”，更稳妥的写法是“前端规范与准入表达发生显著调整”。再次，在结果方程中，A维度相关项对exec_share和proc_share的系数方向与理论预期大体一致，但统计上并不稳定；链式路径中，B_idx→C_idx和C_idx→D_idx两段显著，而A_idx→B_idx不显著；严格中介分解的Sobel检验和Bootstrap区间均未支持稳定中介效应。",
    ),
    (
        "综合来看，当前机制证据更支持",
        "综合来看，当前证据更支持“接口优先、前端规范先行、局部链条成立”的判断，而不支持“完整稳定的强中介链条已经建立”。这一点需要明确写出。否则，文本证据部分很容易被误写成一个比数据更完整的故事。对本文而言，较为稳妥的表述应是：数字化改革首先改变了政府接口、数据协同和前端程序环境，并伴随采购—执行治理维度的阶段性响应；但这些变化主要体现为治理表达和制度重心的调整，而不是一条从前端到后端均稳定显著、方向单调的强中介链条。",
    ),
    (
        "从公共管理角度看，这一结果的含义在于，PPP治理过程的改善首先依赖制度接口和程序环境的调整",
        "从公共管理角度看，这一结果的含义在于，PPP治理过程的改善首先依赖制度接口和程序环境的调整，而非所有治理环节同步升级；从证据边界看，表5支持的是部分机制和阶段性传导，而不是完整闭合的机制证明。与此同时，由于A/B/C/D维度均来自政策文本的省—年聚合结果，当前稿件更适合将其解释为制度表达与治理重心的重分布证据，而不是与主识别并列的独立因果机制识别。为避免同源文本被误读为独立机制，本轮在附录E中单列说明处理变量与文本证据线索的来源边界。",
    ),
    (
        "本节并不引入新的主识别策略",
        "本节并不引入新的主识别策略，而是围绕表4所报告的treat_share多期DID/TWFE主结果，按“趋势风险—单一区域驱动—有限聚类推断”三个问题逐项防守，并同时明确其证据边界。正文叙述与附录D同步报告标准聚类结果、trend-adjusted DID和wild cluster bootstrap的关键数值。相较之下，stack DID、cohort ATT以及动态补充识别仅保留为边界诊断，不再承担正文中的主防守功能。",
    ),
    (
        "鉴于前文事件研究中的领先项并非完全平稳，本文在正式主规格之外进一步加入省份线性时间趋势",
        "鉴于前文事件研究中的领先项并非完全平稳，本文在正式主规格之外进一步加入省份线性时间趋势，对主结果进行趋势调整型DID检验。该检验保持正式主面板、处理变量、控制变量、地区固定效应和年份固定效应不变，仅额外控制省级线性趋势，因此其作用在于回应“省际异质趋势可能影响主结果”的识别顾虑，而不是替代表4中的主识别框架。趋势调整后的结果表明，采购阶段占比下降这一核心结果仍保持显著负向：proc_share的系数为-0.3521，p = 0.0485，说明推进结构中的“采购向执行转换”并不完全依赖共同趋势设定；执行阶段占比上升在方向上保持一致，但统计强度明显减弱，exec_share的系数为0.2263，p = 0.1945，表明这一判断更容易受到趋势设定影响；综合治理质量口径在趋势调整后反而转为负向且p = 0.6780，更不能被提升为稳健主结论。就防守价值而言，采购阶段占比是三项结果中最强的一项，执行阶段占比主要体现为方向稳定但强度更敏感，综合治理质量口径则继续只能作为边界性结果处理。图8A、表8与附录D共同服务于这一层防守性说明。",
    ),
    (
        "5.6.3 更保守推断下的边界说明",
        "5.6.3 Wild Cluster Bootstrap 与更保守推断边界",
    ),
    (
        "考虑到正式基准样本的地区聚类数量有限，本文进一步采用更保守的wild cluster bootstrap作为小样本推断层面的补充说明",
        "考虑到正式基准样本的地区聚类数量有限，本文进一步采用更保守的wild cluster bootstrap作为小样本推断层面的补充说明。该部分不改变估计框架，也不改变结果方向判断，其作用只是检验在更严格的推断标准下，核心推进结构结论是否仍保留相同的方向层级。为避免“表内显著、附录保守”造成的信息分裂，本轮将wild结果纳入主识别防守叙述，并在附录D汇总报告。结果表明，执行阶段占比与采购阶段占比的方向与基准DID保持一致，但统计强度进一步减弱：exec_share的wild cluster bootstrap p值为0.0761，proc_share为0.1221，ppp_quality_zindex为0.2372。也就是说，在更保守的有限聚类推断下，推进结构重组的方向判断仍被保留，但已不足以支撑强因果措辞；其中采购阶段占比下降的方向更稳定，执行阶段占比上升则更依赖模型设定与样本扰动。因而，这一层证据更适合作为边界说明，而不构成对主识别的额外强化。此外，随机置换得到的安慰剂分布整体围绕零值展开，相关图示仅作为补充材料中的诊断性展示，不承担正文主防守功能。",
    ),
    (
        "本文围绕政务服务数字化改革与PPP治理之间的关系，构建了一条由政策文本量化、省级面板估计和项目级扩展分析相衔接的研究路径",
        "本文围绕政务服务数字化改革与PPP治理之间的关系，构建了一条由政策文本量化、省级面板估计和项目级扩展分析相衔接的研究路径。与将数字化改革简单写成“全面提升治理质量”的宽泛叙述不同，本文更关注改革首先改变了PPP治理中的哪一类具体环节。基于正式口径的省级主面板和treat_share多期DID/TWFE框架，本文得到三个层次分明且边界清晰的结论。",
    ),
    (
        "第二，综合治理质量指标存在正向信号，但稳定性不足",
        "第二，综合治理质量指标存在正向信号，但稳定性不足，不能承担全文主结论。无论在基准结果还是在补充检验中，ppp_quality_zindex都没有形成与推进结构结果同等稳固的统计支持。因此，本文只把这一结果理解为边际改善方向，而不把它提升为“治理质量全面提升”的强断言。与之相应，事件研究结果只能用于说明动态路径和识别边界；趋势调整型DID与wild cluster bootstrap则进一步表明，采购阶段占比下降的防守性支持强于执行阶段占比上升，主结果的推断强度仍需克制表述。",
    ),
    (
        "第三，机制分析支持",
        "第三，文本证据线索支持“接口优先、前端规范先行、部分机制成立”的判断，但不支持完整稳定的强中介链条。A维度所代表的数字治理接口与数据协同率先响应，前端规范和采购—执行治理维度存在局部传导，但严格中介检验并未成立。由于A/B/C/D维度与treat_share都来自政策文本工程，本轮将其统一降格为制度表达与治理重心重分布的证据线索，而不再把它写成独立的强机制识别。项目级扩展分析进一步表明，在严格避免标签泄漏的前提下，PPP项目的高低风险具有一定可识别性，但这一部分仅构成治理辅助识别，不参与主识别，也不替代制度治理。",
    ),
    (
        "趋势调整型DID与逐省剔除检验进一步说明",
        "趋势调整型DID与逐省剔除检验进一步说明，推进结构重组这一核心判断在方向上具有较强稳定性，其中采购阶段占比下降的防守性支撑更强，执行阶段占比上升则对趋势设定和样本扰动更为敏感；wild cluster bootstrap进一步提示，在有限聚类下两项主结果方向仍保留，但推断强度弱于标准聚类结果。也正因如此，本文不将当前结果解释为稳定、强因果的制度效应，而将其界定为过程性、方向性的条件关联证据。",
    ),
    (
        "基于上述结果，本文的政策含义可以集中在四个方面",
        "基于上述结果，本文的政策含义可以集中在四个方面。其一，数字政府建设在PPP领域的现实着力点，应更多放在跨部门协同、信息联通和程序接口重构上，而不是期待抽象质量指标的即时跃升。其二，前端规范准入、物有所值论证、财政承受能力审查和实施方案审批等环节，是数字化改革转化为推进结构改善的关键节点，应作为治理重心予以持续优化。其三，财政、发展改革、政务数据主管部门与行业主管部门之间，应围绕项目入库、采购启动、合同执行和信息披露建立共享校核接口，把“采购—执行转换效率”纳入过程性治理绩效，而不是只考核平台上线数量。其四，项目级模型识别可以作为高风险筛查和辅助预警工具，但其使用必须建立在标签与特征严格分离、预测与因果严格分离的原则之上。",
    ),
    (
        "5. 肖永慧. 2025. 大数据综合试验区提升企业数据资产化的机制",
        "5. 肖永慧. 2025. 大数据综合试验区提升企业数据资产化的机制——基于多期DID模型的实证分析. 中国流通经济, (12): 105-122. DOI: 10.14089/j.cnki.cn11-3664/f.2025.12.008.",
    ),
]


INSERT_AFTER_PREFIX = "这组结果的作用在于为主文中的结构重组判断提供构成性补强"
INSERTED_APPENDIX_BLOCKS = [
    ("heading", "附录C 文本池与样本流转一致性说明"),
    (
        "body",
        "本轮统一采用以下样本流转口径：1472份政策文本全文池，经正式筛选形成1307份DID文本文档样本，进一步聚合为288个省—年文本单元，再与正式V3主面板对接形成266个省—年观测值，其中262个进入主回归样本，另有10000个项目级扩展观察值用于第5.7节。对应的流转表已写入appendix_C_sample_flow_0419_1528.csv。",
    ),
    (
        "body",
        "审稿报告指出旧附表链条中曾出现“全量政策文本池165”的表述。基于当前仓库可核实的正式源文件，本轮未发现可以支持“165 = 全量文本池”这一manuscript-facing口径的现行资产，因此v2d不采纳该写法，而统一维持1472→1307→288→266→262的正式链条。如果后续确有独立的扩展审计文本窗口，应以不同名称单列，而不能与全文政策文本池混用。",
    ),
    ("heading", "附录D 主识别防守结果摘要"),
    (
        "body",
        "主识别防守结果可概括为三点。第一，trend-adjusted DID下，exec_share的系数为0.2263（p = 0.1945），proc_share的系数为-0.3521（p = 0.0485），ppp_quality_zindex的系数为-0.1699（p = 0.6780）；这说明采购阶段占比下降的防守性支撑强于执行阶段占比上升。第二，wild cluster bootstrap下，exec_share、proc_share和ppp_quality_zindex的p值分别为0.0761、0.1221和0.2372，方向判断保留，但更保守推断下的统计强度明显减弱。第三，逐省剔除结果未出现核心系数符号翻转，但强度对样本扰动仍有敏感性。对应汇总表已写入appendix_D_defensive_inference_summary_0419_1528.csv。",
    ),
    ("heading", "附录E 处理变量与文本证据线索的来源边界"),
    (
        "body",
        "treat_share由城市处理状态聚合到省—年层面，A/B/C/D维度则来自政策文本工程后的省—年聚合指标。两类变量都以政策文本体系为基础，因此它们之间的相关性不能被直接写成彼此独立的“机制识别”。本轮据此将第5.4节统一改写为“政策文本证据线索与阶段性传导”，其作用是说明制度表达和治理重心如何随改革推进而调整，而不是证明一条与主识别并列、来源完全独立的强机制链条。更详细的来源边界说明已写入appendix_E_source_boundary_0419_1528.md。",
    ),
]


REMOVE_FROM_PREFIX = "附录A 文本分析诊断与样本补充"


def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def paragraph_text(p: ET.Element) -> str:
    return "".join((t.text or "") for t in p.findall(".//w:t", NS)).strip()


def top_level_children(body: ET.Element) -> list[ET.Element]:
    return list(body)


def iter_top_level_paragraphs(body: ET.Element):
    for child in top_level_children(body):
        if child.tag == qn("p"):
            text = paragraph_text(child)
            if text:
                yield child, text


def first_run_rpr(p: ET.Element) -> ET.Element | None:
    for child in p:
        if child.tag == qn("r"):
            rpr = child.find(qn("rPr"))
            if rpr is not None:
                return copy.deepcopy(rpr)
    return None


def set_paragraph_text(p: ET.Element, text: str) -> None:
    ppr = p.find(qn("pPr"))
    run_rpr = first_run_rpr(p)
    for child in list(p):
        if child is not ppr:
            p.remove(child)
    r = ET.Element(qn("r"))
    if run_rpr is not None:
        r.append(run_rpr)
    t = ET.SubElement(r, qn("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    p.append(r)


def clone_paragraph(template: ET.Element, text: str) -> ET.Element:
    new_p = copy.deepcopy(template)
    set_paragraph_text(new_p, text)
    return new_p


def insert_after(body: ET.Element, ref: ET.Element, new_p: ET.Element) -> None:
    idx = top_level_children(body).index(ref)
    body.insert(idx + 1, new_p)


def serialize_docx(source_docx: Path, document_xml: bytes, output_docx: Path) -> None:
    with zipfile.ZipFile(source_docx, "r") as src:
        items = [(info, src.read(info.filename)) for info in src.infolist()]

    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info, payload in items:
            if info.filename == "word/document.xml":
                payload = document_xml
            dst.writestr(info, payload)


def media_counts(docx_path: Path) -> dict[str, int]:
    counts = {"media": 0, "charts": 0, "embeddings": 0}
    with zipfile.ZipFile(docx_path, "r") as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                counts["media"] += 1
            elif name.startswith("word/charts/"):
                counts["charts"] += 1
            elif name.startswith("word/embeddings/"):
                counts["embeddings"] += 1
    return counts


def find_paragraph(paragraphs: list[tuple[ET.Element, str]], prefix: str) -> tuple[ET.Element, str]:
    matches = [(p, text) for p, text in paragraphs if text.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one paragraph for prefix: {prefix[:60]!r}, got {len(matches)}")
    return matches[0]


def remove_tail_from(body: ET.Element, start_element: ET.Element) -> int:
    children = top_level_children(body)
    start_idx = children.index(start_element)
    removed = 0
    for child in list(children[start_idx:]):
        if child.tag == qn("sectPr"):
            continue
        body.remove(child)
        removed += 1
    return removed


def main() -> None:
    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        document_xml = zf.read("word/document.xml")
    document = ET.fromstring(document_xml)
    body = document.find("w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml missing body")

    paragraphs = list(iter_top_level_paragraphs(body))
    appendix_heading_tpl, _ = find_paragraph(paragraphs, "附录A 处理变量与样本流转补充说明")
    body_tpl, _ = find_paragraph(paragraphs, "本轮修订在正式V3主面板基础上补充提供了province-year层面的treat_share重构材料")

    replacements_done: list[str] = []
    for old_prefix, new_text in REPLACEMENTS:
        paragraph, old_text = find_paragraph(paragraphs, old_prefix)
        set_paragraph_text(paragraph, new_text)
        replacements_done.append(old_text[:50])

    paragraphs = list(iter_top_level_paragraphs(body))
    anchor_paragraph, _ = find_paragraph(paragraphs, INSERT_AFTER_PREFIX)
    inserted = 0
    ref = anchor_paragraph
    for kind, text in INSERTED_APPENDIX_BLOCKS:
        template = appendix_heading_tpl if kind == "heading" else body_tpl
        new_p = clone_paragraph(template, text)
        insert_after(body, ref, new_p)
        ref = new_p
        inserted += 1

    paragraphs = list(iter_top_level_paragraphs(body))
    tail_start, _ = find_paragraph(paragraphs, REMOVE_FROM_PREFIX)
    removed = remove_tail_from(body, tail_start)

    xml_bytes = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    serialize_docx(SOURCE_DOCX, xml_bytes, OUTPUT_DOCX)

    source_media = media_counts(SOURCE_DOCX)
    output_media = media_counts(OUTPUT_DOCX)
    log_lines = [
        "# DOCX Generation Log",
        "",
        f"- source_docx: `{SOURCE_DOCX}`",
        f"- output_docx: `{OUTPUT_DOCX}`",
        f"- replacements: `{len(replacements_done)}`",
        f"- inserted_paragraphs: `{inserted}`",
        f"- removed_tail_children: `{removed}`",
        f"- source_sha256: `{sha256(SOURCE_DOCX)}`",
        f"- output_sha256: `{sha256(OUTPUT_DOCX)}`",
        f"- source_media: `{source_media}`",
        f"- output_media: `{output_media}`",
        "- object_preservation_method: copied the full source package and replaced only `word/document.xml`.",
        "- note: old legacy appendix tail starting at `附录A 文本分析诊断与样本补充` was removed and replaced by the v2d manuscript-facing appendix structure.",
    ]
    OUTPUT_LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"OUTPUT_DOCX={OUTPUT_DOCX}")
    print(f"REPLACEMENTS={len(replacements_done)}")
    print(f"INSERTED={inserted}")
    print(f"REMOVED={removed}")


if __name__ == "__main__":
    main()
