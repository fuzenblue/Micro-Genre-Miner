# Deployment Guide: Micro-Genre Miner

## 📋 Overview

This guide provides comprehensive instructions for deploying the Micro-Genre Miner Streamlit application in various environments, from local development to production cloud deployment.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
```bash
# System Requirements
- Python 3.8+ 
- Git
- 4GB+ RAM
- 2GB free disk space
```

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/Micro-Genre-Miner.git
cd Micro-Genre-Miner
```

### 2. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file
echo TMDB_API_KEY=your_api_key_here > .env
echo TMDB_BASE_URL=https://api.themoviedb.org/3 >> .env
```

### 4. Run Application
```bash
cd app
streamlit run app.py
```

**Access**: http://localhost:8501

---

## 🐳 Docker Deployment

### Build Image
```bash
cd app
docker build -t micro-genre-miner .
```

### Run Container
```bash
docker run -p 8501:8501 micro-genre-miner
```

### Docker Compose (Recommended)
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: ./app
    ports:
      - "8501:8501"
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
    volumes:
      - ./data:/app/data:ro
    restart: unless-stopped
```

```bash
docker-compose up -d
```

---

## ☁️ Cloud Deployment Options

## 1. Streamlit Cloud (Easiest)

### Setup Steps
1. **Push to GitHub**: Ensure code is in public/private GitHub repo
2. **Connect Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
3. **Deploy**: Select repository and branch
4. **Configure Secrets**: Add TMDB_API_KEY in secrets management

### Configuration
```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### Secrets Management
```toml
# .streamlit/secrets.toml (DO NOT COMMIT)
TMDB_API_KEY = "your_api_key_here"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
```

---

## 2. Heroku Deployment

### Prerequisites
```bash
# Install Heroku CLI
# Create Heroku account
heroku login
```

### Setup Files
```bash
# Procfile
web: sh setup.sh && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

```bash
# setup.sh
mkdir -p ~/.streamlit/
echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml
```

```bash
# runtime.txt
python-3.10.12
```

### Deploy
```bash
# Create Heroku app
heroku create micro-genre-miner

# Set environment variables
heroku config:set TMDB_API_KEY=your_api_key_here

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

## 3. AWS EC2 Deployment

### Launch EC2 Instance
```bash
# Instance Configuration
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (2 vCPU, 4GB RAM)
- Security Group: Allow HTTP (80), HTTPS (443), SSH (22)
- Storage: 20GB GP3
```

### Server Setup
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
git clone https://github.com/yourusername/Micro-Genre-Miner.git
cd Micro-Genre-Miner

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure Nginx
```nginx
# /etc/nginx/sites-available/micro-genre-miner
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/micro-genre-miner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setup Systemd Service
```ini
# /etc/systemd/system/micro-genre-miner.service
[Unit]
Description=Micro Genre Miner Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Micro-Genre-Miner/app
Environment=PATH=/home/ubuntu/Micro-Genre-Miner/venv/bin
ExecStart=/home/ubuntu/Micro-Genre-Miner/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable micro-genre-miner
sudo systemctl start micro-genre-miner
```

---

## 4. Google Cloud Platform (GCP)

### Cloud Run Deployment
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/micro-genre-miner

# Deploy to Cloud Run
gcloud run deploy micro-genre-miner \
  --image gcr.io/PROJECT_ID/micro-genre-miner \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 1 \
  --set-env-vars TMDB_API_KEY=your_api_key_here
```

### App Engine Deployment
```yaml
# app.yaml
runtime: python310

env_variables:
  TMDB_API_KEY: "your_api_key_here"

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
```

```bash
gcloud app deploy
```

---

## 5. Azure Container Instances

### Deploy Container
```bash
# Create resource group
az group create --name micro-genre-miner-rg --location eastus

# Deploy container
az container create \
  --resource-group micro-genre-miner-rg \
  --name micro-genre-miner \
  --image your-registry/micro-genre-miner:latest \
  --dns-name-label micro-genre-miner \
  --ports 8501 \
  --environment-variables TMDB_API_KEY=your_api_key_here \
  --cpu 1 \
  --memory 2
```

---

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
TMDB_API_KEY=your_tmdb_api_key
TMDB_BASE_URL=https://api.themoviedb.org/3

# Optional
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Streamlit Configuration
```toml
# .streamlit/config.toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
showErrorDetails = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[logger]
level = "info"
```

