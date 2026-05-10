#!/bin/bash
# Build and push TxGuard Docker image to Google Artifact Registry
# Usage: ./build.sh [-p PROJECT_ID] [-r REGION] [-t IMAGE_TAG]

set -e

PROJECT_ID=""
REGION="us-central1"
IMAGE_TAG="latest"

while getopts "p:r:t:" opt; do
  case $opt in
    p) PROJECT_ID="$OPTARG" ;;
    r) REGION="$OPTARG" ;;
    t) IMAGE_TAG="$OPTARG" ;;
    *) echo "Usage: $0 -p PROJECT_ID [-r REGION] [-t IMAGE_TAG]"; exit 1 ;;
  esac
done

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 -p PROJECT_ID [-r REGION] [-t IMAGE_TAG]"
  echo "Example: $0 -p my-gcp-project -r us-central1 -t v1.0.0"
  exit 1
fi

IMAGE="gcr.io/$PROJECT_ID/txguard:$IMAGE_TAG"

echo "Building TxGuard container image..."
docker build -t txguard:latest -f Dockerfile .

echo "Tagging image as $IMAGE..."
docker tag txguard:latest $IMAGE

echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

echo "Pushing to Artifact Registry..."
docker push $IMAGE

echo ""
echo "Image pushed: $IMAGE"
echo ""
echo "Deploy with Terraform:"
echo "  cd infra"
echo "  terraform init"
echo "  terraform apply -var='project_id=$PROJECT_ID' -var='image=$IMAGE' -var='db_password=YOUR_PASSWORD'"
echo ""
echo "Or directly with gcloud:"
echo "  gcloud run deploy txguard --image=$IMAGE --region=$REGION --platform=managed"