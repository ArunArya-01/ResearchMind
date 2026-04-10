import { Link } from "react-router-dom";
import { ArrowRight, Zap, Brain, Network } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-bone font-display text-6xl md:text-7xl font-bold tracking-tight mb-6">
            Research<span className="text-crimson">Mind</span>
          </h1>
          <p className="text-bone/60 font-mono text-lg md:text-xl max-w-3xl mx-auto leading-relaxed">
            The next great discovery is hiding in the gap between two fields that have never spoken.
          </p>
        </div>

        {/* Problem Statement */}
        <div className="glass-panel p-8 md:p-12 mb-12">
          <h2 className="text-pure-black font-display text-3xl font-bold mb-6 text-center">
            The Problem
          </h2>
          <p className="text-pure-black/70 font-mono text-base leading-relaxed max-w-4xl mx-auto">
            The modern scientific community suffers from extreme "information overload." The sheer volume of published papers prevents meaningful cross-domain innovation. As researchers specialize deeply into narrow niches, critical interdisciplinary connections are lost. These undiscovered connections—the white spaces where two unrelated scientific fields have not yet been bridged—are where the next major breakthroughs lie.
          </p>
        </div>

        {/* Solution Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="glass-panel p-8">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-xl bg-crimson/20 mr-4">
                <Zap className="w-8 h-8 text-crimson" />
              </div>
              <h3 className="text-pure-black font-display text-xl font-semibold">
                Ingestion (Vision)
              </h3>
            </div>
            <p className="text-pure-black/70 font-mono text-sm leading-relaxed">
              Uses Multimodal AI to scan research PDFs, meticulously extracting not just the text, but the technical data embedded in charts, tables, and diagrams.
            </p>
          </div>

          <div className="glass-panel p-8">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-xl bg-crimson/20 mr-4">
                <Brain className="w-8 h-8 text-crimson" />
              </div>
              <h3 className="text-pure-black font-display text-xl font-semibold">
                Synthesis (Swarm)
              </h3>
            </div>
            <p className="text-pure-black/70 font-mono text-sm leading-relaxed">
              Transforms the extracted data into an interactive 3D Knowledge Graph, identifying isolated clusters. Highlights "Discovery Gaps" as glowing red anomalies.
            </p>
          </div>

          <div className="glass-panel p-8">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-xl bg-crimson/20 mr-4">
                <Network className="w-8 h-8 text-crimson" />
              </div>
              <h3 className="text-pure-black font-display text-xl font-semibold">
                Artifact (Manuscript)
              </h3>
            </div>
            <p className="text-pure-black/70 font-mono text-sm leading-relaxed">
              Converts the chaotic swarm debate into a synthesized, polished scientific manuscript that serves as a ready-to-test research proposal.
            </p>
          </div>
        </div>

        {/* Core USP */}
        <div className="glass-panel p-8 md:p-12 mb-12">
          <h2 className="text-pure-black font-display text-3xl font-bold mb-6 text-center">
            Adversarial Swarm Logic
          </h2>
          <p className="text-pure-black/70 font-mono text-base leading-relaxed max-w-4xl mx-auto mb-8">
            The heart of ResearchMind is our Adversarial Swarm (Agentic AI)—a highly specialized structural debate system designed to eliminate LLM hallucinations and generate robust scientific hypotheses.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="text-center">
              <h4 className="text-crimson font-display text-xl font-semibold mb-3">Agent Alpha (The Visionary)</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                Looks at the "Red Anomalies" in the Knowledge Graph and proposes wild, novel hypotheses to bridge the gaps.
              </p>
            </div>
            <div className="text-center">
              <h4 className="text-crimson font-display text-xl font-semibold mb-3">Agent Beta (The Skeptic)</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                Rigorously "red-teams" the visionary's proposals. Challenges logic, checks against known constraints, and demands structural proof.
              </p>
            </div>
          </div>
        </div>

        {/* Key Features */}
        <div className="glass-panel p-8 md:p-12 mb-12">
          <h2 className="text-pure-black font-display text-3xl font-bold mb-8 text-center">
            Key Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="p-4 rounded-xl bg-crimson/10 mb-4">
                <Zap className="w-12 h-12 text-crimson mx-auto" />
              </div>
              <h4 className="text-pure-black font-display text-lg font-semibold mb-2">Multimodal Ingestion</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                Powered by Gemini to comprehensively analyze complex visual and textual data.
              </p>
            </div>
            <div className="text-center">
              <div className="p-4 rounded-xl bg-crimson/10 mb-4">
                <Network className="w-12 h-12 text-crimson mx-auto" />
              </div>
              <h4 className="text-pure-black font-display text-lg font-semibold mb-2">3D Knowledge Graph</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                An interactive, real-time 3D constellation of 200+ research nodes mapping out relationships.
              </p>
            </div>
            <div className="text-center">
              <div className="p-4 rounded-xl bg-crimson/10 mb-4">
                <Brain className="w-12 h-12 text-crimson mx-auto" />
              </div>
              <h4 className="text-pure-black font-display text-lg font-semibold mb-2">Discovery Gaps</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                Visually highlights structural disconnected areas in research as pulsing red anomalies.
              </p>
            </div>
            <div className="text-center">
              <div className="p-4 rounded-xl bg-crimson/10 mb-4">
                <ArrowRight className="w-12 h-12 text-crimson mx-auto" />
              </div>
              <h4 className="text-pure-black font-display text-lg font-semibold mb-2">Synthesis Report</h4>
              <p className="text-pure-black/70 font-mono text-sm">
                Automatically generates beautifully formatted final research proposals from the Swarm's debate.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="glass-panel p-8 md:p-12 inline-block">
            <h2 className="text-pure-black font-display text-2xl font-bold mb-4">
              Ready to Bridge the Gaps?
            </h2>
            <p className="text-pure-black/70 font-mono text-base mb-6">
              Explore our multimodal vision capabilities or dive into the synthesis lab to witness the swarm in action.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/vision"
                className="inline-flex items-center px-6 py-3 bg-crimson text-bone font-display font-semibold rounded-lg hover:bg-crimson/90 transition-colors"
              >
                Explore Vision <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
              <Link
                to="/synthesis"
                className="inline-flex items-center px-6 py-3 glass-panel text-pure-black font-display font-semibold rounded-lg hover:bg-bone/95 transition-colors"
              >
                Synthesis Lab <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
