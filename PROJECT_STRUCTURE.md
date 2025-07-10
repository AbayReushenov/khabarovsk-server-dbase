# 🏔️ Khabarovsk Forecast Buddy - Project Structure

## 🤝 Joint Project Overview

This is a **collaborative full-stack project** for AI-powered sales forecasting of down jackets in Khabarovsk. The project is split across two GitHub repositories for optimal development workflow and deployment.

## 📁 Repository Structure

### Frontend Repository
- **Repository**: [habarovsk-forecast-buddy](https://github.com/AbayReushenov/habarovsk-forecast-buddy)
- **Technology**: React 18 + TypeScript + Vite
- **Live Demo**: [habarovsk-forecast-buddy.lovable.app](https://habarovsk-forecast-buddy.lovable.app/)
- **Purpose**: User interface, data visualization, file upload

### Backend Repository
- **Repository**: [khabarovsk-server-dbase](https://github.com/AbayReushenov/khabarovsk-server-dbase)
- **Technology**: FastAPI + Python 3.11
- **Purpose**: API server, AI integration, database management

## 🔗 Integration Points

```
┌─────────────────────────────┐
│     Frontend Repository     │
│   habarovsk-forecast-buddy  │
│                             │
│  ┌─────────────────────────┐│
│  │   React Application    ││
│  │   - UI Components      ││
│  │   - API Client         ││
│  │   - State Management   ││
│  └─────────────────────────┘│
└─────────────┬───────────────┘
              │ HTTP/REST API
              ▼
┌─────────────────────────────┐
│     Backend Repository      │
│   khabarovsk-server-dbase   │
│                             │
│  ┌─────────────────────────┐│
│  │   FastAPI Server       ││
│  │   - REST Endpoints     ││
│  │   - GigaChat AI        ││
│  │   - Supabase DB        ││
│  └─────────────────────────┘│
└─────────────────────────────┘
```

## 🚀 Development Workflow

### 1. Clone Both Repositories

```bash
# Create project directory
mkdir khabarovsk-forecast-project
cd khabarovsk-forecast-project

# Clone backend
git clone https://github.com/AbayReushenov/khabarovsk-server-dbase.git
cd khabarovsk-server-dbase
pip install -r requirements.txt
# Setup .env file and run: uvicorn app.main:app --reload

# Clone frontend (in separate terminal)
cd ../
git clone https://github.com/AbayReushenov/habarovsk-forecast-buddy.git
cd habarovsk-forecast-buddy
npm install
# Run: npm run dev
```

### 2. Development Order

1. **Backend First**: Start the FastAPI server (port 8000)
2. **Frontend Second**: Start the React dev server (port 8080)
3. **Integration**: Frontend automatically connects to backend API

### 3. API Integration

The frontend includes built-in API client with:
- Health monitoring (`/api/v1/health`)
- Automatic fallback to mock data
- Error handling and user feedback
- File upload validation

## 📋 Why Separate Repositories?

### ✅ Advantages

1. **Independent Development**
   - Different technology stacks (Python vs TypeScript)
   - Separate CI/CD pipelines
   - Independent versioning

2. **Deployment Flexibility**
   - Frontend: Deployed on lovable.app
   - Backend: Can be deployed on Render, Railway, etc.
   - Scalable architecture

3. **Team Collaboration**
   - Clear separation of responsibilities
   - Frontend and backend developers can work independently
   - Easier code reviews and maintenance

4. **Technology-Specific Tooling**
   - Python-specific tools for backend (pytest, black, mypy)
   - Node.js tools for frontend (Vite, ESLint, Prettier)

### 🔄 Coordination

- **API Contract**: Defined in backend OpenAPI docs
- **Cross-references**: READMEs link to each other
- **Shared Documentation**: Integration guides and API specs
- **Version Compatibility**: Tags and releases coordinated

## 🛠️ Maintenance

### Updating Both Projects

```bash
# Backend updates
cd khabarovsk-server-dbase
git pull origin main
pip install -r requirements.txt

# Frontend updates
cd ../habarovsk-forecast-buddy
git pull origin main
npm install
```

### API Changes

When making API changes:
1. Update backend first
2. Test with backend docs at `/docs`
3. Update frontend API client if needed
4. Test integration end-to-end

## 📄 License

Both repositories are licensed under **MIT License**, allowing:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

## 🙏 Contributing

Contributions welcome to both repositories:
- **Backend Issues**: [khabarovsk-server-dbase/issues](https://github.com/AbayReushenov/khabarovsk-server-dbase/issues)
- **Frontend Issues**: [habarovsk-forecast-buddy/issues](https://github.com/AbayReushenov/habarovsk-forecast-buddy/issues)

---

**Made with ❤️ for Khabarovsk retailers**
