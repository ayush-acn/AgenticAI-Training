# From the langchain tutorial 
import os
import asyncio
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage


# 1. Loading the Env 
load_dotenv()
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true" # Enable LangSmith tracing
os.environ['LANGSMITH_PROJECT'] = 'LangGraphTraining' 

# main method to run mcp client
async def main():
    print('Runing MCP Client')
    llm = ChatBedrockConverse(model= "us.anthropic.claude-sonnet-4-6")
    
    client = MultiServerMCPClient({
        'time': {
            'transport': 'stdio',
            'command': 'uvx',
            'args': ['mcp-server-time', '--local-timezone=India/Kolkata']
        },
        'calculator': {
            'transport': 'stdio',
            'command': 'uvx',
            'args': ['mcp-server-calculator']
        },
        'kiwi-flight-search': {
            'transport': 'streamable_http',
            'url': 'https://mcp.kiwi.com'
        },
        'yahoo-finance-server': {
            'transport': 'stdio',
            'command': 'uvx',
            'args': ['yahoo-finance-server']
        }
    })

    # Now need to fetch the MCP tools
    tools = await client.get_tools()
    print('Available tools from MCP servers:', [tool.name for tool in tools])

    # Binding the tools
    llm_with_tools = llm.bind_tools(tools)

    # Tool Node
    tool_node = ToolNode(tools)

    async def call_model(state: MessagesState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    # Router
    def should_continue(state: MessagesState):
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "tools"
        return "__end__"
    
    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue, {
        "tools": "tools",
        "__end__": END,
    })
    builder.add_edge("tools", "call_model")

    graph = builder.compile(checkpointer=MemorySaver())


    # IMPORTANT: thread_id must be inside config["configurable"].
    config = {
        'configurable': {
            'thread_id': '1',
        }
    }

    input_1 = {'messages': [HumanMessage(content="what's (3 + 5 * 23 / 5) x 12?")]}
    input_2 = {'messages': [HumanMessage(content="What time is it in India now?")]}
    input_3 = {'messages': [HumanMessage(content="Find me a flight from Delhi to London for tomorrow.")]}
    input_4 = {'messages': [HumanMessage(content="get me the stock price of AAPL")]}

    result_1 = await graph.ainvoke(input_1, config=config)
    print('Result 1:', result_1['messages'][-1].content)
    print('-----')

    result_2 = await graph.ainvoke(input_2, config=config)
    print('Result 2:', result_2['messages'][-1].content)
    print('-----')

    result_3 = await graph.ainvoke(input_3, config=config)
    print('Result 3:', result_3['messages'][-1].content)
    print('-----')

    result_4 = await graph.ainvoke(input_4, config=config)
    print('Result 4:', result_4['messages'][-1].content)
    print('-----')

if __name__ == "__main__":
    asyncio.run(main())