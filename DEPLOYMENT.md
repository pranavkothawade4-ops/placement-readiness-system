# 🌐 Live Deployment Guide: PlacementPulse

This guide explains how to deploy the **PlacementPulse** application live to the internet so that students, placement officers, and recruiters can access it from anywhere.

All necessary deployment configuration files (`Procfile`, `render.yaml`, `Dockerfile`, `.dockerignore`, and `.gitignore`) have already been generated in your project directory.

---

## 📋 Step 0: Push Code to GitHub (Required for Most Cloud Hosts)

Most cloud platforms (Render, Railway, Fly.io, etc.) connect directly to your GitHub repository to build and deploy your app automatically whenever you push updates.

Open **PowerShell** or Terminal in your project directory:

```powershell
cd "C:\Users\Admin\.gemini\antigravity\scratch\placement-readiness-system"

# 1. Initialize Git repository
git init

# 2. Stage and commit all files
git add .
git commit -m "Initial release of PlacementPulse System"

# 3. Create a new repository on GitHub (https://github.com/new) named "placement-readiness-system"
# Then link and push your code:
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/placement-readiness-system.git
git push -u origin main
```

---

## 🥇 Option 1: Deploy on Render.com (Recommended – Free & Easiest)

**Render** offers a 100% free web service tier with free automatic HTTPS/SSL and instant GitHub integration.

### Steps:
1. Go to [https://render.com](https://render.com) and sign in with your GitHub account.
2. In the Render Dashboard, click **New +** &rarr; select **Web Service**.
3. Choose **Build and deploy from a Git repository**, and select your `placement-readiness-system` repo.
4. Fill in the following details:
   - **Name**: `placementpulse` (or your preferred name)
   - **Region**: Choose the closest region (e.g., *Singapore*, *Oregon*, or *Frankfurt*)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (uses project root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Select **Free**
5. Click **Create Web Service**.
6. Render will install dependencies, seed the initial database, and deploy the application.
7. Your live website URL will be ready at:
   ```
   https://placementpulse.onrender.com
   ```

---

## 🥈 Option 2: Deploy on Railway.app (Fastest 60-Second Deploy)

**Railway** automatically detects the `Procfile` or `Dockerfile` and deploys instantly.

### Steps:
1. Go to [https://railway.app](https://railway.app) and log in with GitHub.
2. Click **New Project** &rarr; Select **Deploy from GitHub repo**.
3. Pick your `placement-readiness-system` repository.
4. Click **Deploy Now**.
5. Once deployment starts, go to **Settings** &rarr; **Networking** &rarr; click **Generate Domain**.
6. You will get a live URL such as:
   ```
   https://placement-readiness-production.up.railway.app
   ```

---

## 🥉 Option 3: Deploy on PythonAnywhere.com (Dedicated Python Host)

If you prefer classic Python server hosting:

### Steps:
1. Create a free account at [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a **Bash Console** in PythonAnywhere and clone your repo:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/placement-readiness-system.git
   cd placement-readiness-system
   pip install -r requirements.txt
   ```
3. Go to the **Web** tab &rarr; click **Add a new web app** &rarr; choose **Manual Configuration** with **Python 3.11**.
4. Set **Source Code Directory**: `/home/yourusername/placement-readiness-system`
5. Click on the **WSGI configuration file** link and replace its content with:
   ```python
   import sys
   import os

   path = '/home/yourusername/placement-readiness-system'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
6. Click the green **Reload** button at the top of the Web tab.
7. Your app is live at:
   ```
   https://yourusername.pythonanywhere.com
   ```

---

## 🐳 Option 4: Deploy Anywhere with Docker (Google Cloud Run / Fly.io / VPS)

The project includes a multi-threaded, production-ready `Dockerfile`:

### Deploy to Fly.io:
```bash
# Install flyctl if not already installed, then:
fly auth login
fly launch
fly deploy
```

### Deploy to Google Cloud Run:
```bash
# Build and submit container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/placement-pulse

# Deploy to Cloud Run
gcloud run deploy placement-pulse \
  --image gcr.io/YOUR_PROJECT_ID/placement-pulse \
  --platform managed \
  --allow-unauthenticated \
  --port 5000
```

---

## 🖥️ Option 5: Self-Hosted Linux VPS (Ubuntu + Nginx + Gunicorn)

If deploying to your own cloud server (AWS EC2, DigitalOcean Droplet, Linode, Hostinger):

### 1. Server Setup:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git nginx
git clone https://github.com/YOUR_GITHUB_USERNAME/placement-readiness-system.git
cd placement-readiness-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create Systemd Service (`/etc/systemd/system/placementpulse.service`):
```ini
[Unit]
Description=PlacementPulse Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/placement-readiness-system
Environment="PATH=/home/ubuntu/placement-readiness-system/venv/bin"
ExecStart=/home/ubuntu/placement-readiness-system/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start placementpulse
sudo systemctl enable placementpulse
```

### 3. Nginx Reverse Proxy (`/etc/nginx/sites-available/placementpulse`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/placementpulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Enable Free HTTPS (Let's Encrypt SSL):
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🔑 Default Production Administrator Credentials

When the app boots on your live server, it automatically initializes the SQLite database and seeds the default TPO administrative account:

- **Portal URL**: `/admin/login`
- **Email**: `admin@campus.edu`
- **Password**: `admin123`

*(You can change the email/password or create new officers in the TPO Dashboard at any time).*
