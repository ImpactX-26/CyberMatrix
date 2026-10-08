import axios from 'axios';
import { PROPERTIES, findProperty, buildView } from '../data/demoData';
import { stageFor } from '../data/sim';
import { getMode, setMode, bumpVersion } from './mode';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 2500,
});

// One health probe decides live vs demo. Retry re-runs it.
let probe = null;
export function checkBackend(force = false) {
  if (force || !probe) {
    setMode('checking');
    probe = http
      .get('/properties', { timeout: 1500 })
      .then(() => setMode('live', { forced: false }))
      .catch(() => setMode('demo'))
      .finally(() => { if (force) bumpVersion(); });
  }
  return probe;
}
export const retryBackend = () => { setMode('checking', { forced: false }); return checkBackend(true); };
export const continueWithDemo = () => setMode('demo', { forced: true });

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

// Try FastAPI → fall back to synthetic data.
async function call(request, fallback) {
  await checkBackend();
  if (getMode().mode === 'live') {
    try {
      const { data } = await request();
      if (data !== undefined && data !== null) return data;
    } catch (e) {
      setMode('demo');
    }
  }
  await wait(350); // lets skeletons breathe; keeps demo feeling like a real fetch
  return fallback();
}

const view = (id) => { const p = findProperty(id); return p ? buildView(p, stageFor(p)) : null; };

export const getProperties = () => call(() => http.get('/properties'), () => PROPERTIES);
export const getProperty = (id) => call(() => http.get(`/properties/${id}`), () => findProperty(id));
export const getSnapshot = (id) => call(() => http.get(`/properties/${id}/snapshot`), () => { const v = view(id); return v && { owner: v.owner, extent: v.property.extent, mortgage: v.mortgage, survey: v.property.survey }; });
export const getEvents = (id) => call(() => http.get(`/properties/${id}/events`), () => view(id)?.events || []);
export const getTimeline = (id) => call(() => http.get(`/properties/${id}/timeline`), () => view(id)?.events || []);
export const getEvidence = (id) => call(() => http.get(`/properties/${id}/evidence`), () => view(id)?.evidence || []);
export const monitorProperty = (id) => call(() => http.post(`/properties/${id}/monitor`), () => ({ id, monitoring: true }));
export const simulateEvent = (id, event) => call(() => http.post(`/properties/${id}/simulate-event`, { event }), () => ({ id, event, simulated: true }));
export const getInvestigation = (id) => call(() => http.get(`/investigations/${id}`), () => { const v = view(id); return v && { state: v.state, finding: v.finding, why: v.why, next: v.next }; });
