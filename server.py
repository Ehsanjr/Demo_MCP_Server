import os
import requests

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_PAT = os.getenv("CONFLUENCE_PAT")

if not CONFLUENCE_BASE_URL:
    raise RuntimeError("CONFLUENCE_BASE_URL is not set")

if not CONFLUENCE_PAT:
    raise RuntimeError("CONFLUENCE_PAT is not set")


# --------------------------------------------------
# MCP Server
# --------------------------------------------------

mcp = FastMCP("Confluence Server")


# --------------------------------------------------
# Confluence HTTP helper
# --------------------------------------------------

def confluence_get(endpoint: str, params: dict | None = None):

    url = f"{CONFLUENCE_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    headers = {
        "Authorization": f"Bearer {CONFLUENCE_PAT}",
        "Accept": "application/json",
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        verify=False,   # فعلاً برای تست
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# Tool 1 - List Spaces
# --------------------------------------------------

@mcp.tool()
def list_spaces(limit: int = 50) -> list[dict]:
    """
    List Confluence spaces available to the current user.
    """

    data = confluence_get(
        "/rest/api/space",
        {
            "limit": limit,
        },
    )

    spaces = []

    for space in data.get("results", []):
        spaces.append({
            "id": space.get("id"),
            "key": space.get("key"),
            "name": space.get("name"),
            "type": space.get("type"),
        })

    return spaces


# --------------------------------------------------
# Tool 2 - List Pages
# --------------------------------------------------

@mcp.tool()
def list_pages(
    space_key: str,
    limit: int = 5,
) -> list[dict]:
    """
    List pages from a Confluence space.

    Returns the page ID, title, type, status,
    and storage body returned by Confluence.
    """

    data = confluence_get(
        "/rest/api/content",
        {
            "spaceKey": space_key,
            "limit": limit,
            "expand": "body.storage",
        },
    )

    pages = []

    for page in data.get("results", []):
        pages.append({
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
            "status": page.get("status"),
            "body": (
                page.get("body", {})
                    .get("storage", {})
                    .get("value", "")
            ),
        })

    return pages


# --------------------------------------------------
# Tool 3 - Search Pages
# --------------------------------------------------

@mcp.tool()
def search_pages(
    space_key: str,
    keyword: str,
    limit: int = 20,
) -> list[dict]:
    """
    Search Confluence pages in a specific space.

    Searches page title and page content.
    """

    data = confluence_get(
        "/rest/api/content",
        {
            "spaceKey": space_key,
            "type": "page",
            "limit": limit,
            "expand": "body.storage",
        },
    )

    keyword_lower = keyword.lower()

    results = []

    for page in data.get("results", []):

        title = page.get("title", "")

        body = (
            page.get("body", {})
                .get("storage", {})
                .get("value", "")
        )

        if (
            keyword_lower in title.lower()
            or keyword_lower in body.lower()
        ):
            results.append({
                "id": page.get("id"),
                "title": title,
                "body": body,
            })

    return results


# --------------------------------------------------
# Tool 4 - Get Page
# --------------------------------------------------

@mcp.tool()
def get_page(page_id: str) -> dict:
    """
    Get the complete content of a Confluence page by ID.
    """

    data = confluence_get(
        f"/rest/api/content/{page_id}",
        {
            "expand": "body.storage,version,space",
        },
    )

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "status": data.get("status"),
        "space": data.get("space", {}).get("key"),
        "version": data.get("version", {}).get("number"),
        "body": (
            data.get("body", {})
                .get("storage", {})
                .get("value", "")
        ),
    }



@mcp.tool()
def list_child_pages(
    page_id: str,
    limit: int = 50,
) -> list[dict]:
    """
    List direct child pages of a Confluence page.
    """
    if limit is None:
        limit = 50

    data = confluence_get(
        f"/rest/api/content/{page_id}/child/page",
        {
            "limit": limit,
        },
    )


    pages = []

    for page in data.get("results", []):
        pages.append({
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
            "status": page.get("status"),
        })

    return pages


@mcp.tool()
def list_attachments(
    page_id: str,
    limit: int | None = None,
) -> list[dict]:
    """
    List attachments/files attached to a Confluence page.
    """

    if limit is None:
        limit = 50

    data = confluence_get(
        f"/rest/api/content/{page_id}/child/attachment",
        {
            "limit": limit,
        },
    )

    attachments = []

    for item in data.get("results", []):
        attachments.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "media_type": item.get("metadata", {}).get("mediaType"),
            "file_size": item.get("extensions", {}).get("fileSize"),
        })

    return attachments


@mcp.tool()
def find_page(
    space_key: str,
    title: str,
) -> list[dict]:
    """
    Find Confluence pages by exact title inside a specific space.
    Returns the real page IDs and titles from Confluence.
    """

    data = confluence_get(
        "/rest/api/content",
        {
            "spaceKey": space_key,
            "type": "page",
            "status": "current",
            "title": title,
            "limit": 20,
        },
    )

    pages = []

    for page in data.get("results", []):
        pages.append({
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
            "status": page.get("status"),
            "space": page.get("space", {}).get("key"),
        })

    return pages



@mcp.tool()
def list_attachments_by_page(
    space_key: str,
    page_title: str,
    limit: int | None = None,
) -> list[dict]:
    """
    Find a Confluence page by exact title in a space
    and return its attachments.
    """

    if limit is None:
        limit = 50

    # Step 1: Find the page
    page_data = confluence_get(
        "/rest/api/content",
        {
            "spaceKey": space_key,
            "type": "page",
            "status": "current",
            "title": page_title,
            "limit": 20,
        },
    )

    pages = page_data.get("results", [])

    if not pages:
        return []

    # Use the first exact-title match
    page_id = pages[0].get("id")

    if not page_id:
        return []

    # Step 2: Get attachments of that page
    attachment_data = confluence_get(
        f"/rest/api/content/{page_id}/child/attachment",
        {
            "limit": limit,
        },
    )

    attachments = []

    for item in attachment_data.get("results", []):
        attachments.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "media_type": (
                item.get("metadata", {})
                    .get("mediaType")
            ),
            "file_size": (
                item.get("extensions", {})
                    .get("fileSize")
            ),
        })

    return attachments


# --------------------------------------------------
# Run MCP
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")