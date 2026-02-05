"""
Mudrex MCP Server
=================

Model Context Protocol (MCP) server for Mudrex Futures Trading SDK.

This module provides a local MCP server that exposes Mudrex trading
functionality to Claude Desktop and other MCP clients.

Usage:
    Run the server directly:
        $ python -m mudrex.mcp
    
    Or import and use programmatically:
        >>> from mudrex.mcp import create_server, run_server
        >>> server = create_server(api_secret="your-secret")
        >>> run_server()

Configuration:
    Set the MUDREX_API_SECRET environment variable:
        $ export MUDREX_API_SECRET="your-api-secret"
        $ python -m mudrex.mcp
    
    Or configure in Claude Desktop's config:
        {
          "mcpServers": {
            "mudrex": {
              "command": "python",
              "args": ["-m", "mudrex.mcp"],
              "env": {
                "MUDREX_API_SECRET": "your-secret"
              }
            }
          }
        }
"""

from mudrex.mcp.server import create_server, run_server

__all__ = ["create_server", "run_server"]
