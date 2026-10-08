import { Link } from 'react-router-dom';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';
import StatusBadge from './StatusBadge';

const STYLE = {
  investigation: { box: 'border-bad/30 bg-[#FDECEE]', icon: 'bg-bad text-white', Icon: ShieldAlert, title: 'INVESTIGATION REQUIRED', text: 'text-bad' },
  change: { box: 'border-warn/40 bg-[#FFF6E5]', icon: 'bg-warn text-white', Icon: AlertTriangle, title: 'Change detected', text: 'text-[#9a6209]' },
  clear: { box: 'border-ok/30 bg-[#EAF6EE]', icon: 'bg-ok text-white', Icon: ShieldCheck, title: 'No material changes detected', text: 'text-ok' },
};

export default function StatusBanner({ state, changes = 0, priority, investigationTo, children }) {
  const s = STYLE[state];
  const sub = state === 'investigation' ? `${changes} significant changes detected`
    : state === 'change' ? `${changes} change${changes === 1 ? '' : 's'} detected — monitoring continues`
    : 'Recorded state matches the baseline';
  return (
    <div className={`flex flex-wrap items-center gap-4 rounded-2xl border p-5 ${s.box}`}>
      <span className={`grid h-14 w-14 shrink-0 place-items-center rounded-full ${s.icon}`}><s.Icon size={28} /></span>
      <div className="min-w-0 flex-1">
        <p className={`font-display text-xl font-bold sm:text-2xl ${s.text}`}>{s.title}</p>
        <p className="text-sm text-navy/70">{children || sub}</p>
      </div>
      <div className="flex items-center gap-3">
        {priority && <StatusBadge status={priority} label={`${priority} PRIORITY`} />}
        {investigationTo && state === 'investigation' && <Link to={investigationTo} className="btn-navy !py-2">Open investigation</Link>}
      </div>
    </div>
  );
}
