# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import re
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


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


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "（2026.4.15）已确认采用的图和表"
MASTER_PLAN = SOURCE_DIR / "PPP论文写作总计划_公共管理期刊风格版_20260415.md"
LOCKED_SECTION3 = SOURCE_DIR / "PPP论文_理论分析与研究假设稿_公共管理风格_20260415.md"
FULL_DRAFT = SOURCE_DIR / "PPP论文完整正文初稿_公共管理风格_20260415.md"
TABLE_SOURCE = SOURCE_DIR / "PPP论文正文主表汇总_正式插入版_竖向适配修正版.docx"
OUTPUT_DOCX = ROOT / "PPP论文_完整论文初稿_公共管理风格_20260415.docx"
BACKUP_TXT = ROOT / "PPP论文_完整论文初稿_公共管理风格_20260415_备份.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def strip_markdown(line: str) -> str:
    text = line.replace("**", "")
    text = text.replace("`", "")
    return text.strip()


def replace_locked_section(full_text: str, section3_text: str) -> str:
    start = full_text.find("## 3 ")
    end = full_text.find("## 4 ", start)
    if start == -1 or end == -1:
        return full_text

    locked = section3_text.strip()
    if "已同步保存至" in locked:
        locked = locked.split("已同步保存至", 1)[0].rstrip()
    if locked.startswith("一、理论分析"):
        locked = locked.split("\n", 1)[1].lstrip()
        locked = "## 3 理论分析与研究假设\n\n" + locked
    elif not locked.startswith("## 3 "):
        locked = "## 3 理论分析与研究假设\n\n" + locked
    if not locked.endswith("\n"):
        locked += "\n"
    return full_text[:start] + locked + "\n" + full_text[end:].lstrip()


def consistency_check(text: str) -> None:
    must_have = [
        "推进结构",
        "治理过程",
        "treat_share",
        "接口优先",
        "预测不等于因果",
        "执行阶段占比显著上升",
        "采购阶段占比显著下降",
    ]
    for phrase in must_have:
        if phrase not in text:
            raise RuntimeError(f"缺少关键口径短语：{phrase}")

    forbidden = [
        "主识别模型是BERTopic",
        "模型替代治理",
    ]
    for phrase in forbidden:
        if phrase in text:
            raise RuntimeError(f"发现越界表述：{phrase}")


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        sig = f.read(24)
    if sig[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"暂不支持的图片格式：{path.name}")
    width, height = struct.unpack(">II", sig[16:24])
    return width, height


def extract_tables(docx_path: Path) -> list[ET.Element]:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": W}
    tables = root.findall(".//w:tbl", ns)
    return [copy.deepcopy(tbl) for tbl in tables]


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


def build_empty_paragraph() -> ET.Element:
    p = ET.Element(qn(W, "p"))
    ET.SubElement(p, qn(W, "r"))
    return p


def build_image_paragraph(
    image_name: str,
    rel_id: str,
    docpr_id: int,
    width_px: int,
    height_px: int,
) -> ET.Element:
    max_cx = int(6.2 * 914400)
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


def build_placeholder_table_note(caption: str) -> ET.Element:
    return build_paragraph(
        f"【{caption}的正式表格内容见当前采用主表文件，当前版本保留为可替换位置】",
        align="center",
        first_line=False,
        size=22,
    )


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
        f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
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


def clean_text_for_backup(markdown: str) -> str:
    lines_out: list[str] = []
    for line in markdown.splitlines():
        s = line.strip()
        if not s or s == "---":
            lines_out.append("")
            continue
        if s.startswith("#"):
            s = re.sub(r"^#+\s*", "", s)
        s = strip_markdown(s)
        lines_out.append(s)
    return "\n".join(lines_out).strip() + "\n"


