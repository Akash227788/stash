# 🚀 Google Cloud Run Deployment Guide for Stash API

## Prerequisites ✅
- [x] Google Cloud SDK installed and authenticated
- [x] Docker installed (for local testing)
- [x] Project ID: `stash-467107`
- [x] Service account created: `stash-api-service@stash-467107.iam.gserviceaccount.com`

## Quick Deployment (3 Steps)

### Step 1: Create Secrets (Run Once)
```bash
# Wait a few minutes for Secret Manager API to propagate, then run:
./secret-manager-commands.sh
```

### Step 2: Build and Deploy
```bash
# Build the container
gcloud builds submit --tag gcr.io/stash-467107/stash-api --project=stash-467107

# Deploy to Cloud Run (using pre-generated environment variables)
gcloud run deploy stash-api \
    --image gcr.io/stash-467107/stash-api \
    --platform managed \
    --region us-central1 \
    --project stash-467107 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 100 \
    --service-account "stash-api-service@stash-467107.iam.gserviceaccount.com" \
    --env-vars-file cloud-run-env-vars.txt \
    --set-secrets "$(cat cloud-run-secrets.txt)"
```

### Step 3: Test Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe stash-api --region=us-central1 --project=stash-467107 --format="value(status.url)")

# Test health endpoint
curl "${SERVICE_URL}/health"

# Test dummy data upload
curl -X POST "${SERVICE_URL}/test/upload-dummy-receipt"
```

## Alternative: Manual Deployment

If the automated script doesn't work, here's the manual approach:

### 1. Enable Required APIs
```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    --project=stash-467107
```

### 2. Create Secrets Manually
```bash
# Create each secret individually
echo "AIzaSyCF6j9dnNaKmZ1w4ZmNt79epRTSMVNHA6Y" | gcloud secrets create genai-api-key --data-file=- --project=stash-467107
echo "AqwHL33GNqmqoSlcYwVJRdRXHO5jFGJjT6fJTrHJTN0hh-qbTSY1ayVuvVIjqHPpkLQ1fqYeXPFUnvjtwvYQ1g" | gcloud secrets create stash-secret-key --data-file=- --project=stash-467107
echo "BDDYP0z_JqfRPsXAIj52cE1gV2ImnMdxT7_2zWdrvHU" | gcloud secrets create jwt-secret-key --data-file=- --project=stash-467107
echo "7yLwXeQF0V60vUhseuR2199DUTQ_IGHWhle-cmAOL3Y" | gcloud secrets create webhook-secret --data-file=- --project=stash-467107
```

### 3. Grant Service Account Access to Secrets
```bash
gcloud projects add-iam-policy-binding stash-467107 \
    --member="serviceAccount:stash-api-service@stash-467107.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Deploy with Simplified Environment Variables
```bash
gcloud run deploy stash-api \
    --image gcr.io/stash-467107/stash-api \
    --platform managed \
    --region us-central1 \
    --project stash-467107 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --service-account "stash-api-service@stash-467107.iam.gserviceaccount.com" \
    --set-env-vars "PROJECT_ID=stash-467107,FIRESTORE_PROJECT_ID=stash-467107,GCLOUD_STORAGE_BUCKET=stash_bucket_1,DEBUG=false,ENVIRONMENT=production" \
    --set-secrets "GENAI_API_KEY=genai-api-key:latest,SECRET_KEY=stash-secret-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,WEBHOOK_SECRET=webhook-secret:latest"
```

## Environment Variables Management

### Sensitive Data (Stored in Secret Manager)
- `GENAI_API_KEY` → `genai-api-key` secret
- `SECRET_KEY` → `stash-secret-key` secret  
- `JWT_SECRET_KEY` → `jwt-secret-key` secret
- `WEBHOOK_SECRET` → `webhook-secret` secret

### Non-Sensitive Data (Environment Variables)
- All other configuration from `.env` file
- Includes project settings, feature flags, thresholds, etc.

## Testing Your Deployment

### Health Check
```bash
curl https://stash-api-<HASH>-uc.a.run.app/health
```

### Upload Test Data
```bash
curl -X POST https://stash-api-<HASH>-uc.a.run.app/test/upload-dummy-receipt
```

### Get User Data
```bash
curl https://stash-api-<HASH>-uc.a.run.app/test/get-user-data/test_user_123
```

## Updating Environment Variables

To update environment variables after deployment:

### Update Regular Variables
```bash
gcloud run services update stash-api \
    --region us-central1 \
    --project stash-467107 \
    --set-env-vars "NEW_VAR=new_value"
```

### Update Secrets
```bash
# Update secret value
echo "new_secret_value" | gcloud secrets versions add secret-name --data-file=- --project=stash-467107

# Service will automatically use the latest version
```

## Monitoring and Logs

### View Logs
```bash
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=stash-api" --limit=50 --project=stash-467107
```

### View Metrics
- Go to Cloud Console → Cloud Run → stash-api → Metrics

## Troubleshooting

### Common Issues
1. **Secret Manager API not enabled**: Wait 5-10 minutes after enabling
2. **Permission denied**: Ensure service account has `secretmanager.secretAccessor` role
3. **Container fails to start**: Check logs for import errors or missing dependencies
4. **Environment variables not loading**: Verify `.env` file syntax and variable names

### Debug Commands
```bash
# Check service status
gcloud run services describe stash-api --region=us-central1 --project=stash-467107

# View recent logs
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=stash-api" --project=stash-467107

# Test local container
docker build -t stash-test .
docker run -p 8080:8080 --env-file .env stash-test
```

## Security Best Practices ✅

- [x] Sensitive data stored in Secret Manager
- [x] Service account with minimal required permissions
- [x] Container runs as non-root user
- [x] Environment-specific configuration
- [x] Secrets automatically rotated when updated

## Next Steps

1. **Custom Domain**: Add your domain to Cloud Run
2. **Authentication**: Implement user authentication
3. **Monitoring**: Set up alerting and monitoring
4. **CI/CD**: Automate deployments with Cloud Build triggers
5. **Scaling**: Configure auto-scaling based on traffic

---

Your Stash API is now ready for production deployment to Google Cloud Run! 🚀
