# ZenithGuard 🛡️
### Unified Financial Crime & Insider Risk Intelligence Platform

ZenithGuard is an enterprise-grade financial crime detection and insider threat intelligence platform. It fuses employee access telemetry (IAM, core banking logs, branch-level access control) with transaction graphs to expose complex money laundering rings, smurfing/structuring patterns, circular transaction paths, and insider collusion in near real-time.

---

## 🌟 Key Features

- **Insider Touch & Access Correlation**: Cross-references employee account queries and profile modifications against subsequent high-risk customer transactions within configurable time windows.
- **Multi-Vector Fraud Detection Engines**:
  - **Circular Flow Detection**: Cycles and layering loops in transaction subgraphs.
  - **Transaction Splitting / Structuring**: Detection of transactions just below regulatory reporting thresholds (e.g., INR 50,000 threshold).
  - **Rapid Pass-Through**: Swift pass-through velocity identifying money mule accounts.
  - **Role-DNA Anomaly Profiler**: Statistical and behavioral baselining of employees by cohort and role.
  - **Unauthorized Access & Mismatch**: Alerts when staff query customers outside their allocated branch or customer range without approved service tickets.
  - **Collusion Engine**: Exposes covert relationships between staff members and external fraud rings.
- **False Positive Shield**: Suppresses noise by cross-checking verified customer service tickets, known payroll patterns, and scheduled batch jobs.
- **Interactive Money Flow Visualizer & Case Replay**: Visual canvas showing transaction paths, node relationships, risk gauges, and step-by-step playback slider.
- **Live Threat Simulator**: Inject synthetic attacks (suspicious insider query, structuring wave, circular loop) or benign tickets to test pipeline defenses on the fly.
- **Forensic PDF Dossier Export**: Generate audit-ready regulatory reports and SAR dossiers with cryptographic SHA-256 evidence hashing.

---

## 🏛️ System Architecture & Tech Stack

- **Backend**:
  - **Language**: Python 3.10+
  - **Framework**: FastAPI (asynchronous, OpenAPI 3.0 auto-documented)
  - **ORM & DB**: SQLAlchemy 2.0 with SQLite (`zenithguard.db`)
  - **Analytics & Graphs**: Pandas, NumPy, NetworkX, Scikit-Learn
  - **Reporting**: ReportLab for forensic PDF document synthesis
  - **Validation**: Pydantic v2
- **Frontend**:
  - **Framework**: React 18 with Vite
  - **Routing**: React Router v6
  - **Styling**: Tailwind CSS & Lucide React icons
  - **Visualizations**: Recharts & custom interactive SVG flow graphs

---

## 📋 Prerequisites

Before running the platform, ensure you have installed:
- **Python**: 3.10, 3.11, or 3.12 (`python --version`)
- **Node.js**: 18+ or 20+ (`node -v`)
- **Package Manager**: `npm` (included with Node.js) or `yarn` / `pnpm`

---

## 🚀 Quick Start Guide

Follow these steps to get both the backend and frontend up and running.

### 1. Backend Installation & Run

1. **Open a terminal** and navigate to the project root directory:
   ```bash
   cd c:\Users\Sakshi\hackmatrix
   ```

2. *(Recommended)* **Create and activate a Python virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration** *(Optional)*:
   The project comes pre-configured with SQLite defaults. If needed, copy `.env.example` to `.env`:
   - Windows PowerShell:
     ```powershell
     Copy-Item .env.example .env
     ```
   - Linux / macOS / Git Bash:
     ```bash
     cp .env.example .env
     ```

5. *(Optional)* **Re-seed Synthetic Data**:
   A seeded SQLite database (`backend/data/zenithguard.db`) is already included. If you want to regenerate a fresh dataset:
   ```bash
   python backend/data/generate.py
   ```

6. **Start the FastAPI Backend Server**:
   ```bash
   python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *The backend will now be live on `http://127.0.0.1:8000`.*

---

### 2. Frontend Installation & Run

1. **Open a second terminal window** and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   *The frontend development server will launch on `http://127.0.0.1:5173`.*

---

## 🌐 Application URLs & Endpoints

| Service / Interface | URL | Description |
| :--- | :--- | :--- |
| **Frontend Web Application** | [http://127.0.0.1:5173](http://127.0.0.1:5173) | Main investigator portal (Dashboard, Alert Queue, Role-DNA, Simulator) |
| **Backend API Interactive Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Swagger UI for interactive API exploration and testing |
| **Backend ReDoc Specification** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Clean, comprehensive API documentation viewer |
| **API Health & Status Endpoint** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Health check returning service status and timestamp |

---

## 🧪 Running Automated Tests

To execute unit and integration tests for the detection engines:
```bash
pytest backend/tests/test_detection.py -v
```

---

## 📂 Project Structure

```text
ZenithGuard/
├── backend/
│   ├── app/
│   │   ├── detection/             # Multi-vector detection algorithms
│   │   │   ├── access_mismatch.py # Branch/customer boundary violations
│   │   │   ├── circular_flow.py   # Cycle and layering detection
│   │   │   ├── collusion.py       # Staff-customer collusion analysis
│   │   │   ├── false_positive_shield.py # Ticket & routine suppression
│   │   │   ├── fusion.py          # Unified alert scoring and weighting
│   │   │   ├── insider_touch.py   # Telemetry correlation with transactions
│   │   │   ├── pipeline.py        # Central scan coordinator
│   │   │   ├── role_dna_anomaly.py# Cohort statistical profiler
│   │   │   └── transaction_splitting.py # Structuring / smurfing engine
│   │   ├── export_pdf.py          # ReportLab forensic report generation
│   │   └── main.py                # FastAPI REST endpoints & routes
│   ├── data/
│   │   ├── csv/                   # Raw generated telemetry and ledger data
│   │   ├── database.py            # SQLAlchemy database engine and session
│   │   ├── generate.py            # Synthetic dataset generator
│   │   ├── models.py              # Database ORM entity models
│   │   └── zenithguard.db         # Seeded SQLite database
│   └── tests/
│       └── test_detection.py      # Core detection engine test suite
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI widgets & graphs
│   │   │   ├── CaseReplaySlider.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── MoneyFlowGraph.jsx # Interactive node-link transaction graph
│   │   │   └── RiskGauge.jsx
│   │   ├── pages/                 # Full investigator pages
│   │   │   ├── AlertDetail.jsx    # Deep-dive investigation & PDF export
│   │   │   ├── AlertQueue.jsx     # Filterable alert inbox
│   │   │   ├── Dashboard.jsx      # High-level KPIs & trend charts
│   │   │   ├── RoleDnaProfiler.jsx# Employee telemetry & risk profiling
│   │   │   ├── ShieldMetrics.jsx  # False Positive Shield effectiveness
│   │   │   └── Simulator.jsx      # Live attack and scenario injection
│   │   ├── App.jsx                # Layout & client router
│   │   ├── index.css              # Global styles & Tailwind directives
│   │   └── main.jsx               # React entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js             # Vite config with backend proxy (/api -> :8000)
├── .env.example                   # Baseline environment configurations
├── requirements.txt               # Python backend dependencies
└── README.md                      # Platform documentation and guide
```

---

## 🔒 Security & Privacy Notice
All employee names, customer records, and transaction details in this repository are synthetically generated for demonstration and evaluation purposes. Do not commit actual banking secrets or production API credentials to version control.
