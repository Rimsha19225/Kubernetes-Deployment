# Troubleshooting Guide for Kubernetes Deployment

## Common Issues and Solutions

### 1. Images Not Found

**Problem**: Pods are stuck in ImagePullBackOff state
```
kubectl get pods
NAME                                  READY   STATUS              RESTARTS   AGE
todo-app-backend-6c5d4d8f7b-xl2v4    0/1     ImagePullBackOff   0          5m
```

**Solution**:
- If using Minikube, ensure Docker environment is set:
  ```bash
  eval $(minikube docker-env)
  ```
- Rebuild the images:
  ```bash
  docker build -t todo-frontend:latest -f ./frontend/Dockerfile ./frontend
  docker build -t todo-backend:latest -f ./backend/Dockerfile ./backend
  ```
- Restart the deployments:
  ```bash
  kubectl rollout restart deployment/todo-app-frontend
  kubectl rollout restart deployment/todo-app-backend
  ```

### 2. Service Not Accessible

**Problem**: Cannot access the application through the NodePort service

**Solution**:
- Check if the service is properly configured:
  ```bash
  kubectl get service todo-app-frontend
  ```
- Verify the service type is NodePort:
  ```bash
  kubectl describe service todo-app-frontend
  ```
- Get the correct URL for Minikube:
  ```bash
  minikube service todo-app-frontend --url
  ```

### 3. Database Connection Issues

**Problem**: Backend logs show database connection errors

**Solution**:
- Verify the database URL secret is properly encoded:
  ```bash
  kubectl get secret todo-app-secrets -o yaml
  ```
- Check backend logs for specific error details:
  ```bash
  kubectl logs deployment/todo-app-backend
  ```
- Ensure the Neon database URL is properly base64 encoded in the values file

### 4. Secrets Not Mounted

**Problem**: Application fails with missing environment variables that should come from secrets

**Solution**:
- Verify the secret exists:
  ```bash
  kubectl get secret todo-app-secrets
  ```
- Check if the deployment refers to the correct secret name:
  ```bash
  kubectl get deployment todo-app-backend -o yaml | grep -A 10 -B 10 secretKeyRef
  ```
- Check if the key names in the secret match what's referenced in the deployment

### 5. Health Check Failures

**Problem**: Pods are in CrashLoopBackOff or Unhealthy state

**Solution**:
- Check pod status and events:
  ```bash
  kubectl describe pod <pod-name>
  ```
- Check application logs:
  ```bash
  kubectl logs <pod-name>
  ```
- Verify health check paths are correct and accessible
- Adjust initialDelaySeconds if needed for slower startups

## Debugging Steps

### 1. Check Overall Deployment Status
```bash
kubectl get all -l app.kubernetes.io/instance=todo-app
```

### 2. Check Resource Details
```bash
kubectl describe deployment todo-app-frontend
kubectl describe deployment todo-app-backend
kubectl describe service todo-app-frontend
kubectl describe service todo-app-backend
```

### 3. Check Logs
```bash
kubectl logs deployment/todo-app-frontend
kubectl logs deployment/todo-app-backend
```

### 4. Check Events
```bash
kubectl get events --sort-by='.lastTimestamp'
```

### 5. Port Forward for Direct Testing
```bash
# Test frontend
kubectl port-forward svc/todo-app-frontend 8080:80

# Test backend
kubectl port-forward svc/todo-app-backend 8081:80
```

## Helm-Specific Issues

### 1. Chart Installation Fails
```bash
# Check for validation errors
helm lint helm/todo-chart

# Get more detailed error info
helm install todo-app helm/todo-chart --debug --dry-run

# Check for existing releases
helm list
```

### 2. Upgrade Issues
```bash
# Rollback to previous version
helm rollback todo-app

# Check history
helm history todo-app
```

### 3. Missing Values
If getting errors about undefined values, ensure all required values are provided:
```bash
helm install todo-app helm/todo-chart \
  --set secrets.databaseUrl=your_encoded_db_url \
  --set secrets.secretKey=your_encoded_secret
```

## Networking Issues

### 1. Frontend Cannot Connect to Backend
- Verify the backend service name matches what's in the frontend environment:
  ```bash
  kubectl get service todo-app-backend
  ```
- Check if the service is accessible internally:
  ```bash
  kubectl run debug --image=curlimages/curl -it --rm -- curl http://todo-app-backend:80/health
  ```

### 2. External Access Problems
- Ensure the frontend service type is set to NodePort or LoadBalancer
- For Minikube, use:
  ```bash
  minikube service todo-app-frontend --url
  ```

## Resource Issues

### 1. Out of Memory
- Increase memory limits in values.yaml:
  ```yaml
  frontend:
    resources:
      limits:
        memory: "1Gi"  # Increase from default
  backend:
    resources:
      limits:
        memory: "2Gi"  # Increase from default
  ```

### 2. CPU Limits Too Restrictive
- Increase CPU limits if experiencing throttling:
  ```yaml
  frontend:
    resources:
      limits:
        cpu: "1000m"  # Increase from default
  backend:
    resources:
      limits:
        cpu: "2000m"  # Increase from default
  ```

## Verification Commands

Use the provided verification script:
```bash
chmod +x scripts/verify-deployment.sh
./scripts/verify-deployment.sh
```

## Additional Help

For more information:
- View all deployed resources: `kubectl get all -l app=todo-app`
- Check resource utilization: `kubectl top pods`
- Get detailed deployment status: `kubectl rollout status deployment/<name>`
- Get all resource configurations: `kubectl get all -l app=todo-app -o yaml`