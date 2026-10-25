# Testing Guide

## Overview

This guide covers testing procedures for the VulnScanner application at different levels.

## Prerequisites

- All services running (Backend, Frontend, PostgreSQL, Redis, Celery)
- Test URLs accessible
- Development environment configured

## 1. Backend Unit Tests

### Setup Test Database

```bash
# Create test database
createdb vulnscanner_test

# Set test environment
export DATABASE_URL=postgresql://vulnscanner:password@localhost:5432/vulnscanner_test
```

### Run Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_scanners.py

# Run with verbose output
pytest -v
```

### Example Test Cases

Create `backend/tests/test_scanners.py`:

```python
import pytest
from scanners.sql_injection import SQLInjectionScanner
from scanners.xss import XSSScanner
from scanners.security_headers import SecurityHeadersScanner

def test_sql_injection_scanner():
    scanner = SQLInjectionScanner()
    # Test with safe URL
    vulnerabilities = scanner.scan("https://httpbin.org/get?id=1")
    assert isinstance(vulnerabilities, list)

def test_xss_scanner():
    scanner = XSSScanner()
    vulnerabilities = scanner.scan("https://httpbin.org/get?name=test")
    assert isinstance(vulnerabilities, list)

def test_security_headers_scanner():
    scanner = SecurityHeadersScanner()
    # Test with a site that likely has missing headers
    vulnerabilities = scanner.scan("http://example.com")
    assert len(vulnerabilities) > 0
```

## 2. API Endpoint Testing

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Create a scan
curl -X POST http://localhost:8000/api/scans/create \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://httpbin.org",
    "scan_depth": 2,
    "scan_types": ["headers", "ssl"]
  }'

# Get scan status (replace with actual scan_id)
curl http://localhost:8000/api/scans/scan_abc123def456

# Get scan results
curl http://localhost:8000/api/scans/scan_abc123def456/results

# Get scan history
curl http://localhost:8000/api/scans/history?page=1&page_size=10

# Download report
curl -O http://localhost:8000/api/reports/scan_abc123def456/download
```

### Testing with Python

```python
import requests

API_URL = "http://localhost:8000"

# Create scan
response = requests.post(
    f"{API_URL}/api/scans/create",
    json={
        "target_url": "https://httpbin.org",
        "scan_depth": 2,
        "scan_types": ["headers", "ssl"]
    }
)
scan = response.json()
scan_id = scan["scan_id"]
print(f"Scan created: {scan_id}")

# Poll for completion
import time
while True:
    response = requests.get(f"{API_URL}/api/scans/{scan_id}")
    status = response.json()
    print(f"Status: {status['status']} - Progress: {status['progress']}%")
    
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(2)

# Get results
response = requests.get(f"{API_URL}/api/scans/{scan_id}/results")
results = response.json()
print(f"Found {len(results['vulnerabilities'])} vulnerabilities")
```

## 3. Frontend Testing

### Component Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- ScanHistory
```

### Example Component Test

Create `frontend/src/components/NewScan.test.tsx`:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import NewScan from './NewScan';

test('renders new scan form', () => {
  render(<NewScan onScanCreated={() => {}} />);
  expect(screen.getByLabelText(/Target URL/i)).toBeInTheDocument();
});

test('validates URL input', async () => {
  render(<NewScan onScanCreated={() => {}} />);
  
  const input = screen.getByLabelText(/Target URL/i);
  fireEvent.change(input, { target: { value: 'invalid-url' } });
  
  const button = screen.getByText(/Start Scan/i);
  fireEvent.click(button);
  
  // Should show validation error
});
```

## 4. Integration Testing

### Full Workflow Test

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be ready
sleep 10

# 3. Run integration test script
python tests/integration_test.py
```

Create `tests/integration_test.py`:

```python
import requests
import time

API_URL = "http://localhost:8000"

def test_full_scan_workflow():
    """Test complete scan workflow"""
    
    # 1. Health check
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")
    
    # 2. Create scan
    response = requests.post(
        f"{API_URL}/api/scans/create",
        json={
            "target_url": "https://httpbin.org",
            "scan_depth": 1,
            "scan_types": ["headers"]
        }
    )
    assert response.status_code == 200
    scan_id = response.json()["scan_id"]
    print(f"✓ Scan created: {scan_id}")
    
    # 3. Wait for completion (max 60 seconds)
    max_attempts = 30
    for attempt in range(max_attempts):
        response = requests.get(f"{API_URL}/api/scans/{scan_id}")
        status = response.json()["status"]
        
        if status == "completed":
            print("✓ Scan completed")
            break
        elif status == "failed":
            print("✗ Scan failed")
            return False
        
        time.sleep(2)
    
    # 4. Get results
    response = requests.get(f"{API_URL}/api/scans/{scan_id}/results")
    assert response.status_code == 200
    results = response.json()
    print(f"✓ Results retrieved: {len(results['vulnerabilities'])} vulnerabilities")
    
    # 5. Download report
    response = requests.get(f"{API_URL}/api/reports/{scan_id}/download")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/pdf'
    print("✓ Report downloaded")
    
    return True

