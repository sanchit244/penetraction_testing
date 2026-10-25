import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');

  const vulnerabilityTrends = [
    { date: 'Oct 10', critical: 2, high: 5, medium: 8, low: 12, info: 15 },
    { date: 'Oct 11', critical: 3, high: 7, medium: 10, low: 14, info: 18 },
    { date: 'Oct 12', critical: 1, high: 4, medium: 6, low: 10, info: 12 },
    { date: 'Oct 13', critical: 4, high: 8, medium: 12, low: 16, info: 20 },
    { date: 'Oct 14', critical: 2, high: 6, medium: 9, low: 13, info: 16 },
    { date: 'Oct 15', critical: 3, high: 7, medium: 11, low: 15, info: 19 },
    { date: 'Oct 16', critical: 2, high: 5, medium: 8, low: 11, info: 14 },
  ];

  const scannerPerformance = [
    { scanner: 'SQL Injection', findings: 45, accuracy: 92 },
    { scanner: 'XSS', findings: 38, accuracy: 88 },
    { scanner: 'CSRF', findings: 28, accuracy: 95 },
    { scanner: 'API Security', findings: 52, accuracy: 90 },
    { scanner: 'Authentication', findings: 34, accuracy: 87 },
    { scanner: 'Business Logic', findings: 29, accuracy: 85 },
  ];

  const radarData = [
    { category: 'Injection', value: 85, fullMark: 100 },
    { category: 'Auth', value: 72, fullMark: 100 },
    { category: 'XSS', value: 90, fullMark: 100 },
    { category: 'Config', value: 65, fullMark: 100 },
    { category: 'API', value: 78, fullMark: 100 },
    { category: 'Logic', value: 70, fullMark: 100 },
  ];

  const topVulnerabilities = [
    { name: 'SQL Injection', count: 45, severity: 'critical' },
    { name: 'XSS (Reflected)', count: 38, severity: 'high' },
    { name: 'Missing Authentication', count: 34, severity: 'critical' },
    { name: 'CSRF Token Missing', count: 28, severity: 'medium' },
    { name: 'Weak Password Policy', count: 25, severity: 'high' },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Security Analytics
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Advanced insights and trends across all security scans
          </Typography>
        </Box>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="24h">Last 24 Hours</MenuItem>
            <MenuItem value="7d">Last 7 Days</MenuItem>
            <MenuItem value="30d">Last 30 Days</MenuItem>
            <MenuItem value="90d">Last 90 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* Vulnerability Trends Over Time */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Vulnerability Trends Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={vulnerabilityTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="critical" stackId="1" stroke="#d32f2f" fill="#d32f2f" />
                  <Area type="monotone" dataKey="high" stackId="1" stroke="#f57c00" fill="#f57c00" />
                  <Area type="monotone" dataKey="medium" stackId="1" stroke="#fbc02d" fill="#fbc02d" />
                  <Area type="monotone" dataKey="low" stackId="1" stroke="#388e3c" fill="#388e3c" />
                  <Area type="monotone" dataKey="info" stackId="1" stroke="#1976d2" fill="#1976d2" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Scanner Performance */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Scanner Performance
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={scannerPerformance} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="scanner" type="category" width={120} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="findings" fill="#1976d2" name="Findings" />
                  <Bar dataKey="accuracy" fill="#388e3c" name="Accuracy %" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Coverage Radar */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Security Coverage
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="category" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar name="Coverage" dataKey="value" stroke="#1976d2" fill="#1976d2" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Vulnerabilities */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Top Vulnerabilities
              </Typography>
              <Box>
                {topVulnerabilities.map((vuln, index) => (
                  <Paper
                    key={index}
                    sx={{
                      p: 2,
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                      <Typography variant="h6" color="primary" sx={{ width: 30 }}>
                        #{index + 1}
                      </Typography>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {vuln.name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <Chip
                            label={vuln.severity.toUpperCase()}
                            color={
                              vuln.severity === 'critical' ? 'error' :
                              vuln.severity === 'high' ? 'warning' : 'default'
                            }
                            size="small"
                          />
                          <Typography variant="caption" color="textSecondary">
                            Found in {vuln.count} scans
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                    <Box sx={{ width: 200 }}>
                      <Typography variant="caption" color="textSecondary">
                        Occurrence Rate
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(vuln.count / 50) * 100}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </Paper>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Key Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Mean Time to Detect (MTTD)
              </Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 600 }}>
                2.3 min
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Average time to identify vulnerabilities
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                False Positive Rate
              </Typography>
              <Typography variant="h3" color="success.main" sx={{ fontWeight: 600 }}>
                8.2%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                ML-powered accuracy improvement
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Scan Efficiency
              </Typography>
              <Typography variant="h3" color="info.main" sx={{ fontWeight: 600 }}>
                92%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Resource utilization score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
