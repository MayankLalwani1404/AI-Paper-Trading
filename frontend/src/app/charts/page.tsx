'use client';

import React from 'react';
import Sidebar from '@/components/Sidebar';
import PriceChart from '@/components/PriceChart';
import { useOHLCV, useSymbols } from '@/lib/hooks';
import { useState } from 'react';

export default function Charts() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [selectedInterval, setSelectedInterval] = useState('1d');
  const { data, isLoading } = useOHLCV(selectedSymbol, selectedInterval);
  const { symbols, isLoading: symbolsLoading } = useSymbols('US');

  const intervals = ['1m', '5m', '15m', '1h', '1d', '1w'];

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Charts</h1>

          {/* Controls */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Symbol</label>
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                >
                  {symbolsLoading ? (
                    <option>Loading symbols...</option>
                  ) : symbols.length > 0 ? (
                    symbols.map((sym: any) => (
                      <option key={sym} value={sym}>
                        {sym}
                      </option>
                    ))
                  ) : (
                    <option>AAPL</option>
                  )}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Interval</label>
                <select
                  value={selectedInterval}
                  onChange={(e) => setSelectedInterval(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                >
                  {intervals.map((int) => (
                    <option key={int} value={int}>
                      {int}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Chart */}
          <PriceChart data={data} symbol={selectedSymbol} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}
