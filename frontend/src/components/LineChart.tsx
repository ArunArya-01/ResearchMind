import { Line, LineChart as RechartsLineChart, XAxis, YAxis } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart";

interface LineChartProps {
  data: Array<{ [key: string]: any }>;
  config: { [key: string]: { label: string; color: string } };
  xKey: string;
  yKey: string;
  width?: number;
  height?: number;
}

const LineChart = ({ data, config, xKey, yKey, width = 400, height = 300 }: LineChartProps) => {
  return (
    <ChartContainer config={config} className="min-h-[200px] w-full">
      <RechartsLineChart data={data} width={width} height={height}>
        <XAxis dataKey={xKey} />
        <YAxis />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Line type="monotone" dataKey={yKey} stroke={`var(--color-${yKey})`} strokeWidth={2} />
      </RechartsLineChart>
    </ChartContainer>
  );
};

export default LineChart;