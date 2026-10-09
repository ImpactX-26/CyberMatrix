import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { TRACE } from '../data/demoData';

const AGENTS = [
  { name: 'Orchestrator Agent', role: 'Runs the investigation workflow', cls: 'bg-ai/10 text-ai border-ai/25' },
  { name: 'Change Investigation Agent', role: 'Compares records and finds inconsistencies', cls: 'bg-info/10 text-info border-info/25' },
  { name: 'Evidence Agent', role: 'Attaches the source records', cls: 'bg-ok/10 text-ok border-ok/25' },
];
const chip = (name) => AGENTS.find((a) => a.name === name)?.cls;

export default function AgentTrace() {
  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-3">
        {AGENTS.map((a) => (
          <div key={a.name} className={`rounded-xl border p-3 ${a.cls}`}>
            <p className="text-sm font-bold">{a.name}</p>
            <p className="text-xs opacity-80">{a.role}</p>
          </div>
        ))}
      </div>
      <ol className="mt-5 space-y-2">
        {TRACE.map((t, i) => (
          <li key={t.step} className="anim-reveal card flex flex-wrap items-start gap-x-4 gap-y-1 p-4 sm:flex-nowrap" style={{ animationDelay: `${i * 90}ms` }}>
            <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-bold text-white ${t.status === 'warn' ? 'bg-warn' : 'bg-ok'}`}>{t.step}</span>
            <div className="min-w-0 flex-1">
              <p className="flex items-center gap-1.5 font-semibold">
                {t.status === 'warn' ? <AlertTriangle size={16} className="text-warn" /> : <CheckCircle2 size={16} className="text-ok" />}
                {t.action}
              </p>
              <p className="text-sm text-navy/65">{t.result}</p>
            </div>
            <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${chip(t.agent)}`}>{t.agent}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
