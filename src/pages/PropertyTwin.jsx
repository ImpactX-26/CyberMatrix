import { useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft, MapPin, Activity, ArrowRight, ShieldAlert } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import StatusBanner from '../components/StatusBanner';
import StatusBadge from '../components/StatusBadge';
import Timeline from '../components/Timeline';
import EventCard from '../components/EventCard';
import EvidenceCard from '../components/EvidenceCard';
import EvidenceFilters from '../components/EvidenceFilters';
import DocumentModal from '../components/DocumentModal';
import MapView from '../components/MapView';
import PropertyGraph from '../components/PropertyGraph';
import AgentTrace from '../components/AgentTrace';
import SimulatePanel from '../components/SimulatePanel';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { useView } from '../hooks/useView';
import { MAIN_ID } from '../data/demoData';

const TABS = ['Overview', 'Timeline', 'Map', 'Evidence', 'Graph', 'Investigation'];

function Overview({ view }) {
  const p = view.property;
  const rows = [
    ['Property ID', p.id], ['Survey Number', p.survey], ['Hissa', p.hissa], ['Owner', view.owner], ['Extent', p.extent],
    ['Mortgage', view.mortgage], ['Last Updated', view.lastUpdated], ['Monitoring', 'Active'],
  ];
  const byYear = {};
  view.events.forEach((e) => { const y = e.date.slice(-4); byYear[y] = (byYear[y] || 0) + 1; });
  const chart = Object.entries(byYear).map(([year, events]) => ({ year, events }));
  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="card p-6 lg:col-span-3">
        <h2 className="text-xl font-bold">Property Details</h2>
        <dl className="mt-4 grid gap-x-8 sm:grid-cols-2">
          {rows.map(([k, v]) => (
            <div key={k} className="flex justify-between gap-3 border-b border-navy/10 py-2.5 text-sm">
              <dt className="text-navy/55">{k}</dt>
              <dd className="text-right font-semibold">{k === 'Monitoring' ? <span className="inline-flex items-center gap-1.5 text-ok"><Activity size={14} /> {v}</span> : v}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-4 text-xs text-navy/45">Baseline at monitoring start: 5 Acres · survey {p.survey} · ownership as recorded after the 2022 sale.</p>
      </div>
      <div className="card p-6 lg:col-span-2">
        <h2 className="text-xl font-bold">Property Events Over Time</h2>
        <p className="text-sm text-navy/55">{view.events.length} recorded event{view.events.length === 1 ? '' : 's'}</p>
        <div className="mt-3 h-44">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart} margin={{ left: -24, right: 8, top: 8 }}>
              <CartesianGrid vertical={false} stroke="#08263D14" />
              <XAxis dataKey="year" tick={{ fontSize: 12 }} /><YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip /><Bar dataKey="events" fill="#08263D" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function InvestigationTab({ view }) {
  if (view.state !== 'investigation') {
    return <div className="card p-8 text-center text-navy/65"><ShieldAlert className="mx-auto mb-2 text-navy/30" /> No investigation has been triggered. Use “Simulate Property Change” above to add the next event.</div>;
  }
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h2 className="text-xl font-bold">Key finding</h2>
        <p className="mt-1 text-lg">{view.finding}</p>
        <ul className="mt-4 space-y-2 text-sm">{view.why.map((w) => <li key={w} className="flex items-center gap-2"><span className="text-warn">⚠</span> {w}</li>)}</ul>
        <p className="mt-4 text-sm font-semibold">Status: Needs human verification</p>
        <Link to={`/investigation/${view.property.id}`} className="btn-navy mt-4">Open full investigation <ArrowRight size={16} /></Link>
      </div>
      <div><h2 className="mb-3 text-xl font-bold">AI Investigation Trace</h2><AgentTrace /></div>
    </div>
  );
}

export default function PropertyTwin() {
  const { id } = useParams();
  const [sp, setSp] = useSearchParams();
  const tab = (sp.get('tab') || 'overview').toLowerCase();
  const { view, loading, notFound, stage } = useView(id);
  const [selId, setSelId] = useState(null);
  const [filter, setFilter] = useState('All');
  const [doc, setDoc] = useState(null);

  if (notFound) return <div className="px-4 py-16"><ErrorState title="Property not found" message={`No synthetic property with ID ${id}.`} backHome /></div>;
  if (loading || !view) return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6"><LoadingState /></div>;

  const p = view.property;
  const selected = view.events.find((e) => e.id === selId) || view.events[view.events.length - 1];
  const evidence = filter === 'All' ? view.evidence : view.evidence.filter((e) => e.sourceType === filter);

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
      <div>
        <Link to="/portfolio" className="inline-flex items-center gap-1.5 text-sm text-navy/60 hover:text-navy"><ArrowLeft size={15} /> Back to portfolio</Link>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-4xl font-bold">{p.id}</h1>
            <p className="text-lg text-navy/70">Survey No. {p.survey}</p>
            <p className="mt-1 flex items-center gap-1.5 text-sm text-navy/55"><MapPin size={14} /> {p.village} Village · {p.hobli} Hobli · {p.taluk} Taluk · {p.district} District</p>
          </div>
          <StatusBadge status="clear" label="Synthetic Demo Data" dot={false} />
        </div>
      </div>

      <StatusBanner state={view.state} changes={view.changes} priority={view.state === 'investigation' ? 'HIGH' : undefined} investigationTo={`/investigation/${p.id}`} />
      {p.id === MAIN_ID && <SimulatePanel propertyId={p.id} stage={stage} />}

      <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
        <div className="inline-flex min-w-full gap-1 rounded-2xl border border-navy/10 bg-white p-1.5 sm:min-w-0" role="tablist">
          {TABS.map((t) => (
            <button key={t} role="tab" aria-selected={tab === t.toLowerCase()} onClick={() => setSp(t === 'Overview' ? {} : { tab: t.toLowerCase() })}
              className={`whitespace-nowrap rounded-xl px-4 py-2 text-sm font-semibold transition ${tab === t.toLowerCase() ? 'bg-navy text-white shadow' : 'text-navy/65 hover:bg-navy/5'}`}>{t}</button>
          ))}
        </div>
      </div>

      {tab === 'overview' && <Overview view={view} />}
      {tab === 'timeline' && (
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-3"><h2 className="mb-3 text-xl font-bold">Property Timeline</h2><Timeline events={view.events} selectedId={selected?.id} onSelect={(e) => setSelId(e.id)} newestStage={stage} /></div>
          <div className="lg:col-span-2 lg:sticky lg:top-24 lg:self-start"><EventCard event={selected} /></div>
        </div>
      )}
      {tab === 'map' && <MapView height={520} tone={view.state === 'investigation' ? 'bad' : 'info'} selectedSurvey={p.survey} />}
      {tab === 'evidence' && (
        <div className="space-y-5">
          <EvidenceFilters value={filter} onChange={setFilter} items={view.evidence} />
          {evidence.length ? <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{evidence.map((e) => <EvidenceCard key={e.id} item={e} onOpen={setDoc} />)}</div>
            : <p className="card p-8 text-center text-navy/60">No {filter.toLowerCase()} evidence recorded yet.</p>}
        </div>
      )}
      {tab === 'graph' && <PropertyGraph view={view} />}
      {tab === 'investigation' && <InvestigationTab view={view} />}
      <DocumentModal doc={doc} onClose={() => setDoc(null)} />
    </div>
  );
}
