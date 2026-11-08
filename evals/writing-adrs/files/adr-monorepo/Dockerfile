FROM node:24-bookworm
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build --workspaces --if-present
CMD ["node", "services/gateway/dist/index.js"]
