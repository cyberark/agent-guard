#!/usr/bin/env python3
"""
Test script to verify environment variable propagation through Agent Guard MCP Proxy.
This script simulates what happens when Claude Desktop sets environment variables
and they need to be passed through to the wrapped MCP server.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def create_test_mcp_server():
    """Create a simple test MCP server that prints environment variables."""
    test_server_content = '''
import os
import sys
print(f"TEST_ENV_VAR: {os.environ.get('TEST_ENV_VAR', 'NOT_SET')}", file=sys.stderr)
print(f"ANOTHER_VAR: {os.environ.get('ANOTHER_VAR', 'NOT_SET')}", file=sys.stderr)
# Simple MCP server that just exits
sys.exit(0)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_server_content)
        return f.name

def test_env_propagation():
    """Test that environment variables are propagated through the proxy."""
    print("Testing environment variable propagation...")
    
    # Create a test MCP server
    test_server_path = create_test_mcp_server()
    
    try:
        # Set test environment variables
        env = os.environ.copy()
        env['TEST_ENV_VAR'] = 'test_value_123'
        env['ANOTHER_VAR'] = 'another_value_456'
        
        # Run the Agent Guard proxy with the test server
        cmd = [
            sys.executable, '-m', 'agent_guard_core.cli.cli',
            'mcp-proxy', 'start',
            '-d',  # Enable debug mode
            '--cap', 'audit',
            sys.executable, test_server_path
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print(f"With environment variables: TEST_ENV_VAR={env['TEST_ENV_VAR']}, ANOTHER_VAR={env['ANOTHER_VAR']}")
        
        # Run the command and capture output
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/niv.rabin/code/cyberark/agent-guard"
        )
        
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")
        
        # Check if the environment variables were propagated
        if 'TEST_ENV_VAR: test_value_123' in result.stderr and 'ANOTHER_VAR: another_value_456' in result.stderr:
            print("✅ SUCCESS: Environment variables were propagated correctly!")
        else:
            print("❌ FAILED: Environment variables were not propagated correctly!")
        
    except subprocess.TimeoutExpired:
        print("⚠️  Test timed out (expected for some cases)")
    except Exception as e:
        print(f"❌ Error running test: {e}")
    finally:
        # Clean up
        Path(test_server_path).unlink()

if __name__ == "__main__":
    test_env_propagation()
