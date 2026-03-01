import Image from "next/image";

export default function HeroSection() {
  return (
    <div className="mb-10 animate-slideUp" style={{ animationDelay: '0.1s' }}>
      <div className="flex items-start gap-5 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm transition-shadow hover:shadow-md">
        <div className="mt-1 bg-blue-50 p-4 rounded-xl border border-blue-100 shadow-sm">
          <Image
            src="/icons/sparkles.svg"
            alt="Sparkle"
            height={48}
            width={56}
            className="drop-shadow-sm text-accent1 drop-shadow-[0_2px_4px_rgba(29,78,216,0.2)]"
          />
        </div>
        <div className="flex-1">
          <h1 className="text-4xl font-semibold mb-3 tracking-tight text-slate-900">
            Create medical content faster
          </h1>
          <p className="text-slate-600 text-lg font-normal leading-relaxed max-w-3xl">
            Search clinical literature or upload your reference documents to seamlessly create
            high-quality content and explore the latest medical breakthroughs.
          </p>
        </div>
      </div>
    </div>
  );
}
