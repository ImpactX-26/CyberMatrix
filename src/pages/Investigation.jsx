import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, FileText, Download, Search, UserCheck } from 'lucide-react';
import StatusBanner from '../components/StatusBanner';
import AgentTrace from '../components/AgentTrace';
import PropertyGraph from '../components/PropertyGraph';
import DocumentModal from '../components/DocumentModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { useView } from '../hooks/useView';

function RecordCard({ title, tone, rows, onView }) {
  return (
    <div className={`card border-t-4 p-6 ${tone}`}>
      <h3 className="flex items-center gap-2 text-lg font-bold"><FileText size={18} /> {title}</h3>
      <dl className="mt-4 divide-y divide-navy/10 text-sm">
        {rows.map(([k, v]) => <div key={k} className="flex justify-between gap-3 py-2"><dt className="text-navy/55">{k}</dt><dd className="font-semibold">{v}</dd></div>)}
      </dl>
      <button className="btn-ghost mt-4 w-full !py-2" onClick={onView}>View Document</button>
    </div>
  );
}

export default function Investigation() {
  const { id } = useParams();
  const { view, loading, notFound } = useView(id);
  const [doc, setDoc] = useState(null);

  if (notFound) return <div className="px-4 py-16"><ErrorState title="Property not found" message={`No synthetic property with ID ${id}.`} backHome /></div>;
  if (loading || !view) return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6"><LoadingState /></div>;

  const p = view.property;
  const open = view.state === 'investigation';
  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link to={`/property/${id}`} className="inline-flex items-center gap-1.5 text-sm text-navy/60 hover:text-navy"><ArrowLeft size={15} /> Back to property</Link>
        <button className="btn-ghost !py-2" onClick={() => window.print()}><Download size={15} /> Export Report</button>
      </div>

      <StatusBanner state={view.state} changes={view.changes} priority={open ? 'HIGH' : undefined}>
        <span className="font-semibold">{p.id}</span> · Survey {p.survey}
      </StatusBanner>

      {!open ? (
        <div className="card p-10 text-center">
          <Search className="mx-auto text-navy/30" />
          <h2 className="mt-3 text-2xl font-bold">No investigation open for {p.id}</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-navy/65">An investigation starts when registration and mutation records disagree. Add events on the property page to trigger one.</p>
          <Link to={`/property/${id}`} className="btn-navy mt-5">Go to Simulate Property Change</Link>
        </div>
      ) : (
        <>
          <section className="grid gap-6 lg:grid-cols-5">
            <div className="card p-6 lg:col-span-3">
              <h2 className="text-lg font-bold text-navy/60">Key Finding</h2>
              <p className="mt-2 font-display text-3xl font-semibold leading-snug">{view.finding}</p>
              <p className="mt-4 text-sm text-navy/65">This is a potential suspicious transaction pattern, not a conclusion. It needs human/legal verification.</p>
            </div>
            <div className="card p-6 lg:col-span-2">
              <h2 className="text-lg font-bold">Why Flagged</h2>
              <ul className="mt-3 space-y-3">
                {view.why.map((w) => <li key={w} className="flex items-start gap-2.5 text-sm font-medium"><AlertTriangle size={18} className="mt-0.5 shrink-0 text-warn" /> {w}</li>)}
              </ul>
            </div>
          </section>

          <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            <RecordCard title="Registration Record" tone="border-t-ai" onView={() => setDoc(view.registration.doc)} rows={[
              ['Buyer', view.registration.buyer], ['Seller', view.registration.seller], ['Date', view.registration.date], ['Registration No.', view.registration.no], ['Extent', view.registration.extent]]} />
            <RecordCard title="Mutation Record" tone="border-t-warn" onView={() => setDoc(view.mutation.doc)} rows={[
              ['New Owner', view.mutation.newOwner], ['Previous Owner', view.mutation.previousOwner], ['Date', view.mutation.date], ['Mutation No.', view.mutation.no], ['Extent', view.mutation.extent]]} />
            <div className="card flex flex-col border-t-4 border-t-info p-6 md:col-span-2 xl:col-span-1">
              <h3 className="flex items-center gap-2 text-lg font-bold"><UserCheck size={18} /> Next Verification</h3>
              <p className="mt-4 text-lg">{view.next}</p>
              <p className="mt-2 text-sm text-navy/60">Compare the underlying deed with the mutation order.</p>
              <p className="mt-auto pt-5"><span className="rounded-full border border-warn/40 bg-warn/[0.12] px-3 py-1 text-sm font-semibold text-[#9a6209]">Needs human verification</span></p>
              <Link to={`/property/${id}?tab=evidence`} className="mt-4 text-sm font-semibold text-info hover:underline">See all evidence →</Link>
            </div>
          </section>

          <section><h2 className="mb-3 text-2xl font-bold">AI Investigation Trace</h2><AgentTrace /></section>
          <section><h2 className="mb-3 text-2xl font-bold">Property Relationship Graph</h2><PropertyGraph view={view} /></section>
        </>
      )}
      <DocumentModal doc={doc} onClose={() => setDoc(null)} />
    </div>
  );
}
