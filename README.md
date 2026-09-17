# Hotel AI Guest Assistant — Gemini Starter

A full-stack starter for the Hotel Guest Assistant assignment.

## Included
- FastAPI backend
- Gemini integration using Google's `google-genai` Python SDK
- Hotel knowledge base in JSON
- Grounded AI responses
- Deterministic availability tool
- Date and guest validation
- Basic automated tests
- Environment-variable API-key configuration

## 1. Setup

Open the project in VS Code.

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `backend/.env` and add your Gemini key:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Do not commit `.env` to GitHub.

## 2. Run

```powershell
uvicorn main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## 3. Try the chat API

POST `/chat`

```json
{
  "message": "What time is check-in?",
  "conversation": []
}
```

## 4. Try availability

POST `/availability`

```json
{
  "check_in": "2026-09-20",
  "check_out": "2026-09-22",
  "adults": 3
}
```

Availability and calculations are handled by deterministic backend code. Gemini is used for natural-language responses and is grounded on `data/hotel.json`.

## 5. Tests

From the `backend` directory:

```powershell
pytest
```

## Current scope

This is the backend foundation. The next development stage is the React/Next.js guest-facing UI, followed by stronger conversation context, availability intent extraction/tool calling, error handling, and the complete 8–10 scenario evaluation required by the assignment.
