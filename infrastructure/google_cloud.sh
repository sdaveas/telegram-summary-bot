#!/bin/bash

# Set your Google Cloud project ID
PROJECT_ID="telegram-summary-bot-432903"
SERVICE_NAME="telegram-summary-bot"

# Set your image name and tag
IMAGE_NAME="telegram-summary-bot"
IMAGE_TAG="v1"

# Source the environment variables
if [ -f .env ]; then
    source .env
else
    echo ".env file not found"
    exit 1
fi

# Build your Docker image
docker buildx build -t $IMAGE_NAME:$IMAGE_TAG --platform "linux/amd64" .

# Configure Docker to use Google Container Registry
gcloud auth configure-docker

# Tag your image for Google Container Registry
docker tag $IMAGE_NAME:$IMAGE_TAG gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG

# Push your image to Google Container Registry
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG

# Deploy to Cloud Run
gcloud run deploy \
--platform managed \
--image gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG \
--port 8443 \
--region europe-central2 \
--allow-unauthenticated \
--set-env-vars TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN",ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY",DATABASE_PATH="$DATABASE_PATH",WEBHOOK_HOST="$WEBHOOK_HOST"


echo "Creating a new bucket for the deployment"
gcloud beta run services update $SERVICE_NAME \
    --region europe-central2 \
    --add-volume name=telegram-summary-bot-database,type=cloud-storage,bucket=telegram-summary-bot-database \
    --add-volume-mount volume=telegram-summary-bot-database,mount-path=/app/database

echo "Deployment complete. Check the Google Cloud Console for your app's URL."