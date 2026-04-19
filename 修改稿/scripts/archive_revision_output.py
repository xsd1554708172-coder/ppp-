from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVISION_ROOT = ROOT / "修改稿"


def detect_bucket(token: str) -> str:
    token_lower = token.lower()
    if token_lower.startswith("v1"):
        return "v1修改稿留底"
    if token_lower.startswith("v2"):
        return "v2修改稿留底"
    raise ValueError(f"无法根据 token 判断留底目录: {token}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive a revised manuscript into the correct v1/v2 archive folder."
    )
    parser.add_argument("--source", required=True, help="Path of the revised manuscript file.")
    parser.add_argument("--token", required=True, help="Version token such as v1d or v2d.")
    parser.add_argument("--timestamp", default=None, help="Optional timestamp in MMDD_HHMM format.")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    token = args.token.strip()
    bucket = detect_bucket(token)
    target_dir = REVISION_ROOT / bucket / token
    target_dir.mkdir(parents=True, exist_ok=True)

    stamp = args.timestamp or datetime.now().strftime("%m%d_%H%M")
    target = target_dir / f"{token}_{stamp}{source.suffix.lower()}"
    shutil.copy2(source, target)
    print(target)


if __name__ == "__main__":
    main()
