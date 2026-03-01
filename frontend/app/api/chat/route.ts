import { API_ENDPOINTS } from '@/data';
import { NextRequest, NextResponse } from 'next/server';

interface ClientPayload {
  session_id: string;
  user_query?: string | null;
  images?: string[];
  parameters?: Record<string, string[]>;
  selectedImageId?: string | null;
  selectedImageUrl?: string | null;
  template: string;
  message_id: number;
}

interface ServerPayload {
  session_id: string;
  user_query: string;
  images: string[];
  parameters: Record<string, string[]>;
  template: string;
  message_id: number;
}

export async function POST(request: NextRequest) {
  try {
    const body: ClientPayload = await request.json();

    const {
      session_id,
      user_query = null,
      parameters,
      selectedImageId,
      selectedImageUrl,
      template,
      message_id
    } = body;

    let imageUrls: string[] = [];
    if (body.images && body.images.length > 0) {
      imageUrls = body.images;
    } 
    else if (selectedImageUrl && /^https?:\/\//i.test(selectedImageUrl)) {
      imageUrls = [selectedImageUrl];
    } 
    else if (selectedImageId && /^https?:\/\//i.test(selectedImageId)) {
      imageUrls = [selectedImageId];
    }

    const backendPayload: ServerPayload = {
      session_id,
      user_query: user_query?.trim() || "", 
      images: imageUrls,
      parameters: parameters || {},
      template: template,
      message_id: message_id
    };

    const response = await fetch(`${API_ENDPOINTS.CHAT}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendPayload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', errorText);
      return NextResponse.json(
        { error: 'Backend error', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Chat Route Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}