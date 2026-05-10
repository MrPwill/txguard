# GCP Project
data "google_project" "project" {
  project = var.project_id
}

# Artifact Registry - store container image
resource "google_artifact_registry_repository" "txguard" {
  location      = var.region
  repository_id = var.service_name
  description   = "TxGuard AI container images"
  format        = "DOCKER"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "txguard" {
  name     = var.service_name
  location = var.region

  template {
    service_account = google_service_account.txguard.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image
      ports {
        container_port = var.container_port
      }
      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }
      env {
        name  = "DATABASE_URL"
        value = google_sql_database_instance.txguard.connection_name
      }
      env {
        name  = "REDIS_URL"
        value = google_redis_instance.txguard.host
      }
      env {
        name  = "SECRET_KEY"
        value = google_secret_manager_secret.txguard.secret_id
      }
      env {
        name  = "CHROMA_PATH"
        value = "/tmp/chroma_db"
      }
      env {
        name  = "MODEL_DIR"
        value = "/app/ml/saved_models"
      }
      env {
        name  = "GOOG_API_KEY"
        value = var.openrouter_api_key
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    max_instance_request_concurrency = 80
    timeout                          = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  annotations = {
    "generated-by" = "terraform"
  }
}

# Cloud SQL - PostgreSQL 16
resource "google_sql_database_instance" "txguard" {
  database_version = "POSTGRES_16"
  name             = "${var.service_name}-db"
  region           = var.region

  delete_scheduled_protection = true

  settings {
    tier            = "db-f1-micro"
    region           = var.region
    availability_type = "REGIONAL"
    ip_configuration {
      ipv4_enabled = false
      private_network = google_compute_network.txguard.id
      require_ssl    = true
    }
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }
    maintenance_window {
      day  = 7
      hour = 4
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "txguard" {
  name     = "txguard"
  instance = google_sql_database_instance.txguard.name
}

resource "google_sql_user" "txguard" {
  name     = "postgres"
  instance = google_sql_database_instance.txguard.name
  password = var.db_password
}

# Memorystore - Redis 7
resource "google_redis_instance" "txguard" {
  name           = "${var.service_name}-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  redis_version  = "REDIS_7"

  connect_mode = "PRIVATE_SERVICE_CONNECT"
  authorized_network = google_compute_network.txguard.id
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  dynamic "auth" {
    for_each = var.redis_password != "" ? [""] : []
    content {
      satisfied = true
    }
  }
}

# VPC Network
resource "google_compute_network" "txguard" {
  name                    = "${var.service_name}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

resource "google_compute_subnetwork" "txguard" {
  name          = "${var.service_name}-subnet"
  network       = google_compute_network.txguard.id
  region        = var.region
  ip_cidr_range = "10.10.0.0/28"

  private_ip_google_access = true
}

# VPC Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "${var.service_name}-connector"
  region        = var.region
  network       = google_compute_network.txguard.name
  min_instances = 2
  max_instances = 10
  machine_type  = "e2-standard-2"
}

# Private Service Connect for Cloud SQL
resource "google_compute_global_address" "sql" {
  name          = "${var.service_name}-sql-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.txguard.id
  address       = "10.20.0.0"
}

resource "google_service_networking_connection" "sql_vpc" {
  network                 = google_compute_network.txguard.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges  = [google_compute_global_address.sql.name]
}

# Secret Manager for secrets
resource "google_secret_manager_secret" "txguard" {
  secret_id = "${var.service_name}-secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "txguard" {
  secret = google_secret_manager_secret.txguard.id
  secret_data = var.db_password
}

# Service Account for Cloud Run
resource "google_service_account" "txguard" {
  account_id = "${var.service_name}-sa"
  display_name = "TxGuard AI Service Account"
}

resource "google_project_iam_member" "txguard_runner" {
  project = var.project_id
  role    = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.txguard.email}"
}

resource "google_project_iam_member" "txguard_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member   = "serviceAccount:${google_service_account.txguard.email}"
}

resource "google_project_iam_member" "txguard_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member   = "serviceAccount:${google_service_account.txguard.email}"
}

resource "google_project_iam_member" "txguard_redis_accessor" {
  project = var.project_id
  role    = "roles/redis.viewer"
  member   = "serviceAccount:${google_service_account.txguard.email}"
}

resource "google_project_iam_member" "txguard_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member   = "serviceAccount:${google_service_account.txguard.email}"
}

# Cloud Run IAM - allow public access to /docs and /api
resource "google_cloud_run_v2_service_iam_member" "public" {
  location = var.region
  name     = google_cloud_run_v2_service.txguard.name
  role     = "roles/run.invoker"
  member   = "public"
}