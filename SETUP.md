# VulnScanner - Quick Start Guide

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
cd D:\pentration
```

2. **Create environment file**
```bash
copy .env.example .env
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
copy ..\.env.example .env
# Edit .env with your database credentials
```

5. **Start Redis** (if not using Docker)
```bash
# Install Redis for Windows or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

6. **Start PostgreSQL** (if not using Docker)
```bash
# Make sure PostgreSQL is running and create database
createdb vulnscanner_db
```

7. **Run the backend**
```bash
uvicorn main:app --reload
```

8. **Start Celery worker** (in a new terminal)
```bash
cd backend
venv\Scripts\activate
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create environment file**
```bash
copy .env .env.local
```

4. **Start development server**
```bash
npm start
```

5. **Access the application**
- Open browser at: http://localhost:3000

## 📖 Usage

### Creating a New Scan

1. Click "New Scan" in the navigation bar
2. Enter the target URL (e.g., https://example.com)
3. Select scan depth (1-5)
4. Choose scan types:
   - SQL Injection
   - Cross-Site Scripting (XSS)
   - CSRF Protection
   - Security Headers
   - SSL/TLS Configuration
5. Click "Start Scan"

### Monitoring Scan Progress

- Real-time progress updates
- Vulnerability count by severity
- Estimated completion time

### Viewing Results

1. Navigate to "History" tab
2. Click "View Details" on any completed scan
3. Review vulnerabilities organized by severity
4. Download PDF report

### Downloading Reports

- Click "Download Report" button in scan results
- PDF includes:
  - Scan summary
  - Severity breakdown
  - Detailed vulnerability descriptions
  - Remediation recommendations
  - CWE/CVE references

## 🔧 Configuration

### Backend Configuration (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vulnscanner_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Scan Settings
MAX_CONCURRENT_SCANS=3
SCAN_TIMEOUT=3600
REQUEST_TIMEOUT=30
```

### Frontend Configuration (.env)

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Verify PostgreSQL is running
- Check Redis connection
- Verify all dependencies installed: `pip install -r requirements.txt`

### Celery worker errors
- On Windows, use: `celery -A tasks.celery_app worker --loglevel=info --pool=solo`
- Check Redis connection
- Verify environment variables

### Frontend build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)
- Verify API URL in .env

### Scans fail immediately
- Check target URL is accessible
- Verify firewall/antivirus not blocking requests
- Check backend logs for errors

## 📚 API Documentation

Access interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚠️ Important Notes

- **Authorization Required**: Only scan websites you own or have permission to test
- **Educational Purpose**: This tool is for learning and authorized testing only
- **Rate Limiting**: Be respectful of target servers
- **False Positives**: Always manually verify findings

## 🎓 MCA Project Documentation

For academic purposes, this project demonstrates:
- Full-stack development
- Microservices architecture
- Asynchronous task processing
- Security vulnerability assessment
- REST API design
- Real-time monitoring
- Report generation
- Database design

## 📄 License

MIT License - For educational purposes only

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check backend logs: `logs/app.log`
4. Review Docker logs: `docker-compose logs`
