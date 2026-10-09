import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, MapPin } from 'lucide-react';
import MapView from '../components/MapView';
import { PROPERTIES, MAIN_ID } from '../data/demoData';
import { setStage } from '../data/sim';
import { monitorProperty } from '../services/api';

const OPTIONS = {
  district: ['Bengaluru'], taluk: ['Anekal'], hobli: ['Jigani'], village: ['Bannerghatta'],
};
const Select = ({ label, name, value, onChange }) => (
  <label className="block">
    <span className="label">{label}</span>
    <select name={name} value={value} onChange={onChange} className="mt-1 w-full rounded-xl border border-navy/15 bg-white px-3 py-2.5 text-sm">
      {OPTIONS[name].map((o) => <option key={o}>{o}</option>)}
    </select>
  </label>
);

export default function PropertySetup() {
  const nav = useNavigate();
  const [f, setF] = useState({ district: 'Bengaluru', taluk: 'Anekal', hobli: 'Jigani', village: 'Bannerghatta', survey: '49', hissa: '1' });
  const [notice, setNotice] = useState('');
  const on = (e) => setF({ ...f, [e.target.name]: e.target.value });

  const start = (e) => {
    e.preventDefault();
    const match = PROPERTIES.find((p) => p.survey === `${f.survey}/${f.hissa}`);
    if (!match) { setNotice(`No synthetic record for Survey ${f.survey}/${f.hissa}. Opening the synthetic demo property instead.`); }
    const id = match ? match.id : MAIN_ID;
    if (id === MAIN_ID) setStage(0);
    monitorProperty(id).catch(() => {});
    setTimeout(() => nav(`/property/${id}`), match ? 0 : 900);
  };
  const demo = () => { setStage(0); monitorProperty(MAIN_ID).catch(() => {}); nav(`/property/${MAIN_ID}`); };

  return (
    <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-2">
      <div>
        <h1 className="text-4xl font-bold">Watch a Property</h1>
        <p className="mt-2 text-navy/65">Enter property details to start monitoring changes.</p>
        <form onSubmit={start} className="card mt-6 space-y-4 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <Select label="District" name="district" value={f.district} onChange={on} />
            <Select label="Taluk" name="taluk" value={f.taluk} onChange={on} />
            <Select label="Hobli" name="hobli" value={f.hobli} onChange={on} />
            <Select label="Village" name="village" value={f.village} onChange={on} />
            <label className="block"><span className="label">Survey Number</span>
              <input name="survey" value={f.survey} onChange={on} inputMode="numeric" required className="mt-1 w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm" /></label>
            <label className="block"><span className="label">Hissa</span>
              <input name="hissa" value={f.hissa} onChange={on} inputMode="numeric" required className="mt-1 w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm" /></label>
          </div>
          <button type="submit" className="btn-navy w-full !py-3">Start Monitoring</button>
          {notice && <p className="rounded-lg bg-warn/[0.12] p-3 text-sm" role="status">{notice}</p>}
          <div className="flex items-center gap-3 text-xs text-navy/40"><span className="h-px flex-1 bg-navy/10" /> Or <span className="h-px flex-1 bg-navy/10" /></div>
          <button type="button" onClick={demo} className="flex w-full items-center gap-3 rounded-xl border border-info/30 bg-info/5 p-4 text-left hover:bg-info/10">
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-info text-white"><Zap size={18} /></span>
            <span>
              <span className="block text-sm font-bold">Try Demo Property</span>
              <span className="block text-xs text-navy/60">PROP-0491 · Survey 49/1 · Synthetic Demo Property</span>
            </span>
          </button>
        </form>
      </div>
      <div>
        <MapView height={460} selectedSurvey={`${f.survey}/${f.hissa}`} caption={`Survey No. ${f.survey}/${f.hissa} · ${f.village} Village, ${f.taluk} Taluk, ${f.district} District`} />
        <p className="mt-3 flex items-center gap-1.5 text-xs text-navy/50"><MapPin size={13} /> Synthetic parcels — no real private property data.</p>
      </div>
    </div>
  );
}
