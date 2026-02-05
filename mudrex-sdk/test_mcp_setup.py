"""
Test MCP Server Setup
======================

Quick test to verify the MCP server can be imported and initialized.
This doesn't require API credentials and won't make any actual API calls.
"""

def test_mcp_imports():
    """Test that MCP module can be imported."""
    try:
        from mudrex.mcp import create_server, run_server
        print("✓ MCP module imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import MCP module: {e}")
        print("\nMake sure to install with MCP support:")
        print("  pip install -e '.[mcp]'")
        return False


def test_mcp_tools_module():
    """Test that tools module can be imported."""
    try:
        from mudrex.mcp.tools import register_tools
        print("✓ MCP tools module imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import tools module: {e}")
        return False


def test_mcp_server_module():
    """Test that server module can be imported."""
    try:
        from mudrex.mcp.server import create_server, run_server
        print("✓ MCP server module imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import server module: {e}")
        return False


def test_mcp_dependencies():
    """Test that MCP dependencies are installed."""
    try:
        from mcp.server.fastmcp import FastMCP
        print("✓ FastMCP dependency is installed")
        return True
    except ImportError:
        print("✗ FastMCP not installed")
        print("\nInstall with:")
        print("  pip install -e '.[mcp]'")
        return False


def main():
    """Run all tests."""
    print("Testing MCP Server Setup")
    print("=" * 50)
    
    tests = [
        test_mcp_dependencies,
        test_mcp_imports,
        test_mcp_tools_module,
        test_mcp_server_module,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed!")
        print("\nYour MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Set your API secret: export MUDREX_API_SECRET='your-secret'")
        print("2. Run the server: python -m mudrex.mcp")
        print("3. Or configure Claude Desktop - see README.md")
    else:
        print("✗ Some tests failed")
        print("\nPlease install MCP dependencies:")
        print("  pip install -e '.[mcp]'")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
