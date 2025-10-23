# 📋 Decision 004: Third-Party Integrations Strategy
**Date**: 2025-10-22
**Status**: PLANNING
**Architect**: Senior Product Architect
**Impact**: CRITICAL - Defines integration architecture

---

## 🎯 "Zero Integration" Clarification

**What "Zero Integration" Means:**
- **For Hotels**: No need to set up multiple separate tools, APIs, or integrations
- **For Stayfull**: We integrate with best-in-class services on the backend
- **Value Prop**: One platform, everything connected, hotel just uses it

**Strategy**: Build the integration layer so hotels don't have to.

---

## 🔌 Confirmed Third-Party Integrations

### 1. Payments
**Service**: Stripe
**Purpose**: Payment processing, subscriptions, refunds
**Django Integration**: `django-stripe` or `dj-stripe`
**Priority**: Phase 1 (Foundation)
**Cost**: 2.9% + 30¢ per transaction
**Features Enabled**:
- F-001: PMS Core (payment collection)
- F-008: Promotions (discount codes)
- F-013: Bookkeeper (financial tracking)

---

### 2. IoT / Smart Room Control ⭐ NEW FEATURE
**Service**: Seam.co
**Purpose**: Door locks, thermostats, smart devices
**API**: REST API + webhooks
**Python SDK**: `seamapi` (official)
**Priority**: Phase 3 (Guest Experience)
**Cost**: ~$5-10/room/month
**Features Enabled**:
- **F-022: Smart Room Automation** (NEW)
  - Keyless check-in (digital keys via app/email)
  - Auto temperature adjustment (pre-arrival)
  - Energy savings (auto-off when vacant)
  - Remote access for housekeeping
  - Lock status monitoring

**Supported Devices**:
- Smart locks: August, Yale, Schlage, Salto
- Thermostats: Nest, Ecobee, Honeywell
- Access control systems

**Integration Points**:
```python
# On reservation confirmed
seam.locks.create_access_code(
    device_id=room.smart_lock_id,
    code=generate_unique_code(),
    starts_at=reservation.check_in_date,
    ends_at=reservation.check_out_date
)

# Send to guest
send_digital_key(guest.email, access_code)
```

---

### 3. Channel Management & Unified Inbox
**Service**: Channex.io
**Purpose**: OTA distribution + message aggregation
**API**: REST API + webhooks
**Python SDK**: Available
**Priority**: Phase 5 (Distribution)
**Cost**: Per reservation commission or flat fee
**Features Enabled**:
- F-017: AI Channel Manager
  - Booking.com, Expedia, Airbnb sync
  - Rate parity management
  - Inventory sync
  - Two-way calendar sync
- F-010: Unified Inbox
  - All OTA messages in one place
  - WhatsApp, email, OTA messaging
  - AI-powered auto-response

**Integration Points**:
```python
# Sync availability
channex.update_availability(
    room_type_id=room_type.channex_id,
    date=date,
    available=get_available_rooms(date)
)

# Receive messages
@webhook_handler
def handle_channex_message(data):
    message = parse_message(data)
    ai_response = generate_ai_response(message)
    channex.send_reply(message.id, ai_response)
```

---

### 4. Price Intelligence / Competitive Data
**Service**: Aggregate Intelligence (or similar)
**Purpose**: Competitor rate scraping for dynamic pricing
**API**: REST API
**Priority**: Phase 2 (Revenue & Marketing)
**Cost**: ~$50-100/month per hotel
**Features Enabled**:
- F-005: AI Dynamic Pricing
  - Real-time competitor rates
  - Market demand signals
  - Event detection
  - Price recommendations

**Integration Points**:
```python
# Daily price check
competitor_rates = aggregate.get_competitor_rates(
    location=hotel.location,
    check_in=date,
    room_type='standard'
)

# AI pricing decision
optimal_rate = ai_pricing_engine.calculate(
    our_rate=current_rate,
    competitor_avg=competitor_rates.average,
    occupancy=get_occupancy(date),
    events=get_local_events(date)
)
```

**Alternatives to Consider**:
- OTA Insight
- RateGain
- Competitor scraping (custom solution)

---

### 5. Email Service Provider
**Service**: SendGrid or Resend
**Purpose**: Transactional + marketing emails
**Django Integration**: `django-sendgrid-v5` or native
**Priority**: Phase 1 (Foundation)
**Cost**: Free tier available, ~$15-20/month at scale
**Features Enabled**:
- F-002: Onboarding (confirmation emails)
- F-004: Chat Bot (email conversations)
- F-012: AI CRM (email campaigns)

---

