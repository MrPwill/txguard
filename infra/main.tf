terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  backend "local" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "image" {
  description = "Container image URL (gcr.io/project/image:tag)"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openrouter_api_key" {
  description = "OpenRouter API key for CrewAI"
  type        = string
  default     = ""
  sensitive   = true
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "txguard"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "memory" {
  description = "Memory allocation (e.g. 1Gi, 2Gi)"
  type        = string
  default     = "1Gi"
}

variable "cpu" {
  description = "CPU allocation (e.g. 1, 2)"
  type        = string
  default     = "1"
}

variable "min_instances" {
  description = "Minimum instance count"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instance count"
  type        = number
  default     = 3
}

data "google_project" "project" {
  project = var.project_id
}

output "service_url" {
  value       = google_cloud_run_v2_service.txguard.uri
  description = "TxGuard Cloud Run service URL"
}

output "api_docs_url" {
  value       = "${google_cloud_run_v2_service.txguard.uri}/docs"
  description = "FastAPI OpenAPI documentation URL"
}