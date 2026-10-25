# ⚡ VulnScanner Pro v2.0 - Quick Start Guide

Get your advanced security testing platform up and running in **under 5 minutes**.

---

## 🎯 **What You Get with v2.0**

| Feature | Status |
|---------|---------|
| ✅ **17 Advanced Security Scanners** | READY |
| ✅ **Modern Dashboard with Charts** | READY |
| ✅ **Analytics & Trends** | READY |
| ✅ **Scheduled Scans** | READY |
| ✅ **Scan Comparison Tool** | READY |
| ✅ **Dark/Light Mode** | READY |
| ✅ **Real-time Progress** | READY |
| ✅ **Comprehensive Reporting** | READY |

---

## 🚀 **5-Minute Setup**

### **Step 1: Prerequisites**
Make sure you have:
- ✅ Python 3.11+
- ✅ Node.js 18+
- ✅ Docker & Docker Compose (optional)
- ✅ 4GB RAM minimum
- ✅ Windows/Mac/Linux

### **Step 2: Clone & Setup**
```bash
# If you have the project, navigate to it
cd vulnscanner

# Install backend dependencies
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### **Step 3: Configure Environment**
```bash
cd ../backend
cp .env.example .env

# Edit .env with your configuration
# Set DATABASE_URL, REDIS_URL, SECRET_KEY
```

### **Step 4: Start Services**
```bash
# Terminal 1: Start database and cache
docker-compose up -d

# Terminal 2: Start Celery worker
cd backend
celery -A tasks.celery_app worker --pool=solo --loglevel=info

# Terminal 3: Start FastAPI backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Start React frontend
cd frontend
npm start
```

### **Step 5: Access the Platform**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Default Credentials**: None required (add authentication in production)

---

## 🎨 **First-Time Tour**

### **1. Dashboard Overview** (`http://localhost:3000`)
- View scan statistics
- Check vulnerability trends
- See recent activity
- Quick-start new scan

### **2. Start Your First Scan**
1. Click **"New Scan"** in navigation
2. Enter target URL: `https://example.com` (or use `http://localhost:8080`)
3. Select scanners (default: all 17)
4. Choose scan depth (recommended: 2-3)
5. Click **"Start Scan"**

### **3. Monitor Progress**
- Live progress bar
- Real-time scanner status
- Estimated completion time
- Notification when complete

### **4. View Results**
- Severity breakdown (Critical, High, Medium, Low, Info)
- Detailed vulnerability descriptions
- CVSS scores
- Remediation guidance
- Download PDF report

---

## 🔍 **Key Features in 60 Seconds**

### **Advanced Scanners**
- **API Security**: Test REST, GraphQL, JWT, rate limiting
- **Business Logic**: Race conditions, parameter tampering, workflow bypass
- **Authentication**: MFA bypass, session fixation, password policies
- **Cloud Security**: AWS/Azure/GCP, containers, Kubernetes

### **Modern UI Features**
- **Dashboard**: Real-time metrics and charts
- **Analytics**: Trend analysis and scanner performance
- **Scheduled Scans**: Cron-based automation
- **Compare Scans**: Track remediation progress
- **Dark Mode**: Eye-friendly interface

---

## 📋 **Sample Use Cases**

### **Case 1: API Security Testing**
```bash
# Test API endpoints
Target: https://api.example.com
Scanners: api_security, business_logic, authentication
Depth: 3
```

### **Case 2: Web Application Security**
```bash
# Comprehensive web app test
Target: https://webapp.example.com
Scanners: All 17 scanners
Depth: 2
```

### **Case 3: Local Development Testing**
```bash
# Test local development server
Target: http://localhost:8080
Scanners: api_security, xss, csrf, headers
Depth: 2
```

---

## 🚨 **Production Checklist**

### **Before Going Live**
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Enable HTTPS for API and frontend
- [ ] Configure CORS properly
- [ ] Set up proper database credentials
- [ ] Enable Redis authentication
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure firewall rules
- [ ] Set up backup strategy

