import React from 'react';

const SubscriptionItem = ({ subscription }) => {
  const { name, amount, billingCycle, nextPaymentDate, category, trialInfo } = subscription;

  const getLogo = (name) => {
    switch (name.toLowerCase()) {
      case 'netflix':
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-black flex-shrink-0 relative">
            <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-black flex items-center justify-center text-white font-bold text-xs">N</div>
          </div>
        );
      case 'spotify':
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-[#1DB954] flex-shrink-0 relative">
            <div className="absolute inset-0 flex items-center justify-center text-white">
              <span className="material-symbols-outlined">graphic_eq</span>
            </div>
          </div>
        );
      case 'adobe':
      case 'adobe cc':
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-[#FF0000] flex-shrink-0 relative">
            <div className="absolute inset-0 bg-gradient-to-tr from-[#FF0000] to-[#FF4D4D] flex items-center justify-center text-white font-serif font-bold text-xl">A</div>
          </div>
        );
      case 'midjourney':
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-slate-800 flex-shrink-0 relative">
            <div className="absolute inset-0 bg-slate-800 flex items-center justify-center text-white">
              <span className="material-symbols-outlined">sailing</span>
            </div>
          </div>
        );
      case 'dropbox':
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-blue-500 flex-shrink-0 relative">
            <div className="absolute inset-0 bg-blue-500 flex items-center justify-center text-white">
              <span className="material-symbols-outlined">inventory_2</span>
            </div>
          </div>
        );
      default:
        return (
          <div className="h-12 w-12 rounded-full overflow-hidden bg-primary/20 flex-shrink-0 relative">
            <div className="absolute inset-0 flex items-center justify-center text-primary font-bold">
              {name.charAt(0).toUpperCase()}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="group relative flex items-center justify-between p-4 rounded-xl bg-white dark:bg-surface-dark border border-slate-100 dark:border-transparent hover:border-primary/30 transition-all shadow-sm">
      <div className="flex items-center gap-4">
        {getLogo(name)}
        <div className="flex flex-col">
          <p className="text-base font-bold text-slate-900 dark:text-white leading-tight">{name}</p>
          {trialInfo ? (
            <div className="flex items-center gap-1 mt-0.5">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
              <p className="text-xs text-amber-500 font-medium">{trialInfo}</p>
            </div>
          ) : (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Due {nextPaymentDate ? new Date(nextPaymentDate).toLocaleDateString('en-US', { month: 'short', day: '2-digit' }) : 'N/A'} • {category || 'Other'}
            </p>
          )}
        </div>
      </div>
      <div className="flex flex-col items-end">
        <p className="text-base font-bold text-slate-900 dark:text-white">${amount.toFixed(2)}</p>
        <p className="text-xs text-slate-400">{billingCycle || 'Monthly'}</p>
      </div>
    </div>
  );
};

export default SubscriptionItem;
