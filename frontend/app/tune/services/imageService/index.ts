import { ImageItem } from '@/app/tune/types/index';
import { UploadApiResponse } from '@/app/tune/types';
import { API_ENDPOINTS } from '@/data';

export const uploadImagesToApi = async (files: FileList): Promise<ImageItem[]> => {
  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append('files', file);
  });

  const res = await fetch(API_ENDPOINTS.IMAGE_UPLOAD_API, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) throw new Error('Upload failed');

  const data = (await res.json()) as UploadApiResponse;

  return data.uploaded_images.map((img) => ({
    id: img.id,
    src: img.view_url,
    azure_url: img.view_url,
    title: img.filename,
    speciality: 'uploaded',
    disease_area: [],
  }));
};