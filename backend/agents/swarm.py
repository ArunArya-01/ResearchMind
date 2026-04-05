import asyncio
import os
from google import genai
from typing import Callable, Any, Awaitable


class SwarmOrchestrator:
    def _select_best_model(self) -> str:
        # Primary target requested by product direction.
        return 'gemini-2.5-flash-lite'

    def __init__(self, log_callback: Callable[[str], Awaitable[Any]]):
      self.log_callback = log_callback
      self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
      self.model_name = self._select_best_model()
      self.active_overrides = []

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
            "gemini-2.5-flash-lite",
            "models/gemini-2.5-flash-lite",
        ]
        try:
            last_error = None
            for model_name in model_candidates:
                try:
                    response = await self.client.aio.models.generate_content(model=model_name, contents=prompt)
                    # Persist the working alias for subsequent calls.
                    self.model_name = model_name
                    return response
                except Exception as e:
                    last_error = e
                    # Try next alias only for model-not-found style failures.
                    msg = str(e)
                    if "not found" not in msg.lower() and "not supported" not in msg.lower():
                        raise e
            raise last_error if last_error else RuntimeError("No valid Gemini model alias available.")
        except Exception as e:
          if '429' in str(e) or 'ResourceExhausted' in str(e):
            await self.log_status("Agent is cooling down (Rate Limit)... Retrying in 10s.")
            await asyncio.sleep(10)
            response = await self.client.aio.models.generate_content(model=self.model_name, contents=prompt)
            return response
          print(f"DEBUG: API Error: {e}")
          raise e

    async def run_swarm(self, discovery_gap_data: dict, topic: str):
        print("DEBUG: Alpha Agent starting...")
        print(f"DEBUG: Using model: {self.model_name}")
        await self.log("System", "Initializing Adversarial Swarm...")
        
        context = str(discovery_gap_data)
        hypothesis = ""
        critique = ""
        
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
            Topic: {topic}
            Discovery Gap Data: {context}
            Previous Critique: {critique}
            {override_text_alpha}
            
            Formulate a bold, innovative hypothesis based on the 'Red Anomaly' discovery gaps.
            If there was a previous critique, address those flaws in your new hypothesis.
            Keep it concise but impactful.
            """
            
            # Run blocking API call in executor (or just await if using async client, but generic genai SDK is sync by default)
            alpha_response = await self._safe_generate(alpha_prompt)
            hypothesis = alpha_response.candidates[0].content.parts[0].text.strip()
            
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
            
            Retrieved Cross-Reference Data from Vector Database:
            {vector_context}
            {override_text_beta}
            
            Perform a stark 'Red-Team' critique. PRIORITIZE FINDING SAFETY GAPS.
            Identify exactly 3 specific safety flaws, weaknesses, or unsupported claims.
            Explicitly query and cross-reference the vector database chunks provided. Compare claims from Document A against Document B to find contradictions.
            Be direct and analytical.
            """
            beta_response = await self._safe_generate(beta_prompt)
            critique = beta_response.candidates[0].content.parts[0].text.strip()
            
            await self.log("Skeptic", f"Critique Findings (3 Flaws):\n{critique}\n")

        # Final Synthesis
        await self.log("System", "Generating Final Synthesis Report...")
        
        override_text_final = ""
        if self.active_overrides:
            override_text_final = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
            self.active_overrides = []
            
        synthesis_prompt = f"""
        You are the Master Synthesizer. Topic: {topic}. Hypothesis: {hypothesis}. Critique: {critique}. {override_text_final}
        
        Write a highly comprehensive, EXHAUSTIVE synthesis report. 
        
        CRITICAL REQUIREMENT 1: Format strictly mimicking an IEEE academic paper in Markdown. You MUST generate massive volume to reach a 6-page length. Write at least 4 to 6 dense paragraphs per section. DO NOT summarize. Expand deeply on theoretical mechanics.
        
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
        - "G_severity": an integer/float from 1-10 assessing the safety gap severity.
        - "V_certainty": a float from 0.1 to 1.0 reflecting your confidence level.
        - "D_age": the estimated age of the primary methodology/context in years (integer).
        """
        synthesis_response = await self._safe_generate(synthesis_prompt)
        raw_report = synthesis_response.candidates[0].content.parts[0].text.strip()
        
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
                report = raw_report.replace(json_match.group(0), "").strip()
            except Exception as e:
                print(f"DEBUG: Failed to parse Gamma JSON: {e}")
                report = raw_report
        else:
            report = raw_report
        
        report_path = os.path.join(os.getcwd(), "synthesis_report.md")
        with open(report_path, "w") as f:
            f.write(report)
            
        await self.log("System", f"Swarm complete. Gamma Score: {gamma_score:.2f}")
        return report, gamma_score
