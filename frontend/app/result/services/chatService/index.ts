import { API_ENDPOINTS } from '@/data'

const handleResponse = async (res: Response) => {
  if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
  return res.json();
};

export const chatService = {
  fetchDocumentViewUrl: async (pmc_id: string): Promise<string> => {
    try {
      const res = await fetch(`${API_ENDPOINTS.VIEW_API}/${encodeURIComponent(pmc_id)}`, {
        method: 'GET',
      });
      const data = await handleResponse(res);
      return data.view_url || '';
    } catch (error) {
      console.error('Failed to fetch document URL', error);
      return '';
    }
  },
};