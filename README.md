# Mental Health KG Chatbot

A calming, explainable conversational wellness assistant built with React, TypeScript, TailwindCSS, and FastAPI.

## Project Structure

```
Mental Health KRR/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   │   ├── chat/         # Chat components
│   │   │   ├── explanation/  # Explanation panel
│   │   │   ├── intervention/ # Intervention cards
│   │   │   └── layout/       # Layout components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   ├── styles/           # CSS styles
│   │   └── types/            # TypeScript types
│   ├── public/               # Static assets
│   ├── package.json
│   └── tailwind.config.js
├── backend/                  # FastAPI backend
│   ├── main.py               # API endpoints
│   └── requirements.txt
├── context.md                # Project context
├── frontend.md               # Frontend specifications
└── rules.md                  # Implementation rules
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+

### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
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

## Tech Stack

**Frontend:**
- React 18 + TypeScript
- TailwindCSS
- Framer Motion
- React Router
- Lucide Icons

**Backend:**
- FastAPI
- Pydantic
- Uvicorn

## Notes

- This is a UI/API skeleton with placeholder responses
- Ontology logic, NLP, and reasoning will be implemented separately
- No database or persistent storage is used
- All data is in-memory only
