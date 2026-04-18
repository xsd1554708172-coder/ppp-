# -*- coding: utf-8 -*-
from __future__ import annotations

import math
import re
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

import pandas as pd


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCT = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"

for prefix, uri in {
    "w": W,
    "r": R,
    "wp": WP,
    "a": A,
    "pic": PIC,
    "cp": CP,
    "dc": DC,
    "dcterms": DCT,
    "xsi": XSI,
    "ep": EP,
    "vt": VT,
}.items():
    ET.register_namespace(prefix, uri)


ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "（2026.4.15）已确认采用的图和表" / "PPP论文写作总计划_公共管理期刊风格版_20260415.md"
LOCKED_SECTION3_PATH = ROOT / "（2026.4.15）已确认采用的图和表" / "PPP论文_理论分析与研究假设稿_公共管理风格_20260415.md"
REVISION_MD_PATH = ROOT / "PPP论文完整正文初稿_公共管理风格_修订版_图表增强_20260415.md"
CURRENT_DOCX_PATH = ROOT / "PPP论文_完整论文初稿_公共管理风格_20260415.docx"
OUTPUT_DOCX_PATH = ROOT / "PPP论文_完整论文初稿_公共管理风格_修订版_图表增强_20260415.docx"
BACKUP_TXT_PATH = ROOT / "PPP论文_完整论文初稿_公共管理风格_修订版_图表增强_20260415_备份.txt"


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def find_one(filename: str) -> Path:
    matches = list(ROOT.rglob(filename))
    if not matches:
        raise FileNotFoundError(filename)
    matches.sort(key=lambda p: (len(str(p)), str(p)))
    return matches[0]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalize_locked_section(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^#\s+理论分析与研究假设（正式正文初稿）\s*", "", cleaned, count=1)
    cleaned = re.sub(r"^#\s+理论分析与研究假设\s*", "", cleaned, count=1)
    cleaned = cleaned.lstrip()
    if not cleaned.startswith("## 3 "):
        cleaned = "## 3 理论分析与研究假设\n\n" + cleaned
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


def replace_section3(full_text: str, section3_text: str) -> str:
    start = full_text.find("## 3 ")
    end = full_text.find("## 4 ", start)
    if start == -1 or end == -1:
        raise RuntimeError("未在修订版底稿中定位到第3章与第4章边界")
    return full_text[:start] + normalize_locked_section(section3_text) + "\n" + full_text[end:].lstrip()


def strip_markdown(line: str) -> str:
    return line.replace("**", "").replace("`", "").strip()


def clean_text_for_backup(markdown: str) -> str:
    out: list[str] = []
    for line in markdown.splitlines():
        s = line.rstrip()
        if not s:
            out.append("")
            continue
        if s.startswith("#"):
            s = re.sub(r"^#+\s*", "", s)
        out.append(strip_markdown(s))
    return "\n".join(out).strip() + "\n"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        sig = f.read(24)
    if sig[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"暂不支持的图片格式：{path.name}")
    return struct.unpack(">II", sig[16:24])


def safe_float(x) -> float | None:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None
        return float(x)
    except Exception:
        return None


def fmt_num(x, digits: int = 4) -> str:
    val = safe_float(x)
    if val is None:
        return ""
    return f"{val:.{digits}f}"


def fmt_p(x) -> str:
    val = safe_float(x)
    if val is None:
        return ""
    if val < 0.001:
        return "<0.001"
    return f"{val:.3f}"


def stars_from_p(x) -> str:
    val = safe_float(x)
    if val is None:
        return ""
    if val < 0.01:
        return "***"
    if val < 0.05:
        return "**"
    if val < 0.10:
        return "*"
    return ""


def fmt_coef_p(coef, p, digits: int = 4) -> str:
    return f"{fmt_num(coef, digits)}{stars_from_p(p)} [p={fmt_p(p)}]"


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"缺少列：{list(candidates)}")


