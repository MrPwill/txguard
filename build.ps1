@echo off
REM Build and push TxGuard Docker image to Google Container Registry
REM Usage: build.ps1 -ProjectId "my-gcp-project" -Region "us-central1" -ImageTag "latest"

param(
    [string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

if (-not $ProjectId) {
    Write-Host "Usage: build.ps1 -ProjectId YOUR_PROJECT_ID [-Region us-central1] [-ImageTag latest]"
    exit 1
}

$IMAGE = "gcr.io/$ProjectId/txguard:$ImageTag"

Write-Host "Building TxGuard container image..." -ForegroundColor Cyan
docker build -t txguard:latest -f Dockerfile .

Write-Host "Tagging image as $IMAGE..." -ForegroundColor Cyan
docker tag txguard:latest $IMAGE

Write-Host "Pushing to Artifact Registry..." -ForegroundColor Cyan
gcloud auth configure-docker $Region-docker.pkg.dev
docker push $IMAGE

Write-Host ""
Write-Host "Image pushed successfully: $IMAGE" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Deploy with Terraform:" -ForegroundColor White
Write-Host "     cd infra" -ForegroundColor Gray
Write-Host "     terraform init" -ForegroundColor Gray
Write-Host "     terraform apply -var='project_id=$ProjectId' -var='image=$IMAGE' -var='db_password=YOUR_STRONG_PASSWORD'" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Or deploy directly with gcloud:" -ForegroundColor White
Write-Host "     gcloud run deploy txguard --image=$IMAGE --region=$Region --platform=managed" -ForegroundColor Gray