# PDF Document MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

Document processing toolkit for AI agents. Extract text, convert to Markdown, merge PDFs, extract tables, and summarize documents -- all locally with no external API dependencies.

## Tools

| Tool | Description |
|------|-------------|
| `extract_text_from_pdf` | Extract text from all or specific pages of a PDF |
| `convert_pdf_to_markdown` | Convert PDF to structured Markdown with heading detection |
| `merge_pdfs` | Merge multiple PDF files into a single document |
| `extract_tables` | Extract table structures from a PDF page using position analysis |
| `summarize_document` | Generate metadata, statistics, headings, and per-page summaries |

## Installation

```bash
pip install mcp PyMuPDF
```

No external services, API keys, or cloud dependencies required. All processing happens locally.

## Usage

### Run the server

```bash
python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "pdf-document": {
      "command": "python",
      "args": ["/path/to/pdf-document-mcp/server.py"]
    }
  }
}
```

### Example calls

**Extract text from a PDF:**
```
Tool: extract_text_from_pdf
Input: {"file_path": "/Users/me/documents/report.pdf"}
Output: {"total_pages": 12, "total_characters": 48320, "pages": [{"page": 1, "text": "...", "char_count": 4210}, ...]}
```

**Extract specific pages only:**
```
Tool: extract_text_from_pdf
Input: {"file_path": "/Users/me/documents/report.pdf", "pages": [1, 3, 5]}
Output: {"extracted_pages": 3, "pages": [...]}
```

**Convert PDF to Markdown:**
```
Tool: convert_pdf_to_markdown
Input: {"file_path": "/Users/me/documents/whitepaper.pdf"}
Output: {"markdown": "# whitepaper.pdf\n\n---\n## Page 1\n\n### Introduction\n\nThis paper presents...", "char_count": 15200}
```

**Extract tables:**
```
Tool: extract_tables
Input: {"file_path": "/Users/me/documents/financials.pdf", "page_num": 3}
Output: {"tables_found": 2, "tables": [{"header": ["Quarter", "Revenue", "Profit"], "rows": [["Q1", "$1.2M", "$400K"], ...]}]}
```

**Merge multiple PDFs:**
```
Tool: merge_pdfs
Input: {"file_paths": ["/tmp/part1.pdf", "/tmp/part2.pdf", "/tmp/part3.pdf"], "output_path": "/tmp/combined.pdf"}
Output: {"output": "/tmp/combined.pdf", "total_pages": 28}
```

**Summarize a document:**
```
Tool: summarize_document
Input: {"file_path": "/Users/me/documents/thesis.pdf"}
Output: {"statistics": {"total_pages": 45, "total_words": 12500, "total_images": 8}, "headings": [...], "metadata": {"author": "...", "title": "..."}}
```

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 20 calls/day | $0 |
| Pro | Unlimited + OCR support + batch processing | $9/mo |
| Enterprise | Custom + priority support | Contact us |

## License

MIT
