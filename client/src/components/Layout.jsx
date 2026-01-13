import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="min-min-h-screen pb-24">
      {/* Header */}
      <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-4 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-surface-light dark:bg-surface-dark flex items-center justify-center shadow-sm overflow-hidden border border-slate-100 dark:border-slate-700/30">
            <img 
              className="h-full w-full object-cover" 
              alt="User profile avatar" 
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAYUnbDLZfHrUnso6dKUSfiuEEt4TPviXifNi96Ubkj0DlVsfGXRL8dyLFmaw_Rfvu-XEG-EAhe4goibX_Hz8Qt_5VEz9my58cm5csLEAxEghN4QouloLN3P15n2gVxp2rDoZaL-PuAhXygmMnGaswVAjIXxpAT1JOEl6QPp_txrhdk2VEaZTcp1EIawgIiqfbi-jz2PTT7f9qtl5gHJLz7saj8GUzP7sDiNVGPycW1VtYmWyAlCV1IqMXp06NXkRpGrjvSfH9e1Tk"
            />
          </div>
          <div className="flex flex-col">
            <h2 className="text-sm font-medium text-slate-500 dark:text-slate-400 leading-tight">Welcome back</h2>
            <h1 className="text-lg font-bold leading-tight">Alex's Dashboard</h1>
          </div>
        </div>
        <button className="flex items-center justify-center w-10 h-10 rounded-full text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-surface-dark transition-colors">
          <span className="material-symbols-outlined">settings</span>
        </button>
      </header>

      {/* Main Content */}
      <main className="flex flex-col px-4 gap-6">
        {children}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/90 dark:bg-[#102217]/95 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800 pb-safe">
        <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
          <button className="flex flex-col items-center justify-center gap-1 w-16 h-full text-primary">
            <span className="material-symbols-outlined filled" style={{ fontVariationSettings: "'FILL' 1" }}>dashboard</span>
            <span className="text-[10px] font-medium">Home</span>
          </button>
          <button className="flex flex-col items-center justify-center gap-1 w-16 h-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <span className="material-symbols-outlined">calendar_month</span>
            <span className="text-[10px] font-medium">Calendar</span>
          </button>
          <button className="flex flex-col items-center justify-center gap-1 w-16 h-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <span className="material-symbols-outlined">pie_chart</span>
            <span className="text-[10px] font-medium">Insights</span>
          </button>
          <button className="flex flex-col items-center justify-center gap-1 w-16 h-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <span className="material-symbols-outlined">person</span>
            <span className="text-[10px] font-medium">Profile</span>
          </button>
        </div>
      </nav>
      {/* Safe Area Spacing for Bottom Nav */}
      <div className="h-safe w-full bg-white dark:bg-[#102217]"></div>
    </div>
  );
};

export default Layout;
