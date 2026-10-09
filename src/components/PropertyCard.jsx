import { Link } from 'react-router-dom';
import { MapPin } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function PropertyCard({ view }) {
  const { property: p, meta, state } = view;
  const bar = { bad: 'bg-bad', warn: 'bg-warn', ok: 'bg-ok' }[meta.tone];
  const note = state === 'clear' ? 'No Material Changes' : view.stage === 1 ? 'New mortgage registered' : view.stage === 2 ? 'Registration added after recent mortgage' : 'Registration and mutation mismatch';
  return (
    <article className="card flex flex-col overflow-hidden">
      <div className={`h-1.5 ${bar}`} />
      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-xl font-bold">{p.id}</h3>
            <p className="text-sm text-navy/65">Survey {p.survey}</p>
          </div>
          <StatusBadge status={meta.priority} label={meta.priority} />
        </div>
        <p className="mt-4 text-sm font-semibold">{meta.short}</p>
        <p className="text-sm text-navy/65">{note}</p>
        <p className="mt-3 inline-flex items-center gap-1.5 text-xs text-navy/50"><MapPin size={13} /> {p.village}, {p.taluk} · Updated {view.lastUpdated}</p>
        <Link to={`/property/${p.id}`} className="btn-ghost mt-5 w-full">View Details</Link>
      </div>
    </article>
  );
}
