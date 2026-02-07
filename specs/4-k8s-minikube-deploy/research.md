# Research: Kubernetes Minikube Deployment for AI Todo App

## Container Port Requirements

### Frontend Service
- **Default Port**: 3000 (Next.js standard)
- **Alternative Ports**: 3001-3009 (if default unavailable)
- **Protocol**: HTTP/HTTPS

### Backend Service
- **Default Port**: 8000 (FastAPI standard)
- **Alternative Ports**: 8001-8009 (if default unavailable)
- **Protocol**: HTTP/HTTPS

## Resource Limit Recommendations

### Frontend Container
- **Memory Request**: 256MB
- **Memory Limit**: 512MB
- **CPU Request**: 0.2
- **CPU Limit**: 0.5
- **Replica Count**: 1 (development), 2+ (production)

### Backend Container
- **Memory Request**: 512MB
- **Memory Limit**: 1GB
- **CPU Request**: 0.3
- **CPU Limit**: 0.7
- **Replica Count**: 1 (development), 2+ (production)

## Neon Database Configuration

### Connection Method
- **External Connection**: Use Neon database URL via Kubernetes Secret
- **Connection Pooling**: Managed by backend application
- **Environment Variables**: DATABASE_URL in Kubernetes Secret

### Security Considerations
- **TLS/SSL**: Enabled by default with Neon
- **Connection Encryption**: Always encrypted in transit
- **Authentication**: Token-based authentication with Neon

## Helm Chart Best Practices

### Template Structure
- **Parameterization**: Use {{ .Values.param }} for all configurable values
- **Default Values**: Set reasonable defaults in values.yaml
- **Conditional Templates**: Use if/else blocks for optional features

### Naming Conventions
- **Release Names**: Lowercase, hyphenated (e.g., todo-app)
- **Resource Names**: Include release name for uniqueness
- **Labels**: Consistent labeling across all resources

## Minikube-Specific Considerations

### Image Loading Strategy
- **Method**: eval $(minikube docker-env) to use Minikube's Docker daemon
- **Benefits**: No need to push images to external registry
- **Workflow**: Build images directly in Minikube environment

### Resource Allocation
- **Memory**: At least 4GB allocated to Minikube VM
- **CPU**: At least 2 cores allocated to Minikube VM
- **Disk**: Sufficient space for images and persistent volumes

## AI Operations Integration

### kubectl-ai Capabilities
- **Resource Inspection**: View deployment status, logs, events
- **Scaling Operations**: Adjust replica counts dynamically
- **Troubleshooting**: Analyze issues and suggest solutions

### kagent Monitoring
- **Health Checks**: Regular monitoring of pod and service status
- **Performance Metrics**: CPU, memory, and network usage
- **Alerting**: Notifications for anomalies or failures