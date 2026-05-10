FROM node:20-alpine AS builder

WORKDIR /app

COPY txguard-frontend/package*.json ./
RUN npm ci

COPY txguard-frontend/ ./
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./.next/standalone
COPY --from=builder /app/package.json ./

EXPOSE 3000

CMD ["node", ".next/server.js"]