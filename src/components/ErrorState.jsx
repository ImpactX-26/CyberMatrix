import { Link } from 'react-router-dom';
import { WifiOff } from 'lucide-react';

export default function ErrorState({ title = 'Unable to connect to LandShield backend.', message, onRetry, onDemo, backHome }) {
  return (
    <div className="card mx-auto max-w-lg p-8 text-center">
      <span className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-warn/15 text-warn"><WifiOff size={26} /></span>
      <h2 className="mt-4 text-2xl font-bold">{title}</h2>
      {message && <p className="mt-2 text-sm text-navy/65">{message}</p>}
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        {onRetry && <button className="btn-ghost" onClick={onRetry}>Retry</button>}
        {onDemo && <button className="btn-navy" onClick={onDemo}>Continue with Demo</button>}
        {backHome && <Link to="/portfolio" className="btn-navy">Back to portfolio</Link>}
      </div>
    </div>
  );
}
