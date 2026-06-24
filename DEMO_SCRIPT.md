# 7-10 Minute Demo Script

## 1. Product overview

"This is an AI refund support agent for an e-commerce team. The agent can approve, deny, or escalate refund requests. The important part is that the LLM does not get to invent policy decisions. It has to call tools, and the deterministic policy validator makes the final call."

## 2. Standard refund

Select `Aarav Mehta`.

Send:

```text
The headphones arrived, but the right ear cup is defective. I would like a refund please.
```

Point out:

- CRM lookup succeeds.
- Order lookup succeeds.
- Policy is retrieved.
- Policy validation approves the request.

## 3. Policy violation

Select `Sofia Rossi`.

Send:

```text
I used the digital meal plan already, but I changed my mind and want my money back.
```

Point out:

- The agent denies the refund.
- The admin trace cites `Non-Refundable Rules #3`.
- The customer-facing answer stays firm but still helpful.

## 4. Escalation

Select `Liam O'Connor`.

Send:

```text
The espresso machine is defective and I want to return it for a refund.
```

Point out:

- The amount is over $300.
- The agent escalates instead of approving.
- This is the kind of threshold a real support team would want to keep deterministic.

## 5. Code tour

Open:

- `backend/app/agent/refund_agent.py`
- `backend/app/agent/tools.py`
- `backend/app/data/refund_policy.md`
- `backend/app/data/crm_profiles.json`
- `frontend/src/components/AdminDashboard.tsx`

## 6. Voice note

"I added a voice-channel entry point in the UI and API payload. For the slice, it goes through the same backend path so the policy behavior is identical. The next production step would be wiring that button to OpenAI Realtime, ElevenLabs, or LiveKit for streaming audio."

## 7. Close

"The app can run through Docker Compose or through separate Python and React commands. The README includes setup, architecture, demo cases, and the submission notes."
