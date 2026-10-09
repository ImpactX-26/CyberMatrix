import { Link, useNavigate } from 'react-router-dom';
import { Eye, ShieldAlert, Bot, FileCheck, ArrowRight, Building2, GitCompare, Search, FileText, Flag } from 'lucide-react';
import { setStage } from '../data/sim';
import { MAIN_ID } from '../data/demoData';
import { useAuth } from '../context/AuthContext';

const FEATURES = [
  { Icon: Eye, title: 'Track', text: 'Monitor meaningful property changes.' },
  { Icon: ShieldAlert, title: 'Detect', text: 'Identify suspicious transaction sequences.' },
  { Icon: Bot, title: 'Investigate', text: 'AI-assisted investigation.' },
  { Icon: FileCheck, title: 'Evidence', text: 'Connect findings to source records.' },
];
const FLOW = [
  { Icon: Building2, t: 'Property', d: 'Survey 49/1', c: 'text-info' },
  { Icon: GitCompare, t: 'Changes', d: 'Sales, mortgages, mutations', c: 'text-warn' },
  { Icon: Search, t: 'Investigation', d: 'AI agent analysis', c: 'text-ai' },
  { Icon: FileText, t: 'Evidence', d: 'Source records', c: 'text-ok' },
];

function HeroVisual() {
  return (
    <div className="relative mx-auto w-full max-w-xl">
      <svg viewBox="0 0 520 440" className="w-full" role="img" aria-label="Synthetic land parcel with boundary and location marker">
        <defs>
          <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#ffffff" strokeOpacity=".07" /></pattern>
        </defs>
        <rect width="520" height="440" rx="24" fill="#0B3552" />
        <rect width="520" height="440" rx="24" fill="url(#grid)" />
        <g fill="#0f4366" stroke="#ffffff" strokeOpacity=".25">
          <polygon points="30,40 170,30 180,150 40,160" /><polygon points="190,28 330,40 322,140 196,150" />
          <polygon points="30,200 150,210 140,330 36,320" /><polygon points="340,200 490,190 484,330 350,340" />
          <polygon points="170,340 330,350 320,410 176,404" />
        </g>
        <polygon points="170,190 320,170 360,260 310,330 180,310" fill="#159447" fillOpacity=".35" stroke="#fff" strokeWidth="3" className="anim-draw" />
        <path d="M0 175 C120 190 200 150 330 160 S470 120 520 140" stroke="#fff" strokeOpacity=".18" strokeWidth="6" fill="none" />
        <g transform="translate(262 245)">
          <circle r="10" fill="#D92D3A" className="anim-ring" /><circle r="9" fill="#D92D3A" stroke="#fff" strokeWidth="3" />
        </g>
        <text x="236" y="288" fill="#fff" fontSize="15" fontWeight="700">49/1</text>
        <text x="64" y="104" fill="#fff" fillOpacity=".6" fontSize="12">49/2</text>
        <text x="236" y="92" fill="#fff" fillOpacity=".6" fontSize="12">50/1</text>
        <text x="62" y="268" fill="#fff" fillOpacity=".6" fontSize="12">47/2</text>
        <text x="392" y="268" fill="#fff" fillOpacity=".6" fontSize="12">50/2</text>
      </svg>
      <div className="absolute -right-2 top-4 hidden w-52 space-y-2 sm:block">
        {FLOW.map(({ Icon, t, d, c }, i) => (
          <div key={t} className="flex items-center gap-3 rounded-xl bg-white p-2.5 shadow-lg" style={{ marginLeft: i % 2 ? 14 : 0 }}>
            <Icon size={18} className={c} />
            <span className="leading-tight"><span className="block text-sm font-bold">{t}</span><span className="block text-[11px] text-navy/55">{d}</span></span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Landing() {
  const nav = useNavigate();
  const { isAuthenticated } = useAuth();
  const demo = () => { setStage(3); nav(`/investigation/${MAIN_ID}`); };
  return (
    <>
      <section className="bg-gradient-to-br from-deep via-navy to-[#0d3a5c] text-white">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 py-14 sm:px-6 lg:grid-cols-2 lg:py-20">
          <div>
            <h1 className="text-5xl font-bold tracking-wide sm:text-6xl">LANDSHIELD</h1>
            <h2 className="mt-4 text-3xl font-semibold leading-tight text-[#8fe0ae] sm:text-4xl">Don't just verify a property. Watch its story change.</h2>
            <p className="mt-5 max-w-lg text-lg text-white/80">Monitor meaningful property-record changes and investigate suspicious sequences before they become expensive surprises.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              {isAuthenticated
                ? <Link to="/setup" className="btn-primary !px-6 !py-3">Watch a Property <ArrowRight size={16} /></Link>
                : <Link to="/login" className="btn-primary !px-6 !py-3">Get Started <ArrowRight size={16} /></Link>}
              <button onClick={demo} className="btn !border !border-white/40 !px-6 !py-3 text-white hover:bg-white/10">See Demo Investigation</button>
            </div>
            <p className="mt-6 text-xs text-white/50">Synthetic Demo Data · No real people, addresses or records</p>
          </div>
          <HeroVisual />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ Icon, title, text }) => (
            <div key={title} className="card p-6">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-navy text-white"><Icon size={20} /></span>
              <h3 className="mt-4 text-xl font-bold">{title}</h3>
              <p className="mt-1 text-sm text-navy/65">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
        <div className="card p-6 sm:p-10">
          <h2 className="text-3xl font-bold">One property, five steps to an answer</h2>
          <ol className="mt-8 grid gap-4 md:grid-cols-5">
            {['Property', 'Change', 'Investigation', 'Evidence', 'Action'].map((s, i) => (
              <li key={s} className="relative rounded-xl border border-navy/10 bg-cream p-4">
                <span className="text-xs font-bold text-navy/40">Step {i + 1}</span>
                <p className="font-display text-xl font-semibold">{s}</p>
                <p className="mt-1 text-sm text-navy/65">{['Set a baseline: owner, extent, mortgage.', 'New sale, mortgage or mutation recorded.', 'Agents compare records and flag mismatches.', 'Every finding links to a source record.', 'Human or legal verification decides.'][i]}</p>
              </li>
            ))}
          </ol>
          <p className="mt-6 flex items-start gap-2 text-sm text-navy/70"><Flag size={16} className="mt-0.5 shrink-0 text-warn" /> LandShield flags a potential suspicious transaction pattern. It never decides fraud — that needs human/legal verification.</p>
        </div>
      </section>
    </>
  );
}
