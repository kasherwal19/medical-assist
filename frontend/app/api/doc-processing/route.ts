import { API_ENDPOINTS } from '@/data';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { session_id, documents, user_upload = false } = body;

    if (!session_id || !documents || !Array.isArray(documents)) {
      return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
    }

    const response = await fetch(`${API_ENDPOINTS.TRIGGER_DOC_PROCESSING}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id, documents, user_upload }),
    });

    // Handle response from the external API
    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to trigger document processing' }, { status: response.status });
    }

    const result = await response.json();
    return NextResponse.json(result); // Forward the result back to the client
  } catch (error) {
    console.error('Error in API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}