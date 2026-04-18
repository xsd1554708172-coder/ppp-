from __future__ import annotations

import copy
import hashlib
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


ROOT = Path(__file__).resolve().parents[3]
INTEGRATION_DIR = Path(__file__).resolve().parents[1]
SOURCE_DOCX = ROOT / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260417_对象保留版.docx"
OUTPUT_DOCX_ROOT = ROOT / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx"
OUTPUT_DOCX_INTEGRATION = (
    INTEGRATION_DIR / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx"
)
OUTPUT_LOG = INTEGRATION_DIR / "INTEGRATION_LOG_OBJECT_PRESERVING_20260418.md"


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


def find_para_startswith(body: ET.Element, prefix: str) -> ET.Element:
    for p, text in iter_top_level_paragraphs(body):
        if text.startswith(prefix):
            return p
    raise KeyError(prefix)


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


def remove_child(body: ET.Element, elem: ET.Element) -> None:
    body.remove(elem)


def count_top_level_tables(body: ET.Element) -> int:
    return sum(1 for child in top_level_children(body) if child.tag == qn("tbl"))


def count_drawing_paragraphs(body: ET.Element) -> int:
    return sum(
        1
        for child in top_level_children(body)
        if child.tag == qn("p") and child.find(".//w:drawing", NS) is not None
    )


def serialize_to_outputs(source_docx: Path, document_xml: bytes) -> None:
    with zipfile.ZipFile(source_docx, "r") as src:
        items = [(info, src.read(info.filename)) for info in src.infolist()]

    for output in [OUTPUT_DOCX_ROOT, OUTPUT_DOCX_INTEGRATION]:
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as dst:
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


