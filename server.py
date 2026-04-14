#!/usr/bin/env python3
"""
PDF Document MCP Server
========================
Document processing toolkit for AI agents. Extract text, convert to Markdown,
merge PDFs, extract tables, and summarize documents using PyMuPDF.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp PyMuPDF
Run:     python server.py
"""

import io
import json
import os
import re
import tempfile
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 20
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). Upgrade to Pro: https://mcpize.com/pdf-document-mcp/pro"
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

# Path traversal protection
BLOCKED_PATH_PATTERNS = ["/etc/", "/var/", "/proc/", "/sys/", "/dev/", ".."]


def _validate_file_path(file_path: str) -> Optional[str]:
    """Validate file path against traversal attacks. Returns error message or None."""
    for pattern in BLOCKED_PATH_PATTERNS:
        if pattern in file_path:
            return f"Access denied: path contains blocked pattern '{pattern}'"
    real = os.path.realpath(file_path)
    if not os.path.isfile(real):
        return f"File not found: {file_path}"
    return None


def _open_pdf(file_path: str):
    """Open a PDF file and return the fitz document."""
    import fitz
    path_err = _validate_file_path(file_path)
    if path_err:
        raise FileNotFoundError(path_err)
    return fitz.open(file_path)


def _extract_text(file_path: str, pages: Optional[list[int]] = None) -> dict:
    """Extract text from PDF, optionally from specific pages."""
    doc = _open_pdf(file_path)
    result_pages = []
    total_chars = 0

    for i, page in enumerate(doc):
        if pages and (i + 1) not in pages:
            continue
        text = page.get_text("text")
        total_chars += len(text)
        result_pages.append({
            "page": i + 1,
            "text": text,
            "char_count": len(text),
        })

    doc.close()
    return {
        "file": file_path,
        "total_pages": doc.page_count,
        "extracted_pages": len(result_pages),
        "total_characters": total_chars,
        "pages": result_pages,
    }


def _pdf_to_markdown(file_path: str) -> dict:
    """Convert PDF to Markdown with headings, bold, and structure."""
    import fitz
    doc = _open_pdf(file_path)
    md_parts = []
    md_parts.append(f"# {os.path.basename(file_path)}\n")

    for i, page in enumerate(doc):
        md_parts.append(f"\n---\n## Page {i + 1}\n")
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    line_text = ""
                    max_size = 0
                    is_bold = False
                    for span in line.get("spans", []):
                        line_text += span["text"]
                        max_size = max(max_size, span["size"])
                        if "bold" in span.get("font", "").lower():
                            is_bold = True

                    line_text = line_text.strip()
                    if not line_text:
                        continue

                    # Heuristic heading detection based on font size
                    if max_size >= 18:
                        md_parts.append(f"\n### {line_text}\n")
                    elif max_size >= 14 or is_bold:
                        md_parts.append(f"\n**{line_text}**\n")
                    else:
                        md_parts.append(line_text)

            elif block["type"] == 1:  # Image block
                md_parts.append("\n[Image]\n")

        md_parts.append("")

    doc.close()
    markdown = "\n".join(md_parts)
    return {
        "file": file_path,
        "total_pages": doc.page_count,
        "markdown": markdown,
        "char_count": len(markdown),
    }


def _merge_pdfs(file_paths: list[str], output_path: str) -> dict:
    """Merge multiple PDFs into one."""
    import fitz
    merged = fitz.open()
    page_counts = []

    for path in file_paths:
        if not os.path.isfile(path):
            return {"error": f"File not found: {path}"}
        src = fitz.open(path)
        merged.insert_pdf(src)
        page_counts.append({"file": path, "pages": src.page_count})
        src.close()

    merged.save(output_path)
    total = merged.page_count
    merged.close()

    return {
        "output": output_path,
        "total_pages": total,
        "source_files": page_counts,
    }


