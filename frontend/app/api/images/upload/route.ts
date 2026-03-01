import { API_ENDPOINTS } from '@/data';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();

    const response = await fetch(
      `${API_ENDPOINTS.IMAGE_UPLOAD}`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Upload failed' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
