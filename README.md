# Stash - Gamified AI Receipt Management System

This project is a backend for a gamified AI-powered receipt management system. It's built as a multi-agent system using FastAPI and designed to be deployable on Google Cloud Run, utilizing various Google Cloud services.

## Features

*   **Receipt Processing**: Upload receipt images and extract information like merchant, items, and total using Cloud Vision AI and a Generative AI model.
*   **Financial Analytics**: Get spending reports and insights based on your processed receipts.
*   **Gamification**: Earn points for uploading receipts.
*   **Digital Wallet**: View your point balance.
*   **Scalable Architecture**: Built with a multi-agent approach and deployed as a serverless application on Cloud Run.

## Architecture

This project is designed as a multi-agent system where each agent has a specific responsibility. The agents are implemented as FastAPI routers.

*   **Root Agent**: The entry point of the application, provides a welcome message.
*   **Receipt Agent**: Handles receipt processing. It uses Cloud Storage to store the receipt images, Cloud Vision AI to extract text from the images, and a Generative AI model to parse the text and extract the relevant information. It then stores the processed receipt data in Firestore and publishes a message to a Pub/Sub topic.
*   **Analytics Agent**: Provides financial insights. It reads receipt data from Firestore and uses a Generative AI model to generate spending reports.
*   **Game Agent**: Handles the gamification logic. It awards points to users for uploading receipts and updates the user's points in Firestore.
*   **Wallet Agent**: Manages the user's digital wallet. It can retrieve the user's point balance from Firestore.

The entire application is designed to be deployed as a single service on Cloud Run, which communicates with other Google Cloud services.

## Prerequisites

Before you can deploy this project, you need to have the following:

*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured.
*   A Google Cloud project with billing enabled.
*   The `gcloud` command-line tool authenticated with your Google Cloud account.

## Deployment to Google Cloud

Follow these steps to deploy the project to Google Cloud:

### 1. Set up your Google Cloud Project

First, set your project ID in the gcloud CLI:

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

Enable the necessary APIs for the project to function:

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    firestore.googleapis.com \
    pubsub.googleapis.com \
    vision.googleapis.com \
    iam.googleapis.com \
    aiplatform.googleapis.com
```

### 3. Create a Service Account

Create a dedicated service account for the Cloud Run service to interact with other Google Cloud services securely.

```bash
gcloud iam service-accounts create stash-api-runner \
    --description="Service account for Stash API on Cloud Run" \
    --display-name="Stash API Runner"
```

### 4. Grant Permissions to the Service Account

Grant the necessary IAM roles to the service account:

```bash
# Role for Cloud Run
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# Role for Cloud Storage
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Role for Firestore
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Role for Pub/Sub
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# Role for Vision AI
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/vision.user"

# Role for Generative AI (Vertex AI)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:stash-api-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### 5. Create a Google Cloud Storage Bucket

Create a bucket to store the receipt images. Make sure the bucket name is globally unique.

```bash
gsutil mb gs://your-unique-bucket-name
```

### 6. Set Up Environment Variables

Create a `.env` file by copying the `.env.example` file:

```bash
cp .env.example .env
```

Now, edit the `.env` file and replace the placeholder values with your actual configuration:

```
GENAI_API_KEY="your-google-ai-api-key"
GCLOUD_STORAGE_BUCKET="your-unique-bucket-name"
FIRESTORE_PROJECT_ID="your-gcp-project-id"
```

### 7. Deploy to Cloud Run

Run the deployment script:

```bash
./cloud_run.sh
```

This script will use Cloud Build to build the Docker image, push it to Google Container Registry, and deploy it to Cloud Run.

## API Endpoints

Once deployed, you can interact with the API at the URL provided by Cloud Run.

*   `GET /`: Welcome message.
*   `POST /receipt/process-receipt`: Process a receipt image.
    *   **Body**: `{ "imageUrl": "gs://your-bucket/image.jpg", "userId": "user123" }`
*   `GET /analytics/spending-report/{user_id}`: Get a spending report for a user.
*   `POST /game/award-points`: Award points to a user.
    *   **Body**: `{ "userId": "user123", "receiptId": "receipt456" }`
*   `GET /wallet/balance/{user_id}`: Get the point balance for a user.

## Local Development

To run the application locally, follow these steps:

1.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Application Default Credentials (ADC)** for local authentication:
    ```bash
    gcloud auth application-default login
    ```

4.  **Run the development server**:
    ```bash
    ./devserver.sh
    ```

The application will be available at `http://127.0.0.1:8080`.
