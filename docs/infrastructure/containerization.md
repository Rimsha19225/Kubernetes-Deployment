# Docker Build Process Documentation

## Frontend Container Build

To build the frontend container:

```bash
cd frontend/
docker build -t todo-frontend:latest .
```

## Backend Container Build

To build the backend container:

```bash
cd backend/
docker build -t todo-backend:latest .
```

## Build Optimizations

### Multi-stage Build (Future Enhancement)
Consider implementing a multi-stage build for smaller image sizes:

Frontend:
```Dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

Backend:
```Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.local /root/.local
COPY . .
EXPOSE 8000
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Verification Steps

1. Verify images are built:
   ```bash
   docker images | grep todo-
   ```

2. Test run frontend:
   ```bash
   docker run -p 3000:3000 todo-frontend:latest
   ```

3. Test run backend:
   ```bash
   docker run -p 8000:8000 todo-backend:latest
   ```