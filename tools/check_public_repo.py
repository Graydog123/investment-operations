#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run conservative checks before publishing the repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUFFIXES = {".docx", ".pdf", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg"}
FORBIDDEN_PATH_PARTS = {"sources", "private", "account", "accounts", "holdings", "screenshots"}
FORBIDDEN_TEXT: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("本机绝对路径", re.compile(r"/(?:Users|home|mnt)/[^\s)]+")),
    ("临时下载链接", re.compile(r"(?:sandbox:|file://|chatgpt-conversation://)")),
    ("内部账户证据编号", re.compile(r"\bR0[1-6]\b")),
    ("待补私人材料", re.compile(r"(?:账户|持仓|成交)(?:截图|凭证|材料)?待回填")),
    ("私人对话重建", re.compile(r"(?:用户口述事实|用户在对话中|对话重建|复原个人财富)")),
)

TEXT_SUFFIXES = {".md", ".txt", ".py", ".yml", ".yaml", ".cff", ""}


def main() -> int:
    failures: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue

        relative = path.relative_to(ROOT)
        if relative == Path("tools/check_public_repo.py"):
            continue
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & FORBIDDEN_PATH_PARTS:
            failures.append(f"禁止公开的目录：{relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"禁止公开的文件类型：{relative}")

        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"无法按 UTF-8 检查：{relative}")
            continue
        for label, pattern in FORBIDDEN_TEXT:
            if pattern.search(content):
                failures.append(f"{label}：{relative}")

    if failures:
        print("公开安全检查未通过：")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("公开安全检查通过：未发现预设的私人材料、临时路径或禁止文件类型。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
