# AI Customer Support Refund Agent

This is my product vertical slice for an AI customer support agent that processes, denies, or escalates e-commerce refund requests against a strict refund policy.

The goal was to build a realistic slice rather than a static demo: the backend loads CRM data, retrieves policy context, runs tool-based validation, and returns both the customer-facing answer and the internal reasoning trace. The frontend shows the customer chat next to an admin dashboard so the reviewer can see the agent "holding the line" on policy violations.

## What Is Included

- 15 mocked CRM customer profiles with orders, refund history, risk scores, payment states, and edge-case flags.
- A strict refund policy document at `backend/app/data/refund_policy.md`.
- Python FastAPI backend with LangChain-compatible tool functions.
- Deterministic policy validation so the app still works without an OpenAI key.
- Optional OpenAI wording layer through `langchain-openai` when `OPENAI_API_KEY` is present.
- React frontend with customer chat, demo prompt buttons, voice-channel button, and admin reasoning logs.
- Docker Compose setup for reviewers who do not want to configure local Python and Node manually.

## Tech Stack

- Backend: Python, FastAPI, Pydantic, LangChain, LangChain OpenAI
- Frontend: React, TypeScript, Vite, Lucide icons
- Runtime: Docker Compose or local Python/Node

## Architecture

```text
backend/
  app/
    agent/
      refund_agent.py      # Agent orchestration and final response composition
      tools.py             # CRM lookup, order lookup, policy retrieval, policy validation
    api/
      routes.py            # FastAPI endpoints
    data/
      crm_profiles.json    # 15 mocked CRM profiles
      refund_policy.md     # Strict refund policy
    models/
      schemas.py           # Pydantic API and domain models
    data_store.py          # Data loading helpers
    main.py                # FastAPI app

frontend/
  src/
    components/            # Chat, CRM side panel, admin dashboard
    lib/api.ts             # API client
    types/                 # Shared frontend types
```

## How The Agent Works

The backend follows a small tool-orchestration loop:

1. `crm_lookup` loads the customer profile.
2. `order_lookup` validates that the order belongs to that customer.
3. `policy_retrieval` loads the refund policy document.
4. `policy_validation` checks the request against each rule and returns a decision.
5. The response composer writes the final customer-facing answer.

Each tool call is captured as a trace with input, output, status, and timestamps. The React admin panel renders those traces so failures, denials, and escalations are visible during the demo.

The policy decision is deterministic and not left to the LLM. If `OPENAI_API_KEY` is configured, LangChain uses the model only to make the final response sound more natural while preserving the approved, denied, or escalated decision.

## Run With Docker

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health


The app works without this key because the policy engine has a deterministic fallback response.

## No Local Setup

If you do not have Python, Node, or Docker installed locally, deploy it from GitHub using Render, Railway, or GitHub Codespaces. I included a Render blueprint in `render.yaml` and a full no-local guide in `DEPLOYMENT_NO_LOCAL.md`.

## Run Locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Demo Cases

Use these from the UI customer selector:

- Standard approval: `Aarav Mehta / ORD-9001`
  - Message: "The headphones arrived, but the right ear cup is defective. I would like a refund please."
  - Expected: approved.

- Policy violation: `Sofia Rossi / ORD-9006`
  - Message: "I used the digital meal plan already, but I changed my mind and want my money back."
  - Expected: denied because digital access has been used.

- Human review: `Liam O'Connor / ORD-9007`
  - Message: "The espresso machine is defective and I want to return it for a refund."
  - Expected: escalated because the refund is above $300.

- Failure trace: select any customer and change the request in the browser devtools or API docs to an invalid order id.
  - Expected: the admin panel shows the failed tool call.

## Loom Walkthrough Plan

1. Start with the product screen and explain the goal: refund support agent with policy enforcement.
2. Show the standard approval case and point out the admin traces.
3. Show the policy violation case and explain how the agent holds the line.
4. Show the escalation case for an amount above the auto-approval threshold.
5. Open the code and walk through `refund_agent.py`, `tools.py`, `crm_profiles.json`, and `refund_policy.md`.
6. Mention that the voice button currently routes the request through a `voice` channel flag and can be extended to OpenAI Realtime, ElevenLabs, or LiveKit.
7. Close with how to run the project and where the GitHub link is in the submission.

## API Endpoints

- `GET /api/health`
- `GET /api/customers`
- `POST /api/chat`
- `GET /api/cases`

Example request:

```json
{
  "customer_id": "CUST-1001",
  "order_id": "ORD-9001",
  "message": "The headphones are defective and I want a refund.",
  "channel": "chat"
}
```

## Notes

I intentionally made policy validation deterministic instead of relying on the model to decide eligibility. In a real production system, I would keep this split: tools and policy code decide, while the LLM handles summarization, tone, and recovery from ambiguous customer messages.
