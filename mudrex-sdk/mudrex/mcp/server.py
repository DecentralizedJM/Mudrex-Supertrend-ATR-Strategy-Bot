"""
MCP Server for Mudrex Trading SDK
==================================

Implements a local MCP server that exposes Mudrex trading functionality
to Claude Desktop and other MCP clients.
"""

import os
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mudrex.client import MudrexClient
from mudrex.mcp.tools import register_tools

logger = logging.getLogger(__name__)


def create_server(
    api_secret: Optional[str] = None,
    base_url: Optional[str] = None,
) -> FastMCP:
    """
    Create and configure the MCP server with Mudrex trading tools.
    
    Args:
        api_secret: Mudrex API secret key (defaults to MUDREX_API_SECRET env var)
        base_url: Optional custom API base URL
        
    Returns:
        Configured FastMCP server instance
    """
    # Get API credentials from environment if not provided
    api_secret = api_secret or os.getenv("MUDREX_API_SECRET")
    
    if not api_secret:
        raise ValueError(
            "MUDREX_API_SECRET environment variable or api_secret parameter is required. "
            "Get your API key from: https://trade.mudrex.com/settings/api-keys"
        )
    
    # Initialize MCP server
    mcp = FastMCP("mudrex-trading")
    
    # Initialize Mudrex client
    logger.info("Initializing Mudrex client...")
    client_kwargs = {"api_secret": api_secret}
    if base_url:
        client_kwargs["base_url"] = base_url
    
    client = MudrexClient(**client_kwargs)
    
    # Register all trading tools
    logger.info("Registering Mudrex trading tools...")
    register_tools(mcp, client)
    
    logger.info("MCP server ready with %d tools", len(mcp._tools))
    
    return mcp


def run_server(
    api_secret: Optional[str] = None,
    base_url: Optional[str] = None,
) -> None:
    """
    Run the MCP server (blocking).
    
    This starts the server and handles incoming MCP requests over STDIO.
    
    Args:
        api_secret: Mudrex API secret key (defaults to MUDREX_API_SECRET env var)
        base_url: Optional custom API base URL
    """
    # Configure logging
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    try:
        # Create and run server
        mcp = create_server(api_secret=api_secret, base_url=base_url)
        logger.info("Starting Mudrex MCP server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_server()
