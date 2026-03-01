import { TimeRange } from "@/types";

export const TIME_RANGES: TimeRange[] = [
  { label: "24 Hours", value: 1 },
  { label: "48 Hours", value: 2 },
  { label: "1 Week", value: 7 },
];

const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  CHAT_API: `${BACKEND_BASE}/api/chat`,
  CHAT: `${BACKEND_BASE}/api/chat`,

  TRIGGER_DOC_PROCESSING: `${BACKEND_BASE}/api/trigger-doc-processing`,
  DOC_PROCESSING: `${BACKEND_BASE}/api/doc-processing`,

  IMAGES_API: `${BACKEND_BASE}/api/images`,
  IMAGES: `${BACKEND_BASE}/api/images`,
  IMAGE_UPLOAD_API: `${BACKEND_BASE}/api/images/upload`,
  IMAGE_UPLOAD: `${BACKEND_BASE}/api/images/upload`,

  NEWS_HEALTH: `${BACKEND_BASE}/api/news/health`,
  NEWS_HEALTH_API: `${BACKEND_BASE}/api/news/health`,
  NEWS: `${BACKEND_BASE}/api/news`,

  SEARCH_API: `${BACKEND_BASE}/api/search`,
  SEARCH: `${BACKEND_BASE}/api/search`,
  PUBMED_SEARCH_API: `${BACKEND_BASE}/api/pubmed/search`,
  PUBMED_SEARCH: `${BACKEND_BASE}/api/pubmed/search`,

  FILE_UPLOAD_API: `${BACKEND_BASE}/api/upload-file`,
  FILE_UPLOAD: `${BACKEND_BASE}/api/upload-file`,

  VIEW_API: `${BACKEND_BASE}/api/view`,
  VIEW: `${BACKEND_BASE}/api/view`,

};
