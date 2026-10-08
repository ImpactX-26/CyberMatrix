# LANDSHIELD — AI Property Change Intelligence & Early Fraud Warning

> Don't just verify a property. Watch its story change.

LandShield creates a baseline for a property and monitors how its recorded state changes over time.
It never says "fraud confirmed". It flags a **potential suspicious transaction pattern** that needs **human/legal verification**.

```
PROPERTY → CHANGE → INVESTIGATION → EVIDENCE → ACTION
```

All data is synthetic (Person A–D, synthetic survey numbers). No real records are used.

## Features

- Landing page, Watch a Property setup (with synthetic parcel map)
- Property Digital Twin with tabs: Overview · Timeline · Map · Evidence · Graph · Investigation
- Clickable timeline with event details (type, date, previous/new state, source, field)
- **Simulate Property Change**: Add Mortgage → Add Registration → Add Mutation → investigation triggered (works offline)
- Investigation page: key finding, Why Flagged, Registration/Mutation cards, Next Verification
- Evidence view with working filters and a synthetic document preview modal
- AI Investigation Trace (3 agents only: Orchestrator, Change Investigation, Evidence)
- React Flow relationship graph with "Requires Review" highlighting
- Leaflet parcel map with Map View / Satellite View (synthetic, no tiles or API key needed)
- Portfolio of 20 properties with stats, filters and a Recharts events chart
- Loading skeletons, error state, automatic Demo Mode fallback, responsive layout

## Installation

```bash
npm install
```

## Environment

Copy `.env.example` to `.env`:

```text
VITE_API_URL=http://localhost:8000
```

## Run

```bash
npm run dev
```

Open http://localhost:5173

## Demo (PROP-0491, Survey 49/1)

1. Click **Watch a Property → Try Demo Property** (starts at baseline: Person B owns 5 acres, no mortgage; the 2022 sale A → B is the baseline history).
2. On the property page use **Simulate Property Change**:
   - **Add Mortgage** — mortgage registered (status: change detected)
   - **Add Registration** — Person B → Person C
   - **Add Mutation** — Person B → Person D, which triggers the investigation
3. Final state: **INVESTIGATION REQUIRED · HIGH PRIORITY**. Finding: *Registration and mutation indicate different receiving parties.*
4. Open the investigation → evidence (registration + mutation) → agent trace → graph → next verification (underlying deed + mutation order).

"See Demo Investigation" on the landing page jumps straight to the final state. Use **Reset to baseline** to replay.

## Backend

The frontend talks to the FastAPI backend through `src/services/api.js` (all calls are centralized there):

```
GET  /properties            GET  /properties/{id}/timeline
GET  /properties/{id}       GET  /properties/{id}/evidence
GET  /properties/{id}/snapshot   POST /properties/{id}/monitor
GET  /properties/{id}/events     POST /properties/{id}/simulate-event
GET  /investigations/{property_id}
```

Set `VITE_API_URL` to point at the backend. Live data is used where its shape matches
(timeline items need `date` + `title`; evidence items need `sourceId`, `sourceType`, `field`, `value`, `date`, `related`, `rows`);
otherwise the synthetic data fills in.

## Demo Mode

On startup the app probes the backend once. If it is unreachable it automatically uses synthetic data and shows
**Demo Mode Active** with **Retry** and **Continue with Demo**. Nothing is ever blank.

## Structure

```
src/components   shared UI (Timeline, EvidenceCard, PropertyGraph, MapView, AgentTrace, ...)
src/pages        Landing, PropertySetup, PropertyTwin, Investigation, Portfolio
src/services     api.js (axios + fallback), mode.js (live/demo store)
src/data         demoData.js (synthetic scenario), sim.js (simulation stage)
src/hooks        useAsync, useView
```
