class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    def search(self, query: str, search_depth: str = "advanced", max_results: int = 5):
        return {"results": []}
