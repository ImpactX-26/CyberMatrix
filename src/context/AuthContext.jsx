import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as auth from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => auth.getSession());

  // Keep tabs in sync (log out in one tab -> logged out in others).
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === null || e.key === auth.SESSION_STORAGE_KEY) setUser(auth.getSession());
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const signIn = useCallback(async (creds) => {
    const res = await auth.signIn(creds);
    if (res.ok) setUser(res.session);
    return res;
  }, []);

  const logout = useCallback(() => {
    auth.signOut();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: !!user, signIn, signUp: auth.signUp, resetPassword: auth.resetPassword, logout }),
    [user, signIn, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
