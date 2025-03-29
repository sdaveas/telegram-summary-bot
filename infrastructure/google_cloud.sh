#!/bin/bash

# Set your Google Cloud project ID
PROJECT_NUMBER=479511119155
PROJECT_ID="telegram-summary-bot-432903"
SERVICE_NAME="telegram-summary-bot-test"
REGION="europe-southwest1"
ENV_DIR=".env"

load_env_vars() {
    local env_file=$ENV_DIR
    if [[ -f "$env_file" ]]; then
        export $(grep -v '^#' "$env_file" | xargs)
    else
        echo "No .env file found."
    fi
}

log_in() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q '@'; then
        echo "Not logged in. Authenticating..."
        gcloud auth login
    else
        echo "Already logged in as $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
    fi
}

enable_service_if_needed() {
  local service=$1
  
  if ! gcloud services list --enabled --filter="name:$service" --quiet | grep -q "$service"; then
    echo "Enabling $service..."
    gcloud services enable "$service"
  else
    echo "$service is already enabled."
  fi
}

grant_secret_access_if_needed() {
  local project_number=$1
  local service_account="${project_number}-compute@developer.gserviceaccount.com"
  local role="roles/secretmanager.secretAccessor"
  
  echo "Checking if service account has Secret Manager access..."
  
  # Check if the role is already assigned
  if gcloud projects get-iam-policy $project_number --format="json" | \
     jq -e --arg sa "serviceAccount:$service_account" --arg role "$role" \
     '.bindings[] | select(.role == $role) | .members[] | select(. == $sa)' > /dev/null 2>&1; then
    echo "Service account already has Secret Manager access."
  else
    echo "Granting Secret Manager access to service account..."
    gcloud projects add-iam-policy-binding $project_number \
      --member="serviceAccount:$service_account" \
      --role="$role" > /dev/null
    echo "Access granted successfully."
  fi
}

manage_secret() {
  local secret_name=$1
  local secret_value=$2
  
  # Check if secret exists
  if gcloud secrets describe "$secret_name"; then
    echo "Updating secret: $secret_name"
    echo -n "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=-
  else
    echo "Creating secret: $secret_name"
    echo -n "$secret_value" | gcloud secrets create "$secret_name" --data-file=-
  fi
}

load_env_vars

log_in

gcloud config set project "$PROJECT_ID"
gcloud config set run/region "$REGION"

enable_service_if_needed "cloudbuild.googleapis.com"
enable_service_if_needed "run.googleapis.com"
enable_service_if_needed "secretmanager.googleapis.com"

manage_secret ANTHROPIC_API_KEY "$ANTHROPIC_API_KEY"
manage_secret TELEGRAM_BOT_TOKEN "$TELEGRAM_BOT_TOKEN"

grant_secret_access_if_needed $PROJECT_NUMBER

# TODO: Check if the bucket exists
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --port 8443 \
  --allow-unauthenticated \
  --set-secrets=ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest \
  --set-secrets=TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest \
  --set-env-vars DATABASE_PATH="$DATABASE_PATH",WEBHOOK_HOST="$WEBHOOK_HOST" \
  --add-volume name=messages,type=cloud-storage,bucket=telegram-summary-bot-database \
  --add-volume-mount volume=messages,mount-path=/app/database
