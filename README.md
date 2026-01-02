# Mental Health KG Chatbot

A calming, explainable conversational wellness assistant 


## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+

### Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/message` | Send a message and get bot response |
| GET | `/api/session/{id}` | Get session details |
| POST | `/api/reset` | Reset a session |

All endpoints return placeholder responses. The actual ontology/NLP logic will be implemented separately.

## Features

- 💬 Continuous chat interface
- 📊 Explanation panel with reasoning steps
- 🧘 Guided breathing exercises
- 📈 Dashboard with placeholder analytics
- ⚙️ Settings for theme and preferences
- 📱 Responsive design (mobile, tablet, desktop)


## Notes

- This is a UI/API skeleton with placeholder responses
- Ontology logic, NLP, and reasoning will be implemented separately
- No database or persistent storage is used
- All data is in-memory only
