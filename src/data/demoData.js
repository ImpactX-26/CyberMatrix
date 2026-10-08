// ALL DATA IN THIS FILE IS SYNTHETIC. No real people, addresses or records.

export const MAIN_ID = 'PROP-0491';

export const STATE_META = {
  clear: { label: 'No material changes detected', short: 'No Material Changes', priority: 'LOW', tone: 'ok' },
  change: { label: 'Change detected', short: 'Change Detected', priority: 'MEDIUM', tone: 'warn' },
  investigation: { label: 'Investigation required', short: 'Investigation Required', priority: 'HIGH', tone: 'bad' },
};

// kind: clear | change | investigation  ·  stage = how far the story has progressed (0-3)
const P = (id, survey, village, stage, note, updated, people) => ({
  id, survey, hissa: survey.split('/')[1], village, stage, note, updated,
  people: people || ['Person A', 'Person B', 'Person C', 'Person D'],
  taluk: 'Anekal', hobli: 'Jigani', district: 'Bengaluru', extent: '5 Acres',
});
const names = (n) => {
  const L = 'EFGHIJKLMNOPQRSTUVW';
  const i = (n * 4) % 19;
  return [0, 1, 2, 3].map((k) => `Person ${L[(i + k) % 19]}`);
};

export const PROPERTIES = [
  P(MAIN_ID, '49/1', 'Bannerghatta', 3, 'Registration and mutation mismatch', '14 Jun 2026'),
  P('PROP-0615', '33/2', 'Harohalli', 3, 'Registration and mutation mismatch', '02 Jul 2026', names(1)),
  P('PROP-0773', '71/3', 'Jigani', 2, 'Registration added after recent mortgage', '02 Aug 2026', names(2)),
  P('PROP-0388', '12/4', 'Attibele', 1, 'New mortgage registered', '21 Jul 2026', names(3)),
  P('PROP-0529', '58/1', 'Sarjapura', 1, 'New mortgage registered', '30 May 2026', names(4)),
  P('PROP-0904', '27/2', 'Hennagara', 2, 'Registration added after recent mortgage', '11 Jun 2026', names(5)),
  P('PROP-0822', '62/2', 'Anekal', 0, 'No Material Changes', '20 Jul 2026', names(6)),
  ...[
    ['PROP-0101', '5/1', 'Bagalur'], ['PROP-0117', '8/2', 'Chandapura'], ['PROP-0142', '14/1', 'Huskur'],
    ['PROP-0166', '19/3', 'Kammasandra'], ['PROP-0203', '22/1', 'Muthagadahalli'], ['PROP-0257', '31/2', 'Thattanahalli'],
    ['PROP-0291', '36/1', 'Byagadadenahalli'], ['PROP-0334', '40/2', 'Dommasandra'], ['PROP-0367', '44/1', 'Marsur'],
    ['PROP-0412', '47/3', 'Koppa'], ['PROP-0456', '52/1', 'Samandur'], ['PROP-0577', '66/2', 'Hulimangala'], ['PROP-0640', '70/1', 'Bommasandra'],
  ].map(([id, s, v], i) => P(id, s, v, 0, 'No Material Changes', `${10 + i} May 2026`, names(i + 7))),
];

export const findProperty = (id) => PROPERTIES.find((p) => p.id === id) || null;

export const PORTFOLIO_SERIES = [
  { month: 'Mar', events: 2 }, { month: 'Apr', events: 3 }, { month: 'May', events: 2 },
  { month: 'Jun', events: 5 }, { month: 'Jul', events: 3 }, { month: 'Aug', events: 1 },
];

// ---------- scenario builder ----------
const numFor = (p) => {
  if (p.id === MAIN_ID) return { r0: '001', mrg: 'MRG-2024-014', reg: 'REG-2026-087', mut: 'MUT-2026-044' };
  const n = String(p.id.slice(-3));
  return { r0: String(Number(n) % 90 + 1).padStart(3, '0'), mrg: `MRG-2024-${String(Number(n) % 40 + 1).padStart(3, '0')}`, reg: `REG-2026-${String((Number(n) * 7) % 90 + 10).padStart(3, '0')}`, mut: `MUT-2026-${String((Number(n) * 3) % 80 + 10).padStart(3, '0')}` };
};

