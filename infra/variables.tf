variable "project_id" {
  description = "GCP Project ID for deployment"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "image" {
  description = "Container image (gcr.io/PROJECT/IMAGE:TAG)"
  type        = string
}

variable "db_password" {
  description = "Cloud SQL PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Memorystore Redis password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openrouter_api_key" {
  description = "OpenRouter API key for CrewAI agents"
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
  description = "Memory limit (e.g. 1Gi)"
  type        = string
  default     = "1Gi"
}

variable "cpu" {
  description = "CPU count (e.g. 1)"
  type        = string
  default     = "1"
}

variable "min_instances" {
  description = "Minimum Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 3
}