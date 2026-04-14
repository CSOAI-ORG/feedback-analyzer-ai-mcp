#!/usr/bin/env python3
"""MEOK AI Labs — feedback-analyzer-ai-mcp MCP Server. Analyze customer feedback for sentiment and themes."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
import json

# In-memory store (replace with DB in production)
_store = {}

server = Server("feedback-analyzer-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="analyze_feedback", description="Analyze customer feedback", inputSchema={"type":"object","properties":{"feedback":{"type":"array","items":{"type":"string"}}},"required":["feedback"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "analyze_feedback":
            positive = sum(1 for f in args["feedback"] if any(w in f.lower() for w in ["good", "great", "love", "excellent"]))
            negative = sum(1 for f in args["feedback"] if any(w in f.lower() for w in ["bad", "poor", "hate", "terrible"]))
            return [TextContent(type="text", text=json.dumps({"positive": positive, "negative": negative, "total": len(args["feedback"])}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="feedback-analyzer-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())