# 🏨 Stayfull System Architecture - AI-First Hotel Platform
Last Updated: 2025-10-22 (Django + AI Infrastructure Finalized)
Status: ✅ READY TO BUILD
Vision: 21 AI Features | 10-Minute Setup | 98% Automation

## 🎨 Architecture Philosophy
- **AI-First**: Every feature powered by AI, not just AI-assisted
- **Zero Integration**: All 21 features native in one platform
- **10-Minute Setup**: Conversational onboarding, not forms
- **98% Automation**: Minimize human intervention
- **Test Everything**: 80% coverage minimum, AI accuracy >95%
- **Cost Conscious**: Track every AI API call
- **Performance Obsessed**: <200ms API, <3s AI responses
- **Security by Default**: PCI compliant, data encrypted

## 🏗️ Technology Decisions

### ✅ Final Tech Stack (Decided: 2025-10-22) - STAYFULL AI PLATFORM

**Core Platform:**
- **Framework**: Django 5.x + Django REST Framework
- **Language**: Python 3.13.7 (AI/ML optimized)
- **Admin Interface**: Django Admin (back office management)
- **Templates**: Django Templates + HTMX + Alpine.js (front desk & guest portal)
- **API**: Django REST Framework (REST endpoints for 21 features)
- **Real-time**: Django Channels (WebSockets for live updates)

**AI Infrastructure:** ⭐ CORE DIFFERENTIATOR
- **LLM Gateway**: LangChain (multi-provider orchestration)
- **Primary LLM**: OpenAI GPT-4 (onboarding, complex reasoning)
- **Secondary LLM**: OpenAI GPT-3.5-turbo (chatbot, cost-optimized)
- **Fallback LLM**: Anthropic Claude-3 (reliability)
- **Prompt Management**: LangSmith (versioning, A/B testing, analytics)
- **Vector Database**: pgvector (Supabase PostgreSQL extension for RAG)
- **Voice STT**: OpenAI Whisper (speech-to-text)
- **Voice TTS**: ElevenLabs (text-to-speech, natural voices)
- **Cost Tracking**: Custom middleware + Redis (per-hotel, per-feature)
- **Response Cache**: Redis (embedding similarity, 40% hit rate target)

**Database & Storage:**
- **Database**: Supabase PostgreSQL (with pgvector extension for embeddings)
- **Storage**: Supabase Storage (S3-compatible) - documents, receipts, AI-generated images
- **Cache**: Redis (LLM responses, embeddings, session data)
- **Search**: PostgreSQL full-text search + vector similarity

**Background Jobs:**
- **Queue**: Celery + Redis
- **AI Tasks**: Content generation, dynamic pricing, analytics, email campaigns
- **Operations**: Auto check-out, housekeeping task generation, payment reminders

**Authentication & Security:**
- **Auth**: Django AllAuth + JWT tokens
- **Permissions**: Django Permissions + Role-based access
- **Password**: Django's PBKDF2 (default, secure)
- **Multi-tenancy**: Django middleware + database filtering

**Integrations:**
- **Payments**: Stripe (for guest payments)
- **Email**: SendGrid or Django email backend
- **Monitoring**: Sentry

**Testing:**
- **Framework**: pytest + pytest-django
- **Coverage**: pytest-cov
- **Factories**: factory_boy
- **Coverage Target**: 80%+

**Third-Party Integrations:**
- **Payments**: Stripe (transaction processing, subscriptions)
- **IoT/Smart Room**: Seam.co (door locks, thermostats, access control)
- **Channel Manager**: Channex.io (OTA distribution, unified inbox)
- **Price Intelligence**: Aggregate Intelligence or similar (competitor tracking)
- **Communication**: Twilio (SMS/Voice), SendGrid (email)
- **Social Media**: Meta, Twitter/X, LinkedIn APIs (marketing automation)
- **Reviews**: Google My Business, TrustYou (reputation management)
- **Accounting**: QuickBooks/Xero (optional, financial export)

**Deployment:**
- **Platform**: Railway or Render ($15-20/month)
- **CI/CD**: GitHub Actions
- **Database**: Supabase PostgreSQL (existing)
- **Storage**: Supabase Storage (existing)
- **Static Files**: WhiteNoise

**"Zero Integration" Clarification:**
- Hotels don't need to set up multiple tools - Stayfull handles all integrations
- Backend integrates with best-in-class services
- One platform, everything connected

**Key Architectural Decisions:**
- Django Admin saves 50-70 hours of back-office UI development
- Better suited for complex hotel business logic
- Celery handles critical background jobs (check-out automation, etc.)
- Still uses existing Supabase for database + storage
- Can add React/Next.js front-end later if needed

**Decision Rationale**: See `.architect/decisions/002_HOTEL_PMS_TECH_REASSESSMENT.md`

