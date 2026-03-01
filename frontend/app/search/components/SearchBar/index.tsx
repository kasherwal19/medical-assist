import Image from 'next/image';
import { SearchBarProps } from '@/app/search/types';

export default function SearchBar({ query, setQuery, onSubmit, setTimeframe, resetOffset }: SearchBarProps) {
  return (
    <div className="flex flex-col lg:flex-row items-center gap-4 mb-8">
      <form onSubmit={onSubmit} className="relative w-full lg:w-auto flex-1 group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-accent1 to-accent2 rounded-xl blur opacity-10 group-hover:opacity-20 transition duration-500"></div>
        <div className="relative flex items-center bg-white rounded-xl border border-slate-200 shadow-sm focus-within:border-accent1 focus-within:ring-1 focus-within:ring-accent1/20 transition-all">
          <Image src="/icons/search-line.svg" alt="Search" height={20} width={20}
            className="absolute left-4 top-1/2 -translate-y-1/2 opacity-40 transition-opacity group-hover:opacity-60 invert-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent pl-12 pr-28 py-3.5 focus:outline-none focus:ring-0 rounded-xl text-sm placeholder-slate-400 text-slate-800 transition-all"
            placeholder="Search literature..."
          />
          <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 btn-gradient px-5 py-2 rounded-lg text-sm font-medium cursor-pointer text-white shadow-sm">
            Search
          </button>
        </div>
      </form>

      <div className="flex w-full lg:w-auto">
        <div className="relative w-full lg:w-48">
          <select
            onChange={(e) => {
              resetOffset();
              setTimeframe(e.target.value);
            }}
            className="appearance-none w-full bg-slate-50 px-4 py-3.5 pr-10 border border-slate-200 rounded-xl text-sm text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-1 focus:border-accent1 focus:ring-accent1/50 cursor-pointer shadow-sm transition-colors"
          >
            <option value="none" className="bg-white text-slate-800">Timeframe: All Time</option>
            <option value="24h" className="bg-white text-slate-800">Last 24 Hours</option>
            <option value="7d" className="bg-white text-slate-800">Last 7 Days</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
            <Image src="/icons/arrow-down.svg" alt="Dropdown Arrow" width={12} height={12} className="opacity-50 invert" />
          </div>
        </div>
      </div>
    </div>
  );
}