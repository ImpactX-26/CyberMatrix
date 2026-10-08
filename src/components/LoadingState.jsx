const B = ({ className = '' }) => <div className={`animate-pulse rounded-xl bg-navy/10 ${className}`} />;

export default function LoadingState({ variant = 'page' }) {
  if (variant === 'cards') return <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true">{[...Array(6)].map((_, i) => <B key={i} className="h-44" />)}</div>;
  if (variant === 'timeline') return <div className="space-y-5" aria-busy="true">{[...Array(4)].map((_, i) => <div key={i} className="flex gap-4"><B className="h-9 w-9 !rounded-full" /><B className="h-20 flex-1" /></div>)}</div>;
  if (variant === 'graph') return <B className="h-[460px] w-full" />;
  return (
    <div className="space-y-5" aria-busy="true" aria-label="Loading">
      <B className="h-24 w-full" />
      <div className="grid gap-4 md:grid-cols-3"><B className="h-40" /><B className="h-40" /><B className="h-40" /></div>
      <B className="h-64 w-full" />
    </div>
  );
}
