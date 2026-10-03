from pathlib import Path

from mcp.server import MCPServer


mcp = MCPServer("Local File Server")

WORKSPACE = Path(__file__).parent / "workspace"


@mcp.tool()
def list_files() -> list[str]:
    """List all files in the workspace."""

    return [
        file.name
        for file in WORKSPACE.iterdir()
        if file.is_file()
    ]


@mcp.tool()
def read_file(filename: str) -> str:
    """Read a text file from the workspace."""

    file_path = (WORKSPACE / filename).resolve()

    # جلوگیری از دسترسی خارج از workspace
    if WORKSPACE.resolve() not in file_path.parents:
        raise ValueError("Access denied")

    if not file_path.is_file():
        raise FileNotFoundError(
            f"File '{filename}' not found."
        )

    return file_path.read_text(encoding="utf-8")


@mcp.tool()
def search_in_files(keyword: str) -> list[str]:
    """Find files containing a specific keyword."""

    results = []

    for file_path in WORKSPACE.iterdir():

        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            continue

        if keyword.lower() in content.lower():
            results.append(file_path.name)

    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")