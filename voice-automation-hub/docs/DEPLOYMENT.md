# Deployment Guide

Complete deployment guide for Voice Automation Hub in various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **Python**: 3.11 or higher
- **Node.js**: 20.0 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk**: Minimum 2GB free space

### Required Services
- OpenAI API access with API key
- (Optional) Redis for caching
- (Optional) PostgreSQL for persistence

## Environment Configuration

### Environment Variables
Create `.env` file in project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
ORCHESTRATOR_MODEL=gpt-4o
SUB_AGENT_MODEL=gpt-4o-mini

# Server Configuration
BACKEND_PORT=8000
FRONTEND_PORT=5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Optional: Redis
REDIS_URL=redis://localhost:6379

# Optional: Database
DATABASE_URL=postgresql://user:password@localhost/voicehub

# Security
SECRET_KEY=your-secret-key-here
API_KEY_SALT=your-salt-here

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

### Configuration Files
- `.env` - Environment variables
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `deployment/docker/docker-compose.yml` - Docker configuration

## Local Development

### Windows

#### Quick Start
```powershell
# 1. Install dependencies
.\deployment\windows\install.ps1

# 2. Configure environment
# Edit .env and add your OPENAI_API_KEY

# 3. Start services
.\deployment\windows\start.bat
```

#### Manual Setup
```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### macOS/Linux

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Development Workflow
1. Backend runs on `http://localhost:8000`
2. Frontend runs on `http://localhost:5173`
3. API docs at `http://localhost:8000/docs`
4. Hot reload enabled for both

## Docker Deployment

### Quick Start
```bash
cd deployment/docker
docker-compose up -d
```

### Build Images
```bash
# Build backend
docker build -f deployment/docker/Dockerfile.backend -t voicehub-backend backend/

# Build frontend
docker build -f deployment/docker/Dockerfile.frontend -t voicehub-frontend frontend/
```

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  backend:
    image: voicehub-backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    image: voicehub-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  redis:  # Optional
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Container Management
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Scale services
docker-compose up -d --scale backend=3
```

## Production Deployment

### Security Hardening

#### 1. Environment Security
```bash
# Use secure random keys
openssl rand -hex 32

# Restrict file permissions
chmod 600 .env
chmod 700 data/
```

#### 2. Network Security
```nginx
# Nginx SSL Configuration
server {
    listen 443 ssl http2;
    server_name voicehub.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://localhost:5173;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. Application Security
- Enable rate limiting
- Configure CORS properly
- Use API keys
- Implement authentication
- Regular security audits

### Performance Optimization

#### 1. Backend Configuration
```python
# production.py
WORKERS = multiprocessing.cpu_count() * 2 + 1
WORKER_CLASS = "uvicorn.workers.UvicornWorker"
KEEPALIVE = 5
TIMEOUT = 30
```

#### 2. Frontend Build
```bash
# Production build
npm run build

# Serve with optimizations
npx serve -s dist -l 5173
```

#### 3. Caching Strategy
```nginx
# Static asset caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# API response caching
location /api/static-data {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
}
```

### Process Management

#### Using Systemd (Linux)
```ini
# /etc/systemd/system/voicehub-backend.service
[Unit]
Description=Voice Automation Hub Backend
After=network.target

[Service]
Type=notify
User=voicehub
Group=voicehub
WorkingDirectory=/opt/voicehub/backend
Environment="PATH=/opt/voicehub/venv/bin"
ExecStart=/opt/voicehub/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Manage service
sudo systemctl start voicehub-backend
sudo systemctl enable voicehub-backend
sudo systemctl status voicehub-backend
```

#### Using PM2 (Node.js)
```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name voicehub-backend

# Start frontend
pm2 serve frontend/dist 5173 --spa --name voicehub-frontend

# Save configuration
pm2 save
pm2 startup
```

## Cloud Platforms

### AWS Deployment

#### Using ECS
```bash
# Build and push Docker image
aws ecr get-login-password | docker login --username AWS --password-stdin your-repo
docker build -t voicehub-backend -f deployment/docker/Dockerfile.backend backend/
docker tag voicehub-backend:latest your-repo/voicehub-backend:latest
docker push your-repo/voicehub-backend:latest

# Deploy to ECS
aws ecs update-service --cluster voicehub --service backend --force-new-deployment
```

#### Using EC2
```bash
# Connect to instance
ssh -i key.pem ubuntu@your-instance

# Clone and setup
git clone https://github.com/Zeeeepa/dexto.git
cd dexto/voice-automation-hub
cp .env.example .env
# Edit .env with your keys

# Run with Docker
cd deployment/docker
docker-compose up -d
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/voicehub-backend backend/

# Deploy
gcloud run deploy voicehub-backend \
  --image gcr.io/PROJECT_ID/voicehub-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Using Container Instances
```bash
# Create resource group
az group create --name voicehub --location eastus

# Deploy container
az container create \
  --resource-group voicehub \
  --name voicehub-backend \
  --image your-registry/voicehub-backend:latest \
  --dns-name-label voicehub \
  --ports 8000
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create voicehub-app

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key

# Deploy
git push heroku main

# Open app
heroku open
```

## Monitoring & Maintenance

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/api/health/detailed

# Metrics
curl http://localhost:8000/api/metrics
```

### Logging

#### Centralized Logging
```python
# Configure logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Backup Strategy
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Automated backup script
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d)
tar -czf $BACKUP_DIR/voicehub-$DATE.tar.gz data/
find $BACKUP_DIR -mtime +7 -delete  # Keep last 7 days
```

### Updates & Maintenance
```bash
# Pull latest changes
git pull origin main

# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd frontend && npm update

# Restart services
docker-compose restart
# or
pm2 restart all
# or
sudo systemctl restart voicehub-backend
```

## Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list

# Check logs
tail -f logs/app.log

# Test configuration
python -c "from app.main import app; print('OK')"
```

#### Frontend build fails
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 20+

# Build with verbose output
npm run build --verbose
```

#### Docker issues
```bash
# Check container logs
docker-compose logs backend

# Rebuild containers
docker-compose build --no-cache

# Check container status
docker-compose ps

# Enter container
docker-compose exec backend bash
```

#### Performance issues
1. Check `/api/metrics` for bottlenecks
2. Review `/api/health/detailed` for system status
3. Monitor resource usage: `docker stats`
4. Check error logs: `docker-compose logs --tail=100`

## Deployment Checklist

### Pre-Deployment
- [ ] Test locally with production config
- [ ] Run test suite
- [ ] Update dependencies
- [ ] Review security settings
- [ ] Backup existing data
- [ ] Document changes

### Deployment
- [ ] Set environment variables
- [ ] Build production images
- [ ] Deploy containers
- [ ] Run database migrations (if any)
- [ ] Verify health checks
- [ ] Test critical paths

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Check metrics dashboard
- [ ] Test user workflows
- [ ] Verify backup systems
- [ ] Update documentation
- [ ] Notify team

## Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)

