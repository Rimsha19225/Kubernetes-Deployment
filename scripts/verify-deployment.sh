#!/bin/bash

# Script to verify the full deployment of the AI-Native Todo Application
# This script checks all components of the Kubernetes deployment

set -e  # Exit on any error

echo "=== AI-Native Todo Application Deployment Verification ==="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Verify Kubernetes cluster connection
echo "🔍 Verifying Kubernetes cluster connection..."
kubectl cluster-info > /dev/null 2>&1
echo "✅ Kubernetes cluster connection verified"

# Check for Helm release
RELEASE_NAME="todo-app"
echo "🔍 Checking for Helm release '$RELEASE_NAME'..."
HELM_STATUS=$(helm status "$RELEASE_NAME" 2>/dev/null || echo "not found")

if [[ "$HELM_STATUS" == *"not found"* ]]; then
    echo "❌ Helm release '$RELEASE_NAME' not found. Please install the chart first."
    echo "   Run: helm install todo-app helm/todo-chart/"
    exit 1
fi

echo "✅ Helm release '$RELEASE_NAME' found"

# Check all pods are running
echo "🔍 Checking pod status..."
PODS=$(kubectl get pods -l app.kubernetes.io/instance=todo-app -o json)
POD_COUNT=$(echo "$PODS" | jq '.items | length')

if [ "$POD_COUNT" -eq 0 ]; then
    echo "❌ No pods found with label 'app.kubernetes.io/instance=todo-app'"
    exit 1
fi

RUNNING_PODS=$(echo "$PODS" | jq '[.items[] | select(.status.phase == "Running")] | length')
if [ "$RUNNING_PODS" -ne "$POD_COUNT" ]; then
    echo "❌ Only $RUNNING_PODS out of $POD_COUNT pods are running"
    kubectl get pods -l app.kubernetes.io/instance=todo-app
    exit 1
fi

echo "✅ All $POD_COUNT pods are running"

# Check services
echo "🔍 Checking services..."
FRONTEND_SERVICE="${RELEASE_NAME}-frontend"
BACKEND_SERVICE="${RELEASE_NAME}-backend"

FRONTEND_EXISTS=$(kubectl get service "$FRONTEND_SERVICE" -o name 2>/dev/null || echo "not found")
BACKEND_EXISTS=$(kubectl get service "$BACKEND_SERVICE" -o name 2>/dev/null || echo "not found")

if [[ "$FRONTEND_EXISTS" == *"not found"* ]]; then
    echo "❌ Frontend service '$FRONTEND_SERVICE' not found"
    exit 1
fi

if [[ "$BACKEND_EXISTS" == *"not found"* ]]; then
    echo "❌ Backend service '$BACKEND_SERVICE' not found"
    exit 1
fi

echo "✅ Frontend and backend services exist"

# Check deployments
echo "🔍 Checking deployments..."
FRONTEND_DEPLOYMENT="${RELEASE_NAME}-frontend"
BACKEND_DEPLOYMENT="${RELEASE_NAME}-backend"

FRONTEND_DEPLOY_EXISTS=$(kubectl get deployment "$FRONTEND_DEPLOYMENT" -o name 2>/dev/null || echo "not found")
BACKEND_DEPLOY_EXISTS=$(kubectl get deployment "$BACKEND_DEPLOYMENT" -o name 2>/dev/null || echo "not found")

if [[ "$FRONTEND_DEPLOY_EXISTS" == *"not found"* ]]; then
    echo "❌ Frontend deployment '$FRONTEND_DEPLOYMENT' not found"
    exit 1
fi

if [[ "$BACKEND_DEPLOY_EXISTS" == *"not found"* ]]; then
    echo "❌ Backend deployment '$BACKEND_DEPLOYMENT' not found"
    exit 1
fi

echo "✅ Frontend and backend deployments exist"

# Check deployment statuses
FRONTEND_REPLICAS=$(kubectl get deployment "$FRONTEND_DEPLOYMENT" -o jsonpath='{.status.readyReplicas}')
FRONTEND_EXPECTED=$(kubectl get deployment "$FRONTEND_DEPLOYMENT" -o jsonpath='{.spec.replicas}')

BACKEND_REPLICAS=$(kubectl get deployment "$BACKEND_DEPLOYMENT" -o jsonpath='{.status.readyReplicas}')
BACKEND_EXPECTED=$(kubectl get deployment "$BACKEND_DEPLOYMENT" -o jsonpath='{.spec.replicas}')

if [ "$FRONTEND_REPLICAS" -ne "$FRONTEND_EXPECTED" ]; then
    echo "❌ Frontend deployment: $FRONTEND_REPLICAS/$FRONTEND_EXPECTED replicas ready"
    exit 1
fi

