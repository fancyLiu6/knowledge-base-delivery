# Knowledge Base Delivery System

> 基于 Docker + Nginx 的云原生知识库交付系统，搭配完整的可观测性与服务自愈能力。

---

## 项目简介

本项目将一个纯前端 SPA 知识库系统进行了完整的容器化与可观测性建设，覆盖以下 SRE 核心能力：

- **容器化与多阶段构建**：基于 `nginx:1.25-alpine` 构建轻量镜像
- **Nginx 网关治理**：Gzip 压缩、SPA 路由兜底、安全头、JSON 日志
- **监控与告警**：Prometheus + Grafana 全链路监控，含 QPS / 延迟 / 错误率面板
- **健康检查与自愈**：`/health` 探活端点 + Docker restart policy 进程级自愈
- **Kubernetes 部署**：完整的 Deployment / Service / ServiceMonitor 声明

## 快速开始

### 1. 本地 Docker 运行

```bash
# 构建镜像
docker build -t knowledge-base:latest .

# 启动容器
docker run -d -p 8080:80 --name knowledge-base knowledge-base:latest

# 验证
curl http://localhost:8080
curl http://localhost:8080/health
```

### 2. Docker Compose 一键启动（本地监控套件）

```bash
# 启动全套：前端 + Prometheus + Grafana
docker-compose up -d

# 访问
#   知识库: http://localhost:8080
#   Prometheus: http://localhost:9090
#   Grafana: http://localhost:3000 (admin/admin)
```

### 3. Kubernetes 部署

```bash
# 构建并导入镜像（minikube/kind）
docker build -t knowledge-base:latest .
kind load docker-image knowledge-base:latest --name <cluster-name>

# 部署
kubectl apply -f k8s/deployment.yaml

# 验证
kubectl get pods -l app=knowledge-base
kubectl port-forward svc/knowledge-base 8080:80
```

## 架构图

```
┌──────────────────────────────────────────────────┐
│                    Docker Host                    │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  Prometheus     │◄───│  Nginx Exporter      │ │
│  │  :9090          │    │  :9113               │ │
│  └────────┬────────┘    └──────────▲───────────┘ │
│           │                        │             │
│  ┌────────▼────────┐    ┌──────────┴───────────┐ │
│  │  Grafana        │    │  Knowledge Base      │ │
│  │  :3000          │    │  :8080 → health      │ │
│  └─────────────────┘    │  /nginx_status       │ │
│                          └──────────────────────┘ │
└──────────────────────────────────────────────────┘
```

## 可观测性

| 指标 | 来源 | 用途 |
|------|------|------|
| Nginx QPS | nginx_exporter | 流量分析 |
| 状态码分布 (2xx/4xx/5xx) | nginx_exporter | 错误率监控 |
| 连接数 | nginx_exporter | 并发评估 |
| P99 延迟 | nginx_exporter | 性能基线与回归 |
| 健康检查 | /health 端点 | 黑盒监控 |

## 告警规则

| 告警 | 级别 | 触发条件 |
|------|------|---------|
| InstanceDown | Critical | Nginx 实例不可达 > 2min |
| HighErrorRate | Warning | 5xx 错误率 > 5% |
| HighLatency | Warning | P99 延迟 > 1s |
| HealthCheckFailed | Critical | /health 返回非 200 |

## 项目结构

```
knowledge-base-delivery/
├── Dockerfile
├── docker-compose.yml
├── config/
│   └── nginx.conf              # Nginx 配置（Gzip、路由、健康检查、JSON日志）
├── html/
│   └── index.html              # SPA 知识库页面
├── k8s/
│   └── deployment.yaml         # K8s Deployment + Service + ServiceMonitor
├── monitoring/
│   ├── prometheus.yml          # Prometheus 采集配置
│   ├── alert-rules.yml         # 告警规则定义
│   ├── grafana-datasources.yml # Grafana 数据源
│   ├── grafana-dashboards.yml  # Grafana Dashboard 提供者
│   └── dashboards/
│       └── nginx-overview.json # Nginx 监控面板
└── README.md
```

## 技术要点

- **镜像体积**：基于 Alpine 构建，镜像 < 20MB
- **Gzip 压缩**：静态资源传输体积压缩 70%+
- **SPA 路由**：`try_files $uri /index.html` 解决刷新 404
- **安全头**：X-Frame-Options / X-Content-Type-Options / X-XSS-Protection
- **结构化日志**：JSON 格式输出，可直接对接 ELK / Loki
- **自愈**：Docker `restart: always` + Kubernetes livenessProbe 双重保障

## 开发者

- **刘炳浩** | SRE 工程师
- [GitHub](https://github.com) (替换为你的 GitHub 链接)
