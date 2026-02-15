# 🚀 PRODUCTION DEPLOYMENT GUIDE
## Kaluwala CSR Libraries - Complete Deployment Instructions

## 📦 Files Included

1. ✅ `config.py` - Production configuration with PostgreSQL
2. ✅ `gunicorn.conf.py` - Gunicorn WSGI server config
3. ✅ `Dockerfile` - Container image definition
4. ✅ `docker-compose.yml` - Full stack orchestration
5. ✅ `nginx.conf` - Reverse proxy configuration
6. ✅ `wsgi.py` - Production entry point
7. ✅ `backup.sh` - Database backup script
8. ✅ `requirements.txt` - Python dependencies
9. ✅ `.env.production` - Environment variables template

---

## 🏗️ Architecture

```
Internet → Nginx (80/443) → Gunicorn (8000) → Flask App
                                    ↓
                              PostgreSQL (5432)
```

**Stack:**
- **Web Server:** Nginx (reverse proxy, SSL, static files)
- **App Server:** Gunicorn (WSGI, workers)
- **Application:** Flask (Python 3.11)
- **Database:** PostgreSQL 15
- **Containerization:** Docker + Docker Compose

---

## 🚀 Quick Start (Development)

```bash
# 1. Clone/copy all deployment files

# 2. Create environment file
cp .env.production .env

# 3. Edit .env with your settings
nano .env

# 4. Start services
docker-compose up -d

# 5. Run database migration
docker-compose exec web python migrate.py

# 6. Create admin user
docker-compose exec web python verify_csr_admin.py

# 7. Visit http://localhost
```

---

## 🔧 Environment Configuration

Create `.env` file:

```env
# Flask
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://kaluwala:kaluwala_password@postgres:5432/kaluwala_db

# Site
SITE_URL=https://kaluwala.com

# Email (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@kaluwala.com

# Security
SESSION_COOKIE_SECURE=True
```

---

## 📋 Pre-Deployment Checklist

### 1. **Generate Secret Key:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. **Update Configuration:**
- [ ] Set `SECRET_KEY` in `.env`
- [ ] Configure `DATABASE_URL`
- [ ] Set `SITE_URL` to your domain
- [ ] Configure email credentials
- [ ] Update `SESSION_COOKIE_SECURE=True`

### 3. **Domain Setup:**
- [ ] Point domain DNS to server IP
- [ ] Wait for DNS propagation (check with `dig kaluwala.com`)

---

## 🐳 Docker Deployment

### **Build and Start:**
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### **Initialize Database:**
```bash
# Run migrations
docker-compose exec web python migrate.py

# Create admin user
docker-compose exec web python verify_csr_admin.py
```

### **Manage Services:**
```bash
# Stop all services
docker-compose down

# Restart a service
docker-compose restart web

# View logs
docker-compose logs -f nginx
docker-compose logs -f postgres

# Scale workers
docker-compose up -d --scale web=3
```

---

## 🔒 SSL Setup (Let's Encrypt)

### **Option 1: Automatic (Certbot)**

```bash
# 1. Update nginx.conf with your domain

# 2. Get SSL certificate
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    -d kaluwala.com \
    -d www.kaluwala.com \
    --email admin@kaluwala.com \
    --agree-tos

# 3. Uncomment HTTPS server block in nginx.conf

# 4. Restart nginx
docker-compose restart nginx
```

### **Option 2: Manual SSL**

1. Get SSL certificates from your provider
2. Place in `./certbot/conf/live/kaluwala.com/`
3. Update `nginx.conf` paths
4. Restart nginx

---

## 💾 Database Backups

### **Manual Backup:**
```bash
# Run backup script
docker-compose exec postgres /backups/backup.sh

# Or manual pg_dump
docker-compose exec postgres pg_dump -U kaluwala kaluwala_db > backup.sql
```

### **Automated Backups (Cron):**
```bash
# Add to crontab
0 2 * * * cd /path/to/kaluwala_csr && docker-compose exec postgres /backups/backup.sh

# Daily at 2 AM
```

### **Restore from Backup:**
```bash
# Stop app
docker-compose stop web

# Restore database
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U kaluwala kaluwala_db

# Restart
docker-compose start web
```

---

## 🌐 VPS Deployment (DigitalOcean / AWS)

### **1. Create Server:**
- **Provider:** DigitalOcean Droplet or AWS EC2
- **Size:** 2GB RAM minimum (4GB recommended)
- **OS:** Ubuntu 22.04 LTS
- **Storage:** 50GB SSD

