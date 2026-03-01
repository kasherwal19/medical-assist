import { API_ENDPOINTS } from "@/data";
import { Article, NewsResponse } from "@/types";

export const fetchHealthNews = async ( days: number, options?: { signal?: AbortSignal }): Promise<Article[]> => {
  const res = await fetch(`${API_ENDPOINTS.NEWS_HEALTH_API}?days=${days}`, {
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch news: ${res.status} ${res.statusText}`);
  }

  const data: NewsResponse = await res.json();
  return data.articles ?? [];
};
