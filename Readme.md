# ResearchMind
> **The next great discovery is hiding in the gap between two fields that have never spoken.**

---

## Problem Statement

ResearchMind is an AI-assisted research discovery workspace for exploring interdisciplinary connections across scientific literature. It combines PDF ingestion, dataset summarization, graph-based exploration, and an adversarial multi-agent synthesis loop to turn raw papers into hypothesis-ready discovery reports.

The modern scientific community suffers from extreme "information overload." The sheer volume of published papers prevents meaningful cross-domain innovation. As researchers specialize deeply into narrow niches, critical interdisciplinary connections are lost. These undiscovered connections—the white spaces where two unrelated scientific fields have not yet been bridged—are where the next major breakthroughs lie.

## What It Does

ResearchMind is an AI-native Discovery Engine designed to actively map and bridge these scientific voids. It operates on a three-stage workflow:

1. **Ingestion (Vision)**
   Uses Multimodal AI to scan research PDFs, meticulously extracting not just the text, but the technical data embedded in charts, tables, and diagrams.
   Upload one or more research PDFs and extract structured text, references, keywords, and image metadata.

2. **Synthesis (Swarm)**
   Transforms the extracted data into an interactive 3D Knowledge Graph, identifying isolated clusters. It highlights "Discovery Gaps" as glowing red anomalies, which are then debated by our Adversarial Swarm.

3. **Artifact (Report)**
   Converts the chaotic swarm debate into a synthesized, polished scientific manuscript that serves as a ready-to-test research proposal.
   Build a live knowledge-graph view, surface gaps between concepts, and run a streamed adversarial swarm debate over the uploaded material.
   Export the resulting discovery report as Markdown or PDF for further review, iteration, or experimentation.

## Why It Exists

Modern research moves faster than any single person can reasonably track. Important connections often sit between domains rather than inside a single discipline. ResearchMind is designed to help researchers, builders, and technical teams inspect those gaps, pressure-test speculative ideas, and generate more structured starting points for new investigations.

## Core Idea: Adversarial Swarm Logic

The main synthesis loop uses an adversarial agent pattern to reduce shallow or ungrounded conclusions:

- **Agent Alpha (Visionary)** proposes bold connections, hypotheses, and bridges between disconnected concepts.
- **Agent Beta (Skeptic)** challenges those proposals, looks for weak logic, and pushes for stronger support.
- **System orchestration** streams the debate to the UI and produces a final structured report when the exchange converges.

This design aims to make the generated output more useful than a single-pass LLM response by forcing internal critique before report generation.

## Key Capabilities

- **PDF ingestion pipeline** built around `PyMuPDF` for extracting text and research structure from uploaded papers.
- **Dataset upload support** for `.csv` files, including quick descriptive summaries used during synthesis.
- **Live graph view** for browsing generated node relationships and potential discovery gaps.
- **Streaming swarm debate** over WebSockets so the frontend can display agent-by-agent reasoning in real time.
- **Export pipeline** for discovery reports in both Markdown and PDF formats.
- **ChromaDB-backed chunk storage** for retaining ingested paper content during a session.

## Product Surfaces

The frontend currently exposes these main routes:

- `/` - landing page and product overview
- `/command` - dashboard-like research command center
- `/vision` - PDF and dataset ingestion workflow
- `/synthesis` - swarm debate, graph visualization, and report generation

## Tech Stack

### Frontend

- `React 18`
- `TypeScript`
- `Vite`
- `Tailwind CSS`
- `Framer Motion`
- `Radix UI`
- `TanStack Query`

### Backend

- `FastAPI` for AI and ingestion endpoints
- `Go net/http` for proxying and concurrent graph/node services
- `WebSockets` for streaming swarm events
- `ChromaDB` for local vector/document persistence
- `pandas` for dataset summarization
- `reportlab` for PDF generation

### AI and Research Tooling

- `google-genai`
- `networkx`
- Custom swarm orchestration under `backend/agents/`
- Custom PDF parsing and report builders under `backend/tools/`

