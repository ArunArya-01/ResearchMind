interface RadialGaugeProps {
  progress: number;
  size?: number;
  label?: string;
}

const RadialGauge = ({ progress, size = 80, label }: RadialGaugeProps) => {
  const strokeWidth = 5;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="hsl(0 0% 16%)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="hsl(var(--crimson))"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: "stroke-dashoffset 1s ease-out",
          }}
        />
      </svg>
      <span className="text-pure-black font-mono text-xs font-semibold">{progress}%</span>
      {label && <span className="text-pure-black/60 text-xs font-display">{label}</span>}
    </div>
  );
};

export default RadialGauge;
