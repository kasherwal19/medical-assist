"use client";

import Image from "next/image";
import { useCallback, useMemo } from "react";
import { useFileUploader } from "@/hooks/useFileUploader";
import UploadDropzone from "../UploadDropZone";

export default function UploadSection() {
  const {
    fileInputRef,
    isUploading,
    triggerFileInput,
    uploadFiles,
    errors,
    handleFileChange,
    processingStatus,
    processingProgress,
  } = useFileUploader();

  const isProcessing = useMemo(
    () => processingStatus === "uploading" || processingStatus === "processing",
    [processingStatus]
  );

  const handleTriggerFileInput = useCallback(() => {
    triggerFileInput();
  }, [triggerFileInput]);

  const handleUploadFiles = useCallback(
    (files: File[]) => {
      uploadFiles(files);
    },
    [uploadFiles]
  );

  return (
    <div className="glass-panel glass-panel-hover p-8 rounded-2xl flex flex-col h-full animate-slideUp" style={{ animationDelay: '0.3s' }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-blue-50 p-2.5 rounded-lg border border-blue-100 shadow-sm">
          <Image src="/icons/upload-file.svg" alt="Upload" height={28} width={28} className="opacity-80 drop-shadow-sm" />
        </div>
        <h2 className="text-2xl font-semibold text-slate-800 tracking-tight">
          Upload Reference Documents
        </h2>
      </div>

      <div className="flex-1 flex flex-col mt-auto">
        <input
          type="file"
          multiple
          accept=".pdf"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          disabled={isProcessing}
        />

        <UploadDropzone
          isProcessing={isProcessing}
          isUploading={isUploading}
          processingStatus={processingStatus}
          processingProgress={processingProgress}
          onTriggerFileInput={handleTriggerFileInput}
          onUploadFiles={handleUploadFiles}
        />

        {errors.length > 0 && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 shadow-sm">
            <ul className="list-disc list-inside space-y-1">
              {errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-between items-center text-xs text-slate-500 font-medium mt-4 pt-4 border-t border-slate-200">
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Maximum size: 10 MB</span>
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Supported: .pdf</span>
        </div>
      </div>
    </div>
  );
}