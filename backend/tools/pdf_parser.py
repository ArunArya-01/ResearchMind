import os
import json
import google.generativeai as genai
from pdf2image import convert_from_bytes

def parse_pdf(file_bytes: bytes) -> str:
    """
    Scans a PDF using pdf2image and analyzes it with Gemini 1.5 Flash
    to detect charts and tables, returning a JSON list of their coordinates.
    """
    try:
        images = convert_from_bytes(file_bytes)
    except Exception as e:
        return json.dumps({"error": f"Failed to convert PDF to images: {str(e)}"})
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "MOCK_KEY_IF_NOT_SET"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    results = []
    
    prompt = '''
    Analyze this page from a document. Detect any charts, tables, or graphs.
    Return a strictly valid JSON list of objects mapping to these components. 
    Each object should have:
    - "type": "chart", "table", or "graph"
    - "description": A brief description of the identified component
    - "coordinates": {"x": float, "y": float, "width": float, "height": float} representing the bounding box (normalized 0.0 to 1.0)
    
    IMPORTANT: Return ONLY the JSON array, no markdown formatting like ```json or anything else. Just the raw array starting with [ and ending with ].
    If no charts or tables are found, return exactly [].
    '''
    
    for page_num, image in enumerate(images):
        try:
            response = model.generate_content([prompt, image])
            text = response.text.strip()
            
            # Clean possible markdown block
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            page_results = json.loads(text.strip())
            
            # Append page number
            if isinstance(page_results, list):
                for item in page_results:
                    item["page"] = page_num + 1
                results.extend(page_results)
                
        except Exception as e:
            print(f"Error parsing Gemini response for page {page_num + 1}: {e}")
            
    return json.dumps(results)
