# ResearchMind
> **Tagline:** *Bridging Scientific Gaps with Adversarial Swarm Intelligence.*

---

## 📌 Problem Statement

The modern scientific community suffers from extreme "information overload." The sheer volume of published papers prevents meaningful cross-domain innovation. As researchers specialize deeply into narrow niches, critical interdisciplinary connections are lost. These undiscovered connections—the white spaces where two unrelated scientific fields have not yet been bridged—are where the next major breakthroughs lie. 

## 🚀 The Solution

ResearchMind is an AI-native Discovery Engine designed to actively map and bridge these scientific voids. It operates on a robust three-stage architecture:

1. **Ingestion (Vision)**
   Uses Multimodal AI to scan research PDFs, meticulously extracting not just the text, but the technical data embedded in charts, tables, and diagrams.
2. **Synthesis (Swarm)**
   Transforms the extracted data into an interactive 3D Knowledge Graph, identifying isolated clusters. It highlights "Discovery Gaps" as glowing red anomalies, which are then debated by our Adversarial Swarm. 
3. **Artifact (Manuscript)**
   Converts the chaotic swarm debate into a synthesized, polished scientific manuscript that serves as a ready-to-test research proposal.

---

## 🧠 Core USP: Adversarial Swarm Logic

The heart of ResearchMind is our **Adversarial Swarm (Agentic AI)**—a highly specialized structural debate system designed to eliminate LLM hallucinations and generate robust scientific hypotheses.

- **Agent Alpha (The Visionary):** Looks at the "Red Anomalies" in the Knowledge Graph and proposes wild, novel hypotheses to bridge the gaps.
- **Agent Beta (The Skeptic):** Rigorously "red-teams" the visionary's proposals. It challenges logic, checks against known constraints, and demands structural proof to eliminate false positives.

Together, they debate iteratively until a cohesive, battle-tested scientific pathway emerges.

---

## ⚡ Key Features

| Feature | Description |
| :--- | :--- |
| **Multimodal Ingestion** | Powered by Gemini 1.5 Flash to comprehensively analyze complex visual and textual data. |
| **3D Knowledge Graph** | An interactive, real-time 3D constellation of 200+ research nodes mapping out relationships. |
| **Discovery Gaps** | Visually highlights structural disconnected areas in research as pulsing red anomalies. |
| **Synthesis Report** | Automatically generates beautifully formatted final research proposals from the Swarm's debate. |

---

## 🛠️ The Tech Stack

### Frontend & UI
- **React (Vite) & TypeScript:** High-performance, scalable web interface.
- **Tailwind CSS & Framer Motion:** Fluid animations, 3D perspectives, and sleek glassmorphism effects.
- **Design Identity:** Industrial High-Performance Tech featuring a palette of *Obsidian Black, Bone White, and Crimson Red*.

### Backend & AI
- **Python (FastAPI):** High-speed, robust backend routing.
- **WebSockets:** Enabling real-time, low-latency agent streaming for the swarm debate.
- **Google Gemini 1.5 Flash:** Core reasoning and multimodal vision engine.
- **NetworkX:** Graph logic and structural relationship mapping.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/HackVerse.git
cd HackVerse
```

### 2. Backend Setup
Set up the Python environment and install the required dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
*Make sure to configure your `.env` file based on `.env.example` to include your `GEMINI_API_KEY`.*

Start the FastAPI server:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
Open a new terminal session, install the Node modules, and start the Vite frontend:
```bash
# Return to the project root
npm install
npm run dev
```

Navigate to `http://localhost:5173` to explore the ResearchMind Discovery Engine.
