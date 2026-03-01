import { API_ENDPOINTS } from "@/data";
import { NextRequest, NextResponse } from "next/server";


export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();

    const backendResponse = await fetch(`${API_ENDPOINTS.FILE_UPLOAD}`, {
      method: "POST",
      body: formData,
    });

    const data = await backendResponse.json();

    return NextResponse.json(data, { status: backendResponse.status });

  } catch (error) {
    console.error("Error connecting to Backend", error);
    return NextResponse.json(
      { error: "Failed to connect to backend service" },
      { status: 500 }
    );
  }
}