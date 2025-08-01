# SaturdayPlanner - NVIDIA Brev GPU Deployment Guide

## Quick Docker Deployment

### 1. Build and Test Locally
```bash
# Build the Docker image
docker build -t saturday-planner .

# Run locally with environment variables
docker run -p 8000:8000 --env-file .env saturday-planner
```

### 2. Deploy to NVIDIA Brev

#### Prerequisites
- NVIDIA Brev account
- GPU instance provisioned
- All API keys ready

#### Deployment Steps

1. **Push to Git Repository** (if using Git deployment)
```bash
git add .
git commit -m "Ready for NVIDIA Brev deployment"
git push origin main
```

2. **Or Upload Files Directly to Brev Instance**
   - Upload entire `saturday_planner` directory
   - Ensure `.env` file is included with your API keys

3. **On Brev GPU Instance**
```bash
# Install Docker (if not already installed)
sudo apt update
sudo apt install docker.io docker-compose

# Build and run
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs saturday-planner
```

4. **Access Your Agent**
   - Web Interface: `http://your-brev-instance-ip:8000`
   - Health Check: `http://your-brev-instance-ip:8000/health`

## Environment Variables Required

Ensure your `.env` file has all these values:

```bash
# NVIDIA AI
NEMO_ENDPOINT=https://integrate.api.nvidia.com/v1
NEMO_API_KEY=your_nvidia_key

# Weather
WEATHER_API_KEY=your_weather_key
WEATHER_SERVICE=weatherapi

# Places
PLACES_API_KEY=your_google_places_key
PLACES_SERVICE=google_places

# Google Calendar
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://your-brev-url:8000/auth/callback
DEFAULT_CALENDAR_ID=primary
OAUTH_ENVIRONMENT=production

# SMS Notifications
NOTIFICATION_SERVICE=twilio
NOTIFICATION_API_KEY=your_twilio_sid
NOTIFICATION_AUTH_TOKEN=your_twilio_token
NOTIFICATION_FROM=+17753177996
NOTIFICATION_TO=+12137092430

# Defaults
DEFAULT_ZIP_CODE=94102
DEFAULT_RADIUS_MILES=5
DEFAULT_MAX_PRICE=3
MEMORY_TYPE=file
MEMORY_PATH=/app/data/agent_memory.json
```

## Production Considerations

### Google Calendar OAuth
- Update `GOOGLE_REDIRECT_URI` to your Brev instance URL
- Add the redirect URI to Google Cloud Console
- Set `OAUTH_ENVIRONMENT=production`

### Twilio SMS
- Complete A2P 10DLC registration for SMS delivery
- Register your brand and campaign with Twilio
- This enables SMS notifications in production

### Security
- Never commit `.env` file to public repositories
- Use Brev's environment variable management if available
- Regularly rotate API keys

## Troubleshooting

### Container Won't Start
```bash
docker-compose logs saturday-planner
```

### Health Check Failing
```bash
curl http://localhost:8000/health
```

### API Connection Issues
Check logs for specific API errors:
```bash
docker-compose exec saturday-planner python -c "from agent_tools import *; print('Tools loaded successfully')"
```

## Success Metrics

✅ **Container Running**: `docker-compose ps` shows "Up"  
✅ **Health Check**: `/health` returns `{"status": "healthy"}`  
✅ **Web Interface**: Homepage loads at port 8000  
✅ **Agent Planning**: Can create Saturday plans via web interface  
✅ **Google Calendar**: Events created in your calendar  
✅ **SMS**: Notifications sent (after A2P registration)  

## Final Checklist for Hackathon Submission

- [ ] Docker container builds successfully
- [ ] All API integrations working  
- [ ] Web interface accessible
- [ ] Agent creates real calendar events
- [ ] Agent finds real venues via Google Places
- [ ] NVIDIA Nemotron model responding
- [ ] Shareable URL available from Brev
- [ ] Demo ready for judges