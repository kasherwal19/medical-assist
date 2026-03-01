'use client';

import { Suspense, useEffect, useCallback } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import Header from '@/components/Header';
import SearchBar from '@/app/search/components/SearchBar';
import ResultsList from '@/app/search/components/ResultList';
import { useSearchData } from '@/app/search/hooks/useSearchData';
import { useDocSelection } from '@/app/search/hooks/useDocSelection';

function SearchContent() {
  const searchData = useSearchData();
  const selection = useDocSelection(searchData.results, searchData.sessionId);
  const handleResetOffset = useCallback(() => {
    searchData.setOffset(0);
  }, [searchData]);

  useEffect(() => {
    if (searchData.offset === 0) selection.clearSelection();
  }, [searchData.executedQuery, searchData.offset]);

  return (
    <div className="relative min-h-screen pb-10 bg-slate-50">
      <Header />
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-6 animate-fadeIn">
        <Link href="/" className="inline-flex items-center text-accent1 text-sm font-medium mb-6 hover:underline gap-2 cursor-pointer transition-colors">
          <div className="bg-white p-1 rounded-full border border-slate-200 shadow-sm">
            <Image src="/icons/arrow-left.svg" alt="Back" width={14} height={14} className="opacity-70" />
          </div>
          Go Back
        </Link>

        <div className="glass-panel p-8 min-h-[600px] relative mb-8 rounded-2xl shadow-md bg-white border border-slate-200">
          <div className="flex items-center gap-3 mb-8 pb-6 border-b border-slate-100">
            <div className="bg-blue-50 p-2.5 rounded-lg border border-blue-100 shadow-sm">
              <Image src="/icons/search.svg" alt="Search" height={24} width={24} className="opacity-80 drop-shadow-sm" />
            </div>
            <h1 className="text-2xl font-semibold text-slate-800 tracking-tight">Search Clinical Literature</h1>
          </div>

          <SearchBar
            query={searchData.query}
            setQuery={searchData.setQuery}
            onSubmit={searchData.handleSearchSubmit}
            setTimeframe={searchData.setTimeframe}
            resetOffset={handleResetOffset}
          />

          <ResultsList
            results={searchData.results}
            selectedItems={selection.selectedItems}
            toggleSelection={selection.toggleSelection}
            isLoading={searchData.isLoading}
            isLoadingMore={searchData.isLoadingMore}
            hasMoreResults={searchData.hasMoreResults}
            onLoadMore={searchData.handleLoadMore}
          />
        </div>

        <div className="flex justify-end p-4 bg-white/80 rounded-xl border border-slate-200 backdrop-blur-md sticky bottom-6 z-20 shadow-lg">
          <button
            className="btn-gradient px-10 py-3 rounded-xl text-sm font-semibold tracking-wide transition-all shadow-md disabled:opacity-50 disabled:shadow-none hover:shadow-lg cursor-pointer text-white"
            onClick={selection.handleProceed}
            disabled={selection.isProcessing || selection.selectedItems.size === 0 || !searchData.sessionId}
          >
            {selection.isProcessing ? "Processing..." : `Proceed with ${selection.selectedItems.size} Selected`}
          </button>
        </div>
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center">Loading Search...</div>}>
      <SearchContent />
    </Suspense>
  );
}