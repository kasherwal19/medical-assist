export default function LoadingSkeleton() {
  return (
    <>
      {Array(4)
        .fill(0)
        .map((_, i) => (
          <div
            key={i}
            className="min-w-[280px] w-[280px] md:min-w-[320px] md:w-[320px] border border-slate-700 rounded-2xl p-5 animate-pulse bg-slate-800/40"
          >
            <div className="h-4 bg-slate-700 rounded w-1/3 mb-5"></div>
            <div className="h-5 bg-slate-700/80 rounded w-full mb-3"></div>
            <div className="h-5 bg-slate-700/80 rounded w-4/5 mb-6"></div>
            <div className="h-16 bg-slate-700/50 rounded w-full"></div>
            <div className="mt-6 pt-4 border-t border-slate-700 h-4 bg-slate-700/60 rounded w-1/4"></div>
          </div>
        ))}
    </>
  );
}