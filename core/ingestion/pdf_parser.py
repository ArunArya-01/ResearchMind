import os
import fitz
import requests
from PIL import Image
from io import BytesIO
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ExtractedFigure:
    page: int
    image: Image.Image
    caption: Optional[str] = None


@dataclass
class ExtractedTable:
    page: int
    data: List[List[str]]
    caption: Optional[str] = None


@dataclass
class ParsedPaper:
    title: str
    text: str
    figures: List[ExtractedFigure]
    tables: List[ExtractedTable]
    metadata: Dict


class PDFParser:
    def __init__(self, cache_dir: str = "data/pdfs"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def download_pdf(self, url: str, filename: str) -> str:
        cache_path = os.path.join(self.cache_dir, filename)
        if os.path.exists(cache_path):
            return cache_path
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(cache_path, "wb") as f:
            f.write(response.content)
        return cache_path
    
    def parse_pdf(self, pdf_path: str) -> ParsedPaper:
        doc = fitz.open(pdf_path)
        
        title = self._extract_title(doc)
        text = self._extract_text(doc)
        figures = self._extract_figures(doc)
        tables = self._extract_tables(doc)
        metadata = doc.metadata
        
        doc.close()
        
        return ParsedPaper(
            title=title,
            text=text,
            figures=figures,
            tables=tables,
            metadata=metadata
        )
    
    def _extract_title(self, doc: fitz.Document) -> str:
        if doc.metadata.get("title"):
            return doc.metadata["title"]
        
        first_page = doc[0]
        blocks = first_page.get_text("blocks")
        if blocks:
            return blocks[0][4].strip()
        return "Untitled"
    
    def _extract_text(self, doc: fitz.Document) -> str:
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        return "\n\n".join(text_parts)
    
    def _extract_figures(self, doc: fitz.Document) -> List[ExtractedFigure]:
        figures = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                image = Image.open(BytesIO(image_bytes))
                
                text = page.get_text()
                caption = self._find_caption_nearby(text, img_index)
                
                figures.append(ExtractedFigure(
                    page=page_num + 1,
                    image=image,
                    caption=caption
                ))
        
        return figures
    
    def _find_caption_nearby(self, text: str, img_index: int) -> Optional[str]:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "fig" in line.lower() and img_index >= 0:
                return line.strip()
        return None
    
    def _extract_tables(self, doc: fitz.Document) -> List[ExtractedTable]:
        tables = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            tables_found = page.find_tables()
            
            for table in tables_found:
                table_data = []
                for row in table.extract():
                    table_data.append([cell if cell else "" for cell in row])
                
                caption = self._find_table_caption(page.get_text(), table.bbox)
                
                tables.append(ExtractedTable(
                    page=page_num + 1,
                    data=table_data,
                    caption=caption
                ))
        
        return tables
    
    def _find_table_caption(self, text: str, bbox) -> Optional[str]:
        lines = text.split("\n")
        for line in lines:
            if "table" in line.lower():
                return line.strip()
        return None
