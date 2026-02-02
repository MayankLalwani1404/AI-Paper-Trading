'use client';

import React from 'react';
import { AlertCircle, CheckCircle, TrendingDown, TrendingUp } from 'lucide-react';

interface SignalCardProps {
  symbol: string;
  score: number;
  recommendation: string;
  indicators?: Record<string, any>;
}

const SignalCard: React.FC<SignalCardProps> = ({ symbol, score, recommendation, indicators }) => {
  const getSignalColor = (score: number) => {
    if (score >= 50) return 'text-green-500';
    if (score >= 0) return 'text-blue-500';
    if (score >= -50) return 'text-orange-500';
    return 'text-red-500';
  };

  const getSignalIcon = (score: number) => {
    if (score >= 30) return <TrendingUp className={getSignalColor(score)} />;
    if (score <= -30) return <TrendingDown className={getSignalColor(score)} />;
    return <AlertCircle className={getSignalColor(score)} />;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-primary">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-dark">{symbol}</h3>
          <p className="text-gray-600 mt-1">{recommendation}</p>
        </div>
        <div className="flex items-center space-x-2">
          {getSignalIcon(score)}
          <span className={`text-2xl font-bold ${getSignalColor(score)}`}>
            {score.toFixed(1)}
          </span>
        </div>
      </div>

      {indicators && (
        <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
          {Object.entries(indicators).slice(0, 3).map(([key, value]: [string, any]) => (
            <div key={key} className="bg-light p-2 rounded">
              <p className="text-gray-600">{key}</p>
              <p className="font-semibold text-dark">
                {typeof value === 'number' ? value.toFixed(2) : String(value)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SignalCard;
