import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { scanService, Scan } from '../services/api';

interface ScanHistoryProps {
  onViewScan: (scanId: string) => void;
}

const ScanHistory: React.FC<ScanHistoryProps> = ({ onViewScan }) => {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = async () => {
    try {
      const data = await scanService.getScanHistory(1, 50);
      setScans(data.scans);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load scan history:', error);
      setLoading(false);
    }
  };

  const handleDownloadReport = (scanId: string) => {
    window.open(scanService.downloadReport(scanId), '_blank');
  };

  const handleDeleteScan = async (scanId: string) => {
    if (window.confirm('Are you sure you want to delete this scan?')) {
      try {
        await scanService.deleteScan(scanId);
        loadScans();
      } catch (error) {
        console.error('Failed to delete scan:', error);
      }
    }
  };

  const getSeverityColor = (severity: number, type: string) => {
    if (severity === 0) return 'default';
    if (type === 'critical') return 'error';
    if (type === 'high') return 'warning';
    if (type === 'medium') return 'info';
    return 'success';
  };

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

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Scan History
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Scan ID</TableCell>
                <TableCell>Target URL</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Critical</TableCell>
                <TableCell align="center">High</TableCell>
                <TableCell align="center">Medium</TableCell>
                <TableCell align="center">Low</TableCell>
                <TableCell align="center">Total</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {scans.map((scan) => (
                <TableRow key={scan.scan_id} hover>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {scan.scan_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {scan.target_url}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={scan.status}
                      color={getStatusColor(scan.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={scan.critical_count}
                      color={getSeverityColor(scan.critical_count, 'critical') as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={scan.high_count}
                      color={getSeverityColor(scan.high_count, 'high') as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={scan.medium_count}
                      color={getSeverityColor(scan.medium_count, 'medium') as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={scan.low_count}
                      color={getSeverityColor(scan.low_count, 'low') as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" fontWeight="bold">
                      {scan.total_vulnerabilities}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(scan.created_at).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => onViewScan(scan.scan_id)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      {scan.status === 'completed' && (
                        <Tooltip title="Download Report">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => handleDownloadReport(scan.scan_id)}
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Delete Scan">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteScan(scan.scan_id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {scans.length === 0 && !loading && (
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary">
              No scans found. Start a new scan to see results here.
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ScanHistory;
