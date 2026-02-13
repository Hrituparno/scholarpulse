# 🎓 ScholarPulse - AI Research Agent

An intelligent research assistant that searches academic papers, generates insights, and creates comprehensive research reports using multiple LLM providers.

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://scholarpulse.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-darkgreen)](https://www.djangoproject.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red)](https://streamlit.io/)

---

## 🌟 Live Demo

**Try it now:** [https://scholarpulse.streamlit.app](https://scholarpulse.streamlit.app)

---

## ✨ Features

- 🔍 **Smart Paper Search** - Searches arXiv for relevant research papers
- 🤖 **Multi-LLM System** - Uses Groq, Gemini, and Oxlo for different tasks
- 💡 **Idea Generation** - Generates novel research ideas from papers
- 📊 **Comprehensive Reports** - Creates detailed research reports
- 🎨 **Modern UI** - Glassmorphism design with smooth animations
- ⚡ **Fast & Reliable** - Optimized for speed and accuracy
- 🌍 **Production Ready** - Deployed on Render + Streamlit Cloud

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Streamlit     │────────▶│  Django REST API │
│   Frontend      │         │     Backend      │
└─────────────────┘         └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌─────────┐      ┌─────────┐    ┌─────────┐
              │  Groq   │      │ Gemini  │    │  Oxlo   │
              │   LLM   │      │   LLM   │    │   LLM   │
              └─────────┘      └─────────┘    └─────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     ▼
                              ┌─────────────┐
                              │ arXiv API   │
                              └─────────────┘
```

---

## 🚀 Quick Start

### Option 1: Use Live Demo (Easiest)

Visit: [https://scholarpulse.streamlit.app](https://scholarpulse.streamlit.app)

### Option 2: Run Locally

```bash
# Clone repository
git clone https://github.com/yourusername/scholarpulse.git
cd scholarpulse

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run backend
cd backend
python manage.py migrate
python manage.py runserver

# Run frontend (in another terminal)
cd frontend
streamlit run app.py
```

---

## 🔧 Configuration

### Required API Keys

Get your free API keys:
- **Groq:** https://console.groq.com
- **Google Gemini:** https://makersuite.google.com/app/apikey
- **Oxlo:** https://oxlo.ai (optional fallback)

Add to `.env`:
```env
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_gemini_key_here
OXLO_API_KEY=your_oxlo_key_here
```

---

## 📦 Tech Stack

### Backend
- **Framework:** Django 5.0 + Django REST Framework
- **Database:** SQLite (easily upgradable to PostgreSQL)
- **Server:** Gunicorn + Whitenoise
- **Deployment:** Render

### Frontend
- **Framework:** Streamlit 1.30
- **Styling:** Custom glassmorphism theme
- **Deployment:** Streamlit Cloud

### AI/ML
- **LLM Providers:** Groq, Google Gemini, Oxlo
- **Search:** arXiv API
- **Processing:** LangChain, FAISS

---

## 🎯 How It Works

1. **User Input** - Enter research query in Streamlit UI
2. **Paper Search** - Backend searches arXiv for relevant papers
3. **LLM Analysis** - Multi-LLM system analyzes papers:
   - Groq: Fast initial analysis
   - Gemini: Deep synthesis
   - Oxlo: Fallback if others fail
4. **Idea Generation** - Generates novel research ideas
5. **Report Creation** - Compiles comprehensive research report
6. **Results Display** - Shows papers, ideas, and report in UI

---

## 📁 Project Structure

```
scholarpulse/
├── agent/                  # AI research agents
│   ├── llm.py             # Multi-LLM client
│   ├── lit_review.py      # Paper search & analysis
│   ├── hypothesis.py      # Idea generation
│   └── experiment.py      # Experiment design
│
├── backend/               # Django REST API
│   ├── api/              # API endpoints
│   ├── research/         # Research models & services
│   └── scholarpulse/     # Django settings
│
├── frontend/              # Streamlit UI
│   ├── app.py            # Main application
│   ├── api_client.py     # Backend API client
│   ├── components/       # UI components
│   └── styles/           # Theme & styling
│
├── tools/                 # Utilities
│   ├── arxiv_loader.py   # arXiv integration
│   └── paper_parser.py   # Paper processing
│
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
└── DEPLOYMENT.md        # Deployment guide
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick Deploy:**
1. Push to GitHub
2. Connect to Render (backend)
3. Connect to Streamlit Cloud (frontend)
4. Add environment variables
5. Deploy!

---

## 🧪 Testing

```bash
# Test Groq API
python test_groq_api.py

# Test all LLM providers
python test_all_apis.py

# Test multi-LLM system
python test_multi_llm.py
```

---

## 📊 API Endpoints

### Health Check
```
GET /api/health/
```

### Submit Research
```
POST /api/research/submit/
{
  "query": "machine learning optimization",
  "mode": "Deep Research",
  "llm_provider": "groq"
}
```

### Get Status
```
GET /api/research/status/{task_id}/
```

### Get Results
```
GET /api/research/result/{task_id}/
```

---

## 🎨 Features Showcase

### Multi-LLM System
- **Groq:** Fast inference for initial analysis
- **Gemini:** Deep synthesis and complex reasoning
- **Oxlo:** Reliable fallback with retry logic

### Smart Error Handling
- Automatic retry on failures
- Graceful fallback between providers
- Detailed error logging

### Modern UI
- Glassmorphism design
- Smooth animations
- Responsive layout
- Real-time progress updates

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **arXiv** - For open access to research papers
- **Groq** - For fast LLM inference
- **Google** - For Gemini API
- **Oxlo** - For reliable fallback LLM
- **Render** - For backend hosting
- **Streamlit** - For frontend hosting

---

## 📞 Contact

For questions or feedback:
- Create an issue on GitHub
- Email: your.email@example.com

---

## 🌟 Star This Project

If you find ScholarPulse useful, please star this repository!

---

**Built with ❤️ for researchers, students, and AI enthusiasts**

