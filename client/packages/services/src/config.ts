import Constants from 'expo-constants';

const extra = Constants.expoConfig?.extra || {};

// In development, use Vite proxy path to avoid CORS
// In production, use full API_BASE_URL from environment
const getApiBaseUrl = () => {
  // Always use localhost:8000 for development
  return 'http://localhost:8000';
};

export const CONFIG = {
  apiBaseUrl: getApiBaseUrl(),
  aiProvider: (extra.AI_PROVIDER as 'openai' | 'gemini') || 'openai',
  openAIApiKey: extra.OPENAI_API_KEY || '',
  googleApiKey: extra.GOOGLE_API_KEY || ''
};
