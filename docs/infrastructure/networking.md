# Network Configuration Documentation

## Service Communication

### Internal Communication (Frontend → Backend)
- Frontend accesses backend via: `http://backend-service:80`
- Using Kubernetes internal DNS: `backend-service.default.svc.cluster.local`
- Communication happens over port 80 (service port) → 8000 (container port)

### External Access (Browser → Frontend)
- Frontend is exposed via NodePort service on port 30080
- Accessible externally at: `http://<minikube-ip>:30080`
- NodePort range: 30000-32767

## Service Discovery
- Frontend discovers backend using Kubernetes DNS: `backend-service`
- Backend discovers database via environment variable: `DATABASE_URL`

## Network Policies (Future Enhancement)
- Consider implementing network policies to restrict traffic
- Example: Allow only frontend to communicate with backend
- Deny external access to backend service

## Load Balancing
- Kubernetes built-in load balancing for multiple pod replicas
- Service distributes requests across available pods