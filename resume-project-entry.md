# 简历项目描述

## 简洁版（适合技能清单下方的项目列表）

> **个人博客系统 - 云原生全链路交付**（独立项目）
>
> 基于 Docker + Nginx + Kubernetes + Prometheus 构建的个人技术博客，覆盖容器化、网关配置、CI/CD 与全链路可观测性。
> - 前端：纯 SPA 架构，支持 Markdown 渲染、全文搜索、标签与归档筛选，数据通过 localStorage 持久化
> - 网关：Nginx 反向代理，开启 Gzip 压缩（静态资源减少 70%+），`try_files` 解决 SPA 刷新 404
> - 监控：Prometheus + Nginx Exporter 采集 QPS / P99 延迟 / 5xx 错误率，Grafana 6 面板可视化
> - 运维：Docker Compose 本地一键启动全套监控套件，Kubernetes Deployment 2 副本部署 + `livenessProbe` / `readinessProbe` 健康检查
> - 告警：4 条 Prometheus 告警规则（实例宕机 / 错误率 / 延迟 / 健康检查失败）
>
> 技术栈：Docker · Nginx · Kubernetes · Prometheus · Grafana · Shell · Git
>
> [GitHub](https://github.com/fancyLiu6/knowledge-base-delivery)

---

## 面试扩展版（准备 2-3 分钟讲完）

### 项目动机

作为 SRE 学习项目，我把一个博客系统从"裸 HTML"做成了完整的云原生交付方案。目标是打通容器化 → 监控 → K8s 部署全链路。

### 做了什么

**1. 容器化（Docker）**
- 基于 `nginx:1.25-alpine` 构建极简镜像（< 20MB）
- 多阶段构建，只保留运行时依赖
- 配置了 Docker `HEALTHCHECK` 指令，30 秒间隔检查 `/health` 端点

**2. 网关层治理（Nginx）**
- 开启 Gzip 压缩，`gzip_comp_level 6`，静态资源体积压缩 70%+
- 配置 `try_files $uri /index.html` 解决 SPA 前端路由刷新 404
- JSON 格式结构化日志（`log_format json_combined`），可直接对接 ELK / Loki
- 安全头：`X-Frame-Options` / `X-Content-Type-Options` / `X-XSS-Protection`
- `stub_status` 模块暴露 Nginx 运行指标

**3. 可观测性（Prometheus + Grafana）**
- 部署 Nginx Prometheus Exporter，将 `stub_status` 转为 Prometheus 指标
- 4 条告警规则：InstanceDown / HighErrorRate / HighLatency / HealthCheckFailed
- Grafana Dashboard 包含 6 个面板：QPS、状态码分布、活跃连接、P99 延迟、健康状态、错误率
- 整个监控套件可通过 `docker-compose up -d` 一键启动

**4. Kubernetes 部署**
- 编写 Deployment + Service + ServiceMonitor 声明文件
- `replicas: 2`，`livenessProbe` + `readinessProbe` 基于 `/health` 端点
- 资源限制：`requests: 64Mi / limits: 128Mi`
- 滚动更新策略，零停机部署

**5. Git 工作流**
- 完整 Git 提交历史，规范化 commit message
- 推送到公开 GitHub 仓库，README 含架构图与快速开始指南

### 遇到和解决的问题

- **Prometheus 配置错误**：`rule_files` 被错误嵌套在 `alerting` 块下导致 Prometheus 无法启动，排查日志定位到 YAML 缩进问题后修复
- **nginx-exporter DNS 解析失败**：容器未加入 Docker Compose 网络导致 Prometheus 无法抓取指标，通过 `docker network connect` 修复
- **端口冲突**：knowledge-base 和 nginx-exporter 同时绑定宿主机 9113 端口，修改 compose 配置只保留 nginx-exporter 对外暴露指标端口

### 面试可以延伸聊的

- SLO 怎么基于 QPS 和错误率数据来设定？
- 如果把博客部署到生产环境，还需要加什么（日志采集 / 链路追踪 / 证书管理 / CDN）？
- `livenessProbe` 和 `readinessProbe` 的区别和使用场景？
- 怎么让告警更智能（降噪、分级、on-call 轮值）？

---

## 简历模板 — 完整项目板块

```
## 项目经验

### 个人博客系统 - 云原生全链路交付  2025.05
GitHub: https://github.com/fancyLiu6/knowledge-base-delivery

目标：打通容器化 → 可观测性 → 服务编排的 SRE 完整链路，积累工程化落地经验。

架构与容器化
- 纯前端 SPA 博客（支持 Markdown 编辑、全文搜索、标签/归档筛选），
  本地依赖零安装，数据通过 localStorage 持久化。
- 基于 nginx:1.25-alpine 构建镜像（< 20MB），Dockerfile 内嵌 HEALTHCHECK。

网关与性能调优
- Nginx 开启 Gzip 压缩（静态资源体积减少 70%+），配置 try_files 解决
  SPA 刷新 404；JSON 格式访问日志可直接对接下游采集管道。
- 安全头注入（X-Frame-Options / X-Content-Type-Options / X-XSS-Protection）。

可观测性建设
- 部署 Prometheus + Nginx Prometheus Exporter + Grafana，采集 QPS、P99 延迟、
  状态码分布、活跃连接数等黄金指标。
- 编写 4 条 Prometheus 告警规则（实例宕机、错误率、延迟、健康检查失败），
  Grafana Dashboard 6 个面板实时展示。
- docker-compose 一键拉起完整监控套件。

Kubernetes 部署
- 编写 Deployment + NodePort Service 声明文件，2 副本部署。
- 配置 livenessProbe / readinessProbe 基于 /health 端点；
  设置资源 requests 与 limits。
- 使用 kind 搭建本地集群完成部署验证。

技术栈：Docker · Nginx · Kubernetes · Prometheus · Grafana · Shell · Git
```
