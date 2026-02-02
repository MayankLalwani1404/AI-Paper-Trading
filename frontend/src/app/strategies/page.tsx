'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';

const BUILT_IN_STRATEGIES = [
  {
    name: 'Trend Following',
    description: 'Uses moving averages and breakouts to follow strong trends.',
    exitRules: ['Stop-loss', 'Trailing stop', 'Take-profit'],
  },
  {
    name: 'Momentum RSI',
    description: 'Buys when RSI is strong but not overbought; sells on weakness.',
    exitRules: ['Stop-loss', 'Take-profit', 'Time-based exit'],
  },
  {
    name: 'Breakout + Volume',
    description: 'Targets breakouts with confirming volume strength.',
    exitRules: ['Stop-loss', 'Trailing stop'],
  },
  {
    name: 'Mean Reversion',
    description: 'Looks for oversold conditions and reverts to average price.',
    exitRules: ['Stop-loss', 'Take-profit'],
  },
];

export default function Strategies() {
  const [customStrategy, setCustomStrategy] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('custom_strategy');
    if (stored) setCustomStrategy(stored);
  }, []);

  const saveCustom = () => {
    localStorage.setItem('custom_strategy', customStrategy);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Strategies</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            {BUILT_IN_STRATEGIES.map((s) => (
              <div key={s.name} className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-dark mb-2">{s.name}</h2>
                <p className="text-gray-600 mb-3">{s.description}</p>
                <div className="text-sm text-gray-500">Exit rules: {s.exitRules.join(', ')}</div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-dark mb-2">Custom Technique (Your Account Only)</h2>
            <p className="text-gray-600 mb-4">Describe your technique in plain language or pseudo-code.</p>
            <textarea
              rows={6}
              value={customStrategy}
              onChange={(e) => setCustomStrategy(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Example: Buy when RSI &lt; 30 and MACD crosses up. Exit at 10% profit or 3% stop."
            />
            <div className="mt-4 flex items-center gap-3">
              <button onClick={saveCustom} className="px-4 py-2 bg-primary text-white rounded-lg">
                Save Technique
              </button>
              {saved && <span className="text-green-600">Saved!</span>}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