def build_run(text: str, size: int = 24, bold: bool = False) -> ET.Element:
    r = ET.Element(qn(W, "r"))
    rpr = ET.SubElement(r, qn(W, "rPr"))
    fonts = ET.SubElement(rpr, qn(W, "rFonts"))
    fonts.set(qn(W, "ascii"), "Times New Roman")
    fonts.set(qn(W, "hAnsi"), "Times New Roman")
    fonts.set(qn(W, "eastAsia"), "宋体")
    if bold:
        ET.SubElement(rpr, qn(W, "b"))
    sz = ET.SubElement(rpr, qn(W, "sz"))
    sz.set(qn(W, "val"), str(size))
    szcs = ET.SubElement(rpr, qn(W, "szCs"))
    szcs.set(qn(W, "val"), str(size))
    t = ET.SubElement(r, qn(W, "t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def build_paragraph(
    text: str,
    *,
    align: str = "both",
    first_line: bool = True,
    size: int = 24,
    bold: bool = False,
    space_before: int = 0,
    space_after: int = 0,
) -> ET.Element:
    p = ET.Element(qn(W, "p"))
    ppr = ET.SubElement(p, qn(W, "pPr"))
    jc = ET.SubElement(ppr, qn(W, "jc"))
    jc.set(qn(W, "val"), align)
    spacing = ET.SubElement(ppr, qn(W, "spacing"))
    spacing.set(qn(W, "before"), str(space_before))
    spacing.set(qn(W, "after"), str(space_after))
    spacing.set(qn(W, "line"), "420")
    spacing.set(qn(W, "lineRule"), "auto")
    if first_line:
        ind = ET.SubElement(ppr, qn(W, "ind"))
        ind.set(qn(W, "firstLine"), "420")
    p.append(build_run(text, size=size, bold=bold))
    return p


def build_table_cell(text: str, width: int, *, header: bool = False) -> ET.Element:
    tc = ET.Element(qn(W, "tc"))
    tc_pr = ET.SubElement(tc, qn(W, "tcPr"))
    tcw = ET.SubElement(tc_pr, qn(W, "tcW"))
    tcw.set(qn(W, "w"), str(width))
    tcw.set(qn(W, "type"), "dxa")
    valign = ET.SubElement(tc_pr, qn(W, "vAlign"))
    valign.set(qn(W, "val"), "center")
    shd = ET.SubElement(tc_pr, qn(W, "shd"))
    shd.set(qn(W, "val"), "clear")
    shd.set(qn(W, "fill"), "EDEDED" if header else "FFFFFF")
    for line in str(text).split("\n"):
        tc.append(
            build_paragraph(
                line,
                align="center" if header else "left",
                first_line=False,
                size=20,
                bold=header,
            )
        )
    return tc


def build_table(headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None) -> ET.Element:
    tbl = ET.Element(qn(W, "tbl"))
    tbl_pr = ET.SubElement(tbl, qn(W, "tblPr"))
    tbl_w = ET.SubElement(tbl_pr, qn(W, "tblW"))
    tbl_w.set(qn(W, "w"), "0")
    tbl_w.set(qn(W, "type"), "auto")
    tbl_layout = ET.SubElement(tbl_pr, qn(W, "tblLayout"))
    tbl_layout.set(qn(W, "type"), "fixed")
    borders = ET.SubElement(tbl_pr, qn(W, "tblBorders"))
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        b = ET.SubElement(borders, qn(W, edge))
        b.set(qn(W, "val"), "single")
        b.set(qn(W, "sz"), "8")
        b.set(qn(W, "color"), "808080")

    if col_widths is None:
        col_widths = [1600] * len(headers)
    total_width = sum(col_widths)
    if total_width < 9000:
        scale = 9000 / total_width
        col_widths = [int(w * scale) for w in col_widths]

    tbl_grid = ET.SubElement(tbl, qn(W, "tblGrid"))
    for width in col_widths:
        grid_col = ET.SubElement(tbl_grid, qn(W, "gridCol"))
        grid_col.set(qn(W, "w"), str(width))

    def add_row(values: list[str], *, header: bool = False) -> None:
        tr = ET.SubElement(tbl, qn(W, "tr"))
        for value, width in zip(values, col_widths):
            tr.append(build_table_cell(value, width, header=header))

    add_row(headers, header=True)
    for row in rows:
        add_row([str(x) for x in row], header=False)
    return tbl


def build_image_paragraph(rel_id: str, image_name: str, docpr_id: int, width_px: int, height_px: int) -> ET.Element:
    max_cx = int(6.1 * 914400)
    cx = min(max_cx, max(width_px, 1) * 9525)
    cy = int(cx * height_px / max(width_px, 1))
    xml = f"""
    <w:p xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="{WP}" xmlns:a="{A}" xmlns:pic="{PIC}">
      <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:before="60" w:after="60" w:line="360" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:drawing>
          <wp:inline distT="0" distB="0" distL="0" distR="0">
            <wp:extent cx="{cx}" cy="{cy}"/>
            <wp:docPr id="{docpr_id}" name="{image_name}"/>
            <wp:cNvGraphicFramePr>
              <a:graphicFrameLocks noChangeAspect="1"/>
            </wp:cNvGraphicFramePr>
            <a:graphic>
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:nvPicPr>
                    <pic:cNvPr id="0" name="{image_name}"/>
                    <pic:cNvPicPr/>
                  </pic:nvPicPr>
                  <pic:blipFill>
                    <a:blip r:embed="{rel_id}"/>
                    <a:stretch><a:fillRect/></a:stretch>
                  </pic:blipFill>
                  <pic:spPr>
                    <a:xfrm>
                      <a:off x="0" y="0"/>
                      <a:ext cx="{cx}" cy="{cy}"/>
                    </a:xfrm>
                    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                  </pic:spPr>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    """
    return ET.fromstring(xml)


def styles_xml() -> bytes:
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W}">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
</w:styles>"""
    return xml.encode("utf-8")


def content_types_xml() -> bytes:
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
    return xml.encode("utf-8")


def package_rels_xml() -> bytes:
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""
    return xml.encode("utf-8")


def document_rels_xml(image_rels: list[tuple[str, str]]) -> bytes:
    items = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    ]
    for rel_id, target in image_rels:
        items.append(
            f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{target}"/>'
        )
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    xml += f'<Relationships xmlns="{REL}">' + "".join(items) + "</Relationships>"
    return xml.encode("utf-8")


def core_xml(title: str) -> bytes:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="{CP}" xmlns:dc="{DC}" xmlns:dcterms="{DCT}" xmlns:xsi="{XSI}">
  <dc:title>{title}</dc:title>
  <dc:creator>OpenAI Codex</dc:creator>
  <cp:lastModifiedBy>OpenAI Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{ts}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{ts}</dcterms:modified>
</cp:coreProperties>"""
    return xml.encode("utf-8")


