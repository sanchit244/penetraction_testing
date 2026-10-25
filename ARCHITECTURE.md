# Architecture & Technical Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  New Scan    │  │ Scan History │  │ Scan Results & Viz   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                      API Gateway
                            │
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints                                      │   │
│  │  - POST /api/scans/create                                │   │
│  │  - GET /api/scans/{id}                                   │   │
│  │  - GET /api/scans/{id}/results                           │   │
│  │  - GET /api/reports/{id}/download                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────┴──────────────────────────────────┐ │
│  │         Core Components                                    │ │
│  ├──────────────────┬──────────────────┬──────────────────┐   │ │
│  │  Vulnerability   │  Report          │  Database        │   │ │
│  │  Scanners        │  Generator       │  Manager         │   │ │
│  │                  │                  │                  │   │ │
│  │ • SQL Injection  │ • PDF Export     │ • Scan Records   │   │ │
│  │ • XSS            │ • Remediation    │ • Vulnerabilities│   │ │
│  │ • CSRF           │ • CVSS Scores    │ • Scan History   │   │ │
│  │ • Headers        │ • Risk Summary   │                  │   │ │
│  │ • SSL/TLS        │                  │                  │   │ │
│  └──────────────────┴──────────────────┴──────────────────┘   │ │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───────┐          ┌────────┐         ┌──────────┐
    │ Redis │          │Database│         │  OWASP   │
    │ Broker│          │PostgreSQL       │  ZAP API │
    └───────┘          └────────┘         │Optional) │
        │                                 └──────────┘
        │
    ┌─────────────────────┐
    │ Celery Worker Pool  │
    │ (Async Tasks)       │
    └─────────────────────┘
```

## Key Components

### 1. Vulnerability Scanners

**SQL Injection Scanner**
- Tests parameters with SQL payloads
- Detects error-based and time-based SQLi
- Identifies vulnerable endpoints

**XSS Scanner**
- Tests for reflected XSS
- Checks parameter reflection
- Validates payload encoding

**CSRF Scanner**
- Checks CSRF token presence
- Validates SameSite cookie attributes
- Tests form protection

**Security Headers Scanner**
- Verifies required headers
- Validates CSP policies
- Checks certificate configuration

**SSL/TLS Scanner**
- Validates certificates
- Checks protocol versions
- Tests cipher strength

### 2. Task Processing

**Celery Workers**
- Asynchronous scan execution
- Parallel vulnerability checking
- Progress tracking

**Redis Broker**
- Message queue management
- State persistence
- Task scheduling

### 3. Data Layer

**PostgreSQL Database**
- Scan metadata storage
- Vulnerability records
- Historical data
- User analytics

**Report Storage**
- PDF report files
- Remediation guidelines
- CVSS scoring

## Data Flow

### Scan Creation Flow
```
1. User submits scan request via UI
2. API validates input (URL format, depth)
3. Scan record created in database (PENDING status)
4. Celery task queued
5. UI receives scan_id immediately
6. Worker picks up task from queue
```

### Scan Execution Flow
```
1. Task status updated to RUNNING
2. Initialize VulnerabilityScanner
3. For each enabled scan type:
   - Run individual scanner
   - Collect vulnerabilities
4. Aggregate results by severity
5. Update database with findings
6. Generate PDF report
7. Update status to COMPLETED
```

### Result Retrieval Flow
```
1. User requests scan results
2. API fetches from database
3. Vulnerabilities organized by severity
4. CVSS scores calculated
5. Response sent to frontend
6. UI renders interactive results
```

## Security Considerations

### Authentication & Authorization
- Future: JWT token support
- API key validation
- RBAC for scan management

### Input Validation
- URL format validation
- Payload sanitization
- SQL injection prevention in queries

### Output Encoding
- XSS prevention in reports
- Safe PDF generation
- HTML entity encoding

### Network Security
- CORS configuration
- HTTPS enforcement
- Request timeout limits

### Data Protection
- Password hashing with bcrypt
- Encrypted sensitive fields
- Secure cookie flags

## Scalability

### Horizontal Scaling
- Stateless API servers
- Multiple Celery workers
- Load balancer ready

### Performance Optimization
- Connection pooling
- Scan result caching
- Indexed database queries

### High Availability
- Redis failover support
- Database replication ready
- Worker redundancy

## Monitoring & Logging

### Application Logging
- Request/response logging
- Error tracking
- Scan execution logs
- Performance metrics

### Health Checks
- Database connectivity
- Redis connection status
- Worker availability
- API responsiveness

## Deployment Architecture

### Docker Deployment
- Containerized services
- Docker Compose orchestration
- Volume management
- Network isolation

### Production Considerations
- Kubernetes support ready
- Environment-based configuration
- Secrets management
- CI/CD integration points
