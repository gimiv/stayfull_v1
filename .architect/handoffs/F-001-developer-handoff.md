# F-001 Developer Handoff: Stayfull PMS Core

**Feature**: F-001 - Stayfull PMS Core
**From**: Senior Product Architect
**To**: Developer
**Date**: 2025-10-22
**Estimated Effort**: 2-3 weeks
**Priority**: P1 (Critical - Foundation)

---

## 📋 What You're Building

You are implementing the core Property Management System (PMS) for Stayfull. This is the foundation that all 21 AI features will build upon.

**Core Entities:**
1. Hotel - Represents a hotel property
2. RoomType - Categories of rooms (Standard, Deluxe, Suite)
3. Room - Individual room units
4. Guest - Hotel guests
5. Reservation - Bookings/reservations
6. Staff - Hotel employees

**Key Functionality:**
- Multi-tenant hotel management
- Room inventory and availability tracking
- Reservation system with check-in/check-out
- Guest management
- RESTful API for all operations
- Django Admin for back-office

---

## 📖 Complete Specification

**CRITICAL: Read this first**
👉 `.architect/features/current/F-001-stayfull-pms-core.spec.md`

This 400+ line document contains:
- Complete domain model definitions
- All API endpoint specifications
- Business rules and validation
- Test scenarios (47+ tests)
- Integration points with other features
- Success criteria

**Do not start coding until you've read the entire specification.**

---

## 🏗️ Tech Stack (Confirmed)

**Backend:**
- Django 5.x
- Django REST Framework
- Python 3.13.7

**Database:**
- Supabase PostgreSQL (use existing subscription)
- Database connection details: [To be provided]

**Testing:**
- pytest
- pytest-django
- pytest-cov (target: >80% coverage)
- factory_boy (for test fixtures)

**Tools:**
- Django Admin (for back-office)
- drf-spectacular (API documentation)

---

## 📁 Project Structure to Create

```
stayfull_v1/
├── manage.py
├── pytest.ini
├── setup.cfg
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── production.txt
│
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── apps/
    ├── __init__.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── models.py        # BaseModel with UUID, timestamps
    │   ├── managers.py      # Custom managers
    │   └── mixins.py        # Reusable mixins
    │
    ├── hotels/
    │   ├── __init__.py
    │   ├── models.py        # Hotel, RoomType, Room
    │   ├── admin.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests/
    │       ├── __init__.py
    │       ├── test_models.py
    │       ├── test_views.py
    │       └── factories.py
    │
    ├── guests/
    │   ├── __init__.py
    │   ├── models.py        # Guest
    │   ├── admin.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests/
    │
    ├── reservations/
    │   ├── __init__.py
    │   ├── models.py        # Reservation
    │   ├── admin.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── services.py      # Business logic (availability, etc.)
    │   └── tests/
    │
    └── staff/
        ├── __init__.py
        ├── models.py        # Staff
        ├── admin.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        └── tests/
```

---

## 🚀 Implementation Steps

### Phase 1: Environment & Project Setup (Day 1)

**1.1 Create Virtual Environment**
```bash
cd /Users/mergimkacija/stayfull_v1
python3 -m venv venv
source venv/bin/activate
```

**1.2 Create Requirements Files**

Create `requirements/base.txt`:
```
Django==5.0.10
djangorestframework==3.14.0
psycopg2-binary==2.9.9
django-environ==0.11.2
drf-spectacular==0.27.0
```

Create `requirements/dev.txt`:
```
-r base.txt
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
black==23.12.1
flake8==7.0.0
mypy==1.7.1
django-extensions==3.2.3
ipython==8.19.0
```

**1.3 Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements/dev.txt
```

**1.4 Initialize Django Project**
```bash
django-admin startproject config .
```

**1.5 Restructure Settings**
- Move `config/settings.py` to `config/settings/base.py`
- Create `development.py` and `production.py`
- Configure `django-environ` for environment variables

**1.6 Configure Supabase PostgreSQL**

Create `.env` file:
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-supabase-password
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432
```

In `settings/base.py`:
```python
import environ

env = environ.Env()
environ.Env.read_env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('SUPABASE_DB_NAME'),
        'USER': env('SUPABASE_DB_USER'),
        'PASSWORD': env('SUPABASE_DB_PASSWORD'),
        'HOST': env('SUPABASE_DB_HOST'),
        'PORT': env('SUPABASE_DB_PORT'),
    }
}
```

**1.7 Configure pytest**

Create `pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = tests.py test_*.py *_tests.py
addopts = --cov=apps --cov-report=html --cov-report=term-missing
```

**1.8 Test Database Connection**
```bash
python manage.py check
python manage.py migrate
```

**Expected Outcome**: Django connects to Supabase successfully, migrations run.

---

### Phase 2: Core App & Base Models (Day 2)

**2.1 Create Core App**
```bash
mkdir -p apps/core
python manage.py startapp core apps/core
```

**2.2 Create Base Model**

In `apps/core/models.py`:
```python
import uuid
from django.db import models

class BaseModel(models.Model):
    """Base model with UUID and timestamps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**2.3 Configure INSTALLED_APPS**

In `settings/base.py`:
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
    'drf_spectacular',

    # Local apps
    'apps.core',
]
```

