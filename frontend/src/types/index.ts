export type Decision = "approved" | "denied" | "escalated";

export interface Order {
  order_id: string;
  item: string;
  category: string;
  amount: number;
  currency: string;
  purchase_date: string;
  delivery_date: string;
  status: string;
  payment_status: string;
  refund_status: string;
  warranty_days: number;
  flags: string[];
}

export interface Customer {
  customer_id: string;
  name: string;
  email: string;
  tier: string;
  risk_score: number;
  orders: Order[];
  refund_history: Array<{
    order_id: string;
    date: string;
    amount: number;
    reason: string;
  }>;
}

export interface ToolTrace {
  name: string;
  status: "success" | "warning" | "failure";
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  started_at: string;
  completed_at: string;
}

export interface AgentResponse {
  case_id: string;
  decision: Decision;
  customer_id: string;
  order_id: string;
  answer: string;
  confidence: number;
  tool_traces: ToolTrace[];
  policy_citations: string[];
  created_at: string;
}

export interface ChatBubble {
  id: string;
  role: "customer" | "agent";
  content: string;
  decision?: Decision;
}
