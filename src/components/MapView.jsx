import { useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapContainer, Polygon, Polyline, CircleMarker, Tooltip } from 'react-leaflet';
import { PARCELS, MAP_BOUNDS } from '../data/demoData';

// Synthetic parcel map drawn in a flat coordinate system (no tiles, no API key, never fails offline).
// "Satellite View" is a synthetic imagery-style rendering for the same reason.
const flip = (pts) => pts.map(([x, y]) => [y, x]);
const center = (pts) => [pts.reduce((a, p) => a + p[1], 0) / pts.length, pts.reduce((a, p) => a + p[0], 0) / pts.length];
const GREENS = ['#4c7a3f', '#5d8a46', '#44703a', '#6a914f', '#527d41'];

export default function MapView({ selectedSurvey = '49/1', tone = 'info', height = 420, className = '', caption }) {
  const [sat, setSat] = useState(false);
  const selColor = tone === 'bad' ? '#D92D3A' : '#3478D4';
  const selected = PARCELS.find((p) => p.selected);
  const village = [[2, 2], [2, 138], [98, 138], [98, 2], [2, 2]];

  return (
    <div className={`relative overflow-hidden rounded-2xl border border-navy/10 ${sat ? 'sat' : ''} ${className}`} style={{ height }}>
      <MapContainer crs={L.CRS.Simple} bounds={MAP_BOUNDS} minZoom={-2} maxZoom={4} zoomSnap={0.25} attributionControl={false}
        scrollWheelZoom={false} style={{ height: '100%', width: '100%', background: sat ? '#2f4a2c' : '#EEF1EA' }}>
        <Polyline positions={village} pathOptions={{ color: sat ? '#fff' : '#08263D', weight: 1.5, dashArray: '6 6', opacity: 0.55 }} />
        {PARCELS.map((p, i) => {
          const isSel = p.selected;
          return (
            <Polygon key={p.id} positions={flip(p.pts)}
              pathOptions={{
                color: isSel ? selColor : sat ? '#ffffff' : '#7b8d9b', weight: isSel ? 3 : 1.2,
                fillColor: isSel ? selColor : sat ? GREENS[i % GREENS.length] : '#FFFFFF', fillOpacity: isSel ? 0.35 : sat ? 0.85 : 0.9,
              }}>
              <Tooltip permanent direction="center" className="parcel-label">{p.id}</Tooltip>
            </Polygon>
          );
        })}
        <CircleMarker center={center(selected.pts)} radius={7} pathOptions={{ color: '#fff', weight: 2, fillColor: selColor, fillOpacity: 1 }} />
      </MapContainer>

      <div className="absolute left-3 top-3 z-[500] flex overflow-hidden rounded-lg border border-navy/15 bg-white text-xs font-semibold shadow">
        <button onClick={() => setSat(false)} className={`px-3 py-1.5 ${!sat ? 'bg-navy text-white' : ''}`}>Map View</button>
        <button onClick={() => setSat(true)} className={`px-3 py-1.5 ${sat ? 'bg-navy text-white' : ''}`}>Satellite View</button>
      </div>
      <div className="pointer-events-none absolute bottom-3 left-3 z-[500] max-w-[75%] rounded-lg bg-white/95 px-3 py-2 text-xs shadow">
        <p className="font-bold">Selected Location</p>
        <p className="text-navy/70">{caption || `Survey No. ${selectedSurvey} · Bannerghatta Village, Anekal Taluk, Bengaluru District`}</p>
        <p className="mt-1 text-[10px] text-navy/45">Synthetic Demo Data</p>
      </div>
    </div>
  );
}
