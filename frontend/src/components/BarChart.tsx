import { Bar, BarChart as RechartsBarChart, XAxis, YAxis } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";

interface BarChartProps {
  data: Array<{ [key: string]: any }>;
  config: { [key: string]: { label: string; color: string } };
  xKey: string;
  yKey: string;
  width?: number;
  height?: number;
}

const BarChart = ({ data, config, xKey, yKey, width = 400, height = 300 }: BarChartProps) => {
  return (
    <ChartContainer config={config} className="min-h-[200px] w-full">
      <RechartsBarChart data={data} width={width} height={height}>
        <XAxis dataKey={xKey} />
        <YAxis />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey={yKey} fill={`var(--color-${yKey})`} />
      </RechartsBarChart>
    </ChartContainer>
  );
};

export default BarChart;