# Integration Guide: F-002 ↔ F-003

**F-002**: AI Onboarding Agent (Nora)
**F-003**: Dynamic Commerce Engine (Website + Booking)

---

## 🎯 Integration Overview

**The Big Picture:**

```
User completes onboarding (F-002)
    ↓
Nora creates Hotel + Rooms + Policies (F-001 models)
    ↓
F-003 generates Website Config from onboarding data
    ↓
AI generates Things To Do + Events (F-003)
    ↓
Website auto-publishes (live, bookable)
    ↓
User sees success page with website URL
```

**Timeline:**
- **F-002 First**: User completes 10-minute onboarding
- **F-003 Immediate**: Website generated and published automatically
- **Result**: Fully functional hotel website with booking engine

---

## 📊 Data Flow

### 1. Onboarding Completion Triggers Website Creation

**File**: `apps/ai_agent/services/nora_agent.py`

```python
class NoraAgent:
    def complete_onboarding(self, context):
        """
        Called when onboarding state = COMPLETE.

        Creates:
        1. Hotel record (F-001)
        2. RoomType records (F-001)
        3. Room records (F-001)
        4. Initial policies (F-001)
        5. ✨ Website configuration (F-003)
        6. ✨ AI-generated content (F-003)
        """

        # ... (existing hotel creation from F-002)

        # ========================================
        # F-003 INTEGRATION STARTS HERE
        # ========================================

        # Import F-003 services
        from apps.website.models import WebsiteConfig
        from apps.website.services.ai_content_generator import ThingsToDoGenerator, EventsGenerator

        # 1. Generate Things To Do (10-15 items)
        things_to_do_generator = ThingsToDoGenerator()
        things_to_do_items = things_to_do_generator.generate(hotel)

        logger.info(f"Generated {len(things_to_do_items)} Things To Do items for {hotel.name}")

        # 2. Generate Events (5-10 items)
        events_generator = EventsGenerator()
        events = events_generator.generate(hotel)

        logger.info(f"Generated {len(events)} Events for {hotel.name}")

        # 3. Build initial website configuration
        initial_config = self.build_initial_website_config(context, hotel)

        # 4. Create WebsiteConfig
        website_config = WebsiteConfig.objects.create(
            hotel=hotel,
            draft_config=initial_config,
            meta_title=self.generate_meta_title(hotel),
            meta_description=self.generate_meta_description(hotel),
        )

        # 5. Auto-publish (website goes live immediately)
        website_config.published_by = context.user
        website_config.publish()

        logger.info(f"Website published for {hotel.name} at app.stayfull.com/{hotel.slug}")

        # 6. Update context with website URL
        context.task_state['website_url'] = f"https://app.stayfull.com/{hotel.slug}"
        context.save()

        # 7. Send success message to user
        return {
            'message': f"🎉 Your hotel is live! Check it out at app.stayfull.com/{hotel.slug}",
            'website_url': context.task_state['website_url'],
            'hotel_id': str(hotel.id),
        }
```

### 2. Building Initial Website Config

**File**: `apps/ai_agent/services/nora_agent.py`

```python
def build_initial_website_config(self, context, hotel):
    """
    Build website config from onboarding data.

    Maps NoraContext.task_state → WebsiteConfig.draft_config
    """
    task_state = context.task_state
    field_values = task_state.get('field_values', {})

    config = {
        # Hero Section
        'hero_type': 'image',  # Default to single image
        'hero_image_url': hotel.hero_image_url if hasattr(hotel, 'hero_image_url') else '',
        'hero_tagline': field_values.get('tagline', f"Experience {hotel.name}"),

        # Introduction
        'intro_text': field_values.get('hotel_description', ''),

        # Theme
        'theme': 'modern',  # Default theme

        # Component Order (default sequence)
        'component_order': [
            'hero',
            'intro',
            'rooms',
            'amenities',
            'things_to_do',
            'events',
            'dining',
            'location',
        ],

        # Colors (extracted from hotel branding if provided)
        'primary_color': field_values.get('brand_color', '#0066FF'),
        'secondary_color': '#F6F9FC',

        # Dining
        'dining_description': field_values.get('dining_description', ''),
        'dining_hours': field_values.get('dining_hours', ''),

        # Social Media
        'social_media': {
            'instagram': field_values.get('instagram_url', ''),
            'facebook': field_values.get('facebook_url', ''),
            'twitter': field_values.get('twitter_url', ''),
        },

        # Contact
        'show_contact_form': True,
        'show_phone': True,
        'show_email': True,

        # Metadata
        'created_from_onboarding': True,
        'onboarding_completed_at': timezone.now().isoformat(),
    }

    return config


def generate_meta_title(self, hotel):
    """Generate SEO meta title."""
    return f"{hotel.name} | {hotel.type.title()} Hotel in {hotel.address['city']}, {hotel.address['state']}"


def generate_meta_description(self, hotel):
    """Generate SEO meta description."""
    description = f"Experience {hotel.name}, a {hotel.type} hotel in {hotel.address['city']}. "

    # Add amenities
    if hotel.amenities:
        amenities = hotel.amenities[:3]
        description += ", ".join(amenities) + ". "

    description += "Book direct and save."

    return description[:160]  # Truncate to Google limit
```

