import type { AgentResponse, Customer } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export async function fetchCustomers(): Promise<Customer[]> {
  const response = await fetch(`${API_BASE}/customers`);
  if (!response.ok) throw new Error("Unable to load customer profiles");
  return response.json();
}

export async function sendRefundMessage(payload: {
  customer_id: string;
  order_id: string;
  message: string;
  channel?: "chat" | "voice";
}): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Agent request failed");
  return response.json();
}

export async function fetchCases(): Promise<AgentResponse[]> {
  const response = await fetch(`${API_BASE}/cases`);
  if (!response.ok) throw new Error("Unable to load cases");
  return response.json();
}
