import { useState, useCallback } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Avatar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Badge,
  Tooltip,
  useMediaQuery,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Add as AddIcon,
  History as HistoryIcon,
  Dashboard as DashboardIcon,
  Notifications as NotificationsIcon,
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CompareArrows as CompareIcon,
} from '@mui/icons-material';
import NewScan from './components/NewScan';
import ScanProgress from './components/ScanProgress';
import ScanHistory from './components/ScanHistory';
import ScanResultsView from './components/ScanResultsView';
import Dashboard from './components/Dashboard';
import ScheduledScans from './components/ScheduledScans';
import CompareScans from './components/CompareScans';
import Analytics from './components/Analytics';

type View = 'dashboard' | 'new' | 'progress' | 'history' | 'results' | 'scheduled' | 'compare' | 'analytics';

function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [activeScanId, setActiveScanId] = useState<string>('');
  const [darkMode, setDarkMode] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(3);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const isMobile = useMediaQuery('(max-width:600px)');

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: darkMode ? '#3f51b5' : '#1a237e',
        light: '#534bae',
        dark: '#000051',
      },
      secondary: {
        main: darkMode ? '#f50057' : '#283593',
      },
      background: {
        default: darkMode ? '#121212' : '#f5f5f5',
        paper: darkMode ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 8,
            padding: '8px 16px',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: darkMode
              ? '0 4px 6px rgba(0, 0, 0, 0.3)'
              : '0 4px 6px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
  });

  const handleScanCreated = (scanId: string) => {
    setActiveScanId(scanId);
    setCurrentView('progress');
  };

  const handleScanComplete = useCallback(() => {
    setNotificationCount(prev => prev + 1);
  }, []);

  const handleViewScan = (scanId: string) => {
    setActiveScanId(scanId);
    setCurrentView('results');
  };

  const handleBackToHistory = () => {
    setCurrentView('history');
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleNotificationClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setAnchorEl(null);
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon />, view: 'dashboard' as View },
    { id: 'new', label: 'New Scan', icon: <AddIcon />, view: 'new' as View },
    { id: 'history', label: 'Scan History', icon: <HistoryIcon />, view: 'history' as View },
    { id: 'scheduled', label: 'Scheduled Scans', icon: <ScheduleIcon />, view: 'scheduled' as View },
    { id: 'compare', label: 'Compare Scans', icon: <CompareIcon />, view: 'compare' as View },
    { id: 'analytics', label: 'Analytics', icon: <TrendingUpIcon />, view: 'analytics' as View },
  ];

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <SecurityIcon color="primary" fontSize="large" />
        <Typography variant="h6" color="primary">
          VulnScanner
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={currentView === item.view}
              onClick={() => {
                setCurrentView(item.view);
                setDrawerOpen(false);
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static" elevation={0}>
          <Toolbar>
            {isMobile && (
              <IconButton
                color="inherit"
                edge="start"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}

            <SecurityIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              VulnScanner Pro
              <Chip
                label="v2.0"
                size="small"
                sx={{ ml: 1, bgcolor: 'rgba(255,255,255,0.2)' }}
              />
            </Typography>

            {!isMobile && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  color="inherit"
                  startIcon={<DashboardIcon />}
                  onClick={() => setCurrentView('dashboard')}
                  variant={currentView === 'dashboard' ? 'outlined' : 'text'}
                >
                  Dashboard
                </Button>
                <Button
                  color="inherit"
                  startIcon={<AddIcon />}
                  onClick={() => setCurrentView('new')}
                  variant={currentView === 'new' ? 'outlined' : 'text'}
                >
                  New Scan
                </Button>
                <Button
                  color="inherit"
                  startIcon={<HistoryIcon />}
                  onClick={() => setCurrentView('history')}
                  variant={currentView === 'history' ? 'outlined' : 'text'}
                >
                  History
                </Button>
                <Button
                  color="inherit"
                  startIcon={<TrendingUpIcon />}
                  onClick={() => setCurrentView('analytics')}
                  variant={currentView === 'analytics' ? 'outlined' : 'text'}
                >
                  Analytics
                </Button>
              </Box>
            )}

            <Tooltip title="Toggle dark mode">
              <IconButton color="inherit" onClick={toggleDarkMode} sx={{ ml: 1 }}>
                {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>

            <Tooltip title="Notifications">
              <IconButton color="inherit" onClick={handleNotificationClick}>
                <Badge badgeContent={notificationCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>

            <Avatar sx={{ ml: 2, bgcolor: 'secondary.main' }}>U</Avatar>
          </Toolbar>
        </AppBar>

        {/* Notifications Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleNotificationClose}
          PaperProps={{
            sx: { width: 320, maxHeight: 400 }
          }}
        >
          <Box sx={{ p: 2, pb: 1 }}>
            <Typography variant="h6">Notifications</Typography>
          </Box>
          <Divider />
          <MenuItem onClick={handleNotificationClose}>
            <ListItemText
              primary="Scan completed successfully"
              secondary="2 minutes ago"
              primaryTypographyProps={{ fontWeight: 500 }}
            />
          </MenuItem>
          <MenuItem onClick={handleNotificationClose}>
            <ListItemText
              primary="3 critical vulnerabilities found"
              secondary="5 minutes ago"
            />
          </MenuItem>
          <MenuItem onClick={handleNotificationClose}>
            <ListItemText
              primary="Scheduled scan started"
              secondary="10 minutes ago"
            />
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleNotificationClose}>
            <Typography variant="body2" color="primary" sx={{ width: '100%', textAlign: 'center' }}>
              View all notifications
            </Typography>
          </MenuItem>
        </Menu>

        {/* Mobile Drawer */}
        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        >
          {drawer}
        </Drawer>

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default', py: 3 }}>
          <Container maxWidth="xl">
            {currentView === 'dashboard' && <Dashboard onNewScan={() => setCurrentView('new')} />}
            {currentView === 'new' && <NewScan onScanCreated={handleScanCreated} />}
            {currentView === 'progress' && activeScanId && (
              <ScanProgress scanId={activeScanId} onComplete={handleScanComplete} />
            )}
            {currentView === 'history' && <ScanHistory onViewScan={handleViewScan} />}
            {currentView === 'results' && activeScanId && (
              <ScanResultsView scanId={activeScanId} onBack={handleBackToHistory} />
            )}
            {currentView === 'scheduled' && <ScheduledScans />}
            {currentView === 'compare' && <CompareScans />}
            {currentView === 'analytics' && <Analytics />}
          </Container>
        </Box>

        {/* Footer */}
        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            backgroundColor: theme.palette.primary.main,
            color: 'white',
          }}
        >
          <Container maxWidth="lg">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="body2">
                  VulnScanner Pro © 2026 - Advanced Security Testing Platform
                </Typography>
                <Typography variant="caption" display="block">
                  17 Advanced Scanners • Real-time Monitoring • ML-Powered Detection
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button color="inherit" size="small">Documentation</Button>
                <Button color="inherit" size="small">API</Button>
                <Button color="inherit" size="small">Support</Button>
              </Box>
            </Box>
            <Divider sx={{ my: 2, bgcolor: 'rgba(255,255,255,0.2)' }} />
            <Typography variant="caption" align="center" display="block" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              ⚠️ For authorized security testing only. Always obtain proper authorization before scanning.
            </Typography>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