---

## 🔗 Database Relationships

### NoraContext → Hotel → WebsiteConfig

```
NoraContext (F-002)
    ├── user: User
    ├── organization: Organization
    ├── task_state: JSONField {
    │       'hotel_name': 'Ocean Breeze Resort',
    │       'website_url': 'https://oceanbreeze.com',
    │       'field_values': {...},
    │       ...
    │   }
    └── active_task: 'onboarding'

            ↓ (creates)

Hotel (F-001)
    ├── organization: Organization
    ├── name: 'Ocean Breeze Resort'
    ├── slug: 'ocean-breeze-resort'
    ├── address: JSONField {...}
    ├── amenities: JSONField [...]
    ├── room_types: RoomType[]
    └── website_config: WebsiteConfig (1-to-1)

            ↓ (creates)

WebsiteConfig (F-003)
    ├── hotel: Hotel (FK)
    ├── draft_config: JSONField {
    │       'hero_type': 'image',
    │       'hero_tagline': '...',
    │       'component_order': [...],
    │       ...
    │   }
    ├── published_config: JSONField (same as draft after publish)
    ├── published_at: DateTime
    └── published_by: User

            + (creates)

ThingsToDoItem[] (F-003)
    ├── hotel: Hotel (FK)
    ├── name: 'Museum of Art'
    ├── description: '...'
    ├── category: 'museum'
    └── ...

Event[] (F-003)
    ├── hotel: Hotel (FK)
    ├── name: 'Summer Music Festival'
    ├── start_date: Date
    └── ...
```

---

## 🎬 User Journey

### Complete Flow: Onboarding → Live Website

**Step 1: User Starts Onboarding (F-002)**

```
User clicks "Let's Go, Nora!" on welcome page
    ↓
NoraContext created (active_task='onboarding')
    ↓
Nora guides through 4 sections:
    - Property Info (25%)
    - Rooms Setup (45%)
    - Policies (20%)
    - Review & Launch (10%)
```

**Step 2: User Provides Data (F-002)**

```
User provides:
    ✓ Hotel name, address, contact
    ✓ Website URL (for data extraction)
    ✓ Room types, pricing, amenities
    ✓ Policies (payment, cancellation)
    ✓ Photos (or AI stock images)
```

**Step 3: Onboarding Completes (F-002 → F-003 Integration)**

```
User reaches 100% progress
    ↓
NoraAgent.complete_onboarding() triggered
    ↓
Creates Hotel + RoomTypes + Rooms (F-001)
    ↓
Generates Things To Do (F-003) - 2-3 seconds
    ↓
Generates Events (F-003) - 2-3 seconds
    ↓
Creates WebsiteConfig (F-003) - <1 second
    ↓
Auto-publishes website (F-003) - <1 second
    ↓
Total time: ~5-10 seconds
```

**Step 4: Success Page (F-002)**

```
Nora shows success message:

    🎉 Your hotel is live!

    We did that in 8 minutes!

    [View Website] → https://app.stayfull.com/ocean-breeze-resort

    Remember: I'm always here to help. Just click my icon!

    [Go to Dashboard →]
```

**Step 5: User Views Website (F-003)**

