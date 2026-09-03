# 📚 AI Research Assistant

> Discover, analyze, and chat with academic papers using AI-powered insights and real-time conversations.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.3.2-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🔍 **Paper Search** - Search academic papers from OpenAlex API with 200M+ papers
- 🤖 **AI Summaries** - Get instant AI-powered summaries of paper abstracts powered by Groq
- 💬 **Chat with Papers** - Upload and chat with PDFs using RAG (Retrieval-Augmented Generation)
- 🎯 **Topic Extraction** - Automatically extract research topics and metadata
- 📊 **Citation Tracking** - View citation counts and publication metrics
- 🌐 **Open Access Detection** - Identify and filter open-access papers
- ⚡ **Real-time Processing** - Instant responses with streaming capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│         React + TypeScript + Tailwind CSS                   │
│        Framer Motion for smooth animations                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes                                          │  │
│  │  • /papers - Search & summarization                  │  │
│  │  • /process_pdf - PDF ingestion                      │  │
│  │  • /chat - RAG-based Q&A                             │  │
│  │  • /research - Paper comparison & analysis           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                            │  │
│  │  • Paper Search (OpenAlex)                           │  │
│  │  • LLM (Groq API)                                    │  │
│  │  • PDF Processing (PyMuPDF)                          │  │
│  │  • Embeddings (HuggingFace)                          │  │
│  │  • RAG Engine (LangChain)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌─────────▼──────────┐
│  PostgreSQL      │    │  OpenAlex API     │
│  + pgvector      │    │  + Groq API       │
│  (Vector DB)     │    │                   │
└──────────────────┘    └───────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL with pgvector extension
- Groq API Key

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/ai-research-assistant.git
cd ai-research-assistant
```

### 2. Environment Variables

Create `.env` files:

**Backend** (`backend/.env`):
```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/research_db
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_API_URL=http://127.0.0.1:8000
```

### 3. Start Database

```bash
docker-compose up -d
```

Verify the database is running:
```bash
docker ps
```

### 4. Install & Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on: `http://127.0.0.1:8000`

### 5. Install & Run Frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://127.0.0.1:3000`

## 📖 Usage

### Search for Papers

1. Open `http://127.0.0.1:3000`
2. Enter a search query (e.g., "microplastic detection", "quantum computing")
3. Click **Search** to find papers

### Get AI Summary

1. Click **AI Summary** on any paper
2. The Groq AI will generate a plain-language summary in seconds

### Chat with a Paper

1. Click **Chat w/ Paper** on a paper with open-access PDF
2. Wait for PDF processing to complete
3. Ask questions about the paper in natural language
4. Get instant answers from the AI Research Assistant

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.104.1 - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database
- **LangChain** - RAG and LLM orchestration
- **Groq API** - Fast LLM inference
- **HuggingFace** - Embeddings (all-MiniLM-L6-v2)
- **PyMuPDF** - PDF extraction
- **psycopg2** - PostgreSQL driver

### Frontend
- **Next.js** 16.3.2 - React framework
- **React** 19.2.8 - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** 4 - Styling
- **Framer Motion** - Animations
- **Lucide React** - Icons

### Infrastructure
- **PostgreSQL** 15 + pgvector - Vector database
- **Docker** - Containerization
- **OpenAlex API** - Paper metadata & search

## 📁 Project Structure

```
ai-research-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py          # PDF chat endpoint
│   │   │   ├── papers.py        # Paper search & summarization
│   │   │   └── research.py      # Research agent
│   │   ├── database/
│   │   │   ├── connection.py    # DB setup
│   │   │   └── models.py        # SQLAlchemy models
│   │   ├── models/              # Pydantic schemas
│   │   ├── rag/                 # RAG pipeline
│   │   │   ├── ingestion.py     # Document chunking
│   │   │   ├── retrieval.py     # Vector search
│   │   │   └── generation.py    # Answer generation
│   │   ├── services/            # Business logic
│   │   │   ├── llm_service.py   # Groq integration
│   │   │   ├── embeddings.py    # HuggingFace embeddings
│   │   │   ├── pdf_processor.py # PDF extraction
│   │   │   └── paper_search.py  # OpenAlex search
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx         # Main interface
│   │       ├── layout.tsx       # Layout wrapper
│   │       └── globals.css      # Tailwind styles
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── .env.local
├── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### Papers
- `GET /papers/` - Search papers
- `POST /papers/summarize` - Generate AI summary

### Chat
- `POST /process_pdf` - Ingest PDF to vector store
- `POST /chat` - Chat with processed paper

### Research
- `POST /research/compare` - Compare multiple papers
- `POST /research/report` - Generate literature review

## 🎨 UI Features

- **Dark Mode** - Eye-friendly interface with gradient effects
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Framer Motion for polished UX
- **Real-time Feedback** - Loading states and error handling
- **Accessibility** - Semantic HTML and ARIA labels

## 🔑 API Keys Required

1. **Groq API Key** - Get from [https://console.groq.com](https://console.groq.com)
   - Free tier includes generous API limits
   - Used for instant summarization

## 📊 Performance

- Search: < 1 second
- PDF Processing: 5-30 seconds (depending on size)
- AI Summary: 2-5 seconds
- Chat Response: 3-10 seconds

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml or environment
lsof -i :5432  # Check PostgreSQL
lsof -i :8000  # Check FastAPI
lsof -i :3000  # Check Next.js
```

### PDF Access Denied (403)
- Some papers may require institutional access
- Search for papers marked as "open access"
- Try arXiv, PubMed Central, or SSRN papers

### Database Connection Failed
```bash
# Ensure Docker containers are running
docker-compose up -d
docker-compose ps
```

### Dependencies Issues
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAlex](https://openalex.org) - Academic paper database
- [Groq](https://groq.com) - Fast LLM inference
- [LangChain](https://langchain.com) - RAG framework
- [HuggingFace](https://huggingface.co) - Embeddings
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework
- [Next.js](https://nextjs.org) - Frontend framework

## 📧 Contact

For questions or feedback, please open an issue or reach out via GitHub.

---

**Star ⭐ this repo if you find it useful!**
