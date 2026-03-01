'use client';

import { useMemo } from 'react';
import Image from 'next/image';
import { templates } from '@/app/tune/data/template';
import { TemplateStepProps } from '@/app/tune/types';


export default function TemplateStep({
  selectedTemplate,
  setSelectedTemplate,
  onNext,
  isGenerating,
  includeImages
}: TemplateStepProps) {

  const filteredTemplates = useMemo(() => {
    return templates.filter((t) => t.withImage === includeImages);
  }, [includeImages]);

  // The createSelectHandler is no longer needed as the onClick is inline
  // const createSelectHandler = (id: string) => () => {
  //   setSelectedTemplate(id);
  // };

  return (
    <div className="flex-1 flex flex-col h-full animate-fadeIn min-h-[500px]">
      <div className="bg-slate-50 rounded-xl p-8 border border-slate-200 mb-6 flex-1 flex flex-col">
        <h2 className="text-xl text-slate-800 font-semibold mb-8">Choose Template</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 flex-1 content-start">
          {filteredTemplates.map((template) => (
            <div
              key={template.id}
              onClick={() => setSelectedTemplate(template.id)}
              className={`border-2 rounded-2xl cursor-pointer transition-all duration-300 h-64 flex flex-col justify-between overflow-hidden relative group ${selectedTemplate === template.id
                ? "border-accent1 shadow-sm bg-blue-50/50"
                : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
                }`}
            >
              <div className="p-4 flex flex-col items-center justify-center flex-1 z-10 bg-white">
                <Image
                  src={`/templates/${template.id}.svg`}
                  alt={template.label}
                  width={150}
                  height={150}
                  className={`object-contain transition-transform duration-300 group-hover:scale-105 mix-blend-multiply ${selectedTemplate === template.id ? 'opacity-100' : 'opacity-80 grayscale'}`}
                />
              </div>

              {selectedTemplate === template.id && (
                <div className="absolute top-3 right-3 w-6 h-6 bg-accent1 rounded-full flex items-center justify-center shadow-md z-20">
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                </div>
              )}

              <div className={`p-4 text-center border-t transition-colors z-10 ${selectedTemplate === template.id ? 'bg-blue-50/80 border-blue-100' : 'bg-slate-50/80 border-slate-100'}`}>
                <h3 className={`font-semibold text-sm ${selectedTemplate === template.id ? 'text-accent1' : 'text-slate-600'}`}>{template.label}</h3>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end mt-4 px-2">
        <button
          onClick={onNext}
          disabled={!selectedTemplate || isGenerating}
          className={`btn-gradient px-12 py-3 rounded-xl text-sm font-semibold tracking-wide transition-all shadow-md disabled:opacity-50 hover:shadow-lg cursor-pointer text-white disabled:cursor-not-allowed`}
        >
          {isGenerating ? (
            <span className="flex items-center gap-2"><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</span>
          ) : (
            "Generate Final Output"
          )}
        </button>
      </div>
    </div>
  );
}