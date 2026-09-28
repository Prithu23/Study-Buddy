# StudyBuddy

**Live demo:** https://study-buddy-eta-virid.vercel.app/

A study assistant chatbot that shows how **prompt engineering** changes an AI's answers. Ask one question and compare the reply across four prompting styles: zero-shot, few-shot, role prompting, and a retrieval-based FAQ assistant.

Built with a Flask backend, the Groq API, and a plain HTML/CSS/JS frontend.

## Features

- **Four prompting modes** you can switch between in the UI
- **"Show prompt" toggle** on every answer, so you can see the exact prompt sent to the model
- **FAQ assistant** that answers only from your own `faq.json` and says so when it doesn't know
- **Markdown rendering** for headings, lists, tables and code in answers
- **Clickable sticker prompts** for quick testing
- Deployable to Vercel with no extra configuration

## The four modes

| Mode | What it sends to the model | What to expect |
|------|----------------------------|----------------|
| Zero-shot | Only your question | A generic baseline answer, often long |
| Few-shot | Two example Q&A pairs, then your question | Answers that copy the Definition / Example / Key point format |
| Role | A system prompt: "You are StudyBuddy, a patient study tutor..." | Short, tutor-style answers with an example |
| FAQ | Role prompt plus the best-matching FAQ entries | Answers grounded in your data, or "I couldn't find that in the FAQ" |

## Tech stack

- **Backend:** Python, Flask, flask-cors
- **LLM:** Groq API (`openai/gpt-oss-20b` by default)
- **Frontend:** HTML, CSS, JavaScript (marked + DOMPurify for safe markdown)
- **Hosting:** Vercel

## Project structure

```
study-assistant/
├── app.py              # Flask API and prompt builders
├── faq.json            # Knowledge base for FAQ mode
├── requirements.txt    # Python dependencies
├── .env                # Your API key (never commit this)
├── .gitignore
└── public/
    └── index.html      # The frontend
```

## Run it locally

**1. Create and activate a virtual environment**

```bash
python -m venv venv
```

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (CMD): `venv\Scripts\activate.bat`
- Mac/Linux: `source venv/bin/activate`

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your Groq API key**

Get a key at [console.groq.com](https://console.groq.com) under API Keys, then create a `.env` file:

```
GROQ_API_KEY=your_key_here
```

**4. Start the server**

```bash
python app.py
```

**5. Open the frontend**

Open `public/index.html` in your browser. When opened as a file, it talks to `http://localhost:5000`.

## Deploy to Vercel

1. Push the project to GitHub (make sure `.env` is in `.gitignore`).
2. On [vercel.com](https://vercel.com), choose Add New, then Project, and import the repo.
3. Under Environment Variables, add `GROQ_API_KEY` as the **Name** and your key as the **Value**.
4. Click Deploy.

Vercel detects Flask automatically and serves everything in `public/` as static files. If you add the environment variable after deploying, redeploy so it takes effect.

## API

### `POST /api/chat`

Request:

```json
{ "message": "What is overfitting?", "mode": "role" }
```

`mode` is one of `zero_shot`, `few_shot`, `role`, `faq`.

Response:

```json
{
  "reply": "The model's answer...",
  "mode": "role",
  "prompt_used": [ { "role": "system", "content": "..." }, { "role": "user", "content": "..." } ]
}
```

On failure the response is `{ "error": "..." }` with status 400 or 500.

Quick test:

```bash
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"What is a stack?\", \"mode\": \"few_shot\"}"
```

## Customize it

- **FAQ data:** edit `faq.json`. Each entry is `{"question": "...", "answer": "..."}`.
- **Persona:** edit `ROLE_PROMPT` in `app.py`.
- **Answer format:** edit `FEW_SHOT_EXAMPLES` in `app.py`. The model imitates whatever format your examples use.
- **Model:** change `MODEL` in `app.py`. Groq's model list changes often, so run a quick script with `client.models.list()` to see the IDs your key can use.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `model_not_found` error | The model isn't available to your key. List available models and update `MODEL`. |
| `KeyError: 'GROQ_API_KEY'` | The `.env` file is missing or misnamed, or the Vercel variable isn't set. |
| "Can't reach the server" in the chat | The backend isn't running locally, or `API` in `index.html` still points to `localhost` on the deployed site. |
| Vercel says the variable name is invalid | The **Name** box must contain only `GROQ_API_KEY`. The key itself goes in **Value**. |
| Empty or cut-off replies | Increase `max_tokens` in `app.py`. Reasoning models use some of it for thinking. |

## Ideas for next steps

- Streaming responses so answers appear word by word
- Better FAQ retrieval with embeddings instead of keyword overlap
- Conversation memory so follow-up questions work
- A side-by-side view that runs all four modes on one question

## License

Add your preferred license here (MIT is a common choice for student projects).