### 6. SMS Provider
**Service**: Twilio
**Purpose**: SMS notifications, 2FA, guest communication
**Python SDK**: `twilio` (official, excellent)
**Priority**: Phase 3
**Cost**: ~$0.0075 per SMS
**Features Enabled**:
- F-010: Unified Inbox (SMS channel)
- F-011: Guest Journey (SMS reminders)
- Check-in/out notifications
- Digital key delivery

---

### 7. Voice/Phone System
**Service**: Twilio (Voice API)
**Purpose**: Phone call handling for AI Voice Agent
**Python SDK**: `twilio`
**Priority**: Phase 3
**Cost**: ~$0.013/min inbound, $0.014/min outbound
**Features Enabled**:
- F-009: AI Voice Agent
  - Inbound reservation calls
  - Natural conversation
  - Booking completion
  - FAQ handling

**Stack**:
```
Twilio (phone) → Whisper (STT) → GPT-4 → ElevenLabs (TTS) → Twilio (phone)
```

---

### 8. Social Media APIs
**Services**: Meta (Facebook/Instagram), Twitter/X, LinkedIn
**Purpose**: Automated social media posting
**Python SDKs**: `facebook-sdk`, `tweepy`, `linkedin-api`
**Priority**: Phase 2
**Cost**: Free APIs (organic posting)
**Features Enabled**:
- F-006: Automated AI Marketing
- F-020: AI Influencer Outreach

---

### 9. Google Services
**Services**:
- Google My Business API (reviews, listing)
- Google Ads API (paid advertising)
- Google Analytics 4

**Purpose**: SEO, advertising, reputation management
**Priority**: Phase 2-4
**Features Enabled**:
- F-007: Blog Creation (SEO optimization)
- F-015: Reputation Manager (Google reviews)
- F-018: AI Marketing Suite (Google Ads)

---

### 10. Review Aggregators
**Services**: TrustYou, ReviewPro, or custom scraping
**Purpose**: Aggregate reviews from all platforms
**Priority**: Phase 4
**Features Enabled**:
- F-015: AI Reputation Manager
  - Aggregate reviews (TripAdvisor, Google, Booking.com)
  - Sentiment analysis
  - AI-generated responses
  - Issue detection

---

### 11. Accounting Software (Optional)
**Services**: QuickBooks, Xero
**Purpose**: Financial data export
**Priority**: Phase 4 (nice to have)
**Features Enabled**:
- F-013: AI Bookkeeper
  - Automatic reconciliation
  - Export to accounting software

---

## 🏗️ Integration Architecture

### Layered Approach

```
┌─────────────────────────────────────────┐
│   Django Application (Stayfull Core)    │
├─────────────────────────────────────────┤
│         Integration Layer               │
│   (Standardized internal APIs)          │
├─────────────────────────────────────────┤
│       Service Adapters                  │
│  ┌──────────┬──────────┬─────────────┐ │
│  │ Payments │ Channel  │ Smart Room  │ │
│  │ (Stripe) │(Channex) │  (Seam)     │ │
│  ├──────────┼──────────┼─────────────┤ │
│  │  Email   │   SMS    │   Voice     │ │
│  │(SendGrid)│ (Twilio) │  (Twilio)   │ │
│  ├──────────┼──────────┼─────────────┤ │
│  │  Social  │  Review  │  Pricing    │ │
│  │  Media   │  Sites   │(Aggregate)  │ │
│  └──────────┴──────────┴─────────────┘ │
└─────────────────────────────────────────┘
```

### Django App Structure

```python
apps/
├── integrations/              # NEW
│   ├── __init__.py
│   ├── models.py             # Integration credentials, logs
│   ├── base.py               # Base adapter interface
│   │
│   ├── payments/
│   │   ├── stripe_adapter.py
│   │   └── webhook_handlers.py
│   │
│   ├── iot/
│   │   ├── seam_adapter.py
│   │   └── device_manager.py
│   │
│   ├── channels/
│   │   ├── channex_adapter.py
│   │   └── message_handler.py
│   │
│   ├── pricing/
│   │   ├── aggregate_adapter.py
│   │   └── competitor_tracker.py
│   │
│   ├── communication/
│   │   ├── email_adapter.py
│   │   ├── sms_adapter.py
│   │   └── voice_adapter.py
│   │
│   └── social/
│       ├── facebook_adapter.py
│       ├── instagram_adapter.py
│       └── twitter_adapter.py
```

---

## 🔒 Integration Best Practices

### 1. Adapter Pattern
```python
class BaseIntegrationAdapter(ABC):
    """Base class for all integrations"""

    @abstractmethod
    def authenticate(self, credentials):
        pass

    @abstractmethod
    def test_connection(self):
        pass

    @abstractmethod
    def handle_webhook(self, data):
        pass

    def log_api_call(self, method, endpoint, response):
        IntegrationLog.objects.create(...)
```

