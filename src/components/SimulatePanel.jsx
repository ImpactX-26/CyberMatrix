import { Plus, RotateCcw, ArrowRight } from 'lucide-react';
import { setStage } from '../data/sim';
import { simulateEvent } from '../services/api';

const STEPS = [
  { key: 'baseline', label: 'Baseline' },
  { key: 'mortgage', label: 'Mortgage registered' },
  { key: 'registration', label: 'Registration added' },
  { key: 'mutation', label: 'Mutation added' },
  { key: 'investigation', label: 'Investigation triggered' },
];
const BUTTONS = [['Add Mortgage', 'MORTGAGE_REGISTERED'], ['Add Registration', 'REGISTRATION'], ['Add Mutation', 'MUTATION_UPDATED']];

export default function SimulatePanel({ propertyId, stage }) {
  const done = stage === 3 ? 4 : stage; // index of last reached step
  const advance = (i, ev) => {
    setStage(i + 1);
    simulateEvent(propertyId, ev).catch(() => {}); // best effort; demo works without backend
  };
  return (
    <section className="card p-5" aria-label="Simulate property change">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold">Simulate Property Change</h2>
          <p className="text-sm text-navy/60">Add events one at a time and watch the property story change.</p>
        </div>
        <button className="btn-ghost !py-2" onClick={() => setStage(0)}><RotateCcw size={15} /> Reset to baseline</button>
      </div>
      <ol className="mt-4 flex flex-wrap items-center gap-x-1 gap-y-2 text-xs font-semibold">
        {STEPS.map((s, i) => (
          <li key={s.key} className="flex items-center gap-1">
            <span className={`rounded-full px-3 py-1 ${i <= done ? (i === 4 ? 'bg-bad text-white' : 'bg-navy text-white') : 'bg-navy/[0.08] text-navy/45'}`}>{s.label}</span>
            {i < STEPS.length - 1 && <ArrowRight size={14} className="text-navy/30" />}
          </li>
        ))}
      </ol>
      <div className="mt-4 flex flex-wrap gap-2">
        {BUTTONS.map(([label, ev], i) => (
          <button key={label} className={i === stage ? 'btn-primary !py-2' : 'btn-ghost !py-2'} disabled={i !== stage} onClick={() => advance(i, ev)}>
            <Plus size={15} /> {label}
          </button>
        ))}
      </div>
    </section>
  );
}
