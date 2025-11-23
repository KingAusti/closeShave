# Docker Deployment Guide

This guide covers deploying CloseShave using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### Development

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build and start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services

### Backend

- **Port**: 8000
- **Health Check**: `http://localhost:8000/`
- **Volumes**:
  - `./backend/data` - SQLite database and cache
  - `./backend/logs` - Application logs
  - `./backend/config` - Configuration files

### Frontend

- **Port**: 80
- **Health Check**: `http://localhost/health`
- **Proxy**: API requests are proxied to backend at `/api`

## Building Images

### Build individual services

```bash
# Backend
docker build -t closeshave-backend ./backend

# Frontend
docker build -t closeshave-frontend ./frontend
```

### Build all services

```bash
docker-compose build
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Backend
PYTHONUNBUFFERED=1
DATABASE_URL=sqlite:///app/data/cache.db

# Frontend (if needed)
VITE_API_URL=http://localhost:8000
```

## Volumes and Data Persistence

Data is persisted in mounted volumes:
- `./backend/data` - Database and cache files
- `./backend/logs` - Log files

To use named volumes instead:

```yaml
volumes:
  - backend-data:/app/data
  - backend-logs:/app/logs
```

## Networking

Services communicate through the `closeshave-network` bridge network. The frontend nginx configuration proxies `/api` requests to the backend service.

## Health Checks

Both services include health checks:
- Backend: Checks HTTP endpoint every 30s
- Frontend: Checks nginx health endpoint every 30s

## Troubleshooting

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Rebuild after code changes

```bash
docker-compose up -d --build
```

### Access container shell

```bash
# Backend
docker-compose exec backend /bin/bash

# Frontend
docker-compose exec frontend /bin/sh
```

### Check service status

```bash
docker-compose ps
```

## Production Deployment

### Using Docker Compose

1. Update `docker-compose.prod.yml` with production settings
2. Set environment variables
3. Use production nginx configuration
4. Configure SSL/TLS (recommended: use a reverse proxy like Traefik or Nginx)

### Using Kubernetes

Convert docker-compose to Kubernetes manifests:

```bash
# Install kompose
# macOS: brew install kompose
# Linux: Download from https://kompose.io/

# Convert
kompose convert
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml closeshave
```

## Security Considerations

1. **Don't expose ports directly** - Use a reverse proxy with SSL/TLS
2. **Set proper file permissions** - Ensure volumes have correct ownership
3. **Use secrets** - Store sensitive data in Docker secrets or environment files
4. **Regular updates** - Keep base images and dependencies updated
5. **Resource limits** - Set memory and CPU limits in production

## Performance Tuning

### Backend

- Adjust uvicorn workers: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]`
- Set appropriate timeout values
- Configure database connection pooling

### Frontend

- Enable nginx caching
- Configure gzip compression (already enabled)
- Use CDN for static assets

## Monitoring

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/

# Check frontend health
curl http://localhost/health
```

### Resource Usage

```bash
docker stats
```

## Backup and Restore

### Backup data

```bash
# Backup database and logs
docker-compose exec backend tar czf /tmp/backup.tar.gz /app/data /app/logs
docker cp closeshave-backend:/tmp/backup.tar.gz ./backup.tar.gz
```

### Restore data

```bash
# Copy backup to container
docker cp ./backup.tar.gz closeshave-backend:/tmp/backup.tar.gz

# Extract
docker-compose exec backend tar xzf /tmp/backup.tar.gz -C /
```

