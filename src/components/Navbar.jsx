import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, LogOut } from 'lucide-react';
import Logo from './Logo';
import { MAIN_ID } from '../data/demoData';
import { useAuth } from '../context/AuthContext';

const HOME = { label: 'Home', to: '/', match: (l) => l.pathname === '/' };
const APP_LINKS = [
  { label: 'Portfolio', to: '/portfolio', match: (l) => l.pathname === '/portfolio' },
  { label: 'Map', to: `/property/${MAIN_ID}?tab=map`, match: (l) => l.pathname.startsWith('/property') && l.search.includes('tab=map') },
  { label: 'Investigations', to: `/investigation/${MAIN_ID}`, match: (l) => l.pathname.startsWith('/investigation') },
];

export default function Navbar() {
  const loc = useLocation();
  const nav = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const LINKS = isAuthenticated ? [HOME, ...APP_LINKS] : [HOME];
  const handleLogout = () => { setOpen(false); logout(); nav('/login', { replace: true }); };
  const firstName = (user?.name || '').split(' ')[0];
  return (
    <header className="sticky top-0 z-[1000] border-b border-white/10 bg-deep text-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link to="/" onClick={() => setOpen(false)} aria-label="LandShield home"><Logo light /></Link>
        <nav className="hidden items-center gap-1 md:flex" aria-label="Main">
          {LINKS.map((l) => (
            <Link key={l.label} to={l.to}
              className={`rounded-lg px-3.5 py-2 text-sm font-medium transition-colors ${l.match(loc) ? 'bg-white/[0.12] text-white' : 'text-white/70 hover:text-white'}`}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <Link to="/setup" className="btn-primary hidden !py-2 sm:inline-flex">Watch a Property</Link>
              <span className="hidden max-w-[120px] truncate text-sm text-white/70 lg:inline" title={user?.email}>{firstName}</span>
              <button onClick={handleLogout} className="btn hidden !py-2 border border-white/30 text-white hover:bg-white/10 md:inline-flex"><LogOut size={15} /> Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn hidden !py-2 border border-white/30 text-white hover:bg-white/10 sm:inline-flex">Sign In</Link>
              <Link to="/login" className="btn-primary hidden !py-2 sm:inline-flex">Get Started</Link>
            </>
          )}
          <button className="rounded-lg p-2 md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu" aria-expanded={open}>
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>
      {open && (
        <div className="border-t border-white/10 bg-deep px-4 pb-4 md:hidden">
          {LINKS.map((l) => (
            <Link key={l.label} to={l.to} onClick={() => setOpen(false)} className="block rounded-lg px-3 py-3 text-sm font-medium text-white/85">{l.label}</Link>
          ))}
          {isAuthenticated ? (
            <>
              <Link to="/setup" onClick={() => setOpen(false)} className="btn-primary mt-2 w-full">Watch a Property</Link>
              <button onClick={handleLogout} className="btn mt-2 w-full border border-white/30 text-white hover:bg-white/10"><LogOut size={15} /> Logout{firstName ? ` (${firstName})` : ''}</button>
            </>
          ) : (
            <div className="mt-2 grid grid-cols-2 gap-2">
              <Link to="/login" onClick={() => setOpen(false)} className="btn border border-white/30 text-white hover:bg-white/10">Sign In</Link>
              <Link to="/login" onClick={() => setOpen(false)} className="btn-primary">Get Started</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
