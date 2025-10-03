import React from 'react';

interface WaveformVisualizerProps {
  levels: number[];
  isActive: boolean;
  height?: number;
}

const clamp = (value: number, min = 0, max = 1) => Math.min(max, Math.max(min, value));

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  levels,
  isActive,
  height = 96,
}) => {
  const barCount = levels.length;

  return (
    <div
      className="relative flex w-full items-center justify-center overflow-hidden rounded-xl bg-black/20 px-3 py-6"
      style={{ minHeight: height }}
      aria-hidden="true"
    >
      <div className="flex h-full w-full max-w-md items-end justify-center gap-1">
        {Array.from({ length: barCount }).map((_, index) => {
          const level = clamp(levels[index] ?? 0);
          const barHeight = (level ** 0.8) * height;
          return (
            <span
              key={index}
              className={`h-full w-[3px] rounded-full transition-all duration-75 ease-out ${
                isActive ? 'bg-red-400' : 'bg-white/40'
              }`}
              style={{ height: Math.max(6, barHeight) }}
            />
          );
        })}
      </div>
      <div
        className={`absolute left-1/2 top-1/2 flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-white/20 bg-white/10 text-xs font-semibold ${
          isActive ? 'text-red-200' : 'text-white/60'
        }`}
      >
        {isActive ? 'REC' : 'IDLE'}
      </div>
    </div>
  );
};

export default WaveformVisualizer;
