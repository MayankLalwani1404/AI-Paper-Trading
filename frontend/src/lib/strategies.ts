export type BuiltInStrategy = {
  id: string;
  name: string;
  description: string;
  exitRules: string[];
  defaults: {
    stopLossPct: number;
    takeProfitPct: number;
    trailingStopPct: number;
    timeExitDays: number;
  };
};

export const BUILT_IN_STRATEGIES: BuiltInStrategy[] = [
  {
    id: 'trend_following',
    name: 'Trend Following',
    description: 'Uses moving averages and breakouts to follow strong trends.',
    exitRules: ['Stop-loss', 'Trailing stop', 'Take-profit'],
    defaults: { stopLossPct: 2, takeProfitPct: 6, trailingStopPct: 3, timeExitDays: 10 },
  },
  {
    id: 'momentum_rsi',
    name: 'Momentum RSI',
    description: 'Buys when RSI is strong but not overbought; sells on weakness.',
    exitRules: ['Stop-loss', 'Take-profit', 'Time-based exit'],
    defaults: { stopLossPct: 2.5, takeProfitPct: 5, trailingStopPct: 0, timeExitDays: 7 },
  },
  {
    id: 'breakout_volume',
    name: 'Breakout + Volume',
    description: 'Targets breakouts with confirming volume strength.',
    exitRules: ['Stop-loss', 'Trailing stop'],
    defaults: { stopLossPct: 3, takeProfitPct: 8, trailingStopPct: 4, timeExitDays: 12 },
  },
  {
    id: 'mean_reversion',
    name: 'Mean Reversion',
    description: 'Looks for oversold conditions and reverts to average price.',
    exitRules: ['Stop-loss', 'Take-profit'],
    defaults: { stopLossPct: 2, takeProfitPct: 4, trailingStopPct: 0, timeExitDays: 5 },
  },
];

export const getStrategyById = (id?: string | null): BuiltInStrategy | undefined =>
  BUILT_IN_STRATEGIES.find((s) => s.id === id);
