'use client';

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp } from 'lucide-react';

interface ProgressChartProps {
  rating: number;
}

export const ProgressChart: React.FC<ProgressChartProps> = ({ rating }) => {
  // Generate some rating milestone progress data leading to the current rating
  const data = [
    { name: 'Start', rating: 0 },
    { name: 'Sess 1', rating: Math.round(rating * 0.2) },
    { name: 'Sess 2', rating: Math.round(rating * 0.45) },
    { name: 'Sess 3', rating: Math.round(rating * 0.7) },
    { name: 'Sess 4', rating: Math.round(rating * 0.85) },
    { name: 'Current', rating: rating },
  ];

  return (
    <div className="glass rounded-xl p-5 flex flex-col h-[340px] shadow-sm">
      <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 border-b border-white/10 pb-3 mb-4">
        <TrendingUp className="w-4 h-4 text-brand-400" />
        Rating Progress
      </h3>

      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -25, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorRating" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.03)" />
            <XAxis
              dataKey="name"
              stroke="#475569"
              fontSize={9}
              tickLine={false}
            />
            <YAxis
              stroke="#475569"
              fontSize={9}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                color: '#fff',
                fontSize: '11px',
                borderRadius: '8px',
              }}
            />
            <Area
              type="monotone"
              dataKey="rating"
              stroke="#6366f1"
              fillOpacity={1}
              fill="url(#colorRating)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
