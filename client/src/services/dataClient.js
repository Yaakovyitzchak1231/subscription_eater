import api from './api';

export const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

const DEMO_SUBSCRIPTIONS_KEY = 'demo.subscriptions.v1';
const DEMO_BLACKLIST_KEY = 'demo.blacklist.v1';

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function addDays(date, days) {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function addMonths(date, months) {
  const copy = new Date(date);
  copy.setMonth(copy.getMonth() + months);
  return copy;
}

function toIsoDate(date) {
  return date.toISOString();
}

function normalizeNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function computeNextPaymentDate({ billingCycle }) {
  const now = new Date();
  if (billingCycle === 'yearly') return addMonths(now, 12);
  if (billingCycle === 'weekly') return addDays(now, 7);
  return addMonths(now, 1);
}

function seedDemoSubscriptionsIfEmpty() {
  const existing = readJson(DEMO_SUBSCRIPTIONS_KEY, []);
  if (existing.length > 0) return;

  const now = new Date();
  const seeded = [
    {
      id: crypto.randomUUID(),
      name: 'Netflix',
      provider: 'Netflix',
      amount: 15.49,
      currency: 'USD',
      billingCycle: 'monthly',
      status: 'active',
      category: 'Entertainment',
      nextPaymentDate: toIsoDate(addDays(now, 9)),
      trialExpirationDate: null,
      emailSubject: null,
      emailSnippet: null,
      emailBody: null,
    },
    {
      id: crypto.randomUUID(),
      name: 'Notion',
      provider: 'Notion',
      amount: 10,
      currency: 'USD',
      billingCycle: 'monthly',
      status: 'trial',
      category: 'Productivity',
      nextPaymentDate: null,
      trialExpirationDate: toIsoDate(addDays(now, 6)),
      emailSubject: null,
      emailSnippet: null,
      emailBody: null,
    },
  ];

  writeJson(DEMO_SUBSCRIPTIONS_KEY, seeded);
}

async function demoGetSubscriptions() {
  seedDemoSubscriptionsIfEmpty();
  return readJson(DEMO_SUBSCRIPTIONS_KEY, []);
}

async function demoCreateSubscription(payload) {
  const subscriptions = await demoGetSubscriptions();
  const now = new Date();

  const status = payload.status === 'trial' ? 'trial' : 'active';
  const billingCycle = payload.billingCycle || 'monthly';

  const nextPaymentDate =
    payload.nextPaymentDate ||
    (status === 'active' ? toIsoDate(computeNextPaymentDate({ billingCycle })) : null);
  const trialExpirationDate =
    payload.trialExpirationDate || (status === 'trial' ? toIsoDate(addDays(now, 14)) : null);

  const created = {
    id: crypto.randomUUID(),
    name: payload.name?.trim() || 'Untitled',
    provider: payload.provider?.trim() || payload.name?.trim() || 'Unknown',
    amount: normalizeNumber(payload.amount),
    currency: payload.currency || 'USD',
    billingCycle,
    status,
    category: payload.category || 'Other',
    nextPaymentDate,
    trialExpirationDate,
    emailSubject: null,
    emailSnippet: null,
    emailBody: null,
  };

  const next = [created, ...subscriptions];
  writeJson(DEMO_SUBSCRIPTIONS_KEY, next);
  return created;
}

async function demoUpdateSubscription(id, patch) {
  const subscriptions = await demoGetSubscriptions();
  const next = subscriptions.map((s) => (s.id === id ? { ...s, ...patch } : s));
  writeJson(DEMO_SUBSCRIPTIONS_KEY, next);
  return next.find((s) => s.id === id) || null;
}

async function demoDeleteSubscription(id) {
  const subscriptions = await demoGetSubscriptions();
  const next = subscriptions.filter((s) => s.id !== id);
  writeJson(DEMO_SUBSCRIPTIONS_KEY, next);
  return { success: true };
}

async function demoBlacklist(term, type) {
  const current = readJson(DEMO_BLACKLIST_KEY, []);
  const entry = { id: crypto.randomUUID(), term, type, createdAt: new Date().toISOString() };
  writeJson(DEMO_BLACKLIST_KEY, [entry, ...current]);
  return { success: true };
}

async function demoScan() {
  const randomNames = [
    { name: 'Spotify', amount: 11.99, category: 'Entertainment' },
    { name: 'Dropbox', amount: 9.99, category: 'Productivity' },
    { name: 'YouTube Premium', amount: 13.99, category: 'Entertainment' },
    { name: 'iCloud+', amount: 2.99, category: 'Utility' },
  ];

  const pick = randomNames[Math.floor(Math.random() * randomNames.length)];
  await demoCreateSubscription({
    name: pick.name,
    provider: pick.name,
    amount: pick.amount,
    currency: 'USD',
    billingCycle: 'monthly',
    status: 'active',
    category: pick.category,
  });

  return { message: 'Demo scan complete. Added 1 sample subscription.' };
}

export const dataClient = {
  async login(email, password) {
    if (isDemoMode) {
      const user = { id: 'demo', email: email || 'demo@local' };
      const token = 'demo-token';
      return { token, user };
    }
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },

  async register(email, password) {
    if (isDemoMode) {
      const user = { id: 'demo', email: email || 'demo@local' };
      const token = 'demo-token';
      return { token, user };
    }
    const res = await api.post('/auth/register', { email, password });
    return res.data;
  },

  async getSubscriptions() {
    if (isDemoMode) return demoGetSubscriptions();
    const res = await api.get('/subscriptions');
    return res.data;
  },

  async createSubscription(payload) {
    if (isDemoMode) return demoCreateSubscription(payload);
    const res = await api.post('/subscriptions', payload);
    return res.data;
  },

  async updateSubscription(id, patch) {
    if (isDemoMode) return demoUpdateSubscription(id, patch);
    const res = await api.put(`/subscriptions/${id}`, patch);
    return res.data;
  },

  async deleteSubscription(id) {
    if (isDemoMode) return demoDeleteSubscription(id);
    const res = await api.delete(`/subscriptions/${id}`);
    return res.data;
  },

  async addToBlacklist(payload) {
    if (isDemoMode) return demoBlacklist(payload.term, payload.type);
    const res = await api.post('/blacklist', payload);
    return res.data;
  },

  async scanSubscriptions() {
    if (isDemoMode) return demoScan();
    const res = await api.post('/subscriptions/scan');
    return res.data;
  },

  async getGoogleAuthUrl() {
    if (isDemoMode) {
      return { url: null };
    }
    const res = await api.get('/auth/google');
    return res.data;
  },
};

