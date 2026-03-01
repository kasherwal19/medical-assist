export interface Article {
  title: string;
  description: string | null;
  source: string;
  published_at: string;
  url: string;
}

export interface NewsResponse {
  days: number;
  count: number;
  articles: Article[];
}

export interface TimeRange {
  label: string;
  value: number;
}