from __future__ import annotations

import copy
import hashlib
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_DOCX = Path(
    r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx"
)
OUTPUT_DOCX = SCRIPT_DIR / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx"
OUTPUT_LOG = SCRIPT_DIR / "docx_generation_log_20260418.md"


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


def insert_after(body: ET.Element, ref: ET.Element, new_p: ET.Element) -> None:
    idx = top_level_children(body).index(ref)
    body.insert(idx + 1, new_p)


def insert_before(body: ET.Element, ref: ET.Element, new_p: ET.Element) -> None:
    idx = top_level_children(body).index(ref)
    body.insert(idx, new_p)


def count_top_level_tables(body: ET.Element) -> int:
    return sum(1 for child in top_level_children(body) if child.tag == qn("tbl"))


def count_drawing_paragraphs(body: ET.Element) -> int:
    return sum(
        1
        for child in top_level_children(body)
        if child.tag == qn("p") and child.find(".//w:drawing", NS) is not None
    )


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


def main() -> None:
    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        document = ET.fromstring(zf.read("word/document.xml"))

    body = document.find("w:body", NS)
    if body is None:
        raise RuntimeError("word/document.xml 中缺少 body")

    chapter_heading_tpl = find_para_startswith(body, "2 文献综述")
    body_tpl = find_para_startswith(body, "在公共服务供给方式持续调整的背景下")

    title_p = find_para_startswith(body, "政务服务数字化改革如何重塑PPP项目推进结构")
    subtitle_p = find_para_startswith(body, "——基于政策文本量化、省级面板与治理过程证据")
    abstract_p = find_para_startswith(body, "围绕政务服务数字化改革与PPP治理之间的关系")
    keywords_p = find_para_startswith(body, "关键词：数字政府")
    intro_method_p = find_para_startswith(body, "本文尝试在上述交叉地带推进一步")
    intro_results_p = find_para_startswith(body, "本文的经验结果表明")
    h1_p = find_para_startswith(body, "假说H1：")
    h2_p = find_para_startswith(body, "假说H2：")
    treat_share_p = find_para_startswith(body, "在主识别部分，本文的核心处理变量是treat_share")
    table4_p = find_para_startswith(body, "表4报告了基准多期DID/TWFE结果")
    baseline_meaning_p = find_para_startswith(body, "基准结果对公共管理研究的含义在于")
    mech_open_p = find_para_startswith(body, "在确认数字化改革首先改善PPP推进结构之后")
    mech_close_p = find_para_startswith(body, "从公共管理角度看，这一结果的含义在于")
    conclusion_open_p = find_para_startswith(body, "本文围绕政务服务数字化改革与PPP治理之间的关系")
    conclusion_first_p = find_para_startswith(body, "第一，数字化改革最稳定的作用首先体现为")
    conclusion_boundary_p = find_para_startswith(body, "趋势调整型 DID 与逐省剔除检验进一步说明")
    transparency_heading = find_para_startswith(body, "研究透明度与复现说明")

    set_paragraph_text(subtitle_p, "——基于政策文本量化、省级面板与治理过程的条件关联证据")
    set_paragraph_text(
        abstract_p,
        "围绕政务服务数字化改革与PPP治理之间的关系，本文聚焦一个更具公共管理含义而非纯技术含义的问题：数字化改革究竟首先改变了PPP治理链条中的哪类环节。基于地方政府PPP政策文本、统一口径的省级主面板以及项目级风险底表，本文将政策文本量化结果转化为治理能力测度变量，并以treat_share为核心处理变量，在地区和年份固定效应框架下估计政务服务数字化改革暴露强度与PPP项目推进结构、治理表现之间的平均条件关联。结果显示，在基准TWFE规格下，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组：执行阶段占比与treat_share呈正向关联，采购阶段占比呈负向关联；在正式估计样本上补充构造的执行/采购对数比率指标也给出同向支持。相比之下，综合治理质量指标ppp_quality_zindex虽呈正向变化，但统计上不够稳定，不能承担全文主结论。机制分析表明，改革更可能优先作用于数字治理接口、数据协同和前端规范准入等环节，并伴随采购—执行治理维度的阶段性响应，但完整稳定的强中介链条并未建立。进一步的趋势调整型检验和逐省剔除诊断表明，采购阶段占比下降在更严格设定下仍相对稳健，执行阶段占比上升主要体现为方向保持一致但统计强度有所减弱；事件研究与更保守的小样本推断则提示，这一关系在动态持续性和统计强度上仍需谨慎解释。在严格避免标签泄漏的前提下，项目级高低风险具有中等偏强的可识别性，但这一部分仅构成治理辅助识别的扩展分析，不改变本文以多期DID/TWFE为唯一主识别的研究结构。本文据此将数字化改革在PPP领域的经验结果界定为过程性、方向性的条件关联证据：其更接近于改善政府内部协同、前端规范和审批执行衔接，而非即时、全面地提升所有治理质量指标。",
    )
    set_paragraph_text(keywords_p, "关键词：数字政府；政务服务数字化改革；PPP治理；政策文本量化；推进结构重组；治理辅助识别")
    set_paragraph_text(
        intro_method_p,
        "本文尝试在上述交叉地带推进一步。基于正式口径的PPP政策文本、省级面板和项目级风险底表，本文首先将政策文本分析结果组织为A、B、C、D四类治理维度，并在文档级、省—年级和主面板之间完成统一映射，用以支撑治理能力测度和机制解释；随后，以treat_share为核心处理变量，在地区和年份固定效应框架下考察数字化改革暴露强度与PPP项目推进结构重组之间的平均条件关联；在此基础上，再对机制、异质性、稳健性和项目级扩展分析进行分层检验。本文并不试图将文本分析或机器学习写成主识别模型，也不把所有质量型指标的同步改善预设为既定结论，而是将研究重心放在一个更符合当前证据边界的问题上：数字化改革是否首先与PPP项目的推进结构重组和治理过程调整相关联。",
    )
    set_paragraph_text(
        intro_results_p,
        "本文的经验结果显示，在基准双向固定效应规格下，treat_share与exec_share呈显著正向关联、与proc_share呈显著负向关联，对数比率补充估计也给出同向信号。这意味着当前最稳固的证据首先体现为PPP推进结构的相对重组，而不是所有治理质量指标的同步跃升。相比之下，综合治理质量指标ppp_quality_zindex虽然方向为正，但统计上不够稳定，不能被写成全文主结论。机制分析进一步表明，改革更可能优先作用于数字治理接口和前端规范环节，采购—执行治理维度存在阶段性响应，但严格中介并未成立。相较于将数字政府研究停留在一般行政效率结果、将PPP研究停留在投资安排或财政约束解释、将文本分析停留在方法展示，本文的边际贡献在于把数字化改革、项目推进结构与文本变量工程纳入同一公共管理分析框架，并在严格区分主识别、防守性稳健性与扩展分析的前提下组织证据层级。项目级高低风险识别结果则显示，在严格避免标签泄漏的前提下，文本与结构变量可以服务于风险排序任务，但这一部分属于扩展分析，不构成对主识别的替代。",
    )
    set_paragraph_text(h1_p, "假说H1：政务服务数字化改革暴露强度越高，PPP项目推进结构由采购/准备阶段向执行阶段发生相对份额重组的程度越高。")
    set_paragraph_text(h2_p, "假说H2：政务服务数字化改革暴露强度越高，数字治理接口与前端规范准入相关的治理环境越可能率先响应，并通过阶段性传导与PPP项目推进结构重组相关联，但完整、稳定的强中介链条未必成立。")
    set_paragraph_text(
        treat_share_p,
        "在主识别部分，本文的核心处理变量是treat_share。该变量以省—年为单位，由城市—年处理字段聚合而成，精确定义为treat_share_{pt} = treated_city_count_{pt} / city_n = (1/N_{pt}) × Σ_i treat_i，用于度量某一省份在某一年份受到数字化改革覆盖的处理强度。与之对应，post_t = 1[t>=2016]，did_intensity_{pt} = post_t × treat_share_{pt}，did_any_{pt} = 1(did_intensity_{pt} > 0)；后两者仅作为替代处理口径或稳健性检验使用，不进入全文主结论。这样处理的原因在于，treat_share能够更直接地反映改革在省级治理层面的覆盖程度和处理强度，也与后文多期DID/TWFE主识别保持一致。",
    )
    insert_after(
        body,
        treat_share_p,
        clone_paragraph(
            body_tpl,
            "根据第5.1节并表工作簿中的“省份处理时点”工作表，当前口径下多数进入处理的省份首次处理年份为2016年，西藏为2017年；海南、青海和新疆生产建设兵团在当前口径下未进入处理。正式V3主面板共有266个省—年观察值，其中262个进入第5.3节正式估计样本，另有4个新疆生产建设兵团观测因基准控制变量不完整而被排除。本轮修订随附附录A，补充提供province-year层面的treat_share重构表、处理时点表、266→262删样清单以及处理变量精确定义，以增强当前稿件的可复核性；但城市级处理名单和原始阈值底表未在当前仓库显式落地，因此本文只能将这一部分说明为省级重构意义上的复核材料，而不夸大为完整城市级复现包。",
        ),
    )
    set_paragraph_text(
        table4_p,
        "表4报告了基准多期DID/TWFE结果。结果显示，在地区和年份固定效应框架下，treat_share对exec_share的估计系数为0.3556，在1%水平上显著；对proc_share的估计系数为-0.4023，同样在1%水平上显著。两者共同指向同一个结论：在基准TWFE规格下，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组。就当前证据边界而言，这一结果更适合被理解为过程性结构信号，而不是数字化改革已经对PPP治理产生全面、稳定因果改善的证明。",
    )
    insert_after(
        body,
        table4_p,
        clone_paragraph(
            body_tpl,
            "为回应份额型因变量的加总约束，本文进一步在与表4相同的262个正式估计观测上补充构造执行/采购对数比率指标log((exec_share+c)/(proc_share+c))。考虑到样本中存在零份额情形，本轮补充估计以执行阶段与采购阶段最小正份额的一半作为连续性修正，取c = 0.0034。在与表4一致的地区固定效应、年份固定效应、省级聚类和控制变量设定下，treat_share对该对数比率的估计系数为3.1916，标准误为1.4500，正态近似p = 0.0277。这一结果表明，改革暴露强度较高的地区更可能出现由采购阶段向执行阶段的相对份额重组；同时，将c改为最小正份额或固定值0.01、0.001后，系数方向均保持为正。鉴于该结果属于本轮新增补充估计，本文将其理解为构成性补强，而不是替代正式主规格的第二主模型。",
        ),
    )
    set_paragraph_text(
        baseline_meaning_p,
        "基准结果对公共管理研究的含义在于，数字化改革的现实作用更接近于改善政府内部流程衔接和项目推进程序，而非立即改变所有治理结果。与此同时，也必须保持边界控制：表4及对数比率补充估计共同支持的是推进结构和治理过程的平均条件关联，不支持将改革表述为“全面改善PPP治理质量”的强断言。",
    )
    set_paragraph_text(
        mech_open_p,
        "在确认数字化改革暴露强度与PPP推进结构重组存在稳定条件关联之后，进一步的问题是：这一变化主要通过哪些治理环节发生。根据第三部分提出的理论框架，这里的核心不是寻找一条完整闭合的强中介链条，而是判断改革是否优先作用于数字治理接口和前端规范环境，并是否存在阶段性传导。需要说明的是，本节主要依托当前项目归档中的正式辅助结果，用于补充解释而非与表4同层级的再识别，因此其解读必须更加克制。",
    )
    set_paragraph_text(
        mech_close_p,
        "从公共管理角度看，这一结果的含义在于，PPP治理过程的改善首先依赖制度接口和程序环境的调整，而非所有治理环节同步升级；从证据边界看，表5支持的是部分机制和阶段性传导，而不是完整闭合的机制证明。与此同时，由于A/B/C/D维度均来自政策文本的省—年聚合结果，当前稿件更适合将其解释为制度表达与治理重心的重分布证据，而不是与主识别并列的独立因果机制识别。",
    )
    set_paragraph_text(
        conclusion_open_p,
        "本文围绕政务服务数字化改革与PPP治理之间的关系，构建了一条由政策文本量化、省级面板估计和项目级扩展分析相衔接的研究路径。与将数字化改革简单写成“全面提升治理质量”的宽泛叙述不同，本文更关注改革首先改变了PPP治理中的哪一类具体环节。基于正式口径的省级主面板和treat_share多期DID/TWFE框架，本文得到三个层次分明的结论。",
    )
    set_paragraph_text(
        conclusion_first_p,
        "第一，在基准TWFE规格下，改革暴露强度较高的地区更可能出现PPP项目推进结构的相对重组。exec_share与treat_share呈显著正向关联，proc_share呈显著负向关联；执行/采购对数比率的补充估计也给出同向信号。这意味着当前最稳固的证据并不是所有治理质量指标同步跃升，而是采购/准备环节与执行环节之间的阶段份额发生重新配置。",
    )
    set_paragraph_text(
        conclusion_boundary_p,
        "趋势调整型DID与逐省剔除检验进一步说明，推进结构重组这一核心判断在方向上具有较强稳定性，其中采购阶段占比下降的防守性支撑更强，执行阶段占比上升则对趋势设定和样本扰动更为敏感；更保守的小样本推断及其他补充识别结果主要承担边界诊断功能，而不构成对主识别的替代或显著强化。也正因如此，本文不将当前结果解释为稳定、强因果的制度效应，而将其界定为过程性、方向性的条件关联证据。",
    )

    appendix_a_heading = clone_paragraph(chapter_heading_tpl, "附录A 处理变量与样本流转补充说明")
    appendix_a_p1 = clone_paragraph(
        body_tpl,
        "本轮修订在正式V3主面板基础上补充提供了province-year层面的treat_share重构材料。根据第5.1节并表工作簿中的“处理变量定义”“处理变量精确公式”和“省份处理时点”工作表，当前处理变量口径可以概括为：post_t = 1[t>=2016]，treat_share_{pt} = (1/N_{pt}) × Σ_i treat_i，did_intensity_{pt} = post_t × treat_share_{pt}，did_any_{pt} = 1(did_intensity_{pt} > 0)。多数进入处理的省份首次处理年份为2016年，西藏为2017年；海南、青海和新疆生产建设兵团在当前口径下未进入处理。",
    )
    appendix_a_p2 = clone_paragraph(
        body_tpl,
        "正式V3主面板共有266个省—年观察值，其中262个进入第5.3节正式估计样本，另外4个新疆生产建设兵团观测因基准控制变量不完整而被排除。本轮交付随附appendix_A_treat_share_reconstruction_20260418.csv、appendix_A_province_treatment_timing_20260418.csv、appendix_A_sample_exclusions_20260418.csv和appendix_A_treat_share_definition_tables_20260418.md，分别报告province-year层面的treat_share重构结果、省份首次处理时点、删样清单和处理变量定义表。由于当前仓库未显式保存城市级处理名单与原始阈值底表，本文只能将这些材料界定为省级重构意义上的复核资产，而不将其写成完整城市级复现包。",
    )
    appendix_b_heading = clone_paragraph(chapter_heading_tpl, "附录B 对数比率补充估计说明")
    appendix_b_p1 = clone_paragraph(
        body_tpl,
        "为回应份额型结果变量的构成性约束，本轮修订在正式估计样本上新增报告执行/采购对数比率指标log((exec_share+c)/(proc_share+c))。基准补充估计以执行阶段与采购阶段最小正份额的一半作为连续性修正，取c = 0.0033557047；在与表4一致的地区固定效应、年份固定效应、省级聚类和控制变量设定下，treat_share对应的估计系数为3.1916，标准误为1.4500，正态近似p = 0.0277。将c改为最小正份额、0.01和0.001后，系数方向均保持为正，说明“采购阶段向执行阶段的相对份额重组”这一判断并不完全依赖单一连续性修正规则。",
    )
    appendix_b_p2 = clone_paragraph(
        body_tpl,
        "这组结果的作用在于为主文中的结构重组判断提供构成性补强，而不是替代treat_share多期DID/TWFE作为唯一主识别。对应的fresh re-estimate结果已随本轮交付材料写入appendix_B_log_ratio_reestimate_20260418.csv和appendix_B_log_ratio_note_20260418.md，供匿名评审和后续人工复核使用。",
    )
    insert_before(body, transparency_heading, appendix_b_p2)
    insert_before(body, appendix_b_p2, appendix_b_p1)
    insert_before(body, appendix_b_p1, appendix_b_heading)
    insert_before(body, appendix_b_heading, appendix_a_p2)
    insert_before(body, appendix_a_p2, appendix_a_p1)
    insert_before(body, appendix_a_p1, appendix_a_heading)

    top_tables = count_top_level_tables(body)
    top_drawings = count_drawing_paragraphs(body)
    document_xml = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    serialize_docx(SOURCE_DOCX, document_xml, OUTPUT_DOCX)

    digest = sha256(OUTPUT_DOCX)
    OUTPUT_LOG.write_text(
        "\n".join(
            [
                "# v2c 对象保留版回填日志",
                "",
                f"- 模板来源：`{SOURCE_DOCX}`",
                f"- 输出文件：`{OUTPUT_DOCX}`",
                "- 回填内容：题目副标题、摘要、引言中的识别口径、H1/H2、4.3 处理变量说明、5.2 log-ratio 构成性补强、5.4 机制边界、6 结论收口、附录A/B。",
                "- 目标：保持表格对象与图形对象不变，只替换正文段落。",
                f"- 顶层表格对象数：{top_tables}",
                f"- 顶层图形段落对象数：{top_drawings}",
                f"- SHA256：`{digest}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"OUTPUT_DOCX={OUTPUT_DOCX}")
    print(f"OUTPUT_LOG={OUTPUT_LOG}")
    print(f"TOP_LEVEL_TABLES={top_tables}")
    print(f"TOP_LEVEL_DRAWING_PARAS={top_drawings}")
    print(f"SHA256={digest}")


if __name__ == "__main__":
    main()
