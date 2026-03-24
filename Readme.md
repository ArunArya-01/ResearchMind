# ResearchMind

**Autonomous Multi-Agent Framework for Scientific Hypothesis Generation**

Built for **Hackverse 2026**

---

## Overview

**ResearchMind** is an autonomous agentic system designed to accelerate scientific discovery. By utilizing a multi-agent orchestration layer, it moves beyond simple summarization to identify "white space" gaps in existing research and generate structured, evidence-backed hypotheses. It independently crawls repositories, synthesizes cross-domain data, and stress-tests every theory through an adversarial critique agent.

The system combines state-of-the-art language models with intelligent information retrieval to create a comprehensive research analysis pipeline that produces actionable scientific insights.

## Key Features

* **Autonomous Literature Mapping:** Scans scholarly databases (ArXiv, PubMed) to build a contextual knowledge graph of existing research.
* **Gap Discovery Engine:** Identifies unexplored connections between disparate research fields using vector similarity and semantic analysis.
* **Evidence-Backed Synthesis:** Every hypothesis includes direct citations, logical reasoning chains, and peer-reviewed references.
* **Adversarial Critic Agent:** A dedicated agent that attempts to "debunk" the hypothesis to ensure scientific rigor, logical consistency, and practical feasibility.
* **Researcher Dashboard:** A clean, intuitive UI to visualize the reasoning trace, examine evidence chains, and manage research proposals.
* **Multi-Agent Orchestration:** Coordinated workflow between specialized agents (Researcher, Synthesizer, Critic) for comprehensive analysis.
* **Extensible Architecture:** Easy to add new agents, data sources, or analysis modules.

## How It Works

1. **Research Phase:** Autonomous agents scan multiple literature sources to gather relevant publications and data.
2. **Synthesis Phase:** Cross-domain data is synthesized to identify gaps and potential research directions.
3. **Hypothesis Generation:** Structured hypotheses are generated with full evidence chains and citations.
4. **Critique Phase:** An adversarial agent reviews each hypothesis for logical soundness and feasibility.
5. **Dashboard Presentation:** Results are visualized with reasoning traces for human researchers.

## Tech Stack

* **Orchestration:** CrewAI, LangChain
* **Backend:** FastAPI (Python)
* **LLMs:** GPT-4o / Llama 3 (via Groq)
* **Vector DB:** Pinecone / ChromaDB
* **Frontend:** Vite, React, Tailwind CSS, Framer Motion
* **Data Processing:** Python pandas, NumPy

## Project Structure

```text
├── agents/             # Agent logic (Researcher, Synthesizer, Critic)
├── core/               # RAG pipelines and vector search
├── api/                # FastAPI endpoints and routes
├── web/                # Vite + Tailwind frontend application
├── main.py             # System entry point
└── README.md           # Project documentation
```

## Installation & Setup

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd ResearchMind
pip install -r requirements.txt
```

Configure your API keys for LLM providers and literature databases in the environment configuration.

## Usage

Start the system with:

```bash
python main.py
```

Access the researcher dashboard at `http://localhost:3000` (once the frontend server is running).

## Contributing

Contributions are welcome. Please follow the existing code structure and add tests for new features.

## License

This project is created for Hackverse 2026.
