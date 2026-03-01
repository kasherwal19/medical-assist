"use client";

import Image from "next/image";
import { useState, useCallback, useMemo } from "react";
import { ProcessingStatus } from "@/hooks/useFileUploader";

interface UploadDropzoneProps {
  isProcessing: boolean;
  isUploading: boolean;
  processingStatus: ProcessingStatus;
  processingProgress: string;
  onTriggerFileInput: () => void;
  onUploadFiles: (files: File[]) => void;
}

const getStatusMessage = (status: ProcessingStatus, progress: string) => {
  switch (status) {
    case "uploading":
      return "Uploading files...";
    case "processing":
      return progress || "Processing documents...";
    case "ready":
      return "Documents ready! Redirecting...";
    case "error":
      return "Processing failed";
    default:
      return "";
  }
};

const getStatusColor = (status: ProcessingStatus) => {
  switch (status) {
    case "uploading":
    case "processing":
      return "text-accent2";
    case "ready":
      return "text-green-400";
    case "error":
      return "text-red-400";
    default:
      return "text-muted";
  }
};

export default function UploadDropzone({
  isProcessing,
  isUploading,
  processingStatus,
  processingProgress,
  onTriggerFileInput,
  onUploadFiles,
}: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (!files.length) return;

      onUploadFiles(files);
    },
    [onUploadFiles]
  );

  const handleBrowseClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      e.stopPropagation();
      onTriggerFileInput();
    },
    [onTriggerFileInput]
  );

  const containerHandlers = useMemo(
    () =>
      isProcessing
        ? {}
        : {
          onClick: onTriggerFileInput,
          onDragOver: handleDragOver,
          onDragLeave: handleDragLeave,
          onDrop: handleDrop,
        },
    [isProcessing, onTriggerFileInput, handleDragOver, handleDragLeave, handleDrop]
  );

  const containerClassName = useMemo(
    () =>
      `flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 gap-4 transition-all duration-300 min-h-[220px] ${isProcessing
        ? "border-slate-700 bg-slate-800/50 cursor-wait opacity-80"
        : isDragging
          ? "border-accent1 bg-accent1/10 cursor-pointer shadow-[inset_0_0_20px_rgba(99,102,241,0.2)]"
          : "border-slate-600 bg-slate-800/30 hover:bg-slate-800/60 hover:border-slate-500 cursor-pointer"
      }`,
    [isProcessing, isDragging]
  );

  return (
    <div {...containerHandlers} className={containerClassName}>
      {isProcessing ? (
        <>
          <div className="relative w-12 h-12">
            <div className="absolute inset-0 rounded-full border-2 border-slate-700"></div>
            <div className="absolute inset-0 rounded-full border-t-2 border-accent2 animate-spin"></div>
            <div className="absolute inset-0 rounded-full border-l-2 border-accent1 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          </div>

          <div className="text-center mt-2">
            <p className={`text-lg font-medium tracking-wide ${getStatusColor(processingStatus)}`}>
              {getStatusMessage(processingStatus, processingProgress)}
            </p>
            <p className="text-sm text-muted mt-2">
              Please wait while we process your documents...
            </p>
          </div>
        </>
      ) : (
        <>
          <div className={`p-4 rounded-full transition-colors duration-300 ${isDragging ? 'bg-accent1/20' : 'bg-slate-800'}`}>
            <Image src="/icons/upload-line.svg" alt="Upload" height={28} width={28} className="opacity-80" />
          </div>

          <div className="text-center">
            <p className="text-body text-lg font-medium mb-1">
              {isDragging ? "Drop files here" : "Drag & drop files here"}
            </p>
            <p className="text-muted text-sm">
              or browse your system to select
            </p>
          </div>

          <button
            type="button"
            onClick={handleBrowseClick}
            disabled={isUploading}
            className="mt-2 text-accent2 border border-accent2/30 bg-accent2/10 px-6 py-2 rounded-lg font-medium hover:bg-accent2/20 hover:border-accent2/50 transition-all disabled:opacity-50 tracking-wide text-sm"
          >
            Browse Files
          </button>
        </>
      )}
    </div>
  );
}