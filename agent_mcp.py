import asyncio
import sys
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():

    # MCP Client
    client = MultiServerMCPClient({
        "local_files": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["server.py"],
        },
    })

    tools = await client.get_tools()

    print("MCP Tools:")
    for tool in tools:
        print("-", tool.name)

    # Local LLM
    llm = ChatOllama(
        model="llama3.2"
    )

    # LangChain Agent
    agent = create_agent(
        model=llm,
        tools=tools,
    )

    # درخواست کاربر
    result = await agent.ainvoke({
    "messages": [
        {
            "role": "user",
            "content": """
                List all attachments of the page "R&D" in the "kimia" space.
                Return only the exact file names returned by the tool.
                Do not invent anything.
            """
        }
    ]
})
    print("\nAnswer:")
    print(result["messages"][-1].content)

    print("\nAll messages:")

    for message in result["messages"]:
        print("\n---")
        print("TYPE:", type(message))
        print("CONTENT:", message.content)
        print("TOOL CALLS:", getattr(message, "tool_calls", None))








if __name__ == "__main__":
    asyncio.run(main())