import React from 'react';
import { Target, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';

interface StatsCardsProps {
  attempted: number;
  solved: number;
  hintsUsed: number;
  rating: number;
}

export const StatsCards: React.FC<StatsCardsProps> = ({
  attempted,
  solved,
  hintsUsed,
  rating,
}) => {
  const successRate = attempted > 0 ? Math.round((solved / attempted) * 100) : 0;
  const avgHints = solved > 0 ? (hintsUsed / solved).toFixed(1) : '0';

  const cards = [
    {
      label: 'Performance Rating',
      value: rating,
      desc: 'Based on solved problems difficulty',
      icon: Target,
      color: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    },
    {
      label: 'Problems Solved',
      value: `${solved}/${attempted}`,
      desc: `Success rate of ${successRate}%`,
      icon: CheckCircle2,
      color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    },
    {
      label: 'Avg Hints Used',
      value: avgHints,
      desc: `Total hints revealed: ${hintsUsed}`,
      icon: HelpCircle,
      color: 'text-brand-400 bg-brand-500/10 border-brand-500/20',
    },
    {
      label: 'Learning Focus',
      value: solved > 0 ? 'Active' : 'Get Started',
      desc: 'Socratic timelines guide you',
      icon: AlertCircle,
      color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="glass rounded-xl p-5 flex items-center justify-between shadow-sm">
            <div className="space-y-1">
              <span className="text-xs text-dark-400 font-medium font-mono uppercase tracking-wider block">
                {card.label}
              </span>
              <span className="text-2xl font-bold text-white block">
                {card.value}
              </span>
              <span className="text-[10px] text-dark-500 block">
                {card.desc}
              </span>
            </div>
            <div className={`w-10 h-10 rounded-lg border flex items-center justify-center flex-shrink-0 ${card.color}`}>
              <Icon className="w-5 h-5" />
            </div>
          </div>
        );
      })}
    </div>
  );
};
