import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(config => {
  console.log(`API: ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const episodesApi = {
  getAll: () => api.get('/episodes/'),
  getOne: (num) => api.get(`/episodes/${num}`),
  getNext: () => api.get('/episodes/next'),
  generate: (params = {}) => api.post('/episodes/generate', params),
  getPdfUrl: (num) => `/files/pdfs/episode_${String(num).padStart(3, '0')}/`,
};

export const assessmentsApi = {
  get: (episodeNum) => api.get(`/assessments/${episodeNum}`),
  getResults: (episodeNum) => api.get(`/assessments/${episodeNum}/results`),
  submit: (episodeNum, data) => api.post(`/assessments/${episodeNum}/submit`, data),
  getHistory: () => api.get('/assessments/history'),
};

export const sourcesApi = {
  getAll: () => api.get('/sources/'),
  add: (source) => api.post('/sources/', source),
  toggle: (id, enabled) => api.put(`/sources/${id}/toggle`, { enabled }),
  test: (id) => api.post(`/sources/${id}/test`),
  remove: (id) => api.delete(`/sources/${id}`),
};

export const analyticsApi = {
  getOverview: () => api.get('/analytics/overview'),
  getSnapshot: () => api.get('/analytics/snapshot'),
  getHistory: () => api.get('/analytics/history'),
  getKnowledgeGraph: () => api.get('/analytics/knowledge-graph'),
  getScoreHistory: () => api.get('/analytics/score-history'),
  getPublic: () => api.get('/analytics/public'),
};

export const pipelineApi = {
  getStatus: () => api.get('/pipeline/status'),
  run: (params = {}) => api.post('/pipeline/run', params),
  getConfig: () => api.get('/pipeline/config'),
};

export default api;
