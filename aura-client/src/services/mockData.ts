export interface KpiMetric {
  label: string;
  value: number;
  delta: string;
  icon: 'Home' | 'Zap' | 'Activity';
  color: 'blue' | 'yellow' | 'green';
  isPercent?: boolean;
}

export const generateKpiData = (): KpiMetric[] => {
  const randomDelta = () => (Math.random() * 8 - 4).toFixed(1); // +/-4%
  
  return [
    {
      label: 'Active Properties',
      value: 24 + Math.floor(Math.random() * 3 - 1), // fluctuate ±1
      delta: randomDelta(),
      icon: 'Home',
      color: 'blue',
    },
    {
      label: 'AI Requests',
      value: 18 + Math.floor(Math.random() * 5 - 2), // fluctuate ±2
      delta: randomDelta(),
      icon: 'Zap',
      color: 'yellow',
    },
    {
      label: 'Engagement Rate',
      value: 76 + Math.floor(Math.random() * 6 - 3), // fluctuate ±3
      delta: randomDelta(),
      icon: 'Activity',
      color: 'green',
      isPercent: true,
    },
  ];
};
