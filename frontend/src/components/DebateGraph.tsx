import { Line, LineChart as RechartsLineChart, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";

interface DebateGraphProps {
  data: {
    debate_turns: Array<{
      turn: number;
      agent: string;
      confidence: number;
      key_points: string[];
      challenges_addressed: string[];
    }>;
    overall_metrics: {
      total_turns: number;
      visionary_strength: number;
      skeptic_concerns: number;
      resolution_score: number;
    };
  };
}

const DebateGraph = ({ data }: DebateGraphProps) => {
  // Transform data for line chart
  const chartData = data.debate_turns.map((turn) => ({
    turn: `Turn ${turn.turn}`,
    confidence: turn.confidence,
    agent: turn.agent,
  }));

  const config = {
    confidence: {
      label: "Confidence",
      color: "hsl(var(--chart-1))",
    },
  };

  return (
    <div className="w-full">
      <h3 className="text-bone font-mono text-sm mb-4">Agent Debate Analysis</h3>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-obsidian/50 p-3 rounded border border-crimson/20">
          <div className="text-xs text-bone/60">Visionary Strength</div>
          <div className="text-lg font-bold text-cyan-400">{(data.overall_metrics.visionary_strength * 100).toFixed(0)}%</div>
        </div>
        <div className="bg-obsidian/50 p-3 rounded border border-crimson/20">
          <div className="text-xs text-bone/60">Skeptic Concerns</div>
          <div className="text-lg font-bold text-yellow-400">{(data.overall_metrics.skeptic_concerns * 100).toFixed(0)}%</div>
        </div>
      </div>
      <div className="bg-obsidian/50 p-3 rounded border border-crimson/20">
        <div className="text-xs text-bone/60 mb-2">Resolution Score</div>
        <div className="text-xl font-bold text-green-400">{(data.overall_metrics.resolution_score * 100).toFixed(0)}%</div>
      </div>
      <div className="mt-4">
        <ChartContainer config={config} className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart data={chartData}>
              <XAxis dataKey="turn" />
              <YAxis domain={[0, 1]} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="confidence"
                stroke="hsl(var(--chart-1))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--chart-1))", strokeWidth: 2, r: 4 }}
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>
      <div className="mt-4 space-y-2">
        {data.debate_turns.map((turn, index) => (
          <div key={index} className="bg-obsidian/30 p-3 rounded border border-crimson/10">
            <div className="text-sm font-mono text-bone">
              <span className={turn.agent === 'Visionary' ? 'text-cyan-400' : 'text-yellow-400'}>
                {turn.agent}
              </span>
              <span className="text-bone/60 ml-2">Turn {turn.turn}</span>
            </div>
            <div className="text-xs text-bone/80 mt-1">
              Key Points: {turn.key_points.join(', ')}
            </div>
            {turn.challenges_addressed.length > 0 && (
              <div className="text-xs text-bone/60 mt-1">
                Challenges: {turn.challenges_addressed.join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DebateGraph;