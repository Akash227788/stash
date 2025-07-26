#!/bin/bash
# deploy_to_cloud_run.sh - Deploy Stash API to Google Cloud Run with environment variables

set -e  # Exit on any error

echo "🚀 Deploying Stash API to Google Cloud Run"
echo "=" * 50

# Configuration
PROJECT_ID="stash-467107"
SERVICE_NAME="stash-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Load environment variables from .env file
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

echo "📋 Loading environment variables from .env file..."

# Create env-vars.yaml for Cloud Run deployment
echo "🔧 Creating Cloud Run environment variables configuration..."

cat > env-vars.yaml << 'EOF'
# Cloud Run Environment Variables
# Generated from .env file
apiVersion: v1
kind: ConfigMap
metadata:
  name: stash-env-vars
data:
EOF

# Parse .env file and convert to Cloud Run format
ENV_VARS=""
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Extract key-value pairs
    if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        
        # Remove quotes from value
        value=$(echo "$value" | sed 's/^"//;s/"$//')
        
        # Skip sensitive credentials that will be set via Secret Manager
        if [[ "$key" =~ (GOOGLE_APPLICATION_CREDENTIALS|SECRET_KEY|JWT_SECRET_KEY|WEBHOOK_SECRET|GENAI_API_KEY) ]]; then
            echo "⚠️  Skipping sensitive variable: $key (will be set via Secret Manager)"
            continue
        fi
        
        # Add to env vars string
        if [ -n "$ENV_VARS" ]; then
            ENV_VARS="${ENV_VARS},"
        fi
        ENV_VARS="${ENV_VARS}${key}=${value}"
        
        echo "✅ Added: $key"
    fi
done < .env

echo ""
echo "🔒 Setting up Secret Manager for sensitive data..."

# Create secrets in Secret Manager for sensitive data
echo "Creating secrets for sensitive environment variables..."

# Extract sensitive variables from .env
GENAI_API_KEY=$(grep "^GENAI_API_KEY=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')
SECRET_KEY=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')
JWT_SECRET_KEY=$(grep "^JWT_SECRET_KEY=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')
WEBHOOK_SECRET=$(grep "^WEBHOOK_SECRET=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')

# Create or update secrets
if [ -n "$GENAI_API_KEY" ]; then
    echo "$GENAI_API_KEY" | gcloud secrets create genai-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$GENAI_API_KEY" | gcloud secrets versions add genai-api-key --data-file=- --project=$PROJECT_ID
    echo "✅ Created/Updated secret: genai-api-key"
fi

if [ -n "$SECRET_KEY" ]; then
    echo "$SECRET_KEY" | gcloud secrets create stash-secret-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$SECRET_KEY" | gcloud secrets versions add stash-secret-key --data-file=- --project=$PROJECT_ID
    echo "✅ Created/Updated secret: stash-secret-key"
fi

if [ -n "$JWT_SECRET_KEY" ]; then
    echo "$JWT_SECRET_KEY" | gcloud secrets create jwt-secret-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$JWT_SECRET_KEY" | gcloud secrets versions add jwt-secret-key --data-file=- --project=$PROJECT_ID
    echo "✅ Created/Updated secret: jwt-secret-key"
fi

if [ -n "$WEBHOOK_SECRET" ]; then
    echo "$WEBHOOK_SECRET" | gcloud secrets create webhook-secret --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$WEBHOOK_SECRET" | gcloud secrets versions add webhook-secret --data-file=- --project=$PROJECT_ID
    echo "✅ Created/Updated secret: webhook-secret"
fi

echo ""
echo "🏗️  Building and deploying to Cloud Run..."

# Build the container image
echo "Building container image..."
gcloud builds submit --tag $IMAGE_NAME --project=$PROJECT_ID

# Deploy to Cloud Run with environment variables and secrets
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 100 \
    --min-instances 0 \
    --timeout 300 \
    --concurrency 80 \
    --service-account "stash-api-service@${PROJECT_ID}.iam.gserviceaccount.com" \
    --set-env-vars "$ENV_VARS" \
    --set-secrets "GENAI_API_KEY=genai-api-key:latest,SECRET_KEY=stash-secret-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,WEBHOOK_SECRET=webhook-secret:latest"

echo ""
echo "🎉 Deployment complete!"
echo "📍 Service URL: https://${SERVICE_NAME}-$(echo $REGION | tr '-' '')${PROJECT_ID}.a.run.app"
echo "🔗 You can also find the URL in the Cloud Console: https://console.cloud.google.com/run"

echo ""
echo "🧪 Testing deployment..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo "Testing health endpoint: ${SERVICE_URL}/health"
curl -s "${SERVICE_URL}/health" | python3 -m json.tool || echo "❌ Health check failed"

echo ""
echo "✅ Deployment process completed!"
EOF

chmod +x deploy_to_cloud_run.sh
