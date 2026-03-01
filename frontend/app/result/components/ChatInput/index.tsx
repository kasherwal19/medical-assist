import { useState, KeyboardEvent, ChangeEvent } from 'react';
import Image from 'next/image';

interface ChatInputProps {
  onSend: (query: string) => void;
  isSending: boolean;
  onChangeParameters: () => void;
}

export const ChatInput = ({ onSend, isSending, onChangeParameters }: ChatInputProps) => {
  const [query, setQuery] = useState('');

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isSending) {
      handleSendClick();
    }
  };

  const handleSendClick = () => {
    if (query.trim() && !isSending) {
      onSend(query);
      setQuery('');
    }
  };

  return (
    <div className="pt-4 pb-2 shrink-0 z-10 w-full mt-2">
      <div className="max-w-7xl mx-auto w-full">
        <div className={`bg-white border border-slate-200 rounded-2xl flex items-center p-2 pl-4 shadow-sm transition-all duration-300 ${isSending ? 'opacity-70 cursor-not-allowed' : 'hover:border-accent1 hover:shadow-md'}`}>
          <input
            type="text"
            placeholder={isSending ? "Generating response..." : "Ask AI to modify the draft..."}
            value={query}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={isSending}
            className="flex-1 outline-none text-base text-slate-800 bg-transparent placeholder-slate-400 disabled:cursor-not-allowed"
          />

          <div className="flex items-center gap-2 pl-2">
            <button
              className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-50 hover:text-accent1 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed hidden sm:flex"
              onClick={onChangeParameters}
              disabled={isSending}
            >
              <Image src="/icons/edit.svg" alt="" width={14} height={14} className="opacity-70" />
              Tune Output
            </button>

            <button
              className="p-2.5 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer disabled:bg-slate-100 disabled:text-slate-400 bg-gradient-to-r from-accent1 to-accent2 hover:shadow-md text-white shadow-sm"
              onClick={handleSendClick}
              disabled={isSending || !query.trim()}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};