import Constants from 'expo-constants';

const extra = Constants.expoConfig?.extra || {};

export const CONFIG = {
  apiBaseUrl: extra.API_BASE_URL || 'http://localhost:8000',
  aiProvider: (extra.AI_PROVIDER as 'openai' | 'gemini') || 'openai',
  openAIApiKey: extra.OPENAI_API_KEY || '',
  googleApiKey: extra.GOOGLE_API_KEY || ''
};
