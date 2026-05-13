# ============================================
# Knowledge Base Blog - Terraform IaC
# 等价于 docker-compose.yml 的 Terraform 版本
#
# 用法:
#   terraform init
#   terraform plan
#   terraform apply -auto-approve
#   terraform destroy
# ============================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

# Docker provider
provider "docker" {}

# ---- Docker Network ----
resource "docker_network" "app" {
  name = "knowledge-base-net"
}

# ---- Knowledge Base 容器 ----
resource "docker_image" "knowledge_base" {
  name = "knowledge-base:latest"
  build {
    context    = "${path.module}/.."
    dockerfile = "Dockerfile"
  }
  keep_locally = true
}

resource "docker_container" "knowledge_base" {
  name  = "knowledge-base"
  image = docker_image.knowledge_base.image_id

  ports {
    internal = 80
    external = var.app_port
  }

  networks_advanced {
    name = docker_network.app.name
  }

  healthcheck {
    test     = ["CMD", "wget", "-qO-", "http://localhost/health"]
    interval = "30s"
    timeout  = "3s"
    retries  = 3
  }

  restart = "always"

  labels {
    label = "app"
    value = "knowledge-base"
  }
}

# ---- Nginx Exporter ----
resource "docker_container" "nginx_exporter" {
  name  = "nginx-exporter"
  image = "nginx/nginx-prometheus-exporter:1.1.0"

  command = [
    "-nginx.scrape-uri=http://knowledge-base:80/nginx_status"
  ]

  ports {
    internal = 9113
    external = var.metrics_port
  }

  networks_advanced {
    name = docker_network.app.name
  }

  restart = "always"

  depends_on = [docker_container.knowledge_base]
}
