import { useEffect, useMemo, useState } from 'react';


import axios from 'axios';


import './index.css';


const API =


  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';


const http = axios.create({


  baseURL: API,


  timeout: 5000,


});


/* ---------------------------------------------------------


   LOGIN


--------------------------------------------------------- */



function Login({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const readUsers = () => {
    try {
      return JSON.parse(
        localStorage.getItem('cybermatrix_accounts') || '[]'
      );
    } catch {
      return [];
    }
  };

  async function hashPassword(value) {
    if (!globalThis.crypto?.subtle) {
      throw new Error(
        'Secure password hashing is unavailable. Use localhost or HTTPS.'
      );
    }

    const bytes = await crypto.subtle.digest(
      'SHA-256',
      new TextEncoder().encode(`cybermatrix:${value}`)
    );

    return Array.from(new Uint8Array(bytes))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    setNotice('');

    const cleanEmail = email.trim().toLowerCase();

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setError('Enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.');
      return;
    }

    if (mode === 'register') {
      if (!name.trim() || !phone.trim()) {
        setError('Enter your full name and phone number.');
        return;
      }

      if (password !== confirmPassword) {
        setError('Passwords do not match.');
        return;
      }
    }

    setBusy(true);

    try {
      const users = readUsers();
      const existing = users.find((u) => u.email === cleanEmail);
      const passwordHash = await hashPassword(password);

      if (mode === 'register') {
        if (existing) {
          setError('This email is already registered. Please log in.');
          return;
        }

        users.push({
          name: name.trim(),
          phone: phone.trim(),
          email: cleanEmail,
          passwordHash,
          createdAt: new Date().toISOString(),
        });

        localStorage.setItem(
          'cybermatrix_accounts',
          JSON.stringify(users)
        );

        setMode('login');
        setPassword('');
        setConfirmPassword('');
        setNotice('Account created! You can now log in.');
      } else {
        if (!existing || existing.passwordHash !== passwordHash) {
          setError(
            'Incorrect email or password. Register first if you are new.'
          );
          return;
        }

        const session = {
          name: existing.name,
          phone: existing.phone,
          email: existing.email,
          signedInAt: new Date().toISOString(),
        };

        localStorage.setItem(
          'cybermatrix_user',
          JSON.stringify(session)
        );

        onLogin(session);
      }
    } catch (err) {
      setError(err.message || 'Unable to complete authentication.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-glow" />

      <div className="login-card">
        <div className="login-logo">CYBERMATRIX</div>

        <div className="login-tagline">
          LAND OWNERSHIP INTELLIGENCE
        </div>

        <div className="login-line" />

        <h1>
          {mode === 'register'
            ? 'Create your account.'
            : 'Secure your land.'}
        </h1>

        <p className="login-description">
          {mode === 'register'
            ? 'Join CyberMatrix to monitor land ownership and property risks.'
            : 'Detect ownership conflicts, suspicious transactions and land-record risks.'}
        </p>

        <div className="auth-switch">
          <button
            type="button"
            className={mode === 'login' ? 'auth-switch-active' : ''}
            onClick={() => {
              setMode('login');
              setError('');
              setNotice('');
            }}
          >
            LOGIN
          </button>

          <button
            type="button"
            className={mode === 'register' ? 'auth-switch-active' : ''}
            onClick={() => {
              setMode('register');
              setError('');
              setNotice('');
            }}
          >
            CREATE ACCOUNT
          </button>
        </div>

        <form onSubmit={submit}>
          {mode === 'register' && (
            <>
              <label htmlFor="register-name">Full name</label>
              <input
                id="register-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your full name"
                autoComplete="name"
                required
              />

              <label htmlFor="register-phone">Phone number</label>
              <input
                id="register-phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Your phone number"
                autoComplete="tel"
                required
              />
            </>
          )}

          <label htmlFor="auth-email">Email</label>
          <input
            id="auth-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="owner@example.com"
            autoComplete="email"
            required
          />

          <label htmlFor="auth-password">Password</label>
          <input
            id="auth-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            autoComplete={
              mode === 'register' ? 'new-password' : 'current-password'
            }
            required
          />

          {mode === 'register' && (
            <>
              <label htmlFor="auth-confirm-password">
                Confirm password
              </label>
              <input
                id="auth-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your password"
                autoComplete="new-password"
                required
              />
            </>
          )}

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}

          {notice && (
            <div className="login-notice" role="status">
              {notice}
            </div>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={busy}
          >
            {busy
              ? 'PLEASE WAIT...'
              : mode === 'register'
                ? 'CREATE MY ACCOUNT'
                : 'LOGIN TO CYBERMATRIX'}
          </button>
        </form>

        <div className="login-footer">
          Land Record Intelligence &amp; Verification
        </div>

        <p className="auth-storage-note">
          Demo accounts are saved in this browser.
        </p>
      </div>
    </div>
  );
}



/* ---------------------------------------------------------


   HELPERS


--------------------------------------------------------- */


function formatDate(value) {


  if (!value) return '—';


  const d = new Date(value);


  if (Number.isNaN(d.getTime())) return String(value);


  return d.toLocaleDateString('en-IN', {


    day: '2-digit',


    month: 'short',


    year: 'numeric',


  });


}


function daysUntil(date) {


  const now = new Date();


  const target = new Date(date);


  return Math.max(


    0,


    Math.ceil((target - now) / (1000 * 60 * 60 * 24))


  );


}


function normalizeValue(value) {

  return String(value ?? '').trim().toLowerCase().replace(/\s+/g, ' ').replace(/[.,]/g, '');

}


function normalizeSurvey(value) {

  return String(value ?? '').trim().toLowerCase().replace(/^\s*(?:survey\s*(?:no\.?|number)?|sy\s*no?\.?)\s*/i, '').replace(/\s+/g, '');

}


function latestRecord(records, dateField) {

  if (!Array.isArray(records) || records.length === 0) return null;

  return [...records].sort((a, b) => {

    const da = Date.parse(a?.[dateField] || '');

    const db = Date.parse(b?.[dateField] || '');

    if (Number.isFinite(da) && Number.isFinite(db)) return da - db;

    if (Number.isFinite(da)) return 1;

    if (Number.isFinite(db)) return -1;

    return 0;

  }).at(-1);

}


function calculateRisk(property, registrations = [], mutations = [], mortgages = [], allProperties = [], documentAnalysis = null) {

  const findings = [];

  const issueIds = new Set();

  let score = 0;

  const norm = normalizeValue;

  const survey = normalizeSurvey;

  const regs = Array.isArray(registrations) ? registrations : [];

  const muts = Array.isArray(mutations) ? mutations : [];

  const mort = Array.isArray(mortgages) ? mortgages : [];

  const props = Array.isArray(allProperties) ? allProperties : [];


  function addFinding(id, points, severity, title, detail, evidence = []) {

    if (issueIds.has(id)) return;

    issueIds.add(id);

    score += points;

    findings.push({ severity, title, detail, evidence, points });

  }


  const latestReg = latestRecord(regs, 'transaction_date');

  const latestMut = latestRecord(muts, 'mutation_date');

  const buyers = [...new Set(regs.map(r => norm(r?.buyer)).filter(Boolean))];

  const sellers = [...new Set(regs.map(r => norm(r?.seller)).filter(Boolean))];

  const mutationOwners = [...new Set(muts.map(m => norm(m?.new_owner)).filter(Boolean))];


  // Detect a possible double sale: one seller recorded transferring the same

  // selected parcel to different buyers. The finding is deliberately strong,

  // but still requires checking original deeds and transaction dates.

  const sellerToBuyers = new Map();

  for (const r of regs) {

    const seller = norm(r?.seller);

    const buyer = norm(r?.buyer);

    if (!seller || !buyer || seller === buyer) continue;

    if (!sellerToBuyers.has(seller)) sellerToBuyers.set(seller, new Set());

    sellerToBuyers.get(seller).add(buyer);

  }

  const doubleSales = [...sellerToBuyers.entries()].filter(([, bs]) => bs.size > 1);

  if (doubleSales.length) {

    const details = doubleSales.map(([seller, bs]) => `${seller} is recorded as seller to multiple buyers: ${[...bs].join(', ')}`);

    addFinding('possible-double-sale', 70, 'CRITICAL', 'Possible multiple sale of the same parcel', `${details.join('. ')}. Confirm the survey/hissa and transaction dates in the original registered deeds. This is a serious warning, not a legal finding of fraud.`, details);

  }


  // Compare the latest registered buyer, mutation owner, and current snapshot.

  const regBuyer = norm(latestReg?.buyer);

  const mutOwner = norm(latestMut?.new_owner);

  const currentOwner = norm(property?.owner_name);

  const ownerMismatches = [];

  if (regBuyer && mutOwner && regBuyer !== mutOwner) ownerMismatches.push(`Latest registration buyer (${latestReg.buyer}) differs from latest mutation owner (${latestMut.new_owner})`);

  if (currentOwner && mutOwner && currentOwner !== mutOwner) ownerMismatches.push(`Property snapshot owner (${property.owner_name}) differs from latest mutation owner (${latestMut.new_owner})`);

  if (ownerMismatches.length) {

    addFinding('ownership-record-conflict', 35, 'HIGH', 'Ownership records conflict', `${ownerMismatches.join('. ')}. Verify the latest official records and dates.`, [latestReg?.buyer ? `Registration buyer: ${latestReg.buyer}` : null, latestMut?.new_owner ? `Mutation owner: ${latestMut.new_owner}` : null, property?.owner_name ? `Snapshot owner: ${property.owner_name}` : null].filter(Boolean));

  }


  const statusActive = value => {

    const v = norm(value);

    return Boolean(v) && !['none', 'no', 'clear', 'nil', 'n/a', 'na', 'false', '0', 'not applicable', 'not mortgaged', 'no mortgage'].includes(v);

  };

  const activeMortgages = mort.filter(m => !/discharged|closed|released|cancelled|satisfied/i.test(String(m?.status || m?.mortgage_status || m?.discharge_status || '')));

  if (statusActive(property?.mortgage_status) || activeMortgages.length) {

    addFinding('mortgage', 20, 'HIGH', 'Mortgage or encumbrance requires review', `Mortgage status or mortgage records are present. Verify whether each mortgage is active or discharged.`, [property?.mortgage_status ? `Property status: ${property.mortgage_status}` : '', ...activeMortgages.slice(0, 5).map(m => `Mortgage record: ${m.mortgage_id || m.record_id || m.id || 'record'}`)].filter(Boolean));

  }

  if (statusActive(property?.court_status)) addFinding('court', 25, 'HIGH', 'Court status requires verification', `Recorded court status: ${property.court_status}. Check the current case/order with official records.`, [`Court status: ${property.court_status}`]);

  if (statusActive(property?.restriction_status)) addFinding('restriction', 20, 'HIGH', 'Recorded restriction requires review', `Recorded restriction: ${property.restriction_status}. Verify its scope and whether it remains active.`, [`Restriction: ${property.restriction_status}`]);


  const duplicates = props.filter(p => p?.property_id !== property?.property_id && survey(p?.survey_number) && survey(p?.survey_number) === survey(property?.survey_number) && norm(p?.village) === norm(property?.village) && norm(p?.hissa) === norm(property?.hissa) && norm(p?.owner_name) && norm(property?.owner_name) && norm(p?.owner_name) !== norm(property?.owner_name));

  if (duplicates.length) addFinding('duplicate-parcel', Math.min(25, 10 + duplicates.length * 3), 'HIGH', 'Possible duplicate parcel record', `${duplicates.length} other record(s) share survey, village and hissa but show a different owner. These may be valid separate records; verify parcel boundaries and source records.`, duplicates.slice(0, 5).map(p => `${p.property_id}: ${p.owner_name}`));


  const comparison = documentAnalysis?.comparison || {};

  const uploadedSurvey = comparison.uploaded_survey;

  const databaseSurvey = comparison.database_survey || property?.survey_number;

  const uploadedBuyer = comparison.uploaded_buyer;

  const mutationOwnerForDoc = comparison.mutation_owner;

  const surveyMismatch = Boolean(survey(uploadedSurvey) && survey(databaseSurvey) && survey(uploadedSurvey) !== survey(databaseSurvey));

  const docOwnerMismatch = Boolean(comparison.ownership_conflict || (norm(uploadedBuyer) && norm(mutationOwnerForDoc) && norm(uploadedBuyer) !== norm(mutationOwnerForDoc)));

  if (surveyMismatch || docOwnerMismatch) {

    const points = surveyMismatch && docOwnerMismatch ? 35 : surveyMismatch ? 25 : 25;

    addFinding('uploaded-document-conflict', points, 'HIGH', 'Uploaded document conflicts with property records', [surveyMismatch ? `Uploaded survey (${uploadedSurvey}) differs from selected property survey (${databaseSurvey})` : null, docOwnerMismatch ? `Uploaded buyer/owner (${uploadedBuyer || 'not extracted'}) differs from mutation owner (${mutationOwnerForDoc || 'not available'})` : null].filter(Boolean).join('. ') + '. Check the original document and official records.', [uploadedSurvey ? `Uploaded survey: ${uploadedSurvey}` : null, databaseSurvey ? `Database survey: ${databaseSurvey}` : null, uploadedBuyer ? `Uploaded buyer: ${uploadedBuyer}` : null, mutationOwnerForDoc ? `Mutation owner: ${mutationOwnerForDoc}` : null].filter(Boolean));

  } else if (documentAnalysis && documentAnalysis.text_extracted === false) {

    addFinding('unreadable-document', 0, 'MEDIUM', 'Uploaded document could not be read', 'No reliable text was extracted. The risk score is unchanged because an unreadable file alone does not prove a conflict.', [documentAnalysis.filename || 'Uploaded document']);

  }


  // No penalty just for searching, uploading a clean document, or having

  // incomplete data. Missing evidence is displayed as coverage, not risk.

  score = Math.min(100, Math.round(score));

  const level = score >= 70 ? 'CRITICAL' : score >= 45 ? 'HIGH' : score >= 20 ? 'MEDIUM' : 'LOW';

  const required = [property?.property_id, property?.survey_number, property?.village, property?.owner_name];

  const completeness = Math.round(required.filter(v => String(v ?? '').trim()).length / required.length * 100);

  const coverage = [regs.length > 0, muts.length > 0, mort.length > 0].filter(Boolean).length;

  const evidenceConfidence = completeness === 100 && regs.length && muts.length ? (coverage >= 2 ? 'BETTER COVERAGE' : 'PARTIAL') : 'LIMITED';

  return { score, level, findings, duplicates, dataCompleteness: completeness, evidenceConfidence };

}


/* ---------------------------------------------------------


   MAIN APPLICATION


--------------------------------------------------------- */


function App() {


  const [user, setUser] = useState(() => {


    try {


      return JSON.parse(


        localStorage.getItem('cybermatrix_user')


      );


    } catch {


      return null;


    }


  });


  const [properties, setProperties] = useState([]);


  const [selectedId, setSelectedId] = useState('');


  const [detail, setDetail] = useState(null);


  const [search, setSearch] = useState('');


  const [searchInput, setSearchInput] = useState('');


  const [loading, setLoading] = useState(true);


  const [detailLoading, setDetailLoading] = useState(false);


  const [error, setError] = useState('');


  const [activePage, setActivePage] =


    useState('dashboard');


  const [showUpload, setShowUpload] =


    useState(false);


  const [registrationFile, setRegistrationFile] =


    useState(null);


  const [mortgageFile, setMortgageFile] =


    useState(null);


  const [uploadMessage, setUploadMessage] =


    useState('');


  const [analysisResult, setAnalysisResult] =


    useState(null);


  const [analysisLoading, setAnalysisLoading] =


    useState(false);


  const [visitMessage, setVisitMessage] =


    useState('');


  /* -------------------------------------------------------


     LOAD 279 REAL PROPERTIES


  ------------------------------------------------------- */


  useEffect(() => {


    if (!user) return;


    loadProperties();


  }, [user]);


  async function loadProperties() {


    try {


      setLoading(true);


      setError('');


      const response =


        await http.get('/properties');


      const data = Array.isArray(response.data)


        ? response.data


        : response.data?.properties || [];


      setProperties(data);


      if (


        data.length > 0 &&


        !selectedId


      ) {


        setSelectedId(data[0].property_id);


      }


    } catch (err) {


      console.error(err);


      setError(


        'CyberMatrix backend is unavailable. Start FastAPI on port 8000.'


      );


    } finally {


      setLoading(false);


    }


  }


  /* -------------------------------------------------------


     LOAD SELECTED PROPERTY


  ------------------------------------------------------- */


  useEffect(() => {

    if (!selectedId || !user) return undefined;


    let cancelled = false;


    async function fetchSelectedProperty() {

      // Clear the previous property's information immediately.

      setDetail(null);

      setDetailLoading(true);

      setError('');

      setAnalysisResult(null);

      setRegistrationFile(null);

      setMortgageFile(null);

      setUploadMessage('');

      setVisitMessage('');

      setShowUpload(false);


      try {

        const response = await http.get(`/properties/${selectedId}`);

        if (!cancelled) setDetail(response.data);

      } catch (err) {

        console.error('Property loading failed:', err);

        if (!cancelled) {

          setError(`Unable to load property ${selectedId}. Please try again.`);

        }

      } finally {

        if (!cancelled) setDetailLoading(false);

      }

    }


    fetchSelectedProperty();

    return () => {

      cancelled = true;

    };

  }, [selectedId, user]);


  /* -------------------------------------------------------


     SEARCH


  ------------------------------------------------------- */


  function performSearch(event) {


    event?.preventDefault();


    setSearch(searchInput.trim());


    setActivePage('search');


  }


  const filteredProperties = useMemo(() => {


    const query =


      search.trim().toLowerCase();


    if (!query) {


      return properties;


    }


    return properties.filter((p) =>


      [


        p.property_id,


        p.owner_name,


        p.survey_number,


        p.hissa,


        p.village,


        p.taluk,


        p.hobli,


        p.district,


      ]


        .filter(Boolean)


        .some((value) =>


          String(value)


            .toLowerCase()


            .includes(query)


        )


    );


  }, [properties, search]);


  /* -------------------------------------------------------


     RISK


  ------------------------------------------------------- */


  const risk = useMemo(() => {


    if (!detail?.property) {


      return {


        score: 0,


        level: 'LOW',


        findings: [],


        duplicates: [],

        dataCompleteness: 0,

        evidenceConfidence: 'LIMITED',


      };


    }


    return calculateRisk(


      detail.property,


      detail.registrations || [],


      detail.mutations || [],


      detail.mortgages || [],


      properties,

      analysisResult


    );


  }, [detail, properties, analysisResult]);


  /* -------------------------------------------------------


     LOGOUT


  ------------------------------------------------------- */


  function logout() {


    localStorage.removeItem(


      'cybermatrix_user'


    );


    setUser(null);


  }


  /* -------------------------------------------------------


     FILE UPLOAD


  ------------------------------------------------------- */


  async function handleUpload() {


  if (!registrationFile && !mortgageFile) {


    setUploadMessage(


      'Please select a registration or mortgage document.'


    );


    return;


  }


  const file =


    registrationFile || mortgageFile;


  try {


    setAnalysisLoading(true);


    setAnalysisResult(null);


    setUploadMessage('');


    const formData = new FormData();


    formData.append('file', file);


    const response = await http.post(


      '/documents/analyze',


      formData,


      {


        headers: {


          'Content-Type': 'multipart/form-data',


        },


      }


    );


    const result = response.data;


    /*


     * ------------------------------------------


     * DOCUMENT EVIDENCE


     * ------------------------------------------


     */


    const surveyEvidence =


      result?.evidence?.survey || [];


    const ownershipEvidence =


      result?.evidence?.ownership || [];


    const surveyText = surveyEvidence


      .map((item) => item.text)


      .join(' ');


    const ownershipText = ownershipEvidence


      .map((item) => item.text)


      .join(' ');


    /*


     * ------------------------------------------


     * EXTRACT SURVEY NUMBER


     * ------------------------------------------


     */


    const uploadedSurveyMatch =


      surveyText.match(


        /\b(?:survey(?:\s+number)?|sy\s*no?\.?)\s*[:\-]?\s*([0-9]+\/[0-9]+(?:\/[0-9]+)?)?/i


      );


    const uploadedSurvey =


      uploadedSurveyMatch


        ? uploadedSurveyMatch[1]


        : null;


    /*


     * ------------------------------------------


     * EXTRACT BUYER


     * ------------------------------------------


     */


    const buyerMatch =


      ownershipText.match(


        /\bbuyer\s*[:\-]?\s*([A-Za-z_][A-Za-z0-9_-]*)/i


      );


    const uploadedBuyer =


      buyerMatch


        ? buyerMatch[1]


        : null;


    /*


     * ------------------------------------------


     * CYBERMATRIX DATABASE RECORD


     * ------------------------------------------


     *


     * IMPORTANT:


     * The selected property is stored in `detail`,


     * not `selectedProperty`.


     */


    const databaseProperty =


      detail?.property || null;


    const databaseSurvey =


      databaseProperty?.survey_number || null;


    const mutationOwner =


      detail?.mutations?.length


        ? detail.mutations[


            detail.mutations.length - 1


          ]?.new_owner


        : null;


    /*


     * ------------------------------------------


     * COMPARE DOCUMENT VS DATABASE


     * ------------------------------------------


     */


    const sameSurvey =


      uploadedSurvey &&


      databaseSurvey &&


      String(uploadedSurvey).trim().toLowerCase() ===


        String(databaseSurvey).trim().toLowerCase();


    const ownershipConflict =


      Boolean(


        sameSurvey &&


        uploadedBuyer &&


        mutationOwner &&


        uploadedBuyer.toLowerCase() !==


          mutationOwner.toLowerCase()


      );


    /*


     * ------------------------------------------


     * STORE COMPLETE ANALYSIS


     * ------------------------------------------


     */


    setAnalysisResult({


      ...result,


      comparison: {


        uploaded_survey:


          uploadedSurvey,


        uploaded_buyer:


          uploadedBuyer,


        database_survey:


          databaseSurvey,


        mutation_owner:


          mutationOwner,


        ownership_conflict:


          ownershipConflict,


      },


    });


    setUploadMessage(


      ownershipConflict


        ? 'Ownership conflict detected. Verification required.'


        : 'Document analyzed successfully.'


    );


  } catch (error) {


    console.error(error);


    setUploadMessage(


      error?.response?.data?.detail ||


      'Document analysis failed.'


    );


  } finally {


    setAnalysisLoading(false);


  }


}  /* -------------------------------------------------------


     LAND VISIT


  ------------------------------------------------------- */


  async function scheduleVisit() {
    const property = detail?.property;
    const email = String(user?.email || '').trim().toLowerCase();

    if (!property?.property_id) {
      setVisitMessage('Please select a property first.');
      return;
    }
    if (!email || !email.includes('@')) {
      setVisitMessage('Please sign in with your email address.');
      return;
    }

    // Six calendar months later, preserving local time.
    const now = new Date();
    const targetMonth = now.getMonth() + 6;
    const targetYear = now.getFullYear() + Math.floor(targetMonth / 12);
    const monthIndex = targetMonth % 12;
    const lastDay = new Date(targetYear, monthIndex + 1, 0).getDate();
    const next = new Date(now);
    next.setDate(1);
    next.setFullYear(targetYear, monthIndex, Math.min(now.getDate(), lastDay));

    try {
      await http.post('/reminders', {
        user_email: email,
        property_id: property.property_id,
        scheduled_at: next.toISOString(),
        timezone_name: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
      });
      setVisitMessage(`Reminder saved for ${formatDate(next)}. It is linked to ${email}.`);
    } catch (error) {
      console.error('Reminder error:', error);
      setVisitMessage(
        error?.response?.data?.detail ||
        'Could not save reminder. Check that the backend is running and reminder API is installed.'
      );
    }
  }


  if (!user) {


    return (


      <Login onLogin={setUser} />


    );


  }


  const property =


    detail?.property;


  const registrations =


    detail?.registrations || [];


  const mutations =


    detail?.mutations || [];


  const mortgages =


    detail?.mortgages || [];


  const highRiskCount =


    properties.filter(


      (p) =>


        p.mortgage_status !== 'none' ||


        p.court_status !== 'none' ||


        p.restriction_status !== 'none'


    ).length;


  return (


    <div className="app">


      {/* ---------------------------------------------------


          TOP NAV


      --------------------------------------------------- */}


      <header className="topbar">


        <div className="brand-area">


          <div className="brand">


            CYBERMATRIX


          </div>


          <div className="subtitle">


            Land Ownership Intelligence & Protection


          </div>


        </div>


        <div className="top-actions">


          <div className="live-status">


            <span className="status-dot" />


            LIVE BACKEND


          </div>


          <button


            className="logout-button"


            onClick={logout}


          >


            LOGOUT


          </button>


        </div>


      </header>


      {/* ---------------------------------------------------


          NAVIGATION


      --------------------------------------------------- */}


      <nav className="main-nav">


        <button


          className={


            activePage === 'dashboard'


              ? 'nav-active'


              : ''


          }


          onClick={() =>


            setActivePage('dashboard')


          }


        >


          DASHBOARD


        </button>


        <button


          className={


            activePage === 'search'


              ? 'nav-active'


              : ''


          }


          onClick={() =>


            setActivePage('search')


          }


        >


          SEARCH LAND


        </button>


        <button


          className={


            activePage === 'alerts'


              ? 'nav-active'


              : ''


          }


          onClick={() =>


            setActivePage('alerts')


          }


        >


          ALERTS


        </button>


        <button


          className={


            activePage === 'protection'


              ? 'nav-active'


              : ''


          }


          onClick={() =>


            setActivePage('protection')


          }


        >


          LAND PROTECTION


        </button>


      </nav>


      {/* ---------------------------------------------------


          MAIN


      --------------------------------------------------- */}


      <main className="content">


        {error && (


          <div className="error-banner">


            {error}


          </div>


        )}


        {/* ================================================


            DASHBOARD


        ================================================= */}


        {activePage === 'dashboard' && (


          <>


            <section className="welcome-section">


              <div>


                <div className="eyebrow">


                  OWNER PROTECTION CENTER


                </div>


                <h1>


                  Welcome to CyberMatrix


                </h1>


                <p>


                  Detect land-record conflicts before


                  they become ownership problems.


                </p>


              </div>


              <div className="user-chip">


                {user.email}


              </div>


            </section>


            {/* SEARCH */}


            <section className="search-hero">


              <div className="eyebrow">


                SEARCH YOUR LAND


              </div>


              <h2>


                Check a Survey Number


              </h2>


              <form


                className="big-search"


                onSubmit={performSearch}


              >


                <input


                  value={searchInput}


                  onChange={(e) =>


                    setSearchInput(


                      e.target.value


                    )


                  }


                  placeholder="Survey number, property ID, owner or village"


                />


                <button type="submit">


                  SEARCH


                </button>


              </form>


              <div className="search-example">


                Try: <strong>40/1</strong> or{' '}


                <strong>PROP-00001</strong>


              </div>


            </section>


            {/* STATS */}


            <section className="stats-grid">


              <div className="stat-card">


                <span>


                  REGISTERED PROPERTIES


                </span>


                <strong>


                  {properties.length}


                </strong>


                <small>


                  Real backend records


                </small>


              </div>


              <div className="stat-card">


                <span>


                  PROPERTIES REQUIRING REVIEW


                </span>


                <strong>


                  {highRiskCount}


                </strong>


                <small>


                  Status-based screening


                </small>


              </div>


              <div className="stat-card">


                <span>


                  REGISTRATION RECORDS


                </span>


                <strong>


                  {registrations.length}


                </strong>


                <small>


                  Selected property


                </small>


              </div>


              <div className="stat-card">


                <span>


                  MUTATION RECORDS


                </span>


                <strong>


                  {mutations.length}


                </strong>


                <small>


                  Selected property


                </small>


              </div>


            </section>


            {detailLoading ? (

              <div className="empty">Loading the selected property's records...</div>

            ) : property ? (


              <PropertyInvestigation


                property={property}


                registrations={registrations}


                mutations={mutations}


                mortgages={mortgages}


                risk={risk}


                showUpload={showUpload}


                setShowUpload={setShowUpload}


                registrationFile={registrationFile}


                setRegistrationFile={setRegistrationFile}


                mortgageFile={mortgageFile}


                setMortgageFile={setMortgageFile}


                uploadMessage={uploadMessage}


                handleUpload={handleUpload}


                  analysisResult={analysisResult}


  analysisLoading={analysisLoading}


                visitMessage={visitMessage}


                scheduleVisit={scheduleVisit}


              />


            ) : (

              <div className="empty">Select a property to view its records.</div>

            )}


          </>


        )}


        {/* ================================================


            SEARCH


        ================================================= */}


        {activePage === 'search' && (


          <section>


            <div className="page-title">


              <div>


                <div className="eyebrow">


                  LAND SEARCH


                </div>


                <h1>


                  Find Property


                </h1>


              </div>


              <span className="record-count">


                {filteredProperties.length} results


              </span>


            </div>


            <form


              className="big-search"


              onSubmit={performSearch}


            >


              <input


                value={searchInput}


                onChange={(e) =>


                  setSearchInput(


                    e.target.value


                  )


                }


                placeholder="Survey number / Property ID / Owner / Village"


              />


              <button>


                SEARCH


              </button>


            </form>


            <div className="search-results">


              {loading && (


                <div className="empty">


                  Loading 279 real property records...


                </div>


              )}


              {!loading &&


                filteredProperties.length === 0 && (


                  <div className="empty">


                    No matching land record found.


                  </div>


                )}


              {filteredProperties


                .slice(0, 50)


                .map((p) => (


                  <button


                    className={


                      selectedId === p.property_id


                        ? 'result-card selected-result'


                        : 'result-card'


                    }


                    key={p.property_id}


                    onClick={() => {


                      setSelectedId(


                        p.property_id


                      );


                      setActivePage(


                        'dashboard'


                      );


                    }}


                  >


                    <div>


                      <strong>


                        {p.property_id}


                      </strong>


                      <span>


                        {p.owner_name}


                      </span>


                    </div>


                    <div>


                      <strong>


                        Survey {p.survey_number}


                      </strong>


                      <span>


                        {p.village} — {p.taluk}


                      </span>


                    </div>


                    <div className="result-arrow">


                      ?


                    </div>


                  </button>


                ))}


            </div>


          </section>


        )}


        {/* ================================================


            ALERTS


        ================================================= */}


        {activePage === 'alerts' && (


          <section>


            <div className="page-title">


              <div>


                <div className="eyebrow">


                  OWNER ALERT CENTER


                </div>


                <h1>


                  Land Risk Alerts


                </h1>


              </div>


            </div>


            <div className="alert-card critical-alert">


              <div className="alert-icon">


                !


              </div>


              <div>


                <div className="alert-label">


                  HIGH PRIORITY


                </div>


                <h2>


                  Ownership verification required


                </h2>


                <p>


                  CyberMatrix detected a possible


                  ownership conflict for the selected


                  property.


                </p>


                {property && (


                  <div className="alert-detail">


                    Survey {property.survey_number}


                    {' — '}


                    {property.village}


                  </div>


                )}


              </div>


            </div>


            <div className="notification-panel">


              <div className="eyebrow">


                NOTIFICATION WORKFLOW


              </div>


              <h2>


                Protect affected owners


              </h2>


              <p>


                When a conflicting ownership record is


                detected, CyberMatrix identifies the


                affected owners and prepares an alert


                containing the survey number, conflict


                and evidence.


              </p>


              <div className="notification-preview">


                <div className="notification-title">


                  CYBERMATRIX WARNING


                </div>


                <div>


                  Your land record requires


                  verification.


                </div>


                <div className="notification-property">


                  Survey:{' '}


                  {property?.survey_number || '40/1'}


                </div>


                <div>


                  A conflicting ownership record was


                  detected.


                </div>


              </div>


              <div className="small-note">


                In this MVP the warning is shown inside


                CyberMatrix. SMS / WhatsApp delivery can


                be connected to a messaging provider later.


              </div>


            </div>


          </section>


        )}


        {/* ================================================


            LAND PROTECTION


        ================================================= */}


        {activePage === 'protection' && (


          <section>


            <div className="page-title">


              <div>


                <div className="eyebrow">


                  PREVENTIVE LAND SECURITY


                </div>


                <h1>


                  Protect Your Property


                </h1>


              </div>


            </div>


            <div className="protection-grid">


              <div className="protection-main">


                <div className="protection-icon">


                  ??


                </div>


                <h2>


                  Don't leave your land unprotected.


                </h2>


                <p>


                  CyberMatrix recommends periodic


                  physical verification of vacant or


                  rarely visited land.


                </p>


                <div className="check-list">


                  <div>


                    ? Verify boundary markers


                  </div>


                  <div>


                    ? Check for unauthorized occupation


                  </div>


                  <div>


                    ? Check for unauthorized construction


                  </div>


                  <div>


                    ? Photograph the property


                  </div>


                  <div>


                    ? Verify neighbouring activity


                  </div>


                  <div>


                    ? Keep ownership documents safely stored


                  </div>


                </div>


                <button


                  className="primary-button protection-button"


                  onClick={scheduleVisit}


                >


                  SET 6-MONTH LAND VISIT


                </button>


                {visitMessage && (


                  <div className="success-message">


                    {visitMessage}


                  </div>


                )}


              </div>


              <div className="protection-side">


                <div className="eyebrow">


                  RECOMMENDED SCHEDULE


                </div>


                <div className="visit-number">


                  6


                </div>


                <div className="visit-unit">


                  MONTHS


                </div>


                <p>


                  Recommended maximum interval


                  between physical verification visits.


                </p>


                <div className="protection-warning">


                  ? If your land is vacant for years,


                  regular visits help you identify


                  unauthorized occupation or


                  construction earlier.


                </div>


              </div>


            </div>


          </section>


        )}


      </main>


    </div>


  );


}


/* ---------------------------------------------------------


   PROPERTY INVESTIGATION


--------------------------------------------------------- */


function PropertyInvestigation({


  property,


  registrations,


  mutations,


  mortgages,


  risk,


  showUpload,


  setShowUpload,


  registrationFile,


  setRegistrationFile,


  mortgageFile,


  setMortgageFile,


  uploadMessage,


  handleUpload,


    analysisResult,


  analysisLoading,


  visitMessage,


  scheduleVisit,


}) {


  return (


    <section className="investigation">


      {/* HEADER */}


      <div className="investigation-header">


        <div>


          <div className="eyebrow">


            PROPERTY INVESTIGATION


          </div>


          <h2>


            {property.property_id}


          </h2>


          <p>


            {property.village},{' '}


            {property.taluk},{' '}


            {property.district}


          </p>


        </div>


        <div


          className={`risk-pill risk-${risk.level.toLowerCase()}`}


        >


          {risk.level}


          <span>


            {risk.score}/100


          </span>


        </div>


      </div>


      {/* RISK */}


      <div className="risk-panel">


        <div className="risk-score">


          <div className="score-number">


            {risk.score}


          </div>


          <div className="score-label">


            RISK SCORE


          </div>


        </div>


        <div className="risk-bar-area">


          <div className="risk-bar">


            <div


              className={`risk-fill risk-fill-${risk.level.toLowerCase()}`}


              style={{


                width: `${Math.max(


                  5,


                  risk.score


                )}%`,


              }}


            />


          </div>


          <div className="risk-scale">


            <span>LOW</span>


            <span>MEDIUM</span>


            <span>HIGH</span>


            <span>CRITICAL</span>


          </div>


        </div>


        <div className="risk-summary">


          {risk.findings.length === 0


            ? 'No major conflict detected in the available records.'


            : `${risk.findings.length} verification finding(s) require attention.`}


        </div>


        <div className="risk-evidence-metrics">

          <div className="risk-evidence-metric">

            <span>CORE DATA COMPLETENESS</span>

            <strong>{risk.dataCompleteness ?? 0}%</strong>

          </div>

          <div className="risk-evidence-metric">

            <span>RECORD COVERAGE</span>

            <strong>{risk.evidenceConfidence || 'LIMITED'}</strong>

          </div>

          <p className="risk-evidence-note">Completeness describes filled core fields; it is not a probability that records are correct.</p>

        </div>


      </div>


      {/* PROPERTY INFO */}


      <div className="property-grid">


        <InfoCard


          label="REGISTERED OWNER"


          value={property.owner_name}


        />


        <InfoCard


          label="SURVEY / Hissa"


          value={`${property.survey_number || '—'} / ${


            property.hissa || '—'


          }`}


        />


        <InfoCard


          label="EXTENT"


          value={`${property.extent_acres ?? '—'} acres`}


        />


        <InfoCard


          label="BASELINE"


          value={formatDate(


            property.baseline_date


          )}


        />


        <InfoCard


          label="MORTGAGE"


          value={


            property.mortgage_status || 'none'


          }


        />


        <InfoCard


          label="COURT STATUS"


          value={


            property.court_status || 'none'


          }


        />


        <InfoCard


          label="RESTRICTION"


          value={


            property.restriction_status ||


            'none'


          }


        />


        <InfoCard


          label="LOCATION"


          value={`${property.village || '—'}, ${


            property.taluk || '—'


          }`}


        />


      </div>


      {/* FINDINGS */}


      <div className="section-panel">


        <div className="section-heading">


          <div>


            <div className="eyebrow">


              CYBERMATRIX ANALYSIS


            </div>


            <h2>


              Why is this land at risk?


            </h2>


          </div>


        </div>


        {risk.findings.length === 0 && (


          <div className="safe-message">


            ? No high-risk conflict was detected


            from the available land records.


          </div>


        )}


        {risk.findings.map(


          (finding, index) => (


            <div


              className="finding-card"


              key={index}


            >


              <div


                className={`finding-severity finding-${finding.severity.toLowerCase()}`}


              >


                {finding.severity}


              </div>


              <div className="finding-body">


                <h3>


                  {finding.title}


                </h3>


                <p>


                  {finding.detail}


                </p>


                <div className="evidence-tags">


                  {finding.evidence.map(


                    (item, i) => (


                      <span key={i}>


                        {item}


                      </span>


                    )


                  )}


                </div>


              </div>


            </div>


          )


        )}


      </div>


      {/* OWNERSHIP CONFLICT */}


      {risk.findings.some(


        (f) =>


          f.title.includes('Ownership')


      ) && (


        <div className="section-panel conflict-panel">


          <div className="eyebrow">


            OWNERSHIP CONFLICT


          </div>


          <h2>


            Same land — conflicting owner records


          </h2>


          <div className="comparison">


            <div className="record-box">


              <span>


                REGISTRATION RECORD


              </span>


              {registrations.map(


                (r) => (


                  <div key={r.document_number}>


                    <strong>


                      {r.seller || 'Unknown'}


                      {' ? '}


                      {r.buyer || 'Unknown'}


                    </strong>


                    <small>


                      {r.document_number}


                      {' — '}


                      {formatDate(


                        r.transaction_date


                      )}


                    </small>


                    <small>


                      Survey:{' '}


                      {property.survey_number}


                    </small>


                  </div>


                )


              )}


            </div>


            <div className="conflict-arrow">


              VS


            </div>


            <div className="record-box">


              <span>


                MUTATION RECORD


              </span>


              {mutations.map(


                (m) => (


                  <div key={m.mutation_number}>


                    <strong>


                      {m.previous_owner ||


                        'Unknown'}


                      {' ? '}


                      {m.new_owner ||


                        'Unknown'}


                    </strong>


                    <small>


                      {m.mutation_number}


                      {' — '}


                      {formatDate(


                        m.mutation_date


                      )}


                    </small>


                    <small>


                      Type:{' '}


                      {m.mutation_type ||


                        'Mutation'}


                    </small>


                  </div>


                )


              )}


            </div>


          </div>


          <div className="warning-explanation">


            <strong>


              ? Verification required


            </strong>


            <p>


              These records refer to the same


              property but identify different


              ownership outcomes. This should be


              verified against the original


              registration and mutation documents.


            </p>


          </div>


        </div>


      )}


      {/* UPLOAD */}


      <div className="section-panel">


        <div className="section-heading">


          <div>


            <div className="eyebrow">


              DOCUMENT VERIFICATION


            </div>


            <h2>


              Upload land documents


            </h2>


            <p>


              Compare your original records with


              CyberMatrix property data.


            </p>


          </div>


          <button


            className="secondary-button"


            onClick={() =>


              setShowUpload(!showUpload)


            }


          >


            {showUpload


              ? 'CLOSE'


              : 'UPLOAD DOCUMENTS'}


          </button>


        </div>


        {showUpload && (


          <div className="upload-area">


            <div className="upload-box">


              <label>


                REGISTRATION DOCUMENT


              </label>


              <input


                type="file"


                accept=".pdf,.jpg,.jpeg,.png,.txt"


                onChange={(e) =>


                  setRegistrationFile(


                    e.target.files?.[0] ||


                      null


                  )


                }


              />


              {registrationFile && (


                <div className="file-selected">


                  ? {registrationFile.name}


                </div>


              )}


            </div>


            <div className="upload-box">


              <label>


                MORTGAGE / ENCUMBRANCE DOCUMENT


              </label>


              <input


                type="file"


                accept=".pdf,.jpg,.jpeg,.png,.txt"


                onChange={(e) =>


                  setMortgageFile(


                    e.target.files?.[0] ||


                      null


                  )


                }


              />


              {mortgageFile && (


                <div className="file-selected">


                  ? {mortgageFile.name}


                </div>


              )}


            </div>


            <button


              className="primary-button"


              onClick={handleUpload}


            >


              ANALYZE DOCUMENTS


            </button>


            {analysisLoading && (


  <div className="analysis-loading">


    Analyzing land document and checking


    CyberMatrix records...


  </div>


)}


{uploadMessage && (


  <div


    className={


      analysisResult?.comparison?.ownership_conflict


        ? "analysis-warning-message"


        : "success-message"


    }


  >


    {uploadMessage}


  </div>


)}


{analysisResult && (


  <div className="document-analysis">


    <div className="analysis-header">


      <div>


        <div className="eyebrow">


          DOCUMENT INTELLIGENCE


        </div>


        <h3>


          {analysisResult.filename}


        </h3>


      </div>


      <div


        className={


          analysisResult.comparison?.ownership_conflict


            ? "analysis-status conflict"


            : "analysis-status"


        }


      >


        {analysisResult.comparison?.ownership_conflict


          ? "CONFLICT DETECTED"


          : "ANALYZED"}


      </div>


    </div>


    <div className="document-meta">


      <div>


        <span>DOCUMENT TYPE</span>


        <strong>


          {analysisResult.document_type || "Document"}


        </strong>


      </div>


      <div>


        <span>TEXT EXTRACTED</span>


        <strong>


          {analysisResult.text_extracted


            ? "YES"


            : "NO"}


        </strong>


      </div>


      <div>


        <span>TEXT LENGTH</span>


        <strong>


          {analysisResult.text_length || 0}


        </strong>


      </div>


    </div>


    {analysisResult.comparison?.ownership_conflict && (


      <div className="document-conflict-alert">


        <div className="document-conflict-title">


          ⚠ OWNERSHIP CONFLICT DETECTED


        </div>


        <div className="document-conflict-risk">


          HIGH RISK


        </div>


        <p className="document-conflict-summary">


          The uploaded registration refers to the same


          survey number as the CyberMatrix property, but


          identifies a different ownership outcome.


        </p>


        <div className="document-conflict-grid">


          <div>


            <span>UPLOADED REGISTRATION</span>


            <strong>


              Survey:{" "}


              {analysisResult.comparison.uploaded_survey}


            </strong>


            <strong>


              Buyer:{" "}


              {analysisResult.comparison.uploaded_buyer}


            </strong>


          </div>


          <div>


            <span>CYBERMATRIX MUTATION</span>


            <strong>


              Survey:{" "}


              {analysisResult.comparison.database_survey}


            </strong>


            <strong>


              New owner:{" "}


              {analysisResult.comparison.mutation_owner}


            </strong>


          </div>


        </div>


        <div className="document-conflict-message">


          <strong>


            Verification required


          </strong>


          <p>


            The uploaded document identifies{" "}


            {analysisResult.comparison.uploaded_buyer},


            while the mutation record identifies{" "}


            {analysisResult.comparison.mutation_owner}.


            These records should be verified against the


            original land documents.


          </p>


        </div>


      </div>


    )}


    <EvidenceSection


      title="SURVEY EVIDENCE"


      items={


        analysisResult.evidence?.survey


      }


    />


    <EvidenceSection


      title="OWNERSHIP EVIDENCE"


      items={


        analysisResult.evidence?.ownership


      }


    />


    <EvidenceSection


      title="MORTGAGE / ENCUMBRANCE EVIDENCE"


      items={


        analysisResult.evidence?.mortgage


      }


    />


  </div>


)}


<div className="small-note">


  CyberMatrix extracts document evidence and compares


  it against the selected property record.


</div>


          </div>


        )}


      </div>


      {/* HISTORY */}


      <div className="section-panel">


        <div className="section-heading">


          <div>


            <div className="eyebrow">


              TRANSACTION HISTORY


            </div>


            <h2>


              Registration & mutation records


            </h2>


          </div>


        </div>


        <div className="history-grid">


          <div>


            <h3>


              Registrations


            </h3>


            {registrations.length === 0 && (


              <div className="empty">


                No registration records.


              </div>


            )}


            {registrations.map(


              (r) => (


                <div


                  className="history-row"


                  key={r.document_number}


                >


                  <div>


                    <strong>


                      {r.seller || 'Unknown'}


                      {' ? '}


                      {r.buyer || 'Unknown'}


                    </strong>


                    <span>


                      {r.document_number}


                    </span>


                  </div>


                  <time>


                    {formatDate(


                      r.transaction_date


                    )}


                  </time>


                </div>


              )


            )}


          </div>


          <div>


            <h3>


              Mutations


            </h3>


            {mutations.length === 0 && (


              <div className="empty">


                No mutation records.


              </div>


            )}


            {mutations.map(


              (m) => (


                <div


                  className="history-row"


                  key={m.mutation_number}


                >


                  <div>


                    <strong>


                      {m.previous_owner ||


                        'Unknown'}


                      {' ? '}


                      {m.new_owner ||


                        'Unknown'}


                    </strong>


                    <span>


                      {m.mutation_number}


                    </span>


                  </div>


                  <time>


                    {formatDate(


                      m.mutation_date


                    )}


                  </time>


                </div>


              )


            )}


          </div>


        </div>


      </div>


      {/* PROTECTION */}


      <div className="protection-banner">


        <div>


          <div className="eyebrow">


            LAND PROTECTION


          </div>


          <h2>


            Protect vacant land before someone


            else occupies it.


          </h2>


          <p>


            CyberMatrix recommends checking vacant


            property every 6 months and recording


            physical verification.


          </p>


        </div>


        <button


          className="primary-button"


          onClick={scheduleVisit}


        >


          SET 6-MONTH REMINDER


        </button>


      </div>


      {visitMessage && (


        <div className="success-message">


          {visitMessage}


        </div>


      )}


    </section>


  );


}


/* ---------------------------------------------------------


   INFO CARD


--------------------------------------------------------- */


function EvidenceSection({ title, items }) {


  return (


    <div className="evidence-section">


      <div className="evidence-section-title">


        {title}


      </div>


      {(!items || items.length === 0) ? (


        <div className="no-evidence">


          No matching evidence line found.


        </div>


      ) : (


        <div className="evidence-lines">


          {items.map((item, index) => (


            <div


              className="evidence-line"


              key={index}


            >


              <div className="line-number">


                LINE {item.line_number}


              </div>


              <div className="line-text">


                <span className="problem-marker">


                  !


                </span>


                {item.text}


              </div>


            </div>


          ))}


        </div>


      )}


    </div>


  );


}


function InfoCard({ label, value }) {


  return (


    <div className="info-card">


      <span>


        {label}


      </span>


      <strong>


        {value || '—'}


      </strong>


    </div>


  );


}


export default App;
