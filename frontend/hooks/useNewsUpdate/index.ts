import { Article } from "@/types";
import { fetchHealthNews } from "@/services/newsService";
import { useApiData } from "@/hooks/useAPI";

export function useNewsUpdates(days: number) {
  const { data, loading, error } = useApiData<Article[]>(
    ({ signal }) => fetchHealthNews(days, { signal }),
    [days]
  );

  return {
    articles: data ?? [],
    loading,
    error,
  };
}
