import { useMemo, useState } from 'react';
import { Building2, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import PropertyCard from '../components/PropertyCard';
import LoadingState from '../components/LoadingState';
import { useAsync } from '../hooks/useAsync';
import { useMode } from '../services/mode';
import { useStage, stageFor } from '../data/sim';
import { getProperties } from '../services/api';
import { PROPERTIES, findProperty, buildView, PORTFOLIO_SERIES } from '../data/demoData';

const ORDER = { investigation: 0, change: 1, clear: 2 };
const FILTERS = [['all', 'All'], ['investigation', 'Investigation Required'], ['change', 'Changes Detected'], ['clear', 'Normal']];

export default function Portfolio() {
  const { version } = useMode();
  const sim = useStage();
  const [filter, setFilter] = useState('all');
  const { data, loading } = useAsync(getProperties, [version]);

  const views = useMemo(() => {
    const fromApi = Array.isArray(data) ? data.map((d) => findProperty(d?.id)).filter(Boolean) : [];
    const list = fromApi.length ? fromApi : PROPERTIES;
    return list.map((p) => buildView(p, stageFor(p))).sort((a, b) => ORDER[a.state] - ORDER[b.state]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, sim]);

  if (loading && !data) return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6"><LoadingState variant="cards" /></div>;

  const count = (s) => views.filter((v) => v.state === s).length;
  const stats = [
    { n: views.length, label: 'Properties Monitored', Icon: Building2, c: 'text-navy bg-navy/10' },
    { n: count('clear'), label: 'Normal', Icon: CheckCircle2, c: 'text-ok bg-ok/10' },
    { n: count('change'), label: 'Changes Detected', Icon: AlertTriangle, c: 'text-warn bg-warn/15' },
    { n: count('investigation'), label: 'Investigation Required', Icon: ShieldAlert, c: 'text-bad bg-bad/10' },
  ];
  const shown = filter === 'all' ? views : views.filter((v) => v.state === filter);

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6">
      <div>
        <h1 className="text-4xl font-bold">Property Portfolio</h1>
        <p className="mt-1 text-navy/60">Synthetic Demo Data · every property watched for meaningful record changes</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ n, label, Icon, c }) => (
          <div key={label} className="card flex items-center gap-4 p-5">
            <span className={`grid h-12 w-12 place-items-center rounded-xl ${c}`}><Icon size={22} /></span>
            <div><p className="font-display text-3xl font-bold leading-none">{n}</p><p className="mt-1 text-sm text-navy/60">{label}</p></div>
          </div>
        ))}
      </div>

      <div className="card p-5">
        <h2 className="text-lg font-bold">Property Events Over Time</h2>
        <div className="mt-2 h-36">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={PORTFOLIO_SERIES} margin={{ left: -24, right: 8 }}>
              <CartesianGrid vertical={false} stroke="#08263D14" /><XAxis dataKey="month" tick={{ fontSize: 12 }} /><YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip /><Bar dataKey="events" fill="#3478D4" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filter properties">
        {FILTERS.map(([k, l]) => (
          <button key={k} role="tab" aria-selected={filter === k} onClick={() => setFilter(k)}
            className={`rounded-full border px-4 py-1.5 text-sm font-semibold ${filter === k ? 'border-navy bg-navy text-white' : 'border-navy/15 bg-white hover:bg-navy/5'}`}>{l}</button>
        ))}
      </div>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{shown.map((v) => <PropertyCard key={v.property.id} view={v} />)}</div>
    </div>
  );
}
