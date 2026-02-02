'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { tradingAPI } from '@/lib/api';
import { useWatchlists } from '@/lib/hooks';

export default function Watchlists() {
  const { watchlists, isLoading, mutate } = useWatchlists();
  const [name, setName] = useState('');
  const [symbol, setSymbol] = useState('');
  const [selectedWatchlist, setSelectedWatchlist] = useState<number | null>(null);
  const [message, setMessage] = useState<string>('');

  const createWatchlist = async () => {
    if (!name.trim()) return;
    await tradingAPI.createWatchlist(name.trim());
    setName('');
    setMessage('Watchlist created');
    mutate();
  };

  const addSymbol = async () => {
    if (!symbol.trim() || selectedWatchlist === null) return;
    await tradingAPI.addWatchlistItem(selectedWatchlist, symbol.trim().toUpperCase());
    setSymbol('');
    setMessage('Symbol added');
    mutate();
  };

  const removeSymbol = async (watchlistId: number, sym: string) => {
    await tradingAPI.removeWatchlistItem(watchlistId, sym);
    setMessage('Symbol removed');
    mutate();
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Watchlists</h1>

          {message && <div className="mb-4 text-green-600">{message}</div>}

          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold text-dark mb-4">Create Watchlist</h2>
            <div className="flex gap-3">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Swing Trades"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
              />
              <button
                onClick={createWatchlist}
                className="px-4 py-2 bg-primary text-white rounded-lg"
              >
                Create
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold text-dark mb-4">Add Symbol</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <select
                value={selectedWatchlist ?? ''}
                onChange={(e) => setSelectedWatchlist(Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Select watchlist</option>
                {watchlists.map((wl: any) => (
                  <option key={wl.id} value={wl.id}>{wl.name}</option>
                ))}
              </select>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="e.g., AAPL"
                className="px-4 py-2 border border-gray-300 rounded-lg"
              />
              <button
                onClick={addSymbol}
                className="px-4 py-2 bg-secondary text-white rounded-lg"
              >
                Add
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-dark mb-4">Your Watchlists</h2>
            {isLoading ? (
              <div className="text-gray-500">Loading...</div>
            ) : watchlists.length === 0 ? (
              <div className="text-gray-500">No watchlists yet</div>
            ) : (
              <div className="space-y-4">
                {watchlists.map((wl: any) => (
                  <div key={wl.id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-md font-semibold text-dark mb-2">{wl.name}</h3>
                    <div className="flex flex-wrap gap-2">
                      {wl.symbols.length === 0 ? (
                        <span className="text-gray-500">No symbols</span>
                      ) : (
                        wl.symbols.map((sym: string) => (
                          <span key={sym} className="bg-light px-3 py-1 rounded-full text-sm">
                            {sym}
                            <button
                              onClick={() => removeSymbol(wl.id, sym)}
                              className="ml-2 text-red-500"
                            >
                              ×
                            </button>
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
