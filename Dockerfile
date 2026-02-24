# Stage 1: Build frontend
FROM node:20-alpine AS build-frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Production
FROM python:3.11-slim

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY --from=build-frontend /app/dist ./static

RUN mkdir -p /app/data && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
