import React, { useState } from 'react';
import {
  Box,
  Container,
  TextField,
  Button,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
} from '@mui/material';
import {
  Security as SecurityIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { scanService, ScanCreateRequest } from '../services/api';

interface NewScanProps {
  onScanCreated: (scanId: string) => void;
}

const NewScan: React.FC<NewScanProps> = ({ onScanCreated }) => {
  const [targetUrl, setTargetUrl] = useState('');
  const [scanDepth, setScanDepth] = useState(2);
  const [scanTypes, setScanTypes] = useState<Record<string, boolean>>({
    // Original scanners
    sql_injection: true,
    xss: true,
    csrf: true,
    headers: true,
    ssl: true,
    xxe: true,
    directory_traversal: true,
    sensitive_data: true,
    command_injection: true,
    open_redirect: true,
    ssrf: true,

    // Advanced scanners - High Impact
    api_security: true,
    business_logic: true,
    authentication: true,

    // Advanced scanners - Medium Impact
    advanced_injection: true,
    client_side: true,
    cloud_infrastructure: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectAll, setSelectAll] = useState(true);

  const scannerCategories = {
    'High Impact (Critical Security)': [
      { key: 'api_security', label: 'API Security', description: 'REST, GraphQL, JWT, Rate Limiting' },
      { key: 'business_logic', label: 'Business Logic', description: 'Race Conditions, Parameter Tampering, Workflow Bypass' },
      { key: 'authentication', label: 'Authentication & Sessions', description: 'MFA, Session Management, Password Policies' },
    ],
    'Injection Attacks': [
      { key: 'sql_injection', label: 'SQL Injection', description: 'Database query manipulation' },
      { key: 'advanced_injection', label: 'Advanced Injection', description: 'NoSQL, LDAP, SSTI, XPath, Code Injection' },
      { key: 'command_injection', label: 'OS Command Injection', description: 'System command execution' },
      { key: 'xxe', label: 'XML External Entity (XXE)', description: 'XML processing vulnerabilities' },
    ],
    'Cross-Site Vulnerabilities': [
      { key: 'xss', label: 'Cross-Site Scripting (XSS)', description: 'JavaScript injection attacks' },
      { key: 'csrf', label: 'Cross-Site Request Forgery', description: 'Unauthorized request execution' },
      { key: 'ssrf', label: 'Server-Side Request Forgery', description: 'Internal resource access' },
    ],
    'Client & Modern Web': [
      { key: 'client_side', label: 'Client-Side Security', description: 'DOM XSS, Storage, WebSocket, PostMessage' },
      { key: 'sensitive_data', label: 'Sensitive Data Exposure', description: 'PII, API keys, credentials leakage' },
    ],
    'Infrastructure & Cloud': [
      { key: 'cloud_infrastructure', label: 'Cloud & Infrastructure', description: 'AWS/Azure/GCP, Containers, Kubernetes' },
      { key: 'ssl', label: 'SSL/TLS Security', description: 'Certificate and protocol validation' },
      { key: 'headers', label: 'Security Headers', description: 'CSP, HSTS, X-Frame-Options' },
    ],
    'File & Path Vulnerabilities': [
      { key: 'directory_traversal', label: 'Directory Traversal', description: 'Path manipulation attacks' },
      { key: 'open_redirect', label: 'Open Redirect', description: 'URL redirection vulnerabilities' },
    ],
  };

  const handleScanTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setScanTypes({
      ...scanTypes,
      [event.target.name]: event.target.checked,
    });
  };

  const handleSelectAll = () => {
    const newValue = !selectAll;
    setSelectAll(newValue);
    const updatedScanTypes: Record<string, boolean> = {};
    Object.keys(scanTypes).forEach((key) => {
      updatedScanTypes[key] = newValue;
    });
    setScanTypes(updatedScanTypes);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const selectedScanTypes = Object.entries(scanTypes)
        .filter(([_, enabled]) => enabled)
        .map(([type, _]) => type);

      if (selectedScanTypes.length === 0) {
        setError('Please select at least one scan type');
        setLoading(false);
        return;
      }

      let cleanedUrl = targetUrl.trim();
      if (!cleanedUrl.startsWith('http://') && !cleanedUrl.startsWith('https://')) {
        cleanedUrl = cleanedUrl.startsWith('localhost') || cleanedUrl.startsWith('127.0.0.1')
          ? `http://${cleanedUrl}`
          : `https://${cleanedUrl}`;
      }

      const request: ScanCreateRequest = {
        target_url: cleanedUrl,
        scan_depth: scanDepth,
        scan_types: selectedScanTypes,
        enable_zap: false,
      };

      const response = await scanService.createScan(request);
      onScanCreated(response.scan_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create scan. Please try again.');
      setLoading(false);
    }
  };

  const selectedCount = Object.values(scanTypes).filter(Boolean).length;
  const totalCount = Object.keys(scanTypes).length;

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <SecurityIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
          <Box>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
              New Security Scan
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Configure and launch a comprehensive vulnerability assessment
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ mb: 4 }} />

        <form onSubmit={handleSubmit}>
          <Grid container spacing={4}>
            {/* Target Configuration */}
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Target Configuration
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={8}>
                      <TextField
                        fullWidth
                        label="Target URL"
                        value={targetUrl}
                        onChange={(e) => setTargetUrl(e.target.value)}
                        placeholder="https://example.com or localhost:8080"
                        required
                        helperText="Enter the base URL to scan (protocol is optional)"
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Scan Depth</InputLabel>
                        <Select
                          value={scanDepth}
                          label="Scan Depth"
                          onChange={(e) => setScanDepth(Number(e.target.value))}
                        >
                          <MenuItem value={1}>Level 1 - Surface</MenuItem>
                          <MenuItem value={2}>Level 2 - Standard</MenuItem>
                          <MenuItem value={3}>Level 3 - Deep</MenuItem>
                          <MenuItem value={4}>Level 4 - Thorough</MenuItem>
                          <MenuItem value={5}>Level 5 - Comprehensive</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Scanner Selection */}
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Vulnerability Scanners
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Select security checks to perform ({selectedCount}/{totalCount} selected)
                      </Typography>
                    </Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={selectAll}
                          onChange={handleSelectAll}
                          color="primary"
                        />
                      }
                      label="Select All"
                    />
                  </Box>

                  {Object.entries(scannerCategories).map(([category, scanners]) => (
                    <Accordion key={category} defaultExpanded={category.includes('High Impact')}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <Typography sx={{ fontWeight: 500 }}>{category}</Typography>
                          <Chip
                            size="small"
                            label={`${scanners.filter(s => scanTypes[s.key]).length}/${scanners.length}`}
                            color={scanners.every(s => scanTypes[s.key]) ? 'success' : 'default'}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <FormGroup>
                          <Grid container spacing={2}>
                            {scanners.map((scanner) => (
                              <Grid item xs={12} md={6} key={scanner.key}>
                                <FormControlLabel
                                  control={
                                    <Checkbox
                                      checked={scanTypes[scanner.key]}
                                      onChange={handleScanTypeChange}
                                      name={scanner.key}
                                      color="primary"
                                    />
                                  }
                                  label={
                                    <Box>
                                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                        {scanner.label}
                                      </Typography>
                                      <Typography variant="caption" color="textSecondary">
                                        {scanner.description}
                                      </Typography>
                                    </Box>
                                  }
                                />
                              </Grid>
                            ))}
                          </Grid>
                        </FormGroup>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            </Grid>

            {/* Submit */}
            <Grid item xs={12}>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Alert severity="info" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  Advanced Features Enabled:
                </Typography>
                <Typography variant="caption">
                  • 17 Advanced Scanners • Real-time Progress Tracking • Comprehensive Reporting
                  • CVSS Scoring • Remediation Guidance
                </Typography>
              </Alert>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => {
                    setTargetUrl('');
                    setScanDepth(2);
                  }}
                  disabled={loading}
                >
                  Reset
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading || selectedCount === 0}
                  startIcon={loading ? <CircularProgress size={20} /> : <SecurityIcon />}
                  sx={{ minWidth: 200 }}
                >
                  {loading ? 'Starting Scan...' : `Start Scan (${selectedCount} checks)`}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      <Alert severity="warning" sx={{ mt: 3 }}>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          ⚠️ Authorization Required
        </Typography>
        <Typography variant="caption">
          Only scan websites you own or have explicit permission to test. Unauthorized scanning may be illegal.
        </Typography>
      </Alert>
    </Container>
  );
};

export default NewScan;
