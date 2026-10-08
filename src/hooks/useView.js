import { useMemo } from 'react';
import { useAsync } from './useAsync';
import { useMode } from '../services/mode';
import { useStage, stageFor } from '../data/sim';
import { findProperty, buildView } from '../data/demoData';
import { getProperty, getTimeline, getEvidence, getInvestigation } from '../services/api';

const ok = (arr, key) => Array.isArray(arr) && arr.length > 0 && arr.every((x) => x && x[key]);

// Builds everything a property screen needs. Synthetic by default; live backend data
// overlays it when the shape matches what the UI expects.
export function useView(id) {
  const { mode, version } = useMode();
  const sim = useStage();
  const base = findProperty(id);
  const remote = useAsync(async () => {
    if (!base) return null;
    const [p, t, e, i] = await Promise.all([getProperty(id), getTimeline(id), getEvidence(id), getInvestigation(id)]);
    return { p, t, e, i };
  }, [id, version]);

  const view = useMemo(() => {
    if (!base) return null;
    const v = buildView(base, stageFor(base));
    if (mode === 'live' && remote.data) {
      const { p, t, e, i } = remote.data;
      if (p && p.owner) v.owner = p.owner;
      if (ok(t, 'date') && ok(t, 'title')) v.events = t.map((x) => ({ status: 'normal', summary: '', ...x }));
      if (ok(e, 'sourceId')) v.evidence = e;
      if (i && i.finding) v.finding = i.finding;
      if (i && Array.isArray(i.why)) v.why = i.why;
      if (i && i.next) v.next = i.next;
    }
    return v;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [base, sim, mode, remote.data]);

  return { view, loading: remote.loading && !remote.data, notFound: !base, stage: stageFor(base), live: mode === 'live' };
}
