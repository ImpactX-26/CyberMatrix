const TONES = {
  normal: ['bg-ok/10 text-ok border-ok/25', 'Normal'],
  change: ['bg-warn/[0.12] text-[#9a6209] border-warn/35', 'Change'],
  suspicious: ['bg-bad/10 text-bad border-bad/25', 'Suspicious'],
  investigation: ['bg-bad/10 text-bad border-bad/25', 'Investigation Required'],
  clear: ['bg-ok/10 text-ok border-ok/25', 'No Material Changes'],
  HIGH: ['bg-bad/10 text-bad border-bad/25', 'HIGH'],
  MEDIUM: ['bg-warn/[0.12] text-[#9a6209] border-warn/35', 'MEDIUM'],
  LOW: ['bg-ok/10 text-ok border-ok/25', 'LOW'],
};
export const DOT = { normal: 'bg-ok', change: 'bg-warn', suspicious: 'bg-bad', investigation: 'bg-bad', clear: 'bg-ok', HIGH: 'bg-bad', MEDIUM: 'bg-warn', LOW: 'bg-ok' };

export default function StatusBadge({ status, label, dot = true }) {
  const [cls, def] = TONES[status] || TONES.normal;
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${DOT[status]}`} />}
      {label || def}
    </span>
  );
}
