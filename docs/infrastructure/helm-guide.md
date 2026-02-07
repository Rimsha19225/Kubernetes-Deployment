# Helm Chart Guide for Todo Application

## Installation

### Prerequisites
- Helm 3.x installed
- Kubernetes cluster (Minikube recommended for development)

### Installing the Chart

1. Navigate to the chart directory:
```bash
cd helm/todo-chart
```

2. Install with default values:
```bash
helm install todo-app .
```

3. Install with custom values:
```bash
helm install todo-app . --values my-values.yaml
```

### Providing Secrets

Since the application requires sensitive data, you need to provide secrets during installation:

```bash
helm install todo-app . \
  --set secrets.databaseUrl="your_encoded_database_url" \
  --set secrets.secretKey="your_encoded_secret_key" \
  --set secrets.betterAuthSecret="your_encoded_auth_secret" \
  --set secrets.cohereApiKey="your_encoded_api_key"
```

Alternatively, create a values file:
```yaml
secrets:
  databaseUrl: "your_base64_encoded_database_url"
  secretKey: "your_base64_encoded_secret_key"
  betterAuthSecret: "your_base64_encoded_auth_secret"
  cohereApiKey: "your_base64_encoded_api_key"
```

Then install:
```bash
helm install todo-app . -f my-secrets.yaml
```

## Upgrading the Chart

```bash
helm upgrade todo-app . [flags]
```

## Uninstalling the Chart

```bash
helm uninstall todo-app
```

## Configuration

The following table lists the configurable parameters of the todo-app chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.type` | Frontend service type | `NodePort` |
| `frontend.service.port` | Frontend service port | `80` |
| `frontend.service.nodePort` | Frontend NodePort (if type is NodePort) | `30080` |
| `frontend.replicaCount` | Number of frontend replicas | `1` |
| `frontend.resources` | Frontend resource requests and limits | Memory/CPU as defined in values.yaml |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.type` | Backend service type | `ClusterIP` |
| `backend.service.port` | Backend service port | `80` |
| `backend.replicaCount` | Number of backend replicas | `1` |
| `backend.resources` | Backend resource requests and limits | Memory/CPU as defined in values.yaml |
| `secrets.databaseUrl` | Base64 encoded database URL | `""` |
| `secrets.secretKey` | Base64 encoded JWT secret | `""` |
| `secrets.betterAuthSecret` | Base64 encoded Better Auth secret | `""` |
| `secrets.cohereApiKey` | Base64 encoded Cohere API key | `""` |

## Values File Example

```yaml
frontend:
  image:
    repository: my-registry/todo-frontend
    tag: v1.0.0
  service:
    type: LoadBalancer  # Change for production
    nodePort: 30081
  replicaCount: 2
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1"

backend:
  image:
    repository: my-registry/todo-backend
    tag: v1.0.0
  service:
    type: ClusterIP
  replicaCount: 2
  resources:
    requests:
      memory: "1Gi"
      cpu: "1"
    limits:
      memory: "2Gi"
      cpu: "2"

secrets:
  # Remember to base64 encode these values
  databaseUrl: "encoded_db_url_here"
  secretKey: "encoded_secret_here"
  betterAuthSecret: "encoded_auth_secret_here"
  cohereApiKey: "encoded_api_key_here"
```