## Repository Structure

```text
ResearchMind/
├── backend/
│   ├── agents/          # Swarm orchestration
│   ├── api/             # FastAPI app and routes
│   ├── go/              # Go API proxy/server
│   └── tools/           # PDF parsing, graph logic, report builders
├── core/
│   └── ingestion/       # Additional ingestion pipeline modules
├── frontend/            # React + Vite application
├── data/                # Runtime upload/output storage
├── requirements.txt     # Python dependencies
└── Readme.md
```
```text
ResearchMind/
├── backend/
│   ├── agents/          # Swarm orchestration
│   ├── api/             # FastAPI app and routes
│   ├── go/              # Go API proxy/server
│   └── tools/           # PDF parsing, graph logic, report builders
├── core/
│   └── ingestion/       # Additional ingestion pipeline modules
├── frontend/            # React + Vite application
├── data/                # Runtime upload/output storage
├── requirements.txt     # Python dependencies
└── Readme.md
```

## How The System Flows

1. The frontend uploads PDFs to the Python backend.
2. The backend parses documents, extracts text and metadata, and stores chunks in ChromaDB.
3. Optional CSV uploads are summarized and stored client-side for the synthesis session.
4. The frontend connects to `/ws/swarm` and starts the adversarial debate.
5. The backend streams debate messages, scores, and final report content back to the UI.
6. The report can then be downloaded as Markdown or rendered as a PDF.

## Prerequisites

Before running the project, make sure you have:

- `Python 3.10+`
- `Node.js 18+`
- `npm`
- `Go 1.21+` recommended
- A valid `GOOGLE_API_KEY`

## Environment Variables

Create a root-level `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

The Python backend reads the repo-level `.env` automatically on startup.

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ArunArya-01/ResearchMind.git
cd ResearchMind
```

### 2. Set Up the Python Backend

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

*Make sure to configure your `.env` file to include your `GOOGLE_API_KEY`.*

Start the FastAPI server on port `8001`:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Start the Go Proxy Server

In a second terminal:

```bash
cd backend/go
go mod tidy
go run .
```

By default, the Go server starts on port `8000` and proxies requests to the Python backend on port `8001`.

### 4. Start the Frontend

In a third terminal:

```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173` to explore the ResearchMind Discovery Engine.

## Frontend API Resolution

The frontend tries to connect in this order:

1. `VITE_API_BASE_URL`
2. a previously stored successful API base in `localStorage`
3. `http://<current-host>:8001`
4. `http://<current-host>:8000`

If you want to pin the frontend to a specific backend, create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## Available Backend Endpoints

### HTTP

- `GET /` - backend health/status
- `GET /nodes` - fetch graph node data
- `POST /reset` - clear current processed session data
- `POST /upload/pdf` - upload and process PDFs
- `POST /upload-dataset` - upload CSV datasets
- `POST /download/discovery-report` - export Markdown report
- `POST /download/discovery-pdf` - export PDF report

### WebSocket

- `WS /ws/swarm` - start and stream the adversarial swarm debate

## Typical Usage

1. Start the Python backend, Go proxy, and frontend.
2. Open `/vision` and upload one or more PDF papers.
3. Optionally upload a CSV dataset for additional context.
4. Move to `/synthesis` and start the discovery run.
5. Watch the Visionary and Skeptic agents debate in real time.
6. Export the resulting report as Markdown or PDF.

## Current Notes

- The project README file in this repository is currently named `Readme.md`.
- The Python backend is the source of ingestion, swarm, and export logic.
- The Go service acts primarily as a lightweight API/WebSocket proxy plus graph endpoint.
- Runtime artifacts such as uploaded files and generated outputs are written into local project directories like `data/`, `chroma_db/`, and `pdf_debug/` during use.

## Future Improvements

- Stronger test coverage across ingestion and swarm orchestration
- More deterministic graph generation tied to actual semantic structure
- Better environment examples and deployment docs
- Authentication, persistence, and multi-user session support

## License

MIT LICENSE
