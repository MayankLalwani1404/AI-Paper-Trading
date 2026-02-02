'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { aiAPI } from '@/lib/api';

export default function AIFilter() {
  const [query, setQuery] = useState('Show me stocks where RSI crossed above 70 in the last 3 days');
  const [market, setMarket] = useState('US');
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [spec, setSpec] = useState<any>(null);

  const runFilter = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await aiAPI.filter(query, market, limit);
      setResults(response.data.results || []);
      setSpec(response.data.spec || null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run filter');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-6xl">
          <h1 className="text-4xl font-bold text-dark mb-8">AI Filter</h1>

          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <label className="block text-sm font-medium text-dark mb-2">Query</label>
            <textarea
              rows={4}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Market</label>
                <select
                  value={market}
                  onChange={(e) => setMarket(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="US">US</option>
                  <option value="NSE">NSE</option>
                  <option value="BSE">BSE</option>
                  <option value="CRYPTO">CRYPTO</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Limit</label>
                <input
                  type="number"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={runFilter}
                  className="w-full px-4 py-2 bg-primary text-white rounded-lg"
                >
                  {loading ? 'Running...' : 'Run Filter'}
                </button>
              </div>
            </div>
          </div>

          {error && <div className="text-red-600 mb-4">{error}</div>}

          {spec && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-dark mb-2">Parsed Spec</h2>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                {JSON.stringify(spec, null, 2)}
              </pre>
            </div>
          )}

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-dark mb-4">Results</h2>
            {results.length === 0 ? (
              <div className="text-gray-500">No results</div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {results.map((sym) => (
                  <span key={sym} className="bg-light px-3 py-1 rounded-full text-sm">
                    {sym}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
