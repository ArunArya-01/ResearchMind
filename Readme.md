# ResearchMind

An AI research system that generates **novel, testable scientific hypotheses** by finding unexplored connections between research domains.

## What It Does

ResearchMind identifies "white space" in research — gaps between fields where no one has explored yet. It reads scientific papers (text, charts, tables), builds a knowledge graph, and uses AI agents to debate and synthesize new hypotheses.

## How It Works

1. **Ingest** - Fetch papers and extract text, figures, tables
2. **Map** - Build a knowledge graph of concepts
3. **Discover** - Find missing connections between domains
4. **Synthesize** - AI agents propose and debate hypotheses
5. **Verify** - Validate with mathematical simulations

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python main.py --topic "Your Research Topic"
```

## Tech Stack

- **AI**: Gemini (vision), Groq/Llama (reasoning)
- **Graph**: NetworkX, ChromaDB
- **Backend**: FastAPI
- **Frontend**: Next.js
