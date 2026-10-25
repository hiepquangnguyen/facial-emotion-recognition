# 🚀 Deployment Guide - Render.com

## 📋 Prerequisites

1. **GitHub Repository** - Push your code to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Model Files** - Ensure `models/emotion_model_cnn.h5` exists

## 🔧 Deployment Steps

### 1. Connect to Render

1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click **"New +"** → **"Web Service"**

### 2. Configure Service

- **Repository:** Select your GitHub repo
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

### 3. Environment Variables

Set these in Render dashboard:
```
FLASK_ENV=production
PYTHON_VERSION=3.8.10
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///emotion_app.db
```

### 4. Advanced Settings

- **Plan:** Free Tier
- **Auto-Deploy:** Yes
- **Health Check Path:** `/`

## 📁 Configuration Files

The following files are configured for Render deployment:

### `render.yaml` 
```yaml
services:
  - type: web
    name: emotion-recognition-app
    runtime: python3
    buildCommand: "./build.sh"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT app:app"
    plan: free
```

### `build.sh`
- Installs system dependencies for OpenCV
- Installs Python packages
- Sets up directory structure
- Initializes database

### `runtime.txt`
```
python-3.8.10
```

### `Procfile` (Backup)
```
web: gunicorn --bind 0.0.0.0:$PORT app:app --workers 4 --timeout 120
```

## ⚡ Quick Deploy

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy on Render:**
   - Connect your repo
   - Select branch: `main`
   - Click **"Create Web Service"**

3. **Wait for build** (5-10 minutes)

4. **Access your app** at `https://your-app-name.onrender.com`

## 🔍 Monitoring

### Build Logs
Monitor deployment in Render dashboard:
- View build progress
- Check for errors
- Monitor resource usage

### Health Checks
- Render automatically monitors your app
- Restarts if unhealthy
- Sends notifications on failures

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails:**
   - Check `requirements.txt` for conflicts
   - Verify Python version compatibility
   - Review build logs

2. **Model Not Found:**
   - Ensure `models/emotion_model_cnn.h5` is in repo
   - Check file size limits (512MB max for free tier)

3. **Database Issues:**
   - SQLite file will be created automatically
   - On the free plan the filesystem is ephemeral: users/history are reset on each deploy or restart
   - For persistent data, use a paid plan with a disk (mounted outside the source dir) or an external database

4. **Memory Issues:**
   - Free tier has 512MB RAM limit
   - Optimize model loading
   - Consider upgrading plan

### Debug Commands

```bash
# Check app status
curl https://your-app.onrender.com/

# Test specific endpoint
curl https://your-app.onrender.com/api/model-info

# View logs in Render dashboard
```

## 📊 Performance

### Free Tier Limits
- **RAM:** 512MB
- **CPU:** Shared
- **Storage:** 1GB
- **Bandwidth:** 100GB/month
- **Build time:** 15 minutes max

### Optimization Tips
1. Use `opencv-python-headless` (already configured)
2. Minimize model file size
3. Implement caching for frequent requests
4. Use CDN for static assets

## 🔒 Security

1. **Environment Variables:** Store secrets securely
2. **HTTPS:** Automatically provided by Render
3. **Database:** SQLite with file persistence
4. **Authentication:** User login system included

## 📈 Scaling

To handle more traffic:
1. Upgrade to **Starter Plan** ($7/month)
2. Add more workers: `--workers 4`
3. Enable horizontal scaling
4. Consider Redis for caching

## 🆘 Support

- **Render Docs:** [render.com/docs](https://render.com/docs)
- **GitHub Issues:** [Create Issue](https://github.com/lebaohungk05/CVP/issues)
- **Community:** [Render Community](https://community.render.com)

---

✅ **Your Emotion Recognition App is now ready for cloud deployment!** 