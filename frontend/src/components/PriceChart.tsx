'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PriceChartProps {
  data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  symbol: string;
  isLoading?: boolean;
}

const PriceChart: React.FC<PriceChartProps> = ({ data, symbol, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <p className="text-gray-500">Loading chart...</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-dark mb-4">{symbol} Price Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            style={{ fontSize: '12px' }}
            tick={{ fill: '#666' }}
          />
          <YAxis 
            style={{ fontSize: '12px' }}
            tick={{ fill: '#666' }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            formatter={(value: any) => (typeof value === 'number' ? value.toFixed(2) : value)}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="close" 
            stroke="#3b82f6" 
            dot={false}
            name="Close"
          />
          <Line 
            type="monotone" 
            dataKey="open" 
            stroke="#10b981" 
            dot={false}
            name="Open"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceChart;