---

### Phase 3: Hotel Models (Days 3-4)

**3.1 Create Hotels App**
```bash
mkdir -p apps/hotels
python manage.py startapp hotels apps/hotels
```

**3.2 Implement Models**

Follow the specifications in section 2 of the spec document:
- Hotel model (section 2.1)
- RoomType model (section 2.2)
- Room model (section 2.3)

**Key Implementation Notes:**
- Use `JSONField` for address, contact, settings
- Add proper validation in `clean()` methods
- Create database indexes on foreign keys
- Implement `__str__()` methods for admin display

**3.3 Write Model Tests**

In `apps/hotels/tests/test_models.py`:
- Test hotel creation with valid data
- Test slug auto-generation
- Test validation rules
- Test relationships

**3.4 Create Factories**

In `apps/hotels/tests/factories.py`:
```python
import factory
from apps.hotels.models import Hotel, RoomType, Room

class HotelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hotel

    name = factory.Sequence(lambda n: f'Hotel {n}')
    # ... etc
```

**3.5 Register in Admin**

In `apps/hotels/admin.py`:
```python
from django.contrib import admin
from .models import Hotel, RoomType, Room

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'total_rooms', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'slug']
```

**3.6 Create & Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**3.7 Run Tests**
```bash
pytest apps/hotels/tests/
```

**Expected Outcome**: All hotel models created, tests passing, visible in Django Admin.

---

### Phase 4: Guest Models (Day 5)

**4.1 Create Guests App**
```bash
mkdir -p apps/guests
python manage.py startapp guests apps/guests
```

**4.2 Implement Guest Model**

Follow specification section 2.4:
- Implement all fields
- **IMPORTANT**: Encrypt `id_document_number` field
- Add email uniqueness constraint
- Implement preferences JSON validation

**4.3 Write Tests & Create Admin**
- Model tests
- Factory
- Admin registration

---

### Phase 5: Reservation Models (Day 6)

**5.1 Create Reservations App**
```bash
mkdir -p apps/reservations
python manage.py startapp reservations apps/reservations
```

**5.2 Implement Reservation Model**

Follow specification section 2.5:
- All fields including status, source enums
- Auto-calculation methods for nights, total_amount
- Confirmation number generation

**5.3 Implement Business Logic**

In `apps/reservations/services.py`:
```python
class ReservationService:
    @staticmethod
    def generate_confirmation_number():
        # Generate unique 8-12 char code
        pass

    @staticmethod
    def calculate_total(rate, nights, taxes, fees, extras, discounts):
        # Calculate total amount
        pass

    @staticmethod
    def check_availability(hotel_id, room_type_id, check_in, check_out):
        # Check room availability
        pass
```

**5.4 Write Tests**
- Confirmation number generation (uniqueness)
- Total calculation
- Availability algorithm (critical!)
- Overlapping reservation prevention

---

### Phase 6: Staff Models (Day 7)

**6.1 Create Staff App**
```bash
mkdir -p apps/staff
python manage.py startapp staff apps/staff
```

**6.2 Implement Staff Model**

Follow specification section 2.6

---

### Phase 7: API Endpoints - Hotels (Days 8-9)

**7.1 Create Serializers**

In `apps/hotels/serializers.py`:
```python
from rest_framework import serializers
from .models import Hotel, RoomType, Room

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def validate(self, data):
        # Implement business rules validation
        pass
```

**7.2 Create ViewSets**

In `apps/hotels/views.py`:
```python
from rest_framework import viewsets
from .models import Hotel
from .serializers import HotelSerializer

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_queryset(self):
        # Implement multi-tenancy filtering
        pass
```

**7.3 Configure URLs**

In `apps/hotels/urls.py`:
```python
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)

urlpatterns = router.urls
```

In `config/urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.hotels.urls')),
    # ... other apps
]
```

**7.4 Write API Tests**

In `apps/hotels/tests/test_views.py`:
- Test GET /api/v1/hotels (list)
- Test GET /api/v1/hotels/{id} (retrieve)
- Test POST /api/v1/hotels (create)
- Test PATCH /api/v1/hotels/{id} (update)
- Test validation errors (400 responses)
- Test authentication/authorization

---

### Phase 8: API Endpoints - Reservations (Days 10-12)

**8.1 Implement All Reservation Endpoints**

Follow specification section 3.5:
- List reservations
- Create reservation
- Get reservation details
- Update reservation
- Check-in endpoint
- Check-out endpoint
- Cancel endpoint

**8.2 Implement Availability Endpoint**

This is **critical** - follow specification section 3.6:
```python
@action(detail=False, methods=['post'])
def check_availability(self, request, hotel_id):
    # Implement availability algorithm
    # See spec for detailed logic
    pass
```

**8.3 Write Comprehensive Tests**

Test all scenarios from specification section 4.5:
- Availability calculation
- Overlapping prevention
- Check-in/check-out flow
- Cancellation
- Status transitions

---

### Phase 9: API Documentation (Day 13)

**9.1 Configure drf-spectacular**

