# 🌐 Website Chat Widget (branch: `website-widget`)

This branch adds the same AI agent as a chat bubble that can be embedded on the resort's own website. The Streamlit app on `main` stays as the demo.

```
Resort website ──► widget.js (chat bubble)
                       │  POST /api/chat
                       ▼
               FastAPI (web_api.py) on Render
                       │
                       ▼
          agent.py + tools ──► PostgreSQL, Gmail
```

## Files

| File               | Purpose                                                        |
| ------------------ | -------------------------------------------------------------- |
| `web_api.py`       | FastAPI server: `/api/chat`, `/health`, and serves the widget |
| `widget/widget.js` | Embeddable chat bubble with no dependencies                    |
| `widget/demo.html` | Sample "resort website" page for testing the widget           |
| `render.yaml`      | One-click Render deploy config                                 |

## How it works

- Each browser tab gets its own `session_id`, and the server keeps a separate agent for every session, so customers never see each other's booking details.
- Idle sessions are cleared after 1 hour, with at most 500 kept in memory.
- The widget renders inside a Shadow DOM, so the host website's CSS can't break it.
- Replies are inserted as plain text, never as HTML.
- `ALLOWED_ORIGINS` limits which websites can call the API.

## Run locally

```bash
git checkout website-widget
pip install -r requirements.txt
uvicorn web_api:app --reload
```

Open http://localhost:8000 and click the 🐾 button. It uses the same `.env` as the Streamlit app.

## Deploy on Render

1. Push this branch to GitHub.
2. On Render, choose **New → Blueprint**, then pick this repo and the `website-widget` branch.
3. Fill in the secrets it asks for (`GROQ_API_KEY`, `DATABASE_URL`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `ADMIN_EMAIL`). For `ALLOWED_ORIGINS`, start with `*` for testing.
4. Open `https://<your-service>.onrender.com` to see the demo page.

## Add to the resort's website

Paste one line before `</body>`:

```html
<script src="https://<your-service>.onrender.com/widget/widget.js" defer></script>
```

Then set `ALLOWED_ORIGINS` to the website's address, for example `https://playstaytionpetresort.com,https://www.playstaytionpetresort.com`.

## Known limits

- Sessions live in server memory, so they're lost on restart. Redis would fix this if you ever run more than one server.
- Render's free plan may put the service to sleep when idle, which makes the first message slow.
- There's no rate limiting yet. Add it before any heavy public use.
