# 🚀 F-001 Deployment Guide - Railway

**Last Updated**: 2025-10-23
**Status**: Production-Ready ✅
**Target Platform**: Railway (Primary), Render (Alternative)

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] All 151 tests passing (99% coverage) ✅
- [x] Security scan passed (0 HIGH/MEDIUM vulnerabilities) ✅
- [x] Code formatted with Black ✅
- [x] Documentation complete (README, SECURITY, Swagger UI) ✅
- [ ] Railway account created
- [ ] GitHub repository connected to Railway
- [ ] Production SECRET_KEY generated
- [ ] Environment variables documented

---

## 🎯 Railway Deployment (Recommended)

### Step 1: Create Railway Account

1. Go to [Railway.app](https://railway.app/)
2. Sign up with GitHub account
3. Verify email

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `stayfull_v1` repository
4. Railway will auto-detect Django project

### Step 3: Configure Environment Variables

In Railway Dashboard → Variables, add:

```env
# Django Core
DJANGO_SECRET_KEY=<generate-new-secret-key>
DEBUG=False
DJANGO_ALLOWED_HOSTS=*.railway.app,yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.development

# Database (Supabase)
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.yphgpndlbaducljhqzrb
SUPABASE_DB_PASSWORD=S33kda12091978!
SUPABASE_DB_HOST=aws-1-us-east-2.pooler.supabase.com
SUPABASE_DB_PORT=5432

# Encryption
FIELD_ENCRYPTION_KEY=O_5-FonRrZlqWFKv3Qh6JuTAiJVpSSBnSpFZka4ryiE=

# Railway-specific
PORT=8000
```

**Generate SECRET_KEY**:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 4: Deploy

1. Railway will automatically:
   - Detect `Procfile`
   - Install requirements from `requirements.txt`
   - Run migrations (`release` command in Procfile)
   - Start gunicorn web server

2. Monitor deployment in Railway logs
3. Deployment typically takes 3-5 minutes

### Step 5: Verify Deployment

Once deployed, Railway will provide a URL like:
```
https://stayfull-v1-production.up.railway.app
```

**Test endpoints**:
```bash
# Health check (replace with your Railway URL)
curl https://your-app.railway.app/api/v1/hotels/

# Swagger UI
https://your-app.railway.app/api/docs/
```

---

## 🔒 Production Settings

### Required Changes

1. **Static Files**: Already configured with `whitenoise`
2. **HTTPS Redirect**: Railway handles SSL automatically
3. **CORS**: Update `DJANGO_ALLOWED_HOSTS` in environment variables
4. **Database**: Already using Supabase (production-ready)

### Create Production Superuser

```bash
# In Railway console or local with production DB
railway run python manage.py createsuperuser
```

---

## 🧪 Post-Deployment Testing

### 1. API Endpoints
```bash
# Replace YOUR_URL with Railway deployment URL
export API_URL="https://your-app.railway.app"

# Test hotel list (should require authentication)
curl $API_URL/api/v1/hotels/

# Access Swagger UI
open $API_URL/api/docs/
```

### 2. Django Admin
```bash
# Access admin panel
open $API_URL/admin/

# Login with superuser credentials
# Test: Create a hotel, room type, room
```

### 3. Database Migrations
```bash
# Verify migrations ran successfully
railway run python manage.py showmigrations

# All should have [X] marks
```

### 4. API Documentation
- Swagger UI: `https://your-app.railway.app/api/docs/`
- ReDoc: `https://your-app.railway.app/api/redoc/`
- OpenAPI Schema: `https://your-app.railway.app/api/schema/`

---

## 📊 Monitoring & Logs

### View Logs in Railway
```bash
# Railway Dashboard → Deployments → View Logs
# Or use Railway CLI:
railway logs
```

### Key Metrics to Monitor
- **Response Time**: API should respond < 200ms
- **Error Rate**: Should be < 1%
- **Database Connections**: Monitor Supabase dashboard
- **Memory Usage**: Railway provides metrics

---

## 🔄 Continuous Deployment

### Automatic Deployments

Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "feat: Add new feature"
git push origin master

# Railway detects push and redeploys automatically
```

### Manual Deployment

```bash
# Using Railway CLI
railway up
```

---

## 🐛 Troubleshooting

### Issue: "Application Error" on Railway

**Solution**:
1. Check logs: `railway logs`
2. Verify environment variables are set
3. Ensure `Procfile` exists
4. Check Python version in `runtime.txt`

### Issue: Database Connection Failed

**Solution**:
1. Verify Supabase credentials in environment variables
2. Check Supabase connection pooler is accessible
3. Test connection locally first

### Issue: Static Files Not Loading

**Solution**:
1. Verify `whitenoise` is in `requirements.txt`
2. Run `python manage.py collectstatic` in Railway console
3. Check `STATIC_ROOT` and `STATIC_URL` in settings

### Issue: 404 on API Endpoints

**Solution**:
1. Verify `ALLOWED_HOSTS` includes Railway domain
2. Check URL routing in `config/urls.py`
3. Ensure trailing slashes in API calls

---

## 🎯 Alternative: Render Deployment

If you prefer Render over Railway:

### Render Setup

1. Create account at [Render.com](https://render.com/)
2. New Web Service → Connect GitHub repo
3. Environment: Python
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn config.wsgi:application`
6. Add environment variables (same as Railway)
7. Create PostgreSQL database (or keep Supabase)

---

## 📈 Next Steps After Deployment

### Immediate
- [ ] Test all 24 API endpoints
- [ ] Create test hotel data in Django Admin
- [ ] Test reservation flow end-to-end
- [ ] Verify PII encryption working

### Short-term (1-2 days)
- [ ] Set up custom domain
- [ ] Configure production logging (Sentry)
- [ ] Set up monitoring (UptimeRobot, Pingdom)
- [ ] Create backup strategy for database

### Medium-term (1 week)
- [ ] Performance testing (load testing with Locust)
- [ ] Security audit (OWASP Top 10 checklist)
- [ ] User acceptance testing
- [ ] Document API usage for frontend team

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ All API endpoints respond with 200 OK (authenticated)
✅ Swagger UI loads and shows all 24 endpoints
✅ Django Admin accessible and functional
✅ Database migrations complete
✅ No errors in Railway logs
✅ Can create hotel → room type → room → reservation
✅ PII encryption working (Guest ID documents)

---

## 📞 Support

**Deployment Issues**: Check Railway/Render documentation
**Database Issues**: Check Supabase dashboard
**Code Issues**: Review `ARCHITECT_DEVELOPER_COMMS.md`

---

**Ready to deploy?**

**Estimated deployment time**: 15-20 minutes (including testing)

**Difficulty**: Easy (Railway auto-detects Django)

🚀 Let's ship F-001 to production!
