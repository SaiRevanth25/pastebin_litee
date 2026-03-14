const API_BASE_URL = "https://pastebin-lite-kanm.onrender.com";

export interface CreatePasteRequest {
  content: string;
  ttl_seconds?: number;
  max_views?: number;
}

export interface CreatePasteResponse {
  id: string;
  url: string;
}

export interface GetPasteResponse {
  content: string;
  remaining_views: number;
  expires_at: string;
}

export interface ErrorResponse {
  detail: string;
}

export async function createPaste(
  data: CreatePasteRequest
): Promise<CreatePasteResponse> {
  const response = await fetch(`${API_BASE_URL}/api/pastes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to create paste");
  }

  return response.json();
}

export async function getPaste(
  id: string
): Promise<GetPasteResponse | ErrorResponse> {
  const response = await fetch(`${API_BASE_URL}/api/pastes/${id}`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch paste");
  }

  return response.json();
}