def app_xml() -> bytes:
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="{EP}" xmlns:vt="{VT}">
  <Application>OpenAI Codex</Application>
    </Properties>"""
    return xml.encode("utf-8")


class DataBundle:
    def __init__(self) -> None:
        self.plan_text = read_text(PLAN_PATH)
        self.locked_section3_text = read_text(LOCKED_SECTION3_PATH)
        self.revision_text = read_text(REVISION_MD_PATH)

        ext_matches = list(ROOT.rglob("PPP_doc_level_variables_v3_扩展与审计窗口_20260413_0912.csv"))
        self.doc_all = pd.read_csv(ext_matches[0]) if ext_matches else None
        self.doc_did = pd.read_csv(find_one("PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv"))
        self.prov = pd.read_csv(find_one("PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv"))
        self.panel = pd.read_csv(find_one("PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv"))
        self.base = pd.read_csv(find_one("PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv"))
        self.event = pd.read_csv(find_one("PPP_第5部分_5.4动态系数长表_V3_重估版_20260413_1048.csv"))
        self.mech = pd.read_csv(find_one("PPP_第6部分_6.1-6.4结果方程含中介_V2_四级十二类_实际执行版.csv"))
        self.chain = pd.read_csv(find_one("PPP_第6部分_6.5链式机制路径长表_V2_四级十二类_实际执行版.csv"))
        self.med = pd.read_csv(find_one("PPP_第6部分_6.6严格中介效应分解结果长表_V2_四级十二类_实际执行版.csv"))
        self.het_main = pd.read_csv(find_one("PPP_第7部分_7.1-7.4交互项摘要_V2_四级十二类_实际执行版.csv"))
        self.het_risk = pd.read_csv(find_one("PPP_第7部分_7.5交互项摘要_V2_四级十二类_实际执行版.csv"))
        self.het_open = pd.read_csv(find_one("PPP_第7部分_7.6交互项摘要_V2_四级十二类_实际执行版.csv"))
        self.rob = pd.read_csv(find_one("PPP_第8部分_8.1-8.3常规稳健性结果长表_V3_重估版_20260413_1048.csv"))
        self.psm = pd.read_csv(find_one("PPP_第8部分_8.4PSM-DID结果长表_V3_重估版_20260413_1048.csv"))
        self.iv = pd.read_csv(find_one("PPP_第8部分_8.5候选IV筛查长表_V3_重估版_20260413_1048.csv"))
        self.dml = pd.read_csv(find_one("PPP_第8部分_8.6DML结果汇总_V3_重估版_20260413_1048.csv"))
        self.metrics = pd.read_csv(find_one("PPP_第9部分_严格版_6模型指标汇总.csv"))
        self.project = pd.read_csv(find_one("PPP_project_level_risk_model_data_v3_无泄漏严格版_标签统一_20260413_1048.csv"))
        self.placebo = pd.read_csv(find_one("part5_placebo_coefficients_generated.csv"))

        self.panel["year_num"] = to_numeric(self.panel["year"])
        self.panel["did_any_num"] = to_numeric(self.panel["did_any"]).fillna(0)
        self.panel["text_observed_num"] = to_numeric(self.panel["text_observed"]).fillna(0)
        self.panel["text_missing_num"] = to_numeric(self.panel["text_missing"]).fillna(0)
        self.panel["baseline_num"] = to_numeric(self.panel["baseline_sample_5_3"]).fillna(0)
        self.base_panel = self.panel[self.panel["baseline_num"] == 1].copy()

        self.table_map = self.build_table_map()

    def row_by(self, df: pd.DataFrame, **conds):
        subset = df.copy()
        for k, v in conds.items():
            subset = subset[subset[k] == v]
        if subset.empty:
            raise KeyError(f"未匹配到行：{conds}")
        return subset.iloc[0]

    def build_table_map(self) -> dict[str, tuple[list[str], list[list[str]], list[int] | None]]:
        return {
            "1": self.table1(),
            "2": self.table2(),
            "3": self.table3(),
            "4": self.table4(),
            "5": self.table5(),
            "6": self.table6(),
            "7": self.table7(),
            "8": self.table8(),
            "9": self.table9(),
            "附表A": self.appendix_table_a(),
            "附表B": self.appendix_table_b(),
            "附表C": self.appendix_table_c(),
            "附表D": self.appendix_table_d(),
        }

    def table1(self):
        doc_total = len(self.doc_all) if self.doc_all is not None else 1472
        rows = [
            ["全量政策文本池", "文本原始池", str(doc_total), "用于界定政策文本总体覆盖与扩展审计窗口"],
            ["正式DID文本样本", "2014—2022 主识别窗口", str(len(self.doc_did)), "进入文档级文本变量构造的地方样本文本"],
            [
                "省—年文本单元",
                "平衡口径",
                str(len(self.prov)),
                f"其中 text_observed={int(to_numeric(self.prov['text_observed']).fillna(0).sum())}，text_missing={int(to_numeric(self.prov['text_missing']).fillna(0).sum())}",
            ],
            [
                "V3主面板观测",
                "统一口径方案2",
                str(len(self.panel)),
                f"其中 text_observed={int(self.panel['text_observed_num'].sum())}，text_missing={int(self.panel['text_missing_num'].sum())}",
            ],
            ["正式基准回归样本", "表4对应样本", str(len(self.base_panel)), "作为 treat_share 多期DID/TWFE 的主估计样本"],
            ["项目级扩展样本", "严格无泄漏底表", str(len(self.project)), "仅用于项目级高低风险识别扩展分析"],
        ]
        headers = ["样本层级", "口径/窗口", "样本量", "说明"]
        widths = [1700, 1800, 1200, 4300]
        return headers, rows, widths

    def table2(self):
        topics = self.doc_did[["topic", "topic_secondary_code", "topic_secondary_name", "topic_name"]].drop_duplicates().copy()
        topics["dim"] = topics["topic_secondary_code"].astype(str).str[0]

        def topic_summary(letter: str) -> str:
            subset = topics[topics["dim"] == letter].sort_values("topic")
            if subset.empty:
                return "无独立主导主题簇"
            return "；".join(
                f"topic {int(r.topic)}：{r.topic_secondary_code}-{r.topic_secondary_name}"
                for r in subset.itertuples()
            )

        rows = [
            ["A维度：数字治理接口与数据协同", topic_summary("A"), "刻画平台、在线办理、数据共享和信息公开等制度接口", "A_idx、A_share、z_A_idx"],
            ["B维度：项目识别与前端规范准入", topic_summary("B"), "刻画项目识别、入库筛选、物有所值与财政承受能力审查、实施方案审批", "B_idx、B_share、z_B_idx"],
            ["C维度：采购交易、合同安排与执行绩效", topic_summary("C"), "刻画采购配置、合同权责与执行运营等中后端治理表达", "C_idx、C_share、z_C_idx"],
            ["D维度：风险防控、监督纠偏与退出约束", "BERTopic 未形成独立主导主题簇，主要由词典/代码本识别补充", "刻画风险防控、监督约束与退出安排，作为治理后端约束维度", "D_idx、D_share、z_D_idx"],
        ]
        headers = ["治理维度", "主题映射/二级代码", "公共管理含义", "进入主面板的正式变量"]
        widths = [2000, 3200, 2600, 1400]
        return headers, rows, widths

    def table3(self):
        first_treat = self.panel[self.panel["did_any_num"] > 0].groupby(first_existing_column(self.panel, ["province_harmonized", "province"]))["year_num"].min()
        all_prov_col = first_existing_column(self.panel, ["province_harmonized", "province"])
        provinces_all = sorted(self.panel[all_prov_col].dropna().astype(str).unique())
        never = sorted(set(provinces_all) - set(first_treat.index.astype(str)))
        rows = [
            ["样本期", "2014—2022", "", "", "", "V3主面板覆盖区间"],
            ["地区单元数", str(self.panel[all_prov_col].nunique()), "", "", "", "主面板地区数"],
            ["正式回归地区数", str(self.base_panel[all_prov_col].nunique()), "", "", "", "表4有效地区数"],
            ["首次处理年：2016", str(int((first_treat == 2016).sum())), "", "", "", "主要处理批次"],
            ["首次处理年：2017", str(int((first_treat == 2017).sum())), "", "", "", "少量后续进入处理"],
            ["Never-treated地区", str(len(never)), "", "", "", "用于DID对照基准"],
        ]
        for var in ["treat_share", "did_any", "did_intensity", "exec_share", "proc_share", "prep_share", "ppp_quality_zindex", "A_idx", "B_idx", "C_idx", "D_idx", "doc_count"]:
            s = to_numeric(self.panel[var]).dropna()
            rows.append([var, fmt_num(s.mean(), 4), fmt_num(s.std(ddof=1), 4), fmt_num(s.min(), 4), fmt_num(s.max(), 4), f"N={len(s)}"])
        headers = ["项目/变量", "均值或数量", "标准差", "最小值", "最大值", "说明"]
        widths = [2100, 1500, 1400, 1200, 1200, 2600]
        return headers, rows, widths

    def table4(self):
        rows = []
        for dep in ["exec_share", "proc_share", "ppp_quality_zindex"]:
            r = self.row_by(self.base, depvar=dep, did_var="treat_share")
            rows.append([dep, str(r["coef_star"]), str(r["se_fmt"]), fmt_p(r["p"]), str(int(float(r["N"]))), fmt_num(r["r2"], 3), "主结果" if dep in {"exec_share", "proc_share"} else "方向为正但统计不稳"])
        headers = ["结果变量", "treat_share系数", "聚类标准误", "p值", "N", "R²", "写作口径"]
        widths = [1700, 1700, 1600, 1000, 800, 800, 2400]
        return headers, rows, widths

    def table5(self):
        rows = []
        for outcome in ["exec_share", "proc_share", "ppp_quality_zindex"]:
            note = "领先项存在显著性或边际显著性，仅能说明动态路径与识别边界"
            row = [outcome]
            for evt in ["<=-2", "0", "1", "2", ">=3"]:
                r = self.row_by(self.event, outcome=outcome, event_time=evt)
                row.append(fmt_coef_p(r["coef"], r["p"]))
            row.append(note)
            rows.append(row)
        headers = ["结果变量", "处理前(<=-2)", "当期(0)", "后1期", "后2期", "后3期及以上", "识别边界说明"]
        widths = [1500, 1500, 1300, 1300, 1300, 1700, 2400]
        return headers, rows, widths

    def table6(self):
        a_row = self.row_by(self.chain, dependent="A_idx", variable="treat_share")
        b_row = self.row_by(self.chain, dependent="B_idx", variable="treat_share")
        bc_row = self.row_by(self.chain, dependent="C_idx", variable="B_idx")
        cd_row = self.row_by(self.chain, dependent="D_idx", variable="C_idx")
        td_row = self.row_by(self.chain, dependent="D_idx", variable="treat_share")
        exec_med = self.row_by(self.mech, outcome="exec_share", mediator="A_idx", did_var="treat_share")
        proc_med = self.row_by(self.mech, outcome="proc_share", mediator="A_idx", did_var="treat_share")
        qual_med = self.row_by(self.mech, outcome="ppp_quality_zindex", mediator="A_idx", did_var="treat_share")
        exec_strict = self.row_by(self.med, outcome="exec_share", mediator="A_idx")
        proc_strict = self.row_by(self.med, outcome="proc_share", mediator="A_idx")
        qual_strict = self.row_by(self.med, outcome="ppp_quality_zindex", mediator="A_idx")
        rows = [
            ["A维度先行响应", "treat_share→A_idx", fmt_coef_p(a_row["coef"], a_row["p"]), str(int(float(a_row["N"]))), "接口维度显著先行"],
            ["前端规范响应", "treat_share→B_idx", fmt_coef_p(b_row["coef"], b_row["p"]), str(int(float(b_row["N"]))), "B维度发生显著调整"],
            ["链式传导", "B_idx→C_idx", fmt_coef_p(bc_row["coef"], bc_row["p"]), str(int(float(bc_row["N"]))), "前端规范向采购执行维度传导"],
            ["链式传导", "C_idx→D_idx", fmt_coef_p(cd_row["coef"], cd_row["p"]), str(int(float(cd_row["N"]))), "后端风险约束存在局部传导"],
            ["后端直接效应", "treat_share→D_idx", fmt_coef_p(td_row["coef"], td_row["p"]), str(int(float(td_row["N"]))), "未观察到稳定直接响应"],
            ["中介方程", "exec_share 中 A_idx", f"did={fmt_coef_p(exec_med['coef_did'], exec_med['p_did'])}\nmed={fmt_coef_p(exec_med['coef_mediator'], exec_med['p_mediator'])}", str(int(float(exec_med["N"]))), "直接效应存在，中介项不稳"],
            ["中介方程", "proc_share 中 A_idx", f"did={fmt_coef_p(proc_med['coef_did'], proc_med['p_did'])}\nmed={fmt_coef_p(proc_med['coef_mediator'], proc_med['p_mediator'])}", str(int(float(proc_med["N"]))), "直接效应存在，中介项不稳"],
            ["中介方程", "ppp_quality_zindex 中 A_idx", f"did={fmt_coef_p(qual_med['coef_did'], qual_med['p_did'])}\nmed={fmt_coef_p(qual_med['coef_mediator'], qual_med['p_mediator'])}", str(int(float(qual_med["N"]))), "质量型结果不稳"],
            ["严格中介", "exec_share", f"ab={fmt_num(exec_strict['indirect_effect_ab'])}\nSobel p={fmt_p(exec_strict['sobel_p'])}\nCI=[{fmt_num(exec_strict['boot_ci_low'],3)}, {fmt_num(exec_strict['boot_ci_high'],3)}]", str(int(float(exec_strict["N"]))), "严格中介不足"],
            ["严格中介", "proc_share", f"ab={fmt_num(proc_strict['indirect_effect_ab'])}\nSobel p={fmt_p(proc_strict['sobel_p'])}\nCI=[{fmt_num(proc_strict['boot_ci_low'],3)}, {fmt_num(proc_strict['boot_ci_high'],3)}]", str(int(float(proc_strict["N"]))), "严格中介不足"],
            ["严格中介", "ppp_quality_zindex", f"ab={fmt_num(qual_strict['indirect_effect_ab'])}\nSobel p={fmt_p(qual_strict['sobel_p'])}\nCI=[{fmt_num(qual_strict['boot_ci_low'],3)}, {fmt_num(qual_strict['boot_ci_high'],3)}]", str(int(float(qual_strict["N"]))), "严格中介不足"],
        ]
        headers = ["机制层级", "核心链条/结果", "核心系数与显著性", "N", "结论"]
        widths = [1400, 1900, 3200, 700, 2300]
        return headers, rows, widths

    def table7(self):
        rows = []
        main_sorted = self.het_main.sort_values("p_value")
        for _, r in main_sorted.head(3).iterrows():
            rows.append([str(r["block"]), str(r["outcome"]), str(r["term"]), fmt_coef_p(r["coef"], r["p_value"]), str(int(float(r["N"]))), "仅作为差异线索" if r["outcome"] != "ppp_quality_zindex" else "质量型局部差异，不改写主结论"])
        for _, r in self.het_risk.iterrows():
            rows.append(["PPP风险暴露", str(r["outcome"]), "interaction", fmt_coef_p(r["interaction_coef"], r["interaction_p"]), str(int(float(r["N"]))), str(r["interpretation"])])
        for _, r in self.het_open.iterrows():
            rows.append(["政府数据开放度", str(r["outcome"]), "interaction", fmt_coef_p(r["interaction_coef"], r["interaction_p"]), str(int(float(r["N"]))), "交互项不显著，更多体现为适用边界补充"])
        headers = ["异质性维度", "结果变量", "交互项", "交互结果", "N", "解释"]
        widths = [1600, 1500, 1800, 1600, 700, 2800]
        return headers, rows, widths

    def table8(self):
        def rob_row(spec: str, dep: str):
            return self.row_by(self.rob, depvar=dep, spec=spec)

        rows = []
        for spec, label in [("baseline_treat_share", "常规稳健性：主规格锚定"), ("lagged_controls", "常规稳健性：滞后一期控制变量"), ("drop_special_regions", "常规稳健性：剔除直辖市与兵团")]:
            re = rob_row(spec, "exec_share")
            rp = rob_row(spec, "proc_share")
            rz = rob_row(spec, "ppp_quality_zindex")
            rows.append([label, f"{re['coef_star']} [p={fmt_p(re['p'])}]", f"{rp['coef_star']} [p={fmt_p(rp['p'])}]", f"{rz['coef_star']} [p={fmt_p(rz['p'])}]", "推进结构方向稳定；质量型结果不稳"])

        p_exec = self.row_by(self.psm, outcome="exec_share", treatment="treat_share")
        p_proc = self.row_by(self.psm, outcome="proc_share", treatment="treat_share")
        p_qual = self.row_by(self.psm, outcome="ppp_quality_zindex", treatment="treat_share")
        rows.append(["PSM-DID敏感性", f"{p_exec['coef_fmt']} [p={p_exec['p_fmt']}]", f"{p_proc['coef_fmt']} [p={p_proc['p_fmt']}]", f"{p_qual['coef_fmt']} [p={p_qual['p_fmt']}]", "匹配样本结果敏感，作为识别边界而非强化证据"])

        d_exec = self.row_by(self.dml, outcome="exec_share")
        d_proc = self.row_by(self.dml, outcome="proc_share")
        d_qual = self.row_by(self.dml, outcome="ppp_quality_zindex")
        rows.append(["DML高维稳健性", fmt_coef_p(d_exec["dml_coef"], d_exec["dml_pvalue"]), fmt_coef_p(d_proc["dml_coef"], d_proc["dml_pvalue"]), fmt_coef_p(d_qual["dml_coef"], d_qual["dml_pvalue"]), "三项结果方向一致，但统计强度有限"])

        iv_best = self.iv.sort_values("best_case_rank").iloc[0]
        rows.append(["IV可行性评估", f"最优候选：{iv_best['candidate_iv']}", f"一阶段t={fmt_num(iv_best['first_stage_t'],3)}", f"recommended={iv_best['recommended_as_iv']}", "当前V3主面板下一阶段相关性不足，不能写成正式IV结果"])

        placebo_mean = self.placebo["placebo_coef"].mean()
        placebo_p95 = self.placebo["placebo_coef"].quantile(0.95)
        placebo_p99 = self.placebo["placebo_coef"].quantile(0.99)
        rows.append(["安慰剂检验", f"均值={fmt_num(placebo_mean,4)}", f"95%分位={fmt_num(placebo_p95,4)}", f"99%分位={fmt_num(placebo_p99,4)}", "随机置换系数围绕零值分布，作为补充性稳健性支持"])
        headers = ["检验层级", "exec_share", "proc_share", "ppp_quality_zindex", "写作口径"]
        widths = [2200, 1800, 1800, 1800, 2200]
        return headers, rows, widths

    def table9(self):
        metrics = self.metrics.copy().sort_values("AUC", ascending=False)
        rows = []
        for _, r in metrics.iterrows():
            rows.append([str(r["model"]), fmt_num(r["AUC"], 4), fmt_num(r["AP"], 4), fmt_num(r["F1"], 4), fmt_num(r["Precision"], 4), fmt_num(r["Recall"], 4), fmt_num(r["Accuracy"], 4)])
        headers = ["模型", "AUC", "AP", "F1", "Precision", "Recall", "Accuracy"]
        widths = [2800, 900, 900, 900, 1100, 1100, 1100]
        return headers, rows, widths

    def appendix_table_a(self):
        first_treat = self.panel[self.panel["did_any_num"] > 0].groupby(first_existing_column(self.panel, ["province_harmonized", "province"]))["year_num"].min()
        provinces_all = self.panel[first_existing_column(self.panel, ["province_harmonized", "province"])].nunique()
        rows = [
            ["全量政策文本池", str(len(self.doc_all) if self.doc_all is not None else 1472), "扩展与审计窗口"],
            ["正式DID文档样本", str(len(self.doc_did)), "主识别窗口 2014—2022"],
            ["省—年平衡文本单元", str(len(self.prov)), "方案2 平衡口径"],
            ["V3主面板观测", str(len(self.panel)), f"覆盖地区单元={provinces_all}"],
            ["正式基准回归样本", str(len(self.base_panel)), "表4对应样本"],
            ["首次处理年2016", str(int((first_treat == 2016).sum())), "多期DID主要处理批次"],
            ["首次处理年2017", str(int((first_treat == 2017).sum())), "少量后续处理"],
        ]
        headers = ["层级/窗口", "数量", "说明"]
        widths = [2400, 1200, 4400]
        return headers, rows, widths

    def appendix_table_b(self):
        rows = []
        for letter in ["A", "B", "C", "D"]:
            cnt = to_numeric(self.doc_did[f"{letter}_cnt"]).fillna(0)
            share = to_numeric(self.doc_did[f"{letter}_share"]).fillna(0)
            idx = to_numeric(self.doc_did[f"{letter}_idx"]).fillna(0)
            rows.append([f"{letter}维度", fmt_num((cnt > 0).mean(), 4), fmt_num(share.mean(), 4), fmt_num(idx.mean(), 4), "文档级代码本覆盖率诊断"])
        headers = ["维度", "文档覆盖率", "平均share", "平均idx", "说明"]
        widths = [1600, 1500, 1500, 1500, 2900]
        return headers, rows, widths

    def appendix_table_c(self):
        first_treat = self.panel[self.panel["did_any_num"] > 0].groupby(first_existing_column(self.panel, ["province_harmonized", "province"]))["year_num"].min()
        all_prov_col = first_existing_column(self.panel, ["province_harmonized", "province"])
        never = sorted(set(self.panel[all_prov_col].dropna().astype(str).unique()) - set(first_treat.index.astype(str)))
        rows = [
            ["2016", str(int((first_treat == 2016).sum())), "首个处理年份的主体批次"],
            ["2017", str(int((first_treat == 2017).sum())), "后续少量进入处理"],
            ["Never-treated", str(len(never)), "、".join(never)],
        ]
        headers = ["处理年份结构", "地区数", "说明"]
        widths = [1600, 1200, 4900]
        return headers, rows, widths

    def appendix_table_d(self):
        rows = []
        for var in ["ppp_governance_capacity_index", "ppp_norm_risk_index", "dfi", "digital_econ", "ln_ppp_inv", "doc_count", "total_chars", "total_sentences"]:
            if var not in self.panel.columns:
                continue
            s = to_numeric(self.panel[var]).dropna()
            rows.append([var, fmt_num(s.mean(), 4), fmt_num(s.std(ddof=1), 4), fmt_num(s.min(), 4), fmt_num(s.max(), 4)])
        headers = ["变量", "均值", "标准差", "最小值", "最大值"]
        widths = [2400, 1500, 1500, 1500, 1500]
        return headers, rows, widths


def load_figure_path(filename: str) -> Path:
    return find_one(filename)


def parse_figure_placeholder(line: str):
    m = re.match(r"^\[此处插入图([0-9A-Z]+)：(.+?)（对应文件 (.+?)）\]$", line.strip())
    if m:
        return m.group(1), m.group(2).strip(), m.group(3).strip()
    return None


def parse_table_placeholder(line: str):
    stripped = line.strip()
    m1 = re.match(r"^\[此处插入表([0-9A-Z]+)：(.+?)\]$", stripped)
    if m1:
        return f"{m1.group(1)}", m1.group(2).strip()
    m2 = re.match(r"^\[此处插入附表([0-9A-Z]+)：(.+?)\]$", stripped)
    if m2:
        return f"附表{m2.group(1)}", m2.group(2).strip()
    return None


def build_document(data: DataBundle) -> tuple[bytes, dict[str, bytes]]:
    merged_text = replace_section3(data.revision_text, data.locked_section3_text)
    for phrase in ["推进结构改善优先", "接口优先", "预测不等于因果", "不替代治理", "表4", "图6", "表8", "图10"]:
        if phrase not in merged_text:
            raise RuntimeError(f"修订版正文缺少关键结构性短语：{phrase}")

    body = ET.Element(qn(W, "body"))
    media_payloads: dict[str, bytes] = {}
    image_rels: list[tuple[str, str]] = []
    image_docpr_id = 1
    image_counter = 0
    chapter_started = False

    for raw_line in merged_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        fig_info = parse_figure_placeholder(stripped)
        if fig_info:
            label, caption, filename = fig_info
            fig_path = load_figure_path(filename)
            image_counter += 1
            media_name = f"image{image_counter}.png"
            rel_id = f"rId{image_counter + 1}"
            media_payloads[media_name] = fig_path.read_bytes()
            image_rels.append((rel_id, media_name))
            width, height = png_size(fig_path)
            body.append(build_image_paragraph(rel_id, media_name, image_docpr_id, width, height))
            image_docpr_id += 1
            body.append(build_paragraph(f"图{label} {caption}", align="center", first_line=False, size=21, space_after=60))
            continue

        tbl_info = parse_table_placeholder(stripped)
        if tbl_info:
            key, caption = tbl_info
            label_text = key if key.startswith("附表") else f"表{key}"
            body.append(build_paragraph(f"{label_text} {caption}", align="center", first_line=False, size=21, space_after=40))
            headers, rows, widths = data.table_map[key]
            body.append(build_table(headers, rows, widths))
            continue

        if stripped.startswith("# "):
            body.append(build_paragraph(strip_markdown(stripped[2:]), align="center", first_line=False, size=32, bold=True, space_after=120))
            continue
        if stripped.startswith("## "):
            text = strip_markdown(stripped[3:])
            if re.match(r"^—", text) and not chapter_started:
                body.append(build_paragraph(text, align="center", first_line=False, size=26, space_after=100))
            else:
                chapter_started = chapter_started or bool(re.match(r"^\d+\s", text))
                body.append(build_paragraph(text, align="left", first_line=False, size=28, bold=True, space_before=160, space_after=60))
            continue
        if stripped.startswith("### "):
            body.append(build_paragraph(strip_markdown(stripped[4:]), align="left", first_line=False, size=25, bold=True, space_before=100, space_after=40))
            continue
        if stripped.startswith("**关键词**") or stripped.startswith("**关"):
            body.append(build_paragraph(strip_markdown(stripped), align="left", first_line=False, size=24, space_after=40))
            continue
        if stripped.startswith("**假说") and stripped.endswith("**"):
            body.append(build_paragraph(strip_markdown(stripped), align="left", first_line=False, size=24, bold=True, space_before=50, space_after=50))
            continue
        body.append(build_paragraph(strip_markdown(stripped), align="both", first_line=True, size=24))

    sect = ET.SubElement(body, qn(W, "sectPr"))
    pgsz = ET.SubElement(sect, qn(W, "pgSz"))
    pgsz.set(qn(W, "w"), "11906")
    pgsz.set(qn(W, "h"), "16838")
    pgmar = ET.SubElement(sect, qn(W, "pgMar"))
    for k, v in {"top": "1440", "right": "1800", "bottom": "1440", "left": "1800", "header": "851", "footer": "992", "gutter": "0"}.items():
        pgmar.set(qn(W, k), v)

    document = ET.Element(qn(W, "document"))
    document.append(body)
    return ET.tostring(document, encoding="utf-8", xml_declaration=True), {"rels": document_rels_xml(image_rels), "media": media_payloads}


def save_docx(document_xml: bytes, rels_xml: bytes, media_payloads: dict[str, bytes]) -> None:
    with zipfile.ZipFile(OUTPUT_DOCX_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", package_rels_xml())
        zf.writestr("docProps/core.xml", core_xml("政务服务数字化改革如何优化PPP项目推进与治理过程？"))
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", styles_xml())
        zf.writestr("word/_rels/document.xml.rels", rels_xml)
        for media_name, payload in media_payloads.items():
            zf.writestr(f"word/media/{media_name}", payload)


def verify_output(data: DataBundle) -> None:
    if not OUTPUT_DOCX_PATH.exists() or OUTPUT_DOCX_PATH.stat().st_size == 0:
        raise RuntimeError("修订版 DOCX 未生成成功")

    with zipfile.ZipFile(OUTPUT_DOCX_PATH) as zf:
        names = set(zf.namelist())
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/_rels/document.xml.rels",
        }
        missing = required - names
        if missing:
            raise RuntimeError(f"DOCX 包缺少关键部件：{sorted(missing)}")
        xml_text = zf.read("word/document.xml").decode("utf-8")

    expected_labels = [
        "表1 PPP政策文本样本结构与语料覆盖情况",
        "表2 政策文本分析框架、主题映射与变量落地",
        "表3 V3主面板样本结构、处理时点与主要变量描述统计",
        "表4 基准多期DID_TWFE结果",
        "表5 动态路径与事件研究摘要表",
        "表6 机制检验主结果表",
        "表7 异质性结果摘要表",
        "表8 稳健性检验摘要表",
        "表9 项目级高低风险识别——六模型预测绩效比较",
        "图1 政策文本构造与治理能力测度总览",
        "图2 文档级文本与省—年治理测度的双层主题嵌入结构",
        "图3 PPP项目推进状态空间与结构演变",
        "图4 处理组与对照组核心变量分布差异",
        "图5 处理时点与样本覆盖结构",
        "图6 基准DID主结果的系数与置信区间",
        "图7 事件研究动态路径图",
        "图8 主结果稳健性证据阶梯图",
        "图9 安慰剂分布图",
        "图10 项目级高低风险识别的ROC曲线比较",
        "图11 项目级高低风险识别的PR曲线比较",
        "图A1 BERTopic主题相似性矩阵诊断",
        "图B3 不同阈值下的成本收益权衡",
    ]
    for label in expected_labels:
        if label not in xml_text:
            raise RuntimeError(f"DOCX 缺少图表标题：{label}")

    wrong_old_titles = [
        "一级主题—二级代码—主题名称—触发词",
        "试编码样本数",
        "理论地区宇宙",
        "首个处理年份为2016",
    ]
    for old in wrong_old_titles:
        if old in xml_text:
            raise RuntimeError(f"正文仍残留错配旧表内容：{old}")

    merged = replace_section3(data.revision_text, data.locked_section3_text)
    for phrase in [
        "图6给出了主结果可视化",
        "图7和表5可以用来说明改革影响具有动态展开过程",
        "表6支持的是部分机制和阶段性传导",
        "表8和图8看",
        "表9以及图10、图11展示的是排序和识别能力",
        "附录A1还给出BERTopic主题相似性矩阵",
    ]:
        if phrase not in merged:
            raise RuntimeError(f"修订版正文缺少关键证据承接句：{phrase}")


def main() -> None:
    for path in [PLAN_PATH, LOCKED_SECTION3_PATH, REVISION_MD_PATH, CURRENT_DOCX_PATH]:
        if not path.exists():
            raise FileNotFoundError(path)

    data = DataBundle()
    merged_text = replace_section3(data.revision_text, data.locked_section3_text)
    BACKUP_TXT_PATH.write_text(clean_text_for_backup(merged_text), encoding="utf-8-sig")

    document_xml, assets = build_document(data)
    save_docx(document_xml, assets["rels"], assets["media"])
    verify_output(data)

    print(f"DOCX={OUTPUT_DOCX_PATH}")
    print(f"BACKUP={BACKUP_TXT_PATH}")
    print(f"FIGURES={len(assets['media'])}")
    print("TABLES=9正文+4附表")


if __name__ == "__main__":
    main()
