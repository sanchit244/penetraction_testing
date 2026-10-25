import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { scanService, ScanResults } from '../services/api';

interface ScanResultsViewProps {
  scanId: string;
  onBack: () => void;
}

const ScanResultsView: React.FC<ScanResultsViewProps> = ({ scanId, onBack }) => {
  const [results, setResults] = useState<ScanResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, [scanId]);

  const loadResults = async () => {
    try {
      const data = await scanService.getScanResults(scanId);
      setResults(data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load scan results');
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string): "error" | "warning" | "info" | "success" | "default" => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const handleDownloadReport = () => {
    window.open(scanService.downloadReport(scanId), '_blank');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={onBack} sx={{ mt: 2 }}>
          Back to History
        </Button>
      </Container>
    );
  }

  if (!results) return null;

  const sortedVulnerabilities = [...results.vulnerabilities].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button startIcon={<ArrowBackIcon />} onClick={onBack}>
          Back to History
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={handleDownloadReport}
        >
          Download PDF Report
        </Button>
      </Box>

      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Scan Results
        </Typography>

        <Box mb={3}>
          <Typography variant="body1" color="text.secondary">
            Target: {results.target_url}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Scan ID: {results.scan_id}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Duration: {results.summary.scan_duration}
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom>
          Summary
        </Typography>

        <Grid container spacing={2} mb={4}>
          <Grid item xs={6} sm={4} md={2}>
            <Card sx={{ bgcolor: '#ffebee' }}>
              <CardContent>
                <Typography variant="h5" color="error">
                  {results.summary.critical_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Critical
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card sx={{ bgcolor: '#fff3e0' }}>
              <CardContent>
                <Typography variant="h5" color="warning.main">
                  {results.summary.high_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  High
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card sx={{ bgcolor: '#fff9c4' }}>
              <CardContent>
                <Typography variant="h5">
                  {results.summary.medium_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Medium
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card sx={{ bgcolor: '#e8f5e9' }}>
              <CardContent>
                <Typography variant="h5" color="success.main">
                  {results.summary.low_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Low
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card sx={{ bgcolor: '#e3f2fd' }}>
              <CardContent>
                <Typography variant="h5" color="info.main">
                  {results.summary.info_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Info
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent>
                <Typography variant="h5">
                  {results.summary.total_vulnerabilities}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h6" gutterBottom>
          Vulnerabilities ({sortedVulnerabilities.length})
        </Typography>

        {sortedVulnerabilities.length === 0 ? (
          <Alert severity="success" sx={{ mt: 2 }}>
            No vulnerabilities found! Your application appears to be secure.
          </Alert>
        ) : (
          <Box mt={2}>
            {sortedVulnerabilities.map((vuln, index) => (
              <Accordion key={index} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    <Chip
                      label={vuln.severity.toUpperCase()}
                      color={getSeverityColor(vuln.severity)}
                      size="small"
                    />
                    <Typography variant="body1" fontWeight="bold">
                      {vuln.name}
                    </Typography>
                    {vuln.cvss_score && (
                      <Chip
                        label={`CVSS: ${vuln.cvss_score}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Description:
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {vuln.description}
                    </Typography>

                    <Typography variant="subtitle2" gutterBottom>
                      URL:
                    </Typography>
                    <Typography variant="body2" paragraph fontFamily="monospace">
                      {vuln.url}
                    </Typography>

                    {vuln.parameter && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          Parameter:
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {vuln.parameter}
                        </Typography>
                      </>
                    )}

                    {vuln.evidence && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          Evidence:
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: '#f5f5f5', mb: 2 }}>
                          <Typography variant="body2" fontFamily="monospace" fontSize="0.85rem">
                            {vuln.evidence}
                          </Typography>
                        </Paper>
                      </>
                    )}

                    {vuln.remediation && (
                      <>
                        <Typography variant="subtitle2" gutterBottom>
                          Remediation:
                        </Typography>
                        <Alert severity="info" sx={{ mb: 2 }}>
                          {vuln.remediation}
                        </Alert>
                      </>
                    )}

                    {vuln.cwe_id && (
                      <Typography variant="body2" color="text.secondary">
                        {vuln.cwe_id}
                      </Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ScanResultsView;
