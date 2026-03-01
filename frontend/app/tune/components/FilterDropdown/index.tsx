import { useState, useRef, useEffect } from "react";
import Image from "next/image";

type FilterDropdownProps = {
  label: string;
  options: string[];
  value: string | null;
  onChange: (val: string) => void;
};

export default function FilterDropdown({ label, options, value, onChange }: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (option: string) => {
    if (value === option) {
      onChange(''); // Deselect
    } else {
      onChange(option);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-4 py-2 border rounded-lg text-sm transition-colors ${value
          ? "border-accent1 bg-blue-50 text-accent1 shadow-sm"
          : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
      >
        <span className={value ? "font-semibold" : "font-medium"}>
          {value || label}
        </span>
        <div className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""} ${value ? "opacity-100" : "opacity-60"}`}>
          <Image
            src="/icons/arrow-down.svg"
            alt="Dropdown"
            height={12}
            width={12}
            className={value ? "brightness-0 invert-0 opacity-80" : "invert opacity-50"}
          />
        </div>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg z-20 py-2 max-h-60 overflow-y-auto hidden-scrollbar animate-fadeIn">
          {options.length === 0 ? (
            <div className="px-4 py-3 text-sm text-slate-500">No options available</div>
          ) : (
            options.map((option) => (
              <button
                key={option}
                onClick={() => handleSelect(option)}
                className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center justify-between ${value === option
                  ? "bg-blue-50 font-semibold text-accent1"
                  : "text-slate-700 hover:bg-slate-50 hover:text-accent1"
                  }`}
              >
                <span className="truncate pr-2">{option}</span>
                {value === option && (
                  <svg className="w-4 h-4 text-accent1 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
