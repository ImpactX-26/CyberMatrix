import { MousePointerClick } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function EventCard({ event }) {
  if (!event) {
    return (
      <div className="card flex h-full min-h-[200px] flex-col items-center justify-center p-6 text-center text-sm text-navy/55">
        <MousePointerClick className="mb-2" /> Select an event to see its details.
      </div>
    );
  }
  const rows = [
    ['Event Type', event.type],
    ['Event Date', event.date],
    ['Previous State', event.previous],
    ['New State', event.next],
    ['Source Record', event.source],
    ['Relevant Field', event.field],
  ];
  return (
    <div className="card anim-reveal p-6" key={event.id}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-xl font-bold">{event.title}</h3>
        <StatusBadge status={event.status} />
      </div>
      <dl className="mt-4 divide-y divide-navy/10 text-sm">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between gap-4 py-2.5">
            <dt className="text-navy/55">{k}</dt>
            <dd className="text-right font-semibold">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
