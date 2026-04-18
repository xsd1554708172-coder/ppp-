from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TARGET_DOCX = next(p for p in SCRIPT_DIR.iterdir() if p.suffix.lower() == ".docx")
LOG_PATH = SCRIPT_DIR / "docx_sanitization_log_20260418.md"

OLD_PHRASE = "\u5e73\u884c\u8d8b\u52bf\u5df2\u7ecf\u6210\u7acb"
NEW_PHRASE = "\u52a8\u6001\u524d\u8d8b\u52bf\u5dee\u5f02\u5df2\u88ab\u5145\u5206\u6392\u9664"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    before_sha = sha256(TARGET_DOCX)
    with zipfile.ZipFile(TARGET_DOCX, "r") as src:
        items = [(info, src.read(info.filename)) for info in src.infolist()]

    xml_before = None
    for info, payload in items:
        if info.filename == "word/document.xml":
            xml_before = payload.decode("utf-8")
            break
    if xml_before is None:
        raise RuntimeError("word/document.xml not found")

    before_count = xml_before.count(OLD_PHRASE)
    xml_after = xml_before.replace(OLD_PHRASE, NEW_PHRASE)
    after_old_count = xml_after.count(OLD_PHRASE)
    after_new_count = xml_after.count(NEW_PHRASE)

    temp_docx = TARGET_DOCX.with_suffix(".tmp.docx")
    with zipfile.ZipFile(temp_docx, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info, payload in items:
            if info.filename == "word/document.xml":
                payload = xml_after.encode("utf-8")
            dst.writestr(info, payload)
    temp_docx.replace(TARGET_DOCX)

    after_sha = sha256(TARGET_DOCX)
    log_text = "\n".join(
        [
            "# DOCX Sanitization Log",
            "",
            f"- target: `{TARGET_DOCX.name}`",
            f"- old_phrase: `{OLD_PHRASE}`",
            f"- new_phrase: `{NEW_PHRASE}`",
            f"- replacements_before: `{before_count}`",
            f"- old_phrase_after: `{after_old_count}`",
            f"- new_phrase_after: `{after_new_count}`",
            f"- sha256_before: `{before_sha}`",
            f"- sha256_after: `{after_sha}`",
        ]
    )
    LOG_PATH.write_text(log_text + "\n", encoding="utf-8")

    print(f"TARGET_DOCX={TARGET_DOCX}")
    print(f"LOG_PATH={LOG_PATH}")
    print(f"REPLACEMENTS_BEFORE={before_count}")
    print(f"OLD_PHRASE_AFTER={after_old_count}")
    print(f"NEW_PHRASE_AFTER={after_new_count}")
    print(f"SHA256_BEFORE={before_sha}")
    print(f"SHA256_AFTER={after_sha}")


if __name__ == "__main__":
    main()
