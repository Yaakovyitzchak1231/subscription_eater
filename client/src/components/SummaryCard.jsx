import React from 'react';

const SummaryCard = ({ totalSpend, upcomingPaymentsCount, upcomingPaymentsAmount }) => {
  return (
    <section className="w-full">
      <div className="relative overflow-hidden rounded-2xl bg-surface-light dark:bg-surface-dark shadow-sm border border-slate-100 dark:border-slate-700/30 p-6">
        {/* Background decorative elements */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-primary/5 blur-3xl"></div>
        <div className="relative z-10 flex flex-col gap-1">
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Total Monthly Spend</p>
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-extrabold text-slate-900 dark:text-primary tracking-tight">${totalSpend.toFixed(2)}</span>
            <span className="text-sm font-medium text-slate-400">/ mo</span>
          </div>
        </div>
        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-700/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 text-primary">
              <span className="material-symbols-outlined text-lg">calendar_month</span>
            </span>
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 dark:text-slate-400">Upcoming this week</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white">{upcomingPaymentsCount} payments (${upcomingPaymentsAmount.toFixed(2)})</span>
            </div>
          </div>
          <button className="text-xs font-bold text-primary hover:text-primary/80 transition-colors">
            View Details
          </button>
        </div>
      </div>
    </section>
  );
};

export default SummaryCard;
