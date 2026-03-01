import { API_ENDPOINTS } from '@/data';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch(`${API_ENDPOINTS.IMAGES}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to fetch images' }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}