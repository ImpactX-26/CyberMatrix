import { useMemo } from 'react';
import { useAsync } from './useAsync';
import { useMode } from '../services/mode';
import {
  getProperty,
  getTimeline,
  getEvidence,
} from '../services/api';

function makeEvents(propertyData, timeline) {
  if (Array.isArray(timeline) && timeline.length > 0) {
    return timeline.map((event) => ({
      status: event.status || 'normal',
      title: event.title || event.event_type || 'Property event',
      summary: event.summary || event.description || '',
      date: event.date || event.event_date || '',
      type: event.type || event.event_type || '',
      sourceId: event.sourceId || event.source_id || '',
      sourceType: event.sourceType || event.source_type || '',
      previous: event.previous || event.previous_state || '',
      next: event.next || event.new_state || '',
    }));
  }

  const events = [];

  for (const registration of propertyData.registrations || []) {
    events.push({
      status: 'normal',
      title: 'Registration',
      summary: `${registration.seller || 'Unknown seller'} ? ${registration.buyer || 'Unknown buyer'}`,
      date: registration.transaction_date || '',
      type: registration.document_type || 'Registration',
      sourceId: registration.document_number || '',
      sourceType: 'Registration',
      previous: registration.seller || '',
      next: registration.buyer || '',
    });
  }

  for (const mutation of propertyData.mutations || []) {
    events.push({
      status: 'normal',
      title: `Mutation: ${mutation.mutation_type || 'Mutation'}`,
      summary: `${mutation.previous_owner || 'Unknown'} ? ${mutation.new_owner || 'Unknown'}`,
      date: mutation.mutation_date || '',
      type: mutation.mutation_type || 'Mutation',
      sourceId: mutation.mutation_number || '',
      sourceType: 'Mutation',
      previous: mutation.previous_owner || '',
      next: mutation.new_owner || '',
    });
  }

  for (const mortgage of propertyData.mortgages || []) {
    events.push({
      status: 'normal',
      title: 'Mortgage',
      summary: mortgage.institution
        ? `${mortgage.institution} · ${mortgage.status || 'recorded'}`
        : 'Mortgage record',
      date: mortgage.mortgage_date || '',
      type: 'Mortgage',
      sourceId: mortgage.mortgage_id || '',
      sourceType: 'Mortgage',
      previous: '',
      next: mortgage.status || '',
    });
  }

  return events.sort((a, b) => {
    return String(a.date).localeCompare(String(b.date));
  });
}

function makeView(data, timeline, evidence) {
  if (!data?.property) return null;

  const p = data.property;

  const events = makeEvents(data, timeline);

  return {
    property: {
      ...p,
      survey: p.survey_number,
      extent: p.extent_acres,
      owner: p.owner_name,
    },

    owner: p.owner_name,
    extent: p.extent_acres,
    mortgage: p.mortgage_status,
    survey: p.survey_number,
    hissa: p.hissa,

    events,
    evidence: Array.isArray(evidence) ? evidence : [],

    state: 'connected',

    finding: null,
    why: [],
    next: null,
  };
}

export function useView(id) {
  const { mode, version } = useMode();

  const remote = useAsync(
    async () => {
      const [property, timeline, evidence] = await Promise.all([
        getProperty(id),
        getTimeline(id).catch(() => []),
        getEvidence(id).catch(() => []),
      ]);

      return {
        property,
        timeline,
        evidence,
      };
    },
    [id, version],
  );

  const view = useMemo(() => {
    if (!remote.data) return null;

    return makeView(
      remote.data.property,
      remote.data.timeline,
      remote.data.evidence,
    );
  }, [remote.data]);

  return {
    view,
    loading: remote.loading,
    notFound: !remote.loading && !view,
    stage: 0,
    live: mode === 'live',
  };
}
