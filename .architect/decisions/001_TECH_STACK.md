# 📋 Decision 001: Technology Stack
**Date**: 2025-10-22
**Status**: PROPOSED
**Architect**: Senior Product Architect
**Impact**: CRITICAL - Affects entire project foundation

---

## 🎯 Context
Building a production-grade Property Management System requiring:
- Multi-tenancy support
- Payment processing integration
- Document/image management
- Role-based access control (Landlords, Tenants, Admins)
- Reporting and analytics
- High reliability and security
- Scalability for multiple properties
- Mobile-friendly (potential native apps later)

---

## 🔍 Technology Stack Options & Recommendations

### Backend Framework

#### Option 1: **Django + Django REST Framework** ⭐ RECOMMENDED
**Pros:**
- Batteries-included (ORM, admin panel, auth out of box)
- Excellent for business applications
- Strong security features built-in
- Mature ecosystem for payments (Stripe, etc.)
- Great testing framework
- Fast development velocity
- Built-in multi-tenancy packages available

**Cons:**
- Slightly heavier than microframeworks
- Python async support not as mature as Node

**Verdict**: Best fit for property management - rapid development with enterprise features.

#### Option 2: FastAPI
**Pros:**
- Modern async Python
- Automatic API documentation
- Fast performance
- Type hints and validation

**Cons:**
- Less batteries-included
- Smaller ecosystem
- More manual setup for admin features

#### Option 3: Node.js (Express/NestJS)
**Pros:**
- JavaScript full-stack
- Large ecosystem
- Good async performance

**Cons:**
- Less structure for complex business logic
- More decision fatigue
- TypeScript setup complexity

---

### Database

#### Option 1: **PostgreSQL** ⭐ RECOMMENDED
**Pros:**
- Rock-solid reliability
- JSONB for flexible data
- Excellent for financial data (ACID compliance)
- Row-level security for multi-tenancy
- Full-text search built-in
- Free and open-source

**Cons:**
- Slightly more setup than SQLite

**Verdict**: Industry standard for business applications.

#### Option 2: MySQL
**Pros:**
- Widely supported
- Good performance

**Cons:**
- Less advanced features than PostgreSQL
- JSON support inferior

---

### Authentication

#### Option 1: **Django AllAuth + JWT** ⭐ RECOMMENDED
**Pros:**
- Mature Django integration
- Social auth ready
- Email verification built-in
- Session + token auth options

**Cons:**
- Django-specific

**Verdict**: Perfect match for Django backend.

#### Option 2: Auth0 / Clerk
**Pros:**
- Managed service
- Modern UI

**Cons:**
- Monthly costs
- External dependency
- Less control

---

### Payment Processing

#### Option 1: **Stripe** ⭐ RECOMMENDED
**Pros:**
- Best developer experience
- Comprehensive documentation
- Handles subscriptions, one-time payments
- Automatic tax calculation
- Built-in customer portal
- Excellent Python SDK

**Cons:**
- 2.9% + 30¢ fee

**Verdict**: Industry leader, worth the fees.

#### Option 2: PayPal
**Pros:**
- Widely recognized
- Lower fees in some regions

**Cons:**
- Worse developer experience
- Less reliable API

---

### File Storage

#### Option 1: **AWS S3 + CloudFront** ⭐ RECOMMENDED
**Pros:**
- Extremely reliable
- CDN integration
- Django-storages support
- Affordable at scale

**Cons:**
- Requires AWS account

**Verdict**: Industry standard.

#### Option 2: Local + Backblaze B2
**Pros:**
- Cheaper than AWS
- S3-compatible

**Cons:**
- Less integrated
- Smaller ecosystem

---

### Task Queue

#### Option 1: **Celery + Redis** ⭐ RECOMMENDED
**Pros:**
- Standard for Django
- Handles async tasks (emails, reports, payments)
- Mature and battle-tested
- Good monitoring tools

**Cons:**
- Extra infrastructure

**Verdict**: Essential for background tasks.

---

### Frontend (Initial)

#### Option 1: **Django Templates + HTMX** ⭐ RECOMMENDED FOR MVP
**Pros:**
- Fastest time to market
- No build step
- Server-side rendering
- Progressive enhancement
- Can migrate to SPA later

**Cons:**
- Not as "modern" feeling

**Verdict**: Perfect for rapid MVP, can add React later.

#### Option 2: React + Next.js
**Pros:**
- Modern UX
- Great for complex interactions

**Cons:**
- Slower initial development
- More complexity
- Build pipeline needed

**Later Phase**: Add React admin panel after MVP.

---

### Testing

#### Option 1: **pytest + pytest-django** ⭐ RECOMMENDED
**Pros:**
- Best Python testing framework
- Clean syntax
- Excellent fixture system
- Great Django integration

**Cons:**
- None significant

**Verdict**: Standard choice.

---

### Deployment

#### Option 1: **Docker + Railway/Render** ⭐ RECOMMENDED FOR MVP
**Pros:**
- Simple deployment
- Affordable ($5-20/month initially)
- PostgreSQL included
- Auto-scaling
- CI/CD built-in

**Cons:**
- Less control than AWS

**Verdict**: Best for early stage.

#### Option 2: AWS (ECS/EC2)
**Later Phase**: Migrate when scaling requires it.

---

