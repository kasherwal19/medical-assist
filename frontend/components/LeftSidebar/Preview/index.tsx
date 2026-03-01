'use client';

import React, { useState } from 'react';
import { FileText, AlertCircle, Loader2 } from 'lucide-react';

interface PreviewProps {
  documentId: string;
  url: string;
  userId?: string;
}

const PreviewComponent: React.FC<PreviewProps> = ({ documentId, url }) => {
  const [loading, setLoading] = useState(true);

  const [prevUrl, setPrevUrl] = useState(url);

  const handleLoading = () => {
    setLoading(false);
  };

  if (url !== prevUrl) {
    setPrevUrl(url);
    setLoading(true);
  }

  if (!documentId) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-500 bg-slate-50 rounded-xl border-2 border-dashed border-slate-200 m-6">
        <FileText className="w-12 h-12 mb-4 opacity-40 text-slate-400" />
        <p className="text-sm font-medium tracking-wide">Select a document to preview</p>
      </div>
    );
  }

  if (!url) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-slate-50 m-6 rounded-xl border border-slate-200">
        <AlertCircle className="w-12 h-12 text-slate-500 mb-4" />
        <h3 className="text-slate-800 font-semibold mb-2">Preview Unavailable</h3>
        <p className="text-slate-500 text-sm">No preview URL found for this document.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-slate-100 overflow-hidden">

      {loading && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-white/80 backdrop-blur-md">
          <Loader2 className="w-10 h-10 animate-spin text-accent1 mb-4" />
          <p className="text-xs font-semibold text-accent1 uppercase tracking-widest animate-pulse">
            Loading Document...
          </p>
        </div>
      )}

      <iframe
        src={url}
        className={`w-full h-full border-none transition-opacity duration-500 ${loading ? 'opacity-0' : 'opacity-100 bg-white'}`}
        title={`Preview of ${documentId}`}
        onLoad={handleLoading}
      />
    </div>
  );
};

export default PreviewComponent;