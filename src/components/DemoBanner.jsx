import { CloudOff, RefreshCw } from 'lucide-react';
import { useMode } from '../services/mode';
import { retryBackend, continueWithDemo } from '../services/api';

export default function DemoBanner() {
  const { mode, forced } = useMode();
  if (mode !== 'demo') return null;
  return (
    <div className="border-b border-warn/30 bg-[#FFF6E5] text-sm text-navy" role="status">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2 sm:px-6">
        <span className="inline-flex items-center gap-2 font-semibold"><CloudOff size={16} className="text-warn" /> Demo Mode Active</span>
        <span className="text-navy/70">
          {forced ? 'Showing Synthetic Demo Data.' : 'Unable to connect to LandShield backend. Showing Synthetic Demo Data.'}
        </span>
        <span className="ml-auto flex gap-2">
          <button onClick={retryBackend} className="inline-flex items-center gap-1.5 rounded-lg border border-navy/20 bg-white px-3 py-1 text-xs font-semibold hover:bg-navy/5"><RefreshCw size={13} /> Retry</button>
          {!forced && <button onClick={continueWithDemo} className="rounded-lg bg-navy px-3 py-1 text-xs font-semibold text-white hover:bg-deep">Continue with Demo</button>}
        </span>
      </div>
    </div>
  );
}
