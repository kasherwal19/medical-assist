'use client';

import { useState, useRef, useEffect } from 'react';

interface FileDropdownProps {
  files: string[];
  onSelect: (filename: string) => void;
  selectedFile: string | null;
}

export default function FileDropdown({ files, onSelect, selectedFile }: FileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscKey);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscKey);
    };
  }, []);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const handleSelect = (file: string) => {
    onSelect(file);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full" ref={ref}>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={handleToggle}
        className={`w-full flex items-center justify-between px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 cursor-pointer ${isOpen
          ? 'bg-blue-50 border-accent1 shadow-sm border'
          : 'bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 shadow-sm'
          }`}
      >
        <div className="flex items-center gap-2 text-slate-800 font-medium truncate">
          <span className="truncate">
            {selectedFile || files[0] || 'No file available'}
          </span>
        </div>

        <svg
          className={`w-4 h-4 ml-2 text-slate-500 transition-transform duration-300 ${isOpen ? 'rotate-180 text-accent1' : ''
            }`}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.25a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {isOpen && (
        <ul
          role="listbox"
          className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-lg max-h-60 overflow-y-auto custom-scrollbar animate-fadeIn py-1"
        >
          {files.length === 0 ? (
            <li className="px-4 py-3 text-sm text-slate-500 italic">
              No files found
            </li>
          ) : (
            files.map((file) => (
              <li key={file}>
                <button
                  role="option"
                  aria-selected={selectedFile === file}
                  onClick={handleSelect.bind(null, file)}
                  className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center justify-between cursor-pointer ${file === selectedFile
                    ? 'text-accent1 font-semibold bg-blue-50 border-l-2 border-accent1'
                    : 'text-slate-700 hover:bg-slate-50 hover:text-accent1 border-l-2 border-transparent'
                    }`}
                >
                  <span className="truncate pr-2">{file}</span>
                  {file === selectedFile && (
                    <svg className="w-4 h-4 text-accent1 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
