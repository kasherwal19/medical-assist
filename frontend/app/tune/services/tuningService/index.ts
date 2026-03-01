import { ImageItem, ImagesApiResult, ImageApiResponse, GeneratePayload} from '@/app/tune/types/index';
import { APIResponse, ChatPayload, SessionHistoryData } from '@/app/result/types';
import { API_ENDPOINTS } from '@/data';

const getNextMessageId = (sessionId: string): number => {
  try {
    const cacheKey = `session_history_${sessionId}`; 
    const cached = sessionStorage.getItem(cacheKey);
    if (!cached) return 1;

    const parsed = JSON.parse(cached) as SessionHistoryData;
    
    if (Array.isArray(parsed.messages) && parsed.messages.length > 0) {
       const lastAssistantMsg = [...parsed.messages].findLast(m => m.role === 'assistant');

       const lastId = lastAssistantMsg && typeof lastAssistantMsg.messageId === 'number' 
         ? lastAssistantMsg.messageId 
         : 0;

       return lastId + 1;
    }
    return 1;
  } catch {
    return 1;
  }
};

export const tuningService = {
  async fetchImages(): Promise<ImageItem[]> {
    const res = await fetch(API_ENDPOINTS.IMAGES_API);
    if (!res.ok) throw new Error('Failed to fetch images');

    const data: ImagesApiResult = await res.json();

    return data.results.map((item: ImageApiResponse) => ({
      id: item.id,
      src: item.azure_url,
      azure_url: item.azure_url,
      title: item.filename,
      speciality: item.speciality,
      disease_area: item.disease_area
    }));
  },

  async generateContent(payload: GeneratePayload): Promise<APIResponse> {
    if (!payload.session_id) {
      throw new Error('Missing session_id');
    }

    const { selectedImageId } = payload;
    const message_id = getNextMessageId(payload.session_id);

    const apiPayload: ChatPayload = {
      session_id: payload.session_id,
      user_query: "", 
      images: payload.selectedImageId ? [payload.selectedImageId] : [],
      parameters: payload.parameters || {},
      template: payload.selectedTemplate || 'plainhero',
      message_id: message_id,
      selectedImageId: selectedImageId,
      selectedImageUrl: selectedImageId && /^https?:\/\//i.test(selectedImageId) ? selectedImageId : null,
    };

    const res = await fetch(API_ENDPOINTS.CHAT_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(apiPayload)
    });

    const data = await res.json().catch(() => null);

    if (!res.ok || !data) {
      throw new Error(data || 'Generation failed');
    }

    return data as APIResponse;
  }
};