import { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
  Chip,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';

interface DashboardProps {
  onNewScan: () => void;
}

interface DashboardStats {
  totalScans: number;
  activeScans: number;
  criticalVulns: number;
  highVulns: number;
  mediumVulns: number;
  lowVulns: number;
  infoVulns: number;
  recentScans: RecentScan[];
  scanTrends: TrendData[];
  vulnerabilityDistribution: VulnDistribution[];
}

interface RecentScan {
  id: string;
  url: string;
  status: string;
  vulnerabilities: number;
  created_at: string;
}

interface TrendData {
  date: string;
  scans: number;
  vulnerabilities: number;
}

interface VulnDistribution {
  name: string;
  value: number;
  color: string;
}

const Dashboard = ({ onNewScan }: DashboardProps) => {
  const [stats, setStats] = useState<DashboardStats>({
    totalScans: 0,
    activeScans: 0,
    criticalVulns: 0,
    highVulns: 0,
    mediumVulns: 0,
    lowVulns: 0,
    infoVulns: 0,
    recentScans: [],
    scanTrends: [],
    vulnerabilityDistribution: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/analytics/dashboard');
      const data = await response.json();

      // Transform data for charts
      const vulnDist = [
        { name: 'Critical', value: data.criticalVulns || 0, color: '#d32f2f' },
        { name: 'High', value: data.highVulns || 0, color: '#f57c00' },
        { name: 'Medium', value: data.mediumVulns || 0, color: '#fbc02d' },
        { name: 'Low', value: data.lowVulns || 0, color: '#388e3c' },
        { name: 'Info', value: data.infoVulns || 0, color: '#1976d2' },
      ];

      setStats({
        totalScans: data.totalScans || 0,
        activeScans: data.activeScans || 0,
        criticalVulns: data.criticalVulns || 0,
        highVulns: data.highVulns || 0,
        mediumVulns: data.mediumVulns || 0,
        lowVulns: data.lowVulns || 0,
        infoVulns: data.infoVulns || 0,
        recentScans: data.recentScans || [],
        scanTrends: data.scanTrends || [],
        vulnerabilityDistribution: vulnDist,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data for demo
      setStats({
        totalScans: 45,
        activeScans: 2,
        criticalVulns: 12,
        highVulns: 28,
        mediumVulns: 54,
        lowVulns: 89,
        infoVulns: 123,
        recentScans: [
          { id: '1', url: 'https://example.com', status: 'completed', vulnerabilities: 15, created_at: '2026-10-16T10:30:00' },
          { id: '2', url: 'https://test.com', status: 'running', vulnerabilities: 0, created_at: '2026-10-16T11:00:00' },
          { id: '3', url: 'https://demo.com', status: 'completed', vulnerabilities: 8, created_at: '2026-10-16T09:15:00' },
        ],
        scanTrends: [
          { date: 'Oct 10', scans: 8, vulnerabilities: 45 },
          { date: 'Oct 11', scans: 12, vulnerabilities: 67 },
          { date: 'Oct 12', scans: 6, vulnerabilities: 32 },
          { date: 'Oct 13', scans: 15, vulnerabilities: 89 },
          { date: 'Oct 14', scans: 10, vulnerabilities: 54 },
          { date: 'Oct 15', scans: 14, vulnerabilities: 76 },
          { date: 'Oct 16', scans: 9, vulnerabilities: 43 },
        ],
        vulnerabilityDistribution: [
          { name: 'Critical', value: 12, color: '#d32f2f' },
          { name: 'High', value: 28, color: '#f57c00' },
          { name: 'Medium', value: 54, color: '#fbc02d' },
          { name: 'Low', value: 89, color: '#388e3c' },
          { name: 'Info', value: 123, color: '#1976d2' },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }: any) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography color="textSecondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              bgcolor: color + '20',
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const getStatusChip = (status: string) => {
    const statusConfig: any = {
      completed: { label: 'Completed', color: 'success' },
      running: { label: 'Running', color: 'info' },
      pending: { label: 'Pending', color: 'warning' },
      failed: { label: 'Failed', color: 'error' },
    };

    const config = statusConfig[status] || { label: status, color: 'default' };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  if (loading || !stats) {
    return (
      <Box sx={{ width: '100%', mt: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 2 }}>
        <CircularProgress />
        <Typography color="textSecondary">Loading dashboard metrics...</Typography>
      </Box>
    );
  }

  const vulnDist = stats.vulnerabilityDistribution || [];
  const scanTrends = stats.scanTrends || [];
  const recentScans = stats.recentScans || [];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Security Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Overview of your vulnerability scans and security posture
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh data">
            <IconButton onClick={fetchDashboardData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={onNewScan}
            size="large"
          >
            Start New Scan
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Scans"
            value={stats.totalScans}
            subtitle="All time"
            icon={<SecurityIcon sx={{ fontSize: 32, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Scans"
            value={stats.activeScans}
            subtitle="Currently running"
            icon={<ScheduleIcon sx={{ fontSize: 32, color: '#f57c00' }} />}
            color="#f57c00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Issues"
            value={stats.criticalVulns}
            subtitle="Requires immediate action"
            icon={<WarningIcon sx={{ fontSize: 32, color: '#d32f2f' }} />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Vulnerabilities"
            value={stats.criticalVulns + stats.highVulns + stats.mediumVulns + stats.lowVulns + stats.infoVulns}
            subtitle="Across all scans"
            icon={<TrendingUpIcon sx={{ fontSize: 32, color: '#388e3c' }} />}
            color="#388e3c"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Vulnerability Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Vulnerability Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={vulnDist}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {vulnDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Scan Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Scan Trends (Last 7 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={scanTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="scans" stroke="#1976d2" strokeWidth={2} name="Scans" />
                  <Line type="monotone" dataKey="vulnerabilities" stroke="#d32f2f" strokeWidth={2} name="Vulnerabilities" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Vulnerability Severity Breakdown */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Severity Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={vulnDist}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                    {vulnDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Scans */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Recent Scans
          </Typography>
          <Box>
            {recentScans.map((scan) => (
              <Paper
                key={scan.id}
                sx={{
                  p: 2,
                  mb: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  '&:hover': { bgcolor: 'action.hover' },
                  cursor: 'pointer',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                  <SecurityIcon color="primary" />
                  <Box>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {scan.url}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {new Date(scan.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {getStatusChip(scan.status)}
                  <Chip
                    label={`${scan.vulnerabilities} vulnerabilities`}
                    color={scan.vulnerabilities > 10 ? 'error' : scan.vulnerabilities > 5 ? 'warning' : 'success'}
                    size="small"
                  />
                </Box>
              </Paper>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
