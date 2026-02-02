'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import SignalCard from '@/components/SignalCard';
import { useTradeSignals, useSymbols, useIndicators } from '@/lib/hooks';

export default function Market() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const { symbols, isLoading: symbolsLoading } = useSymbols('US');
  const { signals, score, recommendation, isLoading: signalsLoading } = useTradeSignals(selectedSymbol);
  const { indicators, isLoading: indicatorsLoading } = useIndicators(selectedSymbol);

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Market Scanner</h1>

          {/* Symbol Selection */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <label className="block text-sm font-medium text-dark mb-3">Select Symbol</label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            >
              {symbolsLoading ? (
                <option>Loading symbols...</option>
              ) : (
                symbols.map((sym: any) => (
                  <option key={sym} value={sym}>
                    {sym}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Main Signal Card */}
          {signalsLoading ? (
            <div className="text-center text-gray-500 py-8">Loading signals...</div>
          ) : (
            <>
              <SignalCard
                symbol={selectedSymbol}
                score={score || 0}
                recommendation={recommendation || 'NEUTRAL'}
                indicators={indicators}
              />

              {/* Indicators Grid */}
              {indicators && Object.keys(indicators).length > 0 && (
                <div className="mt-8">
                  <h2 className="text-2xl font-bold text-dark mb-4">Technical Indicators</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(indicators).map(([key, value]: [string, any]) => (
                      <div key={key} className="bg-white rounded-lg shadow p-4">
                        <h3 className="text-sm font-medium text-gray-600 uppercase">{key}</h3>
                        <p className="text-2xl font-bold text-dark mt-2">
                          {typeof value === 'number' ? value.toFixed(2) : String(value)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
