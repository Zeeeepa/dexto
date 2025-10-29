/**
 * Frontend configuration
 */

export const config = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
  apiEndpoints: {
    chatkit: '/chatkit',
    workflows: '/api/workflows',
    health: '/health',
  },
  voice: {
    language: 'en-US',
    continuous: false,
    interimResults: false,
  },
};

