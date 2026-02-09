'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { tradingAPI } from '@/lib/api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Trading() {
  const [formData, setFormData] = useState({
    symbol: 'AAPL',
    quantity: 1,
    side: 'BUY',
    orderType: 'MARKET',
    orderPrice: 150,
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const formatError = (error: any, fallback: string) => {
    const detail = error?.response?.data?.detail;
    if (!detail) return fallback;
    if (typeof detail === 'string') return detail;
    return JSON.stringify(detail);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' || name === 'orderPrice' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      const response = await tradingAPI.placeOrder({
        symbol: formData.symbol,
        quantity: formData.quantity,
        side: formData.side,
        order_type: formData.orderType,
        price: formData.orderPrice,
      });

      if (response.status === 200 || response.status === 201) {
        setMessage({
          type: 'success',
          text: `Order placed successfully! Order ID: ${response.data.id}`,
        });
        setFormData({ symbol: 'AAPL', quantity: 1, side: 'BUY', orderType: 'MARKET', orderPrice: 150 });
      }
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: formatError(error, 'Failed to place order'),
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-64 flex-1 bg-light p-8">
        <div className="max-w-2xl">
          <h1 className="text-4xl font-bold text-dark mb-8">Place Trade</h1>

          {/* Message Alert */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
              message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            }`}>
              {message.type === 'success' ? (
                <CheckCircle className="text-green-600" size={20} />
              ) : (
                <AlertCircle className="text-red-600" size={20} />
              )}
              <p className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
                {message.text}
              </p>
            </div>
          )}

          {/* Trading Form */}
          <div className="bg-white rounded-lg shadow p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Symbol */}
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Symbol</label>
                <input
                  type="text"
                  name="symbol"
                  value={formData.symbol}
                  onChange={handleInputChange}
                  placeholder="e.g., AAPL"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                  required
                />
              </div>

              {/* Order Type */}
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Side</label>
                <select
                  name="side"
                  value={formData.side}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-dark mb-2">Order Type</label>
                <select
                  name="orderType"
                  value={formData.orderType}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                >
                  <option value="MARKET">MARKET</option>
                  <option value="LIMIT">LIMIT</option>
                </select>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Quantity</label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  placeholder="1"
                  min="1"
                  step="1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                  required
                />
              </div>

              {/* Price */}
              <div>
                <label className="block text-sm font-medium text-dark mb-2">Price Per Share</label>
                <input
                  type="number"
                  name="orderPrice"
                  value={formData.orderPrice}
                  onChange={handleInputChange}
                  placeholder="150.00"
                  step="0.01"
                  min="0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                  required
                />
              </div>

              {/* Summary */}
              <div className="bg-light p-4 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Total Value:</span>
                  <span className="font-semibold text-dark">
                    ${(formData.quantity * formData.orderPrice).toFixed(2)}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  {formData.quantity} × ${formData.orderPrice.toFixed(2)}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-colors ${
                  formData.side === 'BUY'
                    ? 'bg-green-600 hover:bg-green-700 disabled:bg-gray-400'
                    : 'bg-red-600 hover:bg-red-700 disabled:bg-gray-400'
                }`}
              >
                {isLoading ? 'Placing Order...' : `${formData.side} ${formData.quantity} ${formData.symbol}`}
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
