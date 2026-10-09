import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, CheckCircle2, AlertCircle, ArrowLeft, Loader2, ShieldCheck, GitCompare, FileCheck } from 'lucide-react';
import Logo from '../components/Logo';
import { useAuth } from '../context/AuthContext';
import { isValidEmail, isValidPhone } from '../services/auth';

const EMPTY = { name: '', phone: '', email: '', password: '', confirm: '' };

function AuthVisual() {
  return (
    <svg viewBox="0 0 520 300" className="w-full max-w-md" role="img" aria-label="Abstract land parcels with a monitored boundary">
      <defs>
        <pattern id="lgrid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="#fff" strokeOpacity=".07" /></pattern>
      </defs>
      <rect width="520" height="300" rx="22" fill="#0B3552" />
      <rect width="520" height="300" rx="22" fill="url(#lgrid)" />
      <g fill="#0f4366" stroke="#fff" strokeOpacity=".22">
        <polygon points="24,28 150,22 158,108 30,116" /><polygon points="170,20 300,30 292,100 176,108" />
        <polygon points="24,150 120,158 112,262 30,254" /><polygon points="340,150 496,140 490,260 350,268" />
        <polygon points="330,28 496,22 490,118 338,110" />
      </g>
      <polygon points="150,130 290,112 330,190 285,254 160,238" fill="#159447" fillOpacity=".35" stroke="#fff" strokeWidth="2.5" className="anim-draw" />
      <path d="M0 125 C110 140 190 100 310 112 S460 82 520 98" stroke="#fff" strokeOpacity=".15" strokeWidth="5" fill="none" />
      <g transform="translate(238 184)"><circle r="9" fill="#159447" className="anim-ring" /><circle r="8" fill="#159447" stroke="#fff" strokeWidth="2.5" /></g>
      <text x="205" y="222" fill="#fff" fontSize="13" fontWeight="700">Parcel monitored</text>
    </svg>
  );
}

function Field({ id, label, error, right, children }) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <label htmlFor={id} className="mb-1.5 block text-sm font-semibold text-navy">{label}</label>
        {right}
      </div>
      {children}
      {error && (
        <p id={`${id}-err`} role="alert" className="mt-1.5 flex items-center gap-1.5 text-xs font-medium text-bad">
          <AlertCircle size={13} className="shrink-0" /> {error}
        </p>
      )}
    </div>
  );
}

const inputCls = (err) =>
  `w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-navy placeholder:text-navy/35 transition-colors focus:border-ok focus:outline-none focus:ring-2 focus:ring-ok/25 ${err ? 'border-bad' : 'border-navy/20'}`;

function PasswordInput({ id, value, onChange, error, autoComplete, placeholder }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <input id={id} type={show ? 'text' : 'password'} value={value} onChange={onChange} autoComplete={autoComplete}
        placeholder={placeholder} aria-invalid={!!error} aria-describedby={error ? `${id}-err` : undefined}
        className={`${inputCls(error)} pr-11`} />
      <button type="button" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'}
        className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-navy/50 hover:text-navy">
        {show ? <EyeOff size={17} /> : <Eye size={17} />}
      </button>
    </div>
  );
}

