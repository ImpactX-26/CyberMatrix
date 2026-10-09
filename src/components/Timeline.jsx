import { Landmark, FileSignature, Stamp, Search, Home } from 'lucide-react';
import StatusBadge, { DOT } from './StatusBadge';

const ICON = { SALE_REGISTERED: FileSignature, MORTGAGE_REGISTERED: Landmark, MUTATION_UPDATED: Stamp, INVESTIGATION_TRIGGERED: Search };

export default function Timeline({ events, selectedId, onSelect, newestStage }) {
  return (
    <ol className="relative space-y-4 pl-1">
      <span className="absolute bottom-4 left-[22px] top-4 w-px bg-navy/15" aria-hidden="true" />
      {events.map((e) => {
        const Icon = ICON[e.type] || Home;
        const active = e.id === selectedId;
        const fresh = newestStage !== undefined && e.stage === newestStage && e.stage > 0;
        return (
          <li key={e.id} className={fresh ? 'anim-reveal' : ''}>
            <button onClick={() => onSelect(e)} aria-pressed={active}
              className={`relative flex w-full items-start gap-4 rounded-2xl border p-4 text-left transition ${active ? 'border-navy bg-white shadow-card' : 'border-transparent hover:bg-white/70'}`}>
              <span className={`z-10 grid h-9 w-9 shrink-0 place-items-center rounded-full text-white ${DOT[e.status]}`}><Icon size={17} /></span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-medium text-navy/55">{e.date}</span>
                <span className="mt-0.5 block font-display text-lg font-semibold">{e.title}</span>
                <span className="block text-sm text-navy/70">{e.summary}</span>
              </span>
              <StatusBadge status={e.status} />
            </button>
          </li>
        );
      })}
    </ol>
  );
}
