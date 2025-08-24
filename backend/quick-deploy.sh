#!/bin/bash

# Quick Azure Container Deployment Script
# Usage: ./quick-deploy.sh "mongodb_url" "openai_api_key"

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 \"mongodb_url\" \"openai_api_key\""
    echo "Example: $0 \"mongodb+srv://user:pass@cluster.mongodb.net/\" \"sk-...\""
    exit 1
fi

MONGODB_URL="$1"
OPENAI_API_KEY="$2"

# Configuration
APP_NAME="travel-agent-api"
RESOURCE_GROUP="travel-agent-rg"
LOCATION="centralindia"
SUBSCRIPTION_ID="effd4b2e-98eb-48c1-ad07-ad597a94c754"
ACR_NAME="travelagentreg$(date +%s | tail -c 6)"
IMAGE_TAG="latest"

echo "🚀 Quick deployment starting..."

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

# Create ACR
echo "🏭 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --location $LOCATION --output table
az acr update -n $ACR_NAME --admin-enabled true

# Get ACR details
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# Build and push
echo "🔨 Building and pushing Docker image..."
az acr login --name $ACR_NAME
docker build -t $ACR_SERVER/$APP_NAME:$IMAGE_TAG .
docker push $ACR_SERVER/$APP_NAME:$IMAGE_TAG

# Deploy
echo "🚀 Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $ACR_SERVER/$APP_NAME:$IMAGE_TAG \
    --registry-login-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $APP_NAME-$(date +%s | tail -c 6) \
    --ports 8000 \
    --cpu 1 \
    --memory 2 \
    --environment-variables \
        MONGODB_URL="$MONGODB_URL" \
        OPENAI_API_KEY="$OPENAI_API_KEY" \
        DATABASE_NAME="travel_agent" \
        API_V1_STR="/api/v1" \
        DEBUG="false" \
        LOG_LEVEL="info" \
    --output table

# Get URL and test
CONTAINER_URL=$(az container show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "ipAddress.fqdn" --output tsv)
echo "🌐 Container URL: http://$CONTAINER_URL:8000"

echo "⏳ Waiting for container to start..."
sleep 45

# Test endpoints
echo "🏥 Testing health endpoint..."
curl -f "http://$CONTAINER_URL:8000/api/v1/health/" | jq . && echo "✅ Health check passed!" || echo "❌ Health check failed!"

echo "🚀 Testing readiness endpoint..."
curl -f "http://$CONTAINER_URL:8000/api/v1/health/ready" | jq . && echo "✅ Readiness check passed!" || echo "❌ Readiness check failed!"

echo "💬 Testing chat endpoint..."
curl -X POST "http://$CONTAINER_URL:8000/api/v1/chat/message" \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, test message", "session_id": "test-123"}' | jq . && echo "✅ Chat test passed!" || echo "❌ Chat test failed!"

echo ""
echo "🎉 Deployment Complete!"
echo "URL: http://$CONTAINER_URL:8000"
echo "Docs: http://$CONTAINER_URL:8000/docs"
echo "Health: http://$CONTAINER_URL:8000/api/v1/health/"
echo ""
echo "To delete: az group delete --name $RESOURCE_GROUP --yes --no-wait"
