import { useSyncExternalStore } from 'react';

// Tiny store: is the backend live, or are we serving synthetic demo data?
let state = { mode: 'checking', forced: false, version: 0 };
const listeners = new Set();
const emit = () => listeners.forEach((l) => l());

export const getMode = () => state;
export const subscribe = (l) => { listeners.add(l); return () => listeners.delete(l); };
export function setMode(mode, extra = {}) {
  state = { ...state, mode, ...extra };
  emit();
}
export const bumpVersion = () => { state = { ...state, version: state.version + 1 }; emit(); };
export const useMode = () => useSyncExternalStore(subscribe, getMode);
