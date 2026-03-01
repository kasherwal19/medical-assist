import { useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { 
  uploadFilesToApi, 
  triggerDocProcessing 
} from "@/services/uploadService";

type UploadableFiles = File[];

export type ProcessingStatus = 'idle' | 'uploading' | 'processing' | 'ready' | 'error';

const VALIDATION_CONFIG = {
  allowedTypes: [".pdf"],
  maxSizeMB: 10,
};

export const useFileUploader = () => {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>('idle');
  const [processingProgress, setProcessingProgress] = useState<string>('');

  const isBrowser = typeof window !== "undefined";

  const triggerFileInput = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const validateFiles = useCallback((files: File[]) => {
    const { allowedTypes, maxSizeMB } = VALIDATION_CONFIG;

    const valid: File[] = [];
    const errors: string[] = [];

    files.forEach((file) => {
      const ext = file.name.split(".").pop()?.toLowerCase();

      if (!ext || !allowedTypes.includes(`.${ext}`)) {
        errors.push(`${file.name}: unsupported file type`);
        return;
      }

      if (file.size / (1024 * 1024) > maxSizeMB) {
        errors.push(`${file.name}: exceeds ${maxSizeMB} MB`);
        return;
      }

      valid.push(file);
    });

    return { valid, errors };
  }, []);

  const uploadFiles = useCallback(
    async (files: UploadableFiles) => {
      setErrors([]);
      setProcessingStatus('idle');
      setProcessingProgress('');

      const { valid, errors } = validateFiles(files);

      if (errors.length) {
        setErrors(errors);
        return;
      }

      if (!valid.length) return;

      // Step 1: Upload files
      setIsUploading(true);
      setProcessingStatus('uploading');
      setProcessingProgress('Uploading files...');

      try {
        const { ok, data } = await uploadFilesToApi(valid);

        if (!ok || !data.session_id) {
          setErrors([data?.error ?? "Upload failed. Please try again."]);
          setProcessingStatus('error');
          setIsUploading(false);
          return;
        }

        // Store uploaded documents
        if (isBrowser && data.documents) {
          sessionStorage.setItem(
            "selectedDocuments",
            JSON.stringify(data.documents)
          );
        }

        // Step 2: Trigger document processing
        setProcessingStatus('processing');
        setProcessingProgress('Processing documents... This may take a few minutes.');

        const { ok: procOk } = await triggerDocProcessing(
          data.session_id,
          data.documents,
          true
        );

        if (!procOk) {
          console.error('Failed to trigger document processing');
          setErrors(['Failed to start document processing']);
          setProcessingStatus('error');
          setIsUploading(false);
          return;
        }

        // Step 3: Navigate to tune page (processing happens in background)
        setProcessingStatus('ready');
        setProcessingProgress('Redirecting to tune page...');
        
        router.push(`/tune?session_id=${data.session_id}`);

      } catch (err) {
        console.error('Upload error:', err);
        setErrors(["Network error while uploading files"]);
        setProcessingStatus('error');
      } finally {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    },
    [router, validateFiles, isBrowser]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) return;
      uploadFiles(Array.from(e.target.files));
    },
    [uploadFiles]
  );

  return {
    fileInputRef,
    isUploading,
    errors,
    processingStatus,
    processingProgress,
    triggerFileInput,
    handleFileChange,
    uploadFiles,
  };
};
 