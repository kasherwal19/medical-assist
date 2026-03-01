import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Article } from '@/app/search/types';
import { searchService } from '@/app/search/services/searchService';

export function useSearchData() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [executedQuery, setExecutedQuery] = useState(initialQuery);
  const [results, setResults] = useState<Article[]>([]);
  const [timeframe, setTimeframe] = useState<string>('none');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(5);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMoreResults, setHasMoreResults] = useState(true);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    setExecutedQuery(query);
  };

  const handleLoadMore = () => {
    if (!isLoadingMore) setOffset((prev) => prev + limit);
  };

  useEffect(() => {
    const fetchResults = async () => {
      if (!executedQuery.trim()) {
        setIsLoading(false);
        return;
      }

      offset === 0 ? setIsLoading(true) : setIsLoadingMore(true);

      try {
        const data = await searchService.fetchResults({
          keyword: executedQuery,
          offset,
          limit,
          timeframe: timeframe === 'none' ? null : timeframe,
        });

        if (offset === 0) {
          setResults(data.results || []);
          setSessionId(data.session_id);
        } else {
          setResults((prev) => [...prev, ...(data.results || [])]);
        }
        
        setHasMoreResults(data.results ? data.results.length === limit : false);
      } catch (error) {
        console.error('Failed to fetch results', error);
      } finally {
        offset === 0 ? setIsLoading(false) : setIsLoadingMore(false);
      }
    };

    fetchResults();
  }, [executedQuery, offset, timeframe, limit]);

  return {
    query, setQuery,
    executedQuery,
    timeframe, setTimeframe,
    results, sessionId,
    isLoading, isLoadingMore, hasMoreResults,
    handleSearchSubmit, handleLoadMore,
    offset,
    setOffset 
  };
}