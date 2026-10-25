import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  CompareArrows as CompareIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
} from '@mui/icons-material';

interface ScanResult {
  id: string;
  url: string;
  created_at: string;
  vulnerabilities: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
}

const CompareScans = () => {
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [scan1, setScan1] = useState('');
  const [scan2, setScan2] = useState('');
  const [comparison, setComparison] = useState<any>(null);

  useEffect(() => {
    // Fetch scans from API
    const fetchScans = async () => {
      try {
        await fetch('http://localhost:8000/api/scans/history');

        // Use mock data for demo
        const mockScans: ScanResult[] = [
          {
            id: '1',
            url: 'https://example.com',
            created_at: '2026-10-14T10:30:00',
            vulnerabilities: { critical: 3, high: 5, medium: 8, low: 12, info: 15 },
          },
          {
            id: '2',
            url: 'https://example.com',
            created_at: '2026-10-15T14:20:00',
            vulnerabilities: { critical: 2, high: 4, medium: 6, low: 10, info: 12 },
          },
          {
            id: '3',
            url: 'https://example.com',
            created_at: '2026-10-16T09:15:00',
            vulnerabilities: { critical: 1, high: 3, medium: 5, low: 8, info: 10 },
          },
          {
            id: '4',
            url: 'https://test.com',
            created_at: '2026-10-15T11:00:00',
            vulnerabilities: { critical: 5, high: 8, medium: 12, low: 18, info: 22 },
          },
          {
            id: '5',
            url: 'https://demo.com',
            created_at: '2026-10-16T08:45:00',
            vulnerabilities: { critical: 0, high: 2, medium: 4, low: 6, info: 8 },
          },
        ];

        setScans(mockScans);
      } catch (error) {
        // Use mock data on error
        setScans([
          {
            id: '1',
            url: 'https://example.com',
            created_at: '2026-10-14T10:30:00',
            vulnerabilities: { critical: 3, high: 5, medium: 8, low: 12, info: 15 },
          },
          {
            id: '2',
            url: 'https://example.com',
            created_at: '2026-10-15T14:20:00',
            vulnerabilities: { critical: 2, high: 4, medium: 6, low: 10, info: 12 },
          },
          {
            id: '3',
            url: 'https://example.com',
            created_at: '2026-10-16T09:15:00',
            vulnerabilities: { critical: 1, high: 3, medium: 5, low: 8, info: 10 },
          },
        ]);
      }
    };

    fetchScans();
  }, []);

  const handleCompare = () => {
    if (!scan1 || !scan2) return;

    const s1 = scans.find((s) => s.id === scan1);
    const s2 = scans.find((s) => s.id === scan2);

    if (!s1 || !s2) return;

    const calculateDiff = (before: number, after: number) => {
      const diff = after - before;
      const percent = before > 0 ? ((diff / before) * 100).toFixed(1) : '0';
      return {
        diff,
        percent,
        trend: diff < 0 ? 'down' : diff > 0 ? 'up' : 'flat',
      };
    };

    const diff = {
      critical: calculateDiff(s1.vulnerabilities.critical, s2.vulnerabilities.critical),
      high: calculateDiff(s1.vulnerabilities.high, s2.vulnerabilities.high),
      medium: calculateDiff(s1.vulnerabilities.medium, s2.vulnerabilities.medium),
      low: calculateDiff(s1.vulnerabilities.low, s2.vulnerabilities.low),
      info: calculateDiff(s1.vulnerabilities.info, s2.vulnerabilities.info),
    };

    const totalBefore =
      s1.vulnerabilities.critical +
      s1.vulnerabilities.high +
      s1.vulnerabilities.medium +
      s1.vulnerabilities.low +
      s1.vulnerabilities.info;

    const totalAfter =
      s2.vulnerabilities.critical +
      s2.vulnerabilities.high +
      s2.vulnerabilities.medium +
      s2.vulnerabilities.low +
      s2.vulnerabilities.info;

    setComparison({
      scan1: s1,
      scan2: s2,
      diff,
      totalBefore,
      totalAfter,
      totalDiff: calculateDiff(totalBefore, totalAfter),
      improvement: totalAfter < totalBefore,
    });
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'down') return <TrendingDownIcon color="success" />;
    if (trend === 'up') return <TrendingUpIcon color="error" />;
    return <TrendingFlatIcon color="disabled" />;
  };

  const getSeverityColor = (severity: string) => {
    const colors: any = {
      critical: 'error',
      high: 'warning',
      medium: 'warning',
      low: 'success',
      info: 'info',
    };
    return colors[severity] || 'default';
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Compare Scans
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Compare vulnerability scan results to track remediation progress
        </Typography>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={5}>
              <FormControl fullWidth>
                <InputLabel>First Scan (Before)</InputLabel>
                <Select
                  value={scan1}
                  label="First Scan (Before)"
                  onChange={(e) => setScan1(e.target.value)}
                >
                  {scans.map((scan) => (
                    <MenuItem key={scan.id} value={scan.id}>
                      {new Date(scan.created_at).toLocaleString()} - {scan.url}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2} sx={{ textAlign: 'center' }}>
              <CompareIcon color="primary" sx={{ fontSize: 40 }} />
            </Grid>
            <Grid item xs={12} md={5}>
              <FormControl fullWidth>
                <InputLabel>Second Scan (After)</InputLabel>
                <Select
                  value={scan2}
                  label="Second Scan (After)"
                  onChange={(e) => setScan2(e.target.value)}
                >
                  {scans.map((scan) => (
                    <MenuItem key={scan.id} value={scan.id}>
                      {new Date(scan.created_at).toLocaleString()} - {scan.url}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button
              variant="contained"
              startIcon={<CompareIcon />}
              onClick={handleCompare}
              disabled={!scan1 || !scan2}
              size="large"
            >
              Compare Scans
            </Button>
          </Box>
        </CardContent>
      </Card>

      {comparison && (
        <Box>
          {/* Summary Card */}
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Summary
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="textSecondary">
                      Before ( {new Date(comparison.scan1.created_at).toLocaleDateString()} )
                    </Typography>
                    <Typography variant="h3" color="error.main" sx={{ fontWeight: 600 }}>
                      {comparison.totalBefore}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Vulnerabilities
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="textSecondary">
                      After ( {new Date(comparison.scan2.created_at).toLocaleDateString()} )
                    </Typography>
                    <Typography variant="h3" color="success.main" sx={{ fontWeight: 600 }}>
                      {comparison.totalAfter}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Vulnerabilities
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                      {getTrendIcon(comparison.totalDiff.trend)}
                      <Typography
                        variant="body1"
                        color={comparison.totalDiff.trend === 'down' ? 'success.main' : 'error.main'}
                      >
                        {comparison.totalDiff.diff < 0 ? '' : '+'}
                        {comparison.totalDiff.diff} ({comparison.totalDiff.percent}%)
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h6" color="textSecondary">
                      Status
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      {comparison.improvement ? (
                        <Chip
                          icon={<TrendingDownIcon />}
                          label="Improved"
                          color="success"
                          sx={{ mt: 1 }}
                        />
                      ) : (
                        <Chip
                          icon={<TrendingUpIcon />}
                          label="Regressed"
                          color="error"
                          sx={{ mt: 1 }}
                        />
                      )}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Detailed Comparison */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Vulnerability Breakdown
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Severity</TableCell>
                      <TableCell align="center">Before</TableCell>
                      <TableCell align="center">After</TableCell>
                      <TableCell align="center">Difference</TableCell>
                      <TableCell align="center">Trend</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {['critical', 'high', 'medium', 'low', 'info'].map((severity) => {
                      const before = (comparison.scan1.vulnerabilities as any)[severity];
                      const after = (comparison.scan2.vulnerabilities as any)[severity];
                      const diff = comparison.diff[severity];

                      return (
                        <TableRow key={severity}>
                          <TableCell>
                            <Chip
                              label={severity.toUpperCase()}
                              color={getSeverityColor(severity)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Typography variant="h6">{before}</Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Typography variant="h6">{after}</Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Typography
                              variant="body1"
                              color={diff.diff < 0 ? 'success.main' : diff.diff > 0 ? 'error.main' : 'textSecondary'}
                            >
                              {diff.diff < 0 ? '' : '+'}
                              {diff.diff} ({diff.percent}%)
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            {getTrendIcon(diff.trend)}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          <Alert severity={comparison.improvement ? 'success' : 'warning'} sx={{ mt: 3 }}>
            {comparison.improvement
              ? `Great job! You've reduced vulnerabilities by ${Math.abs(comparison.totalDiff.percent)}% since the last scan.`
              : 'Vulnerability count has increased. Review the remediation recommendations and rescan after fixes.'}
          </Alert>
        </Box>
      )}
    </Box>
  );
};

export default CompareScans;