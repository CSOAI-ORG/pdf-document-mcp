<div align="center">

# Pdf Document MCP

**MCP server for pdf document mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-pdf-document-mcp)](https://pypi.org/project/meok-pdf-document-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Pdf Document MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `extract_text_from_pdf` | Extract text content from a PDF file. Optionally specify page numbers |
| `convert_pdf_to_markdown` | Convert a PDF document to Markdown format. Detects headings based on |
| `merge_pdfs` | Merge multiple PDF files into a single document. |
| `extract_tables` | Extract table-like structures from a specific page in a PDF. |
| `summarize_document` | Generate a structural summary of a PDF: metadata, statistics (pages, |

## Installation

```bash
pip install meok-pdf-document-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pdf-document-mcp": {
      "command": "python",
      "args": ["-m", "meok_pdf_document_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