def main() -> None:
    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        document = ET.fromstring(zf.read("word/document.xml"))

    body = document.find("w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml 中缺少 body")

    chapter_heading_tpl = find_para_startswith(body, "2 文献综述")
    subsection_heading_tpl = find_para_startswith(body, "2.1 数字政府、政策执行与组织协同")
    body_tpl = find_para_startswith(body, "在公共服务供给方式持续调整的背景下")

    # Title and subtitle.
    set_paragraph_text(
        find_para_startswith(body, "政务服务数字化改革如何优化PPP项目推进与治理过程"),
        "政务服务数字化改革如何重塑PPP项目推进结构？",
    )
    set_paragraph_text(
        find_para_startswith(body, "——基于政策文本量化与省级面板评估的证据"),
        "——基于政策文本量化、省级面板与治理过程证据",
    )

    # Literature and positioning paragraphs with explicit citations.
    replacements = {
        "既有研究为理解这一问题提供了三方面基础，但仍存在明显空缺。第一，关于数字政府或数字治理改革的研究，更多关注营商环境、政务效率和企业行为等结果变量": "既有研究为理解这一问题提供了三方面基础，但仍存在明显空缺。第一，关于数字政府或数字治理改革的研究，更多关注营商环境、政务效率、信息披露和企业行为等结果变量，对改革如何通过制度接口重塑具体治理过程的讨论仍然有限（肖永慧，2025；边江泽等，2025）。第二，关于PPP治理的经验研究，已有工作已经注意到地方治理压力、财政约束、政策内容与项目推进之间的关系，但对“政府改革如何通过政策执行与流程重构影响PPP推进结构”的解释仍不充分（孙慧等，2024；汪峰等，2025）。第三，关于政策文本分析的研究，尽管主题识别、词典计量和机器学习方法已被广泛引入政策研究，但不少工作停留在主题展示或分类比较层面，尚未进一步完成“文本结果如何进入正式变量工程、如何服务于因果识别和治理解释”的闭环（曹玲静、张志强，2022；李牧南等，2024）。至于项目级机器学习识别，已有相关经验更多出现在金融舞弊或企业风险领域，直接移植到PPP并不自然，其适用边界也需要重新界定（范小云等，2022；范柏乃、盛中华，2024）。",
        "数字政府研究的一个基本判断是，信息基础设施和政务流程数字化并不会自动改变公共治理结果": "数字政府研究的一个基本判断是，信息基础设施和政务流程数字化并不会自动改变公共治理结果，但会首先改变政府内部的组织协同方式、程序透明程度和政策执行效率。已有文献围绕在线审批、数据共享、数字治理平台和制度接口重构等问题，揭示了数字化改革对部门协同、规则标准化和行政效率的影响路径。这类研究的重要贡献，在于把数字化改革理解为一类政府内部治理结构调整，而不是单纯技术升级。问题在于，现有讨论更多聚焦一般性行政效率、营商环境或企业端结果，对PPP这类跨部门、跨阶段且强依赖前端审查与执行衔接的治理场景，仍缺少足够细致的经验证据（肖永慧，2025；边江泽等，2025）。",
        "进一步看，制度冲击型改革的经验研究表明，规则重塑和信息披露安排的改变往往先改善信息质量、组织环境与行为约束": "进一步看，制度冲击型改革的经验研究表明，规则重塑和信息披露安排的改变往往先改善信息质量、组织环境与行为约束，再经由这些过程性变化影响终端绩效；关于政策系统“变与稳”的讨论也提示，不同治理环节对改革的响应并不同步，前端流程、制度接口和披露机制常常早于综合绩效指标发生变化（王渊等，2025；廖燕珠、莫桂芳，2025）。由此出发，数字化改革在PPP场景下更值得优先考察的，不是所有质量口径是否同步跃升，而是项目推进链条是否首先出现可观测的结构重组。",
        "围绕PPP的研究，已有工作分别从财政压力、政绩激励、项目筛选、合同治理和风险约束等角度讨论了地方政府行为及其后果": "围绕PPP的研究，已有工作分别从财政压力、政绩激励、项目筛选、合同治理和风险约束等角度讨论了地方政府行为及其后果。相关研究已经指出，PPP项目推进并非单一市场行为，而是政府部门之间协调、评估、采购、签约和执行共同作用的结果。特别是在公共服务供给语境下，PPP项目所处阶段不仅反映项目生命周期位置，也在相当程度上反映地方政府治理能力和程序执行状态。已有经验研究对项目推进速度、签约率、实施率及其影响因素提供了不少识别，但关于“数字化政务服务改革如何通过改变政府流程和前端规范影响PPP推进结构”的研究仍然不足（孙慧等，2024；汪峰等，2025）。",
        "近期关于PPP政策内容、市场反应与项目进程的研究进一步说明，PPP项目并非单纯的资本投入单元": "近期关于PPP政策内容、市场反应与项目进程的研究进一步说明，PPP项目并非单纯的资本投入单元，而是制度供给、政策约束、市场预期和项目执行共同作用的治理对象。无论是规范性政策文本对市场信号的影响，还是经济增长目标对项目推进节奏的牵引，都表明项目阶段转换本身具有清晰的公共管理含义（孙慧等，2024；汪峰等，2025）。正因为如此，执行阶段占比和采购阶段占比并不是单纯的生命周期统计，而是地方政府治理能力和政策执行状态的外在窗口。",
        "政策文本量化方法已经从传统的词频和词典统计，扩展到主题模型、深度学习分类和嵌入式语义表示": "政策文本量化方法已经从传统的词频和词典统计，扩展到主题模型、深度学习分类和嵌入式语义表示。相关文献已经证明，政策文本不仅可以揭示政策议题结构，还可以在一定条件下进入制度测度和治理研究。但在实际应用中，文本分析常常停留在主题展示或方法比较层面，未能完成从“文本发现”到“正式变量工程”的过渡。尤其在公共管理研究中，如果文本分析不能与制度维度、样本层级和识别设计相对接，方法本身再复杂，也难以转化为稳定的实证证据（曹玲静、张志强，2022；李牧南等，2024）。",
        "从政策信息学、主题建模和自动编码的最新进展看，文本量化方法的真正价值不在于算法名称本身": "从政策信息学、主题建模和自动编码的最新进展看，文本量化方法的真正价值不在于算法名称本身，而在于能否把非结构化政策语义转化为可比较、可聚合、可进入正式识别框架的制度信息。就本文而言，BERTopic、词典扩展和自动编码都只是服务于治理维度识别和变量工程的工具，其方法层级从属于研究问题层级；如果不能与治理维度划分、样本层级组织和经验识别衔接，再复杂的文本处理也难以形成可信的公共管理证据（王蓝蓝、刘艳丽，2024；曹玲静、张志强，2022；李牧南等，2024）。",
        "机器学习和预测模型已经广泛进入风险治理、合规监管和异常识别等研究领域": "机器学习和预测模型已经广泛进入风险治理、合规监管和异常识别等研究领域。在金融、会计和舆情研究中，这类方法往往能够较好地完成分类或排序任务。然而，从公共管理研究的角度看，预测能力并不等于制度解释能力，更不等于治理替代。尤其在PPP场景下，如果风险标签与文本特征定义交叉不清，模型很容易因为标签泄漏而获得看似优异但并不可靠的结果。因此，项目级机器学习分析的关键不在于模型堆叠得多复杂，而在于是否清楚划定标签边界、特征边界以及预测与因果之间的界限（范柏乃、盛中华，2024；范小云等，2022；刘敏等，2025）。",
        "风险治理研究与多源文本研究同时提示，排序能力、预警能力与制度解释能力并不处于同一层次": "风险治理研究与多源文本研究同时提示，排序能力、预警能力与制度解释能力并不处于同一层次。项目级模型即便能够较好地区分高低风险项目，也更多体现为前端筛查和资源配置上的治理辅助价值，而不能被直接转译为制度因果识别（范柏乃、盛中华，2024；范小云等，2022；刘敏等，2025）。对本文而言，这一区分尤为关键：项目级扩展分析的意义在于补充公共治理工具箱，而不在于重写省级面板上的主识别结论。",
        "已有关于PPP项目进程和政策内容的研究表明，前端规范供给、政府目标牵引和项目入库规则往往会优先改变项目在不同阶段之间的转换速度": "已有关于PPP项目进程和政策内容的研究表明，前端规范供给、政府目标牵引和项目入库规则往往会优先改变项目在不同阶段之间的转换速度，而不必然立即改善所有质量指标（孙慧等，2024；汪峰等，2025）。换言之，数字化改革若通过提升协同效率、压缩程序摩擦和规范准入条件发挥作用，那么最早可见的经验结果更可能是采购、准备与执行阶段之间的结构重组，而不是综合治理质量的同步跃升。",
        "从风险治理与多源文本研究的视角看，项目级模型的合理定位并不是替代制度识别": "从风险治理与多源文本研究的视角看，项目级模型的合理定位并不是替代制度识别，而是在既有治理框架之内提高前端筛查与风险排序效率（范柏乃、盛中华，2024；范小云等，2022；刘敏等，2025）。也正因如此，本文将第5.7节置于主识别之后：其任务不是重新解释前文的因果结果，而是考察文本与结构变量在项目层面能否转化为具有现实操作性的辅助识别工具。",
    }
    for prefix, new_text in replacements.items():
        set_paragraph_text(find_para_startswith(body, prefix), new_text)

    # 4.4 model section upgrade.
    p_44_1 = find_para_startswith(body, "本文的主识别模型是以treat_share为核心处理变量的多期DID/TWFE模型。形式上，模型以省级结果变量为被解释变量")
    p_44_2 = find_para_startswith(body, "需要强调的是，本文对识别强度的处理是克制的。首先，本文并不把事件研究结果写成“前趋势风险已被充分排除”的强证据")
    p_44_3 = find_para_startswith(body, "从公共管理研究的角度看，这样的识别安排意味着本文并不试图用更复杂的方法覆盖一切疑问")
    p_44_4 = find_para_startswith(body, "从制度冲击型改革的经验研究看，识别的关键不在于为每一项改革寻找单独政策文本冲击")
    p_ch5 = find_para_startswith(body, "5 实证结果与分析")

    set_paragraph_text(
        p_44_1,
        "本文的主识别模型是以treat_share为核心处理变量的多期DID/TWFE模型。形式上，本文估计的核心方程可以写为：",
    )
    eq_para = clone_paragraph(body_tpl, "Y_pt = β TreatShare_pt + γ'X_pt + μ_p + λ_t + ε_pt")
    eq_note_para = clone_paragraph(
        body_tpl,
        "其中，Y_pt分别表示exec_share、proc_share和ppp_quality_zindex等省级结果变量；TreatShare_pt表示省份p在年份t所对应的数字化改革处理强度；X_pt为正式主面板中统一口径的控制变量；μ_p和λ_t分别表示地区固定效应与年份固定效应；标准误在省级层面聚类。之所以将这一设定作为唯一主识别，原因有二：一是当前正式结果和写作总控文档都明确将treat_share多期DID/TWFE设定为全文唯一主模型；二是这一模型与本文“改革冲击—治理过程变化—推进结构调整”的问题结构最为契合。",
    )
    insert_after(body, p_44_1, eq_para)
    insert_after(body, eq_para, eq_note_para)
    set_paragraph_text(
        p_44_2,
        "这一模型的识别含义，并不是比较单一政策是否发生，而是在固定样本、统一控制变量和双向固定效应框架中，检验数字化改革强度变化是否伴随PPP推进结构和治理结果的系统性调整。换言之，本文关注的是省级层面平均结构效应，而不是将每一个动态系数都直接解释为同方向、同强度的改革释放路径。就当前样本而言，正式主面板覆盖2014—2022年、31个省级单元与新疆生产建设兵团，正式主识别样本为262个省—年观察值；后文所有主结果均以这一口径为基准锚点。",
    )
    set_paragraph_text(
        p_44_3,
        "需要强调的是，本文对识别强度的处理是克制的。考虑到错位处理时点下TWFE动态系数的解释存在额外边界，本文不把事件研究结果写成“平行趋势已经成立”的强证明，而只将其用于动态路径和识别边界说明（Sun & Abraham, 2021）。与此同时，趋势调整型DID、逐省剔除和wild cluster bootstrap只承担主识别防守功能；DML、PSM-DID、候选工具变量和其他替代估计则仅用于灵敏度检验和边界诊断，不改变主识别结构。",
    )
    set_paragraph_text(
        p_44_4,
        "从公共管理研究的角度看，这样的识别安排意味着本文并不试图用更复杂的方法覆盖一切疑问，而是将不同证据放在各自恰当的位置上：主识别回答“改革是否首先改善了推进结构”，机制检验回答“改革首先改动了哪些治理接口”，稳健性检验回答“主结果是否在更严格设定下仍可防守”，扩展分析回答“文本与结构变量是否还能服务于项目级辅助识别”。这种分层安排，构成了后文实证分析的基本结构。",
    )
    insert_before(
        body,
        p_ch5,
        clone_paragraph(
            body_tpl,
            "同时需要说明，机制与异质性部分主要依托当前项目归档中的既有正式辅助结果，其任务在于补充解释和提示适用边界，而不与表4主识别处于同一证据层级。本文因此不将这些结果写成第二套识别体系，而只在其能够支持的范围内作辅助性讨论。",
        ),
    )

    # 5.3 correction.
    set_paragraph_text(
        find_para_startswith(body, "从动态结果看，exec_share和proc_share在处理后呈现出与基准结果一致的方向"),
        "就正式动态长表而言，当前事件研究结果并不支持把这一部分写成与基准DID同向强化的动态展开。一方面，exec_share和proc_share在处理前<=-2窗口上的领先项已经显示出统计显著，这意味着处理组与对照组在政策启动之前并非完全平稳；另一方面，处理后各期系数存在明显波动，且若干时期的方向与表4中的平均效应并不一致。更稳妥的解释因此不是“执行逐步上升、采购相应下降”，而是“动态诊断揭示了平均结构效应之外仍存在时序不平稳和解释边界”。",
    )
    set_paragraph_text(
        find_para_startswith(body, "这一结论并不推翻基准结果，但它对写作口径提出了明确约束。第一，动态结果可以用来说明改革影响的时间路径"),
        "这一结论并不推翻基准结果，但它对写作口径提出了更严格的约束。第一，事件研究在本文中只能作为时序路径和识别边界的诊断工具，而不能被写成平行趋势成立或效应逐步释放的强证据。第二，对于错位处理时点下的TWFE事件研究，动态系数本身并不天然等同于无偏的处理效应路径，因此正文必须避免把个别时期系数直接外推为稳定的改革演进逻辑（Sun & Abraham, 2021）。第三，对ppp_quality_zindex而言，动态结果同样未形成稳定支持，因此更不能据此抬升为主结论。",
    )
    set_paragraph_text(
        find_para_startswith(body, "从公共管理含义上看，这一结果提示PPP治理结构的调整往往发生在制度改革推进过程中"),
        "从公共管理含义上看，这一结果提示制度启动时点、平均结构效应与分期动态系数不能被简单等同：改革可能确实改变了PPP推进结构，但这一变化未必表现为一条单调、平滑且与平均效应完全同向的动态轨迹。对本文而言，第5.3节的价值主要在于诚实呈现识别边界，并为后文更严格的防守性检验提供问题意识，而不是额外增强主结论。",
    )

    # 5.4 mechanism caution.
    set_paragraph_text(
        find_para_startswith(body, "在确认数字化改革首先改善PPP推进结构之后，进一步的问题是：这一变化主要通过哪些治理环节发生"),
        "在确认数字化改革首先改善PPP推进结构之后，进一步的问题是：这一变化主要通过哪些治理环节发生。根据第三部分提出的理论框架，这里的核心不是寻找一条完整闭合的强中介链条，而是判断改革是否优先作用于数字治理接口和前端规范环境，并是否存在阶段性传导。需要说明的是，本节主要依托当前项目归档中的正式辅助结果，用于补充解释而非与表4同层级的再识别，因此其解读必须更加克制。",
    )
    set_paragraph_text(
        find_para_startswith(body, "表5汇总了机制检验的核心结果。首先，treat_share对A维度指数的影响显著"),
        "表5汇总了机制检验的核心结果。首先，treat_share对A维度指数的影响显著，表明数字治理接口与数据协同确实是最先响应的治理环节，这与理论部分提出的“接口优先”判断一致。其次，B维度和C维度对应的文本治理表达也出现联动变化，说明前端准入、采购安排和执行衔接的制度重心随着改革推进而发生了重分布。需要注意的是，这里的经验含义应理解为治理表达结构变化和制度重心转移，而不宜机械理解为所有单项指标均线性改善。尤其对B维度而言，相关系数的方向含义必须结合指标定义解释，正文不宜直接把它翻译为“前端规范显著增强”，更稳妥的写法是“前端规范与准入表达发生显著调整”。再次，在结果方程中，A维度中介项对exec_share和proc_share的系数方向与理论预期大体一致，但统计上并不稳定；链式路径中，B_idx→C_idx和C_idx→D_idx两段显著，而A_idx→B_idx不显著；严格中介分解的Sobel检验和Bootstrap区间均未支持稳定中介效应。",
    )
    set_paragraph_text(
        find_para_startswith(body, "综合来看，当前机制证据更支持“接口优先、前端规范先行、局部链条成立”的判断"),
        "综合来看，当前机制证据更支持“接口优先、前端规范先行、局部链条成立”的判断，而不支持“完整稳定的强中介链条已经建立”。这一点需要明确写出。否则，机制部分很容易被误写成一个比数据更完整的故事。对本文而言，较为稳妥的表述应是：数字化改革首先改变了政府接口、数据协同和前端程序环境，并伴随采购—执行治理维度的阶段性响应；但这些变化主要体现为治理表达和制度重心的调整，而不是一条从前端到后端均稳定显著、方向单调的强中介链条。",
    )

    # 5.6 object-preserving rewrite.
    p_trend = find_para_startswith(body, "鉴于前文事件研究中的领先项并非完全平稳")
    p_fig8 = find_para_startswith(body, "图8 主识别防守型稳健性补充诊断图")
    p_delete_one = find_para_startswith(body, "为了判断主结果是否主要由个别地区驱动")
    p_fig9 = find_para_startswith(body, "图9 安慰剂分布图（补充诊断）")
    p_bootstrap_other = find_para_startswith(body, "考虑到正式基准样本的地区聚类数量有限，本文进一步采用更保守的 wild cluster bootstrap")
    p_57_heading = find_para_startswith(body, "5.7 项目级扩展分析：高低风险的辅助识别")

    insert_before(body, p_trend, clone_paragraph(subsection_heading_tpl, "5.6.1 趋势调整型防守检验"))
    set_paragraph_text(
        p_trend,
        "鉴于前文事件研究中的领先项并非完全平稳，本文在正式主规格之外进一步加入省份线性时间趋势，对主结果进行趋势调整型DID检验。该检验保持正式主面板、处理变量、控制变量、地区固定效应和年份固定效应不变，仅额外控制省级线性趋势，因此其作用在于回应“省际异质趋势可能影响主结果”的识别顾虑，而不是替代表4中的主识别框架。趋势调整后的结果表明，采购阶段占比下降这一核心结果仍保持显著负向，说明推进结构中的“采购向执行转换”并不完全依赖共同趋势设定；执行阶段占比上升在方向上保持一致，但统计强度明显减弱，表明这一判断更容易受到趋势设定影响；综合治理质量口径在趋势调整后仍未形成稳定支持，因此不能被提升为稳健主结论。就防守价值而言，采购阶段占比是三项结果中最强的一项，执行阶段占比主要体现为方向稳定但强度更敏感，综合治理质量口径则继续只能作为边界性结果处理。图8A与表8共同服务于这一层防守性说明。",
    )
    set_paragraph_text(
        p_fig8,
        "图8 主识别防守型补充诊断图：A. 趋势调整型DID与基准DID的结果比较；B. 逐省剔除诊断下核心结果的稳定性",
    )
    insert_after(body, p_fig8, clone_paragraph(subsection_heading_tpl, "5.6.2 单一地区驱动风险诊断：逐省剔除检验"))
    set_paragraph_text(
        p_delete_one,
        "为了判断主结果是否主要由个别地区驱动，本文进一步实施逐省剔除检验。在保持处理变量、控制变量、固定效应和聚类口径不变的前提下，依次删除单个省份并重新估计主规格，以观察核心系数的方向是否翻转，以及统计强度是否对个别地区存在明显敏感性。结果显示，执行阶段占比与采购阶段占比在删除任一单一省份后均未发生符号翻转，这意味着推进结构改善这一核心判断并非由单一地区机械驱动；与此同时，两项结果的统计强度对个别地区仍存在一定敏感性，因此更稳妥的写法应是“方向稳定，但强度仍受样本扰动影响”，而不是“完全不受地区结构影响”。相较之下，综合治理质量口径的波动更大，因而更不宜承担稳健主发现。图8B与表8共同承担这一诊断功能。",
    )
    insert_before(body, p_fig9, clone_paragraph(subsection_heading_tpl, "5.6.3 更保守推断下的边界说明"))
    insert_before(
        body,
        p_fig9,
        clone_paragraph(
            body_tpl,
            "考虑到正式基准样本的地区聚类数量有限，本文进一步采用更保守的wild cluster bootstrap作为小样本推断层面的补充说明。该部分不改变估计框架，也不改变结果方向判断，其作用只是检验在更严格的推断标准下，核心推进结构结论是否仍保留相同的方向层级。结果表明，执行阶段占比与采购阶段占比的方向与基准DID保持一致，但统计强度进一步减弱；综合治理质量口径仍未获得稳定支持。因而，这一层证据更适合作为边界说明，而不构成对主识别的额外强化。",
        ),
    )
    set_paragraph_text(p_bootstrap_other, "5.6.4 其他补充识别结果（简述）")
    insert_after(
        body,
        p_bootstrap_other,
        clone_paragraph(
            body_tpl,
            "本文同时保留了stack DID、cohort ATT、动态补充识别、PSM-DID、DML和候选工具变量筛查，但这些方法的功能均限于边界诊断而非结论抬升。前两者主要用于观察核心结果是否对处理时点结构异常敏感；动态补充识别只用于提示前趋势风险是否仍需保留；PSM-DID在当前样本下结果敏感且部分口径出现方向反转，DML只提供方向一致而非稳定显著的高维稳健性线索，候选工具变量的一阶段也不足以支撑正式IV识别。正因如此，正文只保留其方法性说明，而不把它们抬升为主防守层，更不将其写成对表4主结果的额外强化。",
        ),
    )

    # 5.7 fix merged paragraph and typo.
    p_57_boundary = find_para_startswith(body, "这里需要坚持两条边界。第一，表9展示的是排序和识别能力")
    p_57_tail = find_para_startswith(body, "潜力，而不是改变全文主线。")
    set_paragraph_text(
        p_57_boundary,
        "这里需要坚持两条边界。第一，表9展示的是排序和识别能力，而不是制度因果效应，因此不能与前文的多期DID/TWFE结论混写。第二，模型性能略高并不意味着某种算法已经替代治理判断。对公共管理研究而言，这一部分更合理的定位是治理辅助工具：它可以帮助识别需要重点关注的项目，但无法替代前端规范、审批约束和跨部门协同本身。也正因为如此，本文将第5.7节压缩为扩展分析而非全文压轴，其作用是补充说明文本和结构变量在项目层面的应用潜力，而不是改变全文主线。",
    )
    remove_child(body, p_57_tail)

    # Transparency section before references.
    p_refs = find_para_startswith(body, "参考文献")
    transparency_heading = clone_paragraph(chapter_heading_tpl, "研究透明度与复现说明")
    transparency_p1 = clone_paragraph(
        body_tpl,
        "本文使用的政策文本、PPP项目资料以及省级统计/行政数据均来自公开政策文件、正式数据库和可复核的省级公开资料。受原始平台抓取规则、版权限制和整理流程约束，原始底库不随本文同步公开；在不违反平台规则的前提下，作者可提供经清洗后的省级主面板、核心变量说明、文本维度映射表和表图复核清单，以供匿名评审和后续复核使用。",
    )
    transparency_p2 = clone_paragraph(
        body_tpl,
        "本文的主要复现材料包括文本变量构造说明、主面板变量字典、基准DID/TWFE回归脚本、DID防守性补强脚本以及结果汇总表。考虑到部分原始数据存在平台访问限制，代码和派生数据将在匿名评审结束后按期刊政策和合理申请原则提供。",
    )
    transparency_p3 = clone_paragraph(
        body_tpl,
        "本研究不涉及对人类受试者的干预性实验，也不处理可识别的个人隐私数据，因而不属于需要单独伦理审批的研究类型。本文在文稿结构整理、语言润饰和一致性核对环节使用了生成式人工智能工具辅助，但研究设计、数据构建、实证估计、结果复核与全部学术责任均由作者承担。",
    )
    insert_before(body, p_refs, transparency_heading)
    insert_after(body, transparency_heading, transparency_p1)
    insert_after(body, transparency_p1, transparency_p2)
    insert_after(body, transparency_p2, transparency_p3)

    # Reference cleanup.
    set_paragraph_text(
        find_para_startswith(body, "7. 王蓝蓝, 刘艳丽. 2024. 基于BERTopic的计算机视觉领域热点技术主题及演化分析."),
        "7. 王蓝蓝, 刘艳丽. 2024. 基于BERTopic的计算机视觉领域热点技术主题及演化分析. 科学观察, 19(2). DOI: 10.15978/j.cnki.1673-5668.202402005.",
    )
    set_paragraph_text(
        find_para_startswith(body, "8. 曹玲静, 张志强. 政策信息学视角下政策文本量化方法研究进展."),
        "8. 曹玲静, 张志强. 2022. 政策信息学视角下政策文本量化方法研究进展. DOI: 10.11968/tsyqb.1003-6938.2022087.",
    )
    set_paragraph_text(
        find_para_startswith(body, "12. 李牧南等. 2024. 基于深度学习的我国科技政策属性识别."),
        "12. 李牧南, 王亮, 赖华鹏. 2024. 基于深度学习的我国科技政策属性识别. 科研管理, 45(2). DOI: 10.19571/j.cnki.1000-2995.2024.02.001.",
    )

    top_tables = count_top_level_tables(body)
    top_drawings = count_drawing_paragraphs(body)
    document_xml = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    serialize_to_outputs(SOURCE_DOCX, document_xml)

    digest = sha256(OUTPUT_DOCX_ROOT)
    OUTPUT_LOG.write_text(
        "\n".join(
            [
                "# 2026-04-18 对象保留投稿版回填说明",
                "",
                f"- 模板来源：`{SOURCE_DOCX}`",
                f"- 输出文件：`{OUTPUT_DOCX_ROOT}`",
                f"- 同步副本：`{OUTPUT_DOCX_INTEGRATION}`",
                "- 保留对象：原对象保留版中的顶层表格对象与图形段落对象。",
                "- 关键回填：标题、副标题、引言与文献综述引文嵌入、4.4 模型正式化、5.3 动态边界修正、5.4 机制表述收紧、5.6 四层主识别防守结构、5.7 边界修正、研究透明度说明、参考文献补齐。",
                f"- 顶层表格对象数：{top_tables}",
                f"- 顶层图形段落对象数：{top_drawings}",
                f"- SHA256：`{digest}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"ROOT_DOCX={OUTPUT_DOCX_ROOT}")
    print(f"INTEGRATION_DOCX={OUTPUT_DOCX_INTEGRATION}")
    print(f"LOG={OUTPUT_LOG}")
    print(f"TOP_LEVEL_TABLES={top_tables}")
    print(f"TOP_LEVEL_DRAWING_PARAS={top_drawings}")
    print(f"SHA256={digest}")


if __name__ == "__main__":
    main()
