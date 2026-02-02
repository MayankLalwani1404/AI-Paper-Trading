'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { usePortfolio, useLatestPrice } from '@/lib/hooks';
import { TrendingUp, Eye, EyeOff } from 'lucide-react';
import SignalCard from '@/components/SignalCard';

export default function Home() {
  const { portfolio, totalValue, cashBalance, isLoading } = usePortfolio();
  const [showBalance, setShowBalance] = useState(true);

  const topGainers = portfolio?.slice(0, 5) || [];

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-dark">Dashboard</h1>
            <p className="text-gray-600 mt-2">Welcome back! Here's your trading overview.</p>
          </div>

          {/* Portfolio Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Total Portfolio Value</p>
              <div className="flex items-center justify-between mt-3">
                <p className="text-3xl font-bold text-dark">
                  {showBalance ? `$${(totalValue || 0).toFixed(2)}` : '••••••'}
                </p>
                <button
                  onClick={() => setShowBalance(!showBalance)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {showBalance ? <Eye size={20} /> : <EyeOff size={20} />}
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Cash Balance</p>
              <p className="text-3xl font-bold text-green-600 mt-3">
                ${(cashBalance || 0).toFixed(2)}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Open Positions</p>
              <p className="text-3xl font-bold text-primary mt-3">
                {portfolio?.length || 0}
              </p>
            </div>
          </div>

          {/* Top Gainers */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold text-dark mb-4 flex items-center">
              <TrendingUp className="mr-2 text-primary" />
              Top Positions
            </h2>
            {isLoading ? (
              <p className="text-gray-500">Loading positions...</p>
            ) : topGainers.length > 0 ? (
              <div className="space-y-3">
                {topGainers.map((position: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-light rounded">
                    <div>
                      <p className="font-semibold text-dark">{position.symbol}</p>
                      <p className="text-sm text-gray-600">{position.quantity} shares @ ${position.entry_price}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-dark">${(position.quantity * position.entry_price).toFixed(2)}</p>
                      <p className={`text-sm ${position.gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.gain >= 0 ? '+' : ''}{position.gain.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No open positions</p>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button className="bg-primary text-white rounded-lg shadow p-6 hover:bg-blue-600 transition-colors text-left">
              <h3 className="text-lg font-semibold mb-2">Place Trade</h3>
              <p className="text-blue-100">Buy or sell securities</p>
            </button>
            <button className="bg-secondary text-white rounded-lg shadow p-6 hover:bg-green-600 transition-colors text-left">
              <h3 className="text-lg font-semibold mb-2">Market Scanner</h3>
              <p className="text-green-100">Analyze market trends</p>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
