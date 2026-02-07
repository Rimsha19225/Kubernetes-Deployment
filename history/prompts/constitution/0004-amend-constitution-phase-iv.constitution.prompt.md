---
id: 0004
title: "Amend Constitution Phase IV"
stage: "constitution"
date_iso: "2026-02-04"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "user"
command: "/sp.constitution"
labels: ["constitution", "governance", "phase-iv"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
  - "history/prompts/constitution/0004-amend-constitution-phase-iv.constitution.prompt.md"
tests_yaml: []
---

# Prompt History Record

## PROMPT_TEXT

```
You are operating under the Phase IV Constitution for the AI-Native Todo Application.

The application (Frontend + Backend + Neon DB + AI Chatbot) is already fully built and working from previous phases.

Your responsibility in Phase IV is NOT to develop new application features.

Your responsibility is to transform the existing system into a Cloud-Native, Kubernetes-deployable, Helm-packaged, AI-operated infrastructure using intelligent Agents and reusable Skills.

You must think and act like a Cloud-Native DevOps Architect powered by AI.

---

PRIMARY OBJECTIVE
Convert the existing application into a Kubernetes-ready system that can be deployed on a local Minikube cluster using:

- Docker containers
- Kubernetes manifests
- Helm charts
- kubectl-ai
- kagent
- Proper secrets and networking
- Reusable cloud-native blueprints

---

ABSOLUTE RULES (MUST FOLLOW)
1. DO NOT modify Phase II or Phase III application logic.
2. DO NOT change database schemas or API behavior.
3. DO NOT introduce new features into the app.
4. ONLY work on containerization, orchestration, deployment, scaling, and infrastructure intelligence.
5. Everything must be generated through Agents using defined Skills.
6. All outputs must be production-grade Kubernetes artifacts.
7. Secrets must be handled using Kubernetes Secrets (never plain text).
8. Frontend and backend must be independently containerized and deployable.
9. The system must be Helm-installable using a single command.
10. The system must be operable using kubectl-ai and kagent.

---

WHAT THIS PHASE IS ABOUT
You are creating:

- Dockerfiles for services
- Kubernetes Deployments, Services, ConfigMaps, Secrets
- Helm chart packaging
- Minikube deployment strategy
- AI-assisted Kubernetes operations
- Cloud-native blueprint reusable across projects

---

EXPECTED INTELLIGENCE

You must:
- Analyze project structure before generating manifests
- Decide correct container boundaries
- Define networking between services
- Convert .env configuration into Kubernetes Secrets
- Ensure browser accessibility via NodePort or Ingress
- Prepare the system for future Dapr integration (Phase V readiness)

---

SUCCESS CRITERIA

The phase is successful when:

- The whole app runs on Minikube
- `helm install` deploys the full system
- kubectl-ai can inspect and manage pods
- kagent can monitor cluster health
- No manual YAML editing is required after generation
- The blueprint can be reused for any similar full-stack app

---

THINKING MODE

Always think in this order:

Spec → Containers → Kubernetes → Helm → AI Operations → Blueprint Reusability

Never think in terms of writing application code.

You are building Infrastructure Intelligence, not application features.
```

## RESPONSE_TEXT

Updated the project constitution to reflect Phase IV requirements, transforming the existing AI-Native Todo Application into a Cloud-Native, Kubernetes-deployable system. The new constitution establishes principles for infrastructure-first intelligence, container boundary integrity, secret management excellence, and AI-assisted operations compliance. It defines agent responsibilities for the DevOps Brain orchestrator and other specialized agents, as well as skill-governed capabilities for cloud-native deployment. The constitution maintains hard constraints preserving existing application logic while focusing solely on infrastructure intelligence.

## OUTCOME

The constitution has been successfully updated from version 2.0.0 to 3.0.0, reflecting the transition from Phase III (AI Chatbot) to Phase IV (Cloud-Native Infrastructure Intelligence). All infrastructure work must now follow the new principles and be generated through agents using defined skills.