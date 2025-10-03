# Frontend (Vite React) production image built entirely in Docker

# 1) Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# 2) Nginx serve stage
FROM nginx:alpine AS runner
# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy build artifacts
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
