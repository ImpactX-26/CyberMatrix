import { useMemo } from 'react';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';

const BASE = { borderRadius: 12, padding: '10px 12px', fontSize: 13, fontWeight: 600, width: 150, textAlign: 'center', border: '2px solid', background: '#fff', color: '#08263D' };
const KIND = {
  person: { borderColor: '#3478D4' },
  property: { borderColor: '#08263D', background: '#08263D', color: '#fff' },
  mortgage: { borderColor: '#7657D9', background: '#F3EFFD' },
  record: { borderColor: '#E59B28', background: '#FFF6E5' },
  doc: { borderColor: '#8a98a5', background: '#F1F3F5' },
};
const RED = { borderColor: '#D92D3A', background: '#FDECEE' };

export default function PropertyGraph({ view, height = 520 }) {
  const { A, B, C, D } = view.persons;
  const s = view.stage;
  const flag = s >= 3;

  const { nodes, edges } = useMemo(() => {
    const N = (id, label, kind, x, y, bad = false) => ({
      id, position: { x, y }, data: { label }, draggable: true, selectable: false,
      style: { ...BASE, ...KIND[kind], ...(bad ? RED : {}) },
    });
    const E = (id, source, target, label, bad = false) => ({
      id, source, target, label, animated: bad,
      markerEnd: { type: MarkerType.ArrowClosed, color: bad ? '#D92D3A' : '#5b7083' },
      style: { stroke: bad ? '#D92D3A' : '#5b7083', strokeWidth: bad ? 2.5 : 1.6, strokeDasharray: bad ? '6 4' : undefined },
      labelStyle: { fontSize: 10, fontWeight: 700, fill: bad ? '#D92D3A' : '#08263D' },
      labelBgStyle: { fill: '#fff', fillOpacity: 0.95 }, labelBgPadding: [4, 2], labelBgBorderRadius: 4,
    });
    const nodes = [N('A', A, 'person', 0, 0), N('P', `Property ${view.property.survey}`, 'property', 260, 0), N('B', B, 'person', 260, 150)];
    const edges = [E('a-p', 'A', 'P', 'OWNS'), E('a-b', 'A', 'B', 'SELLS'), E('b-p', 'B', 'P', 'OWNS')];
    if (s >= 1) { nodes.push(N('M', `Mortgage ${view.mortgageNo}`, 'mortgage', 520, 0)); edges.push(E('m-p', 'M', 'P', 'MORTGAGES')); }
    if (s >= 2) {
      nodes.push(N('R', `Registration ${view.registration.no}`, 'record', 70, 300, flag), N('C', C, 'person', 70, 450, flag), N('DOC', 'Underlying deed', 'doc', 260, 450));
      edges.push(E('b-r', 'B', 'R', 'SELLS', flag), E('r-c', 'R', 'C', 'BUYS', flag), E('r-doc', 'R', 'DOC', 'SUPPORTED_BY'));
    }
    if (s >= 3) {
      nodes.push(N('MU', `Mutation ${view.mutation.no}`, 'record', 450, 300, true), N('D', D, 'person', 450, 450, true));
      edges.push(E('b-mu', 'B', 'MU', 'MUTATES', true), E('mu-d', 'MU', 'D', 'MUTATES', true), E('mu-doc', 'MU', 'DOC', 'SUPPORTED_BY'), E('c-d', 'C', 'D', 'REQUIRES REVIEW', true));
    }
    return { nodes, edges };
  }, [view, A, B, C, D, s, flag]);

  return (
    <div className="card overflow-hidden">
      <div style={{ height }} className="w-full">
        <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.15 }} nodesConnectable={false}
          zoomOnScroll={false} preventScrolling={false} minZoom={0.3} proOptions={{ hideAttribution: true }}>
          <Background gap={22} color="#dfe5e1" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-navy/10 bg-white px-5 py-3 text-xs font-medium">
        <span className="inline-flex items-center gap-2"><span className="h-0.5 w-6 bg-[#5b7083]" /> Normal Relationship</span>
        <span className="inline-flex items-center gap-2"><span className="h-0.5 w-6 border-t-2 border-dashed border-bad" /> Requires Review</span>
        <span className="text-navy/45">Synthetic Demo Data</span>
      </div>
    </div>
  );
}
