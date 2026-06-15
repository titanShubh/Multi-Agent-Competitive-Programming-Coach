'use client';

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
import { BrainCircuit } from 'lucide-react';

interface TopicRadarProps {
  proficiency: Record<string, { score: number; problems_attempted: number; problems_solved: number }>;
}

export const TopicRadar: React.FC<TopicRadarProps> = ({ proficiency }) => {
  // Transform data for Recharts
  const data = Object.entries(proficiency).map(([topic, stats]) => ({
    topic,
    score: Math.round(stats.score * 100),
  }));

  const hasData = data.length > 0;

  return (
    <div className="glass rounded-xl p-5 flex flex-col h-[340px] shadow-sm">
      <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 border-b border-white/10 pb-3 mb-4">
        <BrainCircuit className="w-4 h-4 text-brand-400" />
        Topic Proficiency
      </h3>

      <div className="flex-1 flex items-center justify-center">
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
              <PolarGrid stroke="rgba(255, 255, 255, 0.05)" />
              <PolarAngleAxis
                dataKey="topic"
                tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 500 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: '#475569', fontSize: 8 }}
                axisLine={false}
              />
              <Radar
                name="Proficiency"
                dataKey="score"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.25}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center text-dark-500 space-y-1">
            <p className="text-xs font-medium">No topics analyzed yet</p>
            <p className="text-[10px] max-w-[200px]">
              Complete a session to see your algorithmic profile.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
