import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const casesAPI = {
  getAll: () => apiClient.get('/cases'),
  getById: (id: string) => apiClient.get(`/cases/${id}`),
  updateNextSteps: (id: string, steps: string[]) => 
    apiClient.patch(`/cases/${id}/next-steps`, { steps }),
};

export const documentsAPI = {
  get: (id: string) => apiClient.get(`/documents/${id}`),
  getSummary: (id: string) => apiClient.get(`/documents/${id}/summary`),
};

export default apiClient;