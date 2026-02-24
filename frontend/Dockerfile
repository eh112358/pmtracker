# Build stage
FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage - nginx unprivileged
FROM nginxinc/nginx-unprivileged:alpine

# Copy built files (Vite outputs to dist/)
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config (configured for non-root)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
