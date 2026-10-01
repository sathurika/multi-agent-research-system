from tavily import TavilyClient

from config.settings import get_settings


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return structured results."""

    settings = get_settings()

    client = TavilyClient(api_key=settings.tavily_api_key)

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
    )

    results = []

    for result in response.get("results", []):
        results.append(
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
            }
        )

    return results
if __name__ == "__main__":
    results = search_web("latest developments in RAG systems")

    for result in results:
        print("\nTITLE:", result["title"])
        print("URL:", result["url"])
        print("CONTENT:", result["content"][:300])