import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export interface ScanCreateRequest {
  target_url: string;
  scan_depth?: number;
  enable_zap?: boolean;
  scan_types?: string[];
}

export interface Scan {
  scan_id: string;
  target_url: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress: number;
  total_vulnerabilities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  info_count: number;
  error_message?: string;
}

export interface Vulnerability {
  name: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  cvss_score?: number;
  url: string;
  parameter?: string;
  method?: string;
  evidence?: string;
  payload?: string;
  remediation?: string;
  references?: string[];
  cwe_id?: string;
  cve_id?: string;
}

export interface ScanResults {
  scan_id: string;
  target_url: string;
  status: string;
  vulnerabilities: Vulnerability[];
  summary: {
    total_vulnerabilities: number;
    critical_count: number;
    high_count: number;
    medium_count: number;
    low_count: number;
    info_count: number;
    scan_duration: string;
  };
  completed_at?: string;
}

// API methods
export const scanService = {
  createScan: async (data: ScanCreateRequest): Promise<Scan> => {
    const response = await apiClient.post('/api/scans/create', data);
    return response.data;
  },

  getScanStatus: async (scanId: string): Promise<Scan> => {
    const response = await apiClient.get(`/api/scans/${scanId}`);
    return response.data;
  },

  getScanResults: async (scanId: string): Promise<ScanResults> => {
    const response = await apiClient.get(`/api/scans/${scanId}/results`);
    return response.data;
  },

  getScanHistory: async (page: number = 1, pageSize: number = 20) => {
    const response = await apiClient.get('/api/scans/history', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  deleteScan: async (scanId: string): Promise<void> => {
    await apiClient.delete(`/api/scans/${scanId}`);
  },

  downloadReport: (scanId: string): string => {
    return `${API_BASE_URL}/api/reports/${scanId}/download`;
  },
};

export default apiClient;
