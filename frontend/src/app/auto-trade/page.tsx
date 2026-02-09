'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { tradingAPI } from '@/lib/api';
import { BUILT_IN_STRATEGIES, getStrategyById } from '@/lib/strategies';

export default function AutoTrade() {
  const [form, setForm] = useState({
    symbol: 'AAPL',
    quantity: 1,
    side: 'BUY',
    orderType: 'MARKET',
    price: 150,
    stopLossPct: 2,
    takeProfitPct: 5,
    trailingStopPct: 3,
    timeExitDays: 5,
  });
  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('selected_strategy');
    if (stored) {
      setSelectedStrategyId(stored);
      const strat = getStrategyById(stored);
      if (strat) {
        setForm((prev) => ({
          ...prev,
          stopLossPct: strat.defaults.stopLossPct,
          takeProfitPct: strat.defaults.takeProfitPct,
          trailingStopPct: strat.defaults.trailingStopPct,
          timeExitDays: strat.defaults.timeExitDays,
        }));
      }
    }
  }, []);

  const formatError = (err: any, fallback: string) => {
    const detail = err?.response?.data?.detail;
    if (!detail) return fallback;
    if (typeof detail === 'string') return detail;
    return JSON.stringify(detail);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === 'quantity' || name === 'price' || name.includes('Pct') || name.includes('Days')
        ? Number(value)
        : value,
    }));
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const exitRules = {
        stop_loss_pct: form.stopLossPct,
        take_profit_pct: form.takeProfitPct,
        trailing_stop_pct: form.trailingStopPct,
        time_exit_days: form.timeExitDays,
      };
      const response = await tradingAPI.placeOrder({
        symbol: form.symbol,
        quantity: form.quantity,
        order_type: form.orderType,
        side: form.side,
        price: form.price,
        exit_rules: exitRules,
      });
      setMessage({
        type: 'success',
        text: `Order placed. ID: ${response.data.id}`,
      });
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: formatError(err, 'Failed to place order'),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Auto‑Trade</h1>

          {message && (
            <div className={`mb-4 rounded-lg p-3 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {message.text}
            </div>
          )}

          <form onSubmit={submit} className="bg-white rounded-lg shadow p-6 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Symbol</label>
                <input
                  name="symbol"
                  value={form.symbol}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Side</label>
                <select
                  name="side"
                  value={form.side}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark mb-2">Strategy</label>
              <select
                value={selectedStrategyId}
                onChange={(e) => {
                  const id = e.target.value;
                  setSelectedStrategyId(id);
                  const strat = getStrategyById(id);
                  if (strat) {
                    localStorage.setItem('selected_strategy', id);
                    setForm((prev) => ({
                      ...prev,
                      stopLossPct: strat.defaults.stopLossPct,
                      takeProfitPct: strat.defaults.takeProfitPct,
                      trailingStopPct: strat.defaults.trailingStopPct,
                      timeExitDays: strat.defaults.timeExitDays,
                    }));
                  }
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Manual (no preset)</option>
                {BUILT_IN_STRATEGIES.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
              {selectedStrategyId && (
                <p className="mt-2 text-sm text-gray-600">
                  {getStrategyById(selectedStrategyId)?.description}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Quantity</label>
                <input
                  type="number"
                  name="quantity"
                  value={form.quantity}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Order Type</label>
                <select
                  name="orderType"
                  value={form.orderType}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="MARKET">MARKET</option>
                  <option value="LIMIT">LIMIT</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Price</label>
                <input
                  type="number"
                  name="price"
                  value={form.price}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Stop‑Loss (%)</label>
                <input
                  type="number"
                  name="stopLossPct"
                  value={form.stopLossPct}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Take‑Profit (%)</label>
                <input
                  type="number"
                  name="takeProfitPct"
                  value={form.takeProfitPct}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Trailing Stop (%)</label>
                <input
                  type="number"
                  name="trailingStopPct"
                  value={form.trailingStopPct}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Time Exit (days)</label>
                <input
                  type="number"
                  name="timeExitDays"
                  value={form.timeExitDays}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-lg"
            >
              {loading ? 'Placing...' : 'Place Auto‑Trade'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
