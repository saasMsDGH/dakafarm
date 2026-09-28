import axios from 'axios';
import { isSwahiliActive, translateToSwahili } from '../utils/swalI18n';

// Create a configured axios instance
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', // Dynamic URL from .env
  headers: {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  }
});

// Intercept requests to add the Authorization token automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept responses to handle 401 Unauthorized globally and translate backend error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If language is Swahili, translate detail error messages from FastAPI
    if (isSwahiliActive() && error.response && error.response.data) {
      const detail = error.response.data.detail;
      if (typeof detail === 'string') {
        error.response.data.detail = translateToSwahili(detail);
      } else if (Array.isArray(detail)) {
        error.response.data.detail = detail.map((item) => {
          if (item && item.msg) {
            return { ...item, msg: translateToSwahili(item.msg) };
          }
          return item;
        });
      }
    }

    if (error.response && error.response.status === 401) {
      // Token is invalid or expired
      localStorage.removeItem('access_token');
      // Dispatch an event so the AuthContext knows to log the user out
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);
