# PDF Document MCP Server

> **By [MEOK AI Labs](https://meok.ai)** — Sovereign AI tools for everyone.

Document processing toolkit for AI agents. Extract text, convert to Markdown, merge PDFs, extract tables, and summarize documents -- all locally with no external API dependencies.

[![MCPize](https://img.shields.io/badge/MCPize-Listed-blue)](https://mcpize.com/mcp/pdf-document)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-255+_servers-purple)](https://meok.ai)

## Tools

| Tool | Description |
|------|-------------|
| `extract_text_from_pdf` | Extract text content from a PDF file |
| `convert_pdf_to_markdown` | Convert a PDF document to Markdown format |
| `merge_pdfs` | Merge multiple PDF files into a single document |
| `extract_tables` | Extract table-like structures from a PDF page |
| `summarize_document` | Generate a structural summary of a PDF |

## Quick Start

```bash
pip install mcp
git clone https://github.com/CSOAI-ORG/pdf-document-mcp.git
cd pdf-document-mcp
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "pdf-document": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/pdf-document-mcp"
    }
  }
}
```

## Pricing

| Plan | Price | Requests |
|------|-------|----------|
| Free | $0/mo | 20 calls/day |
| Pro | $9/mo | Unlimited + OCR support + batch processing |
| Enterprise | Contact us | Custom + priority support |

[Get on MCPize](https://mcpize.com/mcp/pdf-document)

## Part of MEOK AI Labs

This is one of 255+ MCP servers by MEOK AI Labs. Browse all at [meok.ai](https://meok.ai) or [GitHub](https://github.com/CSOAI-ORG).

---
**MEOK AI Labs** | [meok.ai](https://meok.ai) | nicholas@meok.ai | United Kingdom
