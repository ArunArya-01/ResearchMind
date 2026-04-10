import asyncio
import os
from pathlib import Path
from typing import Callable, Any, Awaitable
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

_import_error = None
try:
    import google.genai as genai
except ModuleNotFoundError:
    try:
        import google.generativeai as genai
    except ModuleNotFoundError as exc:
        genai = None
        _import_error = exc


class SwarmOrchestrator:
    def _select_best_model(self) -> str:
        # Primary target requested by product direction.
        return 'gemini-1.5-flash'

    def __init__(self, log_callback: Callable[[str], Awaitable[Any]]):
      self.log_callback = log_callback
      if genai is None:
          raise RuntimeError(
              "Google GenAI SDK not installed. Install `google-genai` (preferred) or `google-generativeai`."
          ) from _import_error
      self._load_project_env()
      api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
      print(f"GOOGLE_API_KEY loaded: {bool(api_key)}")
      if not api_key:
          raise ValueError("GOOGLE_API_KEY not found in environment")

      # Ensure downstream SDK calls can discover credentials via env as well.
      os.environ["GOOGLE_API_KEY"] = api_key
      os.environ.setdefault("GEMINI_API_KEY", api_key)

      self._genai_client = None
      if hasattr(genai, "configure"):
          # Legacy SDK path (and harmless for mixed installations).
          genai.configure(api_key=api_key)
      # google-genai (new SDK) path
      if hasattr(genai, "Client"):
          self._genai_client = genai.Client(api_key=api_key)
      else:
          # If no Client exists, we rely on configure + GenerativeModel path.
          if not hasattr(genai, "GenerativeModel"):
              raise RuntimeError("Unsupported Google GenAI SDK import. Install `google-genai`.")

      self.model_name = self._select_best_model()
      self.active_overrides = []

    def _load_project_env(self) -> None:
        if load_dotenv:
            load_dotenv()
        for parent in Path(__file__).resolve().parents:
            env_path = parent / ".env"
            if env_path.exists():
                if load_dotenv:
                    load_dotenv(dotenv_path=env_path, override=False)
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
                    if key and key not in os.environ:
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

        model = genai.GenerativeModel(model_name)
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
        gate_prompt = f"""You are a strict Data Science Gatekeeper.
Evaluate this theoretical paper and this dataset:
Theory: {pdf_content[:2000]}
Dataset Columns & Summary: {csv_summary[:2000]}

Can this specific dataset legitimately benchmark, test, or prove this specific theory? Is there a strong, logical causal link? 
If they are completely unrelated (e.g., Blockchain theory and Diamond prices), you must block it to prevent spurious correlation.

Reply ONLY with "[FUSION_APPROVED]" if the dataset is scientifically relevant, or "[FUSION_TERMINATED]" if they are unrelated.
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
            scenario = "Data Scientist (CSV-only)"
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
            
            alpha_prompt = f"""
            You are Agent Alpha, the Visionary.
            Scenario: {scenario}
            Topic: {topic}
            Discovery Gap Data (PDF): {context}
            Empirical Dataset Summary (CSV): {dataset_summary if dataset_summary else 'None'}
            Previous Critique: {critique}
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

        # DuckDuckGo Novelty Verification
        await self.log("System", "Verifying novelty via DuckDuckGo Live Search...")
        novelty_context = ""
        try:
            from ddgs import DDGS
            results = DDGS().text(f"'{hypothesis}' research", max_results=3)
            novelty_context = "\\n".join([r.get('body', '') for r in results])
            await self.log("System", f"Found live context for novelty verification.")
        except Exception as e:
            print(f"DEBUG: DDG Search failed - {e}")
            novelty_context = "Could not reach DuckDuckGo for live verification."
            await self.log("System", "DuckDuckGo Live Search failed.")

        # Final Synthesis
        await self.log("System", "Generating Final Synthesis Reports...")
        
        override_text_final = ""
        if self.active_overrides:
            override_text_final = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
            self.active_overrides = []
            
        synthesis_prompt = f"""
        You are the Master Synthesizer. Topic: {topic}. Hypothesis: {hypothesis}. Critique: {critique}. {override_text_final}
        
        CRITICAL REQUIREMENT 0 (THE FEASIBILITY GATE):
        Before writing anything, evaluate if fusing these research documents makes logical, scientific sense. 
        If the domains are fundamentally incompatible and a fusion lacks scientific merit, YOU MUST ABORT. 
        If aborting, DO NOT write the IEEE paper. Instead, output ONLY this:
        1. A large header: `# 🚨 SYNTHESIS ABORTED: INCOMPATIBLE DOMAINS`
        2. Two short paragraphs explaining exactly why the AI agents determined these fields cannot be responsibly fused.
        3. The mandatory JSON block at the bottom with "G_severity" set to 10.0.
        
        If (and ONLY if) the domains are compatible, proceed to CRITICAL REQUIREMENT 1.
        
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
        It MUST contain the following sections exactly:
        # Discovery Report
        ## 1. Core Hypothesis
        [Explain the hypothesis clearly and concisely.]
        ## 2. Empirical Grounding & Data Tables
        [Analyze and present the CSV math/dataset summary. Output a markdown table summarizing the data. If no CSV text is provided, state that empirical data was not supplied.]
        ## 3. Swarm Debate Summary
        [Logically summarize the core arguments between the Visionary and Skeptic based on the transcript to show the resolution of flaws. Structure it as a debate format (e.g. Vision Agent: ... Skeptic Agent: ...)]
        ## 4. Novelty Verification
        [Evaluate the hypothesis against the DuckDuckGo live search context to assess true novelty in the field.]
        ## 5. Architectural Flow
        [Create a Mermaid.js diagram representing the system architecture or hypothesis flow inside a ```mermaid ... ``` block. Use graph TD; syntax.]
        ## 6. Research Hypotheses
        [List 3-5 specific, testable research hypotheses. For each one, include the measurable prediction and the PDF passage, dataset field, or observed summary that motivated it.]
        ## 7. Research Gaps
        [List the most important unsolved gaps discovered by the agents. Separate PDF-derived gaps, dataset-derived gaps, and validation gaps. If an input type was not supplied, state that clearly.]

        Throughout the report, expose only clean public reasoning summaries. Do not reveal hidden chain-of-thought.
        """
        
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
            "gamma_score": gamma_score
        }
