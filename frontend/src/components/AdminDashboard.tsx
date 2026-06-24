import { Activity, AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";

import type { AgentResponse, ToolTrace } from "../types";

interface Props {
  latestCase?: AgentResponse;
  cases: AgentResponse[];
}

const iconForTrace = (trace: ToolTrace) => {
  if (trace.status === "success") return <CheckCircle2 size={18} />;
  if (trace.status === "warning") return <AlertTriangle size={18} />;
  return <Clock3 size={18} />;
};

export function AdminDashboard({ latestCase, cases }: Props) {
  return (
    <section className="admin-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Admin reasoning</p>
          <h2>{latestCase ? latestCase.case_id : "No case yet"}</h2>
        </div>
        <Activity size={22} />
      </div>

      {latestCase ? (
        <>
          <div className={`decision-banner ${latestCase.decision}`}>
            <strong>{latestCase.decision}</strong>
            <span>{Math.round(latestCase.confidence * 100)}% confidence</span>
          </div>
          <div className="citation-row">
            {latestCase.policy_citations.length > 0 ? latestCase.policy_citations.map((citation) => (
              <span key={citation}>{citation}</span>
            )) : <span>No policy citation</span>}
          </div>
          <div className="trace-list">
            {latestCase.tool_traces.map((trace) => (
              <article key={`${latestCase.case_id}-${trace.name}`} className={`trace ${trace.status}`}>
                <div className="trace-title">
                  {iconForTrace(trace)}
                  <strong>{trace.name.replaceAll("_", " ")}</strong>
                  <span>{trace.status}</span>
                </div>
                <pre>{JSON.stringify(trace.output, null, 2)}</pre>
              </article>
            ))}
          </div>
        </>
      ) : (
        <div className="empty-state">Send a refund request to see tool calls, failures, and policy validation here.</div>
      )}

      <div className="case-strip">
        <strong>Recent cases</strong>
        {cases.length === 0 && <span>No cases logged</span>}
        {cases.slice(0, 4).map((item) => (
          <div key={item.case_id} className="case-row">
            <span>{item.case_id}</span>
            <strong className={item.decision}>{item.decision}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
