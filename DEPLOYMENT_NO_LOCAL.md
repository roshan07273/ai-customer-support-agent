# Run And Test Without Local Setup

If you do not currently have Python, Node, or Docker installed locally, use one of these browser-based options.

## Best Option: Render

Render can deploy the backend and frontend directly from your GitHub repository.

### Steps

1. Create a public GitHub repository.
2. Upload this project to that repository.
3. Go to Render and choose **New +** then **Blueprint**.
4. Connect your GitHub repo.
5. Render will read `render.yaml` and create:
   - `ai-refund-agent-api`
   - `ai-refund-agent-web`
6. Deploy both services.
7. Open the frontend URL from Render and test the app.

### Important

The frontend environment variable in `render.yaml` is:

```text
VITE_API_BASE_URL=https://ai-refund-agent-api.onrender.com/api
```

If Render creates a different backend URL, update the frontend service environment variable to:

```text
https://YOUR-BACKEND-SERVICE.onrender.com/api
```

Then redeploy the frontend.

### OpenAI Key

The app works without an OpenAI key because refund decisions are deterministic.

If you want the LangChain response-polishing layer:

1. Open the `ai-refund-agent-api` service in Render.
2. Go to **Environment**.
3. Add:

```text
OPENAI_API_KEY=your_key_here
```

4. Redeploy the backend.

## Fastest Testing Option: GitHub Codespaces

Use this if you want to test and record the demo without installing anything locally.

1. Push the project to GitHub.
2. Open the repo on GitHub.
3. Click **Code** then **Codespaces** then **Create codespace**.
4. In the Codespaces terminal, run:

```bash
docker compose up --build
```

5. Codespaces will show forwarded ports.
6. Open port `5173` for the frontend.
7. Open port `8000` for backend docs.

## Railway Option

Railway also works well for this project.

Create two services from the same GitHub repo:

### Backend Service

- Root directory: `backend`
- Build: Dockerfile
- Port: `8000`
- Health path: `/api/health`
- Optional env var: `OPENAI_API_KEY`

### Frontend Service

- Root directory: `frontend`
- Build command:

```bash
npm install && npm run build
```

- Output directory:

```text
dist
```

- Environment variable:

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-URL/api
```

## What To Record In Loom

Once deployed, open the frontend URL and use these demo cases:

- Approval: `Aarav Mehta`
- Denial: `Sofia Rossi`
- Escalation: `Liam O'Connor`

The admin reasoning panel will show tool calls, policy citations, and decision traces.
