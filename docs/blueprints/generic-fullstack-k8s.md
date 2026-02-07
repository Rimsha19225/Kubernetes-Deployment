# Generic Full-Stack Kubernetes Blueprint

## Overview
This blueprint describes a standardized approach for deploying full-stack web applications (frontend + backend) to Kubernetes using Docker containers, Helm charts, and standardized configuration patterns.

## Architecture Pattern
- Frontend application (Node.js/React/Vue/Angular) served on port 3000
- Backend API (Express/FastAPI/Django/Spring Boot) served on port 8000
- External database connection via secrets
- Environment-specific configuration via ConfigMaps
- Health checks for monitoring and readiness

## Containerization Strategy
### Frontend Container
- Multi-stage build for optimized images
- Static asset serving
- Environment variable injection at build time or runtime
- Lightweight base image (nginx-alpine or similar)

### Backend Container
- Minimal dependencies installation
- Proper signal handling for graceful shutdown
- Health check endpoint
- Configuration via environment variables

## Kubernetes Resource Pattern
### Deployments
- Separate deployments for frontend and backend
- Proper resource requests and limits
- Health checks (liveness and readiness probes)
- Pod anti-affinity for high availability (optional)

### Services
- Frontend: NodePort or LoadBalancer for external access
- Backend: ClusterIP for internal access only
- Proper port mapping (service → container)

### ConfigMaps
- Non-sensitive configuration
- Runtime environment settings
- API endpoints for frontend/backend communication

### Secrets
- Database credentials
- API keys
- Encryption secrets
- TLS certificates (if needed)

## Helm Chart Structure
```
chart-name/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── _helpers.tpl
└── README.md
```

## Configuration Parameters
The Helm chart should accept these common parameters:

### Image Configuration
- `{frontend/backend}.image.repository`
- `{frontend/backend}.image.tag`
- `{frontend/backend}.image.pullPolicy`

### Service Configuration
- `{frontend/backend}.service.type`
- `{frontend/backend}.service.port`
- `frontend.service.nodePort` (for NodePort services)

### Resource Configuration
- `{frontend/backend}.resources.requests.memory`
- `{frontend/backend}.resources.requests.cpu`
- `{frontend/backend}.resources.limits.memory`
- `{frontend/backend}.resources.limits.cpu`

### Replica Configuration
- `{frontend/backend}.replicaCount`

## Environment Variables Pattern
### Frontend Environment Variables
- `NEXT_PUBLIC_API_BASE_URL` (for API communication)
- `NEXT_PUBLIC_APP_URL` (for self-referencing)

### Backend Environment Variables
- `DATABASE_URL` (database connection)
- `SECRET_KEY` (JWT/encryption)
- `API_KEYS` (external service keys)
- `LOG_LEVEL` (logging configuration)

## Security Considerations
- Never put secrets in ConfigMaps
- Use Kubernetes secrets for sensitive data
- Set proper resource limits to prevent resource exhaustion
- Use non-root user in containers (where possible)
- Enable RBAC if needed
- Consider network policies for traffic restriction

## Monitoring and Observability
- Standardized health check endpoints
- Proper logging format
- Resource limits for monitoring
- Standard labels for service discovery

## Deployment Workflow
1. Build Docker images
2. Push to registry (or use Minikube's Docker environment)
3. Create values file with environment-specific configuration
4. Install Helm chart with values
5. Verify deployment status
6. Monitor application health

## Scaling Considerations
- Horizontal Pod Autoscaler based on CPU/memory
- Database connection pool sizing
- Session management (stateless services preferred)
- CDN for static assets (frontend)

## Adaptation Instructions
To adapt this blueprint for other full-stack applications:

1. **Replace Dockerfiles** with appropriate build processes for your tech stack
2. **Adjust port numbers** in deployments and services to match your application
3. **Update environment variables** to match your application's configuration needs
4. **Modify health check paths** to match your application's endpoints
5. **Adjust resource requests/limits** based on your application's requirements
6. **Update image names** in values.yaml and deployment templates
7. **Customize security context** if required by your application
8. **Modify service types** based on your access requirements

## Technology Agnostic Elements
- Kubernetes resource definitions (Deployments, Services, ConfigMaps, Secrets)
- Helm templating structure
- Standardized labeling scheme
- Service discovery patterns
- Resource management approach
- Security patterns

This blueprint provides a solid foundation that can be customized for various full-stack application technologies while maintaining consistent deployment patterns.