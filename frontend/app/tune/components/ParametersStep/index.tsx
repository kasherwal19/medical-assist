'use client';

import Image from 'next/image';
import { requiredGroups, optionalGroups } from '@/app/tune/data/parameter-options';
import { useCallback, useMemo } from 'react';

type ParametersStepProps = {
  selections: Record<string, string[]>;
  setSelections: React.Dispatch<React.SetStateAction<Record<string, string[]>>>;
  showOptional: boolean;
  setShowOptional: React.Dispatch<React.SetStateAction<boolean>>;
  includeImages: boolean;
  setIncludeImages: React.Dispatch<React.SetStateAction<boolean>>;
  onNext: () => void;
};

export default function ParametersStep({
  selections,
  setSelections,
  showOptional,
  setShowOptional,
  includeImages,
  setIncludeImages,
  onNext
}: ParametersStepProps) {
  const createSelectionHandler = (category: string, option: string) => () => {
    setSelections(prev => ({
      ...prev,
      [category]: [option],
    }));
  };

  const handleToggleOptionalVisibility = () => {
    setShowOptional(prev => !prev);
  };

  const handleToggleIncludeImages = () => {
    setIncludeImages(prev => !prev);
  };

  const canProceed = useMemo(() => {
    return requiredGroups.every(group => {
      const selected = selections[group.title];
      return Array.isArray(selected) && selected.length === 1;
    });
  }, [selections]);

  const handleProceed = useCallback(() => {
    if (canProceed) {
      onNext();
    }
  }, [canProceed, onNext]);

  return (
    <div className="flex-1 flex flex-col animate-fadeIn">
      <div className="bg-slate-50 rounded-xl p-8 border border-slate-200 mb-6 flex-1 flex flex-col">
        <h2 className="text-xl text-slate-800 font-semibold mb-8">Select Parameters</h2>

        <div className="flex flex-col xl:flex-row gap-8">
          {/* Required */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 flex-1">
            {requiredGroups.map((group) => (
              <div key={group.title} className="space-y-4">
                <h3 className="text-sm font-bold text-slate-800 flex gap-1">
                  {group.title} {group.required && <span className="text-red-400">*</span>}
                </h3>
                <div className="space-y-3">
                  {group.options.map((option) => (
                    <label key={option} className="flex items-start gap-3 cursor-pointer group">
                      <div className={`mt-0.5 w-5 h-5 min-w-[20px] rounded-full border flex items-center justify-center transition-all ${(selections[group.title] || []).includes(option) ? 'border-accent1 bg-blue-50/50 shadow-sm' : 'border-slate-300 bg-white group-hover:border-accent1'}`}
                      >
                        {(selections[group.title] || []).includes(option) && (<div className="w-2 h-2 rounded-full bg-accent1 shadow-[0_0_2px_rgba(29,78,216,0.3)]" />)}
                      </div>
                      <input
                        type="radio"
                        name={group.title}
                        className="hidden"
                        onChange={createSelectionHandler(group.title, option)}
                        checked={(selections[group.title] || []).includes(option)}
                      />
                      <span className={`text-sm font-light leading-tight pt-0.5 transition-colors ${(selections[group.title] || []).includes(option) ? 'text-slate-900 font-medium' : 'text-slate-600 group-hover:text-slate-900'
                        }`}>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Optional */}
          <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 flex-1 transition-all duration-300 ${showOptional ? 'opacity-100 pointer-events-auto' : 'opacity-30 pointer-events-none select-none grayscale'}`}>
            {optionalGroups.map((group) => (
              <div key={group.title} className="space-y-4">
                <h3 className="text-sm font-normal text-slate-800">{group.title}</h3>
                <div className="space-y-3">
                  {group.options.map((option) => (
                    <label key={option} className="flex items-start gap-3 cursor-pointer group">
                      <div className={`mt-0.5 w-5 h-5 min-w-[20px] rounded-full border flex items-center justify-center transition-all ${(selections[group.title] || []).includes(option) ? 'border-accent1 bg-blue-50/50 shadow-sm' : 'border-slate-300 bg-white group-hover:border-accent1'}`}
                      >
                        {(selections[group.title] || []).includes(option) && (<div className="w-2 h-2 rounded-full bg-accent1 shadow-[0_0_2px_rgba(29,78,216,0.3)]" />)}
                      </div>
                      <input
                        type="radio"
                        name={group.title}
                        className="hidden"
                        onChange={createSelectionHandler(group.title, option)}
                        checked={(selections[group.title] || []).includes(option)}
                        disabled={!showOptional}
                      />
                      <span className={`text-sm font-light leading-tight pt-0.5 transition-colors ${(selections[group.title] || []).includes(option) ? 'text-slate-900 font-medium' : 'text-slate-600 group-hover:text-slate-900'
                        }`}>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12">
          <button
            onClick={handleToggleOptionalVisibility}
            className="flex items-center gap-2 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 hover:text-accent1 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm cursor-pointer"
          >
            <span className="text-lg leading-none font-bold text-accent1">{showOptional ? '−' : '+'}</span>
            {showOptional ? 'Remove Optional Parameters' : 'Add Optional Parameters'}
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row justify-between items-center gap-6 mt-4 px-2">
        <label className="flex items-center gap-3 cursor-pointer select-none group">
          <div className={`w-5 h-5 border rounded flex items-center justify-center transition-colors ${includeImages ? 'bg-accent1 border-accent1' : 'bg-white border-slate-300 group-hover:border-accent1'}`}>
            {includeImages && <svg className="h-3.5 w-3.5 text-white" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>}
          </div>
          <input
            type="checkbox"
            className="hidden"
            checked={includeImages}
            onChange={handleToggleIncludeImages}
          />
          <span className={`text-sm transition-colors ${includeImages ? 'text-slate-900 font-medium' : 'text-slate-600 group-hover:text-slate-900'}`}>
            Include Images
          </span>
        </label>

        <button
          title={!canProceed ? "Please select 'Format' and 'Target Audience' before proceeding." : ""}
          onClick={handleProceed}
          className="btn-gradient px-12 py-3 rounded-xl text-sm font-semibold tracking-wide transition-all shadow-md disabled:opacity-50 disabled:shadow-none hover:shadow-lg cursor-pointer disabled:cursor-not-allowed text-white"
          disabled={!canProceed}
        >
          <span className="flex items-center gap-2">Proceed <Image src="/icons/arrow-right-white.svg" alt="" width={16} height={16} className="invert brightness-0" /></span>
        </button>
      </div>
    </div>
  );
}