```
User clicks "View Website"
    ↓
Opens new tab: app.stayfull.com/ocean-breeze-resort
    ↓
Website shows:
    ✓ Hero section with hotel photo
    ✓ Introduction text
    ✓ Rooms carousel (all room types)
    ✓ Amenities grid
    ✓ Things To Do section (15 items)
    ✓ Events section (10 items)
    ✓ Dining information
    ✓ Location map
    ✓ "Book Now" button (sticky header)
```

**Step 6: Guest Books Room (F-003)**

```
Guest clicks "Book Now"
    ↓
4-step booking flow:
    1. Select dates/guests
    2. Choose room type
    3. Enter guest details
    4. Pay with Stripe
    ↓
Reservation created (F-003)
    ↓
Email + SMS sent to guest
    ↓
Email sent to hotel
```

---

## 🔧 Integration Points Reference

### F-002 Calls F-003 Services

**Location**: `apps/ai_agent/services/nora_agent.py`

```python
# Import F-003 services
from apps.website.models import WebsiteConfig, ThingsToDoItem, Event
from apps.website.services.ai_content_generator import ThingsToDoGenerator, EventsGenerator
from apps.website.services.seo_service import SEOService

# Use in complete_onboarding()
things_to_do_generator = ThingsToDoGenerator()
things_to_do_generator.generate(hotel)

events_generator = EventsGenerator()
events_generator.generate(hotel)

website_config = WebsiteConfig.objects.create(...)
website_config.publish()
```

### F-003 Queries F-001 Models

**Location**: `apps/website/views.py`, `apps/website/services/component_renderer.py`

```python
# F-003 uses Hotel, RoomType, Room created by F-002
from apps.hotels.models import Hotel, RoomType, Room

# In website views
hotel = Hotel.objects.get(slug=hotel_slug, organization=request.user.staff.organization)
room_types = hotel.room_types.filter(is_active=True)
rooms = hotel.rooms.filter(is_active=True)
```

### Success Page Integration

**F-002 Template**: `apps/ai_agent/templates/ai_agent/success.html`

```html
<!-- Created during F-002 onboarding completion -->

<div class="success-page">
    <h1>🎉 Your hotel is live!</h1>
    <p>We did that in {{ onboarding_duration }} minutes!</p>

    <!-- F-003 website URL -->
    <a href="https://app.stayfull.com/{{ hotel.slug }}" target="_blank" class="btn-primary">
        View Your Website →
    </a>

    <p>Your website: <strong>app.stayfull.com/{{ hotel.slug }}</strong></p>

    <div class="next-steps">
        <h2>What's Next?</h2>
        <ul>
            <li>✓ Your website is live and accepting bookings</li>
            <li>✓ We've added 15 local attractions for your guests</li>
            <li>✓ We've added 10 upcoming events in your area</li>
            <li>→ Customize your website in the Website Manager</li>
            <li>→ Start managing bookings in your Dashboard</li>
        </ul>
    </div>

    <a href="{% url 'dashboard:home' %}" class="btn-secondary">
        Go to Dashboard →
    </a>
</div>
```

---

## ⚙️ Configuration Dependencies

### Environment Variables (Both Features)

```bash
# F-002 (Onboarding)
OPENAI_API_KEY=sk-...
GOOGLE_PLACES_API_KEY=...

# F-003 (Website)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STAYFULL_COMMISSION_RATE=0.15
TICKETMASTER_API_KEY=...

# Shared
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Settings (Both Features)

```python
# config/settings.py

INSTALLED_APPS = [
    ...
    'apps.core',           # F-001 (Organization, User)
    'apps.hotels',         # F-001 (Hotel, RoomType, Room)
    'apps.ai_agent',       # F-002 (NoraContext, Nora services)
    'apps.website',        # F-003 (WebsiteConfig, Components)
    'apps.bookings',       # F-003 (Reservation, Payment)
    ...
]

# F-002 Settings
OPENAI_API_KEY = env('OPENAI_API_KEY')
GOOGLE_PLACES_API_KEY = env('GOOGLE_PLACES_API_KEY')

