import { API_ENDPOINTS } from '@/data';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { pmc_id } = body;

    if (!pmc_id) {
      return NextResponse.json(
        { error: 'pmc_id is required' },
        { status: 400 }
      );
    }

    const res = await fetch(
      `${API_ENDPOINTS.VIEW}/${encodeURIComponent(pmc_id)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!res.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch document URL' },
        { status: res.status }
      );
    }

    const data = await res.json();

    return NextResponse.json({
      view_url: data.view_url,
    });
  } catch (error) {
    console.error('Error in /api/view:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