In `settings/base.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Stayfull API',
    'VERSION': '1.0.0',
}
```

**9.2 Generate API Docs**
```bash
python manage.py spectacular --file schema.yml
```

**9.3 Access Swagger UI**
http://localhost:8000/api/schema/swagger-ui/

---

### Phase 10: Testing & QA (Days 14-15)

**10.1 Run Full Test Suite**
```bash
pytest
```

**Target**: >80% coverage

**10.2 Check Coverage Report**
```bash
pytest --cov-report=html
open htmlcov/index.html
```

**10.3 Code Quality**
```bash
black apps/
flake8 apps/
mypy apps/
```

**10.4 Manual Testing**
- Test all endpoints in Postman/Insomnia
- Test Django Admin functionality
- Test edge cases
- Test error handling

---

## ✅ Definition of Done

Before marking F-001 as complete, verify:

### Code Complete
- [ ] All 6 models created (Hotel, RoomType, Room, Guest, Reservation, Staff)
- [ ] All migrations run successfully
- [ ] All API endpoints implemented (see spec section 3)
- [ ] All business rules enforced (see spec section 2)
- [ ] Django Admin configured for all models

### Testing
- [ ] Unit tests for all models
- [ ] Integration tests for all API endpoints
- [ ] Test coverage >80%
- [ ] All 47+ test scenarios from spec passing
- [ ] No failing tests

### Quality
- [ ] Code formatted with black
- [ ] No flake8 warnings
- [ ] No mypy type errors
- [ ] No security vulnerabilities (run `bandit`)

### Documentation
- [ ] API documentation generated (Swagger/OpenAPI)
- [ ] All endpoints documented
- [ ] README updated with setup instructions

### Performance
- [ ] API response times <200ms p95
- [ ] Database queries optimized (no N+1)
- [ ] Proper indexes on foreign keys

### Deployment Ready
- [ ] Works with Supabase PostgreSQL
- [ ] Environment variables configured
- [ ] Can create superuser and access admin
- [ ] Sample data seeded for testing

---

## 🧪 How to Test Your Implementation

### 1. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 2. Run Server
```bash
python manage.py runserver
```

### 3. Access Admin
http://localhost:8000/admin

### 4. Create Test Data
- Create a hotel
- Create room types (Standard, Deluxe)
- Create 10 rooms
- Create a guest
- Create a reservation

### 5. Test API
```bash
# List hotels
curl http://localhost:8000/api/v1/hotels/

# Check availability
curl -X POST http://localhost:8000/api/v1/hotels/{hotel_id}/check-availability \
  -H "Content-Type: application/json" \
  -d '{"check_in_date": "2025-11-01", "check_out_date": "2025-11-03", "adults": 2}'

# Create reservation
curl -X POST http://localhost:8000/api/v1/hotels/{hotel_id}/reservations \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

### 6. Run Tests
```bash
pytest --cov
```

---

## 🚨 Critical Implementation Notes

### Security
1. **Encrypt `id_document_number`** - Use Django's encryption at field level
2. **Multi-tenancy** - CRITICAL: Implement proper data isolation
3. **API Authentication** - Use Django REST Framework authentication
4. **Input Validation** - Validate all user input, never trust client data

### Performance
1. **Avoid N+1 queries** - Use `select_related()` and `prefetch_related()`
2. **Add indexes** - On all foreign keys and frequently queried fields
3. **Optimize availability query** - This will be called frequently

### Business Logic
1. **Confirmation number** - Must be globally unique, 8-12 chars
2. **Availability algorithm** - Must prevent double-booking at all costs
3. **Status transitions** - Follow allowed state machine (spec section 2.5)
4. **Total calculation** - Must be accurate for financial integrity

---

## 📞 Questions?

If you encounter ambiguity or have questions:
1. Check the complete specification first
2. Check Django/DRF documentation
3. Ask the architect for clarification

**Do NOT:**
- Skip tests
- Ignore validation rules
- Change the API contract without approval
- Deploy without >80% test coverage

---

## 📦 Deliverables

When you're done, you should have:
1. ✅ Working Django project connected to Supabase
2. ✅ All 6 models with migrations
3. ✅ All API endpoints functional
4. ✅ Django Admin fully configured
5. ✅ >80% test coverage
6. ✅ API documentation generated
7. ✅ README with setup instructions

**Commit your code frequently with clear messages:**
```bash
git commit -m "feat: Add Hotel and RoomType models with tests"
git commit -m "feat: Implement reservation check-in/out flow"
git commit -m "test: Add availability algorithm tests"
```

---

## 🎯 Success Looks Like

When you're done:
- Hotel admin can log into Django Admin and manage hotels, rooms, guests
- API clients can check availability and create reservations
- No double-booking possible (validated by tests)
- All business rules enforced
- Fast (<200ms) API responses
- Ready for F-002 (AI Onboarding Agent) to integrate

---

**Good luck! You're building the foundation of Stayfull. 🏨**

**Estimated Start Date**: [Your choice]
**Target Completion**: 2-3 weeks from start

---

**Architect Signature**: Senior Product Architect
**Date**: 2025-10-22
