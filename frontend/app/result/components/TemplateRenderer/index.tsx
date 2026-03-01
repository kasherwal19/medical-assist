import React from 'react';
import { StructuredContent, Section } from '@/app/result/types';

interface TemplateRendererProps {
  content: StructuredContent | string | null | undefined;
  template: string;
  imageUrl?: string;
}

const StyledTitle = ({ children }: { children: React.ReactNode }) => (
  <div className="flex items-center mb-8 relative">
    <div className="w-1.5 self-stretch bg-gradient-to-b from-accent1 to-accent2 mr-4 rounded-full shadow-sm"></div>
    <h1 className="text-3xl font-bold text-slate-900 tracking-tight leading-tight">{children}</h1>
  </div>
);

const SectionItem = ({ section }: { section: Section }) => (
  <div className="mb-8 last:mb-0 group/section">
    <h3 className="text-xl font-semibold text-accent1 mb-3 drop-shadow-sm group-hover/section:text-accent2 transition-colors">{section.heading}</h3>
    <div className="text-slate-700 leading-relaxed text-base space-y-4 whitespace-pre-wrap font-light group-hover/section:text-slate-900 transition-colors">
      {section.paragraph}
    </div>
    {section.sources && section.sources.length > 0 && (
      <div className="mt-5 pt-4 border-t border-slate-200">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 block">
          Sources
        </span>
        <div className="flex flex-wrap gap-2">
          {section.sources.map((source, idx) => (
            <a
              key={idx}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-50 text-accent1 border border-slate-200 hover:bg-white hover:border-accent1 transition-all hover:shadow-sm"
              title={`${source.document_name} - Page ${source.page_no}`}
            >
              <svg
                className="w-3.5 h-3.5 opacity-80"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="truncate max-w-[150px] md:max-w-[250px] text-slate-700">
                {source.document_name}
              </span>
              <span className="text-slate-400 mx-1">|</span>
              <span className="opacity-70 whitespace-nowrap text-slate-500">
                p. {source.page_no}
              </span>
            </a>
          ))}
        </div>
      </div>
    )}
  </div>
);

export const TemplateRenderer: React.FC<TemplateRendererProps> = ({
  content,
  template,
  imageUrl
}) => {
  const containerClasses = "w-full bg-white p-10";

  if (!content) return <div className={`${containerClasses} text-slate-500 italic text-center animate-pulse`}>Generating content...</div>;
  if (typeof content === 'string') return <div className={`${containerClasses} whitespace-pre-wrap text-body`}>{content}</div>;

  const title = content.title;
  const sections = content.sections;

  if (!title || !sections || !Array.isArray(sections)) {
    return <div className={`${containerClasses} text-red-400`}>Error: Invalid content format</div>;
  }

  if (template === 'hero') {
    return (
      <div className={containerClasses}>
        {imageUrl && (
          <div className="relative w-full rounded-xl mb-10 overflow-hidden ring-1 ring-slate-200 shadow-md">
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent z-10"></div>
            <img
              src={imageUrl}
              alt="Hero"
              className="block w-full h-full object-cover max-h-[400px]"
            />
          </div>
        )}
        <StyledTitle>{title}</StyledTitle>
        <div className="space-y-8 relative z-20">
          {sections.map((section: Section, idx: number) => (
            <SectionItem key={idx} section={section} />
          ))}
        </div>
      </div>
    );
  }

  if (template === 'dual') {
    const mid = Math.ceil(sections.length / 2);
    const leftSections = sections.slice(0, mid);
    const rightSections = sections.slice(mid);

    return (
      <div className={containerClasses}>
        <div className="col-span-2 mb-6">
          <StyledTitle>{title}</StyledTitle>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div className="flex flex-col gap-8">
            {imageUrl && (
              <div className="rounded-xl overflow-hidden ring-1 ring-slate-200 shadow-md mb-4">
                <img
                  src={imageUrl}
                  alt="Dual"
                  className="block w-full object-cover"
                />
              </div>
            )}
            {leftSections.map((section: Section, idx: number) => <SectionItem key={idx} section={section} />)}
          </div>
          <div className="flex flex-col gap-8 md:mt-2">
            {rightSections.map((section: Section, idx: number) => <SectionItem key={idx} section={section} />)}
          </div>
        </div>
      </div>
    );
  }

  if (template === 'embedded') {
    return (
      <div className={containerClasses}>
        <StyledTitle>{title}</StyledTitle>
        <div className="block relative mt-8">
          {imageUrl && (
            <div className="md:float-right md:ml-10 mb-8 md:mb-4 w-full md:w-2/5 aspect-[4/3] rounded-xl overflow-hidden ring-1 ring-slate-200 shadow-md">
              <img src={imageUrl} alt="Embedded" className="block w-full h-full object-cover hover:scale-105 transition-transform duration-700" />
            </div>
          )}
          <div className="space-y-8">
            {sections.map((section: Section, idx: number) => (
              <SectionItem key={idx} section={section} />
            ))}
          </div>
          <div className="clear-both"></div>
        </div>
      </div>
    );
  }

  if (template === 'plainhero') {
    return (
      <div className={containerClasses}>
        <StyledTitle>{title}</StyledTitle>
        <div className="space-y-10 mt-8">
          {sections.map((section: Section, idx: number) => (
            <SectionItem key={idx} section={section} />
          ))}
        </div>
      </div>
    );
  }

  if (template === 'plaindual') {
    const mid = Math.ceil(sections.length / 2);
    const col1 = sections.slice(0, mid);
    const col2 = sections.slice(mid);

    return (
      <div className={containerClasses}>
        <StyledTitle>{title}</StyledTitle>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mt-8">
          <div className="space-y-8">
            {col1.map((s: Section, i: number) => <SectionItem key={i} section={s} />)}
          </div>
          <div className="space-y-8">
            {col2.map((s: Section, i: number) => <SectionItem key={i} section={s} />)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={containerClasses}>
      <StyledTitle>{title}</StyledTitle>
      <div className="space-y-6 mt-8">
        {sections.map((s: Section, i: number) => <div key={i} className="text-slate-700 font-light leading-relaxed">{s.paragraph}</div>)}
      </div>
    </div>
  );
};