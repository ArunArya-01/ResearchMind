# ResearchMind

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built for Hackverse 2026](https://img.shields.io/badge/Built%20for-Hackverse%202026-brightgreen.svg)](https://hackverse.com)

### Autonomous Cross-Modal GraphRAG for Hypothesis Synthesis

**Built for Hackverse 2026 | Redefining Scientific Discovery with AI**

---

## Vision

> **Most AI summarizes knowledge. ResearchMind creates it.**

ResearchMind is an **agentic AI research system** that goes beyond retrieval and summarization to generate **novel, testable scientific hypotheses**.

It identifies **"White Space" in research** — unexplored intersections between domains — by combining:

- Cross-modal understanding (text + charts + tables)
- Knowledge Graph reasoning (GraphRAG)
- Multi-agent debate (Visionary vs Skeptic)

---

## Key Features

### Cross-Modal "Vision" Ingestion
- Uses **Gemini 1.5 Flash**
- Understands:
  - Graphs
  - Tables
  - Scientific diagrams

---

### Multi-Hop GraphRAG Engine
- Built with **NetworkX**
- Constructs dynamic Knowledge Graphs
- Detects **"Islands of Knowledge"**
- Triggers **Discovery Events**

---

### Adversarial Debate Protocol
- **Visionary Agent** → proposes hypothesis
- **Skeptic Agent** → challenges it
- **Arbiter** → refines and scores

---

### Deterministic Math Verification
- Python sandbox execution
- Validates:
  - Simulations
  - Mathematical consistency
  - Physical laws

---

### Auto-Citing Evidence Trace
- Each claim includes:
  - Confidence Score
  - DOI / ArXiv references

---

## Tech Stack

| Layer | Technology |
|------|-----------|
| Orchestration | CrewAI / LangGraph |
| Multimodal AI | Gemini 1.5 Flash |
| Fast Inference | Groq (Llama 3.2) |
| Graph Engine | NetworkX / PyVis |
| Vector DB | ChromaDB |
| Backend | FastAPI |
| Frontend | Next.js + Framer Motion |

---

## System Pipeline

### 1. Ingestion Stage
- Fetch papers via **Semantic Scholar API**
- Extract:
  - Text
  - Figures
  - Tables

---

### 2. Mapping Stage
- Extract entities:
  - Materials
  - Phenomena
  - Methods
- Build Knowledge Graph

---

### 3. Discovery Stage
- Identify missing connections using graph traversal

> Example:
> Material improves heat transfer + Device needs cooling
> → New research hypothesis

---

### 4. Synthesis Stage
- Visionary proposes
- Skeptic critiques
- Arbiter finalizes

---

### 5. Output
Generates:
- Research Proposal
- Hypothesis
- Methodology
- Simulation Results
- Citations

---

## Project Structure

```
├── agents/
│   ├── visionary.py
│   ├── skeptic.py
│   └── validator.py
│
├── core/
│   ├── graph_rag.py
│   ├── vision_parse.py
│   └── tools.py
│
├── api/
├── web/
└── main.py
```

---

## Setup & Installation

### 1. Clone Repo
```bash
git clone https://github.com/your-username/ResearchMind.git
cd ResearchMind
```

---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Environment Setup
Create `.env` file:

```env
GOOGLE_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

---

### 4. Run Project
```bash
python main.py --topic "Post-Quantum Cryptography"
```

---

## Use Cases

- Scientific discovery
- Drug research
- Material science
- Climate modeling
- AI-assisted research writing

---

## Why It Matters

ResearchMind transforms:

**Data → Knowledge → Insight → Hypothesis**

Instead of summarizing existing research, it **creates new directions for science**.

---

## Hackathon Highlights

- Fully autonomous research pipeline
- Zero-cost architecture
- Novel combination:
  - GraphRAG
  - Multimodal AI
  - Agent debate

---

## Future Scope

- Lab simulation integrations
- Reinforcement learning agents
- Collaborative research UI
- Patent generation

---

## Contributing

Pull requests are welcome.
Open an issue for major changes.

---

## License

MIT License

---

## Tagline

> **"Don't just search knowledge. Create it."**