### **Security Hardening**
- [ ] Implement rate limiting
- [ ] Add JWT authentication
- [ ] Enable audit logging
- [ ] Regular dependency updates
- [ ] Security headers configuration
- [ ] API key management

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not, restart services
docker-compose down
docker-compose up -d
```

#### **2. Celery Not Starting**
```bash
# Check Redis connection
redis-cli ping

# Restart Celery with debug
celery -A tasks.celery_app worker --pool=solo --loglevel=debug
```

#### **3. Frontend Won't Start**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

#### **4. Scanner Timeouts**
```bash
# Increase timeout in .env
SCAN_TIMEOUT=60
MAX_CONCURRENT_SCANS=2
```

---

## 📈 **Performance Tips**

### **For Fast Scans**
```bash
# .env configuration for speed
SCAN_TIMEOUT=30
MAX_CONCURRENT_SCANS=5
SCAN_DEPTH=2
ENABLE_ZAP=false
```

### **For Thorough Scans**
```bash
# .env configuration for depth
SCAN_TIMEOUT=120
MAX_CONCURRENT_SCANS=2
SCAN_DEPTH=4
ENABLE_ZAP=true  # If OWASP ZAP is installed
```

---

## 🔧 **Customization Options**

### **Add Custom Payloads**
```python
# backend/scanners/your_scanner.py
class YourCustomScanner:
    def __init__(self):
        self.payloads = [
            'your-custom-payload',
            'another-payload',
        ]
    
    def scan(self, url):
        # Your custom scanning logic
        pass
```

### **Custom Scanner Categories**
```javascript
// frontend/src/components/NewScan.tsx
const customCategories = {
    'Your Category': [
        { key: 'your_scanner', label: 'Your Scanner', description: 'Custom description' },
    ],
};
```

### **API Integration**
```bash
# Create scan via API
curl -X POST "http://localhost:8000/api/scans/create" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "scan_depth": 2,
    "scan_types": ["api_security", "business_logic"]
  }'
```

---

## 🎓 **Educational Mode**

### **For Learning & Practice**
```bash
# Use local test applications
Target: http://dvwa.local  # Damn Vulnerable Web App
Target: http://bwapp.local # Buggy Web Application
Target: http://juice-shop  # OWASP Juice Shop

# Scan with limited scope
Scanners: sql_injection, xss, headers
Depth: 1
```

### **Training Exercises**
1. **Beginner**: Test local DVWA instance
2. **Intermediate**: Build custom scanner
3. **Advanced**: Add ML-based detection
4. **Expert**: Implement zero-day detection

---

## 📞 **Getting Help**

### **Documentation**
- **API Docs**: `http://localhost:8000/docs`
- **Scanner Docs**: Check each scanner's docstring
- **Component Docs**: Check React component PropTypes

### **Debug Mode**
```bash
# Backend debug
uvicorn main:app --reload --log-level debug

# Celery debug
celery -A tasks.celery_app worker --pool=solo --loglevel=debug

# Frontend debug
npm start -- --verbose
```

### **Community Support**
- Discord: [Join Community]
- GitHub: [Issues]
- Stack Overflow: Tag `vulnscanner`

---

## 🎉 **Congratulations!**

You've successfully set up **VulnScanner Pro v2.0** - one of the most comprehensive open-source security testing platforms.

### **Next Steps**
1. **Run your first scan** on a test application
2. **Explore the analytics dashboard**
3. **Schedule daily security checks**
4. **Compare before/after remediation**
5. **Customize for your specific needs**

### **Remember**
- ✅ **Only scan authorized targets**
- ✅ **Follow responsible disclosure**
- ✅ **Keep dependencies updated**
- ✅ **Contribute back to the community**

---

**Happy Security Testing! 🛡️**

*Quick Start Guide v1.0 - October 16, 2026*
*Last updated: 2026-10-16T11:35:00Z*
