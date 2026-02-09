'use client';

import React from 'react';
import Sidebar from '@/components/Sidebar';
import { usePortfolio } from '@/lib/hooks';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';

export default function Portfolio() {
  const { portfolio, totalValue, cashBalance, isLoading } = usePortfolio();

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Portfolio</h1>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Total Value</p>
                  <p className="text-3xl font-bold text-dark mt-2">${(totalValue || 0).toFixed(2)}</p>
                </div>
                <DollarSign className="text-primary" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Cash Balance</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">${(cashBalance || 0).toFixed(2)}</p>
                </div>
                <TrendingUp className="text-green-600" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Invested</p>
                  <p className="text-3xl font-bold text-primary mt-2">${((totalValue || 0) - (cashBalance || 0)).toFixed(2)}</p>
                </div>
                <TrendingDown className="text-primary" size={32} />
              </div>
            </div>
          </div>

          {/* Holdings Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-dark">Holdings</h2>
            </div>

            {isLoading ? (
              <div className="p-6 text-center text-gray-500">Loading portfolio...</div>
            ) : portfolio && portfolio.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-light">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Symbol</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Quantity</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Entry Price</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Current Price</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Value</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Gain/Loss</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-dark">Return %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {portfolio.map((position: any, index: number) => {
                      const entryPrice = position.entry_price ?? position.avg_price ?? 0;
                      const currentPrice = position.current_price ?? entryPrice;
                      const value = position.quantity * currentPrice;
                      const gainLoss = entryPrice > 0 ? (currentPrice - entryPrice) * position.quantity : 0;
                      const returnPct = entryPrice > 0 ? ((currentPrice - entryPrice) / entryPrice) * 100 : 0;

                      return (
                        <tr key={index} className="hover:bg-light transition-colors">
                          <td className="px-6 py-4 font-semibold text-dark">{position.symbol}</td>
                          <td className="px-6 py-4 text-gray-700">{position.quantity}</td>
                          <td className="px-6 py-4 text-gray-700">${entryPrice.toFixed(2)}</td>
                          <td className="px-6 py-4 text-gray-700">${currentPrice.toFixed(2)}</td>
                          <td className="px-6 py-4 text-gray-700">${value.toFixed(2)}</td>
                          <td className={`px-6 py-4 font-semibold ${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {gainLoss >= 0 ? '+' : ''}${gainLoss.toFixed(2)}
                          </td>
                          <td className={`px-6 py-4 font-semibold ${returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-6 text-center text-gray-500">No holdings yet</div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
