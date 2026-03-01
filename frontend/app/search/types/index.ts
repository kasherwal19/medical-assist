export type Article = {
  pmc_id: string;
  title: string;
  journal: string;
  doi: string;
  publisher: string;
  article_url: string;
  pdf_url: string;
  abstract: string;
};

export type SearchResponse = {
  session_id: string;
  keyword: string;
  offset: number;
  results_count: number;
  results: Article[];
};

export interface SearchParams {
  keyword: string;
  offset: number;
  limit: number;
  timeframe: string | null;
}

export interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  setTimeframe: (t: string) => void;
  resetOffset: () => void;
}

export interface ResultsListProps {
  results: Article[];
  selectedItems: Set<string>;
  toggleSelection: (id: string) => void;
  isLoading: boolean;
  isLoadingMore: boolean;
  hasMoreResults: boolean;
  onLoadMore: () => void;
}