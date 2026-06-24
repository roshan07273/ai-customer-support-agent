import { useEffect, useMemo, useState } from "react";

import { AdminDashboard } from "./components/AdminDashboard";
import { ChatConsole } from "./components/ChatConsole";
import { CustomerPanel } from "./components/CustomerPanel";
import { fetchCases, fetchCustomers, sendRefundMessage } from "./lib/api";
import type { AgentResponse, ChatBubble, Customer } from "./types";
import "./styles.css";

export default function App() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [messages, setMessages] = useState<ChatBubble[]>([]);
  const [input, setInput] = useState("");
  const [cases, setCases] = useState<AgentResponse[]>([]);
  const [latestCase, setLatestCase] = useState<AgentResponse | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchCustomers().then((data) => {
      setCustomers(data);
      setSelectedId(data[0]?.customer_id ?? "");
    });
    fetchCases().then(setCases).catch(() => setCases([]));
  }, []);

  const selectedCustomer = useMemo(
    () => customers.find((customer) => customer.customer_id === selectedId),
    [customers, selectedId],
  );

  useEffect(() => {
    if (!selectedCustomer) return;
    setMessages([
      {
        id: "welcome",
        role: "agent",
        content: `Hi, I am ready to review ${selectedCustomer.orders[0].item} against the refund policy.`,
      },
    ]);
    setLatestCase(undefined);
  }, [selectedCustomer]);

  async function handleSend(messageOverride?: string, channel: "chat" | "voice" = "chat") {
    const content = (messageOverride ?? input).trim();
    const order = selectedCustomer?.orders[0];
    if (!selectedCustomer || !order || content.length < 3) return;

    setInput("");
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: "customer", content }]);
    setIsLoading(true);
    try {
      const response = await sendRefundMessage({
        customer_id: selectedCustomer.customer_id,
        order_id: order.order_id,
        message: content,
        channel,
      });
      setLatestCase(response);
      setCases((current) => [response, ...current.filter((item) => item.case_id !== response.case_id)]);
      setMessages((current) => [
        ...current,
        {
          id: response.case_id,
          role: "agent",
          content: response.answer,
          decision: response.decision,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "agent",
          content: "I hit a service issue while checking the refund policy. Please try again in a moment.",
          decision: "escalated",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <CustomerPanel customers={customers} selectedId={selectedId} onSelect={setSelectedId} />
      <ChatConsole
        selectedCustomer={selectedCustomer}
        messages={messages}
        input={input}
        isLoading={isLoading}
        onInputChange={setInput}
        onSend={handleSend}
      />
      <AdminDashboard latestCase={latestCase} cases={cases} />
    </div>
  );
}
