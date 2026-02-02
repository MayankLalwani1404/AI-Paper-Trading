'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { TrendingUp, Wallet, BarChart3, Zap, Home, Settings, List, Sparkles, Filter, Wand2 } from 'lucide-react';
import clsx from 'clsx';

const Sidebar = () => {
  const pathname = usePathname();

  const navItems = [
    { label: 'Dashboard', href: '/', icon: Home },
    { label: 'Portfolio', href: '/portfolio', icon: Wallet },
    { label: 'Market', href: '/market', icon: TrendingUp },
    { label: 'Charts', href: '/charts', icon: BarChart3 },
    { label: 'Watchlists', href: '/watchlists', icon: List },
    { label: 'AI Filter', href: '/ai-filter', icon: Filter },
    { label: 'Strategies', href: '/strategies', icon: Sparkles },
    { label: 'Auto-Trade', href: '/auto-trade', icon: Wand2 },
    { label: 'Trading', href: '/trading', icon: Zap },
  ];

  return (
    <aside className="w-64 bg-dark text-white h-screen fixed left-0 top-0 pt-6">
      <div className="px-6 mb-8">
        <h1 className="text-2xl font-bold">AI Trading</h1>
      </div>

      <nav className="space-y-2 px-4">
        {navItems.map(({ label, href, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
              pathname === href
                ? 'bg-primary text-white'
                : 'text-gray-300 hover:bg-gray-700'
            )}
          >
            <Icon size={20} />
            <span>{label}</span>
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 px-4 py-4 border-t border-gray-700">
        <Link
          href="/settings"
          className="flex items-center space-x-3 px-4 py-3 text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <Settings size={20} />
          <span>Settings</span>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;