# F-003 Settings
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STAYFULL_COMMISSION_RATE = float(env('STAYFULL_COMMISSION_RATE', '0.15'))
TICKETMASTER_API_KEY = env('TICKETMASTER_API_KEY')
```

---

## 🧪 Testing Integration

### Integration Test: Onboarding → Website

**File**: `apps/ai_agent/tests/test_integration_f003.py`

```python
from django.test import TestCase
from apps.ai_agent.models import NoraContext
from apps.ai_agent.services.nora_agent import NoraAgent
from apps.hotels.models import Hotel
from apps.website.models import WebsiteConfig, ThingsToDoItem, Event


class OnboardingToWebsiteIntegrationTest(TestCase):
    """
    Test F-002 → F-003 integration.
    """

    def test_onboarding_creates_website(self):
        """
        Completing onboarding should:
        1. Create Hotel (F-001)
        2. Create WebsiteConfig (F-003)
        3. Generate Things To Do (F-003)
        4. Generate Events (F-003)
        5. Auto-publish website (F-003)
        """

        # Setup: Create user + organization
        user = self.create_user()
        organization = self.create_organization()

        # Create NoraContext with completed onboarding data
        context = NoraContext.objects.create(
            user=user,
            organization=organization,
            active_task='onboarding',
            task_state={
                'current_step': 'complete',
                'field_values': {
                    'hotel_name': 'Ocean Breeze Resort',
                    'address': {'city': 'Miami', 'state': 'FL', ...},
                    'phone': '+1234567890',
                    'email': 'info@oceanbreeze.com',
                    # ... (complete onboarding data)
                },
                'completed_steps': ['hotel_name', 'address', ...],
            }
        )

        # Execute: Complete onboarding
        agent = NoraAgent(context)
        result = agent.complete_onboarding(context)

        # Assert: Hotel created
        hotel = Hotel.objects.get(name='Ocean Breeze Resort')
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.organization, organization)

        # Assert: WebsiteConfig created and published
        website_config = hotel.website_config
        self.assertIsNotNone(website_config)
        self.assertIsNotNone(website_config.published_config)
        self.assertIsNotNone(website_config.published_at)

        # Assert: Things To Do generated
        things_to_do = hotel.things_to_do.all()
        self.assertGreaterEqual(things_to_do.count(), 10)
        self.assertLessEqual(things_to_do.count(), 15)

        # Assert: Events generated
        events = hotel.events.all()
        self.assertGreaterEqual(events.count(), 5)
        self.assertLessEqual(events.count(), 10)

        # Assert: Website URL in context
        self.assertIn('website_url', context.task_state)
        self.assertEqual(context.task_state['website_url'], f"https://app.stayfull.com/{hotel.slug}")

    def test_website_loads_after_onboarding(self):
        """
        After onboarding, website should be publicly accessible.
        """

        # Setup: Complete onboarding (creates hotel + website)
        hotel = self.complete_onboarding()

        # Execute: Load public website
        response = self.client.get(f'/{hotel.slug}/')

        # Assert: Website loads
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, hotel.name)

        # Assert: Components render
        self.assertContains(response, 'hero')  # Hero section
        self.assertContains(response, 'Rooms')  # Rooms section
        self.assertContains(response, 'Things To Do')  # Things To Do section
        self.assertContains(response, 'Events')  # Events section

        # Assert: Book Now button present
        self.assertContains(response, 'Book Now')
```

---

## 🚨 Critical Integration Rules

### 1. Auto-Publish After Onboarding

**Rule**: When onboarding completes, website MUST auto-publish (not stay as draft).

**Reason**: The "wow moment" is seeing the live website immediately.

```python
# ✅ Correct
website_config.publish()  # Auto-publish after onboarding

# ❌ WRONG
# Leave as draft - user would have to manually publish
```

### 2. Generate AI Content During Onboarding

**Rule**: Things To Do and Events MUST generate during onboarding (not async later).

**Reason**: Complete website experience from day 1.

```python
# ✅ Correct - Generate during onboarding
things_to_do_generator.generate(hotel)  # 2-3 seconds
events_generator.generate(hotel)  # 2-3 seconds

