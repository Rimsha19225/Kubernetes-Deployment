# Specification: Kubernetes Minikube Deployment for AI Todo App

## Feature Overview

This specification defines the exact infrastructure artifacts required to make the existing AI-Native Todo Application (Frontend, Backend, DB, AI Chatbot) Kubernetes-deployable on Minikube using Docker, Kubernetes, Helm, and AI Ops tools. This is Phase IV work focused entirely on infrastructure transformation without modifying application logic.

## Scope

### In Scope
- Docker containerization of frontend and backend services
- Kubernetes Deployments, Services, ConfigMaps, and Secrets
- Helm chart packaging for the full application stack
- Minikube deployment strategy
- Service networking and exposure configuration
- AI operations integration (kubectl-ai, kagent)
- Secrets management (conversion from .env to Kubernetes Secrets)
- Cloud-native blueprint creation for reuse

### Out of Scope
- Application code modification
- Database schema changes
- Business logic alterations
- New feature development

## Functional Requirements

### FR-1: Containerization
- System MUST create separate Docker images for frontend and backend services
- System MUST define appropriate build contexts for each service
- System MUST expose correct ports for each service
- System MUST handle environment variables through Kubernetes ConfigMaps and Secrets

### FR-2: Kubernetes Resources
- System MUST create Deployments for frontend and backend services
- System MUST create Services to expose frontend (NodePort) and backend (ClusterIP)
- System MUST create ConfigMaps for non-sensitive configuration
- System MUST create Secrets for sensitive data (JWT, DB URL, API keys)
- System MUST define appropriate resource limits and replica counts

### FR-3: Networking & Service Exposure
- System MUST establish internal communication between frontend and backend via ClusterIP services
- System MUST expose frontend service via NodePort for external browser access
- System MUST implement proper DNS naming conventions for internal service discovery

### FR-4: Helm Chart Structure
- System MUST create a Helm chart with appropriate templates for all resources
- System MUST define a values.yaml file with configurable parameters
- System MUST support installation via `helm install` command
- System MUST implement parameterization for common deployment variations

### FR-5: Minikube Deployment
- System MUST provide image build strategy for Minikube environment
- System MUST ensure images are available within the cluster
- System MUST define correct deployment order for dependent services

### FR-6: AI Operations Support
- System MUST enable kubectl-ai to inspect and manage all resources
- System MUST support kagent monitoring of pods and cluster health
- System MUST include appropriate labels and annotations for AI tooling

### FR-7: Secrets & Configuration Management
- System MUST convert .env files to Kubernetes Secrets
- System MUST define secure mounting of secrets into pods
- System MUST prohibit plain text secrets in manifests

### FR-8: Cloud-Native Blueprint
- System MUST create reusable blueprint for similar full-stack applications
- System MUST use generic naming conventions
- System MUST separate infrastructure logic from application logic

### FR-9: Future Readiness
- System MUST support Dapr sidecar integration in future phases
- System MUST implement pod annotations strategy to accommodate Dapr

## Technical Architecture

### Containerization Specification
- **Dockerfiles required**: 2 (one for frontend, one for backend)
- **Separate containers needed**:
  - Frontend container: Next.js application
  - Backend container: FastAPI application
- **Build context**:
  - Frontend: ./frontend directory
  - Backend: ./backend directory
- **Port exposure rules**:
  - Frontend: Port 3000 (Next.js default)
  - Backend: Port 8000 (FastAPI default)
- **Environment variable handling strategy**: Store non-sensitive vars in ConfigMap, sensitive vars in Secrets

### Kubernetes Resource Specification
- **Deployments needed**:
  - frontend-deployment: Running Next.js application
  - backend-deployment: Running FastAPI application
- **Services needed**:
  - frontend-service: NodePort service for external access
  - backend-service: ClusterIP service for internal access
- **ConfigMaps needed**:
  - app-config: Non-sensitive application configuration
- **Secrets needed**:
  - app-secrets: JWT secret, DB URL, API keys
- **Labels and selectors strategy**:
  - app: {app-name}
  - version: {version}
  - tier: frontend/backend
- **Pod resource limits and replicas**:
  - Memory: 512Mi (request), 1Gi (limit) per pod
  - CPU: 250m (request), 500m (limit) per pod
  - Replicas: 1 for both frontend and backend

### Networking & Service Exposure
- **Frontend to backend communication**: Using backend-service.default.svc.cluster.local
- **Browser access to frontend**: Via NodePort service on port range 30000-32767
- **Internal DNS naming**: Using Kubernetes DNS convention (service.namespace.svc.cluster.local)

### Helm Chart Structure
- **Chart directory structure**:
  - Chart.yaml
  - values.yaml
  - templates/
    - frontend-deployment.yaml
    - backend-deployment.yaml
    - frontend-service.yaml
    - backend-service.yaml
    - configmap.yaml
    - secret.yaml
    - ingress.yaml (optional)
- **Values.yaml structure**:
  - frontend.image.repository: Image repository for frontend
  - frontend.image.tag: Image tag for frontend
  - frontend.service.port: Service port for frontend
  - frontend.replicaCount: Number of frontend replicas
  - backend.image.repository: Image repository for backend
  - backend.image.tag: Image tag for backend
  - backend.service.port: Service port for backend
  - backend.replicaCount: Number of backend replicas
  - resources.limits.memory: Memory limits
  - resources.limits.cpu: CPU limits
- **Parameterization rules**: Allow customization of image, ports, resource limits
- **Install command expectations**: `helm install todo-app ./todo-chart`

### Minikube Deployment Specification
- **Image build strategy**: Build images directly in Minikube Docker environment using `eval $(minikube docker-env)`
- **Image availability**: Images built in Minikube Docker daemon context
- **Deployment order**: Database first (Neon), then backend, then frontend

### AI Operations Specification
- **kubectl-ai usage**: All resources labeled appropriately for AI identification and management
- **kagent monitoring**: Health checks and resource monitoring enabled for all pods
- **Required labels**: `ai-monitored: true`, `component: frontend/backend`

### Secrets & Configuration Management
- **.env conversion**: Extract JWT_SECRET, DATABASE_URL, API keys to Kubernetes Secrets
- **Secret mounting rules**: Mount secrets as environment variables or volume mounts
- **Security requirements**: No plain text secrets in manifests or values.yaml

### Cloud-Native Blueprint Requirement
- **Generic naming**: Use parameterized names in templates
- **Reusability features**: Parameterized image names, ports, and configuration
- **App logic separation**: Clear distinction between app and infra logic

### Phase V Readiness
- **Dapr readiness**: Include annotation support for Dapr sidecars
- **Pod annotations placeholder**:预留 annotations field in deployment templates for future Dapr integration

## Assumptions
- Neon database is accessed via external connection string
- Frontend and backend communicate via REST API
- All existing application logic remains unchanged
- Minikube is properly installed and running

## Success Criteria

- Full application (frontend, backend, db, chatbot) successfully runs on Minikube
- Single `helm install` command deploys the entire system
- kubectl-ai can inspect and manage all deployed resources
- kagent can monitor cluster health and individual pod status
- No manual YAML editing required after agent-generated manifests
- The cloud-native blueprint is reusable for similar full-stack applications
- All services are accessible through browsers via NodePort
- Secrets are properly managed using Kubernetes Secrets
- System maintains all existing application functionality