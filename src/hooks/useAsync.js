import { useEffect, useState } from 'react';

export function useAsync(fn, deps = []) {
  const [s, set] = useState({ loading: true, data: null, error: null });
  useEffect(() => {
    let alive = true;
    set((x) => ({ ...x, loading: true }));
    fn()
      .then((data) => alive && set({ loading: false, data, error: null }))
      .catch((error) => alive && set({ loading: false, data: null, error }));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return s;
}
