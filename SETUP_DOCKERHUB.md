# Quick Setup Guide for Docker Hub Publishing

This is a quick checklist to get your CloseShave images published to Docker Hub.

## Prerequisites

1. ✅ Docker Hub account: https://hub.docker.com/signup
2. ✅ Docker installed and running
3. ✅ Logged into Docker Hub: `docker login`

## Quick Start (5 minutes)

### 1. Update Configuration Files

Replace `YOUR_USERNAME` and `closeshave` with your actual usernames:

**Files to update:**
- `docker-compose.public.yml` - Replace `closeshave` with your Docker Hub username
- `scripts/install-public.sh` - Replace `YOUR_USERNAME` with your GitHub username
- `.github/workflows/docker-publish.yml` - Replace `closeshave` with your Docker Hub username
- `README.md` - Replace `YOUR_USERNAME` with your GitHub username

### 2. Build and Push Images

```bash
# Option A: Use the automated script
./scripts/publish-dockerhub.sh v0.1.0

# Option B: Manual build and push
docker build -t yourusername/backend:latest ./backend
docker build -t yourusername/frontend:latest ./frontend
docker push yourusername/backend:latest
docker push yourusername/frontend:latest
```

### 3. Test the Public Installation

```bash
# Download and test the public compose file
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/closeshave/main/docker-compose.public.yml -o test-compose.yml

# Update the image names in test-compose.yml to match your Docker Hub username
# Then test:
docker-compose -f test-compose.yml pull
docker-compose -f test-compose.yml up -d
```

### 4. Share with Others

Once published, users can install with:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/closeshave/main/scripts/install-public.sh | bash
```

## Automated Publishing (Optional)

Set up GitHub Actions for automatic publishing:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DOCKERHUB_USERNAME` - Your Docker Hub username
   - `DOCKERHUB_TOKEN` - Your Docker Hub access token (create at https://hub.docker.com/settings/security)

3. Create a release tag to trigger publishing:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The GitHub Action will automatically build and push images when you create a tag.

## Verification Checklist

- [ ] Images are visible on Docker Hub
- [ ] `docker pull yourusername/backend:latest` works
- [ ] `docker pull yourusername/frontend:latest` works
- [ ] Public compose file uses correct image names
- [ ] Install script uses correct GitHub username
- [ ] README installation instructions are updated
- [ ] Tested installation on a clean machine

## Troubleshooting

**"denied: requested access to the resource is denied"**
- Make sure you're logged in: `docker login`
- Verify the image name matches your Docker Hub username
- Check that the repository exists on Docker Hub (or it will be created automatically)

**"repository does not exist"**
- The repository will be created automatically on first push
- Make sure the image name format is: `username/repository:tag`

**Install script fails**
- Check that GitHub URLs use your actual username
- Verify the repository is public (or use a token for private repos)

## Next Steps

- Set up automated publishing with GitHub Actions
- Create version tags for releases
- Monitor Docker Hub for downloads and issues
- Consider setting up a Docker Hub organization for better management

