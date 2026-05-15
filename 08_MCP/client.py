# Creating MCP Client

import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
BASE_URL = os.getenv('OPENAI_BASE_URL')

# LangSmith Tracing
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true" 
os.environ['LANGSMITH_PROJECT'] = 'AgenticAITraining' 



async def main():
    print('Starting the MCP Client')
    model = ChatOpenAI(
        api_key = API_KEY,
        base_url= BASE_URL,
        model = 'gpt-5.1'
    )

    # Defining the MCP client - STDIO
    # client = MultiServerMCPClient(
    #     {
    #         'math': {
    #             'command': 'python',
    #             'args': [r'C:\Data\Codes\AgenticAITraining\Lanchain_Azure_openAI\08_MCP\server.py'],
    #             'transport': 'stdio'
    #         }
    #     }
    # )

    client = MultiServerMCPClient(
        {
            # 'math': {
            #     'command': 'python',
            #     'args': [r'C:\Data\Codes\AgenticAITraining\Lanchain_Azure_openAI\08_MCP\server.py'],
            #     'transport': 'stdio'
            # },
            "kiwi-com-flight-search": {
                "transport": "streamable-http",
                "url": "https://mcp.kiwi.com"
            },
             "math": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8000/mcp",  # URL of your MCP server
                "timeout": 30  # Increase timeout to 30 seconds
            },
        }
    )

    tools = await client.get_tools()
    print("Available tools for the MCP Server", [tool.name for tool in tools])

    prompt = 'You have access to a tool. Use the tool to help answer user queries.'
    agent = create_agent(model, tools, system_prompt=prompt)

    msg1 = {'messages': HumanMessage('what is the root of (1+6*4)')}
    msg2 = {'messages': HumanMessage('Find me a flight from Delhi to London for 23-May-26.')}
    msg3 = {'messages': HumanMessage('What is the lowest total cost of the London to Delhi and then Delhi to Jabalpur Flight, use only the available tools for the task.')}

    try: 
        result = await agent.ainvoke(msg3)
        print('Result :', result['messages'][-1].content)
        print('-'*30)
    except Exception as e:
        print("Error in with msg1 generation {e}")
    

if __name__ == '__main__':
    asyncio.run(main())