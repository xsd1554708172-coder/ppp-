from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVISION_ROOT = ROOT / "修改稿"
LOG_ROOT = REVISION_ROOT / "操作日志"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_\-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "operation"


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def add_block(lines: list[str], title: str, values: list[str]) -> None:
    cleaned = [value for value in values if value]
    if not cleaned:
        return
    lines.extend(["", f"## {title}", ""])
    for value in cleaned:
        lines.append(f"- `{value}`")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write one timestamped revision-operation log file.")
    parser.add_argument("--action", required=True)
    parser.add_argument("--series", default="workspace")
    parser.add_argument("--token", default="general")
    parser.add_argument("--reviewed-source", action="append", default=[])
    parser.add_argument("--revised-output", action="append", default=[])
    parser.add_argument("--archive", action="append", default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--comment-file", action="append", default=[])
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--commit-message", default="")
    args = parser.parse_args()

    LOG_ROOT.mkdir(parents=True, exist_ok=True)

    now = datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d_%H%M%S")
    action_slug = slugify(args.action)
    series_slug = slugify(args.series)
    token_slug = slugify(args.token)
    log_path = LOG_ROOT / f"{stamp}__{series_slug}__{token_slug}__{action_slug}.md"

    branch = run_git("branch", "--show-current")
    head = run_git("rev-parse", "--short", "HEAD")

    lines = [
        "# 修改操作日志",
        "",
        f"- 时间：{now.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"- 动作：`{args.action}`",
        f"- 系列：`{args.series}`",
        f"- Token：`{args.token}`",
        f"- 分支：`{branch or 'unknown'}`",
        f"- HEAD：`{head or 'unknown'}`",
    ]

    if args.commit_message:
        lines.append(f"- 计划提交说明：`{args.commit_message}`")

    add_block(lines, "被审源稿", args.reviewed_source)
    add_block(lines, "修订输出", args.revised_output)
    add_block(lines, "归档输出", args.archive)
    add_block(lines, "其他输出", args.output)
    add_block(lines, "读取的修改建议", args.comment_file)
    add_block(lines, "备注", args.note)

    lines.append("")
    log_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(log_path)


if __name__ == "__main__":
    main()
