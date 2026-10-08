export const FILTERS = ['All', 'Registration', 'Mutation', 'Mortgage', 'RTC'];

export default function EvidenceFilters({ value, onChange, items }) {
  const count = (f) => (f === 'All' ? items.length : items.filter((i) => i.sourceType === f).length);
  return (
    <div className="flex flex-wrap gap-2" role="tablist" aria-label="Evidence filters">
      {FILTERS.map((f) => (
        <button key={f} role="tab" aria-selected={value === f} onClick={() => onChange(f)}
          className={`rounded-full border px-4 py-1.5 text-sm font-semibold transition ${value === f ? 'border-navy bg-navy text-white' : 'border-navy/15 bg-white text-navy hover:bg-navy/5'}`}>
          {f} <span className="opacity-60">({count(f)})</span>
        </button>
      ))}
    </div>
  );
}
