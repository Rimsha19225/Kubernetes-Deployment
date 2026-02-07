# AI Operations Integration Guide

## kubectl-ai Usage

The deployment is configured for AI-assisted operations with proper labeling for kubectl-ai identification.

### Common Operations with kubectl-ai

#### Inspecting Resources
```bash
# View all resources
kubectl-ai view all resources

# Inspect specific deployment
kubectl-ai view deployment todo-app-frontend

# Check service status
kubectl-ai view service todo-app-frontend
```

#### Scaling Operations
```bash
# Scale frontend deployment
kubectl-ai scale deployment todo-app-frontend --replicas=3

# Scale backend deployment
kubectl-ai scale deployment todo-app-backend --replicas=2
```

#### Troubleshooting
```bash
# Analyze pod issues
kubectl-ai analyze pod -l app=todo-app-frontend

# Check resource usage
kubectl-ai analyze resources -l ai-monitored=true
```

### Resource Labels for AI Identification

All resources are labeled with:
- `ai-monitored: "true"` - Enables AI monitoring
- `component: frontend/backend` - Identifies the component type
- Standard Kubernetes labels for grouping

## kagent Monitoring

kagent can monitor the deployed services with the following configuration:

### Pod Monitoring
All pods are configured with:
- Proper health checks (liveness and readiness probes)
- Resource limits and requests defined
- Appropriate labels for kagent identification

### Health Check Configuration
- Frontend: Health check on `/` endpoint, port 3000
- Backend: Health check on `/health` endpoint, port 8000
- Both with appropriate initial delays and intervals

### Resource Monitoring
- Memory and CPU usage tracked via resource limits/requests
- Pod status and restart counts monitored
- Service availability monitored through endpoints

## Recommended AI Operations

### Routine Monitoring
```bash
# Monitor all todo-app resources
kubectl get all -l app=todo-app

# Check resource utilization
kubectl top pods
```

### Scaling Based on Load
The deployments are configured with resource limits that allow for horizontal pod autoscaling based on CPU and memory usage.

### Common Maintenance Tasks
```bash
# Restart all pods in deployment
kubectl rollout restart deployment/todo-app-frontend

# Update image in deployment
kubectl set image deployment/todo-app-backend backend=todo-backend:new-version

# View logs from all app pods
kubectl logs -l app=todo-app --tail=100
```

## AI Tool Integration Points

### For kubectl-ai
- Proper resource naming following conventions
- Descriptive labels for identification
- Standard ports and protocols
- Health endpoints available

### For kagent
- Resource monitoring labels applied
- Proper health checks configured
- Resource requests and limits defined
- Pod readiness/liveness probes

These configurations allow AI tools to:
- Identify and categorize resources properly
- Monitor application health
- Analyze resource usage patterns
- Recommend scaling actions
- Troubleshoot common issues