## 🎯 Final Recommended Stack (REVISED for Supabase + Vercel)

```
Frontend:    Next.js 14+ (App Router) + React + TypeScript
Backend:     Next.js API Routes + Server Actions
Database:    Supabase PostgreSQL (already subscribed)
Auth:        Supabase Auth (already included)
Storage:     Supabase Storage (already included)
Payments:    Stripe
Real-time:   Supabase Realtime (bonus feature)
API Client:  Supabase JS Client
UI:          shadcn/ui + Tailwind CSS
Forms:       React Hook Form + Zod validation
Testing:     Vitest + React Testing Library + Playwright
Deployment:  Vercel (already subscribed)
Monitoring:  Vercel Analytics + Sentry
```

### 💰 Cost Savings
- Supabase (existing): Covers database, auth, storage, real-time
- Vercel (existing): Covers hosting, CDN, serverless functions
- **New monthly costs**: ~$0 (using existing subscriptions!)
- Only variable cost: Stripe transaction fees

---

## 📊 Architecture Layers (REVISED)

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js + React)            │
│   ├─ app/                              │
│   │   ├─ (auth)/                       │
│   │   ├─ dashboard/                    │
│   │   ├─ properties/                   │
│   │   ├─ tenants/                      │
│   │   └─ payments/                     │
│   └─ components/ (shadcn/ui)           │
├─────────────────────────────────────────┤
│   API Layer (Next.js)                   │
│   ├─ app/api/ (REST endpoints)         │
│   └─ Server Actions (mutations)        │
├─────────────────────────────────────────┤
│   Business Logic (TypeScript)           │
│   ├─ lib/services/                     │
│   ├─ lib/validations/ (Zod schemas)    │
│   └─ lib/utils/                        │
├─────────────────────────────────────────┤
│   Supabase Layer                        │
│   ├─ PostgreSQL (with RLS)             │
│   ├─ Auth (JWT + Social)               │
│   ├─ Storage (S3-compatible)           │
│   └─ Realtime subscriptions            │
├─────────────────────────────────────────┤
│   External Services                     │
│   ├─ Stripe (Payments)                 │
│   ├─ Vercel Cron (scheduled jobs)      │
│   └─ Resend/SendGrid (Email)           │
└─────────────────────────────────────────┘

Deployment: Vercel Edge Network (Global CDN)
```

---

## ✅ Decision Rationale (REVISED)

**Why Next.js + Supabase:**
1. **Zero additional infrastructure costs** - Already subscribed!
2. Modern, scalable architecture designed to work together
3. TypeScript end-to-end for type safety
4. Server-side rendering + static generation (best SEO)
5. Fast development with amazing DX

**Why Supabase specifically:**
1. **PostgreSQL** - ACID compliance for financial data
2. **Row Level Security** - Perfect for multi-tenancy (landlords see only their properties)
3. **Built-in Auth** - Social login, JWT, email verification out of box
4. **Storage** - S3-compatible, handles documents/images
5. **Realtime** - Live updates for maintenance requests, payments (bonus!)
6. **Auto-generated APIs** - Instant REST/GraphQL endpoints
7. **Database migrations** - Built-in versioning

**Why Next.js specifically:**
1. **Server Actions** - Simplify data mutations without API boilerplate
2. **React Server Components** - Better performance, less JS to client
3. **App Router** - Modern routing with layouts
4. **Vercel deployment** - One command deploy with preview URLs
5. **Middleware** - Auth protection, rate limiting
6. **API Routes** - Custom endpoints when needed (Stripe webhooks)

**Why TypeScript + Zod:**
1. Compile-time type safety prevents bugs
2. Zod runtime validation ensures data integrity
3. Type inference from database schema (Supabase generates types!)
4. Better IDE autocomplete and refactoring

**Why Stripe:**
1. Handles recurring rent payments elegantly
2. Automatic failed payment retry
3. Customer portal for tenants
4. Best documentation
5. Excellent Next.js integration

---

## 🚀 Implementation Order (REVISED)

1. **Phase 1 (Week 1)**: Foundation
   - Next.js project with TypeScript
   - Supabase setup & connection
   - Database schema design
   - Row Level Security policies
   - Auth flow (login/signup/logout)
   - shadcn/ui components setup

2. **Phase 2 (Week 2-3)**: Core features
   - Property CRUD with tests
   - Landlord dashboard
   - Tenant management
   - Lease tracking
   - Image uploads (Supabase Storage)

3. **Phase 3 (Week 4)**: Payments
   - Stripe integration
   - Checkout flow
   - Payment tracking
   - Automated rent billing
   - Tenant payment portal

4. **Phase 4 (Week 5+)**: Enhancement
   - Maintenance requests (with realtime updates!)
   - Document management
   - Reporting & analytics
   - Email notifications
   - Mobile responsiveness polish

---

## 📝 Notes
- Leveraging existing Supabase + Vercel subscriptions = **$0 additional infrastructure cost**
- Modern stack with excellent developer experience
- Type-safe end-to-end (TypeScript + Zod + Supabase types)
- Can scale to thousands of properties
- Real-time capabilities included (bonus feature!)
- Amazing CI/CD with Vercel preview deployments
- Supabase Row Level Security = built-in multi-tenancy

---

## 🔄 Review Date
Re-evaluate after 3 months or at 100 active properties.
