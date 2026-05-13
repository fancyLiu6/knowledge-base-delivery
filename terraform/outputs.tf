output "app_url" {
  description = "博客访问地址"
  value       = "http://localhost:${var.app_port}"
}

output "health_check_url" {
  description = "健康检查端点"
  value       = "http://localhost:${var.app_port}/health"
}

output "metrics_url" {
  description = "Nginx Exporter 指标端点"
  value       = "http://localhost:${var.metrics_port}/metrics"
}

output "container_names" {
  description = "运行的容器名称"
  value = [
    docker_container.knowledge_base.name,
    docker_container.nginx_exporter.name
  ]
}
