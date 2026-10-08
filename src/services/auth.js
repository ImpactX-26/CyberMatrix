// Demo-only frontend authentication backed by localStorage.
// NOT real security: there is no server, and anything in localStorage is readable by the user.
// Passwords are hashed (SHA-256 when available) so they are not stored as plain text.

const USERS_KEY = 'landshield_users';
const SESSION_KEY = 'landshield_auth';

const read = (key, fallback) => {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
};
const write = (key, value) => localStorage.setItem(key, JSON.stringify(value));

async function hash(text) {
  try {
    if (globalThis.crypto?.subtle) {
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`landshield:${text}`));
      return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
    }
  } catch { /* fall through */ }
  return `plain:${btoa(unescape(encodeURIComponent(text)))}`;
}

export const normalizeEmail = (e) => String(e || '').trim().toLowerCase();

export const isValidEmail = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(e || '').trim());

// Accepts 10-digit numbers (optionally +91 / 0 prefix) and general international numbers (10-15 digits).
export function isValidPhone(p) {
  const s = String(p || '').trim().replace(/[\s\-().]/g, '');
  if (!/^\+?\d+$/.test(s)) return false;
  const digits = s.replace('+', '');
  if (s.startsWith('+91')) return /^[6-9]\d{9}$/.test(digits.slice(2));
  if (!s.startsWith('+') && digits.length === 10) return /^[6-9]\d{9}$/.test(digits);
  return digits.length >= 10 && digits.length <= 15;
}

export function getSession() {
  const s = read(SESSION_KEY, null);
  return s && s.email ? s : null;
}

export async function signUp({ name, phone, email, password }) {
  const users = read(USERS_KEY, []);
  const key = normalizeEmail(email);
  if (users.some((u) => u.email === key)) {
    return { ok: false, error: 'An account with this email already exists. Please sign in.' };
  }
  users.push({
    name: name.trim(),
    phone: phone.trim(),
    email: key,
    passwordHash: await hash(password),
    createdAt: new Date().toISOString(),
  });
  write(USERS_KEY, users);
  return { ok: true };
}

export async function signIn({ email, password }) {
  const users = read(USERS_KEY, []);
  const user = users.find((u) => u.email === normalizeEmail(email));
  if (!user || user.passwordHash !== (await hash(password))) {
    return { ok: false, error: 'Incorrect email or password. Please check your details and try again.' };
  }
  const session = { name: user.name, email: user.email, phone: user.phone, signedInAt: new Date().toISOString() };
  write(SESSION_KEY, session);
  return { ok: true, session };
}

export async function resetPassword({ email, password }) {
  const users = read(USERS_KEY, []);
  const user = users.find((u) => u.email === normalizeEmail(email));
  if (!user) return { ok: false, error: 'No account found for this email.' };
  user.passwordHash = await hash(password);
  write(USERS_KEY, users);
  return { ok: true };
}

export function signOut() {
  localStorage.removeItem(SESSION_KEY);
}

export const SESSION_STORAGE_KEY = SESSION_KEY;
