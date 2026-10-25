import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { scanService, Scan } from '../services/api';

interface ScanProgressProps {
  scanId: string;
  onComplete: () => void;
}

const ScanProgress: React.FC<ScanProgressProps> = ({ scanId, onComplete }) => {
  const [scan, setScan] = useState<Scan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const fetchScanStatus = async () => {
      try {
        const data = await scanService.getScanStatus(scanId);
        setScan(data);
        setLoading(false);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(intervalId);
          onComplete();
        }
      } catch (err: any) {
        setError('Failed to fetch scan status');
        setLoading(false);
        clearInterval(intervalId);
      }
    };

    fetchScanStatus();
    intervalId = setInterval(fetchScanStatus, 2000); // Poll every 2 seconds

    return () => clearInterval(intervalId);
  }, [scanId, onComplete]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
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
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!scan) return null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Scan Progress</Typography>
          <Chip
            label={scan.status.toUpperCase()}
            color={getStatusColor(scan.status) as any}
            sx={{ fontWeight: 'bold' }}
          />
        </Box>

        <Box mb={4}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Target: {scan.target_url}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Scan ID: {scan.scan_id}
          </Typography>
        </Box>

        {scan.status === 'running' && (
          <Box mb={4}>
            <Typography variant="body1" gutterBottom>
              Progress: {scan.progress}%
            </Typography>
            <LinearProgress variant="determinate" value={scan.progress} sx={{ height: 10, borderRadius: 5 }} />
          </Box>
        )}

        {scan.error_message && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {scan.error_message}
          </Alert>
        )}

        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Vulnerability Summary
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#ffebee' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" color="error">
                      {scan.critical_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Critical
                    </Typography>
                  </Box>
                  <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#fff3e0' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" color="warning.main">
                      {scan.high_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High
                    </Typography>
                  </Box>
                  <WarningIcon sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#fff9c4' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" color="orange">
                      {scan.medium_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Medium
                    </Typography>
                  </Box>
                  <WarningIcon sx={{ fontSize: 40, color: 'orange' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#e8f5e9' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" color="success.main">
                      {scan.low_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Low
                    </Typography>
                  </Box>
                  <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#e3f2fd' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" color="info.main">
                      {scan.info_count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Info
                    </Typography>
                  </Box>
                  <InfoIcon sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ bgcolor: '#f5f5f5' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4">
                      {scan.total_vulnerabilities}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total
                    </Typography>
                  </Box>
                  <SecurityIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ScanProgress;
