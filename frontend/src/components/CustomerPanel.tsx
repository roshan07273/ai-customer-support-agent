import { ShieldCheck, UserRound } from "lucide-react";

import type { Customer } from "../types";

interface Props {
  customers: Customer[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export function CustomerPanel({ customers, selectedId, onSelect }: Props) {
  const selected = customers.find((customer) => customer.customer_id === selectedId);
  const order = selected?.orders[0];

  return (
    <aside className="sidebar">
      <div className="brand-row">
        <div className="brand-mark">NS</div>
        <div>
          <h1>Refund Agent</h1>
          <p>Northstar Commerce</p>
        </div>
      </div>

      <label className="field-label" htmlFor="customer-select">Customer</label>
      <select id="customer-select" value={selectedId} onChange={(event) => onSelect(event.target.value)}>
        {customers.map((customer) => (
          <option key={customer.customer_id} value={customer.customer_id}>
            {customer.name} · {customer.orders[0]?.order_id}
          </option>
        ))}
      </select>

      {selected && order && (
        <div className="profile-block">
          <div className="profile-heading">
            <UserRound size={20} />
            <div>
              <strong>{selected.name}</strong>
              <span>{selected.email}</span>
            </div>
          </div>
          <dl className="metrics-grid">
            <div>
              <dt>Tier</dt>
              <dd>{selected.tier}</dd>
            </div>
            <div>
              <dt>Risk</dt>
              <dd>{selected.risk_score}</dd>
            </div>
            <div>
              <dt>Refunds</dt>
              <dd>{selected.refund_history.length}</dd>
            </div>
            <div>
              <dt>Amount</dt>
              <dd>${order.amount.toFixed(0)}</dd>
            </div>
          </dl>
          <div className="order-card">
            <ShieldCheck size={18} />
            <div>
              <strong>{order.item}</strong>
              <span>{order.status} · {order.payment_status}</span>
              {order.flags.length > 0 && <small>{order.flags.join(", ")}</small>}
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