### ✅ Other Confirmed Decisions
- Version Control: Git
- Development Method: SpecLight + TDD
- Code Generation: Claude Code
- Testing Approach: Test-first development

## 📐 System Design - Hotel PMS

### Domain Model
```
Hotel
  ↓
Room ←→ RoomType
  ↓
Reservation ←→ Guest
  ↓           ↓
Booking → Payment
  ↓
Housekeeping

Staff ←→ Role (Front Desk, Housekeeping, Manager, Admin)
```

### Core Entities

#### Hotel
- id: UUID
- name: string
- address: JSON
- contact: JSON
- total_rooms: integer
- created_at: timestamp

#### RoomType
- id: UUID
- hotel_id: UUID (FK → Hotel)
- name: string (e.g., "Standard", "Deluxe", "Suite")
- base_rate: decimal
- max_occupancy: integer
- amenities: JSON
- description: text

#### Room
- id: UUID
- hotel_id: UUID (FK → Hotel)
- room_type_id: UUID (FK → RoomType)
- room_number: string
- floor: integer
- status: enum (AVAILABLE, OCCUPIED, CLEANING, MAINTENANCE, OUT_OF_ORDER)
- created_at: timestamp

#### Guest
- id: UUID
- first_name: string
- last_name: string
- email: string
- phone: string
- id_document: string (encrypted)
- preferences: JSON
- created_at: timestamp

#### Reservation
- id: UUID
- guest_id: UUID (FK → Guest)
- room_id: UUID (FK → Room)
- check_in_date: date
- check_out_date: date
- status: enum (PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED)
- adults: integer
- children: integer
- special_requests: text
- created_at: timestamp

#### Payment
- id: UUID
- reservation_id: UUID (FK → Reservation)
- amount: decimal
- status: enum (PENDING, PAID, FAILED, REFUNDED)
- payment_method: enum (CREDIT_CARD, CASH, BANK_TRANSFER)
- transaction_id: string
- paid_at: timestamp

#### Housekeeping
- id: UUID
- room_id: UUID (FK → Room)
- assigned_to: UUID (FK → Staff)
- status: enum (PENDING, IN_PROGRESS, COMPLETED, INSPECTION_NEEDED)
- priority: enum (LOW, NORMAL, HIGH, URGENT)
- notes: text
- completed_at: timestamp

#### Staff
- id: UUID
- user_id: UUID (FK → User)
- hotel_id: UUID (FK → Hotel)
- role: enum (FRONT_DESK, HOUSEKEEPING, MANAGER, ADMIN)
- employee_id: string
- shift: JSON
- created_at: timestamp

## 🔒 Security Architecture

### Authentication
- **Strategy**: Supabase Auth with JWT
- **Methods**: Email/password, magic links, social (Google, GitHub)
- **2FA**: Supported via Supabase Auth
- **Password**: Bcrypt hashing (handled by Supabase)
- **Tokens**: JWT with configurable expiry
- **Session**: Server-side validation on protected routes

### Authorization
- **Type**: Role-Based Access Control (RBAC)
- **Row-Level Security**: PostgreSQL RLS policies in Supabase
- **Multi-tenancy**: RLS ensures landlords only see their data
- **API Protection**: Next.js middleware for route protection
- **Rate Limiting**: Vercel + Supabase built-in limits
- **Audit**: Audit logs for all mutations

### Data Security
- **Encryption at Rest**: Supabase default
- **Encryption in Transit**: TLS 1.3
- **Secrets**: Vercel environment variables
- **API Keys**: Supabase RLS policies prevent abuse

## 🚀 Deployment Architecture

### Development
- **Local**: pnpm dev (Next.js dev server)
- **Database**: Supabase cloud (dev project) or local Supabase
- **Hot Reload**: Next.js Fast Refresh
- **Debug**: VS Code + Chrome DevTools

### Production
- **Platform**: Vercel (existing subscription)
- **Database**: Supabase PostgreSQL (managed)
- **Storage**: Supabase Storage (S3-compatible)
- **CDN**: Vercel Edge Network (global)
- **Functions**: Vercel Serverless Functions
- **Cron Jobs**: Vercel Cron (for recurring billing)
- **Monitoring**: Vercel Analytics + Sentry
- **Logs**: Vercel Logs + Supabase Logs

## 📊 Performance Targets
- API Response: <200ms p95
- Database Query: <50ms p95
- Test Suite: <60 seconds
- Build Time: <2 minutes
- Deployment: <5 minutes

## 🔄 Evolution Path
1. **Phase 1**: Monolith (Current)
2. **Phase 2**: Modular Monolith
3. **Phase 3**: Services (if needed)
4. **Phase 4**: Microservices (only if required)
