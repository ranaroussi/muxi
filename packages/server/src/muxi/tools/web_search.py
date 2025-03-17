"""
Web search tool implementation.

This module provides a tool for performing web searches and retrieving
information from the internet.
"""

import logging
import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from muxi.server.tools.base import BaseTool
from muxi.server.config import config

logger = logging.getLogger(__name__)


class WebSearch(BaseTool):
    """
    A tool for performing web searches.

    This tool allows agents to search the web for information using a
    search engine API. It returns search results including titles, snippets,
    and URLs.
    """

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """
        Initialize the web search tool.

        Args:
            api_key: Optional API key. If not provided, will use the one from config.
            search_engine_id: Optional search engine ID. If not provided, will use the one from config.
        """
        self.api_key = api_key or config.tools.google_search_api_key
        self.search_engine_id = search_engine_id or config.tools.search_engine_id

        if not self.api_key:
            logger.warning(
                "Search API key not provided. Web search tool will not work."
            )

        if not self.search_engine_id:
            logger.warning(
                "Search engine ID not provided. Web search tool will not work."
            )

    @property
    def name(self) -> str:
        """Return the name of the web search tool."""
        return "web_search"

    @property
    def description(self) -> str:
        """Return the description of the web search tool."""
        return (
            "Searches the web for information on the given query. "
            "Useful for finding current information, facts, news, "
            "and data that may not be in the model's training data. "
            "Input should be a search query string."
        )

    async def execute(
        self,
        query: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the web search tool with the given query.

        Args:
            query: The search query string.
            num_results: Number of results to return (default: 5).

        Returns:
            A dictionary containing the search results.
            If successful, the dictionary will have a "results" key with a list
            of search results. Each result has "title", "link", and "snippet".
            If there's an error, the dictionary will have an "error" key.
        """
        if not query or not isinstance(query, str):
            return {"error": "Query must be a non-empty string"}

        if not self.api_key or not self.search_engine_id:
            return {
                "error": "Search API key or search engine ID is missing. "
                         "Please configure these in your .env file."
            }

        try:
            # Build the search URL
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # API limit is 10 per page
            }

            base_url = "https://www.googleapis.com/customsearch/v1?"
            url = base_url + urllib.parse.urlencode(params)

            # Make the request
            request = urllib.request.Request(url)
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode())

            # Process the results
            search_results = []
            if 'items' in data:
                for item in data['items'][:num_results]:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })

            result_msg = f"Found {len(search_results)} results for query: {query}"
            return {
                "result": result_msg,
                "search_results": search_results
            }

        except urllib.error.HTTPError as e:
            logger.error(f"HTTP error during search: {e.code}", exc_info=True)
            return {"error": f"HTTP error during search: {e.code} {e.reason}"}

        except urllib.error.URLError as e:
            logger.error(f"URL error during search: {e.reason}", exc_info=True)
            return {"error": f"URL error during search: {e.reason}"}

        except Exception as e:
            logger.error(f"Error during web search: {str(e)}", exc_info=True)
            return {"error": f"Error during web search: {str(e)}"}
