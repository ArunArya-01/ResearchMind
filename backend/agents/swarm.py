import asyncio
import os
from pathlib import Path
from typing import Callable, Any, Awaitable

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

_new_sdk_import_error = None
_legacy_sdk_import_error = None

try:
    import google.genai as google_genai
except ModuleNotFoundError as exc:
    google_genai = None
    _new_sdk_import_error = exc

try:
    import google.generativeai as legacy_genai
except ModuleNotFoundError as exc:
    legacy_genai = None
    _legacy_sdk_import_error = exc


class SwarmOrchestrator:
    def _select_best_model(self) -> str:
        # Primary target requested by product direction.
        return 'gemini-2.5-flash-lite'

    def __init__(self, log_callback: Callable[[str], Awaitable[Any]]):
        self.log_callback = log_callback
        if google_genai is None and legacy_genai is None:
            raise RuntimeError(
                "Google GenAI SDK not installed. Install `google-genai` (preferred) or `google-generativeai`."
            ) from (_new_sdk_import_error or _legacy_sdk_import_error)
        
        self._load_project_env()
        
        # Use GOOGLE_API_KEY consistently for all Gemini auth paths.
        api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
        api_key = api_key.strip("'").strip('"')
        
        print(f"GOOGLE_API_KEY loaded: {bool(api_key)}")
        
        if not api_key or api_key.startswith("<"):
            raise ValueError("Valid GOOGLE_API_KEY not found or is empty. Please set a real API key in your .env or environment variables.")

        # Force API-key auth mode and avoid accidental Vertex/ADC resolution.
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        os.environ.pop("GOOGLE_CLOUD_LOCATION", None)
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ["GOOGLE_API_KEY"] = api_key
        os.environ["GEMINI_API_KEY"] = api_key

        self._api_key = api_key
        self._genai_client = None
        self._use_legacy_sdk = False

        if google_genai is not None:
            self._genai_client = google_genai.Client(api_key=self._api_key)
        elif legacy_genai is not None:
            legacy_genai.configure(api_key=self._api_key)
            self._use_legacy_sdk = True

        self.model_name = self._select_best_model()
        self.active_overrides = []

    def _load_project_env(self) -> None:
        # Search current working directory and script directories
        env_paths = [Path.cwd() / ".env", Path(__file__).resolve().parent / ".env"]
        for parent in Path(__file__).resolve().parents:
            if parent / ".env" not in env_paths:
                env_paths.append(parent / ".env")

        # Specifically add repo root
        repo_root = Path(__file__).resolve().parent.parent.parent
        if repo_root / ".env" not in env_paths:
            env_paths.insert(0, repo_root / ".env")

        for env_path in env_paths:
            if env_path.exists():
                if load_dotenv:
                    # override=True ensures .env wins if the user's terminal has an empty export
                    load_dotenv(dotenv_path=env_path, override=True)
                self._load_env_fallback(env_path)
                break

    def _load_env_fallback(self, env_path: Path) -> None:
        try:
            with env_path.open("r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Apply to os.environ if missing or currently an empty string
                    if key and (key not in os.environ or not os.environ[key].strip()):
                        os.environ[key] = value
        except Exception:
            pass

    async def _generate_text(self, model_name: str, prompt: str) -> str:
        if self._genai_client:
            response = await asyncio.to_thread(
                self._genai_client.models.generate_content,
                model=model_name,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text

        if not self._use_legacy_sdk or legacy_genai is None:
            raise RuntimeError("Gemini client initialization failed before generation.")

        model = legacy_genai.GenerativeModel(model_name)
        response = await asyncio.to_thread(model.generate_content, prompt)
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text

    def inject_override(self, command: str):
        self.active_overrides.append(command)

    async def log(self, agent_name: str, message: str):
        import json
        payload = {"agent": agent_name, "message": message}
        await self.log_callback(json.dumps(payload))

    async def log_status(self, message: str):
        import json
        payload = {"type": "status", "content": message}
        await self.log_callback(json.dumps(payload))

    async def _safe_generate(self, prompt: str):
        model_candidates = [
            self.model_name,
            "gemini-1.5-pro",
            "gemini-pro",
        ]

        # Max 3 outer retries for 429/503
        for attempt in range(3):
            try:
                last_error = None
                for model_name in model_candidates:
                    try:
                        text = await self._generate_text(model_name, prompt)
                        # Persist the working alias
                        self.model_name = model_name
                        return text
                    except Exception as e:
                        last_error = e
                        msg = str(e).lower()
                        # Allow falling back to other models on these errors:
                        if "not found" in msg or "not supported" in msg or "503" in msg or "unavailable" in msg or "overloaded" in msg or "resource_exhausted" in msg:
                            continue
                        raise e
                raise last_error if last_error else RuntimeError("No valid Gemini model available.")
            except Exception as e:
                msg = str(e).lower()
                if ('429' in msg or 'resource_exhausted' in msg or '503' in msg or 'unavailable' in msg) and attempt < 2:
                    severity = "Rate Limit" if '429' in msg else "Overloaded"
                    await self.log_status(f"API {severity} (Attempt {attempt+1}/3)... Retrying in 10s.")
                    await asyncio.sleep(10)
                    continue
                print(f"DEBUG: API Error: {e}")
                raise e

    async def check_data_alignment(self, pdf_content: str, csv_summary: str) -> str:
        gate_prompt = f"""CRITICAL DIRECTIVE: You are a ruthless peer reviewer.
If the uploaded Dataset (CSV) and Theory (PDF), OR the two Theories (PDFs) belong to fundamentally different domains (e.g., Diamond Prices vs. Blockchain, or Breast Cancer vs. Quantum Computing) and share NO direct, scientifically proven causal variables, you MUST output EXACTLY:
[FUSION_TERMINATED]: Domains are fundamentally incompatible.
Do not attempt to find a creative metaphor. Terminate immediately.

You are a strict Data Science Gatekeeper.
Evaluate this theoretical paper and this dataset:
Theory: {pdf_content[:2000]}
Dataset Columns & Summary: {csv_summary[:2000]}

Can this specific dataset legitimately benchmark, test, or prove this specific theory? Is there a strong, logical causal link?
If there is ANY doubt about a direct, scientifically proven causal link, treat them as incompatible and terminate.

Reply ONLY with "[FUSION_APPROVED]" if the dataset is scientifically relevant, or "[FUSION_TERMINATED]: Domains are fundamentally incompatible." if they are unrelated.
"""
        response = await self._safe_generate(gate_prompt)
        return response.strip()

    async def run_swarm(self, discovery_gap_data: dict, topic: str, dataset_summary: str = None):
        print("DEBUG: Alpha Agent starting...")
        print(f"DEBUG: Using model: {self.model_name}")
        await self.log("System", "Initializing Adversarial Swarm...")
        
        context = str(discovery_gap_data)
        has_pdf = bool(discovery_gap_data.get("context"))
        has_csv = bool(dataset_summary)
        if has_pdf and not has_csv:
            scenario = "Theorist (PDF-only)"
        elif not has_pdf and has_csv:
            # CSV-only: bypass Gatekeeper entirely — no PDF to compare against
            scenario = "Data Scientist (CSV-only)"
            await self.log("System", "[FUSION_APPROVED] - Proceeding with standalone Data Profiling.")
        elif has_pdf and has_csv:
            scenario = "Breakthrough (Hybrid)"
            
            # --- START DATA-THEORY GATEKEEPER ---
            await self.log("System", "Running Data-Theory Gate pre-check...")
            pdf_content = discovery_gap_data.get("context", "")
            gate_text = await self.check_data_alignment(pdf_content, dataset_summary)
            if "[FUSION_TERMINATED]" in gate_text:
                raise Exception("[FUSION_TERMINATED]")
            # --- END DATA-THEORY GATEKEEPER ---
            
        else:
            scenario = "System Ready (None)"
            
        hypothesis = ""
        critique = ""
        full_transcript = []

        await self.log(
            "System",
            f"Input mode: {scenario}. Debate will stream as claim, evidence, reasoning summary, and critique.",
        )
        
        for iteration in range(1, 3):
            await self.log("System", f"Starting Iteration {iteration}/2")
            
            # Agent Alpha (Visionary)
            await self.log("Visionary", "Analyzing Discovery Gap and generating hypothesis...")
            
            override_text_alpha = ""
            if self.active_overrides:
                override_text_alpha = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
                self.active_overrides = []

            # --- THE 96% ACCURACY ALPHA PROMPT UPDATE ---
            grounding_directive = ""

            if scenario == "Theorist (PDF-only)":
                grounding_directive = """
                CRITICAL GROUNDING RULE:
                1. Identify a REAL, specific limitation explicitly mentioned in the text.
                2. Propose a strictly scientific breakthrough to solve that exact limitation.
                3. DO NOT invent science fiction concepts.
                """
            elif scenario == "Data Scientist (CSV-only)":
                grounding_directive = """
                CRITICAL GROUNDING RULE: You are performing pure Exploratory Data Analysis (EDA).
                1. Because no theoretical PDF was provided, DO NOT invent medical, biological, or physical theories.
                2. DO NOT treat basic data cleaning steps (like removing an 'id' column) as scientific hypotheses.
                3. Focus ONLY on identifying statistically significant patterns: Which features are likely highly correlated? Which features have extreme outliers? Propose a hypothesis based STRICTLY on the statistical distributions of the provided data.
                """

            alpha_prompt = f"""
            You are Agent Alpha, the Visionary.
            Scenario: {scenario}
            Topic: {topic}
            Discovery Gap Data (PDF): {context}
            Empirical Dataset Summary (CSV): {dataset_summary if dataset_summary else 'None'}
            Previous Critique: {critique}
            {grounding_directive}
            {override_text_alpha}

            Formulate a bold, innovative hypothesis.
            If there was a previous critique, address those flaws in your new hypothesis.

            Return a clean public debate turn with these labels:
            CLAIM:
            EVIDENCE USED:
            REASONING SUMMARY:
            RESEARCH HYPOTHESIS:
            OPEN GAP:

            Keep it concise but impactful. Do not reveal hidden chain-of-thought; the
            REASONING SUMMARY must be a short evidence-backed explanation.
            """
            
            # Run blocking API call in executor (or just await if using async client, but generic genai SDK is sync by default)
            alpha_response = await self._safe_generate(alpha_prompt)
            hypothesis = alpha_response.strip()
            full_transcript.append(f"Visionary: {hypothesis}")
            
            await self.log("Visionary", f"Proposed Hypothesis:\n{hypothesis}\n")
            
            # Vector Query Implementation
            try:
                import chromadb
                chroma_client = chromadb.PersistentClient(path="./chroma_db")
                collection = chroma_client.get_collection(name="research_papers")
                
                qr = collection.query(
                    query_texts=[hypothesis],
                    n_results=5
                )
                retrieved_chunks = qr.get("documents", [[]])[0]
                retrieved_metadatas = qr.get("metadatas", [[]])[0]
                
                vector_context = ""
                for doc_chunk, meta in zip(retrieved_chunks, retrieved_metadatas):
                    vector_context += f"[Source Document: {meta.get('source_doc', 'Unknown')}]\n{doc_chunk}\n\n"
                    
            except Exception as e:
                print(f"DEBUG: Vector query failed - {e}")
                vector_context = "No cross-reference data found."

            # Agent Beta (Skeptic)
            await self.log("Skeptic", f"Evaluating hypothesis and performing Red-Team cross-reference critique...")
            
            override_text_beta = ""
            if self.active_overrides:
                override_text_beta = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
                self.active_overrides = []
            
            beta_prompt = f"""
            You are Agent Beta, the Skeptic.
            Hypothesis:
            {hypothesis}

            Empirical Dataset Summary (CSV):
            {dataset_summary if dataset_summary else 'None'}
            
            Retrieved Cross-Reference Data from Vector Database:
            {vector_context}
            {override_text_beta}
            
            Perform a stark 'Red-Team' critique. PRIORITIZE FINDING SAFETY GAPS.
            Identify exactly 3 specific safety flaws, weaknesses, or unsupported claims.
            Explicitly query and cross-reference the vector database chunks provided. Compare claims from Document A against Document B to find contradictions.

            Return a clean public debate turn with these labels:
            CHALLENGE:
            EVIDENCE CHECK:
            REASONING SUMMARY:
            THREE FLAWS:
            RESEARCH GAP:

            Be direct and analytical. Do not reveal hidden chain-of-thought; the
            REASONING SUMMARY must be a concise explanation grounded in the provided
            PDF text, vector context, and/or CSV summary.
            """
            beta_response = await self._safe_generate(beta_prompt)
            critique = beta_response.strip()
            full_transcript.append(f"Skeptic: {critique}")
            
            await self.log("Skeptic", f"Critique Findings (3 Flaws):\n{critique}\n")

        # --- ACADEMIC SEARCH PATCH ---
        await self.log("System", "Verifying novelty via DuckDuckGo Live Search...")
        novelty_context = ""
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            # Use topic (clean string) + academic modifiers instead of the raw hypothesis blob.
            # Raw hypothesis is multi-line structured text that confuses DDG and returns noisy results.
            search_query = f"{topic} computer science research paper"

            results = DDGS(timeout=10).text(search_query, max_results=3)
            novelty_context = "\n".join([r.get('body', '') for r in results])
            await self.log("System", f"Found live context for novelty verification.")
        except ImportError as e:
            print(f"DEBUG: DuckDuckGo Search import failed - {e}. Install with: pip install ddgs")
            novelty_context = "Could not reach DuckDuckGo for live verification."
            await self.log("System", "DuckDuckGo search module not installed. Install with: pip install ddgs")
        except Exception as e:
            print(f"DEBUG: DuckDuckGo Search failed - {e}")
            novelty_context = "Could not reach DuckDuckGo for live verification."
            await self.log("System", f"DuckDuckGo Live Search failed: {str(e)}")

        # Final Synthesis
        await self.log("System", "Generating Final Synthesis Reports...")
        
        override_text_final = ""
        if self.active_overrides:
            override_text_final = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
            self.active_overrides = []
            
        synthesis_prompt = f"""
        You are the Master Synthesizer. Topic: {topic}. Hypothesis: {hypothesis}. Critique: {critique}. {override_text_final}

        CRITICAL REASONING RULE: Read the Skeptic Agent's summary carefully.
        IF the Skeptic Agent successfully proved that the Visionary's hypothesis is scientifically invalid, hallucinatory, or unsupported by the provided texts:
        1. DO NOT write a research paper supporting the hypothesis.
        2. Change the title of the report to "Discovery Terminated: Null Hypothesis."
        3. Under "Core Hypothesis," explicitly state that the proposed synthesis was rejected due to lack of empirical grounding.
        4. Focus the rest of the report entirely on the research gaps and WHY the current data/literature cannot support the Visionary's claims.
        Only proceed to write a supporting IEEE paper if the Skeptic's critique was substantially addressed or partially refuted by the Visionary.

        CRITICAL DATA FIDELITY RULE: Read the Skeptic's critique carefully.
        If the Skeptic identifies that the Visionary's hypothesis relies on data modalities, file types, or external data sources (e.g., genomic data, live APIs, imaging data) that are NOT explicitly present in the provided CSV or PDF:
        1. YOU MUST REJECT the Visionary's hypothesis.
        2. Change the report title to "Discovery Terminated: Data-Deficient Hypothesis."
        3. In the Core Hypothesis section, explicitly state: "The proposed hypothesis cannot be evaluated because it relies on [Missing Data Type] which is absent from the provided empirical datasets."
        4. Do NOT generate an Architectural Flow or Novelty Verification section for a data-deficient hypothesis. Instead, list what data would be required to make the hypothesis testable.

        
        CRITICAL REQUIREMENT 0 (THE FEASIBILITY GATE):
        Before writing anything, evaluate if fusing these research documents makes logical, scientific sense. 
        If the domains are fundamentally incompatible and a fusion lacks scientific merit, YOU MUST ABORT. 
        If aborting, DO NOT write the IEEE paper. Instead, output ONLY this:
        1. A large header: `# 🚨 SYNTHESIS ABORTED: INCOMPATIBLE DOMAINS`
        2. Two short paragraphs explaining exactly why the AI agents determined these fields cannot be responsibly fused.
        3. The mandatory JSON block at the bottom with "G_severity" set to 10.0.
        
        If (and ONLY if) the domains are compatible AND the hypothesis survived Skeptic scrutiny, proceed to CRITICAL REQUIREMENT 1.
        
        CRITICAL REQUIREMENT 1: Format strictly mimicking an IEEE academic paper in Markdown. You MUST generate massive volume to reach a 6-page length. Write 2 to 3 dense paragraphs per section. DO NOT summarize. Expand deeply on theoretical mechanics.
        
        Use EXACTLY these headers in this order. Do NOT include a Results section:
        # [Generate a Formal Academic Paper Title]
        **Abstract** — [Dense 250-word academic summary]
        ## I. Introduction
        [Massive multi-paragraph breakdown of global context and limitations of current methods]
        ## II. Problem Statement
        [Exhaustive analysis of the exact problem]
        ## III. Objectives
        [Detailed list of specific goals and success metrics]
        ## IV. Literature Review
        [Deep dive into previous research methodologies and why they fail]
        ## V. Methodology
        [Exhaustive, highly technical breakdown of the proposed architecture and theoretical mechanics]
        ## VI. Implementation
        [Deep technical explanation of how this is deployed in a physical edge environment, step-by-step]
        ## VII. Conclusion
        [Final extensive verdict on viability and future laboratory steps]
        ## References
        [Generate 6-8 highly plausible, formal academic references in IEEE format]

        CRITICAL REQUIREMENT 2: At the absolute very end, output a strict JSON block wrapped in ```json ... ``` containing EXACTLY three variables based on your findings:
        - "G_severity": an integer/float from 1-10 assessing the safety gap severity (Use 10.0 if you aborted the synthesis).
        - "V_certainty": a float from 0.1 to 1.0 reflecting your confidence level.
        - "D_age": the estimated age of the primary methodology/context in years (integer).
        """
        
        discovery_prompt = f"""
        CRITICAL DIRECTIVE: THE "KILL SWITCH" PROTOCOL
        You are the Master Synthesizer. Your absolute highest priority is SCIENTIFIC INTEGRITY, not document completion. You are strictly forbidden from writing a research paper if the foundational data is flawed.

        Step 1: Read the Skeptic Agent's summary immediately.
        Step 2: Check for FATAL FLAWS. A fatal flaw exists if the Skeptic points out:
          - DOMAIN MISMATCH: The uploaded files (e.g., two PDFs) are from fundamentally unrelated scientific fields (e.g., Oncology and Silicon Photonics) with no scientifically proven crossover.
          - PHANTOM DATA: The Visionary's hypothesis relies on data (e.g., genomic profiles, DW-MRI) that does not actually exist in the provided CSV or PDFs.

        IF A FATAL FLAW IS DETECTED:
        You MUST abandon the standard report template. You are FORBIDDEN from generating a Mermaid diagram, Architectural Flow, or Novelty Verification. You must output EXACTLY and ONLY the following format:

        # [FUSION TERMINATED]: Incompatible Contexts Detected

        ## Error Diagnostics
        [1-paragraph summary of why the two files cannot be merged, or what data is missing, based entirely on the Skeptic's critique.]

        ## Skeptic Intercept
        [Copy/paste the exact objection from the Skeptic Agent here.]

        [END OF GENERATION]

        Only if NO fatal flaw is detected, proceed with the standard Discovery Report below.
        ---

        You are the Master Synthesizer. Scenario: {scenario}.
        Topic: {topic}.

        Hypothesis:
        {hypothesis}

        Debate Transcript:
        {"\\n\\n".join(full_transcript)}

        Empirical Math context (if any):
        {dataset_summary if dataset_summary else 'None'}

        Novelty Verification Context (DDG):
        {novelty_context}

        {override_text_final}

        Generate a comprehensive Discovery Report in Markdown.
        It MUST contain the following sections exactly in this order:

        # Discovery Report

        ## Problem Statement
        [Generate a clear, concise problem statement derived directly from the given datasets and research context. Focus on the core issue that the hypothesis addresses. This should be 2-3 dense paragraphs explaining the fundamental problem.]

        ## Core Hypothesis
        [Explain the hypothesis clearly and concisely in 2-3 paragraphs. Make it bold and specific.]

        ## Research Hypotheses
        [List 3-5 specific, testable research hypotheses derived from the datasets and PDF content. Format each as:
        - **Hypothesis 1:** [Clear statement with measurable prediction] — Motivated by: [PDF passage, dataset field, or observed summary]
        - **Hypothesis 2:** [Clear statement with measurable prediction] — Motivated by: [source]
        - **Hypothesis 3:** [Clear statement with measurable prediction] — Motivated by: [source]
        ]

        ## Empirical Grounding & Data Tables
        [Analyze and present the CSV math/dataset summary. Output a markdown table summarizing key statistics from the data. If no CSV text is provided, state that empirical data was not supplied.]

        ## Swarm Debate Summary
        [Logically summarize the core arguments between the Visionary and Skeptic based on the transcript. Structure it as a debate format:

        **Visionary Agent:** [Present the visionary's main argument and hypothesis proposal]

        **Skeptic Agent:** [Present the skeptic's key challenges and identified flaws]

        **Resolution:** [Explain how the debate refined the hypothesis and addressed the identified weaknesses]
        ]

        ## Novelty Verification
        [Evaluate the hypothesis against the DuckDuckGo live search context to assess true novelty in the field. Explain what makes this approach unique.]

        ## Architectural Flow
        [Describe the system architecture or hypothesis flow in clear prose. Optionally include a Mermaid.js diagram inside a ```mermaid ... ``` block using graph TD; syntax, but ensure the text description is complete on its own.]

        ## Research Gaps
        [List the most important unsolved gaps discovered by the agents. Organize as:

        **PDF-Derived Gaps:** [List gaps identified from the research document]

        **Dataset-Derived Gaps:** [List gaps identified from the data analysis]

        **Validation Gaps:** [List gaps that require future experimental validation]
        ]

        Throughout the report, expose only clean public reasoning summaries. Do not reveal hidden chain-of-thought. Write in a professional, academic tone suitable for research documentation.
        """
        
        # Generate Debate Graph Data
        debate_graph_prompt = f"""
        Analyze the debate transcript and generate data for visualizing agent debate analysis.

        Debate Transcript:
        {"\\n\\n".join(full_transcript)}

        Output JSON data with the following structure:
        {{
          "debate_turns": [
            {{
              "turn": 1,
              "agent": "Visionary",
              "confidence": 0.8,
              "key_points": ["point1", "point2"],
              "challenges_addressed": []
            }},
            {{
              "turn": 2,
              "agent": "Skeptic",
              "confidence": 0.6,
              "key_points": ["critique1", "critique2"],
              "challenges_addressed": ["challenge1"]
            }}
          ],
          "overall_metrics": {{
            "total_turns": 2,
            "visionary_strength": 0.8,
            "skeptic_concerns": 0.6,
            "resolution_score": 0.7
          }}
        }}

        Assign realistic confidence scores (0.1-1.0) based on the strength of arguments.
        """

        debate_graph_response = await self._safe_generate(debate_graph_prompt)
        debate_graph_data = debate_graph_response.strip()

        # Generation calls
        discovery_response = await self._safe_generate(discovery_prompt)
        discovery_report = discovery_response.strip()

        synthesis_response = await self._safe_generate(synthesis_prompt)
        raw_report = synthesis_response.strip()
        
        # Isolate and parse the JSON block
        import re, json, math
        gamma_score = 0.0
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_report, re.DOTALL)
        
        if json_match:
            try:
                metrics = json.loads(json_match.group(1))
                g_sev = float(metrics.get("G_severity", 5.0))
                v_cert = float(metrics.get("V_certainty", 0.5))
                d_age = float(metrics.get("D_age", 5.0))
                
                # Formula: Gamma = (G_severity * V_certainty) * log10(D_age + 2)
                gamma_score = (g_sev * v_cert) * math.log10(d_age + 2)
                
                # Strip the json block dynamically from the manuscript
                ieee_report = raw_report.replace(json_match.group(0), "").strip()
            except Exception as e:
                print(f"DEBUG: Failed to parse Gamma JSON: {e}")
                ieee_report = raw_report
        else:
            ieee_report = raw_report
        
        report_path = os.path.join(os.getcwd(), "ieee_report.md")
        with open(report_path, "w") as f:
            f.write(ieee_report)
            
        await self.log("System", f"Swarm complete. Gamma Score: {gamma_score:.2f}")
        return {
            "discovery_report": discovery_report,
            "ieee_manuscript": ieee_report,
            "gamma_score": gamma_score,
            "debate_graph_data": debate_graph_data
        }
