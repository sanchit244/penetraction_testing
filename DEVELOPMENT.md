# Development Guide

## Project Structure

```
vulnscanner/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── scans.py          # Scan endpoints
│   │   └── reports.py        # Report endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration
│   │   └── database.py       # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py        # Pydantic schemas
│   │   └── scan.py           # SQLAlchemy models
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── scanner.py        # Main scanner orchestrator
│   │   ├── sql_injection.py
│   │   ├── xss.py
│   │   ├── csrf.py
│   │   ├── security_headers.py
│   │   └── ssl_scanner.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py     # Celery configuration
│   │   └── scan_tasks.py     # Scan task definition
│   ├── utils/
│   │   ├── __init__.py
│   │   └── report_generator.py
│   ├── main.py               # FastAPI app entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── NewScan.tsx
│   │   │   ├── ScanProgress.tsx
│   │   │   ├── ScanHistory.tsx
│   │   │   └── ScanResultsView.tsx
│   │   ├── services/
│   │   │   └── api.ts        # API client
│   │   ├── App.tsx           # Main app component
│   │   ├── index.tsx         # React entry
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── SETUP.md
├── ARCHITECTURE.md
└── DEVELOPMENT.md
```

## Adding New Vulnerability Scanners

### 1. Create Scanner Class

```python
# backend/scanners/new_vuln.py
from typing import List
from models.schemas import VulnerabilitySchema, SeverityEnum

class NewVulnerabilityScanner:
    """Scan description"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan implementation"""
        vulnerabilities = []
        # Scanning logic
        return vulnerabilities
```

### 2. Register Scanner

```python
# backend/scanners/scanner.py
from scanners.new_vuln import NewVulnerabilityScanner

class VulnerabilityScanner:
    def __init__(self, timeout: int = 30):
        self.scanners = {
            'new_vuln': NewVulnerabilityScanner(timeout),
            # ... other scanners
        }
```

### 3. Update Frontend

Add checkbox to `NewScan.tsx` scan types:
```jsx
<FormControlLabel
  control={
    <Checkbox
      checked={scanTypes.new_vuln}
      onChange={handleScanTypeChange}
      name="new_vuln"
    />
  }
  label="New Vulnerability Type"
/>
```

## Extending the Backend

### Adding New API Endpoints

```python
# backend/api/custom.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

Then include in `main.py`:
```python
from api import custom
app.include_router(custom.router)
```

### Database Migrations

Using Alembic for schema changes:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

## Frontend Development

### Creating New Components

```tsx
// frontend/src/components/MyComponent.tsx
import React from 'react';
import { Box, Typography } from '@mui/material';

interface MyComponentProps {
  title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  return (
    <Box>
      <Typography variant="h5">{title}</Typography>
    </Box>
  );
};

export default MyComponent;
```

### Consuming API Services

```tsx
import { scanService } from '../services/api';

const MyComponent = () => {
  useEffect(() => {
    const fetchData = async () => {
      const scan = await scanService.getScanStatus('scan_id');
      // Use data
    };
    fetchData();
  }, []);
};
```

## Testing

### Backend Unit Tests

```bash
# Run pytest
pytest backend/tests/

# With coverage
pytest --cov=backend backend/tests/
```

### Frontend Tests

```bash
# Run React tests
npm test

# Generate coverage
npm test -- --coverage
```

## Performance Optimization

### Backend

1. **Database Optimization**
   - Add indexes on frequently queried fields
   - Use pagination for large result sets
   - Cache scan summaries

2. **API Response**
   - Implement response compression
   - Use pagination
   - Lazy load vulnerabilities

### Frontend

1. **Component Optimization**
   - Use React.memo for expensive components
   - Implement virtualization for large lists
   - Lazy load routes

2. **Network Optimization**
   - Implement request batching
   - Use WebSocket for real-time updates
   - Cache API responses

## Debugging

### Backend Debugging

```bash
# Enable debug logging
export DEBUG=True

# Run with debugger
python -m pdb main.py
```

### Frontend Debugging

1. React Developer Tools browser extension
2. Chrome DevTools Network tab
3. Console for JavaScript errors

### Docker Debugging

```bash
# View logs
docker-compose logs backend
docker-compose logs frontend

# Interactive terminal
docker-compose exec backend bash
```

## Common Issues & Solutions

### Scan hangs indefinitely
- Check Celery worker is running
- Verify Redis connection
- Check database connectivity

### API returns 500 error
- Check backend logs
- Verify database connection
- Check environment variables

### Frontend can't connect to API
- Verify REACT_APP_API_URL
- Check CORS settings
- Verify backend is running

### Database connection errors
- Verify PostgreSQL is running
- Check connection string format
- Verify credentials

## CI/CD Integration

### GitHub Actions Example

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
      
      redis:
        image: redis:7
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Run tests
        run: pytest backend/tests/
      
      - name: Build Docker images
        run: docker-compose build
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Max line length: 100
- Use Black formatter

### TypeScript/React
- Use ESLint
- Prefer functional components
- Use hooks over class components
- Keep components small and focused

## Documentation Standards

### Code Comments
- Explain WHY, not WHAT
- Keep comments concise
- Update comments with code changes

### Docstrings
```python
def scan(self, url: str) -> List[VulnerabilitySchema]:
    """
    Scan URL for vulnerabilities.
    
    Args:
        url: Target URL to scan
    
    Returns:
        List of detected vulnerabilities
    """
```

## Release Process

1. Create release branch
2. Update version numbers
3. Update CHANGELOG
4. Run full test suite
5. Build Docker images
6. Tag release
7. Push to main
8. Deploy to production