### **2. Initial Server Setup:**
```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create user
adduser kaluwala
usermod -aG sudo,docker kaluwala

# Switch to user
su - kaluwala
```

### **3. Deploy Application:**
```bash
# Clone repository (or upload files)
git clone https://github.com/your-repo/kaluwala_csr.git
cd kaluwala_csr

# Or upload via SCP:
# scp -r kaluwala_csr/ kaluwala@your-server-ip:~/

# Create environment
cp .env.production .env
nano .env  # Edit with your settings

# Create directories
mkdir -p uploads logs backups certbot/conf certbot/www

# Build and start
docker-compose up -d

# Initialize database
docker-compose exec web python migrate.py
docker-compose exec web python verify_csr_admin.py
```

### **4. Configure Firewall:**
```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### **5. Setup SSL:**
```bash
# Get certificate
docker-compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    -d your-domain.com \
    --email admin@your-domain.com \
    --agree-tos

# Update nginx.conf (uncomment HTTPS block)
# Restart nginx
docker-compose restart nginx
```

---

## 📊 Monitoring & Logs

### **View Logs:**
```bash
# Application logs
docker-compose logs -f web

# Nginx access logs
docker-compose logs -f nginx

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### **System Monitoring:**
```bash
# Container stats
docker stats

# Disk usage
df -h

# Check services
docker-compose ps
```

---

## 🧪 Testing Deployment

### **1. Health Check:**
```bash
curl http://localhost/health
# Should return: {"status": "healthy", "database": "connected"}
```

### **2. Test Public Portal:**
```bash
curl http://localhost/
# Should return HTML home page
```

### **3. Test Library Microsite:**
```bash
curl http://localhost/libraries/bpsmv
# Should return library details
```

### **4. Test API Endpoint:**
```bash
curl "http://localhost/api/analytics?library=bpsmv"
# Should return analytics data
```

### **5. E2E Test Scenario:**
```
1. Visit http://your-domain.com
2. Click "BPSMV" library
3. Click "Book a Seat Now"
4. Login with credentials
5. Book a seat
6. Login as CSR Admin
7. View analytics dashboard
8. Verify booking appears in metrics
```

---

## 🔄 Updates & Maintenance

### **Deploy Code Updates:**
```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Restart with zero downtime
docker-compose up -d --no-deps --build web

# Run migrations if needed
docker-compose exec web python migrate.py
```

### **Database Migration:**
```bash
# Create migration
docker-compose exec web flask db migrate -m "description"

# Apply migration
docker-compose exec web flask db upgrade
```

---

## 🚨 Troubleshooting

### **Service Won't Start:**
```bash
# Check logs
docker-compose logs web

# Check configuration
docker-compose config

# Restart service
docker-compose restart web
```

### **Database Connection Error:**
```bash
# Check postgres is running
docker-compose ps postgres

# Test connection
docker-compose exec web python -c "from app import create_app; app = create_app('production'); print('OK')"
```

### **Nginx 502 Bad Gateway:**
```bash
# Check gunicorn is running
docker-compose ps web

# Check gunicorn logs
docker-compose logs web

# Restart web service
docker-compose restart web
```

---

## 📈 Performance Optimization

### **1. Database:**
```bash
# Increase connections
# Edit docker-compose.yml postgres command:
command: postgres -c max_connections=200
```

### **2. Gunicorn Workers:**
```python
# Edit gunicorn.conf.py
workers = 4  # Adjust based on CPU cores
```

### **3. Nginx Caching:**
```nginx
# Add to nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
```

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Home page loads at https://kaluwala.com
- [ ] SSL certificate valid (green padlock)
- [ ] Library microsites accessible
- [ ] Login/registration works
- [ ] Booking system functional
- [ ] Admin dashboard accessible
- [ ] CSR admin panel working
- [ ] Email notifications sending
- [ ] Database backups running
- [ ] Logs being generated
- [ ] Health check passing

---

## 📞 Support

**Documentation:** See individual .md files
**Logs:** Check docker-compose logs
**Database:** Access via docker-compose exec postgres psql

---

## 🎯 Next Steps

1. Setup monitoring (optional): Sentry, New Relic
2. Configure CDN for static files: Cloudflare
3. Setup automated backups to S3/Google Cloud
4. Configure email domain: SPF, DKIM records
5. Add application monitoring
6. Setup staging environment

**Total Deployment Time:** 2-4 hours
**Estimated Costs:** $10-20/month (VPS + domain)

Your production-ready library system is complete! 🚀📚
