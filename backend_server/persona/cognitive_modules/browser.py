"""
Author: Siyu Chen (3210101016@zju.edu.cn)

File: browser.py
"""

import re
import sys

import requests
from bs4 import BeautifulSoup
from utils.config import google_api_cx, google_api_key


class SearchEngine:
    def __init__(self):
        # nothing is done here
        pass

    def search(self, query):
        """
        Search for the query on the web.

        Args:
            query (str): The sentence to search for.

        Returns:
            A list of dictionaries, each containing the following keys:
            [ {"link" : link , "title" : title, "snippet" : snippet } ... ]
            where link is the URL of the search result, title is the title of the search result, and snippet is the snippet of the search result.
        """
        raise NotImplementedError(
            "Method 'search' not implemented in abstract class 'SearchEngine'."
        )


class GoogleSearch(SearchEngine):

    def __init__(self, api_key=google_api_key, cx=google_api_cx):
        self.api_key = api_key
        self.cx = cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        super().__init__()

    def search(self, query):
        params = {"key": self.api_key, "cx": self.cx, "q": query}
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            try:
                json = response.json()
                return [
                    {"link": item["link"], "title": item["title"], "snippet": item["snippet"]}
                    for item in json["items"]
                ]
            except Exception as e:
                return []

        else:
            return []


class Browser:

    def __init__(self):
        pass

    def browse(self, link):
        """
        Browse the given URL and return the plain text content of the page.

        Args:
            url (str): The URL of the web page to browse.

        Returns:
            str: The plain text content of the page.
        """
        try:
            # Send a GET request to the URL
            response = requests.get(link)

            # Check if the request was successful
            response.raise_for_status()

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, "lxml")

            # Extract the plain text from the parsed HTML
            plain_text = soup.get_text(separator="\n", strip=True)

            return plain_text

        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


# some simple tests

if __name__ == "__main__":
    search_engine = GoogleSearch()
    search_results = search_engine.search("python programming")
    print(search_results)
    browser = Browser()
    print(browser.browse(search_results[0]["link"]))