def _extract_tables(file_path: str, page_num: int = 1) -> dict:
    """Extract table-like structures from a PDF page using text position analysis."""
    import fitz
    doc = _open_pdf(file_path)

    if page_num < 1 or page_num > doc.page_count:
        doc.close()
        return {"error": f"Page {page_num} out of range (1-{doc.page_count})"}

    page = doc[page_num - 1]
    blocks = page.get_text("dict")["blocks"]

    # Group text spans by vertical position (y-coordinate) to detect rows
    rows_by_y: dict[int, list[dict]] = defaultdict(list)

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                y_key = round(span["bbox"][1] / 4) * 4  # Group within 4pt bands
                rows_by_y[y_key].append({
                    "text": span["text"].strip(),
                    "x": span["bbox"][0],
                    "font_size": span["size"],
                })

    # Sort rows by y position, then cells within each row by x position
    tables = []
    current_table = []
    prev_y = None

    for y_key in sorted(rows_by_y.keys()):
        cells = sorted(rows_by_y[y_key], key=lambda c: c["x"])
        row_texts = [c["text"] for c in cells if c["text"]]

        if len(row_texts) < 2:
            # Single-column row -- if we were building a table, finish it
            if current_table and len(current_table) >= 2:
                tables.append(current_table)
            current_table = []
            continue

        # Check for gap from previous row (new table)
        if prev_y is not None and y_key - prev_y > 20:
            if current_table and len(current_table) >= 2:
                tables.append(current_table)
            current_table = []

        current_table.append(row_texts)
        prev_y = y_key

    if current_table and len(current_table) >= 2:
        tables.append(current_table)

    doc.close()

    # Convert to structured format
    structured_tables = []
    for i, table in enumerate(tables):
        header = table[0] if table else []
        rows = table[1:] if len(table) > 1 else []
        structured_tables.append({
            "table_index": i + 1,
            "header": header,
            "rows": rows,
            "row_count": len(rows),
            "column_count": len(header),
        })

    return {
        "file": file_path,
        "page": page_num,
        "tables_found": len(structured_tables),
        "tables": structured_tables,
    }


def _summarize_document(file_path: str) -> dict:
    """Generate a structural summary of a PDF document."""
    import fitz
    doc = _open_pdf(file_path)
    metadata = doc.metadata or {}

    # Gather statistics
    total_chars = 0
    total_words = 0
    total_images = 0
    page_summaries = []
    all_headings = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        chars = len(text)
        words = len(text.split())
        total_chars += chars
        total_words += words

        # Count images
        img_list = page.get_images(full=True)
        total_images += len(img_list)

        # Detect headings (larger font text)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["size"] >= 14 and span["text"].strip():
                        heading = span["text"].strip()[:100]
                        if heading and len(heading) > 3:
                            all_headings.append({
                                "text": heading,
                                "page": i + 1,
                                "font_size": round(span["size"], 1),
                            })

        # First line as page summary
        first_line = text.strip().split("\n")[0][:120] if text.strip() else ""
        page_summaries.append({
            "page": i + 1,
            "words": words,
            "images": len(img_list),
            "first_line": first_line,
        })

    doc.close()

    # Deduplicate headings
    seen = set()
    unique_headings = []
    for h in all_headings:
        if h["text"] not in seen:
            seen.add(h["text"])
            unique_headings.append(h)

    return {
        "file": file_path,
        "metadata": {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "creation_date": metadata.get("creationDate", ""),
        },
        "statistics": {
            "total_pages": doc.page_count,
            "total_characters": total_chars,
            "total_words": total_words,
            "total_images": total_images,
            "avg_words_per_page": round(total_words / max(doc.page_count, 1)),
        },
        "headings": unique_headings[:50],
        "page_summaries": page_summaries[:20],
    }


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "PDF Document MCP",
    instructions="Document processing toolkit: extract text from PDFs, convert to Markdown, merge files, extract tables, and summarize documents. By MEOK AI Labs.")


@mcp.tool()
def extract_text_from_pdf(file_path: str, pages: Optional[list[int]] = None) -> dict:
    """Extract text content from a PDF file. Optionally specify page numbers
    (1-indexed) to extract from specific pages only.

    Args:
        file_path: Absolute path to the PDF file
        pages: Optional list of page numbers to extract (e.g. [1, 3, 5])
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _extract_text(file_path, pages)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def convert_pdf_to_markdown(file_path: str) -> dict:
    """Convert a PDF document to Markdown format. Detects headings based on
    font size, preserves bold text, and marks image locations.

    Args:
        file_path: Absolute path to the PDF file
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _pdf_to_markdown(file_path)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def merge_pdfs(file_paths: list[str], output_path: str) -> dict:
    """Merge multiple PDF files into a single document.

    Args:
        file_paths: List of absolute paths to PDF files to merge (in order)
        output_path: Absolute path where the merged PDF will be saved
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _merge_pdfs(file_paths, output_path)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def extract_tables(file_path: str, page_num: int = 1) -> dict:
    """Extract table-like structures from a specific page in a PDF.
    Uses text position analysis to detect rows and columns.

    Args:
        file_path: Absolute path to the PDF file
        page_num: Page number to extract tables from (1-indexed, default 1)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _extract_tables(file_path, page_num)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def summarize_document(file_path: str) -> dict:
    """Generate a structural summary of a PDF: metadata, statistics (pages,
    words, images), detected headings/outline, and per-page summaries.

    Args:
        file_path: Absolute path to the PDF file
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _summarize_document(file_path)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
