import { FileText, Eye } from 'lucide-react';

const TONE = { Registration: 'bg-ai/10 text-ai', Mutation: 'bg-warn/15 text-[#9a6209]', Mortgage: 'bg-info/10 text-info', RTC: 'bg-ok/10 text-ok' };

export default function EvidenceCard({ item, onOpen }) {
  const rows = [['Source ID', item.sourceId], ['Field', item.field], ['Value', item.value], ['Date', item.date], ['Related Event', item.related]];
  return (
    <article className="card anim-reveal flex flex-col p-5">
      <div className="flex items-center justify-between">
        <span className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-bold ${TONE[item.sourceType] || 'bg-navy/10'}`}><FileText size={14} /> {item.sourceType}</span>
        <span className="text-xs text-navy/45">Synthetic</span>
      </div>
      <dl className="mt-4 flex-1 space-y-2 text-sm">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between gap-3"><dt className="text-navy/55">{k}</dt><dd className="text-right font-semibold">{v}</dd></div>
        ))}
      </dl>
      <button className="btn-ghost mt-5 w-full !py-2" onClick={() => onOpen(item)}><Eye size={16} /> View Document</button>
    </article>
  );
}