if [ "$BACKEND_REPLICAS" -ne "$BACKEND_EXPECTED" ]; then
    echo "❌ Backend deployment: $BACKEND_REPLICAS/$BACKEND_EXPECTED replicas ready"
    exit 1
fi

echo "✅ All deployments have expected replicas ready"

# Check ConfigMap and Secret exist
CONFIGMAP_NAME="${RELEASE_NAME}-config"
SECRET_NAME="${RELEASE_NAME}-secrets"

CONFIGMAP_EXISTS=$(kubectl get configmap "$CONFIGMAP_NAME" -o name 2>/dev/null || echo "not found")
SECRET_EXISTS=$(kubectl get secret "$SECRET_NAME" -o name 2>/dev/null || echo "not found")

if [[ "$CONFIGMAP_EXISTS" == *"not found"* ]]; then
    echo "❌ ConfigMap '$CONFIGMAP_NAME' not found"
    exit 1
fi

if [[ "$SECRET_EXISTS" == *"not found"* ]]; then
    echo "❌ Secret '$SECRET_NAME' not found"
    exit 1
fi

echo "✅ ConfigMap and Secret exist"

# Check if AI operations labels are present
echo "🔍 Checking AI operations labels..."

# Check if resources have ai-monitored label
AI_MONITORED_CONFIGMAP=$(kubectl get configmap "$CONFIGMAP_NAME" -o jsonpath='{.metadata.labels.ai-monitored}' 2>/dev/null)
AI_MONITORED_SECRET=$(kubectl get secret "$SECRET_NAME" -o jsonpath='{.metadata.labels.ai-monitored}' 2>/dev/null)
AI_MONITORED_FRONTEND_DEPLOY=$(kubectl get deployment "$FRONTEND_DEPLOYMENT" -o jsonpath='{.metadata.labels.ai-monitored}' 2>/dev/null)
AI_MONITORED_BACKEND_DEPLOY=$(kubectl get deployment "$BACKEND_DEPLOYMENT" -o jsonpath='{.metadata.labels.ai-monitored}' 2>/dev/null)

if [[ -z "$AI_MONITORED_CONFIGMAP" ]] || [[ "$AI_MONITORED_CONFIGMAP" != "true" ]]; then
    echo "⚠️  ConfigMap '$CONFIGMAP_NAME' missing or incorrect ai-monitored label: $AI_MONITORED_CONFIGMAP"
else
    echo "✅ ConfigMap has ai-monitored label"
fi

if [[ -z "$AI_MONITORED_SECRET" ]] || [[ "$AI_MONITORED_SECRET" != "true" ]]; then
    echo "⚠️  Secret '$SECRET_NAME' missing or incorrect ai-monitored label: $AI_MONITORED_SECRET"
else
    echo "✅ Secret has ai-monitored label"
fi

if [[ -z "$AI_MONITORED_FRONTEND_DEPLOY" ]] || [[ "$AI_MONITORED_FRONTEND_DEPLOY" != "true" ]]; then
    echo "⚠️  Frontend deployment missing or incorrect ai-monitored label: $AI_MONITORED_FRONTEND_DEPLOY"
else
    echo "✅ Frontend deployment has ai-monitored label"
fi

if [[ -z "$AI_MONITORED_BACKEND_DEPLOY" ]] || [[ "$AI_MONITORED_BACKEND_DEPLOY" != "true" ]]; then
    echo "⚠️  Backend deployment missing or incorrect ai-monitored label: $AI_MONITORED_BACKEND_DEPLOY"
else
    echo "✅ Backend deployment has ai-monitored label"
fi

# Summary
echo ""
echo "=== Deployment Verification Summary ==="
echo "✅ Helm release: $RELEASE_NAME"
echo "✅ Pods: $RUNNING_PODS/$POD_COUNT running"
echo "✅ Services: $FRONTEND_SERVICE, $BACKEND_SERVICE"
echo "✅ Deployments: $FRONTEND_DEPLOYMENT ($FRONTEND_REPLICAS/$FRONTEND_EXPECTED), $BACKEND_DEPLOYMENT ($BACKEND_REPLICAS/$BACKEND_EXPECTED)"
echo "✅ ConfigMap: $CONFIGMAP_NAME"
echo "✅ Secret: $SECRET_NAME"

echo ""
echo "🎉 The AI-Native Todo Application deployment is successfully verified!"
echo ""
echo "To access the application:"
echo "Frontend URL: $(kubectl get service $FRONTEND_SERVICE -o jsonpath='{.spec.type}' 2>/dev/null)/$(kubectl get service $FRONTEND_SERVICE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null)"
echo "Backend URL: $BACKEND_SERVICE:$(kubectl get service $BACKEND_SERVICE -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)"

echo ""
echo "For detailed status, run: kubectl get all -l app.kubernetes.io/instance=$RELEASE_NAME"