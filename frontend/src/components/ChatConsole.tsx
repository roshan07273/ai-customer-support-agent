import { Mic, Send, Sparkles } from "lucide-react";

import type { ChatBubble, Customer } from "../types";

const demoPrompts = [
  { label: "Standard refund", text: "The headphones arrived, but the right ear cup is defective. I would like a refund please." },
  { label: "Policy violation", text: "I used the digital meal plan already, but I changed my mind and want my money back." },
  { label: "Escalation case", text: "The espresso machine is defective and I want to return it for a refund." },
];

interface Props {
  selectedCustomer?: Customer;
  messages: ChatBubble[];
  input: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: (message?: string, channel?: "chat" | "voice") => void;
}

export function ChatConsole({ selectedCustomer, messages, input, isLoading, onInputChange, onSend }: Props) {
  return (
    <main className="chat-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Customer chat</p>
          <h2>{selectedCustomer ? `Case for ${selectedCustomer.name}` : "Loading CRM"}</h2>
        </div>
        <span className="live-pill">Live tools</span>
      </div>

      <div className="prompt-row">
        {demoPrompts.map((prompt) => (
          <button key={prompt.label} type="button" onClick={() => onSend(prompt.text)} disabled={isLoading}>
            <Sparkles size={16} />
            {prompt.label}
          </button>
        ))}
      </div>

      <div className="conversation">
        {messages.map((message) => (
          <div key={message.id} className={`bubble ${message.role}`}>
            <span>{message.role === "customer" ? "Customer" : "Agent"}</span>
            <p>{message.content}</p>
            {message.decision && <strong className={`decision ${message.decision}`}>{message.decision}</strong>}
          </div>
        ))}
        {isLoading && (
          <div className="bubble agent pending">
            <span>Agent</span>
            <p>Checking CRM, order state, and refund policy...</p>
          </div>
        )}
      </div>

      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          onSend();
        }}
      >
        <button type="button" title="Voice demo channel" onClick={() => onSend(input || "I am speaking to request a refund.", "voice")} disabled={isLoading}>
          <Mic size={19} />
        </button>
        <input
          value={input}
          onChange={(event) => onInputChange(event.target.value)}
          placeholder="Type the customer's refund request..."
        />
        <button type="submit" title="Send message" disabled={isLoading || input.trim().length < 3}>
          <Send size={19} />
        </button>
      </form>
    </main>
  );
}
