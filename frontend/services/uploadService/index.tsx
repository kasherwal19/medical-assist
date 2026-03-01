import { API_ENDPOINTS } from "@/data";

export const uploadFilesToApi = async (files: File[]) => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(API_ENDPOINTS.FILE_UPLOAD_API, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  return { ok: response.ok, data };
};

export const triggerDocProcessing = async (
  sessionId: string,
  documents: string[],
  userUpload: boolean = true
) => {
  const response = await fetch(API_ENDPOINTS.TRIGGER_DOC_PROCESSING, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      documents,
      user_upload: userUpload
    }),
  });

  return { ok: response.ok, data: await response.json() };
};
