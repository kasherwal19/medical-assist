import { useState, useEffect } from "react";

type Fetcher<T> = (options: { signal?: AbortSignal }) => Promise<T>;

export function useApiData<T>(
  fetcher: Fetcher<T>,
  deps: unknown[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const result = await fetcher({ signal });

        if (!signal.aborted) {
          setData(result);
        }
      } catch (err: unknown) {
        if (!signal.aborted) {
          setError(
            err instanceof Error ? err.message : "Failed to load data"
          );
        }
      } finally {
        if (!signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => controller.abort();
  }, deps);

  return { data, loading, error };
}
