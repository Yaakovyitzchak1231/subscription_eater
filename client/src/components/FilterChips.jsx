import React from 'react';

const categories = ['All', 'Entertainment', 'Utility', 'Productivity', 'Health'];

const FilterChips = ({ activeCategory, onCategoryChange }) => {
  return (
    <section className="w-full overflow-x-auto no-scrollbar pb-2">
      <div className="flex gap-3 min-w-max">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => onCategoryChange(category)}
            className={`flex h-9 items-center justify-center px-4 rounded-full text-sm font-bold transition-colors ${
              (activeCategory === category || (category === 'All' && !activeCategory))
                ? 'bg-primary text-black shadow-[0_0_10px_rgba(43,238,121,0.2)]'
                : 'bg-white dark:bg-surface-dark border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-medium hover:bg-slate-50 dark:hover:bg-[#1f3b2e]'
            }`}
          >
            {category}
          </button>
        ))}
      </div>
    </section>
  );
};

export default FilterChips;
