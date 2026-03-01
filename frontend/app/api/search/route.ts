import { API_ENDPOINTS } from '@/data';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { keyword, offset, limit, timeframe } = body;

    const response = await fetch(`${API_ENDPOINTS.PUBMED_SEARCH}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        keyword: keyword || '',
        offset: offset || 0,
        limit: limit || 10,
        timeframe: timeframe || '7d'
      }),
    });

    // Check for response errors
    if (!response.ok) {
      console.error('Failed to fetch from the backend:', response.statusText);
      return NextResponse.json({ error: 'Failed to fetch results from backend' }, { status: response.status });
    }

    // Parse the response data
    const data = await response.json();

    // Return the results back to the client
    return NextResponse.json(data);
  } catch {
    console.error('Error in search route:');
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}