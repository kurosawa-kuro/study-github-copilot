# 既存インフラ。今回のチュートリアルでは触らない前提。
# Step 0-C で「IaC は変更しない」と前提固定すること。

terraform {
  required_version = ">= 1.7"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
  backend "gcs" {
    bucket = "myapi-tfstate-dev"
    prefix = "envs/dev"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-northeast1"
}

resource "google_redis_instance" "cache" {
  name           = "myapi-cache-dev"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  redis_version  = "REDIS_7_0"
  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
}

resource "google_cloud_run_v2_service" "api" {
  name     = "myapi-dev"
  location = var.region
  template {
    containers {
      image = "asia-northeast1-docker.pkg.dev/${var.project_id}/myapi/api:latest"
      env {
        name  = "MYAPI_REDIS_HOST"
        value = google_redis_instance.cache.host
      }
    }
  }
}
