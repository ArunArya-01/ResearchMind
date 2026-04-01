import asyncio
import os
import google.generativeai as genai
from typing import Callable, Any, Awaitable

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class SwarmOrchestrator:
    def _select_best_model(self) -> str:
        available_models = []
        try:
            for m in genai.list_models():
                if "generateContent" in getattr(m, "supported_generation_methods", []):
                    available_models.append(m.name)
        except Exception:
            pass

        priorities = ['models/gemini-3-flash', 'models/gemini-2.5-flash', 'models/gemini-1.5-flash']
        selected = None
        for p in priorities:
            if p in available_models or p.replace('models/', '') in available_models:
                selected = p
                break
                
        if not selected:
            if available_models:
                selected = available_models[0]
            else:
                print("CRITICAL: No generative models available for this API key.")
                selected = 'gemini-1.5-flash-latest'
                
        return selected.replace('models/', '')

    def __init__(self, log_callback: Callable[[str], Awaitable[Any]]):
        self.log_callback = log_callback
        model_name = self._select_best_model()
        self.model = genai.GenerativeModel(model_name)
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
        try:
            return await asyncio.to_thread(self.model.generate_content, prompt)
        except Exception as e:
            if '429' in str(e) or 'ResourceExhausted' in getattr(type(e), '__name__', ''):
                await self.log_status("Agent is cooling down (Rate Limit)... Retrying in 10s.")
                await asyncio.sleep(10)
                return await asyncio.to_thread(self.model.generate_content, prompt)
            raise e

    async def run_swarm(self, discovery_gap_data: dict, topic: str):
        print("DEBUG: Alpha Agent starting...")
        print(f"DEBUG: Using model: {self.model.model_name}")
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
            hypothesis = alpha_response.text.strip()
            
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
            critique = beta_response.text.strip()
            
            await self.log("Skeptic", f"Critique Findings (3 Flaws):\n{critique}\n")

        # Final Synthesis
        await self.log("System", "Generating Final Synthesis Report...")
        
        override_text_final = ""
        if self.active_overrides:
            override_text_final = f"\n\n<[ CRITICAL DIRECTOR COMMAND DIRECTIVE: IMPERATIVE OVERRIDE ]>\n" + "\n".join(self.active_overrides) + "\n</[ CRITICAL DIRECTOR COMMAND DIRECTIVE ]>\n"
            self.active_overrides = []
            
        synthesis_prompt = f"""
        You are the Master Synthesizer.
        Topic: {topic}
        Final Hypothesis: {hypothesis}
        Final Critique: {critique}
        {override_text_final}
        
        Write a final 'synthesis_report.md' summarizing the findings, the final hypothesis, and acknowledging the remaining risks. Format it beautifully in Markdown.

        CRITICAL REQUIREMENT 1: You MUST include a specific section heading exactly titled "<b style="color:crimson;">CRITICAL RESEARCH GAPS</b>" (including the HTML tags) detailing the safety gaps found.
        
        CRITICAL REQUIREMENT 2: You MUST include an 'ACTIONABLE MAINTENANCE PROTOCOL' (a 3-step bulleted list) in your report outlining exactly how to mitigate the found risks.
        
        CRITICAL REQUIREMENT 3: At the absolute very end of your response, output a strict JSON block wrapped in ```json ... ``` containing EXACTLY three variables based on your findings:
        - "G_severity": an integer/float from 1-10 assessing the safety gap severity.
        - "V_certainty": a float from 0.1 to 1.0 reflecting your confidence level.
        - "D_age": the estimated age of the primary methodology/context in years (integer).
        """
        synthesis_response = await self._safe_generate(synthesis_prompt)
        raw_report = synthesis_response.text.strip()
        
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
