import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Grid,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';

interface ScheduledScan {
  id: string;
  name: string;
  url: string;
  scanTypes: string[];
  schedule: string;
  nextRun: string;
  enabled: boolean;
  lastRun?: string;
}

const ScheduledScans = () => {
  const [scans, setScans] = useState<ScheduledScan[]>([
    {
      id: '1',
      name: 'Daily Security Check',
      url: 'https://example.com',
      scanTypes: ['sql_injection', 'xss', 'headers'],
      schedule: '0 2 * * *',
      nextRun: '2026-10-17 02:00:00',
      enabled: true,
      lastRun: '2026-10-16 02:00:00',
    },
    {
      id: '2',
      name: 'Weekly Full Audit',
      url: 'https://example.com',
      scanTypes: ['all'],
      schedule: '0 3 * * 0',
      nextRun: '2026-10-19 03:00:00',
      enabled: true,
      lastRun: '2026-10-12 03:00:00',
    },
    {
      id: '3',
      name: 'API Security Scan',
      url: 'https://api.example.com',
      scanTypes: ['api_security', 'authentication'],
      schedule: '*/30 * * * *',
      nextRun: '2026-10-16 12:00:00',
      enabled: false,
    },
  ]);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingScan, setEditingScan] = useState<ScheduledScan | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    scanTypes: [] as string[],
    schedule: '',
    enabled: true,
  });

  const allScanTypes = [
    { id: 'sql_injection', name: 'SQL Injection' },
    { id: 'xss', name: 'XSS' },
    { id: 'csrf', name: 'CSRF' },
    { id: 'headers', name: 'Security Headers' },
    { id: 'ssl', name: 'SSL/TLS' },
    { id: 'api_security', name: 'API Security' },
    { id: 'business_logic', name: 'Business Logic' },
    { id: 'authentication', name: 'Authentication' },
    { id: 'advanced_injection', name: 'Advanced Injection' },
    { id: 'client_side', name: 'Client Side' },
    { id: 'cloud_infrastructure', name: 'Cloud Infrastructure' },
  ];

  const schedulePresets = [
    { label: 'Every 15 minutes', value: '*/15 * * * *' },
    { label: 'Every 30 minutes', value: '*/30 * * * *' },
    { label: 'Every hour', value: '0 * * * *' },
    { label: 'Daily at 2 AM', value: '0 2 * * *' },
    { label: 'Weekly (Sunday 3 AM)', value: '0 3 * * 0' },
    { label: 'Monthly (1st day 4 AM)', value: '0 4 1 * *' },
  ];

  const handleCreate = () => {
    setEditingScan(null);
    setFormData({
      name: '',
      url: '',
      scanTypes: [],
      schedule: '',
      enabled: true,
    });
    setDialogOpen(true);
  };

  const handleEdit = (scan: ScheduledScan) => {
    setEditingScan(scan);
    setFormData({
      name: scan.name,
      url: scan.url,
      scanTypes: scan.scanTypes,
      schedule: scan.schedule,
      enabled: scan.enabled,
    });
    setDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    setScans(scans.filter((s) => s.id !== id));
  };

  const handleToggle = (id: string) => {
    setScans(
      scans.map((s) =>
        s.id === id ? { ...s, enabled: !s.enabled } : s
      )
    );
  };

  const handleSave = () => {
    if (editingScan) {
      setScans(
        scans.map((s) =>
          s.id === editingScan.id
            ? {
                ...s,
                ...formData,
                nextRun: calculateNextRun(formData.schedule),
              }
            : s
        )
      );
    } else {
      setScans([
        ...scans,
        {
          id: Date.now().toString(),
          ...formData,
          nextRun: calculateNextRun(formData.schedule),
        },
      ]);
    }
    setDialogOpen(false);
  };

  const calculateNextRun = (_cron: string): string => {
    // Simplified next run calculation
    const now = new Date();
    now.setHours(now.getHours() + 24);
    return now.toISOString().slice(0, 19).replace('T', ' ');
  };

  const handleRunNow = (id: string) => {
    console.log('Run scan now:', id);
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            Scheduled Scans
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Configure automated security scans on a schedule
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Create Schedule
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        Scheduled scans run automatically based on your configured cron expression. All scans are executed asynchronously.
      </Alert>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Target URL</TableCell>
                  <TableCell>Schedule</TableCell>
                  <TableCell>Next Run</TableCell>
                  <TableCell>Last Run</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scans.map((scan) => (
                  <TableRow key={scan.id}>
                    <TableCell>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {scan.name}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
                        {scan.scanTypes.slice(0, 2).map((type) => (
                          <Chip
                            key={type}
                            label={type}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                        {scan.scanTypes.length > 2 && (
                          <Chip label={`+${scan.scanTypes.length - 2}`} size="small" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {scan.url}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {scan.schedule}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(scan.nextRun).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {scan.lastRun
                          ? new Date(scan.lastRun).toLocaleString()
                          : 'Never'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={scan.enabled ? 'Active' : 'Paused'}
                        color={scan.enabled ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleRunNow(scan.id)}
                          color="primary"
                        >
                          <PlayIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleToggle(scan.id)}
                          color={scan.enabled ? 'warning' : 'success'}
                        >
                          {scan.enabled ? <PauseIcon /> : <PlayIcon />}
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleEdit(scan)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(scan.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingScan ? 'Edit Scheduled Scan' : 'Create New Scheduled Scan'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Scan Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target URL"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  placeholder="https://example.com"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Schedule Preset</InputLabel>
                  <Select
                    value={formData.schedule}
                    label="Schedule Preset"
                    onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                  >
                    {schedulePresets.map((preset) => (
                      <MenuItem key={preset.value} value={preset.value}>
                        {preset.label} ({preset.value})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Custom Cron Expression"
                  value={formData.schedule}
                  onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                  placeholder="* * * * *"
                  helperText="Format: minute hour day month day-of-week"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Scan Types
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {allScanTypes.map((type) => (
                    <Chip
                      key={type.id}
                      label={type.name}
                      onClick={() => {
                        if (formData.scanTypes.includes(type.id)) {
                          setFormData({
                            ...formData,
                            scanTypes: formData.scanTypes.filter((t) => t !== type.id),
                          });
                        } else {
                          setFormData({
                            ...formData,
                            scanTypes: [...formData.scanTypes, type.id],
                          });
                        }
                      }}
                      color={formData.scanTypes.includes(type.id) ? 'primary' : 'default'}
                      variant={formData.scanTypes.includes(type.id) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enabled}
                      onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    />
                  }
                  label="Enable scheduled scan"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>
            {editingScan ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScheduledScans;