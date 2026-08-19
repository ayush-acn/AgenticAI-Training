# From the langgraph Sereies 

from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP('Math')

@mcp.tool()
def add(a: int, b: int) -> int:
    '''Adding 2 numbers'''
    print(f'MCP tool add: {a} and {b}')
    return a+b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    '''Subtracting 2 numbers'''
    print(f'MCP tool subtract: {a} and {b}')
    return a-b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    '''Multiplying 2 numbers'''
    print(f'MCP tool multiply: {a} and {b}')
    return a*b

@mcp.tool()
def divide(a: int, b: int) -> int:
    '''Divide 2 numbers'''
    if b == 0:
        raise ValueError('Cannot divide by zero')
    print(f'MCP tool divide: {a} and {b}')
    return a/b

if __name__ == '__main__':
    print('Strating MCP Server')
    mcp.run(transport='stdio')