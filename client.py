import asyncio
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
    )

    async with Client(server_params) as client:

        # دریافت Toolهای موجود روی Server
        result = await client.list_tools()

        tools = result.tools

        print("Available tools:")

        for tool in tools:
            print(f"- {tool.name}")

        # -------------------------
        # list_files
        # -------------------------

        print("\n--- list_files ---")

        result = await client.call_tool(
            "list_files",
            {}
        )

        print(result)

        # -------------------------
        # search_in_files
        # -------------------------

        print("\n--- search_in_files ---")

        result = await client.call_tool(
            "search_in_files",
            {
                "keyword": "database"
            }
        )

        print(result)

        # -------------------------
        # read_file
        # -------------------------

        print("\n--- read_file ---")

        result = await client.call_tool(
            "read_file",
            {
                "filename": "database.py"
            }
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())