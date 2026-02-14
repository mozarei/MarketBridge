export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export const DEV_USER_ID = process.env.NEXT_PUBLIC_DEV_USER_ID ?? "1";

export type SyncEvent = {
  id: number;
  user_id: number | null;
  item_id: number | null;
  channel_listing_id: number | null;
  order_id: number | null;
  job_id: string | null;
  event_type: string;
  status: "started" | "succeeded" | "failed";
  message: string | null;
  payload: Record<string, unknown> | null;
  created_at: string;
};

export async function getEvents(limit = 100): Promise<SyncEvent[]> {
  const response = await fetch(`${API_BASE_URL}/events?limit=${limit}`, {
    headers: {
      "X-User-Id": DEV_USER_ID,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to load events (${response.status})`);
  }

  return (await response.json()) as SyncEvent[];
}