export function buildView(p, stage) {
  const [A, B, C, D] = p.people;
  const n = numFor(p);
  const rtcId = `RTC-${p.survey.replace('/', '-')}`;
  const allEvents = [
    { id: `${p.id}-E1`, stage: 0, type: 'SALE_REGISTERED', title: 'Sale registered', date: '12 Jan 2022', summary: `${A} → ${B}`, status: 'normal', field: 'Owner', previous: A, next: B, source: `REG-2022-${n.r0}`, sourceType: 'Registration' },
    { id: `${p.id}-E2`, stage: 1, type: 'MORTGAGE_REGISTERED', title: 'Mortgage registered', date: '18 Mar 2024', summary: `Mortgage by ${B}`, status: 'normal', field: 'Mortgage', previous: 'No active mortgage', next: `Active mortgage · ${B} → Demo Bank`, source: n.mrg, sourceType: 'Mortgage' },
    { id: `${p.id}-E3`, stage: 2, type: 'SALE_REGISTERED', title: 'Registration', date: '12 Jun 2026', summary: `${B} → ${C}`, status: 'change', field: 'Buyer', previous: B, next: C, source: n.reg, sourceType: 'Registration' },
    { id: `${p.id}-E4`, stage: 3, type: 'MUTATION_UPDATED', title: 'Mutation updated', date: '14 Jun 2026', summary: `New owner: ${D}`, status: 'suspicious', field: 'New Owner', previous: B, next: D, source: n.mut, sourceType: 'Mutation' },
    { id: `${p.id}-E5`, stage: 3, type: 'INVESTIGATION_TRIGGERED', title: 'Investigation triggered', date: '15 Jun 2026', summary: 'Registration and mutation party mismatch', status: 'investigation', field: 'Receiving party', previous: `Registration: ${C}`, next: `Mutation: ${D}`, source: `${n.reg} / ${n.mut}`, sourceType: 'Investigation' },
  ];
  const doc = (rows) => rows;
  const allEvidence = [
    { id: 'ev1', stage: 0, sourceType: 'Registration', sourceId: `REG-2022-${n.r0}`, field: 'Buyer', value: B, date: '12 Jan 2022', related: 'Sale registered', rows: doc([['Buyer', B], ['Seller', A], ['Date', '12 Jan 2022'], ['Registration No.', `REG-2022-${n.r0}`], ['Extent', '5 Acres']]) },
    { id: 'ev2', stage: 0, sourceType: 'RTC', sourceId: rtcId, field: 'Recorded owner', value: B, date: '12 Jan 2022', related: 'Baseline snapshot', rows: doc([['Recorded owner', B], ['Survey No.', p.survey], ['Extent', '5 Acres'], ['Cultivation', 'Agricultural (synthetic)'], ['Encumbrance', 'None at baseline']]) },
    { id: 'ev3', stage: 1, sourceType: 'Mortgage', sourceId: n.mrg, field: 'Borrower', value: B, date: '18 Mar 2024', related: 'Mortgage registered', rows: doc([['Borrower', B], ['Lender', 'Demo Bank (synthetic)'], ['Amount', '₹25,00,000'], ['Date', '18 Mar 2024'], ['Mortgage No.', n.mrg]]) },
    { id: 'ev4', stage: 2, sourceType: 'Registration', sourceId: n.reg, field: 'Buyer', value: C, date: '12 Jun 2026', related: 'Registration', rows: doc([['Buyer', C], ['Seller', B], ['Date', '12 Jun 2026'], ['Registration No.', n.reg], ['Extent', '5 Acres']]) },
    { id: 'ev5', stage: 3, sourceType: 'Mutation', sourceId: n.mut, field: 'New Owner', value: D, date: '14 Jun 2026', related: 'Mutation', rows: doc([['New Owner', D], ['Previous Owner', B], ['Date', '14 Jun 2026'], ['Mutation No.', n.mut], ['Extent', '5 Acres']]) },
    { id: 'ev6', stage: 3, sourceType: 'Mutation', sourceId: n.mut, field: 'Previous Owner', value: B, date: '14 Jun 2026', related: 'Mutation', rows: doc([['New Owner', D], ['Previous Owner', B], ['Date', '14 Jun 2026'], ['Mutation No.', n.mut], ['Extent', '5 Acres']]) },
  ];
  const events = allEvents.filter((e) => e.stage <= stage);
  const evidence = allEvidence.filter((e) => e.stage <= stage);
  const state = stage >= 3 ? 'investigation' : stage >= 1 ? 'change' : 'clear';
  const changes = Math.min(stage, 3);
  const dates = ['12 Jan 2022', '18 Mar 2024', '12 Jun 2026', '14 Jun 2026'];
  const registration = stage >= 2 ? { buyer: C, seller: B, date: '12 Jun 2026', no: n.reg, extent: '5 Acres', doc: allEvidence[3] } : null;
  const mutation = stage >= 3 ? { newOwner: D, previousOwner: B, date: '14 Jun 2026', no: n.mut, extent: '5 Acres', doc: allEvidence[4] } : null;
  return {
    property: p, stage, state, meta: STATE_META[state], changes, events, evidence, registration, mutation,
    owner: stage >= 3 ? D : B,
    mortgage: stage >= 1 ? `Active · ${B} → Demo Bank` : 'No Active Mortgage',
    lastUpdated: dates[stage],
    finding: 'Registration and mutation indicate different receiving parties.',
    why: ['Registration and mutation parties mismatch', 'Ownership transition inconsistency', 'Related records require verification'],
    next: 'Review underlying deed and mutation order.',
    persons: { A, B, C, D },
    mortgageNo: n.mrg,
  };
}

