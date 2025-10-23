# 📋 Decision 002: Hotel PMS Tech Stack Reassessment
**Date**: 2025-10-22
**Status**: ✅ APPROVED - Django + Supabase
**Architect**: Senior Product Architect
**Impact**: CRITICAL - Correcting course for hotel-specific requirements
**User Decision**: Approved Django recommendation

---

## 🚨 Context Update

**CRITICAL DISCOVERY**: The project is a **Hotel Management System (PMS)**, NOT general property management.

This fundamentally changes the requirements:

### Hotel PMS Requirements
1. **Front Desk Operations**
   - Check-in/check-out flow (must be <100ms response time)
   - Real-time room availability
   - Guest registration with ID scanning
   - Payment processing at check-out

2. **Housekeeping Management**
   - Real-time room status updates
   - Task assignment and tracking
   - Priority management
   - Inspection workflows

3. **Reservation System**
   - Room inventory management
   - Booking calendar
   - Rate management (seasonal, weekday/weekend)
   - Online booking integration (future)

4. **Back Office**
   - Room type configuration
   - Rate management
   - Staff management
   - Comprehensive reporting
   - Revenue analytics

5. **Integration Needs** (future phases)
   - Channel managers (Booking.com, Expedia)
   - POS systems (restaurant, bar)
   - Payment gateways
   - Accounting software

---

## 🎯 Revised Tech Stack Analysis

### Option 1: Django + Django REST Framework ⭐⭐⭐ STRONGLY RECOMMENDED

**Why Django is Superior for Hotel PMS:**

1. **Admin Panel = Back Office System** (saves 60-100+ hours)
   - Room type management
   - Rate configuration
   - Staff management
   - Report generation
   - Audit logs
   - All of this comes FREE with Django admin

2. **Complex Business Logic**
   - Availability calculations (room conflicts, overbooking protection)
   - Dynamic pricing rules
   - Housekeeping workflows
   - Check-out billing (room charges + extras)
   - Django ORM handles this better than TypeScript

3. **Background Jobs (Celery)**
   - Automated check-out at 11 AM
   - Housekeeping task generation
   - Automated reminders
   - Report generation
   - Payment retry logic
   - Email confirmations

4. **Proven Hotel PMS Packages**
   - django-hotels (existing packages to reference)
   - Strong booking/reservation libraries
   - Mature payment integrations
   - Reporting frameworks

5. **Data Integrity**
   - Hotel operations require ACID compliance
   - No double-booking allowed
   - Django ORM + PostgreSQL transactions are bulletproof

6. **Integration Capabilities**
   - REST API for channel managers
   - Webhook handling for payments
   - Third-party system integration
   - Django has mature libraries for everything

**Django Stack:**
```
Backend:         Django 5.x + Django REST Framework
Database:        Supabase PostgreSQL (use existing subscription!)
Cache:           Redis (for room availability caching)
Queue:           Celery + Redis (background jobs)
Storage:         Supabase Storage (guest documents, receipts)
Auth:            Django AllAuth + JWT
API:             Django REST Framework (for mobile/integrations)

Frontend:
- Internal:      Django Admin (back office) + Django Templates (front desk)
- Guest Portal:  React/Next.js (future phase)

Testing:         pytest + pytest-django
Deployment:      Railway/Render ($10-20/month)
```

**Cost:**
- Railway/Render: $10-20/month
- Supabase: $0 (already subscribed - use for database + storage)
- Redis: $0 (Railway includes it)
- **Total: $10-20/month** (vs $0 for pure Supabase, but saves 100+ dev hours)

---

### Option 2: Next.js + Supabase (Original Recommendation)

**Why This is LESS Suitable for Hotel PMS:**

1. **No Admin Panel**
   - Have to build every back-office page manually
   - Room configuration UI: 8-10 hours
   - Rate management UI: 10-15 hours
   - Staff management UI: 8-10 hours
   - Reports UI: 20-30 hours
   - **Total: 50-70 hours of manual UI building**

2. **Complex Logic in TypeScript**
   - Availability calculations are complex
   - Dynamic pricing rules harder to maintain
   - Less mature libraries for hotel operations

3. **Background Jobs**
   - Vercel Cron is limited
   - Can't run long-running tasks
   - Expensive at scale

4. **Real-time is Overhyped for This Use Case**
   - Yes, Supabase has real-time
   - But front desk doesn't need millisecond updates
   - Polling every 5-10 seconds is fine
   - Can add real-time later via Django Channels if needed

**Verdict:** Saves $20/month but costs 70+ hours of development time. Not worth it.

