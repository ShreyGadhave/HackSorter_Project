# 🎯 HackSorter - Multi-Agent AI Hiring System

> **Real-time AI-powered candidate evaluation with 7 specialized agents**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the System](#running-the-system)
- [API Documentation](#api-documentation)
- [Dashboard Guide](#dashboard-guide)
- [Bulk Submission Guide](#bulk-submission-guide)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Overview

HackSorter is an intelligent hiring system that uses multiple specialized AI agents to evaluate job candidates in real-time. The system analyzes resumes, cover letters, GitHub profiles, and job descriptions using 7 different agents, each with expertise in different evaluation criteria.

### Key Highlights

- ✅ **Real-time Analysis**: Stream candidate evaluation as it happens
- ✅ **7 Specialized AI Agents**: Resume, Cover Letter, JD Match, GitHub, Location, Fairness, Referee
- ✅ **Interactive Dashboard**: Beautiful React dashboard with 4 analytical tabs
- ✅ **Production Ready**: Fully tested and optimized
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile
- ✅ **Data Persistence**: localStorage integration with auto-sync
- ✅ **Error Handling**: Comprehensive error management and recovery

---

## ✨ Features

### Frontend Dashboard

1. **Live Activity Feed** 📡

   - Real-time event streaming
   - Color-coded log entries (info, success, error, warning)
   - Currently analyzing indicator
   - Export to CSV
   - Clear data option

2. **Statistics Dashboard** 📊

   - Total candidates analyzed
   - Average candidate score (0-100)
   - Shortlist rate percentage
   - Average analysis time in seconds

3. **Recent Candidates Table** 👥

   - Candidate profiles with scores
   - Verdict status (Shortlisted/Rejected/Pending)
   - Analysis duration
   - Completion timestamps

4. **Agent Performance Metrics** 🤖
   - Per-agent performance tracking
   - Completion counts
   - Average scores
   - Last scores and update times

### Backend Features

- 7 AI agents with specialized evaluation criteria
- LangGraph orchestration for agent coordination
- Groq API integration for LLM inference
- Server Sent Events (SSE) for real-time streaming
- Health check endpoint
- Comprehensive API documentation

### Data Management

- localStorage integration for client-side persistence
- 1000-entry activity limit (auto-cleanup)
- Structured data logging
- Metrics tracking per agent

---

## 🛠️ Tech Stack

### Frontend

- **React 18** - Modern UI framework with hooks
- **Vite 5** - Lightning-fast build tool
- **CSS3** - Advanced styling with Grid, Flexbox, animations
- **localStorage API** - Client-side data persistence
- **Server Sent Events** - Real-time data streaming

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Python 3.13** - Latest Python runtime
- **LangGraph** - Multi-agent orchestration
- **Groq API** - Fast LLM inference
- **Pydantic** - Data validation

### Database & Storage

- **localStorage** - Client-side persistence (browser)
- **In-memory** - Backend request processing

### DevOps & Tools

- **npm** - Package management
- **git** - Version control
- **python-dotenv** - Environment configuration

---

## 📁 Project Structure

```
HackSorter_Project/
├── 📁 frontend/                    # React application
│   ├── 📁 components/
│   │   ├── ActivityDashboard.jsx   # Main dashboard (4 tabs)
│   │   ├── ActivityDashboard.css   # Dashboard styling
│   │   ├── AgentTerminal.jsx       # Real-time analysis display
│   │   └── AgentTerminal.css       # Terminal styling
│   ├── App.jsx                     # Main app component
│   ├── App.css                     # Application styling
│   ├── main.jsx                    # React entry point
│   ├── index.html                  # HTML template
│   ├── package.json                # Dependencies
│   ├── vite.config.js              # Build configuration
│   ├── uploadHandler.js            # API utilities
│   ├── ExampleUsage.jsx            # Component examples
│   └── 📁 node_modules/            # Installed packages
│
├── 📁 backend/                     # FastAPI application
│   ├── main.py                     # API entry point
│   ├── graph.py                    # LangGraph orchestration
│   ├── state.py                    # State management
│   ├── 📁 agents/                  # AI agent implementations
│   │   ├── resume_analyst.py
│   │   ├── cover_letter.py
│   │   ├── jd_matcher.py
│   │   ├── github_analyst.py
│   │   ├── location_coordinator.py
│   │   ├── fairness_auditor.py
│   │   └── referee.py
│   └── 📁 utils/                   # Utilities
│       ├── preprocessor.py
│       └── formatters.py
│
├── 📁 scripts/                     # Utility scripts
│
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── package-lock.json               # npm lock file
└── README.md                       # This file

```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.13+
- Node.js 22+
- npm 10+
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/ShreyGadhave/HackSorter_Project.git
cd HackSorter_Project
```

### Step 2: Setup Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file with API keys
cp .env.example .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_key_here
```

### Step 3: Setup Frontend

```bash
cd frontend

# Install npm dependencies
npm install

# The Vite dev server will be configured
# to proxy API requests to localhost:8000
```

### Step 4: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check Node version
node --version   # Should be 22+

# Check npm version
npm --version    # Should be 10+
```

---

## 🚀 Running the System

### Terminal 1: Start Backend

```bash
cd HackSorter_Project
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2: Start Frontend

```bash
cd HackSorter_Project/frontend
npm run dev
```

Expected output:

```
VITE v5.x.x ready in xxx ms
➜  Local:   http://localhost:3000/
```

### Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

---

## 📡 API Documentation

### Health Check

```http
GET /health
```

Returns: `200 OK`

### Analyze Candidate (JSON)

```http
POST /analyze-json
Content-Type: application/json

{
  "job_application": {
    "resume": "string (candidate resume text)",
    "github_url": "string (GitHub profile URL)",
    "cover_letter": "string (cover letter text)",
    "job_description": "string (job description text)"
  }
}
```

**Response**: Server Sent Events (SSE) stream

```
data: {"agent": "Resume Analyst", "message": "...", "status": "done"}
data: {"agent": "Cover Letter Analyst", "message": "...", "status": "done"}
...
data: {"agent": "Referee Agent", "full_verdict": {...}, "status": "complete"}
```

### Analyze Candidate (File Upload)

```http
POST /analyze
Content-Type: multipart/form-data

resume_file: (PDF file)
github_url: string
cover_letter: string
jd_text: string
```

**Response**: Server Sent Events (SSE) stream

### Response Format

Each event is JSON:

```javascript
{
  "agent": "Agent Name",
  "message": "Agent's analysis",
  "status": "done|complete|error",
  "type": "analysis|verdict|system",
  "score": 85.5,  // For scoring agents
  "thought_process": "...",  // Agent's reasoning
  "full_verdict": {  // Final verdict from Referee
    "verdict": "SHORTLISTED|REJECTED",
    "final_score": 85.5,
    "reason": "Explanation"
  }
}
```

---

## 📊 Dashboard Guide

### Accessing the Dashboard

1. Open http://localhost:3000 in your browser
2. You'll see the Activity Dashboard

### Submitting Candidates

**Single Candidate Mode**: Click the ➕ button (blue FAB)

- Upload resume (PDF)
- Enter GitHub URL
- Write cover letter
- Provide job description
- Click "Analyze Candidate"

**Bulk Submission Mode**: Click the 📊 button (orange FAB)

- Load dataset JSON file (contains multiple candidates)
- Enter job description (same for all candidates)
- Select how many candidates to submit (1-1000)
- Click "Submit X Candidates"
- Monitor real-time progress
- Export results as JSON

### Tab 1: Live Activity

- Shows all events in real-time
- Color-coded by severity:
  - 🟢 Green: Success
  - 🔵 Blue: Info
  - 🟡 Yellow: Warning
  - 🔴 Red: Error
- **Export**: Download activity log as CSV
- **Clear**: Reset all activity data

### Tab 2: Statistics

Shows four key metrics:

- **Total Candidates**: Count of analyzed profiles
- **Avg Score**: Mean score across all candidates (0-100)
- **Shortlist Rate**: Percentage of shortlisted candidates
- **Avg Analysis Time**: Mean time per analysis in seconds

### Tab 3: Recent Candidates

Table showing:

- **Name**: Candidate's name
- **Score**: Final score (0-100), color-coded
- **Verdict**: SHORTLISTED (green), REJECTED (red), PENDING (gray)
- **Time**: Analysis duration in seconds
- **Completed**: Timestamp of completion

### Tab 4: Agent Metrics

Performance cards for each agent:

- **Resume Analyst**
- **Cover Letter Analyst**
- **JD Match Analyst**
- **GitHub Analyst**
- **Location Coordinator**
- **Fairness Auditor**
- **Referee Agent**

### Bulk Submission Panel

#### Load Dataset

- Click "📁 Load Dataset (JSON)"
- Select your candidate dataset file
- System validates and shows candidate count

#### Select Candidates

- Use slider to choose how many candidates to submit
- Range: 1 to total candidates in dataset
- Default: 10 candidates

#### Job Description

- Enter the job description (applies to all candidates)
- This will be used for all candidates' JD Match analysis

#### Submit

- Click "Submit X Candidates" button
- System submits all candidates simultaneously
- Each candidate gets independent analysis pipeline

#### Monitor Progress

- Real-time stats showing:
  - Submitted: Candidates sent to backend
  - Completed: Analyses finished successfully
  - Failed: Candidates that errored
  - Pending: Still being analyzed
- Progress bar fills as submissions complete

#### View Results

- Completed candidates list with verdicts
- Failed candidates list with error messages
- Duration of entire bulk submission
- Export results as JSON for further analysis
- **Referee Agent**

Each card shows:

- Completion count
- Average score
- Last score
- Last update time

---

## 📦 Bulk Submission Guide

### What is Bulk Submission?

Bulk submission allows you to submit multiple candidates simultaneously from a dataset JSON file. Each candidate analysis runs independently in parallel, allowing you to evaluate 100+ candidates in one operation.

### Dataset Format

Your JSON file should contain an array of candidate objects:

```json
[
  {
    "applicant_id": "cand_0001",
    "personal_info": {
      "full_name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "555-1234",
      "location": "San Francisco",
      "willing_to_relocate": true
    },
    "resume": {
      "text": "Senior Software Engineer with 5 years experience..."
    },
    "cover_letter": {
      "text": "Dear Hiring Manager, I am excited to apply..."
    },
    "github": {
      "url": "https://github.com/janedoe",
      "repo_list": [...]
    }
  },
  ...
]
```

### How to Use Bulk Submission

1. **Go to Dashboard** → Click 📊 button (bottom-right)
2. **Load Dataset** → Click file selector → Choose your JSON
3. **Enter Job Description** → Paste position requirements
4. **Select Candidates** → Use slider (1-1000 candidates)
5. **Submit** → Click "Submit X Candidates"
6. **Monitor** → Watch real-time progress
7. **Export Results** → Download verdicts as JSON

### Performance Notes

- **Parallel Processing**: All candidates run simultaneously
- **Backend Scaling**: Bottleneck is typically Groq API rate limits
- **Typical Speed**: 100 candidates → ~15-30 seconds (depending on API)
- **Large Batches**: Test with 10-50 before running 1000+

### Example Dataset Structure

We've included `large_dataset_1000.json` with 1000 sample candidates. To test:

1. Click 📊 button
2. Select `large_dataset_1000.json`
3. Enter job description
4. Start with 10 candidates (use slider)
5. Click submit and watch progress

### Common Use Cases

- **Recruitment Drive**: Screen 500+ applications overnight
- **Campus Hiring**: Evaluate all 300 student applications
- **Contractor Screening**: Batch process 50+ freelance profiles
- **Pipeline Management**: Bulk re-evaluate candidates against new JD

---

### How to Submit a Candidate

1. Click the **[+]** floating action button (bottom-right)
2. Fill in the form:
   - **Resume**: Paste resume text
   - **GitHub URL**: e.g., `https://github.com/username`
   - **Cover Letter**: Paste cover letter text
   - **Job Description**: Paste job description
3. Click **Analyze**
4. Watch the dashboard update in real-time

---

## 🏗️ Architecture

### Data Flow

```
User Submits Candidate(s)
        ↓
Frontend logs to localStorage → Dispatches event
        ↓
Single: Sends to /analyze endpoint
Bulk: Sends multiple requests in parallel
        ↓
Backend preprocesses data
        ↓
LangGraph orchestrates 7 agents:
  • Resume Analyst (resume quality)
  • Cover Letter Analyst (motivation)
  • JD Match Analyst (skills match)
  • GitHub Analyst (code quality)
  • Location Coordinator (location fit)
  • Fairness Auditor (bias check)
  • Referee Agent (final verdict)
        ↓
Streams results via SSE (single) or Promise.all (bulk)
        ↓
Frontend receives events/results
        ↓
Updates activity feed in real-time
        ↓
Saves to localStorage
        ↓
Dashboard updates all 4 tabs
```

### Parallel Agent Architecture (Per Candidate)

```
Candidate Submitted
        ↓
    Layer 1 (Parallel):
    [Resume ║ Cover Letter ║ JD Match ║ GitHub ║ Location] → All run simultaneously
        ↓
    Layer 2 (Sequential):
    Fairness Auditor reviews all 5 results
        ↓
    Layer 3 (Final):
    Referee Agent synthesizes verdict
        ↓
Result Returned
```

### Agent Workflow

1. **Resume Analyst**: Evaluates resume quality, experience, skills
2. **Cover Letter Analyst**: Assesses motivation and communication
3. **JD Match Analyst**: Calculates skills match percentage
4. **GitHub Analyst**: Reviews code quality and contributions
5. **Location Coordinator**: Checks location preferences
6. **Fairness Auditor**: Audits for bias and fairness
7. **Referee Agent**: Synthesizes all scores for final verdict

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get API key from: https://console.groq.com

### Frontend Configuration

File: `frontend/vite.config.js`

- Port: 3000 (configurable)
- API proxy: http://localhost:8000

### Backend Configuration

File: `backend/main.py`

- Port: 8000 (configurable)
- Host: 0.0.0.0 (all interfaces)
- Reload: Enabled for development

---

## 🐳 Deployment

### Production Build

```bash
cd frontend
npm run build
```

Creates optimized production bundle in `frontend/dist/`

### Deploy Frontend

1. Build the application: `npm run build`
2. Upload `dist/` folder to your hosting (Vercel, Netlify, AWS S3, etc.)
3. Configure backend API URL in environment variables

### Deploy Backend

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run with production ASGI server:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
   ```
4. Use reverse proxy (Nginx) to serve frontend and proxy API

### Docker Deployment

```dockerfile
# Backend
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]

# Frontend
FROM node:22
WORKDIR /app
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build
```

---

## 🐛 Troubleshooting

### Frontend Issues

**Dashboard not loading?**

- Ensure backend is running: http://localhost:8000
- Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check console for errors (F12)

**No activity showing?**

- Submit a candidate first by clicking [+] button
- Check browser localStorage: DevTools → Application → localStorage
- Verify API connection in Network tab

**Styling looks broken?**

- Clear browser cache
- Restart Vite dev server: `npm run dev`
- Check CSS file imports

### Backend Issues

**API not responding?**

```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify logs for errors
# Check terminal output
```

**Missing Groq API key?**

```bash
# Ensure .env file exists with GROQ_API_KEY
cat .env  # Should show GROQ_API_KEY=...
```

**Analysis not completing?**

- Check Groq API status: https://status.groq.com
- Verify API key is valid
- Check rate limits
- Review backend logs

### Common Errors

**"Cannot find module 'groq'"**

```bash
pip install langchain-groq
```

**"Port 8000 already in use"**

```bash
# Kill existing process or use different port
python -m uvicorn backend.main:app --port 8001
```

**"Port 3000 already in use"**

```bash
# Use different port in vite.config.js
# Or kill existing process
```

**localStorage quota exceeded**

```javascript
// Clear data in browser console
localStorage.removeItem("hiringSystemActivity");
```

---

## 📊 Data Structures

### Activity Log Entry

```javascript
{
  id: "unique-id",
  timestamp: Date,
  agent: "Agent Name",
  message: "Event description",
  type: "info|success|error|warning",
  metadata: {
    score: 85.5,
    // additional data
  }
}
```

### Candidate Record

```javascript
{
  id: "analysis-id",
  name: "Candidate Name",
  score: 82.5,
  verdict: "SHORTLISTED|REJECTED|PENDING",
  analysisTime: 45000,  // milliseconds
  completedAt: "2025-12-10T10:30:00Z"
}
```

### Agent Metrics

```javascript
{
  "Resume Analyst": {
    completionCount: 10,
    avgScore: 81.5,
    lastScore: 85,
    lastCompleted: "2025-12-10T10:30:00Z"
  }
}
```

---

## 🧪 Testing

### Manual Testing

1. Open http://localhost:3000
2. Click [+] to add candidate
3. Submit test data
4. Verify:
   - Live Activity shows events
   - Statistics update
   - Candidates table updates
   - Agent Metrics show performance

### Test Data Template

```
Resume:
John Doe
Senior Software Engineer with 5+ years experience.
Skills: Python, React, FastAPI, AWS, Docker
...

GitHub URL:
https://github.com/johndoe

Cover Letter:
I'm excited about this opportunity...

Job Description:
We're looking for a Senior Software Engineer...
```

---

## 📝 Update Guidelines

### When Making Changes:

1. **Always update this README** with new features/changes
2. Keep deployment instructions current
3. Update troubleshooting section if issues discovered
4. Document any new environment variables
5. Update API documentation if endpoints change
6. Add new features to Feature list above

### File Organization:

- Keep only essential files in root
- No extra .md files except README.md
- Test files removed from root (not production)
- All documentation consolidated in README.md

---

## 📞 Support & Contributing

For issues, feature requests, or contributions:

- Review this README first
- Check Troubleshooting section
- Review API documentation
- Check backend/frontend code comments

---

## 📄 License

This project is part of HackSorter - an AI-powered hiring system.

---

## 🎯 Status

✅ **Production Ready**

- All components tested and verified
- Real-time features working
- Dashboard fully functional
- API endpoints operational
- Documentation complete

**Last Updated**: December 10, 2025

---

**Happy hiring with AI! 🚀**
