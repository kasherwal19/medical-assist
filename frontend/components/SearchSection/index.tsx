import Image from "next/image";

export default function SearchSection() {
  return (
    <div className="glass-panel glass-panel-hover p-8 rounded-2xl flex flex-col justify-between animate-slideUp h-full" style={{ animationDelay: '0.2s' }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-teal-50 p-2.5 rounded-lg border border-teal-100 shadow-sm">
          <Image
            src="/icons/search.svg"
            alt="Search"
            height={28}
            width={28}
            className="drop-shadow-sm opacity-80"
          />
        </div>
        <h2 className="text-2xl font-semibold text-slate-800 tracking-tight">
          Search Clinical Literature
        </h2>
      </div>

      <form action="/search" method="GET" className="relative mt-auto">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-accent1 to-accent2 rounded-xl blur opacity-10 group-hover:opacity-20 transition duration-500"></div>
          <div className="relative flex items-center bg-white rounded-xl border border-slate-200 shadow-sm focus-within:border-accent1 focus-within:ring-1 focus-within:ring-accent1/20 transition-all">
            <Image
              src="/icons/search-line.svg"
              alt="Search"
              height={20}
              width={20}
              className="absolute left-4 top-1/2 -translate-y-1/2 opacity-40 invert-0"
            />
            <input
              name="q"
              type="text"
              placeholder='Try "acute lymphoblastic leukemia"'
              className="w-full bg-transparent pl-12 pr-32 py-4 rounded-xl focus:outline-none focus:ring-0 text-slate-800 text-base placeholder-slate-400"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 btn-gradient px-5 py-2 rounded-lg font-medium cursor-pointer"
            >
              Search
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}