# ❌ WRONG - Defer to background job
# Celery task for later - website incomplete
```

### 3. Preserve Organization Context

**Rule**: ALL F-003 queries MUST filter by organization (multi-tenancy).

**Reason**: Security, data isolation.

```python
# ✅ Correct
hotel = Hotel.objects.get(
    slug=hotel_slug,
    organization=request.user.staff.organization  # REQUIRED
)

# ❌ WRONG - Data leakage
hotel = Hotel.objects.get(slug=hotel_slug)  # Missing organization filter
```

### 4. Success Page Shows Website URL

**Rule**: F-002 success page MUST include clickable website URL.

**Reason**: Immediate validation, "wow moment".

```python
# ✅ Correct
context.task_state['website_url'] = f"https://app.stayfull.com/{hotel.slug}"

# Success message includes link
return {
    'message': f"🎉 Your hotel is live! Check it out at app.stayfull.com/{hotel.slug}",
    'website_url': context.task_state['website_url'],
}
```

---

## 📝 Developer Checklist

### F-002 Developer (AI Onboarding)

When completing Phase 6 (Integration), ensure:

- [ ] `complete_onboarding()` imports F-003 services
- [ ] ThingsToDoGenerator called with hotel instance
- [ ] EventsGenerator called with hotel instance
- [ ] WebsiteConfig created with `build_initial_website_config()`
- [ ] WebsiteConfig.publish() called (auto-publish)
- [ ] Website URL added to context.task_state
- [ ] Success page shows website URL link
- [ ] Success page opens website in new tab
- [ ] Integration test covers F-002 → F-003 flow

### F-003 Developer (Website)

When starting Phase 1 (Foundation), ensure:

- [ ] WebsiteConfig model compatible with F-002 data structure
- [ ] `build_initial_website_config()` helper exists
- [ ] ThingsToDoItem model matches F-002 expectations
- [ ] Event model matches F-002 expectations
- [ ] Public website routes work without authentication
- [ ] Hotel.slug used for URL routing
- [ ] Organization filter on ALL queries
- [ ] Integration test covers onboarding → website flow

---

## 🔄 Data Migration Path

### If F-002 Ships Before F-003

**Scenario**: F-002 deployed, hotels onboarded, then F-003 deployed later.

**Migration Required**:

```python
# apps/website/migrations/0002_backfill_websites.py

from django.db import migrations

def backfill_websites(apps, schema_editor):
    """
    Create WebsiteConfig for all existing hotels.
    Generate Things To Do and Events for each.
    """
    Hotel = apps.get_model('hotels', 'Hotel')
    WebsiteConfig = apps.get_model('website', 'WebsiteConfig')

    from apps.website.services.ai_content_generator import ThingsToDoGenerator, EventsGenerator

    for hotel in Hotel.objects.all():
        # Check if website config exists
        if not hasattr(hotel, 'website_config'):
            # Create config
            config = WebsiteConfig.objects.create(
                hotel=hotel,
                draft_config=build_default_config(hotel),
            )

            # Generate content
            ThingsToDoGenerator().generate(hotel)
            EventsGenerator().generate(hotel)

            # Auto-publish
            config.publish()

            print(f"Created website for {hotel.name}")


class Migration(migrations.Migration):
    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_websites),
    ]
```

**Recommended**: Ship F-002 and F-003 together to avoid this migration.

---

## 📚 Related Documentation

**Feature Specifications:**
- `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
- `.architect/features/F-003_DYNAMIC_COMMERCE_ENGINE.md`

**Developer Handoffs:**
- `.architect/handoffs/F-002_DEVELOPER_HANDOFF.md`
- `.architect/handoffs/F-003_DEVELOPER_HANDOFF.md`

**Development Standards:**
- `.architect/DEVELOPMENT_STANDARDS.md`

**Testing:**
- `apps/ai_agent/tests/test_integration_f003.py`
- `apps/website/tests/test_integration_f002.py`

---

## 💡 Key Takeaways

1. **F-002 and F-003 are deeply integrated** - Not separate features
2. **Onboarding completion triggers website creation** - Happens automatically
3. **AI content generates during onboarding** - Not background job
4. **Website auto-publishes** - User sees live site immediately
5. **Success page shows website URL** - Critical for "wow moment"
6. **Multi-tenancy preserved throughout** - Organization filter on all queries

---

**Questions? Ask the architect. Integration is critical - don't guess!**
