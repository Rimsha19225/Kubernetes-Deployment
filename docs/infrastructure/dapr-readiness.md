# Dapr Integration Readiness

## Overview
This document outlines how the current Kubernetes deployment is prepared for future Dapr (Distributed Application Runtime) integration.

## Current Dapr Preparation

### Annotations in Deployments
Both frontend and backend deployments include the placeholder annotation:
```yaml
annotations:
  dapr.io/enabled: "false"  # Placeholder for future Dapr integration
```

This can be easily updated to `"true"` when Dapr integration is required.

### Dapr Configuration Template

When Dapr is ready to be enabled, update the deployment annotations:

#### For Backend (Service-to-Service Calls)
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
  dapr.io/app-protocol: "http"
  dapr.io/log-level: "info"
  dapr.io/disable-builtin-k8s-secret-store: "false"
```

#### For Frontend (API Gateway Pattern)
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-frontend"
  dapr.io/app-port: "3000"
  dapr.io/app-protocol: "http"
  dapr.io/log-level: "info"
  dapr.io/sidecar-http-port: "3500"  # Dapr sidecar HTTP port
  dapr.io/sidecar-grpc-port: "50001" # Dapr sidecar gRPC port
```

## Dapr Components for Todo Application

### State Store Component
For persisting user data and task state:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

### Pub/Sub Component
For event-driven architecture:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### Configuration Store
For application configuration:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-configstore
spec:
  type: configuration.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

## Dapr Sidecar Injection Process

### Prerequisites
1. Dapr runtime installed in Kubernetes cluster:
```bash
dapr init -k
```

2. Dapr Kubernetes components verified:
```bash
dapr status -k
```

### Enabling Dapr in the Application
To enable Dapr in the Helm chart, users can update the values:

```yaml
dapr:
  enabled: true
  appId: "todo-app"
  appPort: 8000
  appProtocol: "http"
  logLevel: "info"
```

And then update the deployment templates to include Dapr annotations based on these values.

## Dapr Integration Benefits

### Service Invocation
- Automatic service discovery
- Resilient service-to-service communication
- Built-in retries and circuit breakers

### State Management
- Distributed state with various store options
- Actor pattern support
- Transactional state operations

### Pub/Sub
- Event-driven architecture
- Multiple pub/sub broker options
- Declarative subscription model

### Secret Management
- Secure secret retrieval
- Multiple secret stores
- Automatic secret rotation

### Observability
- Distributed tracing
- Metrics collection
- Health monitoring

## Migration Path

### Step 1: Enable Dapr Sidecars
Update the deployment annotations to enable Dapr.

### Step 2: Configure Components
Apply Dapr component configurations for state, pub/sub, and configuration stores.

### Step 3: Update Application Code (if needed)
Modify application code to use Dapr SDKs for service invocation, state management, etc.

### Step 4: Test Integration
Verify Dapr-enabled functionality in the deployment.

## Current Deployment Compatibility
The current deployment is fully compatible with Dapr integration because:

1. Services use standard HTTP/REST communication patterns
2. Applications are stateless (except for database connections)
3. Proper health check endpoints are available
4. Container networking is properly configured
5. Security contexts allow sidecar injection

The infrastructure is ready for Dapr integration with minimal changes required.