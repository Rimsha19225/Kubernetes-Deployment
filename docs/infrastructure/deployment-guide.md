# Minikube Deployment Guide

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

### 4. Build Docker Images
```bash
# Build frontend image
docker build -t todo-frontend:latest -f ./frontend/Dockerfile ./frontend

# Build backend image
docker build -t todo-backend:latest -f ./backend/Dockerfile ./backend
```

### 5. Prepare Secret Values

Create a file called `secrets.yaml` with your encoded secrets:

```yaml
secrets:
  databaseUrl: "your_base64_encoded_database_url_here"
  secretKey: "your_base64_encoded_secret_key_here"
  betterAuthSecret: "your_base64_encoded_auth_secret_here"
  cohereApiKey: "your_base64_encoded_api_key_here"
```

To encode your values, use:
```bash
echo -n 'your_value_here' | base64
```

### 6. Install Helm Chart
```bash
cd helm/todo-chart
helm install todo-app . -f ../secrets.yaml
```

### 7. Access the Application
```bash
# Get the frontend service URL
minikube service todo-app-frontend --url
```

Or use the dashboard:
```bash
minikube dashboard
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
   kubectl logs deployment/todo-app-frontend
   kubectl logs deployment/todo-app-backend
   ```

4. Port forward to test the services:
   ```bash
   kubectl port-forward svc/todo-app-frontend 8080:80
   ```

## Troubleshooting

### Common Issues
- **Images not found**: Ensure you ran `eval $(minikube docker-env)` before building
- **Service not accessible**: Check NodePort range and firewall settings
- **Secrets not mounted**: Verify secret names match values in Helm chart
- **Database connection issues**: Check that the database URL is properly encoded in secrets

### Useful Commands
- View Minikube dashboard: `minikube dashboard`
- Check cluster status: `kubectl cluster-info`
- View all resources: `kubectl get all`
- Describe a specific resource: `kubectl describe <resource-type> <resource-name>`
- View logs: `kubectl logs <pod-name>`

## Cleanup
```bash
helm uninstall todo-app
minikube stop
```

## Development Workflow

For development, you can make changes to the Dockerfiles or application code and rebuild:

1. Make code changes
2. Rebuild the affected image:
   ```bash
   docker build -t todo-frontend:latest -f ./frontend/Dockerfile ./frontend
   ```
3. Restart the deployment:
   ```bash
   kubectl rollout restart deployment/todo-app-frontend
   ```