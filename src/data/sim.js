import { useSyncExternalStore } from 'react';
import { MAIN_ID, findProperty } from './demoData';

// Simulation stage for PROP-0491: 0 baseline · 1 mortgage · 2 registration · 3 mutation → investigation
const KEY = 'landshield.stage';
let stage = 3;
try { const s = sessionStorage.getItem(KEY); if (s !== null) stage = Number(s); } catch (e) { /* ignore */ }
const listeners = new Set();

export const getStage = () => stage;
export function setStage(n) {
  stage = Math.max(0, Math.min(3, n));
  try { sessionStorage.setItem(KEY, String(stage)); } catch (e) { /* ignore */ }
  listeners.forEach((l) => l());
}
const subscribe = (l) => { listeners.add(l); return () => listeners.delete(l); };
export const useStage = () => useSyncExternalStore(subscribe, getStage);

export const stageFor = (propOrId) => {
  const p = typeof propOrId === 'string' ? findProperty(propOrId) : propOrId;
  if (!p) return 0;
  return p.id === MAIN_ID ? stage : p.stage;
};
