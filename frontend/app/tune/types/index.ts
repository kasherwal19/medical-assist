export type ImageItem = {
  id: string;
  src: string;
  azure_url: string;
  title: string;
  speciality: string;
  disease_area: string[];
};

export type ImageApiResponse = {
  id: string;
  azure_url: string;
  filename: string;
  speciality: string;
  disease_area: string[];
};

export type ImagesApiResult = {
  results: ImageApiResponse[];
};

export type UploadedImageApiItem = {
  id: string;
  filename: string;
  size_bytes: number;
  view_url: string;
  status: string;
};

export type UploadApiResponse = {
  session_id: string;
  total_uploaded: number;
  total_failed: number;
  uploaded_images: UploadedImageApiItem[];
  failed_images: unknown[];
  status: string;
};

export type TemplateStepProps = {
  selectedTemplate: string | null;
  setSelectedTemplate: React.Dispatch<React.SetStateAction<string | null>>;
  onNext: () => void;
  isGenerating: boolean;
  includeImages: boolean;
};

export interface GeneratePayload {
  session_id: string | null;
  parameters: Record<string, string[]>;
  selectedImageId: string | null;
  selectedTemplate: string;
}