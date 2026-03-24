# 🔬 HypotheSync

**Autonomous Multi-Agent Framework for Scientific Hypothesis Generation**

Built for **Hackverse 2026**

---

## 📖 Overview
**HypotheSync** is an autonomous agentic system designed to accelerate scientific discovery. By utilizing a multi-agent orchestration layer, it moves beyond simple summarization to identify "white space" gaps in existing research and generate structured, evidence-backed hypotheses. It independently crawls repositories, synthesizes cross-domain data, and stress-tests every theory through an adversarial critique agent.

## 🚀 Key Features
* **Autonomous Literature Mapping:** Scans scholarly databases (ArXiv, PubMed) to build a contextual knowledge graph.
* **Gap Discovery Engine:** Identifies unexplored connections between disparate research fields using vector similarity.
* **Evidence-Backed Synthesis:** Every hypothesis includes direct citations and logical reasoning chains.
* **Adversarial Critic Agent:** A dedicated agent that attempts to "debunk" the hypothesis to ensure scientific rigor and feasibility.
* **Researcher Dashboard:** A clean UI to visualize the reasoning trace and manage research proposals.

## 🛠️ Tech Stack
* **Orchestration:** CrewAI, LangChain
* **Backend:** FastAPI (Python)
* **LLMs:** GPT-4o / Llama 3 (via Groq)
* **Vector DB:** Pinecone / ChromaDB
* **Frontend:** Vite, React, Tailwind CSS, Framer Motion

## 📂 Structure
```text
├── agents/             # Agent logic (Researcher, Synthesizer, Critic)
├── core/               # RAG pipelines and vector search
├── api/                # FastAPI endpoints
├── web/                # Vite + Tailwind frontend
└── main.py             # System entry point