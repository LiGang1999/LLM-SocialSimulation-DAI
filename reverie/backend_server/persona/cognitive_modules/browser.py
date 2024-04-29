import sys
import requests
import re

class Browser: 
    def __init__(self, subscription_key = '6a33b69b1b7f4e0f92d2d72485fc3d7e'):
        self.subscription_key = subscription_key
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"

    def search(self, search_term):
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
        try:
            response = requests.get(self.search_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("请求出错:", e)
            return None

    @staticmethod
    def remove_html_tags(text):
        return re.sub('<[^>]+>', '', text)

    def process_results(self, search_results):
        if search_results:
            for result in search_results.get("webPages", {}).get("value", []):
                name = self.remove_html_tags(result["name"])
                snippet = self.remove_html_tags(result["snippet"])
                print(name)
                print(snippet)
                print()
        else:
            print("未能获取到搜索结果。")

    def run(self):
        search_term = input("请输入搜索词：")
        search_results = self.search(search_term)
        self.process_results(search_results)

if __name__ == "__main__":
    subscription_key = '6a33b69b1b7f4e0f92d2d72485fc3d7e'
    assert subscription_key

    bing_search = Browser(subscription_key)
    bing_search.run()
