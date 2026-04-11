import io
import re
import fitz  # PyMuPDF
from typing import Dict, Any

def parse_pdf(file_bytes: bytes) -> Dict[str, Any]:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {"text": f"Error opening PDF: {str(e)}", "keywords": [], "images": [], "elements": {"pages": 0, "references": 0}}

    pages = doc.page_count
    clean_text = ""
    
    import hashlib
    file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
    import os
    os.makedirs("data/crops", exist_ok=True)
    
    extracted_images = []
    
    for page_num in range(pages):
        page = doc.load_page(page_num)
        page_text = page.get_text()
        clean_text += page_text + "\n"
        
        p_words = re.findall(r'\b[A-Za-z]{4,}\b', page_text)
        p_exclude = {'this', 'that', 'with', 'from', 'have', 'were', 'which', 'their', 'there', 'they', 'also', 'been', 'than', 'into', 'based', 'used', 'using', 'these', 'those', 'would', 'could', 'should', 'only', 'such', 'some', 'many', 'more', 'most', 'other', 'another', 'very', 'much', 'about', 'over', 'under', 'between', 'through', 'after', 'before', 'during', 'while', 'since', 'until', 'because', 'although', 'even', 'though', 'however', 'therefore', 'thus', 'hence', 'then', 'else', 'instead'}
        p_word_freq = {}
        for w in p_words:
            wl = w.lower()
            if wl not in p_exclude:
                score = 2 if w[0].isupper() else 1
                p_word_freq[w] = p_word_freq.get(w, 0) + score
        
        p_sorted = sorted(p_word_freq.items(), key=lambda x: x[1], reverse=True)
        page_keyword = p_sorted[0][0] if p_sorted else "Data"
        
        images_found_on_page = False
        images = page.get_images(full=True)
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image.get("image")
                img_ext = base_image.get("ext", "png")
                
                if image_bytes and len(image_bytes) > 2000:
                    filename = f"crop_page{page_num}_img{img_idx}.{img_ext}"
                    filepath = f"data/crops/{filename}"
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                        
                    extracted_images.append({
                        "keyword": page_keyword,
                        "citation_img": f"/crops/{filename}"
                    })
                    images_found_on_page = True
            except Exception:
                pass
                
        # Handle Tables/Vectors (Fallback) if natively requested
        if not images_found_on_page:
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t_idx, tab in enumerate(tabs.tables):
                        rect = tab.bbox
                        if rect:
                            pix = page.get_pixmap(clip=rect)
                            filename = f"crop_page{page_num}_tab{t_idx}.png"
                            filepath = f"data/crops/{filename}"
                            pix.save(filepath)
                            
                            extracted_images.append({
                                "keyword": page_keyword,
                                "citation_img": f"/crops/{filename}"
                            })
                            images_found_on_page = True
            except AttributeError:
                pass # Older PyMuPDF missing find_tables
        
    doc.close()

    # Keyword extraction
    words = re.findall(r'\b[A-Za-z]{4,}\b', clean_text)
    exclude = {'this', 'that', 'with', 'from', 'have', 'were', 'which', 'their', 'there', 'they', 'also', 'been', 'than', 'into', 'based', 'used', 'using', 'these', 'those', 'would', 'could', 'should', 'only', 'such', 'some', 'many', 'more', 'most', 'other', 'another', 'very', 'much', 'about', 'over', 'under', 'between', 'through', 'after', 'before', 'during', 'while', 'since', 'until', 'because', 'although', 'even', 'though', 'however', 'therefore', 'thus', 'hence', 'then', 'else', 'instead'}
    word_freq = {}
    for w in words:
        wl = w.lower()
        if wl not in exclude:
            score = 3 if w[0].isupper() else 1
            word_freq[w] = word_freq.get(w, 0) + score
            
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    # Give priority to capitalized words as keywords when possible
    keywords = list(dict.fromkeys(w[0] for w in sorted_words))[:10]
    
    if not keywords:
        keywords = []

    references = clean_text.lower().count("references") + clean_text.lower().count("bibliography")

    return {
        "text": clean_text.strip(),
        "keywords": keywords,
        "images": extracted_images,
        "elements": {
            "pages": pages,
            "references": references
        }
    }
