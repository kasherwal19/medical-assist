'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import FileDropdown from './Dropdown';
import PreviewComponent from './Preview';

export interface Files {
  id: string;
  filename: string;
  createdAt: string;
  url: string;
}

interface LeftSidebarProps {
  files: Files[];
  sessionId: string;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ files, sessionId }) => {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  const tempUserId = sessionId;

  // Derive the active ID: use user selection or default to first file
  const activeFileId = selectedFileId ?? (files.length > 0 ? files[0].id : null);

  // Find the full file object
  const activeFile = files.find(f => f.id === activeFileId);
  const activeFileName = activeFile ? activeFile.filename : null;

  // Handler for dropdown selection
  const handleFileSelect = (filename: string) => {
    const match = files.find((file) => file.filename === filename);
    if (match) {
      setSelectedFileId(match.id);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-2xl shadow border border-slate-200 overflow-hidden">

      {/* Header with Back Button and Dropdown */}
      <div className="px-5 py-4 flex items-center gap-3 border-b border-slate-200 bg-slate-50 z-10 shadow-sm">
        <Link href={`/tune?session_id=${sessionId}`} className="text-slate-500 hover:text-slate-900 transition-colors p-2 rounded-lg hover:bg-slate-200 -ml-2 cursor-pointer">
          <Image
            src="/icons/arrow-left.svg"
            alt="Back to Tuning"
            width={18}
            height={18}
            className="opacity-70"
          />
        </Link>

        <div className="flex-1 w-full min-w-0">
          <FileDropdown
            files={files.map((f) => f.filename)}
            onSelect={handleFileSelect}
            selectedFile={activeFileName}
          />
        </div>
      </div>

      <div className="flex-1 overflow-hidden bg-white relative">
        {activeFile ? (
          <PreviewComponent
            documentId={activeFile.id}
            userId={tempUserId}
            url={activeFile.url}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-500 text-sm font-medium">
            No document selected
          </div>
        )}
      </div>
    </div>
  );
};

export default LeftSidebar;