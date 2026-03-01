import { SearchResponse } from '@/app/search/types';
import { SearchParams } from '@/app/search/types';
import { API_ENDPOINTS } from '@/data';


export const searchService = {
  async fetchResults(params: SearchParams): Promise<SearchResponse> {
    const res = await fetch(API_ENDPOINTS.PUBMED_SEARCH_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  async triggerProcessing(sessionId: string, documents: string[], userUpload: boolean = false) {
    const response = await fetch(API_ENDPOINTS.TRIGGER_DOC_PROCESSING, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        documents,
        user_upload: userUpload
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response;
  }
};