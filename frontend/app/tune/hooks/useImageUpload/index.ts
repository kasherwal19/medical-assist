import { useState } from 'react';
import { ImageItem } from '@/app/tune/types/index';
import { uploadImagesToApi } from '@/app/tune/services/imageService/index';

export const useImageUpload = () => {
  const [isUploading, setIsUploading] = useState(false);

  const uploadImages = async (files: FileList | null): Promise<ImageItem[] | null> => {
    if (!files || files.length === 0) return null;

    setIsUploading(true);
    try {
      return await uploadImagesToApi(files);
    } catch (err) {
      console.error(err);
      return null;
    } finally {
      setIsUploading(false);
    }
  };

  return { isUploading, uploadImages };
};