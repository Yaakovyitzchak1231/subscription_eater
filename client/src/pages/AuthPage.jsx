import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AuthPage = ({ isLogin = true }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-background-light dark:bg-background-dark">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary mb-4 shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-3xl text-black">payments</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            {isLogin ? 'Welcome back' : 'Create account'}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            {isLogin ? 'Manage your subscriptions effortlessly' : 'Start tracking your spending today'}
          </p>
        </div>

        <div className="bg-white dark:bg-surface-dark p-8 rounded-3xl shadow-xl border border-slate-100 dark:border-slate-700/30">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 px-1">
                Email Address
              </label>
              <input
                type="email"
                required
                className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 px-1">
                Password
              </label>
              <input
                type="password"
                required
                className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/50 text-red-500 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full py-4 bg-primary hover:bg-primary/90 text-black font-extrabold rounded-xl shadow-lg shadow-primary/20 transition-all transform active:scale-[0.98] mt-2"
            >
              {isLogin ? 'Sign In' : 'Get Started'}
            </button>
          </form>

          <div className="mt-8 text-center">
            <button
              onClick={() => navigate(isLogin ? '/register' : '/login')}
              className="text-sm font-bold text-slate-500 hover:text-primary transition-colors"
            >
              {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
            </button>
          </div>
        </div>
        
        <p className="mt-8 text-center text-xs text-slate-500 dark:text-slate-500 uppercase tracking-widest font-bold">
          Stitch Subscription Tracker
        </p>
      </div>
    </div>
  );
};

export default AuthPage;