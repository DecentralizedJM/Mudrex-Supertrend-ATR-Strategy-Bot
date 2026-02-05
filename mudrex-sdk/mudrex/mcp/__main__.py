"""
Entry point for running the Mudrex MCP server.

Usage:
    python -m mudrex.mcp
"""

from mudrex.mcp.server import run_server

if __name__ == "__main__":
    run_server()
