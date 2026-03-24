import os
import requests
from typing import Optional


class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
    
    def search_papers(self, query: str, limit: int = 10):
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,year,citationCount,externalIds,url"
        }
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_paper(self, paper_id: str, fields: Optional[str] = None):
        if fields is None:
            fields = "title,abstract,authors,year,citationCount,externalIds,url,openAccessPdf,fieldsOfStudy"
        url = f"{self.BASE_URL}/paper/{paper_id}"
        params = {"fields": fields}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_paper_pdf_url(self, paper_id: str) -> Optional[str]:
        paper = self.get_paper(paper_id)
        if paper.get("openAccessPdf"):
            return paper["openAccessPdf"].get("url")
        return None
