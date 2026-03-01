import React, { useState, useCallback, ChangeEvent } from 'react';
import { StructuredContent, Section } from '@/app/result/types';

interface ContentEditorProps {
  content: StructuredContent;
  onSave: (newContent: StructuredContent) => void;
  onCancel: () => void;
}

export const ContentEditor: React.FC<ContentEditorProps> = ({ content, onSave, onCancel }) => {
  const [title, setTitle] = useState(content.title || '');
  const [sections, setSections] = useState<Section[]>(content.sections || []);
  const handleTitleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setTitle(e.target.value);
    },
    []
  );

  const handleSectionInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const index = Number(e.currentTarget.dataset.index);
      const field = e.currentTarget.dataset.field as keyof Section;
      const value = e.currentTarget.value;

      setSections((prev) => {
        const updated = [...prev];
        updated[index] = {
          ...updated[index],
          [field]: value,
        };
        return updated;
      });
    },
    []
  );

  const handleSave = useCallback(() => {
    onSave({ title, sections });
  }, [onSave, title, sections]);

  return (
    <div className="w-full bg-white p-8 rounded-2xl rounded-tl-none border border-slate-200 shadow-sm overflow-hidden relative">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent1 to-accent2 pointer-events-none z-10" />

      <div className="mb-8">
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          Document Title
        </label>
        <input
          type="text"
          value={title}
          onChange={handleTitleChange}
          className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-accent1 focus:border-accent1 focus:bg-white outline-none transition-all font-bold text-lg text-slate-800 placeholder-slate-400 shadow-sm"
          placeholder="Enter a descriptive title..."
        />
      </div>

      <div className="space-y-6">
        {sections.map((section, idx) => (
          <div
            key={idx}
            className="p-6 bg-slate-50 rounded-xl border border-slate-200 shadow-sm"
          >
            <div className="mb-4">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
                Section Heading
              </label>
              <input
                type="text"
                value={section.heading}
                data-index={idx}
                data-field="heading"
                onChange={handleSectionInputChange}
                className="w-full p-3 bg-white border border-slate-300 rounded-lg focus:ring-1 focus:ring-accent1 focus:border-accent1 outline-none text-slate-800 font-medium placeholder-slate-400 transition-colors shadow-sm"
                placeholder="e.g. Overview"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
                Content Paragraph
              </label>
              <textarea
                rows={5}
                value={section.paragraph}
                data-index={idx}
                data-field="paragraph"
                onChange={handleSectionInputChange}
                className="w-full p-4 bg-white border border-slate-300 rounded-lg focus:ring-1 focus:ring-accent1 focus:border-accent1 outline-none text-slate-700 leading-relaxed resize-y custom-scrollbar transition-colors shadow-sm"
                placeholder="Write the section content here..."
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end gap-4 mt-10 pt-6 border-t border-slate-200">
        <button
          onClick={onCancel}
          className="px-6 py-2.5 text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 hover:text-accent1 font-medium transition-colors shadow-sm cursor-pointer"
        >
          Cancel Edits
        </button>
        <button
          onClick={handleSave}
          className="btn-gradient px-8 py-2.5 text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all cursor-pointer"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};