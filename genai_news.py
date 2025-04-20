# Refactored GenAI News Tool to work with MCP (FastMCP)

import os
import json
import hashlib
import requests
import feedparser
import math

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Memory storage path
MEMORY_FILE = "genai_news_memory.json"

# Create MCP agent
mcp = FastMCP("GenAI News Agent")

# Define data models
class NewsItem(BaseModel):
    title: str
    url: str
    source: str
    published: Optional[str] = None
    authors: Optional[List[str]] = None
    summary: Optional[str] = None
    points: Optional[int] = None

class NewsResponse(BaseModel):
    news: List[NewsItem]
    count: int

class MemoryUpdateResponse(BaseModel):
    new_items: List[NewsItem]
    count: int
    memory_size: int

# Utility functions
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"links": {}, "last_run": None}

def save_memory(memory):
    memory["last_run"] = datetime.now().isoformat()
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def is_new_link(url, memory):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return url_hash not in memory["links"]

def add_to_memory(url, metadata, memory):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    memory["links"][url_hash] = {
        "url": url,
        "date_added": datetime.now().isoformat(),
        "metadata": metadata or {}
    }

# Tool: Fetch GenAI News
@mcp.tool()
def latest_genai_news() -> NewsResponse:
    all_news = []

    # Medium
    try:
        feed = feedparser.parse("https://medium.com/feed/tag/artificial-intelligence")
        for entry in feed.entries:
            all_news.append(NewsItem(
                title=entry.title,
                url=entry.link,
                published=entry.published,
                source="Medium",
                summary=entry.get('summary', '')[:400] + '...' if entry.get('summary') else None
            ))
    except Exception as e:
        print(f"Medium fetch error: {str(e)}")

    # arXiv
    try:
        feed = feedparser.parse("http://export.arxiv.org/api/query?search_query=generative+AI&sortBy=lastUpdatedDate&max_results=10")
        for entry in feed.entries:
            all_news.append(NewsItem(
                title=entry.title,
                url=entry.link,
                published=entry.published,
                authors=[author.name for author in entry.authors],
                source="arXiv",
                summary=entry.summary[:400] + '...' if hasattr(entry, 'summary') else None
            ))
    except Exception as e:
        print(f"arXiv fetch error: {str(e)}")

    # Hacker News
    #try:
    #    response = requests.get("https://hn.algolia.com/api/v1/search_by_date", params={"query": "AI", "tags": "story", "numericFilters": "points>10"})
    #    results = response.json()
    #    for hit in results.get("hits", []):
    #        if hit.get("url"):
    #            all_news.append(NewsItem(
    #                title=hit.get("title"),
    #                url=hit.get("url"),
    #                points=hit.get("points"),
    #                source="Hacker News"
    #            ))
    #except Exception as e:
    #    print(f"Hacker News fetch error: {str(e)}")

    # Sort
    with_date = [item for item in all_news if item.published]
    without_date = [item for item in all_news if not item.published]
    with_date.sort(key=lambda x: x.published, reverse=True)
    sorted_news = with_date + without_date

    return NewsResponse(news=sorted_news, count=len(sorted_news))

# Tool: Filter and Update Memory
#@mcp.tool()
#def filter_and_update_memory(news_items: List[NewsItem]) -> MemoryUpdateResponse:
#    memory = load_memory()
#    new_items = []

#    for item in news_items:
#        if is_new_link(item.url, memory):
#            new_items.append(item)
#            metadata = {
#                "title": item.title,
#                "source": item.source,
#                "published": item.published
#            }
#            if item.authors:
#                metadata["authors"] = item.authors
#            if item.points:
#                metadata["points"] = item.points
#            add_to_memory(item.url, metadata, memory)

#    save_memory(memory)
#    return MemoryUpdateResponse(new_items=new_items, count=len(new_items), memory_size=len(memory["links"]))

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
