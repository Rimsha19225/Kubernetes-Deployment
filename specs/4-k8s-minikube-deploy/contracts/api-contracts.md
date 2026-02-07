# API Contracts: Kubernetes Infrastructure for AI Todo App

## Container Interface Contracts

### Frontend Container Contract
- **Entrypoint**: `npm run start` or `yarn start`
- **Exposed Port**: 3000
- **Environment Variables**:
  - NEXT_PUBLIC_API_BASE_URL: Backend service URL
  - NEXT_PUBLIC_DEBUG_MODE: Debug flag
- **Health Check Endpoint**: `/health` (returns 200 OK)

### Backend Container Contract
- **Entrypoint**: `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Exposed Port**: 8000
- **Environment Variables**:
  - DATABASE_URL: Database connection string
  - JWT_SECRET: JWT signing secret
  - DEBUG: Debug flag
- **Health Check Endpoint**: `/health` (returns 200 OK)

## Kubernetes API Contracts

### Deployment Contract
- **API Version**: apps/v1
- **Kind**: Deployment
- **Spec Requirements**:
  - replicas: configurable (default: 1)
  - selector.matchLabels: must match template.metadata.labels
  - template.spec.containers[]: must specify name and image
  - resources: requests and limits for CPU/memory

### Service Contract
- **API Version**: v1
- **Kind**: Service
- **Spec Requirements**:
  - selector: must match deployment labels
  - ports[]: must specify port and targetPort
  - type: NodePort for frontend, ClusterIP for backend

### ConfigMap Contract
- **API Version**: v1
- **Kind**: ConfigMap
- **Data Format**: key-value pairs as strings
- **Access Method**: Environment variables or volume mounts

### Secret Contract
- **API Version**: v1
- **Kind**: Secret
- **Type**: Opaque
- **Data Format**: Base64 encoded values
- **Access Method**: Environment variables or volume mounts

## Helm Chart Contract

### Chart Requirements
- **Chart.yaml**:
  - name: Required
  - version: Required (SemVer format)
  - appVersion: Recommended
- **templates/**: Must contain valid Kubernetes manifests
- **values.yaml**: Must contain default values for all parameters

### Parameter Contract
- **frontend.image.repository**: Docker image repository for frontend
- **frontend.image.tag**: Docker image tag for frontend
- **frontend.service.port**: Port for frontend service
- **backend.image.repository**: Docker image repository for backend
- **backend.image.tag**: Docker image tag for backend
- **backend.service.port**: Port for backend service
- **resources.limits.memory**: Memory limit for containers
- **resources.limits.cpu**: CPU limit for containers

## Minikube Integration Contract
- **Docker Environment**: Must use `eval $(minikube docker-env)` for image building
- **Resource Requirements**: Minimum 4GB memory, 2 CPUs
- **Addon Dependencies**: ingress addon for external access
- **Service Access**: NodePort services accessible via `minikube service`

## AI Operations Contract
- **kubectl-ai Compatibility**: All resources must have appropriate labels for AI identification
- **Monitoring Labels**: Resources must include monitoring labels for kagent
- **Health Endpoints**: Applications must expose health check endpoints
- **Log Format**: Structured logging for AI analysis