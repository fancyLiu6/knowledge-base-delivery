# ---- 应用端口 ----
variable "app_port" {
  description = "Knowledge Base 对外端口"
  type        = number
  default     = 8080
}

# ---- 监控指标端口 ----
variable "metrics_port" {
  description = "Nginx Exporter 对外端口"
  type        = number
  default     = 9113
}