def main() -> None:
    for path in [MASTER_PLAN, LOCKED_SECTION3, FULL_DRAFT, TABLE_SOURCE]:
        if not path.exists():
            raise FileNotFoundError(path)

    master_text = read_text(MASTER_PLAN)
    locked_section3_text = read_text(LOCKED_SECTION3)
    draft_text = read_text(FULL_DRAFT)

    if "推进结构改善优先" not in master_text or "接口优先" not in master_text:
        raise RuntimeError("总控文档关键口径缺失")

    draft_text = replace_locked_section(draft_text, locked_section3_text)
    consistency_check(draft_text)

    tables = extract_tables(TABLE_SOURCE)
    table_map = {i + 1: tables[i] for i in range(min(len(tables), 8))}

    body = ET.Element(qn(W, "body"))
    image_counter = 0
    image_docpr_id = 1
    image_rels: list[tuple[str, str]] = []
    media_payloads: dict[str, bytes] = {}
    title_seen = 0

    for raw_line in draft_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped == "---":
            continue

        fig_match = re.match(
            r"^\[此处插入图(\d+)：(.+?)（对应文件\s+(.+?)）\]$",
            stripped,
        )
        if fig_match:
            num = fig_match.group(1)
            caption = fig_match.group(2).strip()
            filename = fig_match.group(3).strip()
            image_path = SOURCE_DIR / filename
            if image_path.exists():
                image_counter += 1
                rel_id = f"rId{image_counter + 1}"
                media_name = f"image{image_counter}{image_path.suffix.lower()}"
                media_payloads[media_name] = image_path.read_bytes()
                image_rels.append((rel_id, media_name))
                width, height = png_size(image_path)
                body.append(build_image_paragraph(media_name, rel_id, image_docpr_id, width, height))
                image_docpr_id += 1
            else:
                body.append(build_paragraph(f"【缺失图片文件：{filename}】", align="center", first_line=False, size=22))
            body.append(build_paragraph(f"图{num} {caption}", align="center", first_line=False, size=22))
            continue

        tbl_match = re.match(r"^\[此处插入表(\d+)：(.+?)\]$", stripped)
        if tbl_match:
            num = int(tbl_match.group(1))
            caption = tbl_match.group(2).strip()
            body.append(build_paragraph(f"表{num} {caption}", align="center", first_line=False, size=22))
            table_elem = table_map.get(num)
            if table_elem is not None:
                body.append(copy.deepcopy(table_elem))
            else:
                body.append(build_placeholder_table_note(f"表{num} {caption}"))
            continue

        if stripped.startswith("# "):
            title_seen += 1
            text = strip_markdown(stripped[2:])
            if title_seen == 1:
                body.append(build_paragraph(text, align="center", first_line=False, size=36, bold=True, space_after=120))
            else:
                body.append(build_paragraph(text, align="center", first_line=False, size=28, bold=False, space_after=120))
            continue

        if stripped.startswith("## "):
            text = strip_markdown(stripped[3:])
            body.append(build_paragraph(text, align="left", first_line=False, size=30, bold=True, space_before=180, space_after=60))
            continue

        if stripped.startswith("### "):
            text = strip_markdown(stripped[4:])
            body.append(build_paragraph(text, align="left", first_line=False, size=28, bold=True, space_before=120, space_after=60))
            continue

        if stripped.startswith("**关键词**"):
            text = strip_markdown(stripped)
            body.append(build_paragraph(text, align="left", first_line=False, size=24, bold=False))
            continue

        if stripped.startswith("**假说") and stripped.endswith("**"):
            text = strip_markdown(stripped)
            body.append(build_paragraph(text, align="left", first_line=False, size=24, bold=True, space_before=60, space_after=60))
            continue

        text = strip_markdown(stripped)
        body.append(build_paragraph(text, align="both", first_line=True, size=24))

    sect = ET.SubElement(body, qn(W, "sectPr"))
    pgsz = ET.SubElement(sect, qn(W, "pgSz"))
    pgsz.set(qn(W, "w"), "11906")
    pgsz.set(qn(W, "h"), "16838")
    pgmar = ET.SubElement(sect, qn(W, "pgMar"))
    for k, v in {
        "top": "1440",
        "right": "1800",
        "bottom": "1440",
        "left": "1800",
        "header": "851",
        "footer": "992",
        "gutter": "0",
    }.items():
        pgmar.set(qn(W, k), v)

    document = ET.Element(qn(W, "document"))
    document.append(body)
    document_xml = ET.tostring(document, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", package_rels_xml())
        zf.writestr("docProps/core.xml", core_xml("政务服务数字化改革如何优化PPP项目推进与治理过程？"))
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", styles_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels_xml(image_rels))
        for media_name, payload in media_payloads.items():
            zf.writestr(f"word/media/{media_name}", payload)

    BACKUP_TXT.write_text(clean_text_for_backup(draft_text), encoding="utf-8-sig")

    with zipfile.ZipFile(OUTPUT_DOCX) as zf:
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/_rels/document.xml.rels",
        }
        missing = [name for name in required if name not in set(zf.namelist())]
        if missing:
            raise RuntimeError(f"生成的docx缺少关键部件：{missing}")

    print(f"DOCX={OUTPUT_DOCX}")
    print(f"BACKUP={BACKUP_TXT}")
    print(f"TABLES_USED={len(table_map)}")
    print(f"IMAGES_USED={len(media_payloads)}")


if __name__ == "__main__":
    main()
