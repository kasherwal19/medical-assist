import { ResultsListProps } from '@/app/search/types';

export default function ResultsList({
  results, selectedItems, toggleSelection, isLoading,
  isLoadingMore, hasMoreResults, onLoadMore
}: ResultsListProps) {

  const handleToogleSelection = (pmc_id: string) => {
    toggleSelection(pmc_id);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-slate-200 border-t-accent1 animate-spin" />
        <div className="text-slate-500 tracking-wide text-sm font-medium">Searching literature...</div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {results.map((result) => {
        const isSelected = selectedItems.has(result.pmc_id);
        return (
          <div key={result.pmc_id} className={`relative group p-6 rounded-2xl transition-all duration-300 ${isSelected ? 'bg-blue-50/50 border border-accent1/30 shadow-sm' : 'bg-white border border-slate-200 hover:border-slate-300 hover:shadow-sm'}`}>
            <div className="flex items-start gap-4">
              <div className="pt-1 select-none">
                <label className="relative flex cursor-pointer items-center rounded-full p-1" htmlFor={`checkbox-${result.pmc_id}`}>
                  <input
                    type="checkbox"
                    id={`checkbox-${result.pmc_id}`}
                    className="before:content[''] peer relative h-5 w-5 cursor-pointer appearance-none rounded-md border border-slate-300 bg-white transition-all before:absolute before:top-2/4 before:left-2/4 before:block before:h-12 before:w-12 before:-translate-y-2/4 before:-translate-x-2/4 before:rounded-full before:bg-accent1 before:opacity-0 before:transition-opacity checked:border-accent1 checked:bg-accent1 checked:before:bg-accent1 hover:before:opacity-10"
                    checked={isSelected}
                    onChange={handleToogleSelection.bind(null, result.pmc_id)}
                  />
                  <div className="pointer-events-none absolute top-2/4 left-2/4 -translate-y-2/4 -translate-x-2/4 text-white opacity-0 transition-opacity peer-checked:opacity-100">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor" stroke="currentColor" strokeWidth="2">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                    </svg>
                  </div>
                </label>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className={`text-lg font-semibold mb-2 leading-tight transition-colors ${isSelected ? 'text-accent1' : 'text-slate-900 group-hover:text-accent1'}`}>{result.title}</h3>
                <div className="flex flex-wrap gap-3 text-xs text-slate-500 mb-3 font-medium">
                  <span className="bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">Journal: <span className="text-slate-800 font-semibold">{result.journal}</span></span>
                  <span className="bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">Publisher: <span className="text-slate-800 font-semibold">{result.publisher}</span></span>
                </div>
                <p className="text-sm text-slate-600 font-normal leading-relaxed mb-3 line-clamp-2 md:line-clamp-3 bg-slate-50/50 p-4 rounded-xl border border-slate-100 border-l-4 border-l-accent2/50 shadow-sm">{result.abstract}</p>
                {result.article_url && (
                  <div className="flex items-center gap-2 text-xs font-medium">
                    <span className="text-slate-400 uppercase tracking-wider">DOI:</span>
                    <a href={result.article_url} target='_blank' rel="noopener noreferrer" className="text-accent2 hover:underline hover:text-accent1 transition-colors">{result.doi}</a>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {hasMoreResults && (
        <div className="flex justify-center mt-8 pt-4">
          <button onClick={onLoadMore} disabled={isLoadingMore}
            className={`px-8 py-3 rounded-xl text-sm font-semibold transition-all shadow-sm ${isLoadingMore ? 'bg-slate-100 text-slate-400 cursor-wait' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-accent1 hover:border-accent1/30 hover:shadow-md cursor-pointer'}`}>
            {isLoadingMore ? 'Loading more...' : 'Load More Results'}
          </button>
        </div>
      )}
    </div>
  );
}