if __name__ == "__main__":
    success = test_full_scan_workflow()
    print("\n" + ("="*50))
    if success:
        print("All integration tests passed! ✓")
    else:
        print("Integration tests failed! ✗")
```

## 5. Load Testing

### Using Apache Bench

```bash
# Test API health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test scan creation (requires JSON)
ab -n 100 -c 5 -p scan_data.json -T application/json \
   http://localhost:8000/api/scans/create
```

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class VulnScannerUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(1)
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def view_history(self):
        self.client.get("/api/scans/history")
    
    @task(2)
    def create_scan(self):
        self.client.post("/api/scans/create", json={
            "target_url": "https://httpbin.org",
            "scan_depth": 1,
            "scan_types": ["headers"]
        })
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## 6. Security Testing

### SQL Injection Test

```bash
# Test API with SQL injection attempts
curl -X POST http://localhost:8000/api/scans/create \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://test.com' OR '1'='1",
    "scan_depth": 1
  }'
# Should be rejected by validation
```

### XSS Test

```bash
# Test with XSS payload in URL
curl -X POST http://localhost:8000/api/scans/create \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://test.com<script>alert(1)</script>",
    "scan_depth": 1
  }'
# Should be rejected by validation
```

## 7. Test Targets

### Safe Testing Targets

1. **httpbin.org** - HTTP testing service
2. **postman-echo.com** - API testing
3. **example.com** - Basic HTTP responses

### NEVER Test These

❌ Production websites without permission
❌ Government websites
❌ Banking/financial services
❌ Healthcare systems
❌ Educational institutions

## 8. Troubleshooting Tests

### Database Issues

```bash
# Reset test database
dropdb vulnscanner_test
createdb vulnscanner_test

# Run migrations
cd backend
alembic upgrade head
```

### Redis Connection

```bash
# Test Redis connectivity
redis-cli ping
# Should return PONG

# Check keys
redis-cli keys "*"
```

### Celery Worker

```bash
# Check worker status
celery -A tasks.celery_app inspect active

# Purge queue
celery -A tasks.celery_app purge
```

## 9. CI/CD Testing

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: vulnscanner_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/vulnscanner_test
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 10. Test Checklist

### Before Release

- [ ] All unit tests pass
- [ ] Integration tests complete successfully
- [ ] API endpoints return correct status codes
- [ ] Frontend renders without errors
- [ ] Scans execute and complete
- [ ] Reports generate correctly
- [ ] Database queries optimized
- [ ] Error handling works correctly
- [ ] Input validation prevents injection
- [ ] CORS configured properly
- [ ] Environment variables set
- [ ] Docker containers build successfully
- [ ] Load testing shows acceptable performance
- [ ] Security testing passes
- [ ] Documentation is up-to-date

## Expected Test Results

### Security Headers Test
- Should find 5-7 missing headers on most sites
- HSTS, CSP, X-Frame-Options commonly missing

### SSL Test
- Valid HTTPS sites: No critical issues
- HTTP sites: Critical vulnerability flagged

### SQL Injection Test
- Most modern sites: No vulnerabilities
- Legacy sites: May find issues

### XSS Test
- Reflected XSS depends on input handling
- Should detect unencoded parameter reflection

## Test Data

### Valid Test Payloads

```json
{
  "target_url": "https://httpbin.org",
  "scan_depth": 2,
  "scan_types": ["sql_injection", "xss", "csrf", "headers", "ssl"]
}
```

### Invalid Test Payloads

```json
{
  "target_url": "not-a-url",
  "scan_depth": 10,
  "scan_types": ["invalid_type"]
}
```

## Performance Benchmarks

### Expected Response Times

- Health check: < 50ms
- Create scan: < 200ms
- Get scan status: < 100ms
- Get results: < 500ms
- Download report: < 1s

### Scan Duration

- Level 1 (Quick): 30-60 seconds
- Level 2 (Standard): 1-2 minutes
- Level 3 (Deep): 3-5 minutes
- Level 5 (Comprehensive): 5-10 minutes

---

**Remember**: Always obtain proper authorization before scanning any websites!
