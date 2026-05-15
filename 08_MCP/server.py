# Creating the MCP server

from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP('CustomMathMCP')

@mcp.tool()
def add(a: float, b: float) -> float:
    '''Adding two number'''
    print('MCP Add tool')
    return a+b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    '''Subtracting two numbers'''
    print('MCP Subtract tool')
    return a-b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    '''Multipling two numbers'''
    print('MCP Multiply tool')
    return a*b

@mcp.tool()
def square_root(x:float) -> float:
    '''Getting the Square root of a number'''
    print('MCP Square root Tool ')
    return math.sqrt(x)


if __name__ == '__main__':
    print('Starting the MCP Server')
    # mcp.run(transport='stdio')
    mcp.run(transport='streamable-http')