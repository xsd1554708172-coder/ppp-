from __future__ import annotations

import copy
import hashlib
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_DOCX = SCRIPT_DIR.parent / "v1d" / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1d_codexrev_20260419.docx"
OUTPUT_DOCX = SCRIPT_DIR / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1e_0419_2307.docx"
OUTPUT_LOG = SCRIPT_DIR / "docx_generation_log_0419_2307.md"


def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"


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


def insert_before(body: ET.Element, ref: ET.Element, new_p: ET.Element) -> None:
    idx = top_level_children(body).index(ref)
    body.insert(idx, new_p)


def insert_after(body: ET.Element, ref: ET.Element, new_p: ET.Element) -> None:
    idx = top_level_children(body).index(ref)
    body.insert(idx + 1, new_p)


def find_para_startswith(body: ET.Element, prefix: str) -> ET.Element:
    for p, text in iter_top_level_paragraphs(body):
        if text.startswith(prefix):
            return p
    raise KeyError(prefix)


def serialize_docx(source_docx: Path, document_xml: bytes, output_docx: Path) -> None:
    with zipfile.ZipFile(source_docx, "r") as src:
        items = [(info, src.read(info.filename)) for info in src.infolist()]
    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info, payload in items:
            if info.filename == "word/document.xml":
                payload = document_xml
            dst.writestr(info, payload)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def main() -> None:
    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        document = ET.fromstring(zf.read("word/document.xml"))

    body = document.find("w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml missing body")

    chapter_heading_tpl = find_para_startswith(body, "2 文献综述")
    body_tpl = find_para_startswith(body, "数字政府研究的一个基本判断是")

    subtitle_p = find_para_startswith(body, "——基于政策文本量化、省级面板与治理过程证据")
    abstract_p = find_para_startswith(body, "基于2014—2022年省级面板、PPP政策文本和项目级风险底表")
    keywords_p = find_para_startswith(body, "关键词：数字政府")
    sec41_p1 = find_para_startswith(body, "本文的数据结构由三个相互衔接但层级分明的部分构成")
    sec41_p2 = find_para_startswith(body, "从样本结构看，本文首先收集并整理了1472份PPP政策文本")
    sec41_p3 = find_para_startswith(body, "表1报告了政策文本样本结构与语料覆盖情况")
    sec43_p1 = find_para_startswith(body, "在主识别部分，本文的核心处理变量是")
    sec43_p3 = find_para_startswith(body, "从正式主面板口径看")
    sec44_p1 = find_para_startswith(body, "本文的主识别模型是以")
    sec44_p2 = find_para_startswith(body, "其中，Y_pt分别表示")
    sec44_p3 = find_para_startswith(body, "需要强调的是，本文对识别强度的处理是克制的")
    sec52_p1 = find_para_startswith(body, "在描述性事实之后，本文转向正式主识别")
    sec52_p2 = find_para_startswith(body, "表4报告了基准多期DID/TWFE结果")
    sec52_p3 = find_para_startswith(body, "相较之下，")
    sec52_p4 = find_para_startswith(body, "基准结果对公共管理研究的含义在于")
    sec54_heading = find_para_startswith(body, "5.4 机制分析")
    sec54_p1 = find_para_startswith(body, "在确认数字化改革首先改善PPP推进结构之后")
    sec54_p2 = find_para_startswith(body, "表5汇总了机制检验的核心结果")
    sec54_p3 = find_para_startswith(body, "综合来看，当前机制证据更支持")
    sec54_p4 = find_para_startswith(body, "从公共管理")
    sec56_heading = find_para_startswith(body, "5.6 稳健性检验与主识别防守")
    sec56_p1 = find_para_startswith(body, "本节并不引入新的主识别策略")
    sec561_p1 = find_para_startswith(body, "鉴于前文事件研究中的领先项并非完全平稳")
    sec563_heading = find_para_startswith(body, "5.6.3 更保守推断下的边界说明")
    sec563_p1 = find_para_startswith(body, "考虑到正式基准样本的地区聚类数量有限")
    sec564_p1 = find_para_startswith(body, "本文同时保留了stack DID")
    sec6_p1 = find_para_startswith(body, "本文围绕政务服务数字化改革与PPP治理之间的关系")
    sec6_p2 = find_para_startswith(body, "第一，数字化改革最稳")
    sec6_p3 = find_para_startswith(body, "第二，综合治理质量指标存在正向信号")
    sec6_p4 = find_para_startswith(body, "第三，机制分析支持")
    sec6_p5 = find_para_startswith(body, "趋势调整型 DID 与逐省剔除检验进一步说明")
    transparency_heading = find_para_startswith(body, "研究透明度与复现说明")
    trans_p2 = find_para_startswith(body, "本文的主要复现材料包括")

    set_paragraph_text(subtitle_p, "——基于政策文本量化与省级面板的条件关联证据")
    set_paragraph_text(
        abstract_p,
        "本文关注的核心问题不是数字化改革是否立即全面提升PPP治理质量，而是它是否首先与PPP项目推进结构重组相关。基于地方政府PPP政策文本、统一口径的省级主面板以及项目级风险底表，本文将政策文本量化结果转化为治理能力测度变量，并以treat_share为唯一主识别中的核心处理变量，在地区和年份固定效应框架下估计数字化改革暴露强度与PPP项目推进结构、治理表现之间的平均条件关联。结果显示，在基准TWFE规格下，treat_share与exec_share显著正相关（系数0.3556），与proc_share显著负相关（系数-0.4023）；在同一262个正式估计观测上补充构造的执行/采购对数比率指标也给出同向支持（系数3.1916，p = 0.0277）。相比之下，综合治理质量指标ppp_quality_zindex虽有正向信号，但统计上不够稳定，不能承担全文主结论。事件研究仅用于动态路径和识别边界说明；趋势调整型DID与逐省剔除表明采购阶段占比下降的防守性支撑强于执行阶段占比上升；wild cluster bootstrap进一步提示推断强度弱于标准聚类结果。A/B/C/D文本维度与treat_share均依托政策文本工程，因此相关结果统一降格为“政策文本证据线索”，仅用于解释制度接口、数据协同和前端规范环节更可能率先响应，而不再写作独立的强机制识别。项目级高低风险识别只属于治理辅助识别，不改变本文以多期DID/TWFE为唯一主识别的研究结构。本文据此将数字化改革在PPP领域的经验结果界定为过程性、方向性的条件关联证据：其更接近于改善政府内部协同、前端规范和采购—执行衔接，而非立即、全面地提升所有治理质量指标。"
    )
    set_paragraph_text(keywords_p, "关键词：数字政府；政务服务数字化改革；PPP治理；政策文本量化；推进结构重组；治理辅助识别")

    set_paragraph_text(sec41_p1, "本文使用三层正式数据资产：一是PPP政策文本整合池及其文档级变量表，二是省—年文本聚合变量表，三是正式V3主面板与项目级风险底表。当前仓库内可直接核实的样本流转链条为：1472份政策文本全文池，经正式筛选形成1307份DID主识别窗口文本文档，再聚合为288个省—年文本单元，随后与正式V3主面板对接形成266个省—年观测值，其中262个进入第5.3节正式估计样本，另外4个新疆生产建设兵团观测因基准控制变量不完整而被排除。本轮v1e交付随附appendix_C_sample_flow_20260419.csv和appendix_A_sample_exclusions_20260419.csv，用于把1472→1307→288→266→262的样本流转链条落成可复核资产。")
    set_paragraph_text(sec41_p2, "正式V3主面板覆盖2014—2022年省级观察，包含31个省级单位及新疆生产建设兵团。文档级变量表与省—年变量表分别承担文本工程和聚合映射功能，只有在完成省—年层级映射并进入正式主面板后，相关文本变量才参与后文的机制解释与扩展分析；项目级风险底表则只在第5.7节服务于治理辅助识别，不进入主识别框架。与上一轮相比，本轮不再只在正文中口头描述样本流转，而是把关键计数、删样节点和处理变量重构表同步写入附录化资产。")
    set_paragraph_text(sec41_p3, "需要说明的是，当前仓库可以直接支持省—年层面的treat_share重构、样本流转复核和基准样本删样说明，但尚未显式落地城市级处理名单与原始阈值表。因此，本轮只能把相关补充材料界定为province-year层面的复核资产，而不能夸大为完整的城市级复现包。")

    set_paragraph_text(sec43_p1, "在主识别部分，本文的核心处理变量是treat_share。该变量以省—年为单位，由城市处理状态聚合而成，精确定义为treat_share_{pt} = treated_city_count_{pt} / city_n_{pt} = (1/N_{pt}) × Σ_i treat_i。与之相对应，post_t = 1[t >= 2016]，did_intensity_{pt} = post_t × treat_share_{pt}，did_any_{pt} = 1(did_intensity_{pt} > 0)；后两者仅作为替代处理口径或诊断口径使用，不进入全文主结论。根据本轮fresh reconstruction，当前口径下多数进入处理的省份首次处理年份为2016年，西藏为2017年；海南、青海和新疆生产建设兵团在当前post窗口下未进入处理。对应的province-year重构表与处理时点表已写入appendix_A_treat_share_reconstruction_20260419.csv和appendix_A_province_treatment_timing_20260419.csv。")
    set_paragraph_text(sec43_p3, "从正式主面板口径看，treat_share、exec_share和proc_share均取值于0到1之间，其中treat_share样本均值约为0.301，exec_share与proc_share的样本均值分别约为0.705和0.281。当前正式基准DID口径使用8个主控制变量：dfi、digital_econ、base_station_density、software_gdp_share、it_service_gdp_share、ln_rd_expenditure、ln_tech_contract_value与ln_patent_grants。本轮fresh baseline rerun即按这一正式口径复算，并与官方5.3长表在机器精度上对齐。")

    set_paragraph_text(sec44_p1, "本文的主识别模型是以treat_share为核心处理变量的多期DID/TWFE模型。形式上，本文估计的核心方程可以写为：Y_pt = β treat_share_pt + γ'X_pt + μ_p + λ_t + ε_pt。")
    set_paragraph_text(sec44_p2, "其中，Y_pt分别表示exec_share、proc_share和ppp_quality_zindex等省级结果变量；treat_share_pt表示省份p在年份t所对应的数字化改革暴露强度；X_pt为正式主面板中的控制变量；μ_p和λ_t分别表示地区固定效应与年份固定效应；标准误在省级层面聚类。更稳妥地说，这里的β应解释为在控制地区固定效应、年份固定效应和正式控制变量后，省级数字化改革暴露强度与PPP推进结构或治理结果之间的平均条件关联，而不是严格意义上的单一处理平均效应。原因在于，treat_share属于连续暴露强度变量，处理批次又高度集中在2016年前后，因此did_any与did_intensity只承担替代处理口径和诊断功能。")
    set_paragraph_text(sec44_p3, "需要强调的是，本文对识别强度的处理是克制的。事件研究在本文中只用于说明动态路径和识别边界，不用于声称平行趋势已经成立。考虑到错位处理时点下TWFE动态系数的解释存在额外边界，趋势调整型DID、逐省剔除和wild cluster bootstrap共同承担主识别防守功能；did_any与did_intensity仅作为连续处理变量的替代口径；stack DID、cohort ATT、PSM-DID、DML、候选工具变量和其他替代估计只保留为边界诊断，不改变主识别结构。同时需要说明，机制与异质性部分主要依托当前项目归档中的既有正式辅助结果，其任务在于补充解释和提示适用边界，而不与表4主识别处于同一证据层级。")

    set_paragraph_text(sec52_p1, "在描述性事实之后，本文转向正式主识别，考察政务服务数字化改革是否以及在何种意义上改变了PPP项目推进结构。根据总控文件设定，这一部分构成全文的核心主证据，判断标准也必须服从“PPP推进结构改善优先”的写作边界。")
    set_paragraph_text(sec52_p2, "表4报告了基准多期DID/TWFE结果。结果显示，在地区和年份固定效应框架下，treat_share对exec_share的估计系数为0.3556，在1%水平上显著；对proc_share的估计系数为-0.4023，同样在1%水平上显著。两者共同指向同一结论：在基准TWFE规格下，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组。更稳妥地说，这里识别到的是推进结构重组的平均条件关联，而不是数字化改革已经对PPP治理产生全面、稳定因果改善的证明。")
    log_ratio_p = clone_paragraph(sec52_p2, "为回应份额型因变量的构成性约束，本文进一步在与表4相同的262个正式估计观测上补充构造执行/采购对数比率指标log((exec_share+c)/(proc_share+c))。考虑到样本中存在零份额情形，本轮补充估计以执行阶段与采购阶段最小正份额的一半作为连续性修正，即c = 0.0034。在与表4一致的地区固定效应、年份固定效应、省级聚类和控制变量设定下，treat_share对该对数比率的估计系数为3.1916，标准误为1.4500，正态近似p = 0.0277。同时，将c改为最小正份额或固定值0.01、0.001后，系数方向均保持为正。这一结果表明，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组；但鉴于该结果属于新增补充估计，本文只将其理解为份额型结果处理下的构成性补强，而不是替代正式主规格的第二主模型。")
    insert_after(body, sec52_p2, log_ratio_p)
    set_paragraph_text(sec52_p3, "相较之下，ppp_quality_zindex的估计系数虽为正，但在统计上并不显著。这个结果具有明确的写作含义。它说明数字化改革并非完全没有改善综合治理质量的方向性信号，但这一信号不足以承担全文主结论。因此，本文只将其解释为边际改善信号，而不把它提升到与推进结构结果并列的地位。")
    set_paragraph_text(sec52_p4, "基准结果对公共管理研究的含义在于，数字化改革的现实作用更接近于改善政府内部流程衔接和项目推进程序，而非立即改变所有治理结果。与此同时，也必须保持边界控制：表4及对数比率补充估计共同支持的是推进结构和治理过程的平均条件关联，不支持将改革表述为“全面改善PPP治理质量”的强断言。")

    set_paragraph_text(sec54_heading, "5.4 政策文本证据线索与阶段性传导")
    set_paragraph_text(sec54_p1, "在确认数字化改革暴露强度与PPP推进结构重组存在稳定条件关联之后，进一步的问题是：这一变化更可能通过哪些治理环节显现。根据第三部分提出的理论框架，这里的核心不是寻找一条完整闭合的强中介链条，而是判断改革是否优先作用于数字治理接口和前端规范环境，并是否存在阶段性传导。考虑到A/B/C/D维度与treat_share都依托政策文本工程，本节不再将相关结果写成独立的“机制检验”，而改写为政策文本证据线索。")
    set_paragraph_text(sec54_p2, "表5汇总了这组文本证据线索。首先，treat_share对A维度指数的影响显著，表明数字治理接口与数据协同确实是最先响应的治理环节，这与理论部分提出的“接口优先”判断一致。其次，B维度和C维度对应的文本治理表达也出现联动变化，说明前端准入、采购安排和执行衔接的制度重心随改革推进而发生了重分布。需要注意的是，这里的经验含义应理解为治理表达结构变化和制度重心转移，而不宜机械理解为所有单项指标均线性改善。")
    set_paragraph_text(sec54_p3, "综合来看，当前证据更支持“接口优先、前端规范先行、部分机制成立”的判断，而不支持完整稳定的强中介链条已经建成。A维度相关项对exec_share和proc_share的系数方向与理论预期大体一致，但统计上并不稳定；链式路径中，B_idx→C_idx和C_idx→D_idx两段显著，而A_idx→B_idx不显著；严格中介分解的Sobel检验和Bootstrap区间均未支持稳定中介效应。")
    set_paragraph_text(sec54_p4, "从公共管理视角看，这一结果的含义在于，PPP治理过程的改善首先依赖制度接口和程序环境的调整，而非所有治理环节同步升级；从证据边界看，表5支持的是部分机制和阶段性传导，而不是完整闭合的机制证明。由于A/B/C/D维度均来自政策文本工程后的省—年聚合结果，当前稿件更适合将其解释为制度表达与治理重心重分布的证据线索，而不是与主识别并列的独立因果机制识别。")

    set_paragraph_text(sec56_p1, "本节并不引入新的主识别策略，而是围绕表4所报告的treat_share多期DID/TWFE主结果，按“趋势风险—单一区域驱动—有限聚类推断”三个问题逐项防守，并同时明确其证据边界。正文叙述与附录D同步报告标准聚类结果、trend-adjusted DID和wild cluster bootstrap的关键数值。相较之下，stack DID、cohort ATT以及动态补充识别仅保留为边界诊断，不再承担正文中的主防守功能。")
    set_paragraph_text(sec561_p1, "鉴于前文事件研究中的领先项并非完全平稳，本文在正式主规格之外进一步加入省份线性时间趋势，对主结果进行趋势调整型DID检验。该检验保持正式主面板、处理变量、控制变量、地区固定效应和年份固定效应不变，仅额外控制省级线性趋势，因此其作用在于回应“省际异质趋势可能影响主结果”的识别顾虑，而不是替代表4中的主识别框架。趋势调整后的结果表明，采购阶段占比下降这一核心结果仍保持显著负向：proc_share的系数为-0.3521，p = 0.0485；执行阶段占比上升在方向上保持一致，但统计强度明显减弱，exec_share的系数为0.2263，p = 0.1945；综合治理质量口径在趋势调整后转为负向且p = 0.6780，更不能被提升为稳健主结论。")
    set_paragraph_text(sec563_heading, "5.6.3 Wild Cluster Bootstrap 与更保守推断边界")
    set_paragraph_text(sec563_p1, "考虑到正式基准样本的地区聚类数量有限，本文进一步采用更保守的wild cluster bootstrap作为小样本推断层面的补充说明。该部分不改变估计框架，也不改变结果方向判断，其作用只是检验在更严格的推断标准下，核心推进结构结论是否仍保留相同的方向层级。结果表明，执行阶段占比与采购阶段占比的方向与基准DID保持一致，但统计强度进一步减弱：exec_share的wild cluster bootstrap p值为0.0761，proc_share为0.1221，ppp_quality_zindex为0.2372。因此，这一层证据更适合作为边界说明，而不构成对主识别的额外强化。")
    set_paragraph_text(sec564_p1, "本文同时保留了stack DID、cohort ATT、动态补充识别、PSM-DID、DML和候选工具变量筛查，但这些方法的功能均限于边界诊断而非结论抬升。前两者主要用于观察核心结果是否对处理时点结构异常敏感；动态补充识别只用于提示前趋势风险是否仍需保留；PSM-DID在当前样本下结果敏感且部分口径出现方向反转，DML只提供方向一致而非稳定显著的高维稳健性线索，候选工具变量的一阶段也不足以支撑正式IV识别。正因如此，正文只保留其方法性说明，而不把它们抬升为主防守层。")

    set_paragraph_text(sec6_p1, "本文围绕政务服务数字化改革与PPP治理之间的关系，构建了一条由政策文本量化、省级面板估计和项目级扩展分析相衔接的研究路径。与将数字化改革简单写成“全面提升治理质量”的宽泛叙述不同，本文更关注改革首先改变了PPP治理中的哪一类具体环节。基于正式口径的省级主面板和treat_share多期DID/TWFE框架，本文得到三个层次分明且边界清晰的结论。")
    set_paragraph_text(sec6_p2, "第一，在基准TWFE规格下，改革暴露强度较高的地区更可能出现PPP项目推进结构的相对重组。exec_share与treat_share呈显著正相关，proc_share呈显著负相关；执行/采购对数比率的补充估计也给出同向信号。这意味着当前最稳固的证据并不是所有治理质量指标同步跃升，而是采购/准备环节与执行环节之间的阶段份额发生重新配置。")
    set_paragraph_text(sec6_p3, "第二，综合治理质量指标存在正向信号，但稳定性不足，不能承担全文主结论。无论在基准结果还是在补充检验中，ppp_quality_zindex都没有形成与推进结构结果同等稳固的统计支持。因此，本文只把这一结果理解为边际改善方向，而不把它提升为“治理质量全面提升”的强断言。与之相对应，事件研究结果只能用于说明动态路径和识别边界；趋势调整型DID与wild cluster bootstrap则进一步表明，采购阶段占比下降的防守性支撑强于执行阶段占比上升。")
    set_paragraph_text(sec6_p4, "第三，政策文本证据线索支持“接口优先、前端规范先行、部分机制成立”的判断，但不支持完整稳定的强中介链条。A维度所代表的数字治理接口与数据协同率先响应，前端规范和采购—执行治理维度存在局部传导，但严格中介检验并未成立。由于A/B/C/D维度与treat_share都来自政策文本工程，本文将其统一降格为制度表达与治理重心重分布的证据线索，而不再写作独立的强机制识别。")
    set_paragraph_text(sec6_p5, "趋势调整型DID与逐省剔除检验进一步说明，推进结构重组这一核心判断在方向上具有较强稳定性，其中采购阶段占比下降的防守性支撑更强，执行阶段占比上升则对趋势设定和样本扰动更为敏感；wild cluster bootstrap进一步提示，在有限聚类下两项主结果方向仍保留，但推断强度弱于标准聚类结果。也正因如此，本文不将当前结果解释为稳定、强因果的制度效应，而将其界定为过程性、方向性的条件关联证据。")

    appendix_a_heading = clone_paragraph(chapter_heading_tpl, "附录A 处理变量与样本流转补充说明")
    appendix_a_p1 = clone_paragraph(body_tpl, "本轮修订在正式V3主面板基础上补充提供了province-year层面的treat_share重构材料。根据当前仓库内可核实的正式源文件，当前处理变量口径可以概括为：post_t = 1[t >= 2016]，treat_share_{pt} = (1/N_{pt}) × Σ_i treat_i，did_intensity_{pt} = post_t × treat_share_{pt}，did_any_{pt} = 1(did_intensity_{pt} > 0)。多数进入处理的省份首次处理年份为2016年，西藏为2017年；海南、青海和新疆生产建设兵团在当前口径下未进入处理。")
    appendix_a_p2 = clone_paragraph(body_tpl, "正式V3主面板共有266个省—年观察值，其中262个进入第5.3节正式估计样本，另外4个新疆生产建设兵团观测因基准控制变量不完整而被排除。本轮交付随附appendix_A_treat_share_reconstruction_20260419.csv、appendix_A_province_treatment_timing_20260419.csv、appendix_A_sample_exclusions_20260419.csv和appendix_A_treat_share_definition_tables_20260419.md，分别报告province-year层面的treat_share重构结果、省份首次处理时点、删样清单和处理变量定义表。由于当前仓库未显式保存城市级处理名单与原始阈值表，本文只能将这些材料界定为省级重构意义上的复核资产，而不将其写成完整城市级复现包。")
    appendix_b_heading = clone_paragraph(chapter_heading_tpl, "附录B 对数比率补充估计说明")
    appendix_b_p1 = clone_paragraph(body_tpl, "为回应份额型结果变量的构成性约束，本轮修订在正式估计样本上新增报告执行/采购对数比率指标log((exec_share+c)/(proc_share+c))。基准补充估计以执行阶段与采购阶段最小正份额的一半作为连续性修正，即c = 0.0033557047；在与表4一致的地区固定效应、年份固定效应、省级聚类和控制变量设定下，treat_share对应的估计系数为3.1916，标准误为1.4500，正态近似p = 0.0277。将c改为最小正份额、0.01和0.001后，系数方向均保持为正。")
    appendix_b_p2 = clone_paragraph(body_tpl, "这组结果的作用在于为主文中的结构重组判断提供构成性补强，而不是替代treat_share多期DID/TWFE作为唯一主识别。对应的fresh re-estimate结果已随本轮交付材料写入appendix_B_log_ratio_reestimate_20260419.csv和appendix_B_log_ratio_note_20260419.md。")
    appendix_c_heading = clone_paragraph(chapter_heading_tpl, "附录C 文本池与样本流转一致性说明")
    appendix_c_p1 = clone_paragraph(body_tpl, "本轮统一采用以下样本流转口径：1472份政策文本全文池，经正式筛选形成1307份DID文本文档样本，进一步聚合为288个省—年文本单元，再与正式V3主面板对接形成266个省—年观测值，其中262个进入主回归样本。这一链条已直接写入appendix_C_sample_flow_20260419.csv。")
    appendix_c_p2 = clone_paragraph(body_tpl, "审稿报告指出旧附表链条中曾出现“全量政策文本池165”的表述。基于当前仓库可核实的正式源文件，本轮未发现可以支持“165 = 全量文本池”这一manuscript-facing口径的现行资产，因此v1e不采纳该写法，而统一维持1472→1307→288→266→262的正式链条。")
    appendix_d_heading = clone_paragraph(chapter_heading_tpl, "附录D 主识别防守结果摘要")
    appendix_d_p1 = clone_paragraph(body_tpl, "主识别防守结果可概括为三点。第一，trend-adjusted DID下，exec_share的系数为0.2263（p = 0.1945），proc_share的系数为-0.3521（p = 0.0485），ppp_quality_zindex的系数为-0.1699（p = 0.6780）；这说明采购阶段占比下降的防守性支撑强于执行阶段占比上升。第二，wild cluster bootstrap下，exec_share、proc_share和ppp_quality_zindex的p值分别为0.0761、0.1221和0.2372，方向判断保留，但更保守推断下的统计强度明显减弱。第三，逐省剔除结果未出现核心系数符号翻转，但强度对样本扰动仍有敏感性。")
    appendix_d_p2 = clone_paragraph(body_tpl, "需要说明的是，本轮fresh baseline rerun与log-ratio rerun已经在机器精度上对齐正式5.3结果，但趋势调整型DID的手工复算尚未与既有bundle数值完全重合，因此正文仍保留当前项目中已经落地的正式bundle值，并把本轮手工趋势调整型结果仅作为diagnostic artifact随附在fresh_rerun_main_results_20260419.csv和fresh_rerun_summary_20260419.md中，不覆写manuscript-facing数字。")
    appendix_e_heading = clone_paragraph(chapter_heading_tpl, "附录E 处理变量与文本证据线索的来源边界")
    appendix_e_p1 = clone_paragraph(body_tpl, "treat_share由城市处理状态聚合到省—年层面，A/B/C/D维度则来自政策文本工程后的省—年聚合指标。两类变量都以政策文本体系为基础，因此它们之间的相关性不能被直接写成彼此独立的“机制识别”。本轮据此将第5.4节统一改写为“政策文本证据线索与阶段性传导”，其作用是说明制度表达和治理重心如何随改革推进而调整，而不是证明一条与主识别并列、来源完全独立的强机制链条。")
    appendix_e_p2 = clone_paragraph(body_tpl, "项目级机器学习结果同样必须与主识别保持层级边界。它们可以服务于高风险项目筛查、前端预警和资源配置，但不能被写成对省级主识别的因果强化，更不能替代制度治理。")
    trans_insert = clone_paragraph(body_tpl, "本轮v1e修订新增执行了一轮fresh reconstruction / rerun：appendix_C_sample_flow_20260419.csv直接复核了1472→1307→288→266→262的样本流转，appendix_A_*文件复核了treat_share的province-year重构、处理时点与4条删样记录，fresh_rerun_main_results_20260419.csv复算了基准treat_share DID，appendix_B_log_ratio_reestimate_20260419.csv复算了对数比率补充估计。其中，基准5.3结果与正式长表在机器精度上对齐；对数比率补充估计也与此前已落地的补充结果对齐。同时必须说明blocker：当前仓库仍未显式落地城市级处理名单、原始阈值表和可直接一键复算wild cluster bootstrap的完整运行环境；趋势调整型DID的手工复算方向一致，但未与既有正式bundle数值完全重合。")

    for new_p in [
        appendix_a_heading,
        appendix_a_p1,
        appendix_a_p2,
        appendix_b_heading,
        appendix_b_p1,
        appendix_b_p2,
        appendix_c_heading,
        appendix_c_p1,
        appendix_c_p2,
        appendix_d_heading,
        appendix_d_p1,
        appendix_d_p2,
        appendix_e_heading,
        appendix_e_p1,
        appendix_e_p2,
    ]:
        insert_before(body, transparency_heading, new_p)
    insert_before(body, trans_p2, trans_insert)

    xml_bytes = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    serialize_docx(SOURCE_DOCX, xml_bytes, OUTPUT_DOCX)

    OUTPUT_LOG.write_text(
        "\n".join(
            [
                "# v1e 对象保留 DOCX 生成日志",
                "",
                f"- source_docx: `{SOURCE_DOCX}`",
                f"- output_docx: `{OUTPUT_DOCX}`",
                "- method: copied the full source package and replaced only `word/document.xml`.",
                "- major_updates: subtitle, abstract, 4.1 sample flow, 4.3 treat_share definition, 4.4 identification boundary, 5.2 log-ratio reinforcement, 5.4 heading/body reframing, 5.6 defensive wording, conclusion tightening, appendix A-E insertion, transparency rerun note insertion.",
                f"- source_sha256: `{sha256(SOURCE_DOCX)}`",
                f"- output_sha256: `{sha256(OUTPUT_DOCX)}`",
                f"- source_media: `{media_counts(SOURCE_DOCX)}`",
                f"- output_media: `{media_counts(OUTPUT_DOCX)}`",
            ]
        ),
        encoding="utf-8",
    )

    print(f"OUTPUT_DOCX={OUTPUT_DOCX}")
    print(f"OUTPUT_LOG={OUTPUT_LOG}")


if __name__ == "__main__":
    main()