export const TRACE = [
  { step: '01', agent: 'Orchestrator Agent', action: 'Investigation started', result: 'Workflow opened for the watched property', status: 'ok' },
  { step: '02', agent: 'Orchestrator Agent', action: 'Property records loaded', result: 'Baseline snapshot and recorded events retrieved', status: 'ok' },
  { step: '03', agent: 'Change Investigation Agent', action: 'Timeline constructed', result: '5 events ordered chronologically', status: 'ok' },
  { step: '04', agent: 'Change Investigation Agent', action: 'Party mismatch detected', result: 'Registration names Person C; mutation names Person D', status: 'warn' },
  { step: '05', agent: 'Change Investigation Agent', action: 'Mutation record checked', result: 'Mutation lists Person B as the previous owner', status: 'ok' },
  { step: '06', agent: 'Change Investigation Agent', action: 'Issue remains unexplained', result: 'No linking record explains the difference', status: 'warn' },
  { step: '07', agent: 'Evidence Agent', action: 'Evidence collected', result: 'Registration, mutation, mortgage and RTC records attached', status: 'ok' },
  { step: '08', agent: 'Orchestrator Agent', action: 'Investigation complete', result: 'Potential suspicious transaction pattern — needs human/legal verification', status: 'ok' },
];

// ---- synthetic parcel map (x = lng, y = lat in a flat coordinate system) ----
export const PARCELS = [
  { id: '49/2', pts: [[6, 8], [46, 10], [44, 46], [8, 44]] },
  { id: '49/1', pts: [[50, 12], [88, 10], [96, 34], [84, 52], [48, 46]], selected: true },
  { id: '50/1', pts: [[100, 10], [134, 12], [132, 40], [100, 34]] },
  { id: '50/2', pts: [[90, 56], [132, 46], [134, 88], [92, 90]] },
  { id: '47/2', pts: [[6, 50], [44, 52], [46, 90], [8, 92]] },
  { id: '51/1', pts: [[50, 54], [84, 58], [86, 90], [50, 88]] },
];
export const MAP_BOUNDS = [[0, 0], [100, 140]];
