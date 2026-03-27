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
            
            alpha_prompt = f"""
            You are Agent Alpha, the Visionary.
            Topic: {topic}
            Discovery Gap Data: {context}
            Previous Critique: {critique}
            
            Formulate a bold, innovative hypothesis based on the 'Red Anomaly' discovery gaps.
            If there was a previous critique, address those flaws in your new hypothesis.
            Keep it concise but impactful.
            """
            
            # Run blocking API call in executor (or just await if using async client, but generic genai SDK is sync by default)
            alpha_response = await self._safe_generate(alpha_prompt)
            hypothesis = alpha_response.text.strip()
            
            await self.log("Visionary", f"Proposed Hypothesis:\n{hypothesis}\n")
            
            # Agent Beta (Skeptic)
            await self.log("Skeptic", "Evaluating hypothesis and performing Red-Team critique...")
            
            beta_prompt = f"""
            You are Agent Beta, the Skeptic.
            Hypothesis:
            {hypothesis}
            
            Perform a stark 'Red-Team' critique. Identify exactly 3 specific flaws, weaknesses, or unsupported claims in the hypothesis.
            Be direct and analytical.
            """
            beta_response = await self._safe_generate(beta_prompt)
            critique = beta_response.text.strip()
            
            await self.log("Skeptic", f"Critique Findings (3 Flaws):\n{critique}\n")

        # Final Synthesis
        await self.log("System", "Generating Final Synthesis Report...")
        synthesis_prompt = f"""
        You are the Master Synthesizer.
        Topic: {topic}
        Final Hypothesis: {hypothesis}
        Final Critique: {critique}
        
        Write a final 'synthesis_report.md' summarizing the findings, the final hypothesis, and acknowledging the remaining risks. Format it beautifully in Markdown.
        """
        synthesis_response = await self._safe_generate(synthesis_prompt)
        report = synthesis_response.text.strip()
        
        report_path = os.path.join(os.getcwd(), "synthesis_report.md")
        with open(report_path, "w") as f:
            f.write(report)
            
        await self.log("System", f"Swarm complete. Report saved to synthesis_report.md")
        return report