### 2. Credential Management
```python
# apps/integrations/models.py
class HotelIntegration(models.Model):
    hotel = models.ForeignKey(Hotel)
    service = models.CharField(choices=SERVICE_CHOICES)
    credentials = models.JSONField(encrypted=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True)
    error_count = models.IntegerField(default=0)
```

### 3. Webhook Handling
```python
# Centralized webhook endpoint
@csrf_exempt
def webhook_handler(request, service):
    adapter = get_adapter(service)

    # Verify signature
    if not adapter.verify_webhook(request):
        return HttpResponse(status=403)

    # Process async
    process_webhook.delay(service, request.body)

    return HttpResponse(status=200)
```

### 4. Error Handling & Retries
```python
@celery_app.task(bind=True, max_retries=3)
def sync_with_channex(self, hotel_id):
    try:
        adapter = ChannexAdapter(hotel_id)
        adapter.sync_availability()
    except ApiException as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 5. Rate Limiting
```python
from ratelimit import limits

@limits(calls=100, period=60)  # 100 calls per minute
def call_stripe_api(method, **kwargs):
    return stripe.api_call(method, **kwargs)
```

---

## 💰 Integration Cost Analysis

**Per Hotel Monthly Estimates:**

| Service | Monthly Cost | Volume Assumption |
|---------|-------------|-------------------|
| Stripe | Variable | 2.9% + 30¢/transaction |
| Seam.co | $50-100 | 10-20 rooms with smart locks |
| Channex.io | $50-150 | Multi-channel distribution |
| Aggregate Intelligence | $50-100 | Competitor tracking |
| SendGrid | $15-20 | 5,000 emails/month |
| Twilio SMS | $10-20 | ~1,500 SMS/month |
| Twilio Voice | $50-100 | ~100 calls/month (F-009) |
| Google Ads API | Free | Organic only |
| Social Media APIs | Free | Organic posting |
| **Total Fixed** | **$225-490/month** | Excluding transaction fees |

**Our Pricing**: $999/month
**AI Costs**: ~$230/month
**Integration Costs**: ~$225-490/month
**Total Costs**: ~$455-720/month
**Margin**: ~28-55% (still healthy)

---

## 🎯 Integration Priority Order

### Phase 1 (Weeks 1-4): Essential
1. ✅ Stripe (payments)
2. ✅ SendGrid (email)
3. ✅ Supabase Storage (files)

### Phase 2 (Weeks 5-8): Revenue
4. Aggregate Intelligence (dynamic pricing)
5. Google My Business (SEO/reputation)
6. Social Media APIs (marketing automation)

### Phase 3 (Weeks 9-12): Guest Experience
7. Seam.co (smart room automation) ⭐ NEW
8. Twilio SMS (guest communication)
9. Twilio Voice (AI voice agent)
10. Channex.io (unified inbox)

### Phase 4 (Weeks 13-16): Operations
11. Channex.io (channel manager)
12. Review aggregation APIs
13. QuickBooks/Xero (optional)

---

## 🚀 Why Django is Perfect for This

**Python has EXCELLENT libraries for all these services:**
- ✅ Stripe: `stripe` (official, mature)
- ✅ Seam: `seamapi` (official Python SDK)
- ✅ Twilio: `twilio` (official, best-in-class)
- ✅ SendGrid: `sendgrid` (official)
- ✅ OpenAI: `openai` (official)
- ✅ Anthropic: `anthropic` (official)
- ✅ LangChain: Python-first
- ✅ Social: `facebook-sdk`, `tweepy`, etc.

**Django Benefits:**
- Centralized integration management
- Webhook handling (Django views)
- Celery for async API calls
- Built-in credential encryption
- Excellent logging & monitoring

---

## 📝 New Feature Added

### F-022: Smart Room Automation (IoT)
**Priority**: Phase 3 (Guest Experience)
**Integration**: Seam.co
**Description**: Keyless entry, smart thermostats, energy management

**Acceptance Criteria**:
- [ ] Digital key generation on booking
- [ ] Auto-send keys via email/SMS
- [ ] Pre-arrival climate control
- [ ] Energy savings when vacant
- [ ] Remote access for housekeeping
- [ ] Lock status monitoring
- [ ] Integration with 5+ lock brands

---

## ✅ Next Steps

1. Add F-022 (Smart Room Automation) to MASTER_CONTROL.md
2. Update ARCHITECTURE.md with integration layer
3. Create `apps/integrations/` structure in Django setup
4. Document integration credentials management
5. Plan Stripe integration for Phase 1

---

## 🔄 Review Date
Re-evaluate integration choices after Phase 1 MVP.
