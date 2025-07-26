#!/bin/bash
# simple_deploy.sh - Simple deployment script for Google Cloud Run

set -e

PROJECT_ID="stash-467107"
SERVICE_NAME="stash-api"
REGION="us-central1"

echo "🚀 Deploying Stash API to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Step 1: Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com --project=$PROJECT_ID

# Step 2: Grant service account access to secrets
echo "🔐 Granting service account access to secrets..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:stash-api-service@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" --quiet

# Step 3: Wait for Secret Manager API to be ready
echo "⏳ Waiting for Secret Manager API to be ready..."
sleep 30

# Step 4: Create secrets
echo "🔑 Creating secrets in Secret Manager..."

# Read values from .env file
GENAI_API_KEY=$(grep "^GENAI_API_KEY=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')
SECRET_KEY=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')
JWT_SECRET_KEY=$(grep "^JWT_SECRET_KEY=" .env | head -1 | cut -d'=' -f2 | sed 's/^"//;s/"$//')
WEBHOOK_SECRET=$(grep "^WEBHOOK_SECRET=" .env | cut -d'=' -f2 | sed 's/^"//;s/"$//')

# Create secrets (suppress error if already exists)
echo "$GENAI_API_KEY" | gcloud secrets create genai-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$GENAI_API_KEY" | gcloud secrets versions add genai-api-key --data-file=- --project=$PROJECT_ID

echo "$SECRET_KEY" | gcloud secrets create stash-secret-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$SECRET_KEY" | gcloud secrets versions add stash-secret-key --data-file=- --project=$PROJECT_ID

echo "$JWT_SECRET_KEY" | gcloud secrets create jwt-secret-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$JWT_SECRET_KEY" | gcloud secrets versions add jwt-secret-key --data-file=- --project=$PROJECT_ID

echo "$WEBHOOK_SECRET" | gcloud secrets create webhook-secret --data-file=- --project=$PROJECT_ID 2>/dev/null || \
echo "$WEBHOOK_SECRET" | gcloud secrets versions add webhook-secret --data-file=- --project=$PROJECT_ID

echo "✅ Secrets created/updated successfully"

# Step 5: Build container image
echo "🏗️  Building container image..."
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME} --project=$PROJECT_ID

# Step 6: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
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
    --service-account "stash-api-service@${PROJECT_ID}.iam.gserviceaccount.com" \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},FIRESTORE_PROJECT_ID=${PROJECT_ID},GCLOUD_STORAGE_BUCKET=stash_bucket_1,DEBUG=false,ENVIRONMENT=production,GENAI_MODEL=gemini-pro,POINTS_PER_RECEIPT=10,GAMIFICATION_ENABLED=true,VISION_API_ENABLED=true" \
    --set-secrets "GENAI_API_KEY=genai-api-key:latest,SECRET_KEY=stash-secret-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,WEBHOOK_SECRET=webhook-secret:latest"

# Step 7: Get service URL and test
echo ""
echo "🎉 Deployment completed!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo "📍 Service URL: $SERVICE_URL"

echo ""
echo "🧪 Testing deployment..."
echo "Testing health endpoint..."
if curl -f -s "${SERVICE_URL}/health" > /dev/null; then
    echo "✅ Health check passed"
    echo "Testing dummy data upload..."
    if curl -f -s -X POST "${SERVICE_URL}/test/upload-dummy-receipt" > /dev/null; then
        echo "✅ Dummy data upload successful"
        echo ""
        echo "🎯 Deployment successful! Your API is live at:"
        echo "   $SERVICE_URL"
        echo ""
        echo "📋 Available endpoints:"
        echo "   • Health: ${SERVICE_URL}/health"
        echo "   • API Docs: ${SERVICE_URL}/docs"
        echo "   • Test Upload: ${SERVICE_URL}/test/upload-dummy-receipt"
    else
        echo "⚠️  Dummy data upload failed - check logs"
    fi
else
    echo "❌ Health check failed - check logs"
fi

echo ""
echo "📊 To view logs:"
echo "gcloud logs tail \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --project=${PROJECT_ID}"
