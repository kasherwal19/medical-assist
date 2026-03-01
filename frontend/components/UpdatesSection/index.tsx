"use client";

import { useState } from "react";
import Image from "next/image";
import { TimeRange, Article } from "@/types";
import { useNewsUpdates } from "@/hooks/useNewsUpdate";
import { formatNewsDate } from "@/utils/formatters";
import { TIME_RANGES } from "@/data";
import LoadingSkeleton from "@/components/LoadingSkeleton";

export default function UpdatesSection() {
  const [selectedRange, setSelectedRange] = useState<TimeRange>(TIME_RANGES[0]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { articles, loading } = useNewsUpdates(selectedRange.value);

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  const handleRangeSelect = (range: TimeRange) => {
    setSelectedRange(range);
    setIsDropdownOpen(false);
  };

  const handleShare = async (title: string, url: string) => {
    if (!navigator.share) {
      console.log("Sharing is not supported on this browser.");
      return;
    }

    try {
      await navigator.share({ title, url });
    } catch (err) {
      console.log("Error sharing:", err);
    }
  };

  const renderRangeOption = (range: TimeRange) => {
    const isSelected = selectedRange.value === range.value;

    return (
      <button
        key={range.label}
        onClick={handleRangeSelect.bind(null, range)}
        className={`w-full text-left px-4 py-3 text-sm hover:bg-slate-50 transition-colors ${isSelected
          ? "bg-slate-50 font-semibold text-accent1"
          : "text-slate-700"
          }`}
      >
        {range.label}
      </button>
    );
  };

  const renderArticle = (update: Article, index: number) => {
    return (
      <div
        key={index}
        className="min-w-[280px] w-[280px] md:min-w-[320px] md:w-[320px] bg-white border border-slate-200 shadow-sm rounded-2xl p-5 flex flex-col justify-between hover:border-accent1/40 hover:shadow-md transition-all duration-300 snap-start group"
      >
        <div>
          <div className="flex items-center gap-2 mb-3 text-xs text-slate-500 font-medium">
            <div className="p-1.5 bg-slate-100 rounded-md">
              <Image
                src="/icons/newspaper.svg"
                alt="Source"
                height={14}
                width={14}
                className="opacity-70 group-hover:opacity-100 transition-opacity"
              />
            </div>
            <span className="uppercase tracking-wider truncate max-w-[100px] text-teal-600 font-semibold">
              {update.source}
            </span>
            <span className="text-slate-300">•</span>
            <span>{formatNewsDate(update.published_at)}</span>
          </div>

          <div className="flex gap-2 mb-3">
            <h3 className="text-base font-semibold text-slate-900 leading-snug line-clamp-3 group-hover:text-accent1 transition-colors">
              <a
                href={update.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {update.title}
              </a>
            </h3>
          </div>

          <p className="text-sm text-slate-600 line-clamp-3 mb-5 leading-relaxed">
            {update.description || "No description available."}
          </p>
        </div>

        <div className="mt-auto pt-4 border-t border-slate-100">
          <button
            onClick={handleShare.bind(null, update.title, update.url)}
            className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400 hover:text-accent1 transition-colors"
          >
            <span>Share Article</span>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="glass-panel p-8 rounded-2xl animate-slideUp" style={{ animationDelay: '0.4s' }}>
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-5">
        <div className="flex items-start gap-4">
          <div className="bg-gradient-to-br from-teal-50 to-blue-50 p-3 rounded-xl border border-teal-100 shadow-sm">
            <Image
              src="/icons/newspaper.svg"
              alt="Newspaper"
              height={36}
              width={36}
              className="opacity-90"
            />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-slate-900 tracking-tight mb-1">
              Latest Medical Updates
            </h2>
            <p className="text-sm text-slate-500">
              Track recent breakthroughs, clinical findings, and research updates.
            </p>
          </div>
        </div>

        <div className="relative z-20">
          <button
            onClick={toggleDropdown}
            className="flex items-center gap-2 px-4 py-2.5 border border-slate-200 bg-white hover:bg-slate-50 shadow-sm rounded-lg text-sm text-slate-700 transition-all font-medium"
          >
            <span className="text-slate-500">Time Range:</span>
            <span className="font-semibold text-slate-900">
              {selectedRange.label}
            </span>
            <Image
              src="/icons/arrow-down.svg"
              alt="Dropdown"
              height={12}
              width={12}
              className={`transition-transform duration-300 opacity-50 invert ${isDropdownOpen ? "rotate-180" : ""
                }`}
            />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-lg shadow-slate-200/50 overflow-hidden animate-fadeIn">
              {TIME_RANGES.map(renderRangeOption)}
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-5 overflow-x-auto pb-6 pt-2 scrollbar-hide snap-x px-1">
        {loading ? (
          <LoadingSkeleton />
        ) : articles.length > 0 ? (
          articles.map(renderArticle)
        ) : (
          <div className="w-full flex flex-col items-center justify-center text-slate-500 text-sm py-12 bg-slate-50 rounded-xl min-h-[220px] border border-dashed border-slate-200">
            <Image src="/icons/newspaper.svg" alt="" width={32} height={32} className="opacity-20 mb-3 grayscale" />
            No updates found for this time range.
          </div>
        )}
      </div>
    </div>
  );
}