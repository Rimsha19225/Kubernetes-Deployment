# Quickstart Guide: Kubernetes Minikube Deployment for AI Todo App

## Prerequisites

- Docker installed and running
- Minikube installed (v1.20+)
- kubectl installed
- Helm installed (v3.0+)
- Git installed

## Setup Instructions

### 1. Start Minikube
```bash
minikube start --memory=4096 --cpus=2
```

### 2. Enable Required Addons
```bash
minikube addons enable ingress
minikube addons enable dashboard
```

### 3. Set Docker Environment to Minikube
```bash
eval $(minikube docker-env)
```

### 4. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 5. Build Docker Images
```bash
# Build frontend image
docker build -t todo-frontend:latest -f ./frontend/Dockerfile ./frontend

# Build backend image
docker build -t todo-backend:latest -f ./backend/Dockerfile ./backend
```

### 6. Create Kubernetes Secrets
```bash
kubectl create secret generic app-secrets \
  --from-literal=JWT_SECRET=<your-jwt-secret> \
  --from-literal=DATABASE_URL=<your-neon-db-url> \
  --from-literal=COHERE_API_KEY=<your-cohere-api-key>
```

### 7. Install Helm Chart
```bash
helm install todo-app ./helm/todo-chart
```

### 8. Access the Application
```bash
# Get the frontend service URL
minikube service todo-frontend-service --url
```

## Verification Steps

1. Check all pods are running:
   ```bash
   kubectl get pods
   ```

2. Verify services are available:
   ```bash
   kubectl get services
   ```

3. Check application logs:
   ```bash
   kubectl logs deployment/todo-frontend
   kubectl logs deployment/todo-backend
   ```

## Troubleshooting

### Common Issues
- **Images not found**: Ensure you ran `eval $(minikube docker-env)` before building
- **Service not accessible**: Check NodePort range and firewall settings
- **Secrets not mounted**: Verify secret names match values in Helm chart

### Useful Commands
- View Minikube dashboard: `minikube dashboard`
- Check cluster status: `kubectl cluster-info`
- View all resources: `kubectl get all`

## Cleanup
```bash
helm uninstall todo-app
kubectl delete secret app-secrets
minikube stop
```