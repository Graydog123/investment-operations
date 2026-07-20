#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Convert a Word manuscript into reviewable Markdown.

The converter intentionally supports only the structures used by this project:
headings, paragraphs, simple lists, callout tables, and ordinary tables. It is a
publishing helper, not a general-purpose DOCX renderer.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterator

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_blocks(document: DocumentObject) -> Iterator[Paragraph | Table]:
    """Yield paragraphs and tables in document order."""
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


def clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraph_markdown(paragraph: Paragraph) -> str:
    text = clean(paragraph.text)
    if not text:
        return ""

    style = paragraph.style.name if paragraph.style else ""
    if style == "Title":
        return f"# {text}"
    if style == "Subtitle":
        return f"*{text}*"
    if style.startswith("Heading"):
        match = re.search(r"(\d+)", style)
        level = min(int(match.group(1)) if match else 2, 6)
        return f"{'#' * level} {text}"
    if "Bullet" in style:
        return f"- {text}"
    if "Number" in style:
        return f"1. {text}"
    if style == "Source Note":
        return f"> {text}"
    return text


def escape_cell(text: str) -> str:
    return clean(text).replace("|", "\\|").replace("\n", "<br>")


def table_markdown(table: Table) -> str:
    rows: list[list[str]] = []
    for row in table.rows:
        values: list[str] = []
        seen_cells: set[int] = set()
        for cell in row.cells:
            identity = id(cell._tc)
            if identity in seen_cells:
                values.append("")
            else:
                seen_cells.add(identity)
                values.append(escape_cell(cell.text))
        if any(values):
            rows.append(values)

    if not rows:
        return ""
    if len(rows[0]) == 1:
        return "\n".join(f"> {row[0]}" for row in rows if row[0])

    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    body = normalized[1:] or [[""] * width]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def convert(
    source: Path,
    target: Path,
    *,
    sample_heading: str | None = None,
    drop_table_start: int | None = None,
    drop_table_end: int | None = None,
    drop_patterns: tuple[str, ...] = (),
) -> None:
    document = Document(source)
    output: list[str] = []
    table_index = -1
    mode = "all" if sample_heading is None else "before"

    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            text = clean(block.text)
            style = block.style.name if block.style else ""

            if sample_heading is not None:
                if mode == "before":
                    if style.startswith("Heading 1") and text == sample_heading:
                        mode = "body"
                    else:
                        continue
                elif mode == "body" and style.startswith("Heading 1") and text == "事实说明与样章验收":
                    mode = "sources"
                    output.append("## 资料来源与使用边界")
                    continue
                elif mode == "sources":
                    if style.startswith("Heading 2") and text == "四道验收门":
                        break
                    if style.startswith("Heading 2") and text == "案例事实与使用边界":
                        continue

            if any(pattern in text for pattern in drop_patterns):
                continue
            rendered = paragraph_markdown(block)
        else:
            table_index += 1
            if mode == "before":
                continue
            if (
                drop_table_start is not None
                and drop_table_end is not None
                and drop_table_start <= table_index <= drop_table_end
            ):
                continue
            table_text = clean(" ".join(cell.text for row in block.rows for cell in row.cells))
            if any(pattern in table_text for pattern in drop_patterns):
                continue
            rendered = table_markdown(block)

        if rendered:
            output.append(rendered)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n\n".join(output).strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--sample-heading")
    parser.add_argument("--drop-table-start", type=int)
    parser.add_argument("--drop-table-end", type=int)
    parser.add_argument("--drop-pattern", action="append", default=[])
    args = parser.parse_args()
    convert(
        args.source,
        args.target,
        sample_heading=args.sample_heading,
        drop_table_start=args.drop_table_start,
        drop_table_end=args.drop_table_end,
        drop_patterns=tuple(args.drop_pattern),
    )


if __name__ == "__main__":
    main()
