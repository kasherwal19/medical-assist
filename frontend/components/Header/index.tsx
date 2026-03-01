import Image from "next/image";
import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-border-subtle py-3 px-8 flex justify-between items-center transition-all shadow-sm">
      <div className="flex items-center gap-2">
        <Link href="/" className="hover:opacity-90 transition-opacity flex items-center gap-3">
          <div className="flex items-center justify-center p-1.5 bg-gradient-to-br from-blue-50 to-teal-50 rounded-lg border border-teal-100/50 shadow-sm">
            <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M50 8C26.804 8 8 26.804 8 50C8 73.196 26.804 92 50 92C73.196 92 92 73.196 92 50C92 26.804 73.196 8 50 8Z" fill="url(#paint0_linear)" />
              <path d="M50 15C30.67 15 15 30.67 15 50C15 69.33 30.67 85 50 85C69.33 85 85 69.33 85 50C85 30.67 69.33 15 50 15Z" fill="white" />
              <path d="M70.5 35L47.5 70L29.5 50L35.5 44L46 55.5L63 29L70.5 35Z" fill="url(#paint1_linear)" />
              <path d="M68 53H57V42H43V53H32V67H43V78H57V67H68V53Z" fill="url(#paint2_linear)" />
              <defs>
                <linearGradient id="paint0_linear" x1="8" y1="8" x2="92" y2="92" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#1D4ED8" />
                  <stop offset="1" stopColor="#0D9488" />
                </linearGradient>
                <linearGradient id="paint1_linear" x1="29.5" y1="49.5" x2="70.5" y2="49.5" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#1D4ED8" />
                  <stop offset="1" stopColor="#0D9488" />
                </linearGradient>
                <linearGradient id="paint2_linear" x1="32" y1="42" x2="68" y2="78" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#2563EB" stopOpacity="0.9" />
                  <stop offset="1" stopColor="#14B8A6" stopOpacity="0.9" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-slate-800 leading-none">Medical</span>
            <span className="text-sm font-semibold tracking-wide text-teal-600 leading-none mt-0.5">Assist</span>
          </div>
        </Link>
      </div>
      <div className="w-10 h-10 rounded-full bg-slate-100 border-2 border-slate-200 overflow-hidden cursor-pointer shadow-sm hover:shadow-md hover:border-accent1/50 transition-all flex items-center justify-center">
        <svg className="w-6 h-6 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
        </svg>
      </div>
    </header>
  );
}