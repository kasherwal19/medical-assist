import { NextResponse } from "next/server";
import { API_ENDPOINTS } from "@/data";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const days = searchParams.get("days") || "7";
  try {
    const res = await fetch(`${API_ENDPOINTS.NEWS_HEALTH}?days=${days}&limit=10`, {
      headers: {
        "Content-Type": "application/json",
      },
      next: { revalidate: 300 } 
    });

    if (!res.ok) {
      throw new Error(`FastAPI responded with status: ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("Error fetching news:", error);
    return NextResponse.json(
      { error: "Failed to fetch news updates" },
      { status: 500 }
    );
  }
}