### Performance Optimization
```python
# Caching configuration
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return pd.read_parquet("movie_clusters_keybert.parquet")

# Memory optimization
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
```

---

## 📊 Monitoring & Logging

### Health Check Endpoint
```python
# Add to app.py
@st.cache_data
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if st.sidebar.button("Health Check"):
    st.json(health_check())
```

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection
```python
# Simple metrics
import time
start_time = time.time()

# Track page views
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1
```

---

## 🔒 Security Considerations

### API Key Security
```bash
# Never commit API keys
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
```

### HTTPS Configuration
```nginx
# SSL with Let's Encrypt
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### Rate Limiting
```python
# Simple rate limiting
import time
from collections import defaultdict

request_counts = defaultdict(list)

def rate_limit(ip, limit=100, window=3600):
    now = time.time()
    requests = request_counts[ip]
    requests[:] = [req for req in requests if now - req < window]
    
    if len(requests) >= limit:
        return False
    
    requests.append(now)
    return True
```

---

## 🚨 Troubleshooting

### Common Issues

#### Memory Issues
```bash
# Symptoms: App crashes, slow performance
# Solutions:
- Increase container memory (2GB minimum)
- Optimize data loading with chunking
- Use @st.cache_data for large datasets
- Consider data sampling for development
```

#### Port Conflicts
```bash
# Symptoms: "Port already in use"
# Solutions:
netstat -tulpn | grep 8501  # Find process using port
kill -9 <PID>               # Kill process
# Or use different port: streamlit run app.py --server.port=8502
```

#### API Rate Limits
```bash
# Symptoms: TMDB API errors
# Solutions:
- Implement exponential backoff
- Cache API responses
- Use API key with higher limits
- Implement request queuing
```

#### Docker Build Failures
```bash
# Symptoms: Build errors, dependency issues
# Solutions:
docker system prune -a     # Clean Docker cache
pip install --upgrade pip  # Update pip
# Use multi-stage builds for optimization
```

### Debug Mode
```bash
# Enable debug logging
streamlit run app.py --logger.level=debug

# Check logs
tail -f ~/.streamlit/logs/streamlit.log
```

---

## 📈 Performance Optimization

### Caching Strategy
```python
# Data caching
@st.cache_data(ttl=3600, max_entries=3)
def load_filtered_data(genre_filter):
    return df[df['micro_genre_keybert'].str.contains(genre_filter)]

# Resource caching
@st.cache_resource
def load_heavy_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
```

### Memory Management
```python
# Lazy loading
@st.cache_data
def load_data_chunk(chunk_size=1000, offset=0):
    return pd.read_parquet(
        "movie_clusters_keybert.parquet",
        engine='pyarrow'
    ).iloc[offset:offset+chunk_size]
```

### CDN Integration
```html
<!-- For static assets -->
<link rel="preload" href="https://cdn.example.com/fonts/font.woff2" as="font">
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code tested locally
- [ ] Environment variables configured
- [ ] Dependencies updated
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy in place

### Deployment
- [ ] Application deployed successfully
- [ ] Health checks passing
- [ ] SSL certificate configured
- [ ] Domain name configured
- [ ] Monitoring enabled
- [ ] Logging configured

### Post-Deployment
- [ ] Functionality testing
- [ ] Performance monitoring
- [ ] Error tracking setup
- [ ] User feedback collection
- [ ] Documentation updated
- [ ] Team notification sent

---

## 📞 Support & Maintenance

### Regular Maintenance
```bash
# Weekly tasks
- Check application logs
- Monitor resource usage
- Update dependencies
- Backup data files
- Review security alerts

# Monthly tasks
- Performance optimization review
- User feedback analysis
- Dependency security audit
- Cost optimization review
- Documentation updates
```

### Emergency Procedures
```bash
# Application down
1. Check service status: systemctl status micro-genre-miner
2. Check logs: journalctl -u micro-genre-miner -f
3. Restart service: systemctl restart micro-genre-miner
4. Check resources: htop, df -h
5. Rollback if needed: git checkout previous-version

# High resource usage
1. Identify process: htop, ps aux
2. Check memory: free -h
3. Restart application
4. Scale resources if needed
5. Investigate root cause
```

---

**Deployment Guide Version**: 1.0  
**Last Updated**: 2025-11-30 
**Supported Platforms**: Linux, macOS, Windows  
**Minimum Requirements**: Python 3.8+, 4GB RAM, 2GB Storage