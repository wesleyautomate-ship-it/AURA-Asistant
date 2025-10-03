# PropertyPro Mobile (React Native + Expo)

Mobile client for PropertyPro AI.

## Quick Start

- Prerequisites: Node 18+, npm or yarn, Expo CLI (`npm i -g expo-cli` optional).
- From the `mobile/` directory:

```bash
npm install
npm run start
```

Use `i`, `a`, or `w` in the Expo terminal to launch iOS, Android, or Web respectively.

## Configuration

We keep configuration in `app.json > expo.extra` and read it via `expo-constants`:

- `API_BASE_URL`: Defaults to `http://localhost:8000` (backend API)
- `AI_PROVIDER`: `openai` or `gemini`
- `OPENAI_API_KEY`, `GOOGLE_API_KEY`: If you plan to call providers directly from device (not recommended for production). Prefer backend proxy.

## Screens

- `Dashboard` (entry)
- `Properties`
- `Clients`
- `Content`
- `Tasks`
- `Chat`
- `Analytics`

## AI Provider Abstraction

See `src/services/ai/` for a simple provider abstraction that can target `openai` or `gemini`. By default it calls the backend endpoint and passes the provider name; the backend should route to the selected model securely.

## Notes

- For production, never embed API keys in the app. Use the backend as a proxy.
- The current build targets Expo SDK ~51 and React Native 0.74.
