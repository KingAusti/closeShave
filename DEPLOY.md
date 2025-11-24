# Deployment Guide - Publishing to Docker Hub

This guide explains how to publish CloseShave images to Docker Hub so others can easily install and run it.

## Prerequisites

1. Docker installed and running
2. Docker Hub account (create at https://hub.docker.com/)
3. Logged into Docker Hub: `docker login`

## Publishing Images

### Quick Method: Use the Publish Script

The easiest way to build and publish images:

```bash
# Publish with latest tag
./scripts/publish-dockerhub.sh

# Publish with a specific version
./scripts/publish-dockerhub.sh v0.1.0

# Use a custom Docker Hub username
DOCKERHUB_USERNAME=yourusername ./scripts/publish-dockerhub.sh v0.1.0
```

**Note:** Before running, update the `DOCKERHUB_USERNAME` variable in the script or set it as an environment variable.

### Manual Method: Step by Step

#### Step 1: Build the Images

Build both backend and frontend images:

```bash
# Build backend
docker build -t closeshave/backend:latest ./backend

# Build frontend
docker build -t closeshave/frontend:latest ./frontend
```

**Note:** Replace `closeshave` with your Docker Hub username.

### Step 2: Tag Images (Optional)

If you want to tag specific versions:

```bash
# Tag backend
docker tag closeshave/backend:latest closeshave/backend:v0.1.0

# Tag frontend
docker tag closeshave/frontend:latest closeshave/frontend:v0.1.0
```

### Step 3: Push to Docker Hub

```bash
# Push backend
docker push closeshave/backend:latest
docker push closeshave/backend:v0.1.0  # if you tagged a version

# Push frontend
docker push closeshave/frontend:latest
docker push closeshave/frontend:v0.1.0  # if you tagged a version
```

### Step 4: Update Configuration Files

**Important:** Before sharing with others, update these files with your actual usernames:

1. Update `docker-compose.public.yml` with your Docker Hub username:
   ```yaml
   image: YOUR_DOCKERHUB_USERNAME/backend:latest
   image: YOUR_DOCKERHUB_USERNAME/frontend:latest
   ```

2. Update `scripts/install-public.sh` with your GitHub username:
   ```bash
   # Replace YOUR_USERNAME with your actual GitHub username in the curl URLs
   ```

3. Update `.github/workflows/docker-publish.yml` with your Docker Hub username:
   ```yaml
   env:
     DOCKERHUB_USERNAME: your-dockerhub-username
   ```

4. Update `README.md` installation instructions:
   ```bash
   # Replace YOUR_USERNAME with your actual GitHub username in the curl URLs
   ```

## Automated Publishing with GitHub Actions

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Publish Docker Images

on:
  push:
    tags:
      - 'v*'
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: closeshave/backend:latest,closeshave/backend:${{ github.ref_name }}
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: closeshave/frontend:latest,closeshave/frontend:${{ github.ref_name }}
```

**Setup GitHub Secrets:**
1. Go to your repository Settings → Secrets and variables → Actions
2. Add `DOCKERHUB_USERNAME` with your Docker Hub username
3. Add `DOCKERHUB_TOKEN` with your Docker Hub access token (create at https://hub.docker.com/settings/security)

## Testing Public Images

Before publishing, test that the public compose file works:

```bash
# Update docker-compose.public.yml with your image names
docker-compose -f docker-compose.public.yml pull
docker-compose -f docker-compose.public.yml up -d
```

## Version Management

### Semantic Versioning

Tag releases with semantic versions:
- `v0.1.0` - Initial release
- `v0.1.1` - Patch release
- `v0.2.0` - Minor release
- `v1.0.0` - Major release

### Updating Latest Tag

The `latest` tag should always point to the most recent stable release:

```bash
docker tag closeshave/backend:v1.0.0 closeshave/backend:latest
docker push closeshave/backend:latest
```

## Multi-Architecture Builds (Advanced)

For ARM64 support (Apple Silicon, Raspberry Pi):

```bash
# Install buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t closeshave/backend:latest \
  --push ./backend
```

## Troubleshooting

### Authentication Issues

```bash
# Re-login to Docker Hub
docker logout
docker login
```

### Push Permission Denied

- Ensure you're logged into Docker Hub
- Verify the image name matches your Docker Hub username/organization
- Check that the repository exists on Docker Hub (or create it)

### Build Fails

- Check Dockerfile syntax
- Ensure all dependencies are available
- Review build logs for specific errors

## Best Practices

1. **Always tag releases** - Don't rely only on `latest`
2. **Test before pushing** - Build and test locally first
3. **Use GitHub Actions** - Automate publishing on releases
4. **Document changes** - Update CHANGELOG.md with each release
5. **Security scanning** - Use `docker scan` to check for vulnerabilities

## Next Steps

After publishing:
1. Update README.md with installation instructions
2. Create a GitHub release with the tag
3. Share the installation command with users
4. Monitor Docker Hub for downloads and issues

