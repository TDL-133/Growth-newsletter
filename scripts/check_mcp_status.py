#!/usr/bin/env python3
"""
Check MCP tools availability and configuration
"""

import os
import sys
import json
import subprocess

def check_warp_config():
    """Check if Warp MCP config exists"""
    warp_config = os.path.expanduser("~/.warp/mcp.json")
    
    if os.path.exists(warp_config):
        print(f"✅ Warp MCP config found: {warp_config}")
        with open(warp_config, 'r') as f:
            config = json.load(f)
            print(f"📋 Configured MCP servers: {list(config.get('mcpServers', {}).keys())}")
        return True
    else:
        print(f"❌ No Warp MCP config at {warp_config}")
        print("\n💡 To configure MCP in Warp:")
        print("   1. Open Warp Settings")
        print("   2. Go to Features > Model Context Protocol")
        print("   3. Add MCP servers")
        return False

def check_env_vars():
    """Check MCP-related environment variables"""
    mcp_vars = ['FIRECRAWL_API_KEY', 'TAVILY_API_KEY', 'BRIGHTDATA_API_KEY']
    
    print("\n🔑 Environment variables:")
    for var in mcp_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * 20}{value[-4:]}")
        else:
            print(f"   ❌ {var}: Not set")

def test_mcp_import():
    """Test if MCP Python package is available"""
    try:
        import anthropic
        print("\n✅ Anthropic package available")
    except ImportError:
        print("\n❌ Anthropic package not installed")
        print("   Install: pip install anthropic")

def main():
    print("=" * 60)
    print("MCP CONFIGURATION CHECKER")
    print("=" * 60)
    
    check_warp_config()
    check_env_vars()
    test_mcp_import()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    print("""
The 'Transport closed' error means MCP servers are not running.

In Warp Terminal, MCP tools are provided by external servers that
need to be configured and running.

SOLUTION:
1. This session is in Warp, but MCP servers aren't connected
2. MCP tools (firecrawl, tavily, browser) require server connections
3. These servers must be configured in Warp settings

ALTERNATIVE:
Since MCP isn't available, I'll use direct HTTP requests to scrape
growth marketing sources and get real URLs.

Run this instead:
  python3 scripts/collect_real_articles.py
  
This will scrape directly without MCP.
""")

if __name__ == '__main__':
    main()
