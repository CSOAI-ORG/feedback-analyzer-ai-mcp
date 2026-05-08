<div align="center">

# Feedback Analyzer Ai MCP

**MCP server for feedback analyzer ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-feedback-analyzer-ai-mcp)](https://pypi.org/project/meok-feedback-analyzer-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Feedback Analyzer Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `analyze_feedback` | Analyze customer feedback for sentiment breakdown with per-item scores. |
| `extract_themes` | Extract recurring themes from feedback using keyword matching. |
| `sentiment_trend` | Compute sentiment trend over time. Each item needs 'text' and 'date' (YYYY-MM-DD |
| `generate_summary` | Generate an executive summary of feedback with key takeaways and recommendations |

## Installation

```bash
pip install meok-feedback-analyzer-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "feedback-analyzer-ai": {
      "command": "python",
      "args": ["-m", "meok_feedback_analyzer_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
