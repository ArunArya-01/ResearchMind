# Research Command Center (ResearchMind)

## Features

### Frontend (React + Vite + Tailwind CSS)
- **Luxury Digital Lab Interface:** A highly stylized, futuristic dashboard featuring "Liquid Glass" panels, organic mesh gradients, and immersive micro-animations.
- **Multimodal Data Analysis:** Interactive visualization components for analyzing detailed domains like "Synthetic Biometrics", "Quantum Entanglement", and deep-tissue structural reports.
- **Cross-Domain Synthesis Search:** Command palette (`CMD + K`) interface for executing rapid data lookups.
- **Real-time Processing Analytics:** UI mockups of streaming processing loads, latency deltas, and AI vision confidence loops in a terminal-like environment.

### Backend (Python AI Ingestion Pipeline)
- **Hypothesis Generator & Paper Fetching:** Automates fetching of research papers using the Semantic Scholar Graph API based on specific topics.
- **PDF Extraction:** Automatically downloads and parses open-access PDFs, extracting the title, abstract, citation data, full text, figures, and tables into structured JSON.
- **Modular Architecture:** Cleanly separated handlers orchestrating data ingestion, including `SemanticScholarClient` and `PDFParser` managed by an `IngestionPipeline`.

---

## Project Architecture

```
HackVerse/
├── core/                        # Python Backend: Data Ingestion Logic
│   └── ingestion/               # Pipeline for paper fetching & parsing
│       ├── pipeline.py          # Orchestrates fetching -> downloading -> parsing -> saving
│       ├── pdf_parser.py        # Logic to extract text/images from downloaded PDFs
│       └── semantic_scholar.py  # Wrapper for Semantic Scholar API
├── data/                        # Output directory for parsed research (e.g. ingested.json)
├── src/                         # Frontend: React Application
│   ├── components/              # Reusable UI components (e.g. Layout)
│   ├── pages/                   # Application Routes (Home, Analysis, Report)
│   ├── App.tsx                  # React Router configuration
│   ├── index.css                # Global styles, Tailwind directives, custom glassmorphism
│   └── main.tsx                 # React entry point
├── main.py                      # Python CLI entry point for the Ingestion Pipeline
├── package.json                 # Frontend dependencies and scripts (React 19, Vite)
├── requirements.txt             # Backend dependencies (pymupdf, python-dotenv, requests, pillow)
└── tailwind.config.js           # Tailwind configuration & design system tokens
```

---

## Getting Started

### 1. Frontend Setup (React App)

Make sure you have [Node.js](https://nodejs.org/) installed.

```bash
# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The app will be available at `http://localhost:5173`. 

### 2. Backend Setup (Python Ingestion Pipeline)

Ensure you have Python 3.8+ installed. It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt

# Set up your environment variables
cp .env.example .env
# Fill in your SEMANTIC_SCHOLAR_API_KEY in the .env file if available
```

### 3. Running the Data Ingestion Pipeline

To run the AI research fetching script:

```bash
python main.py --topic "quantum computing" --limit 5
```

**CLI Arguments:**
- `--topic`: (Required) The research topic to explore.
- `--limit`: (Optional) Number of papers to fetch (Default is 5).
- `--output`: (Optional) Output JSON file path (Default is `data/ingested.json`).

The pipeline will query Semantic Scholar, download open-access PDFs, parse text and metadata, and save the complete structured output.

---

## Design System & Aesthetic
The web application heavily emphasizes a futuristic sci-fi lab aesthetic. It uses custom CSS variables within `tailwind.config.js` and `index.css` to manage a specific palette of "surface", "on-surface", and translucent colors giving it a signature "glass-panel" look.

Custom fonts (`font-display` and `font-mono`) and detailed SVG visualizers provide a deeply immersive UX out of the box.

---

## Next Steps
This project currently serves as a front-end UI visualization space combined with an offline ingestion backend. Future goals involve connecting the React frontend directly to the Python output for live AI-driven analysis of the ingested papers.

## License 
MIT
