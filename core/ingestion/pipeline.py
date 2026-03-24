import os
from typing import List, Dict
from dataclasses import asdict
import json

from .semantic_scholar import SemanticScholarClient
from .pdf_parser import PDFParser, ParsedPaper


class IngestionPipeline:
    def __init__(self):
        self.semantic_scholar = SemanticScholarClient()
        self.pdf_parser = PDFParser()
    
    def run(self, topic: str, limit: int = 5) -> List[Dict]:
        papers_data = self.semantic_scholar.search_papers(topic, limit=limit)
        
        results = []
        for i, paper in enumerate(papers_data.get("data", [])):
            paper_id = paper.get("paperId")
            if not paper_id:
                continue
            
            try:
                pdf_url = self.semantic_scholar.get_paper_pdf_url(paper_id)
                if not pdf_url:
                    print(f"No PDF available for: {paper.get('title')}")
                    continue
                
                filename = f"{paper_id}.pdf"
                pdf_path = self.pdf_parser.download_pdf(pdf_url, filename)
                
                parsed = self.pdf_parser.parse_pdf(pdf_path)
                
                result = {
                    "paper_id": paper_id,
                    "title": parsed.title,
                    "abstract": paper.get("abstract"),
                    "year": paper.get("year"),
                    "authors": [a.get("name") for a in paper.get("authors", [])],
                    "text": parsed.text,
                    "num_figures": len(parsed.figures),
                    "num_tables": len(parsed.tables),
                    "figures": [
                        {"page": f.page, "caption": f.caption}
                        for f in parsed.figures
                    ],
                    "tables": [
                        {"page": t.page, "caption": t.caption, "rows": len(t.data)}
                        for t in parsed.tables
                    ]
                }
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {paper.get('title')}: {e}")
                continue
        
        return results
    
    def save_results(self, results: List[Dict], output_path: str = "data/ingested.json"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        return output_path
