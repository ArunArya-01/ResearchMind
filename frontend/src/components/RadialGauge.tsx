interface RadialGaugeProps {
  progress: number;
  size?: number;
  label?: string;
  color?: string;
  backgroundColor?: string;
  showValue?: boolean;
}

const RadialGauge = ({
  progress,
  size = 80,
  label,
  color = "hsl(var(--crimson))",
  backgroundColor = "hsl(0 0% 16%)",
  showValue = true
}: RadialGaugeProps) => {
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={backgroundColor}
            strokeWidth={strokeWidth}
            fill="none"
            opacity={0.3}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{
              transition: "stroke-dashoffset 1.5s ease-out",
              filter: "drop-shadow(0 0 4px rgba(217, 4, 41, 0.3))"
            }}
          />
        </svg>
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-white font-mono text-sm font-bold">{Math.round(progress)}%</span>
          </div>
        )}
      </div>
      {label && <span className="text-bone/60 text-xs font-display text-center">{label}</span>}
    </div>
  );
};

export default RadialGauge;