export default function Login() {
  const { isAuthenticated, signIn, signUp, resetPassword } = useAuth();
  const nav = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState('signin'); // signin | signup | forgot
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const dest = location.state?.from
    ? `${location.state.from.pathname}${location.state.from.search || ''}`
    : '/portfolio';

  // Already signed in (and not mid-redirect from a form submit): go straight to the app.
  if (isAuthenticated && !busy) return <Navigate to={dest} replace />;

  const set = (k) => (e) => {
    setForm((f) => ({ ...f, [k]: e.target.value }));
    if (errors[k]) setErrors((x) => ({ ...x, [k]: undefined }));
    if (formError) setFormError('');
  };

  const switchMode = (m) => {
    setMode(m);
    setErrors({});
    setFormError('');
    setNotice('');
    setForm((f) => ({ ...EMPTY, email: f.email }));
  };

  const validate = () => {
    const e = {};
    if (mode === 'signup') {
      if (!form.name.trim()) e.name = 'Full name is required.';
      if (!form.phone.trim()) e.phone = 'Phone number is required.';
      else if (!isValidPhone(form.phone)) e.phone = 'Enter a valid phone number (e.g. 98765 43210).';
    }
    if (!form.email.trim()) e.email = 'Email is required.';
    else if (!isValidEmail(form.email)) e.email = 'Enter a valid email address.';
    if (!form.password) e.password = mode === 'forgot' ? 'New password is required.' : 'Password is required.';
    else if ((mode === 'signup' || mode === 'forgot') && form.password.length < 6) e.password = 'Use at least 6 characters.';
    if (mode === 'signup' || mode === 'forgot') {
      if (!form.confirm) e.confirm = 'Please confirm your password.';
      else if (form.confirm !== form.password) e.confirm = 'Passwords do not match.';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = async (ev) => {
    ev.preventDefault();
    setFormError('');
    setNotice('');
    if (!validate()) return;
    setBusy(true);
    try {
      if (mode === 'signup') {
        const res = await signUp(form);
        if (!res.ok) { setFormError(res.error); return; }
        setBusy(false);
        setMode('signin');
        setForm({ ...EMPTY, email: form.email.trim() });
        setNotice('Account created successfully. Please sign in to continue.');
      } else if (mode === 'forgot') {
        const res = await resetPassword(form);
        if (!res.ok) { setFormError(res.error); return; }
        setBusy(false);
        setMode('signin');
        setForm({ ...EMPTY, email: form.email.trim() });
        setNotice('Password updated. Please sign in with your new password.');
      } else {
        const res = await signIn(form);
        if (!res.ok) { setFormError(res.error); return; }
        nav(dest, { replace: true });
      }
    } finally {
      setBusy(false);
    }
  };

  const title = mode === 'signup' ? 'Create your account' : mode === 'forgot' ? 'Reset your password' : 'Welcome back';
  const sub = mode === 'signup' ? 'Start monitoring your property records.' : mode === 'forgot' ? 'Demo reset: confirm your email and choose a new password.' : 'Sign in to your LandShield workspace.';

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      {/* Brand panel */}
      <aside className="relative flex flex-col justify-between overflow-hidden bg-gradient-to-br from-deep via-navy to-[#0d3a5c] px-6 py-8 text-white sm:px-10 lg:px-14 lg:py-12">
        <Link to="/" aria-label="LandShield home" className="w-fit"><Logo light /></Link>
        <div className="my-10 lg:my-0">
          <h1 className="max-w-lg text-4xl font-bold leading-tight sm:text-5xl">Secure access to your <span className="text-[#8fe0ae]">property intelligence.</span></h1>
          <p className="mt-5 max-w-md text-base text-white/75 sm:text-lg">Monitor property changes, investigate suspicious sequences, and keep your land records in view.</p>
          <ul className="mt-7 space-y-3 text-sm text-white/80">
            {[[ShieldCheck, 'Watch ownership, mortgage and mutation changes'], [GitCompare, 'Flag suspicious transaction sequences early'], [FileCheck, 'Trace every finding to its source record']].map(([Icon, t]) => (
              <li key={t} className="flex items-center gap-3"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-white/10"><Icon size={16} className="text-[#8fe0ae]" /></span>{t}</li>
            ))}
          </ul>
          <div className="mt-9 hidden lg:block"><AuthVisual /></div>
        </div>
        <p className="text-xs text-white/45">Synthetic Demo Data · No real people, addresses or records</p>
      </aside>

      {/* Form panel */}
      <main className="flex items-center justify-center bg-cream px-4 py-10 sm:px-8">
        <div className="w-full max-w-md">
          <Link to="/" className="mb-5 inline-flex items-center gap-1.5 text-sm text-navy/60 hover:text-navy"><ArrowLeft size={15} /> Back to home</Link>
          <div className="card p-6 sm:p-8">
            {mode !== 'forgot' && (
              <div role="tablist" aria-label="Authentication mode" className="mb-6 grid grid-cols-2 rounded-xl bg-navy/[0.06] p-1">
                {[['signin', 'Sign In'], ['signup', 'Sign Up']].map(([m, label]) => (
                  <button key={m} role="tab" aria-selected={mode === m} type="button" onClick={() => switchMode(m)}
                    className={`rounded-lg py-2 text-sm font-semibold transition-colors ${mode === m ? 'bg-white text-navy shadow-sm' : 'text-navy/55 hover:text-navy'}`}>
                    {label}
                  </button>
                ))}
              </div>
            )}

            <h2 className="text-3xl font-bold">{title}</h2>
            <p className="mt-1 text-sm text-navy/60">{sub}</p>

            {notice && (
              <div role="status" className="mt-5 flex items-start gap-2 rounded-xl border border-ok/30 bg-ok/10 px-3.5 py-3 text-sm font-medium text-[#0d6b33]">
                <CheckCircle2 size={17} className="mt-0.5 shrink-0" /> {notice}
              </div>
            )}
            {formError && (
              <div role="alert" className="mt-5 flex items-start gap-2 rounded-xl border border-bad/30 bg-bad/10 px-3.5 py-3 text-sm font-medium text-bad">
                <AlertCircle size={17} className="mt-0.5 shrink-0" /> {formError}
              </div>
            )}

            <form onSubmit={submit} noValidate className="mt-5 space-y-4">
              {mode === 'signup' && (
                <>
                  <Field id="name" label="Full Name" error={errors.name}>
                    <input id="name" value={form.name} onChange={set('name')} autoComplete="name" placeholder="Your full name"
                      aria-invalid={!!errors.name} aria-describedby={errors.name ? 'name-err' : undefined} className={inputCls(errors.name)} />
                  </Field>
                  <Field id="phone" label="Phone Number" error={errors.phone}>
                    <input id="phone" type="tel" value={form.phone} onChange={set('phone')} autoComplete="tel" placeholder="98765 43210"
                      aria-invalid={!!errors.phone} aria-describedby={errors.phone ? 'phone-err' : undefined} className={inputCls(errors.phone)} />
                  </Field>
                </>
              )}
              <Field id="email" label="Email" error={errors.email}>
                <input id="email" type="email" value={form.email} onChange={set('email')} autoComplete="email" placeholder="you@example.com"
                  aria-invalid={!!errors.email} aria-describedby={errors.email ? 'email-err' : undefined} className={inputCls(errors.email)} />
              </Field>
              <Field id="password" label={mode === 'forgot' ? 'New Password' : 'Password'} error={errors.password}
                right={mode === 'signin' && (
                  <button type="button" onClick={() => switchMode('forgot')} className="mb-1.5 text-xs font-semibold text-info hover:underline">Forgot Password?</button>
                )}>
                <PasswordInput id="password" value={form.password} onChange={set('password')} error={errors.password}
                  autoComplete={mode === 'signin' ? 'current-password' : 'new-password'} placeholder={mode === 'signin' ? 'Enter your password' : 'At least 6 characters'} />
              </Field>
              {(mode === 'signup' || mode === 'forgot') && (
                <Field id="confirm" label="Confirm Password" error={errors.confirm}>
                  <PasswordInput id="confirm" value={form.confirm} onChange={set('confirm')} error={errors.confirm}
                    autoComplete="new-password" placeholder="Re-enter your password" />
                </Field>
              )}

              <button type="submit" disabled={busy} className="btn-primary w-full !py-3">
                {busy && <Loader2 size={16} className="animate-spin" />}
                {mode === 'signup' ? 'Create Account' : mode === 'forgot' ? 'Update Password' : 'Sign In'}
              </button>
            </form>

            <p className="mt-5 text-center text-sm text-navy/65">
              {mode === 'signin' && <>Don't have an account? <button type="button" onClick={() => switchMode('signup')} className="font-semibold text-info hover:underline">Create Account</button></>}
              {mode === 'signup' && <>Already have an account? <button type="button" onClick={() => switchMode('signin')} className="font-semibold text-info hover:underline">Sign In</button></>}
              {mode === 'forgot' && <button type="button" onClick={() => switchMode('signin')} className="font-semibold text-info hover:underline">Back to Sign In</button>}
            </p>
          </div>
          <p className="mt-4 text-center text-xs text-navy/45">Demo authentication · accounts are stored only in this browser.</p>
        </div>
      </main>
    </div>
  );
}
