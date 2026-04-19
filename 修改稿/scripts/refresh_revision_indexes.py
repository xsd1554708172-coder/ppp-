from __future__ import annotations

from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVISION_ROOT = ROOT / "修改稿"
INDEX_ROOT = REVISION_ROOT / "索引"
LOG_ROOT = REVISION_ROOT / "操作日志"

SERIES_CONFIG = {
    "v1": {
        "label": "V1",
        "draft": REVISION_ROOT / "v1初始版",
        "advice": REVISION_ROOT / "v1修改建议",
        "notes": REVISION_ROOT / "v1说明文件",
        "archive": REVISION_ROOT / "v1修改稿留底",
    },
    "v2": {
        "label": "V2",
        "draft": REVISION_ROOT / "v2初始版",
        "advice": REVISION_ROOT / "v2修改建议",
        "notes": REVISION_ROOT / "v2说明文件",
        "archive": REVISION_ROOT / "v2修改稿留底",
    },
}


def write_if_changed(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def summarize_dir(path: Path) -> tuple[list[Path], list[Path]]:
    if not path.exists():
        return [], []
    dirs = sorted((p for p in path.iterdir() if p.is_dir()), key=lambda p: p.name.lower())
    files = sorted((p for p in path.iterdir() if p.is_file()), key=lambda p: p.name.lower())
    return dirs, files


def render_dir_block(title: str, path: Path) -> list[str]:
    dirs, files = summarize_dir(path)
    lines = [f"## {title}", "", f"- 路径：`{path.relative_to(ROOT).as_posix()}`"]
    if not path.exists():
        lines += ["- 状态：目录不存在", ""]
        return lines

    lines.append(f"- 子目录数：{len(dirs)}")
    lines.append(f"- 文件数：{len(files)}")
    if dirs:
        lines.append("- 子目录：")
        for item in dirs:
            child_count = len(list(item.iterdir()))
            lines.append(f"  - `{item.name}` ({child_count} items)")
    if files:
        lines.append("- 目录直下文件：")
        for item in files[:20]:
            lines.append(f"  - `{item.name}`")
        if len(files) > 20:
            lines.append(f"  - 其余 {len(files) - 20} 个文件略")
    lines.append("")
    return lines


def render_series_index(series_key: str, generated_at: str) -> str:
    cfg = SERIES_CONFIG[series_key]
    lines = [
        f"# {cfg['label']} 修改稿索引",
        "",
        f"最后更新：{generated_at}",
        "",
        "## 目录结构",
        "",
    ]
    lines.extend(render_dir_block("工作稿目录", cfg["draft"]))
    lines.extend(render_dir_block("修改建议目录", cfg["advice"]))
    lines.extend(render_dir_block("说明文件目录", cfg["notes"]))
    lines.extend(render_dir_block("留底目录", cfg["archive"]))
    return "\n".join(lines).rstrip() + "\n"


def render_overview(generated_at: str) -> str:
    lines = [
        "# 修改稿索引总览",
        "",
        f"最后更新：{generated_at}",
        "",
        "## 固定目录",
        "",
        f"- 修改稿根目录：`{REVISION_ROOT.relative_to(ROOT).as_posix()}`",
        f"- 操作日志目录：`{LOG_ROOT.relative_to(ROOT).as_posix()}`",
        f"- 索引目录：`{INDEX_ROOT.relative_to(ROOT).as_posix()}`",
        "",
        "## 系列索引",
        "",
        "- `索引/v1修改稿索引.md`",
        "- `索引/v2修改稿索引.md`",
        "",
        "## 当前规则摘要",
        "",
        "- 工作稿目录使用 `v1初始版/` 与 `v2初始版/`。",
        "- 修改建议目录统一使用 `v1修改建议/<token>修改建议/` 与 `v2修改建议/<token>修改建议/`，不再保留同级散放评审文件。",
        "- 说明文件目录统一使用 `v1说明文件/<token>/` 与 `v2说明文件/<token>/`。",
        "- 留底目录统一使用 `v1修改稿留底/<token>/` 与 `v2修改稿留底/<token>/`。",
        "- 每次收尾都必须新增一份精确到秒的操作日志，并把“被审源稿”和“修订输出”分开记录。",
        "- 触及样本、识别、结果数值、表图、附录或变量工程的修改，默认至少需要一轮可审计的 fresh rerun；若无法重跑，必须显式写明 blocker。",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)

    write_if_changed(INDEX_ROOT / "修改稿索引总览.md", render_overview(generated_at))
    write_if_changed(INDEX_ROOT / "v1修改稿索引.md", render_series_index("v1", generated_at))
    write_if_changed(INDEX_ROOT / "v2修改稿索引.md", render_series_index("v2", generated_at))
    print(INDEX_ROOT)


if __name__ == "__main__":
    main()
