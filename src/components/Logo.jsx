export default function Logo({ size = 36, light = false, showText = true }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
        <path d="M24 3 6 10v13c0 11 7.6 19.4 18 22 10.4-2.6 18-11 18-22V10z" fill={light ? '#FFFFFF' : '#08263D'} />
        <path d="M14 28l5.5-11 11.5 3.2 3.2 9.3-10.2 5.5z" fill="#159447" />
        <path d="M14 28l5.5-11 11.5 3.2 3.2 9.3-10.2 5.5z" fill="none" stroke={light ? '#08263D' : '#fff'} strokeWidth="1.2" strokeDasharray="2 2" />
        <circle cx="24.5" cy="23.5" r="3.2" fill={light ? '#08263D' : '#fff'} />
      </svg>
      {showText && (
        <span className={`font-display text-xl font-bold tracking-wide ${light ? 'text-white' : 'text-navy'}`}>LANDSHIELD</span>
      )}
    </span>
  );
}
