# Data Model: Kubernetes Infrastructure for AI Todo App

## Infrastructure Components

### Container Images
- **todo-frontend**
  - Type: Application Image
  - Base: Node.js LTS
  - Runtime: Next.js
  - Port: 3000
  - Dependencies: Node modules, application code

- **todo-backend**
  - Type: Application Image
  - Base: Python 3.11
  - Runtime: FastAPI
  - Port: 8000
  - Dependencies: Python packages, application code

### Kubernetes Deployments
- **frontend-deployment**
  - Replica Count: 1 (configurable)
  - Container Image: todo-frontend:latest
  - Resource Requests: 256Mi memory, 0.2 CPU
  - Resource Limits: 512Mi memory, 0.5 CPU
  - Environment: From ConfigMap and Secrets

- **backend-deployment**
  - Replica Count: 1 (configurable)
  - Container Image: todo-backend:latest
  - Resource Requests: 512Mi memory, 0.3 CPU
  - Resource Limits: 1Gi memory, 0.7 CPU
  - Environment: From ConfigMap and Secrets

### Kubernetes Services
- **frontend-service**
  - Type: NodePort
  - Port: 80 (external), 3000 (target)
  - Selector: app=todo-frontend
  - Purpose: External access to frontend

- **backend-service**
  - Type: ClusterIP
  - Port: 8000
  - Selector: app=todo-backend
  - Purpose: Internal access to backend

### Configurations
- **app-config ConfigMap**
  - frontend_api_url: http://backend-service:8000
  - backend_debug: "false"
  - cors_allowed_origins: "*"

- **app-secrets Secret**
  - jwt_secret: [encrypted]
  - database_url: [encrypted]
  - cohere_api_key: [encrypted]

### Persistent Storage (Future)
- **todo-data-volume** (Optional)
  - Type: PersistentVolumeClaim
  - Size: 1Gi
  - Access Mode: ReadWriteOnce
  - Purpose: Persistent data storage (if needed)

## Helm Chart Structure
- **Chart.yaml**
  - Name: todo-app
  - Version: 0.1.0
  - AppVersion: 1.0.0

- **values.yaml**
  - frontend.image.repository: todo-frontend
  - frontend.image.tag: latest
  - frontend.service.type: NodePort
  - frontend.service.port: 80
  - backend.image.repository: todo-backend
  - backend.image.tag: latest
  - backend.service.port: 8000
  - resources.limits.memory: 1Gi
  - resources.limits.cpu: "0.7"

## Networking Model
- **Internal Communication**: frontend → backend-service.default.svc.cluster.local:8000
- **External Access**: NodePort service accessible via Minikube IP
- **DNS Resolution**: Kubernetes internal DNS for service discovery
- **Load Balancing**: Built-in Kubernetes service load balancing

## Security Model
- **Secrets Management**: Kubernetes native secrets for sensitive data
- **Network Policy**: (Future) Restrict inter-pod communication
- **RBAC**: (Future) Role-based access control for cluster resources
- **Pod Security**: (Future) Security contexts and policies