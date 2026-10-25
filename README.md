# Automated Web Application Vulnerability & Penetration Testing Dashboard

A centralized security portal for automated web application vulnerability scanning and penetration testing with real-time reporting.

## 🎯 Features

- **Automated Vulnerability Scanning**: SQL Injection, XSS, CSRF, Security Headers, SSL/TLS
- **OWASP ZAP Integration**: Industry-standard security testing
- **Risk Assessment**: CVSS scoring and severity classification
- **Async Processing**: Celery + Redis for non-blocking scans
- **Real-time Updates**: WebSocket support for live scan progress
- **Comprehensive Reports**: Downloadable PDF reports with remediation guidance
- **Modern Dashboard**: React-based UI with responsive design

## 🏗️ Architecture

```
├── backend/          # FastAPI backend
│   ├── api/         # REST API endpoints
│   ├── core/        # Core business logic
│   ├── scanners/    # Vulnerability scanners
│   ├── tasks/       # Celery tasks
│   └── models/      # Data models
├── frontend/         # React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── pages/
└── docker/          # Docker configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Redis
- OWASP ZAP (optional, for advanced scanning)

### Installation

1. **Clone and setup backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup frontend**:
```bash
cd frontend
npm install
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start services with Docker**:
```bash
docker-compose up -d
```

5. **Run backend**:
```bash
cd backend
uvicorn main:app --reload
```

6. **Run frontend**:
```bash
cd frontend
npm start
```

Access the dashboard at `http://localhost:3000`

## 📊 API Endpoints

- `POST /api/scans/create` - Initiate new scan
- `GET /api/scans/{scan_id}` - Get scan status
- `GET /api/scans/{scan_id}/results` - Get scan results
- `GET /api/scans/{scan_id}/report` - Download PDF report
- `GET /api/scans/history` - List all scans

## 🔒 Security Checks

1. **SQL Injection**: Time-based, error-based, union-based
2. **Cross-Site Scripting (XSS)**: Reflected, stored, DOM-based
3. **CSRF Protection**: Token validation, SameSite cookie checks
4. **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
5. **SSL/TLS**: Certificate validation, cipher strength
6. **Authentication**: Weak credentials, session management
7. **Information Disclosure**: Debug info, version exposure

## 📈 Tech Stack

**Backend**:
- FastAPI (Python web framework)
- Celery (Async task queue)
- Redis (Message broker & cache)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- OWASP ZAP API
- ReportLab (PDF generation)

**Frontend**:
- React 18
- TypeScript
- Material-UI
- Recharts (Data visualization)
- Axios (HTTP client)
- Socket.io (Real-time updates)

## 🎓 Educational Value (MCA Project)

This project demonstrates:
- ✅ Full-stack development (FastAPI + React)
- ✅ Asynchronous processing architecture
- ✅ Security vulnerability assessment
- ✅ API design and integration
- ✅ Real-time communication
- ✅ Report generation
- ✅ Docker containerization
- ✅ Database design
- ✅ Modern DevOps practices

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for educational and authorized security testing only. Always obtain proper authorization before scanning any web applications. Unauthorized scanning may be illegal.
