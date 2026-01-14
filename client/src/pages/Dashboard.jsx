import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import SummaryCard from '../components/SummaryCard';
import FilterChips from '../components/FilterChips';
import SubscriptionItem from '../components/SubscriptionItem';
import { dataClient, isDemoMode } from '../services/dataClient';

const Dashboard = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'trial'
  const [activeCategory, setActiveCategory] = useState('All');
  
  // Modal State
  const [selectedSub, setSelectedSub] = useState(null);
  const [openModal, setOpenModal] = useState(false);

  // Add Subscription Modal State
  const [addOpen, setAddOpen] = useState(false);
  const [addForm, setAddForm] = useState({
    name: '',
    amount: '',
    billingCycle: 'monthly',
    status: 'active',
    category: 'Other',
  });

  const fetchSubscriptions = async () => {
    try {
      const subs = await dataClient.getSubscriptions();
      setSubscriptions(subs);
    } catch (err) {
      setError('Failed to fetch subscriptions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const handleScan = async () => {
    setScanning(true);
    try {
      await dataClient.scanSubscriptions();
      await fetchSubscriptions();
    } catch (err) {
      setError(isDemoMode ? 'Demo scan failed.' : 'Failed to scan emails. Make sure you have connected a Google account.');
    } finally {
      setScanning(false);
    }
  };

  const handleConnectGoogle = async () => {
    if (isDemoMode) {
      setError('Google connect is disabled in demo mode.');
      return;
    }
    try {
      const res = await dataClient.getGoogleAuthUrl();
      window.location.href = res.url;
    } catch (err) {
      setError('Failed to get Google Auth URL');
    }
  };

  const handleAddSubscription = async (e) => {
    e?.preventDefault?.();
    setError(null);

    try {
      const created = await dataClient.createSubscription({
        ...addForm,
        amount: addForm.amount === '' ? null : Number(addForm.amount),
      });
      setSubscriptions((prev) => [created, ...prev]);
      setAddForm({ name: '', amount: '', billingCycle: 'monthly', status: 'active', category: 'Other' });
      setAddOpen(false);
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'Failed to add subscription');
    }
  };

  const calculateMonthlyTotal = () => {
    return subscriptions
      .filter(s => s.status === 'active')
      .reduce((acc, curr) => {
        const amount = curr.amount || 0;
        return acc + (curr.billingCycle === 'yearly' ? amount / 12 : amount);
      }, 0);
  };

  const filteredSubscriptions = subscriptions.filter(sub => {
    const matchesTab = activeTab === 'active' ? sub.status === 'active' : sub.status === 'trial';
    const matchesCategory = activeCategory === 'All' || sub.category === activeCategory;
    return matchesTab && matchesCategory;
  });

  const upcomingThisWeek = subscriptions.filter(sub => {
    if (!sub.nextPaymentDate) return false;
    const nextPay = new Date(sub.nextPaymentDate);
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    return nextPay >= today && nextPay <= nextWeek;
  });

  const upcomingAmount = upcomingThisWeek.reduce((acc, curr) => acc + (curr.amount || 0), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background-dark">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <Layout>
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Summary Card */}
      <SummaryCard 
        totalSpend={calculateMonthlyTotal()} 
        upcomingPaymentsCount={upcomingThisWeek.length}
        upcomingPaymentsAmount={upcomingAmount}
      />

      {/* Navigation Tabs */}
      <section>
        <div className="flex h-12 w-full items-center rounded-xl bg-slate-200 dark:bg-surface-dark p-1">
          <button 
            onClick={() => setActiveTab('active')}
            className={`flex-1 flex h-full items-center justify-center rounded-lg text-sm font-bold transition-all ${
              activeTab === 'active' 
                ? 'bg-white dark:bg-background-dark shadow-sm text-slate-900 dark:text-white' 
                : 'text-slate-500 dark:text-slate-400 font-medium hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Active Subscriptions
          </button>
          <button 
            onClick={() => setActiveTab('trial')}
            className={`flex-1 flex h-full items-center justify-center rounded-lg text-sm font-bold transition-all ${
              activeTab === 'trial' 
                ? 'bg-white dark:bg-background-dark shadow-sm text-slate-900 dark:text-white' 
                : 'text-slate-500 dark:text-slate-400 font-medium hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Free Trials
          </button>
        </div>
      </section>

      {/* Filter Chips */}
      <FilterChips activeCategory={activeCategory} onCategoryChange={setActiveCategory} />

      {/* Subscriptions List */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            {activeTab === 'active' ? 'Your Subscriptions' : 'Current Trials'}
          </h3>
          <button className="flex items-center text-xs font-medium text-primary gap-1">
            Sort by
            <span className="material-symbols-outlined text-sm">sort</span>
          </button>
        </div>
        
        <div className="flex flex-col gap-3">
          {filteredSubscriptions.map((sub) => (
            <div key={sub.id} onClick={() => { setSelectedSub(sub); setOpenModal(true); }}>
              <SubscriptionItem subscription={sub} />
            </div>
          ))}
          
          {filteredSubscriptions.length === 0 && (
            <div className="text-center py-12 px-6 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
              <p className="text-slate-500 dark:text-slate-400 text-sm">
                No {activeTab} subscriptions found.
              </p>
              <button 
                onClick={handleScan}
                className="mt-4 text-primary font-bold text-sm hover:underline"
              >
                {isDemoMode ? 'Add sample subscriptions' : 'Scan your emails'}
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Floating Action Button */}
      <div className="fixed bottom-24 right-4 z-40 flex flex-col gap-3">
        <button
          onClick={() => setAddOpen(true)}
          className="h-12 w-12 rounded-full bg-white dark:bg-surface-dark text-slate-900 dark:text-white shadow-lg flex items-center justify-center transition-transform hover:scale-105 active:scale-95 border border-slate-200 dark:border-slate-700"
          title="Add Subscription"
        >
          <span className="material-symbols-outlined">add</span>
        </button>
        <button 
          onClick={handleConnectGoogle}
          className="h-12 w-12 rounded-full bg-white dark:bg-surface-dark text-slate-900 dark:text-white shadow-lg flex items-center justify-center transition-transform hover:scale-105 active:scale-95 border border-slate-200 dark:border-slate-700"
          title="Connect Google"
        >
          <span className="material-symbols-outlined">link</span>
        </button>
        <button 
          onClick={handleScan}
          disabled={scanning}
          className={`h-14 w-14 rounded-full bg-primary text-black shadow-lg shadow-primary/20 flex items-center justify-center transition-all hover:scale-105 active:scale-95 ${scanning ? 'animate-pulse' : ''}`}
          title="Scan Emails"
        >
          <span className="material-symbols-outlined text-3xl">{scanning ? 'sync' : 'refresh'}</span>
        </button>
      </div>

      {/* Add Subscription Modal */}
      {addOpen && (
        <div className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-surface-dark w-full max-w-lg rounded-t-3xl sm:rounded-2xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom duration-300">
            <form onSubmit={handleAddSubscription} className="p-6 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">Add subscription</h2>
                  <p className="text-sm text-slate-500">Create one manually (works great in demo mode).</p>
                </div>
                <button
                  type="button"
                  onClick={() => setAddOpen(false)}
                  className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">Name</label>
                  <input
                    value={addForm.name}
                    onChange={(e) => setAddForm((p) => ({ ...p, name: e.target.value }))}
                    required
                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Netflix"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">Amount</label>
                  <input
                    value={addForm.amount}
                    onChange={(e) => setAddForm((p) => ({ ...p, amount: e.target.value }))}
                    type="number"
                    step="0.01"
                    min="0"
                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-primary"
                    placeholder="9.99"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">Billing cycle</label>
                  <select
                    value={addForm.billingCycle}
                    onChange={(e) => setAddForm((p) => ({ ...p, billingCycle: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">Status</label>
                  <select
                    value={addForm.status}
                    onChange={(e) => setAddForm((p) => ({ ...p, status: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="active">Active</option>
                    <option value="trial">Trial</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">Category</label>
                  <input
                    value={addForm.category}
                    onChange={(e) => setAddForm((p) => ({ ...p, category: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Entertainment"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setAddOpen(false)}
                  className="flex-1 py-3 rounded-xl bg-slate-200 dark:bg-background-dark text-slate-900 dark:text-white font-bold text-sm transition-colors hover:bg-slate-300 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-3 rounded-xl bg-primary text-black font-extrabold text-sm transition-all hover:scale-[1.01] active:scale-[0.99]"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Simple Tailwind Modal */}
      {openModal && selectedSub && (
        <div className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-surface-dark w-full max-w-lg rounded-t-3xl sm:rounded-2xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom duration-300">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{selectedSub.name}</h2>
                  <p className="text-sm text-slate-500">{selectedSub.category}</p>
                </div>
                <button onClick={() => setOpenModal(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-background-dark/50">
                  <p className="text-xs text-slate-500 mb-1">Price</p>
                  <p className="text-lg font-bold text-slate-900 dark:text-white">${selectedSub.amount?.toFixed(2)}</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-background-dark/50">
                  <p className="text-xs text-slate-500 mb-1">Billing Cycle</p>
                  <p className="text-lg font-bold text-slate-900 dark:text-white capitalize">{selectedSub.billingCycle}</p>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2">Email Source</h3>
                <div className="p-4 rounded-xl bg-slate-900 text-slate-300 text-xs font-mono max-h-48 overflow-y-auto">
                   <p className="font-bold mb-2 text-primary">Subject: {selectedSub.emailSubject}</p>
                   <div className="whitespace-pre-wrap">{selectedSub.emailBody || selectedSub.emailSnippet}</div>
                </div>
              </div>

              <div className="flex gap-3">
                <button 
                  onClick={() => window.open(`https://www.google.com/search?q=how+to+cancel+${selectedSub.name}+subscription`, '_blank')}
                  className="flex-1 py-3 rounded-xl bg-slate-200 dark:bg-background-dark text-slate-900 dark:text-white font-bold text-sm transition-colors hover:bg-slate-300 dark:hover:bg-slate-800"
                >
                  How to Cancel
                </button>
                <button 
                   onClick={async () => {
                     if (window.confirm("Not a subscription?")) {
                        await dataClient.addToBlacklist({ term: selectedSub.emailSubject, type: 'subject' });
                        await dataClient.deleteSubscription(selectedSub.id);
                        setSubscriptions(prev => prev.filter(s => s.id !== selectedSub.id));
                        setOpenModal(false);
                     }
                   }}
                   className="px-4 py-3 rounded-xl bg-red-500/10 text-red-500 font-bold text-sm transition-colors hover:bg-red-500/20"
                >
                  <span className="material-symbols-outlined text-lg">block</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Dashboard;
