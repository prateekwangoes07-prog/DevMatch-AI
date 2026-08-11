FROM node:20-alpine AS base
WORKDIR /app
COPY package.json ./
RUN npm install

# Development stage
FROM base AS development
ENV NODE_ENV=development
COPY . .
CMD ["npm", "run", "dev"]

# Build stage for production
FROM base AS builder
WORKDIR /app
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Production runner stage
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
