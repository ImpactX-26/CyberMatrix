import { useEffect } from 'react';
import { X } from 'lucide-react';

export default function DocumentModal({ doc, onClose }) {
  useEffect(() => {
    if (!doc) return undefined;
    const h = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [doc, onClose]);
  if (!doc) return null;
  return (
    <div className="fixed inset-0 z-[2000] grid place-items-center bg-deep/70 p-4" onClick={onClose} role="dialog" aria-modal="true" aria-label={`${doc.sourceType} document preview`}>
      <div className="anim-reveal relative max-h-[90vh] w-full max-w-lg overflow-auto rounded-xl bg-[#FFFEFA] p-8 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className="absolute right-3 top-3 rounded-lg p-2 hover:bg-navy/5" aria-label="Close preview"><X size={20} /></button>
        <p className="text-center text-xs font-semibold text-bad">SYNTHETIC DEMO DOCUMENT — NOT A REAL RECORD</p>
        <h2 className="mt-3 text-center text-2xl font-bold">{doc.sourceType} Record</h2>
        <p className="text-center text-sm text-navy/60">{doc.sourceId}</p>
        <div className="my-5 border-y border-navy/20 py-1">
          {doc.rows.map(([k, v]) => (
            <div key={k} className="flex justify-between gap-4 border-b border-dashed border-navy/15 py-2.5 text-sm last:border-0">
              <span className="text-navy/60">{k}</span><span className="font-semibold">{v}</span>
            </div>
          ))}
        </div>
        <div className="flex items-end justify-between text-xs text-navy/50">
          <span>Generated for LandShield demo<br />Synthetic Demo Data</span>
          <span className="rotate-[-6deg] rounded border-2 border-ok/50 px-2 py-1 font-bold text-ok/60">DEMO SEAL</span>
        </div>
      </div>
    </div>
  );
}
