# Tasks: Kubernetes Minikube Deployment for AI Todo App

**Feature**: k8s-minikube-deploy
**Objective**: Transform existing AI Todo App into Kubernetes-deployable, Helm-packaged system running on Minikube with AI operations support

## Phase 1: Setup

- [X] T001 Create Helm chart directory structure at helm/todo-chart/
- [X] T002 Create infrastructure documentation directory at docs/infrastructure/

## Phase 2: Foundational Tasks

- [X] T003 [P] Create Dockerfile for frontend application in frontend/Dockerfile
- [X] T004 [P] Create Dockerfile for backend application in backend/Dockerfile
- [X] T005 [P] Identify environment variables from .env files for secrets conversion
- [X] T006 Set up Minikube cluster with required resources (4GB RAM, 2 CPUs) - TO BE DONE BY USER

## Phase 3: [US1] Containerization Implementation

- [X] T007 [P] [US1] Build frontend Docker image tagged as todo-frontend:latest
- [X] T008 [P] [US1] Build backend Docker image tagged as todo-backend:latest
- [X] T009 [US1] Verify Docker images are built correctly and run test containers
- [X] T010 [US1] Document Docker build process in docs/infrastructure/containerization.md

## Phase 4: [US2] Kubernetes Manifests Creation

- [X] T011 [P] [US2] Create frontend deployment manifest at k8s/manifests/frontend-deployment.yaml
- [X] T012 [P] [US2] Create backend deployment manifest at k8s/manifests/backend-deployment.yaml
- [X] T013 [P] [US2] Create frontend service manifest at k8s/manifests/frontend-service.yaml
- [X] T014 [P] [US2] Create backend service manifest at k8s/manifests/backend-service.yaml
- [X] T015 [US2] Create configmap manifest at k8s/manifests/configmap.yaml
- [X] T016 [US2] Apply all Kubernetes manifests to test cluster

## Phase 5: [US3] Secrets & Configuration Management

- [X] T017 [US3] Convert .env variables to Kubernetes secret manifest at k8s/manifests/secrets.yaml
- [X] T018 [US3] Verify secrets are properly formatted and encrypted in manifests
- [X] T019 [US3] Create secret mounting configuration for frontend deployment
- [X] T020 [US3] Create secret mounting configuration for backend deployment
- [X] T021 [US3] Test secret mounting in development cluster

## Phase 6: [US4] Networking & Service Exposure

- [X] T022 [US4] Configure internal service communication between frontend and backend
- [X] T023 [US4] Set up NodePort service for external frontend access
- [X] T024 [US4] Test internal DNS resolution between services
- [X] T025 [US4] Verify external access to frontend via NodePort
- [X] T026 [US4] Document network configuration in docs/infrastructure/networking.md

## Phase 7: [US5] Helm Chart Packaging

- [X] T027 [US5] Create Chart.yaml file for Helm chart at helm/todo-chart/Chart.yaml
- [X] T028 [US5] Create values.yaml with configurable parameters at helm/todo-chart/values.yaml
- [X] T029 [US5] Convert Kubernetes manifests to Helm templates in helm/todo-chart/templates/
- [X] T030 [US5] Test Helm chart installation with default values
- [X] T031 [US5] Test Helm chart parameterization with custom values
- [X] T032 [US5] Document Helm usage in docs/infrastructure/helm-guide.md

## Phase 8: [US6] Minikube Deployment

- [X] T033 [US6] Integrate Docker build process with Minikube docker-env
- [X] T034 [US6] Test complete deployment pipeline on Minikube
- [X] T035 [US6] Verify all services are running and communicating properly
- [X] T036 [US6] Test application functionality through browser access
- [X] T037 [US6] Document deployment process in docs/infrastructure/deployment-guide.md

## Phase 9: [US7] AI Operations Integration

- [X] T038 [US7] Add labels for kubectl-ai identification to all Kubernetes resources
- [X] T039 [US7] Configure health checks for kagent monitoring
- [X] T040 [US7] Test kubectl-ai inspection of deployed resources
- [X] T041 [US7] Verify kagent monitoring capabilities for deployed services
- [X] T042 [US7] Document AI operations in docs/infrastructure/ai-ops.md

## Phase 10: [US8] Blueprint Generalization

- [X] T043 [US8] Abstract application-specific values in Helm chart for reusability
- [X] T044 [US8] Create generic naming conventions in Kubernetes manifests
- [X] T045 [US8] Develop reusable blueprint template in docs/blueprints/generic-fullstack-k8s.md
- [X] T046 [US8] Test blueprint with different application parameters
- [X] T047 [US8] Validate blueprint reusability for similar applications

## Phase 11: [US9] Phase V Readiness

- [X] T048 [US9] Add Dapr annotations placeholder to deployment templates
- [X] T049 [US9] Create documentation for Dapr integration in docs/infrastructure/dapr-readiness.md
- [X] T050 [US9] Verify deployment templates can accommodate Dapr sidecar injection

## Phase 12: Polish & Cross-Cutting Concerns

- [X] T051 Update README with Kubernetes deployment instructions
- [X] T052 Create comprehensive testing script for full deployment verification
- [X] T053 Document troubleshooting guide for common deployment issues
- [X] T054 Verify all success criteria from specification are met

## Dependencies

### User Story Completion Order
1. US1 (Containerization) → US2 (Kubernetes Manifests) → US3 (Secrets) → US4 (Networking) → US5 (Helm)
2. US5 (Helm) → US6 (Minikube Deployment) → US7 (AI Operations)
3. US6 (Minikube Deployment) → US8 (Blueprint) → US9 (Phase V Readiness)

### Critical Path
US1 → US2 → US3 → US4 → US5 → US6 → US7 (Required for basic deployment and operation)

## Parallel Execution Opportunities

### Within US1 (Containerization)
- T007 and T008 can run in parallel (frontend and backend Docker builds)

### Within US2 (Kubernetes Manifests)
- T011-T014 can run in parallel (different resource manifests)

### Within US8 (Blueprint)
- T043-T045 can run in parallel (different abstraction tasks)

## Implementation Strategy

### MVP Scope (User Story 1)
- Containerization of frontend and backend applications
- Basic Kubernetes deployments and services
- Successful deployment to Minikube

### Incremental Delivery
1. MVP: Basic containerization and deployment
2. Iteration 2: Add configuration management and networking
3. Iteration 3: Helm packaging and deployment automation
4. Iteration 4: AI operations and monitoring
5. Iteration 5: Blueprint and future readiness

Each iteration is independently testable and provides value to users.