# Dexto Deployment Guide

Complete deployment guide for all platforms and environments.

## Table of Contents

- [Platform-Specific Guides](#platform-specific-guides)
- [Installation Methods](#installation-methods)
- [Deployment Modes](#deployment-modes)
- [Production Deployment](#production-deployment)
- [Storage Configuration](#storage-configuration)
- [Monitoring & Observability](#monitoring--observability)

## Platform-Specific Guides

- **[Windows Deployment](docs/deployment/WINDOWS_DEPLOYMENT.md)** - Complete Windows deployment guide
- **[Quick Start](docs/deployment/QUICK_START.md)** - Get started in 5 minutes
- **[Linux/macOS](#linuxmacos-deployment)** - Unix-based systems
- **[Docker](#docker-deployment)** - Containerized deployment
- **[Cloud Platforms](#cloud-deployment)** - AWS, GCP, Azure

## Installation Methods

### NPM Global Install (Recommended)

**Best for:** End users, quick setup

```bash
npm install -g dexto
dexto --version
dexto
```

### Build from Source

**Best for:** Developers, contributors, latest features

```bash
git clone https://github.com/truffle-ai/dexto.git
cd dexto
pnpm install
pnpm run build:all
pnpm run install-cli
dexto --version
```

### Docker

**Best for:** Isolated environments, production deployments

```bash
docker pull dexto/dexto:latest
docker run -p 3000:3000 -p 3001:3001 dexto/dexto:latest
```

## Deployment Modes

### 1. Web UI Mode (Default)

Full-featured web interface with visual agent configuration.

```bash
dexto
# Accessible at http://localhost:3000
```

**Features:**
- Visual chat interface
- Session history
- Agent configuration
- MCP playground
- Tool approval UI
- Settings management

**Use cases:** Development, demos, personal use

### 2. CLI Mode

Interactive terminal-based interface.

```bash
dexto --mode cli
```

**Features:**
- Terminal REPL
- Markdown rendering
- Session continuity
- Command history
- Tool execution

**Use cases:** SSH sessions, scripting, automation

### 3. API Server Mode

HTTP API and WebSocket server for programmatic access.

```bash
dexto --mode server --api-port 4000
```

**Features:**
- RESTful API
- WebSocket support
- Session management
- Multi-client support

**Use cases:** Integration, custom UIs, mobile apps

### 4. MCP Server Mode

Expose Dexto as a Model Context Protocol server.

```bash
dexto --mode mcp
```

**Features:**
- MCP protocol support
- Tool aggregation
- Resource management
- Prompt templates

**Use cases:** Claude Desktop, Cursor, MCP clients

### 5. Bot Modes

Deploy as Discord or Telegram bot.

```bash
# Discord
export DISCORD_BOT_TOKEN=...
dexto --mode discord

# Telegram
export TELEGRAM_BOT_TOKEN=...
dexto --mode telegram
```

**Use cases:** Team collaboration, community support

## Production Deployment

### Process Management

#### PM2 (Node.js Process Manager)

**Install PM2:**
```bash
npm install -g pm2
```

**Create ecosystem file:**

```javascript
// ecosystem.config.cjs
module.exports = {
  apps: [{
    name: 'dexto-api',
    script: 'dexto',
    args: '--mode server --api-port 4000 --skip-setup --no-interactive',
    instances: 'max',
    exec_mode: 'cluster',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      OPENAI_API_KEY: 'sk-...',
      REDIS_URL: 'redis://localhost:6379',
      POSTGRES_CONNECTION_STRING: 'postgresql://...',
      DEXTO_LOG_LEVEL: 'info'
    },
    error_file: '/var/log/dexto/error.log',
    out_file: '/var/log/dexto/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

**Manage:**
```bash
pm2 start ecosystem.config.cjs
pm2 status
pm2 logs dexto-api
pm2 restart dexto-api
pm2 stop dexto-api
pm2 save
pm2 startup  # Configure auto-start
```

#### systemd (Linux)

**Create service file:**

```ini
# /etc/systemd/system/dexto.service
[Unit]
Description=Dexto AI Agent Platform
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=dexto
Group=dexto
WorkingDirectory=/opt/dexto
Environment="NODE_ENV=production"
Environment="OPENAI_API_KEY=sk-..."
Environment="REDIS_URL=redis://localhost:6379"
Environment="POSTGRES_CONNECTION_STRING=postgresql://..."
Environment="DEXTO_LOG_LEVEL=info"
ExecStart=/usr/local/bin/dexto --mode server --api-port 4000 --skip-setup --no-interactive
Restart=always
RestartSec=10
StandardOutput=append:/var/log/dexto/stdout.log
StandardError=append:/var/log/dexto/stderr.log

[Install]
WantedBy=multi-user.target
```

**Manage:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dexto
sudo systemctl start dexto
sudo systemctl status dexto
sudo systemctl restart dexto
sudo journalctl -u dexto -f
```

### Docker Deployment

#### Single Container

**Dockerfile:**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy source
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages ./packages

# Install and build
RUN pnpm install --frozen-lockfile
RUN pnpm run build:all
RUN pnpm run install-cli

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built application
COPY --from=builder /root/.npm-packages /root/.npm-packages
ENV PATH="/root/.npm-packages/bin:${PATH}"

# Expose ports
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3001', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start
CMD ["dexto", "--mode", "server", "--skip-setup", "--no-interactive"]
```

**Build and run:**
```bash
docker build -t dexto:latest .
docker run -d \
  --name dexto-server \
  -p 3000:3000 \
  -p 3001:3001 \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  dexto:latest
```

#### Docker Compose (Recommended)

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  dexto:
    build: .
    container_name: dexto-app
    ports:
      - "3000:3000"
      - "3001:3001"
    environment:
      NODE_ENV: production
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      REDIS_URL: redis://redis:6379
      POSTGRES_CONNECTION_STRING: postgresql://postgres:password@postgres:5432/dexto
      DEXTO_LOG_LEVEL: info
    volumes:
      - ./data:/app/data
      - ./logs:/root/.dexto/logs
      - ./agents:/app/agents
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3001', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: dexto-redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:15-alpine
    container_name: dexto-postgres
    environment:
      POSTGRES_DB: dexto
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: dexto-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - dexto
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
```

**Manage:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose ps
docker-compose restart dexto
docker-compose down
```

### Kubernetes Deployment

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dexto
  labels:
    app: dexto
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dexto
  template:
    metadata:
      labels:
        app: dexto
    spec:
      containers:
      - name: dexto
        image: dexto/dexto:latest
        ports:
        - containerPort: 3000
          name: web
        - containerPort: 3001
          name: api
        env:
        - name: NODE_ENV
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: dexto-secrets
              key: openai-api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: POSTGRES_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: dexto-secrets
              key: postgres-connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: dexto-service
spec:
  selector:
    app: dexto
  ports:
  - name: web
    port: 3000
    targetPort: 3000
  - name: api
    port: 3001
    targetPort: 3001
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs -f deployment/dexto
kubectl scale deployment dexto --replicas=5
```

## Storage Configuration

### Development: In-Memory

**Fast, ephemeral:**

```yaml
storage:
  cache:
    type: memory
  database:
    type: memory
```

### Simple: SQLite

**Single-file, portable:**

```yaml
storage:
  cache:
    type: memory
  database:
    type: sqlite
    filename: /app/data/dexto.db
```

### Production: Redis + PostgreSQL

**Scalable, reliable:**

```yaml
storage:
  cache:
    type: redis
    url: redis://redis:6379
    maxConnections: 100
    ttl: 3600
  database:
    type: postgres
    connectionString: postgresql://user:pass@postgres:5432/dexto
    maxConnections: 25
    ssl: true
```

### Cloud Storage

**S3 for file storage:**

```yaml
storage:
  cache:
    type: redis
    url: redis://...
  database:
    type: postgres
    connectionString: postgresql://...
  files:
    type: s3
    bucket: dexto-files
    region: us-east-1
    accessKeyId: ${AWS_ACCESS_KEY_ID}
    secretAccessKey: ${AWS_SECRET_ACCESS_KEY}
```

## Monitoring & Observability

### OpenTelemetry

**Configure tracing:**

```yaml
# agent.yml
observability:
  enabled: true
  tracing:
    exporter: otlp
    endpoint: http://localhost:4318
    serviceName: dexto-agent
    sampleRate: 1.0
  metrics:
    enabled: true
    port: 9090
```

**Collectors:**
```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  prometheus:
    endpoint: 0.0.0.0:9090
  jaeger:
    endpoint: jaeger:14250
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [jaeger, logging]
    metrics:
      receivers: [otlp]
      exporters: [prometheus, logging]
```

### Health Checks

**HTTP endpoint:**
```bash
curl http://localhost:3001/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.2.4",
  "uptime": 3600,
  "database": "connected",
  "cache": "connected"
}
```

### Logging

**Configure logging:**

```yaml
# agent.yml
logging:
  level: info  # debug, info, warn, error
  format: json  # json, pretty
  outputs:
    - console
    - file
  file:
    path: /var/log/dexto/app.log
    maxSize: 100mb
    maxFiles: 10
    compress: true
```

**View logs:**
```bash
# Local
tail -f ~/.dexto/logs/dexto.log

# Docker
docker logs -f dexto-server

# Kubernetes
kubectl logs -f deployment/dexto

# PM2
pm2 logs dexto-api
```

### Metrics

**Expose Prometheus metrics:**

```yaml
# agent.yml
metrics:
  enabled: true
  port: 9090
  path: /metrics
```

**Sample metrics:**
- `dexto_requests_total` - Total requests
- `dexto_request_duration_seconds` - Request duration
- `dexto_sessions_active` - Active sessions
- `dexto_llm_tokens_total` - Token usage
- `dexto_tool_executions_total` - Tool calls

## Cloud Deployment

### AWS

**EC2:**
```bash
# User data script
#!/bin/bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g dexto pm2
pm2 start dexto -- --mode server --api-port 4000
pm2 save
pm2 startup
```

**ECS:**
```json
{
  "family": "dexto",
  "containerDefinitions": [{
    "name": "dexto",
    "image": "dexto/dexto:latest",
    "memory": 2048,
    "cpu": 1024,
    "portMappings": [
      {"containerPort": 3000},
      {"containerPort": 3001}
    ],
    "environment": [
      {"name": "NODE_ENV", "value": "production"},
      {"name": "REDIS_URL", "value": "redis://..."},
      {"name": "POSTGRES_CONNECTION_STRING", "value": "postgresql://..."}
    ],
    "secrets": [
      {
        "name": "OPENAI_API_KEY",
        "valueFrom": "arn:aws:secretsmanager:..."
      }
    ]
  }]
}
```

### GCP

**Cloud Run:**
```bash
gcloud run deploy dexto \
  --image dexto/dexto:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3001 \
  --set-env-vars OPENAI_API_KEY=sk-... \
  --set-env-vars REDIS_URL=redis://...
```

### Azure

**Container Instances:**
```bash
az container create \
  --resource-group dexto-rg \
  --name dexto \
  --image dexto/dexto:latest \
  --ports 3000 3001 \
  --environment-variables \
    NODE_ENV=production \
    OPENAI_API_KEY=sk-... \
  --cpu 2 \
  --memory 4
```

## Security Best Practices

### 1. API Keys

- Store in environment variables or secrets manager
- Never commit to version control
- Rotate regularly
- Use separate keys per environment

### 2. Network Security

- Use HTTPS/TLS in production
- Configure firewall rules
- Implement rate limiting
- Use VPN for internal services

### 3. Authentication

```yaml
# agent.yml
security:
  authentication:
    enabled: true
    type: jwt
    secret: ${JWT_SECRET}
  authorization:
    enabled: true
    policies:
      - role: admin
        permissions: ["*"]
      - role: user
        permissions: ["chat", "sessions"]
```

### 4. Tool Approval

```yaml
# agent.yml
tools:
  approval:
    mode: required  # required, optional, disabled
    timeout: 30000
    allowedTools:
      - filesystem:read
      - web:search
    blockedTools:
      - filesystem:write
      - process:execute
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -ti:3000 | xargs kill -9
```

**Module not found:**
```bash
pnpm run clean
pnpm install
pnpm run build:all
```

**Database connection failed:**
```bash
# Test connection
psql postgresql://user:pass@host:5432/dexto
redis-cli -u redis://host:6379 ping
```

**High memory usage:**
```yaml
# Limit session history
sessions:
  messageHistoryLimit: 50
  maxSessions: 100
```

## Next Steps

- [Configuration Guide](https://docs.dexto.ai/docs/guides/configuring-dexto)
- [API Reference](https://docs.dexto.ai/api/)
- [Agent Development](https://docs.dexto.ai/docs/guides/building-agents)
- [Discord Community](https://discord.gg/GFzWFAAZcm)

