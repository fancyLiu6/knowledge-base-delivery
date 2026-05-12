# 多阶段构建：Nginx + 前端静态文件
FROM nginx:1.25-alpine

# 安装 Nginx Exporter（轻量 Prometheus 指标暴露器）
RUN wget -qO /usr/local/bin/nginx-prometheus-exporter \
    https://github.com/nginxinc/nginx-prometheus-exporter/releases/download/v1.1.0/nginx-prometheus-exporter_1.1.0_linux_amd64 \
    && chmod +x /usr/local/bin/nginx-prometheus-exporter \
    || echo "exporter download skipped (offline build)"

# 复制 Nginx 配置
COPY config/nginx.conf /etc/nginx/nginx.conf

# 复制 SPA 静态文件
COPY html/ /usr/share/nginx/html/

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

EXPOSE 80 9113

CMD ["nginx", "-g", "daemon off;"]
