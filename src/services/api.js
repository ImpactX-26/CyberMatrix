import axios from 'axios';
import { getMode, setMode, bumpVersion } from './mode';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  timeout: 5000,
});

let probe = null;

export function checkBackend(force = false) {
  if (force || !probe) {
    setMode('checking');

    probe = http
      .get('/properties')
      .then(() => setMode('live', { forced: false }))
      .catch((error) => {
        setMode('error', { error });
        throw error;
      })
      .finally(() => {
        if (force) bumpVersion();
      });
  }

  return probe;
}

export const retryBackend = () => {
  setMode('checking', { forced: false });
  return checkBackend(true);
};

// Kept only so older UI imports do not crash.
// There is no demo mode anymore.
export const continueWithDemo = () => retryBackend();

export const getProperties = async () => {
  const { data } = await http.get('/properties');
  return data;
};

export const getProperty = async (id) => {
  const { data } = await http.get(`/properties/${id}`);
  return data;
};

export const getSnapshot = async (id) => {
  const { data } = await http.get(`/properties/${id}/snapshot`);
  return data;
};

export const getEvents = async (id) => {
  const { data } = await http.get(`/properties/${id}/events`);
  return data?.events || [];
};

export const getTimeline = async (id) => {
  const { data } = await http.get(`/properties/${id}/timeline`);
  return data?.timeline || [];
};

export const getEvidence = async (id) => {
  const { data } = await http.get(`/properties/${id}/evidence`);
  return data?.value || data?.evidence || [];
};

export const monitorProperty = async (id) => {
  return {
    id,
    monitoring: true,
  };
};

export const simulateEvent = async () => {
  throw new Error('Synthetic event simulation has been disabled.');
};