---

### Option 3: Hybrid Approach ⭐⭐ ACCEPTABLE COMPROMISE

```
Backend:         Django (back office, APIs, business logic)
Database:        Supabase PostgreSQL
Storage:         Supabase Storage
Back Office:     Django Admin
Front Desk:      Next.js (fast, modern UI for check-in/out)
Guest Portal:    Next.js (future)
```

**Pros:**
- Django admin for back office
- Modern front desk interface
- Uses existing Supabase
- Best of both worlds

**Cons:**
- More complex architecture
- Two deployments (Django + Next.js)
- More maintenance overhead
- Overkill for MVP

**Verdict:** Good for later phase, but too complex for MVP.

---

## 🏆 Final Recommendation

### Use Django + Supabase PostgreSQL

**Architecture:**
```
┌─────────────────────────────────────────┐
│   Django Admin (Back Office)            │
│   - Room/Rate Management                │
│   - Staff Management                    │
│   - Reports & Analytics                 │
├─────────────────────────────────────────┤
│   Django Templates (Front Desk)         │
│   - Check-in/Check-out                  │
│   - Quick Guest Registration            │
│   - Housekeeping Dashboard              │
├─────────────────────────────────────────┤
│   Django REST API                       │
│   - Mobile apps (future)                │
│   - Channel manager integration         │
│   - Third-party systems                 │
├─────────────────────────────────────────┤
│   Business Logic Layer                  │
│   - Availability Engine                 │
│   - Pricing Rules                       │
│   - Workflow Management                 │
├─────────────────────────────────────────┤
│   Supabase PostgreSQL                   │
│   (existing subscription)               │
├─────────────────────────────────────────┤
│   Celery + Redis                        │
│   - Auto check-out                      │
│   - Housekeeping tasks                  │
│   - Email notifications                 │
├─────────────────────────────────────────┤
│   Supabase Storage                      │
│   - Guest ID documents                  │
│   - Receipts & invoices                 │
└─────────────────────────────────────────┘

Deployment: Railway/Render ($15/month)
```

**Implementation Timeline:**
- Week 1: Django setup, models, admin panel
- Week 2: Reservation system, availability logic
- Week 3: Check-in/out flow, payment integration
- Week 4: Housekeeping module, reporting
- **MVP Ready: 4 weeks**

With Next.js: Add 2-3 weeks for manual UI building.

---

## 💡 Why I Changed My Recommendation Too Quickly

I optimized for "free infrastructure" when I heard about Supabase/Vercel subscriptions, without fully understanding:

1. **The domain** - Hotels need different architecture than I initially assumed
2. **Time-to-market** - Django admin alone justifies the $15/month cost
3. **Maintenance** - Complex hotel logic is easier in Python/Django
4. **Integrations** - Hotels need to integrate with many systems (Django excels here)

---

## 📊 Comparison Table

| Aspect | Django + Supabase | Next.js + Supabase |
|--------|-------------------|-------------------|
| **Development Speed** | ⭐⭐⭐⭐⭐ (Admin panel free) | ⭐⭐⭐ (Build everything) |
| **Back Office** | ⭐⭐⭐⭐⭐ (Django Admin) | ⭐⭐ (Manual build) |
| **Front Desk** | ⭐⭐⭐⭐ (Fast enough) | ⭐⭐⭐⭐⭐ (Modern UI) |
| **Business Logic** | ⭐⭐⭐⭐⭐ (Python ORM) | ⭐⭐⭐ (TypeScript) |
| **Background Jobs** | ⭐⭐⭐⭐⭐ (Celery) | ⭐⭐ (Vercel Cron) |
| **Integrations** | ⭐⭐⭐⭐⭐ (Mature libs) | ⭐⭐⭐ (Less mature) |
| **Cost** | $15-20/month | $0/month |
| **Time to MVP** | 4 weeks | 6-7 weeks |
| **Long-term Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## ✅ Decision

**Switch to Django + Supabase PostgreSQL + Supabase Storage**

**Rationale:**
- Saves 50-70 hours of development time (pays for 3+ years of hosting)
- Better suited for hotel PMS requirements
- Easier to maintain complex business logic
- Can still use existing Supabase subscription for database + storage
- Can add Next.js front-end later if needed

**Next Steps:**
1. Initialize Django project
2. Connect to Supabase PostgreSQL
3. Design database schema (hotel-specific)
4. Set up Django admin
5. Build core reservation system

---

## 🔄 Review Date
Re-evaluate front-end after MVP is in production and we have user feedback.
