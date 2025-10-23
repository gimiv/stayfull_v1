# 📋 Decision 003: Django Project Setup Plan
**Date**: 2025-10-22
**Status**: READY TO EXECUTE
**Architect**: Senior Product Architect
**Impact**: Foundation for entire hotel PMS

---

## 🎯 Project Setup Overview

### Environment Info
- **Python Version**: 3.13.7 (detected)
- **Package Manager**: pip3
- **Project Root**: `/Users/mergimkacija/stayfull_v1`

---

## 📦 Project Structure

```
stayfull_v1/
├── .architect/                  # Architect tracking (existing)
├── .git/                        # Git repository (to be initialized)
├── .gitignore                   # Python/Django gitignore
├── README.md                    # Project documentation
├── requirements/
│   ├── base.txt                # Core dependencies
│   ├── dev.txt                 # Development dependencies
│   └── production.txt          # Production dependencies
├── .env.example                # Environment variables template
├── .env                        # Local environment (gitignored)
├── manage.py                   # Django management script
├── pytest.ini                  # pytest configuration
├── setup.cfg                   # Python tooling config
│
├── config/                     # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Base settings
│   │   ├── development.py     # Dev settings
│   │   └── production.py      # Prod settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config (for future WebSocket support)
│
├── apps/                       # Django applications
│   ├── __init__.py
│   ├── core/                  # Core utilities, base models
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── managers.py
│   │   └── mixins.py
│   │
│   ├── users/                 # User & authentication
│   │   ├── __init__.py
│   │   ├── models.py          # User, Staff models
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   │
│   ├── hotels/                # Hotel management
│   │   ├── __init__.py
│   │   ├── models.py          # Hotel, RoomType, Room
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── guests/                # Guest management
│   │   ├── __init__.py
│   │   ├── models.py          # Guest
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── reservations/          # Reservation & booking
│   │   ├── __init__.py
│   │   ├── models.py          # Reservation
│   │   ├── admin.py
│   │   ├── services.py        # Business logic (availability, etc.)
│   │   └── tests/
│   │
│   ├── payments/              # Payment processing
│   │   ├── __init__.py
│   │   ├── models.py          # Payment
│   │   ├── admin.py
│   │   ├── stripe_handler.py
│   │   └── tests/
│   │
│   └── housekeeping/          # Housekeeping management
│       ├── __init__.py
│       ├── models.py          # HousekeepingTask
│       ├── admin.py
│       └── tests/
│
├── templates/                  # Django templates
│   ├── base.html
│   ├── admin/
│   └── front_desk/
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── media/                      # User uploads (development only, Supabase in production)
```

---

## 📋 Setup Steps

### Phase 1: Environment Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install core dependencies**
   ```bash
   pip install --upgrade pip
   pip install Django==5.0
   pip install djangorestframework
   pip install django-environ
   pip install psycopg2-binary
   pip install pytest pytest-django pytest-cov
   pip install factory-boy
   pip install django-allauth
   pip install celery redis
   pip install stripe
   ```

3. **Create requirements files**
   - `requirements/base.txt`: Core dependencies
   - `requirements/dev.txt`: Development tools (black, flake8, ipython)
   - `requirements/production.txt`: Production-only (gunicorn, whitenoise)

### Phase 2: Django Project Initialization

1. **Initialize Django project**
   ```bash
   django-admin startproject config .
   ```

2. **Restructure settings**
   - Move settings to `config/settings/`
   - Create `base.py`, `development.py`, `production.py`
   - Configure django-environ for environment variables

3. **Configure Supabase PostgreSQL connection**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': env('SUPABASE_DB_NAME'),
           'USER': env('SUPABASE_DB_USER'),
           'PASSWORD': env('SUPABASE_DB_PASSWORD'),
           'HOST': env('SUPABASE_DB_HOST'),
           'PORT': env('SUPABASE_DB_PORT', default='5432'),
       }
   }
   ```

### Phase 3: Create Core Apps

1. **Create apps** (in order)
   ```bash
   python manage.py startapp core apps/core
   python manage.py startapp users apps/users
   python manage.py startapp hotels apps/hotels
   python manage.py startapp guests apps/guests
   python manage.py startapp reservations apps/reservations
   python manage.py startapp payments apps/payments
   python manage.py startapp housekeeping apps/housekeeping
   ```

2. **Configure apps in settings**
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',

       # Third party
       'rest_framework',
       'allauth',
       'allauth.account',

       # Local apps
       'apps.core',
       'apps.users',
       'apps.hotels',
       'apps.guests',
       'apps.reservations',
       'apps.payments',
       'apps.housekeeping',
   ]
   ```

### Phase 4: Database Models (Test-First!)

**Order of model creation:**
1. **users.User** (extends Django User)
2. **users.Staff** (staff profiles)
3. **hotels.Hotel**
4. **hotels.RoomType**
5. **hotels.Room**
6. **guests.Guest**
7. **reservations.Reservation**
8. **payments.Payment**
9. **housekeeping.HousekeepingTask**

**For EACH model:**
1. Write test first (`test_models.py`)
2. Implement model
3. Run test
4. Create migration
5. Register in admin
6. Test in admin panel

### Phase 5: Configure Testing

1. **Create pytest.ini**
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = config.settings.development
   python_files = tests.py test_*.py *_tests.py
   addopts = --cov=apps --cov-report=html --cov-report=term-missing
   ```

2. **Create conftest.py** (pytest fixtures)
   ```python
   import pytest
   from django.contrib.auth import get_user_model

   @pytest.fixture
   def user():
       User = get_user_model()
       return User.objects.create_user(
           email='test@example.com',
           password='testpass123'
       )
   ```

### Phase 6: Git Setup

1. **Initialize Git**
   ```bash
   git init
   ```

2. **Create .gitignore**
   ```
   venv/
   __pycache__/
   *.py[cod]
   .env
   db.sqlite3
   media/
   .coverage
   htmlcov/
   .pytest_cache/
   ```

3. **First commit**
   ```bash
   git add .
   git commit -m "Initial Django project setup for Hotel PMS"
   ```

---

## 🔑 Environment Variables (.env)

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Database
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-supabase-password
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Redis (for development, use local)
REDIS_URL=redis://localhost:6379/0

# Stripe (use test keys)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## ✅ Success Criteria

After setup, you should be able to:
1. ✅ Run `python manage.py runserver` successfully
2. ✅ Access Django admin at http://localhost:8000/admin
3. ✅ Run `pytest` and see 0 failures
4. ✅ Create a superuser and log into admin
5. ✅ Connect to Supabase PostgreSQL successfully

---

## 📊 Estimated Time

- Phase 1 (Environment): 10 minutes
- Phase 2 (Django Init): 15 minutes
- Phase 3 (Create Apps): 10 minutes
- Phase 4 (First Model): 30 minutes (with tests!)
- Phase 5 (Testing Config): 10 minutes
- Phase 6 (Git): 5 minutes

**Total: ~1.5 hours to fully configured Django project with first model**

---

## 🔄 Next Steps After Setup

1. Design complete database schema
2. Write tests for all models
3. Implement all models
4. Configure Django admin for all models
5. Build availability calculation logic
6. Create front desk UI templates
7. Integrate Stripe payments
8. Set up Celery for background tasks

---

## 📝 Notes

- Using Django 5.0 (latest stable)
- Python 3.13.7 detected (excellent, latest version)
- Test-first development enforced
- Supabase PostgreSQL as primary database
- Supabase Storage for file uploads
- Django Admin for back office (saves 50+ hours!)
