# F-003: Dynamic Commerce Engine (Hotel Website + Booking Engine)

**Priority**: P1 - Killer Feature
**Estimated Effort**: 80 hours (~10 days)
**Status**: ✅ APPROVED - Ready for Development
**Dependencies**: F-002 (Nora AI Onboarding) MUST be complete first
**Standards**: `.architect/DEVELOPMENT_STANDARDS.md`

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Vision & Value Proposition](#core-vision--value-proposition)
3. [User Journey & Flow](#user-journey--flow)
4. [Website Components & Structure](#website-components--structure)
5. [Booking Engine Architecture](#booking-engine-architecture)
6. [Payment Processing (Stripe)](#payment-processing-stripe)
7. [SEO & Discoverability](#seo--discoverability)
8. [Dynamic Updates & Version Control](#dynamic-updates--version-control)
9. [AI Content Generation](#ai-content-generation)
10. [Integration with F-002](#integration-with-f-002)
11. [Technical Architecture](#technical-architecture)
12. [Security & Multi-Tenancy](#security--multi-tenancy)
13. [Definition of Done](#definition-of-done)

---

## Executive Summary

### What This Is

**F-003 = Dynamic Commerce Engine**: A live hotel website + booking engine that is automatically generated from F-002 onboarding data and dynamically updated from admin dashboard changes.

**The Complete Flow:**
1. User completes F-002 onboarding (10 minutes)
2. Website instantly goes live at `app.stayfull.com/[hotel-slug]`
3. Success page offers: "Explore Admin Dashboard" or "View Hotel Website"
4. Hotel manages content via PMS dashboard
5. Changes publish to website (with version control)
6. Guests browse, book, and pay via website
7. Bookings flow into PMS (reservations, tasks, inventory, revenue)

### The Transformation

**Industry Standard:**
- Website development: 3-6 months + $5k-$15k
- Booking engine integration: Separate system (commission-based)
- Content updates: Developer needed, slow
- SEO optimization: Manual, ongoing cost

**Stayfull with F-003:**
- Website live: Instant (after 10-min onboarding)
- Booking engine: Integrated, zero commission
- Content updates: Real-time, no developer needed
- SEO: Auto-generated, schema markup included
- AI content: Things To Do, Events (traffic magnets)

### Strategic Importance

**Why F-003 is Critical:**

1. **Commerce = Revenue**: Website converts browsers to bookers
2. **Direct Bookings**: Avoid OTA commissions (15-25%)
3. **AI Content = Free Traffic**: Things To Do, Events, Blogs drive organic visitors
4. **Merchant of Record**: Stayfull controls payment flow (commission model)
5. **Competitive Moat**: Instant website + booking + AI content is unique in PMS market

**Value Equation:**
- F-002 (Nora) = Acquisition (wow factor, 10-min setup)
- F-003 (Commerce Engine) = Revenue (bookings, payment processing)
- Combined = Unstoppable (no competitor offers both)

---

## Core Vision & Value Proposition

### What Makes This Different

**Traditional PMS Approach:**
- PMS = Operations system only
- Website = Separate vendor
- Booking engine = Another vendor
- Payment = Yet another vendor
- Result: Fragmented, expensive, slow

**Stayfull Approach:**
- PMS + Website + Booking + Payment = Unified system
- Single source of truth: Hotel database
- Dynamic updates: Change price → website updates instantly
- AI content: Auto-generated traffic drivers
- Result: Integrated, cheap, fast

### The "Dynamic Commerce Engine" Concept

**What "Dynamic" Means:**

```
Admin Dashboard (PMS)          →  Consumer Website (Commerce Engine)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Update room photo            →  Photo appears on website instantly
Change price $199 → $249     →  Booking engine shows $249
Add new room type            →  "Deluxe Suite" appears on site
Update check-in time         →  Policy page shows new time
Publish changes              →  All updates go live together
```

**Single Source of Truth:**
- Hotel model = Authoritative
- RoomType model = Product catalog
- Room model = Inventory
- Policy model = Terms & conditions
- Changes in database → Reflected on website

**Why This Matters:**
- Hotels manage one system (not five)
- No sync errors (one database)
- Real-time availability (no double bookings)
- Price updates instant (dynamic pricing works)

---

## User Journey & Flow

### Primary User Journey

**User Persona**: Hotel owner (completed F-002 onboarding)

### Journey Map:

#### Stage 1: Onboarding Completion (F-002)
```
User completes F-002 onboarding
↓
Nora creates:
- Hotel record (name, address, contact, photos, policies)
- RoomType records (3 types: Standard, Deluxe, Suite)
- Room records (34 rooms total, numbered 101-334)
- Rate plans (1 base rate per room type)
- Policies (payment, cancellation)
- AI content (Things To Do, Events based on location)
↓
F-003 automatically generates website from this data
↓
Website goes live at: app.stayfull.com/ocean-breeze
```

#### Stage 2: Success & Choice
```
Success page shows two CTAs:
┌─────────────────────────────────────────┐
│  🎉 Your hotel is live!                 │
│  We did that in 8 minutes!              │
│                                         │
│  ocean-breeze.stayfull.com              │
│                                         │
│  [Explore Admin Dashboard]              │
│  [View Hotel Website] ← Opens new tab   │
└─────────────────────────────────────────┘
```

#### Stage 3A: Admin Dashboard Path
```
User clicks "Explore Admin Dashboard"
↓
Redirects to: /admin/dashboard/
↓
Dashboard shows:
- Today's revenue: $0 (no bookings yet)
- Occupancy: 0% (no reservations)
- Quick actions: Manage Rooms, Update Rates, Edit Website
↓
User clicks "Edit Website"
↓
Redirects to Website Manager (/admin/website/)
```

#### Stage 3B: View Website Path
```
User clicks "View Hotel Website"
↓
Opens new tab: app.stayfull.com/ocean-breeze
↓
Consumer website displays:
- Hero section (hotel photo, name, "Book Now" button)
- Rooms & Suites (3 room types with photos, prices)
- Amenities (wifi, parking, breakfast, pool)
- Things To Do (AI-generated: 5 local attractions)
- Events (AI-generated: 3 upcoming events)
- Policies (payment, cancellation, check-in/out)
- Location (map, contact info)
```

### Guest Journey (Consumer)

**User Persona**: Traveler looking for accommodation

```
1. Discovery
   - Google search: "hotels in Miami"
   - Finds: Ocean Breeze Resort (SEO from F-003)
   - Clicks through to: app.stayfull.com/ocean-breeze

2. Browse
   - Hero section: Beautiful beach photo
   - Sticky header: "Book Now" always visible
   - Scrolls through sections:
     - Rooms (carousel of 3 types)
     - Things To Do (5 AI-generated attractions)
     - Amenities (icons + descriptions)
     - Reviews (5-star testimonials)

3. Book
   - Clicks "Book Now" in sticky header
   - Booking modal opens:
     - Check-in date: [Date picker]
     - Check-out date: [Date picker]
     - Guests: [Dropdown: 1-4]
     - [Search Rooms]

   - Sees available rooms:
     ┌────────────────────────────────────┐
     │ Standard Queen Room                │
     │ Max 2 guests • 1 Queen Bed         │
     │ $199/night × 2 nights = $398       │
     │ [Select Room]                      │
     └────────────────────────────────────┘

4. Checkout
   - Guest details:
     - Name: [Input]
     - Email: [Input]
     - Phone: [Input]

   - Payment (Stripe):
     - Card details (Stripe widget)
     - Policy: "💳 50% deposit at booking, rest on arrival"
     - Total: $199 (50% of $398)

   - [Complete Booking]

5. Confirmation
   - Confirmation page:
     - Booking reference: #OB-12345
     - Details: Dates, room, total
     - [Add to Calendar]

   - Email confirmation (guest)
   - SMS confirmation (guest)
   - Email notification (hotel)

6. Post-Booking
   - Guest receives:
     - Confirmation email (immediately)
     - Pre-arrival email (24 hours before)
     - Check-in instructions (day of arrival)

   - Hotel sees in PMS:
     - New reservation in dashboard
     - Check-in task created
     - Revenue stats updated
     - Occupancy updated
```

---

## Website Components & Structure

### Component Architecture

**Philosophy**: Modular, dynamic, user-configurable

**11 Standard Components:**

1. **Hero Section** (Required)
   - Hotel name (from onboarding)
   - Hero image/slideshow/video (from onboarding photos)
   - Tagline/subtitle (user-customizable)
   - Primary CTA: "Book Now" button

2. **Intro Section** (Optional - shows if has content)
   - Description paragraph
   - Optional image
   - Example: "Where design meets comfort. Experience a space that celebrates simplicity..."

3. **Rooms & Suites** (Required)
   - Carousel of room types
   - Each room card:
     - Photo (from onboarding)
     - Name (e.g., "Deluxe Suite")
     - Max occupancy
     - Bed configuration
     - Base price ("/night")
     - "View Details" → Room detail page
     - "Book Now" → Booking flow

4. **Special Offers** (Optional - shows if has active offers)
   - Carousel of promotions
   - Example: "Stay 3 nights, get 1 free"
   - "View Offer" → Offer detail page

5. **Things To Do** (AI-Generated - always active)
   - Filter-based layout (not carousel)
   - Filters: Category, Distance, Price
   - AI generates 10-15 attractions based on:
     - Hotel geolocation
     - Season/time of year
     - Local events APIs
   - Each item:
     - Photo (from Unsplash or AI-generated)
     - Name
     - Category (Museums, Outdoors, Food, Nightlife)
     - Distance from hotel
     - Brief description
     - "Learn More" → External link

6. **Events** (AI-Generated - always active)
   - Filter-based layout
   - Filters: Date, Category, Price
   - AI generates 5-10 upcoming events:
     - Concerts
     - Festivals
     - Sports games
     - Theater shows
   - Data sources:
     - Ticketmaster API
     - Eventbrite API
     - Local event calendars
   - Each item:
     - Photo
     - Event name
     - Date/time
     - Venue
     - Price range
     - "Get Tickets" → External link

7. **Amenities** (Required)
   - Grid layout (not carousel)
   - Icons + labels
   - Extracted during onboarding:
     - From website crawl (AI extracts)
     - User confirms/adds more
   - Common amenities:
     - Free WiFi
     - Free Parking
     - Pool
     - Fitness Center
     - Restaurant
     - Room Service
     - Pet Friendly
     - Business Center

8. **Dining** (Optional - shows if has content)
   - Restaurant name
   - Hours of operation
   - Description
   - Photo
   - Menu link (optional)
   - "Make Reservation" CTA (optional)

9. **Shop/Merchandise** (Optional - shows if has products)
   - Carousel of products
   - Hotel-branded items:
     - Robes
     - Towels
     - Coffee mugs
     - Artwork prints
   - Each product:
     - Photo
     - Name
     - Price
     - "Add to Cart"

10. **Guest Reviews** (Optional - shows if has reviews)
    - Scrolling carousel (auto-scroll)
    - Review cards:
      - 5-star rating
      - Quote
      - Guest name
      - Date
    - Initially populated with sample reviews
    - Real reviews replace samples as they come in

11. **Location** (Required)
    - Interactive map (Google Maps embed)
    - Address
    - Phone number
    - Email
    - "Get Directions" CTA

### Component Visibility Rules

**Required Components** (Always visible):
- Hero
- Rooms & Suites
- Amenities
- Location

**Conditional Components** (Show only if has content):
- Intro (if user adds description)
- Special Offers (if active offers exist)
- Dining (if restaurant info provided)
- Shop (if products added)
- Guest Reviews (if reviews exist)

**AI-Generated Components** (Always show):
- Things To Do (AI generates during onboarding)
- Events (AI generates during onboarding)

**Example Visibility Logic:**

```python
# In template
{% for component in components %}
  {% if component.id == 'hero' or component.id == 'rooms' %}
    {# Always show #}
    {% include component.template %}

  {% elif component.id == 'things-to-do' or component.id == 'events' %}
    {# AI-generated, always show #}
    {% include component.template %}

  {% elif component.visibility == 'active' and component.has_content %}
    {# Show only if active and has content #}
    {% include component.template %}
  {% endif %}
{% endfor %}
```

### Component Sequencing

**User Control**: Drag-and-drop ordering in Website Manager

**Default Sequence:**
1. Hero
2. Intro
3. Rooms & Suites
4. Special Offers
5. Things To Do
6. Events
7. Amenities
8. Dining
9. Shop
10. Guest Reviews
11. Location

**Customization:**
- User can reorder via drag-and-drop
- Cannot hide Hero, Rooms, Location (required)
- Can hide optional components
- Order saved per hotel

---

## Booking Engine Architecture

### Booking Flow: Minimize Clicks

**Core Principle**: "Every click reduces conversion"

**Optimal Flow** (4 steps):

```
Step 1: Select Dates
┌────────────────────────────────────┐
│  Book Your Stay                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Check-in:  [Dec 15, 2025 ▼]      │
│  Check-out: [Dec 17, 2025 ▼]      │
│  Guests:    [2 ▼]                 │
│                                    │
│  [Search Rooms]                    │
└────────────────────────────────────┘

↓

Step 2: Select Room
┌────────────────────────────────────┐
│  Available Rooms                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  ┌──────────────────────────────┐ │
│  │ [Photo]                      │ │
│  │ Standard Queen Room          │ │
│  │ Max 2 guests • 1 Queen Bed   │ │
│  │ Free WiFi, TV, Mini Fridge   │ │
│  │                              │ │
│  │ $199/night × 2 nights = $398 │ │
│  │                              │ │
│  │ [Select Room]                │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ [Photo]                      │ │
│  │ Deluxe King Suite            │ │
│  │ Max 3 guests • 1 King Bed    │ │
│  │ ...                          │ │
│  │ $299/night × 2 nights = $598 │ │
│  │ [Select Room]                │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘

↓

Step 3: Guest Details
┌────────────────────────────────────┐
│  Guest Information                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Full Name:  [____________]        │
│  Email:      [____________]        │
│  Phone:      [____________]        │
│                                    │
│  Special Requests (optional):      │
│  [________________________]        │
│                                    │
│  [Continue to Payment]             │
└────────────────────────────────────┘

↓

Step 4: Payment (Stripe)
┌────────────────────────────────────┐
│  Payment Details                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [Stripe Payment Element]          │
│  (Card number, expiry, CVC)        │
│                                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Booking Summary:                  │
│  Standard Queen Room               │
│  Dec 15 - Dec 17 (2 nights)        │
│  2 guests                          │
│                                    │
│  Room total:      $398.00          │
│  Taxes (12%):     $47.76           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Total:           $445.76          │
│                                    │
│  Payment Policy:                   │
│  💳 50% deposit at booking         │
│  Pay now: $222.88                  │
│  Pay on arrival: $222.88           │
│                                    │
│  ☑ I agree to cancellation policy  │
│                                    │
│  [Complete Booking]                │
└────────────────────────────────────┘

↓

Confirmation Page
┌────────────────────────────────────┐
│  🎉 Booking Confirmed!             │
│                                    │
│  Confirmation #: OB-12345          │
│                                    │
│  Standard Queen Room               │
│  Dec 15 - Dec 17, 2025             │
│  2 guests                          │
│                                    │
│  Check-in: 3:00 PM                 │
│  Check-out: 11:00 AM               │
│                                    │
│  Total Paid: $222.88               │
│  Remaining: $222.88 (at property)  │
│                                    │
│  Confirmation sent to:             │
│  john@example.com                  │
│  +1 (555) 123-4567                 │
│                                    │
│  [Add to Calendar]                 │
│  [View Booking Details]            │
│                                    │
│  Questions? Call us at             │
│  (305) 555-0123                    │
└────────────────────────────────────┘
```

### Booking Entry Points

**Multiple ways to start booking:**

1. **Sticky Header "Book Now" Button**
   - Fixed to top of page (always visible)
   - Most prominent CTA
   - Opens booking modal overlay

2. **Hero Section CTA**
   - Large "Check Availability" button
   - Same as header "Book Now"

3. **Room Cards**
   - Each room type has "Book Now" button
   - Pre-selects that room type
   - Still lets user pick dates/guests

4. **Floating Booking Widget** (Optional - Post-MVP)
   - Sticky on right side of page
   - Minimal form: Dates + Guests + Search

**Priority**: Header + Hero + Room cards for MVP

### Availability Logic

**Real-time Availability Calculation:**

```python
def get_available_rooms(check_in, check_out, guests):
    """
    Find available room types for given dates/guests.

    Logic:
    1. Get all room types for this hotel
    2. For each room type:
       a. Check max_occupancy >= guests
       b. Count total rooms of this type
       c. Count booked rooms (overlapping dates)
       d. Available = total - booked
    3. Return room types with availability > 0
    """

    available_rooms = []

    for room_type in hotel.room_types.all():
        # Check occupancy
        if room_type.max_occupancy < guests:
            continue

        # Count total rooms
        total_rooms = room_type.rooms.filter(status='available').count()

        # Count booked rooms (overlapping date range)
        booked_rooms = Reservation.objects.filter(
            room__room_type=room_type,
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=['confirmed', 'checked-in']
        ).values('room').distinct().count()

        available = total_rooms - booked_rooms

        if available > 0:
            available_rooms.append({
                'room_type': room_type,
                'available_count': available,
                'price': calculate_price(room_type, check_in, check_out)
            })

    return available_rooms
```

### Price Calculation

**Dynamic Pricing:**

```python
def calculate_price(room_type, check_in, check_out):
    """
    Calculate total price for room type and date range.

    Factors:
    - Base rate (from rate plan)
    - Number of nights
    - Weekend surcharge (future)
    - Seasonal pricing (future)
    - Taxes
    """

    nights = (check_out - check_in).days
    base_rate = room_type.get_active_rate_plan().base_price

    # MVP: Simple calculation
    subtotal = base_rate * nights
    taxes = subtotal * hotel.tax_rate
    total = subtotal + taxes

    return {
        'base_rate': base_rate,
        'nights': nights,
        'subtotal': subtotal,
        'taxes': taxes,
        'total': total,
        'currency': hotel.currency
    }
```

---

## Payment Processing (Stripe)

### 🚨 Critical Architecture Decision

**Stayfull = Merchant of Record**

**What This Means:**
- Stayfull owns the Stripe account
- Hotels are **sub-accounts** (Stripe Connect)
- All payments flow through Stayfull
- Stayfull controls commission/fees
- Hotels CANNOT integrate their own payment processor

**Why This Matters:**
- Revenue model: Stayfull takes % of each booking
- Compliance: Stayfull handles PCI, chargebacks, disputes
- Simplicity: Hotels don't need merchant accounts
- Control: Stayfull can enforce policies, prevent fraud

### Stripe Architecture

**Setup:**

```
Stayfull Platform
├── Stripe Account (Platform)
│   └── Stripe Connect
│       ├── Sub-Account: Ocean Breeze Resort
│       ├── Sub-Account: Sunset Inn
│       └── Sub-Account: City Center Hotel
```

**Payment Flow:**

```
Guest books room for $445.76
↓
Stripe Checkout processes payment
↓
Money flows to: Stayfull Platform Account
↓
Stayfull takes commission (e.g., 5% = $22.29)
↓
Remaining amount transferred to: Hotel Sub-Account
($445.76 - $22.29 = $423.47)
↓
Hotel receives payout (daily/weekly/monthly)
```

### Stripe Integration

**Components:**

1. **Stripe Connect Account Creation**
   - Happens during onboarding (F-002)
   - Hotel provides business info
   - Stripe verifies identity
   - Sub-account created automatically

2. **Stripe Checkout/Payment Element**
   - Embedded in booking flow
   - Pre-configured by Stayfull
   - Hotel cannot customize
   - Supports: Cards, Apple Pay, Google Pay

3. **Payment Intent Creation**
   ```python
   # apps/bookings/services/payment_service.py

   def create_payment_intent(reservation, deposit_amount):
       """
       Create Stripe Payment Intent for booking.

       Uses Stripe Connect to route payment to hotel sub-account.
       """

       stripe.api_key = settings.STRIPE_SECRET_KEY

       # Calculate Stayfull commission
       commission = deposit_amount * settings.STAYFULL_COMMISSION_RATE

       intent = stripe.PaymentIntent.create(
           amount=int(deposit_amount * 100),  # Stripe uses cents
           currency=reservation.hotel.currency.lower(),

           # Route to hotel sub-account
           transfer_data={
               'destination': reservation.hotel.stripe_account_id,
               'amount': int((deposit_amount - commission) * 100),
           },

           # Platform fee (commission)
           application_fee_amount=int(commission * 100),

           metadata={
               'reservation_id': str(reservation.id),
               'hotel_id': str(reservation.hotel.id),
               'room_type': reservation.room.room_type.name,
           }
       )

       return intent
   ```

4. **Webhook Handling**
   ```python
   # apps/bookings/views/webhooks.py

   @csrf_exempt
   def stripe_webhook(request):
       """
       Handle Stripe webhook events.

       Events to handle:
       - payment_intent.succeeded → Confirm booking
       - payment_intent.payment_failed → Cancel booking
       - charge.refunded → Process refund
       """

       payload = request.body
       sig_header = request.META['HTTP_STRIPE_SIGNATURE']

       try:
           event = stripe.Webhook.construct_event(
               payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
           )
       except ValueError:
           return HttpResponse(status=400)
       except stripe.error.SignatureVerificationError:
           return HttpResponse(status=400)

       if event['type'] == 'payment_intent.succeeded':
           payment_intent = event['data']['object']
           reservation_id = payment_intent['metadata']['reservation_id']

           # Confirm reservation
           reservation = Reservation.objects.get(id=reservation_id)
           reservation.status = 'confirmed'
           reservation.payment_status = 'deposit_paid'
           reservation.save()

           # Send confirmations
           send_guest_confirmation(reservation)
           send_hotel_notification(reservation)

       return HttpResponse(status=200)
   ```

### Payment Policies

**Deposit vs. Full Payment:**

Determined by hotel's payment policy (set in onboarding):

```python
# Example payment policy:
{
    'deposit_type': 'percentage',  # or 'fixed'
    'deposit_amount': 50,          # 50%
    'deposit_timing': 'at_booking',
    'balance_timing': 'on_arrival'
}

# At booking time:
total = $445.76
deposit = total * 0.5 = $222.88  # Charge now
balance = $222.88                # Charge at property
```

**Payment at Property:**

Some hotels want guests to pay on arrival:

```python
# Payment policy option:
{
    'deposit_amount': 0,
    'balance_timing': 'on_arrival',
    'payment_method': 'at_property'
}

# Result:
# - Guest books without payment
# - Reservation marked as 'pending_payment'
# - Hotel collects payment at check-in
# - Hotel staff marks as paid in PMS
```

**For MVP**: Focus on deposit model (standard for online bookings)

---

## SEO & Discoverability

### 🚨 Critical Requirement

**Quote from discovery**: "Content is worthless unless it's acting as a magnet for consumer clicks"

**Why SEO is F-003 Core** (not future):
- Without traffic, website doesn't generate bookings
- Without bookings, commerce engine has no value
- SEO is infrastructure, not feature

### SEO Architecture

**1. Dynamic Meta Tags**

Every page generates SEO-optimized meta tags:

```html
<!-- Homepage -->
<head>
    <title>Ocean Breeze Resort | Luxury Hotel in Miami Beach, FL</title>
    <meta name="description" content="Experience Ocean Breeze Resort, a luxury boutique hotel in Miami Beach. Oceanfront rooms, rooftop pool, 5-star amenities. Book direct and save 15%.">
    <meta name="keywords" content="Miami Beach hotel, luxury hotel Miami, oceanfront resort, boutique hotel Florida">

    <!-- Open Graph (Social Media) -->
    <meta property="og:title" content="Ocean Breeze Resort | Luxury Hotel in Miami Beach">
    <meta property="og:description" content="Experience Ocean Breeze Resort, a luxury boutique hotel in Miami Beach.">
    <meta property="og:image" content="https://app.stayfull.com/media/ocean-breeze/hero.jpg">
    <meta property="og:url" content="https://app.stayfull.com/ocean-breeze">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Ocean Breeze Resort | Luxury Hotel in Miami Beach">
    <meta name="twitter:description" content="Experience Ocean Breeze Resort...">
    <meta name="twitter:image" content="https://app.stayfull.com/media/ocean-breeze/hero.jpg">

    <!-- Canonical URL -->
    <link rel="canonical" href="https://app.stayfull.com/ocean-breeze">
</head>
```

**Dynamic Generation Logic:**

```python
# apps/website/services/seo_service.py

def generate_meta_tags(hotel, page_type='homepage'):
    """
    Generate SEO meta tags for hotel website pages.

    Uses hotel data to create optimized titles/descriptions.
    """

    if page_type == 'homepage':
        title = f"{hotel.name} | {hotel.type.title()} Hotel in {hotel.address['city']}, {hotel.address['state']}"

        description = f"Experience {hotel.name}, a {hotel.type} hotel in {hotel.address['city']}. "

        # Add amenities
        amenities = hotel.get_top_amenities(3)
        if amenities:
            description += ", ".join(amenities) + ". "

        description += "Book direct and save."

        # Keywords
        keywords = [
            f"{hotel.address['city']} hotel",
            f"{hotel.type} hotel {hotel.address['state']}",
            hotel.name,
        ]

    elif page_type == 'rooms':
        title = f"Rooms & Suites | {hotel.name}"
        description = f"Browse our {hotel.room_types.count()} room types at {hotel.name}. From ${hotel.get_min_price()}/night."

    # ... more page types

    return {
        'title': title[:60],  # Google truncates at 60 chars
        'description': description[:160],  # Google shows 150-160
        'keywords': keywords,
        'og_image': hotel.hero_image_url,
        'canonical_url': f"https://app.stayfull.com/{hotel.slug}"
    }
```

**2. Sitemap Generation**

Auto-generated XML sitemap for search engines:

```xml
<!-- /sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

    <!-- Homepage -->
    <url>
        <loc>https://app.stayfull.com/ocean-breeze</loc>
        <lastmod>2025-10-23</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    <!-- Rooms page -->
    <url>
        <loc>https://app.stayfull.com/ocean-breeze/rooms</loc>
        <lastmod>2025-10-23</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- Individual room pages -->
    <url>
        <loc>https://app.stayfull.com/ocean-breeze/rooms/standard-queen</loc>
        <lastmod>2025-10-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>

    <!-- Things to do -->
    <url>
        <loc>https://app.stayfull.com/ocean-breeze/things-to-do</loc>
        <lastmod>2025-10-22</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>

    <!-- ... more pages -->
</urlset>
```

**Dynamic Sitemap:**

```python
# apps/website/views/sitemap.py

from django.contrib.sitemaps import Sitemap
from apps.hotels.models import Hotel, RoomType

class HotelSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Hotel.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/{obj.slug}/"

class RoomTypeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return RoomType.objects.filter(is_active=True, hotel__is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/{obj.hotel.slug}/rooms/{obj.slug}/"

# In urls.py:
sitemaps = {
    'hotels': HotelSitemap,
    'rooms': RoomTypeSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]
```

**3. Structured Data (Schema.org)**

JSON-LD markup for rich search results:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Hotel",
  "name": "Ocean Breeze Resort",
  "description": "A luxury boutique hotel in Miami Beach with oceanfront rooms and rooftop pool.",
  "image": "https://app.stayfull.com/media/ocean-breeze/hero.jpg",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Ocean Drive",
    "addressLocality": "Miami Beach",
    "addressRegion": "FL",
    "postalCode": "33139",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "25.7907",
    "longitude": "-80.1300"
  },
  "telephone": "+1-305-555-0123",
  "email": "info@oceanbreeze.com",
  "url": "https://app.stayfull.com/ocean-breeze",
  "priceRange": "$$-$$$",
  "starRating": {
    "@type": "Rating",
    "ratingValue": "4.8",
    "bestRating": "5"
  },
  "amenityFeature": [
    { "@type": "LocationFeatureSpecification", "name": "Free WiFi" },
    { "@type": "LocationFeatureSpecification", "name": "Pool" },
    { "@type": "LocationFeatureSpecification", "name": "Parking" }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "127"
  }
}
</script>
```

**Dynamic Schema Generation:**

```python
# apps/website/services/schema_service.py

def generate_hotel_schema(hotel):
    """Generate Schema.org JSON-LD for hotel."""

    schema = {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": hotel.name,
        "description": hotel.description or f"Stay at {hotel.name} in {hotel.address['city']}",
        "image": hotel.hero_image_url,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": hotel.address['street'],
            "addressLocality": hotel.address['city'],
            "addressRegion": hotel.address['state'],
            "postalCode": hotel.address['postal_code'],
            "addressCountry": hotel.address['country']
        },
        "telephone": hotel.contact['phone'],
        "email": hotel.contact['email'],
        "url": f"https://app.stayfull.com/{hotel.slug}",
        "priceRange": hotel.get_price_range(),  # e.g., "$150-$300"
    }

    # Add amenities
    if hotel.amenities:
        schema["amenityFeature"] = [
            {"@type": "LocationFeatureSpecification", "name": amenity}
            for amenity in hotel.amenities
        ]

    # Add ratings if available
    if hotel.average_rating:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(hotel.average_rating),
            "reviewCount": str(hotel.review_count),
            "bestRating": "5"
        }

    return schema
```

**4. robots.txt**

Control search engine crawling:

```
# /robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /nora/

Sitemap: https://app.stayfull.com/sitemap.xml
```

**5. Performance Optimization (SEO Factor)**

**Why Performance Matters for SEO:**
- Google uses page speed as ranking factor
- Core Web Vitals: LCP, FID, CLS
- Slow sites rank lower

**Optimization Strategies:**

```python
# 1. Image Optimization
- Serve WebP format (smaller than JPEG)
- Lazy loading (images load on scroll)
- Responsive images (different sizes for mobile/desktop)
- CDN delivery (CloudFront or similar)

# 2. Code Optimization
- Minify CSS/JS
- Gzip compression
- Browser caching headers
- Django template fragment caching

# 3. Database Optimization
- Query optimization (select_related, prefetch_related)
- Database indexing on frequently queried fields
- Redis caching for expensive queries
```

---

## Dynamic Updates & Version Control

### Publish Workflow

**Key Requirement**: Changes are NOT auto-published.

**Why:**
- Prevents accidental live updates
- Allows batching multiple changes
- Gives hotel control over timing
- Enables version history

### Website Manager Interface

**Architecture:**

```
Admin Dashboard → Website Manager → Live Website
     (PMS)            (Editor)        (Public)
```

**Website Manager** (`/admin/website/`):

```
┌────────────────────────────────────────────────────────────┐
│  Website Manager                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│  [View Live Site ↗]  [Save Draft]  [Publish Changes] ⚠️   │
│                                                            │
│  ⚠️ Unsaved changes                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                            │
│  ┌────────────────────┬─────────────────────────────────┐ │
│  │  Tabs:             │  Live Preview:                  │ │
│  │                    │                                 │ │
│  │  • General         │  [Desktop] [Mobile]             │ │
│  │  • Layout          │                                 │ │
│  │  • AI Assistant    │  ┌───────────────────────────┐ │ │
│  │                    │  │                           │ │ │
│  │ ┌────────────────┐ │  │  [Live website preview]   │ │ │
│  │ │ Hotel Name:    │ │  │  [Updates in real-time]   │ │ │
│  │ │ Ocean Breeze   │ │  │                           │ │ │
│  │ │                │ │  │                           │ │ │
│  │ │ Logo:          │ │  │                           │ │ │
│  │ │ [Upload] [🖼️]  │ │  │                           │ │ │
│  │ │                │ │  │                           │ │ │
│  │ │ Theme:         │ │  │                           │ │ │
│  │ │ ○ Modern       │ │  │                           │ │ │
│  │ │ ● Classic      │ │  │                           │ │ │
│  │ │ ○ Boutique     │ │  │                           │ │ │
│  │ │                │ │  │                           │ │ │
│  │ └────────────────┘ │  └───────────────────────────┘ │ │
│  └────────────────────┴─────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**Tabs:**

1. **General Tab**
   - Hotel name
   - Logo (text or image)
   - Theme selection (2 themes for MVP)
   - Color customization
   - Font customization
   - Header icon size
   - Guest dark mode toggle

2. **Layout Tab**
   - Component sequence (drag-and-drop)
   - Component visibility (show/hide)
   - Hero section settings:
     - Title text
     - Subtitle text
     - Media type (single image/slideshow/video)
     - Title/subtitle font sizes
     - Image height
   - Per-component settings:
     - Section headers
     - Descriptions
     - Photos
   - Amenities editor
   - Reviews editor

3. **AI Assistant Tab** (Future)
   - Generate content suggestions
   - Optimize SEO
   - Write blog posts
   - Create social media posts

### Real-Time Preview

**How It Works:**

```javascript
// User changes theme in General tab
// JavaScript sends message to iframe:

iframeRef.current.contentWindow.postMessage({
    type: 'THEME_UPDATE',
    themeColors: {
        primary: '#000000',
        secondary: '#333333',
        accent: '#0066FF'
    }
}, '*');

// Preview iframe receives message and updates CSS:
window.addEventListener('message', (event) => {
    if (event.data.type === 'THEME_UPDATE') {
        document.documentElement.style.setProperty('--primary', event.data.themeColors.primary);
        document.documentElement.style.setProperty('--secondary', event.data.themeColors.secondary);
        document.documentElement.style.setProperty('--accent', event.data.themeColors.accent);
    }
});
```

**No Page Reload**: Changes appear instantly in preview.

### Save vs. Publish

**Two-Stage System:**

1. **Save Draft**
   - Saves changes to database
   - Does NOT publish to live site
   - Preview updates
   - Can save multiple times before publishing

2. **Publish Changes**
   - Takes draft → makes it live
   - Creates version snapshot (for rollback)
   - Updates live website
   - Notifies search engines (sitemap ping)

**Database Architecture:**

```python
# apps/website/models.py

class WebsiteConfig(models.Model):
    """
    Website configuration for a hotel.

    Stores both draft and published versions.
    """

    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE)

    # Draft version (being edited)
    draft_config = models.JSONField(default=dict)
    draft_updated_at = models.DateTimeField(auto_now=True)

    # Published version (live on website)
    published_config = models.JSONField(default=dict)
    published_at = models.DateTimeField(null=True, blank=True)

    # Version history (last 10 changes)
    version_history = models.JSONField(default=list)

    def publish(self):
        """Publish draft to live site."""

        # Save current published version to history
        if self.published_config:
            self.version_history.insert(0, {
                'config': self.published_config,
                'published_at': self.published_at.isoformat(),
                'published_by': 'user_id_here'
            })

            # Keep only last 10 versions
            self.version_history = self.version_history[:10]

        # Publish draft
        self.published_config = self.draft_config.copy()
        self.published_at = timezone.now()
        self.save()

        # Ping sitemap to search engines
        ping_search_engines(self.hotel.slug)

    def revert_to_version(self, version_index):
        """Revert to a previous version."""

        if 0 <= version_index < len(self.version_history):
            old_version = self.version_history[version_index]
            self.draft_config = old_version['config'].copy()
            self.save()
```

### Version Control UI

**Version History Panel:**

```
┌──────────────────────────────────────────┐
│  Version History                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                          │
│  🟢 Current (published)                  │
│     Oct 23, 2025 at 2:30 PM             │
│     by Sarah Johnson                     │
│     [View]                               │
│                                          │
│  ○  Version 2                            │
│     Oct 22, 2025 at 4:15 PM             │
│     Updated hero image                   │
│     [View] [Revert to This]             │
│                                          │
│  ○  Version 3                            │
│     Oct 20, 2025 at 10:00 AM            │
│     Changed theme to Classic             │
│     [View] [Revert to This]             │
│                                          │
│  ... (7 more versions)                   │
│                                          │
│  [Load More Versions]                    │
└──────────────────────────────────────────┘
```

**Revert Workflow:**

```
User clicks "Revert to This" on Version 2
↓
Confirmation dialog:
┌──────────────────────────────────────────┐
│  Revert to Version 2?                    │
│                                          │
│  This will replace your current draft    │
│  with this version. You can still undo   │
│  by reverting to the current version.    │
│                                          │
│  [Cancel]  [Revert to This Version]     │
└──────────────────────────────────────────┘
↓
Draft config ← Version 2 config
↓
Preview updates to show Version 2
↓
User can edit, then Publish
```

---

## AI Content Generation

### Strategic Importance

**Quote from discovery**: "Things to do and events... is most valuable feature in my opinion (ie create social media posts, update events calendar, write blogs, etc) as these are all things that drive traffic to the commerce engine that are basically free."

**Why AI Content Matters:**

1. **SEO Traffic Magnet**
   - "Things To Do Miami Beach" = high search volume
   - Hotels rank for local content keywords
   - Drives traffic from Google → Hotel website → Bookings

2. **Zero Effort for Hotel**
   - AI generates during onboarding
   - Auto-updates monthly/seasonally
   - No manual content creation

3. **Competitive Differentiator**
   - Mews, Cloudbeds, other PMS: No content generation
   - Stayfull: Auto-generated blog-quality content
   - Shows AI capability (builds trust)

4. **Future Revenue Streams**
   - Hotels pay for content upgrades
   - Social media post generation
   - Email campaign writing
   - All built on same AI infrastructure

### Things To Do Component

**Generated During F-002 Onboarding:**

```python
# apps/ai_agent/services/content_generator.py

class ThingsToDoGenerator:
    """
    Generate "Things To Do" content based on hotel location.

    Uses:
    - Hotel geolocation (lat/lng from address)
    - Current season (from datetime)
    - OpenAI GPT-4o (research + writing)
    - Google Places API (photos, ratings)
    - Yelp/TripAdvisor APIs (optional)
    """

    def generate(self, hotel):
        """
        Generate 10-15 local attractions.

        Returns list of attractions with:
        - Name
        - Category (Museums, Outdoors, Food, Nightlife, Shopping)
        - Distance from hotel
        - Description (150 words)
        - Photo URL
        - Price range
        - Website/booking link
        """

        season = self.get_current_season()
        location = f"{hotel.address['city']}, {hotel.address['state']}"

        # Step 1: Research attractions with GPT-4o
        prompt = f"""
        You are a local expert for {location}.

        Generate a list of 15 must-visit attractions for travelers staying in {location} during {season}.

        Include a diverse mix:
        - 3 museums/cultural sites
        - 3 outdoor activities
        - 3 restaurants/food experiences
        - 3 nightlife/entertainment
        - 3 shopping/local experiences

        For each attraction, provide:
        - Name
        - Category
        - Why it's special (2-3 sentences)
        - Approximate distance from downtown {hotel.address['city']}
        - Price range ($, $$, $$$)

        Format as JSON array.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        attractions = json.loads(response.choices[0].message.content)

        # Step 2: Enrich with real data (Google Places)
        enriched = []
        for attraction in attractions:
            # Search Google Places for this attraction
            places_result = self.google_places_search(
                query=f"{attraction['name']} {location}",
                location=hotel.get_coordinates()
            )

            if places_result:
                attraction['photo_url'] = places_result['photo_url']
                attraction['rating'] = places_result['rating']
                attraction['address'] = places_result['address']
                attraction['website'] = places_result['website']
                attraction['distance_km'] = self.calculate_distance(
                    hotel.get_coordinates(),
                    places_result['coordinates']
                )

            # Generate detailed description
            attraction['description'] = self.generate_description(attraction, season)

            enriched.append(attraction)

        return enriched

    def generate_description(self, attraction, season):
        """
        Generate compelling 150-word description.

        Optimized for:
        - SEO keywords
        - Engaging prose
        - Local expertise tone
        """

        prompt = f"""
        Write a compelling 150-word description for: {attraction['name']}

        Category: {attraction['category']}
        Location: {attraction.get('address', 'Unknown')}
        Season: {season}

        Tone: Enthusiastic local expert
        Include: Why visitors love it, what makes it unique, best time to visit
        SEO: Use keywords like "{attraction['category'].lower()}", "best", "must-visit"

        Write 150 words exactly.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
```

**Example Output:**

```json
[
  {
    "id": "ttd-1",
    "name": "Pérez Art Museum Miami",
    "category": "Museums",
    "description": "Discover contemporary art at its finest in this waterfront architectural gem. Pérez Art Museum Miami (PAMM) showcases international works from the 20th and 21st centuries, with a special focus on artists from the Americas, Caribbean, and Africa. The museum's stunning location on Biscayne Bay offers breathtaking views that complement the inspiring exhibitions. Don't miss the hanging gardens designed by Patrick Blanc – they're as much a work of art as the collections inside. October through March is perfect for visiting when the weather is ideal for exploring the outdoor sculpture garden. PAMM's Thursday evening events feature live music and extended hours, creating the perfect blend of culture and Miami's vibrant social scene. Whether you're an art aficionado or casual appreciator, PAMM delivers an unforgettable museum experience.",
    "distance_km": 2.3,
    "price_range": "$$",
    "rating": 4.6,
    "photo_url": "https://lh3.googleusercontent.com/...",
    "website": "https://www.pamm.org",
    "address": "1103 Biscayne Blvd, Miami, FL 33132"
  },
  {
    "id": "ttd-2",
    "name": "Wynwood Walls",
    "category": "Outdoors",
    "description": "...",
    "distance_km": 3.1,
    ...
  },
  // ... 13 more
]
```

**Storage:**

```python
# apps/hotels/models.py

class ThingsToDoItem(models.Model):
    """AI-generated local attraction."""

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='things_to_do')

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)  # Museums, Outdoors, Food, etc.
    description = models.TextField(max_length=500)

    distance_km = models.DecimalField(max_digits=4, decimal_places=1)
    price_range = models.CharField(max_length=10)  # $, $$, $$$

    photo_url = models.URLField()
    website = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=300)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)

    # SEO
    slug = models.SlugField(max_length=250)

    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
```

### Events Component

**Similar to Things To Do, but event-focused:**

```python
class EventsGenerator:
    """
    Generate "Events" content based on hotel location and current date.

    Uses:
    - Ticketmaster API
    - Eventbrite API
    - GPT-4o (enhancement)
    """

    def generate(self, hotel, date_range_days=90):
        """
        Generate 5-10 upcoming events.

        Categories:
        - Concerts
        - Sports
        - Theater
        - Festivals
        - Conferences
        """

        location = hotel.get_coordinates()

        # Get events from Ticketmaster
        ticketmaster_events = self.fetch_ticketmaster_events(
            location=location,
            radius_km=25,
            date_range=date_range_days
        )

        # Get events from Eventbrite
        eventbrite_events = self.fetch_eventbrite_events(
            location=location,
            date_range=date_range_days
        )

        # Combine and deduplicate
        all_events = self.merge_events(ticketmaster_events, eventbrite_events)

        # Enhance with GPT-4o (better descriptions)
        enhanced = []
        for event in all_events[:10]:  # Top 10 events
            event['description'] = self.enhance_description(event)
            enhanced.append(event)

        return enhanced
```

**Example Output:**

```json
[
  {
    "id": "evt-1",
    "name": "Miami Heat vs. Boston Celtics",
    "category": "Sports",
    "date": "2025-11-15T19:30:00",
    "venue": "FTX Arena",
    "description": "Experience the intensity of NBA basketball as the Miami Heat take on their Eastern Conference rivals, the Boston Celtics. This matchup promises high-energy plays, star power, and the electric atmosphere that makes Heat games unforgettable. Located in downtown Miami, FTX Arena offers state-of-the-art facilities and incredible sightlines. Arrive early to enjoy the pre-game festivities and Miami's vibrant downtown scene. Whether you're a die-hard basketball fan or looking for an exciting night out, this game delivers non-stop action and entertainment.",
    "price_range": "$$$",
    "photo_url": "https://...",
    "tickets_url": "https://www.ticketmaster.com/...",
    "distance_km": 1.8
  },
  // ... more events
]
```

**Auto-Update Strategy:**

```python
# Regenerate events monthly (cron job)
# apps/hotels/management/commands/regenerate_events.py

class Command(BaseCommand):
    """Regenerate events for all active hotels."""

    def handle(self, *args, **options):
        hotels = Hotel.objects.filter(is_active=True)

        for hotel in hotels:
            # Delete old events
            hotel.events.filter(date__lt=timezone.now()).delete()

            # Generate new events
            generator = EventsGenerator()
            events = generator.generate(hotel)

            # Save to database
            for event_data in events:
                Event.objects.create(
                    hotel=hotel,
                    **event_data
                )

            self.stdout.write(f"✓ Regenerated events for {hotel.name}")
```

**Cron Schedule:**

```bash
# Run monthly on 1st of month at 3:00 AM
0 3 1 * * python manage.py regenerate_events
```

---

## Integration with F-002

### Data Flow: F-002 → F-003

**Onboarding Creates Everything Website Needs:**

```
F-002 Onboarding                    →  F-003 Website
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hotel Model:
- name: "Ocean Breeze Resort"       →  Hero title, page title
- address: "Miami Beach, FL"        →  Location section, meta tags
- contact: phone, email             →  Contact info, footer
- check_in_time: "3:00 PM"          →  Policies section
- check_out_time: "11:00 AM"        →  Policies section
- hero_image: URL                   →  Hero section background
- logo: URL                         →  Header logo

RoomType Models (3 types):
- name: "Standard Queen Room"       →  Rooms carousel
- description: AI-enhanced          →  Room detail page
- photos: [URL, URL, URL]           →  Room gallery
- base_price: $199                  →  Pricing display
- max_occupancy: 2                  →  Room details
- amenities: [wifi, tv, ...]        →  Room features

Policies:
- cancellation_policy: {...}        →  "💳 Free cancellation up to 24 hours..."
- payment_policy: {...}             →  "💳 50% deposit at booking..."

AI-Generated Content:
- things_to_do: [15 items]          →  Things To Do section
- events: [10 items]                →  Events section

Amenities:
- amenities: [wifi, parking, ...]   →  Amenities section (icon grid)
```

### Success Page Integration

**After F-002 Onboarding Completes:**

```python
# apps/ai_agent/views.py

def complete_onboarding(request):
    """
    F-002 onboarding completion endpoint.

    Called when Nora finishes onboarding flow.

    Actions:
    1. Create Hotel/RoomType/Room records (F-002 Phase 6)
    2. Generate AI content (Things To Do, Events)
    3. Create WebsiteConfig (F-003)
    4. Generate sitemap
    5. Show success page with CTAs
    """

    context = NoraContext.objects.get(user=request.user, organization=...)
    session_data = context.task_state

    # Create hotel data (F-002 Phase 6)
    hotel = create_hotel_from_session(session_data, request.user)

    # Generate AI content (F-003)
    generate_things_to_do(hotel)
    generate_events(hotel)

    # Create website config (F-003)
    WebsiteConfig.objects.create(
        hotel=hotel,
        published_config={
            'theme': 'classic',
            'components': get_default_components(),
            'hero_title': hotel.name,
            'hero_subtitle': 'Your perfect stay awaits',
        }
    )

    # Generate sitemap
    generate_sitemap(hotel)

    # Mark onboarding complete
    context.complete_task()

    # Render success page
    return render(request, 'ai_agent/success.html', {
        'hotel': hotel,
        'website_url': f"https://app.stayfull.com/{hotel.slug}",
        'admin_url': '/admin/dashboard/',
    })
```

**Success Page Template:**

```html
<!-- apps/ai_agent/templates/ai_agent/success.html -->

<div class="success-page">
    <div class="confetti-animation"></div>

    <h1>🎉 Your hotel is live!</h1>
    <p class="time-elapsed">We did that in {{ onboarding_duration }} minutes!</p>

    <div class="website-preview">
        <a href="{{ website_url }}" target="_blank">
            {{ hotel.slug }}.stayfull.com
        </a>
    </div>

    <div class="cta-buttons">
        <a href="{{ admin_url }}" class="btn btn-primary">
            Explore Admin Dashboard
        </a>

        <a href="{{ website_url }}" target="_blank" class="btn btn-secondary">
            View Hotel Website ↗
        </a>
    </div>

    <div class="next-steps">
        <p>Remember: I'm always here to help!</p>
        <p>Just click the Nora icon and ask me anything.</p>
    </div>
</div>
```

### Admin Dashboard → Website Manager Flow

**When user clicks "Explore Admin Dashboard":**

```python
# apps/admin/views/dashboard.py

@login_required
def dashboard_view(request):
    """
    Main PMS dashboard.

    Shows:
    - Today's revenue
    - Occupancy
    - Check-ins/check-outs
    - Messages
    - Tasks
    - Quick actions
    """

    staff = request.user.staff_positions.first()
    hotel = staff.organization.hotels.first()  # Single property MVP

    context = {
        'hotel': hotel,
        'revenue_today': calculate_revenue_today(hotel),
        'occupancy': calculate_occupancy(hotel),
        'checkins_today': get_checkins_today(hotel),
        'checkouts_today': get_checkouts_today(hotel),
        'unread_messages': get_unread_messages(hotel),
        'pending_tasks': get_pending_tasks(hotel),
    }

    return render(request, 'admin/dashboard.html', context)
```

**Dashboard Template:**

```html
<!-- apps/admin/templates/admin/dashboard.html -->

<div class="dashboard">
    <h1>Dashboard</h1>
    <p>Today's operations at a glance</p>

    <!-- Quick Stats (4 cards) -->
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Today's Revenue</h3>
            <p class="stat-value">${{ revenue_today }}</p>
            <p class="stat-change">+18% from yesterday</p>
        </div>

        <div class="stat-card">
            <h3>Occupancy</h3>
            <p class="stat-value">{{ occupancy }}%</p>
            <p class="stat-detail">28 of 34 rooms occupied</p>
        </div>

        <!-- ... more stats -->
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
        <a href="/admin/website/" class="action-btn">
            Edit Website
        </a>
        <a href="/admin/rooms/" class="action-btn">
            Manage Rooms
        </a>
        <a href="/admin/rates/" class="action-btn">
            Update Rates
        </a>
    </div>

    <!-- Today's Activity (2x2 grid) -->
    <!-- Check-ins, Check-outs, Messages, Tasks -->
</div>
```

**When user clicks "Edit Website":**

Redirects to: `/admin/website/` (Website Manager interface from Section 9)

---

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Users                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Railway)                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌───────────────────┐                 ┌───────────────────┐
│  Django App       │                 │  Static Assets    │
│  (PMS + Website)  │                 │  (CDN)            │
│                   │                 │                   │
│  Apps:            │                 │  - Images         │
│  - hotels         │                 │  - CSS/JS         │
│  - ai_agent       │                 │  - Videos         │
│  - website        │                 └───────────────────┘
│  - bookings       │
│  - admin          │
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                        │
│                                                               │
│  Tables:                                                      │
│  - hotels_hotel                                               │
│  - hotels_roomtype                                            │
│  - hotels_room                                                │
│  - website_websiteconfig                                      │
│  - bookings_reservation                                       │
│  - content_thingstodoitem                                     │
│  - content_event                                              │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                    External Services                          │
│                                                               │
│  - OpenAI (GPT-4o, Whisper)                                   │
│  - Stripe (Payments)                                          │
│  - Google Places API (Location data)                          │
│  - Ticketmaster API (Events)                                  │
│  - Eventbrite API (Events)                                    │
│  - Email (SendGrid)                                           │
│  - SMS (Twilio)                                               │
└───────────────────────────────────────────────────────────────┘
```

### URL Structure

**Consumer-Facing (F-003 Website):**

```
app.stayfull.com/
├── {slug}/                          # Hotel homepage
│   ├── rooms/                       # Rooms overview
│   │   └── {room-slug}/             # Room detail page
│   ├── offers/                      # Special offers
│   │   └── {offer-slug}/            # Offer detail
│   ├── things-to-do/                # Things To Do
│   │   └── {attraction-slug}/       # Attraction detail
│   ├── events/                      # Events
│   │   └── {event-slug}/            # Event detail
│   ├── dining/                      # Dining info
│   ├── shop/                        # Merchandise
│   ├── location/                    # Location/contact
│   └── book/                        # Booking flow
│
├── sitemap.xml                      # SEO sitemap
└── robots.txt                       # Search engine rules
```

**Admin-Facing (PMS):**

```
app.stayfull.com/
├── admin/
│   ├── dashboard/                   # Main PMS dashboard
│   ├── website/                     # Website Manager (F-003)
│   ├── rooms/                       # Room management
│   ├── rates/                       # Rate management
│   ├── reservations/                # Booking management
│   ├── guests/                      # Guest database
│   ├── reports/                     # Analytics
│   └── settings/                    # Hotel settings
│
└── nora/                            # F-002 AI Agent
    ├── welcome/                     # Onboarding welcome
    ├── chat/                        # Nora chat interface
    └── api/                         # Nora API endpoints
```

### Django Apps Structure

**New Apps for F-003:**

```
apps/
├── website/                         # F-003 Website Engine
│   ├── models.py                    # WebsiteConfig, ThingsToDoItem, Event
│   ├── views/
│   │   ├── public.py                # Consumer-facing pages
│   │   ├── admin.py                 # Website Manager
│   │   └── sitemap.py               # SEO sitemap
│   ├── services/
│   │   ├── content_generator.py     # AI content generation
│   │   ├── seo_service.py           # Meta tags, schema
│   │   └── theme_service.py         # Theme rendering
│   ├── templates/
│   │   ├── website/                 # Consumer templates
│   │   └── admin/                   # Website Manager
│   └── urls.py
│
├── bookings/                        # Booking Engine
│   ├── models.py                    # Reservation, Payment
│   ├── views/
│   │   ├── booking_flow.py          # 4-step booking
│   │   ├── confirmation.py          # Success page
│   │   └── webhooks.py              # Stripe webhooks
│   ├── services/
│   │   ├── availability.py          # Room availability
│   │   ├── pricing.py               # Price calculation
│   │   ├── payment_service.py       # Stripe integration
│   │   └── notification_service.py  # Email/SMS
│   └── urls.py
│
├── hotels/                          # Existing (F-001)
│   ├── models.py                    # Hotel, RoomType, Room
│   └── ...
│
└── ai_agent/                        # Existing (F-002)
    ├── models.py                    # NoraContext
    └── ...
```

### Database Models

**New Models for F-003:**

```python
# apps/website/models.py

class WebsiteConfig(models.Model):
    """Website configuration for a hotel."""
    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE)
    draft_config = models.JSONField(default=dict)
    published_config = models.JSONField(default=dict)
    published_at = models.DateTimeField(null=True, blank=True)
    version_history = models.JSONField(default=list)

class ThingsToDoItem(models.Model):
    """AI-generated local attraction."""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='things_to_do')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    distance_km = models.DecimalField(max_digits=4, decimal_places=1)
    price_range = models.CharField(max_length=10)
    photo_url = models.URLField()
    website = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=250)
    is_active = models.BooleanField(default=True)

class Event(models.Model):
    """AI-generated upcoming event."""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    price_range = models.CharField(max_length=10)
    photo_url = models.URLField()
    tickets_url = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=250)
    is_active = models.BooleanField(default=True)

# apps/bookings/models.py

class Reservation(models.Model):
    """Guest booking."""
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)

    # Guest info
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    # Dates
    check_in = models.DateField()
    check_out = models.DateField()
    nights = models.IntegerField()

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=200)

    # Metadata
    confirmation_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    """Payment record."""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20)  # deposit, balance, refund
    stripe_charge_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Security & Multi-Tenancy

### Multi-Tenancy Isolation

**Critical**: All queries MUST filter by organization.

```python
# ✅ CORRECT
hotels = Hotel.objects.filter(organization=request.user.organization)

# ❌ WRONG - Data leakage!
hotels = Hotel.objects.all()
```

**For F-003:**

```python
# Consumer website pages (no authentication)
def hotel_homepage(request, slug):
    """Public hotel homepage - no auth required."""

    # Anyone can view any hotel
    hotel = Hotel.objects.get(slug=slug, is_active=True)

    # But only see published content
    config = hotel.websiteconfig.published_config

    return render(request, 'website/homepage.html', {
        'hotel': hotel,
        'config': config
    })

# Website Manager (admin only)
@login_required
def website_manager(request):
    """Edit hotel website - requires auth + ownership."""

    # Get user's organization
    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Get hotel (single property MVP)
    hotel = organization.hotels.first()

    # Can only edit own hotel
    return render(request, 'admin/website_manager.html', {
        'hotel': hotel,
        'config': hotel.websiteconfig.draft_config
    })

# Booking creation (no auth, but organization-scoped)
def create_booking(request, slug):
    """Create booking - no auth, but must be for valid hotel."""

    hotel = Hotel.objects.get(slug=slug, is_active=True)

    # Reservation is automatically scoped to this hotel
    reservation = Reservation.objects.create(
        hotel=hotel,  # Organization scoped via hotel FK
        ...
    )
```

### Payment Security

**PCI Compliance:**

- ✅ Stripe handles card data (never touch PCI)
- ✅ Use Stripe Checkout or Elements (iframes)
- ✅ Never log payment details
- ✅ Webhooks verify signatures

**Stripe Connect Security:**

```python
# Verify webhook signature
try:
    event = stripe.Webhook.construct_event(
        payload,
        sig_header,
        settings.STRIPE_WEBHOOK_SECRET  # ← Critical security check
    )
except stripe.error.SignatureVerificationError:
    # Invalid signature = potential attack
    return HttpResponse(status=400)
```

### CSRF Protection

**All POST endpoints protected:**

```python
# Django CSRF middleware enabled (settings.py)
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    ...
]

# Templates include CSRF token
<form method="post">
    {% csrf_token %}
    ...
</form>

# Stripe webhooks exempted (signature verification instead)
@csrf_exempt
def stripe_webhook(request):
    # Uses Stripe signature verification instead of CSRF
    ...
```

### Rate Limiting

**Prevent abuse on public endpoints:**

```python
# pip install django-ratelimit

from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def create_booking(request, slug):
    """
    Limit booking creation to 10 per minute per IP.

    Prevents:
    - Spam bookings
    - Inventory locking attacks
    - Bot abuse
    """
    ...
```

---

## Definition of Done

### Functional Requirements

**F-003 is complete when:**

- [ ] **Website Generation**
  - [ ] Hotel website automatically generated from F-002 onboarding data
  - [ ] Website live at `app.stayfull.com/[slug]` immediately after onboarding
  - [ ] All 11 components render correctly
  - [ ] Component visibility rules work (show/hide based on content)
  - [ ] Mobile responsive (tested on iPhone, Android)

- [ ] **Website Manager**
  - [ ] Website Manager accessible at `/admin/website/`
  - [ ] General tab: Name, logo, theme selection works
  - [ ] Layout tab: Component sequencing (drag-drop) works
  - [ ] Live preview updates in real-time (no page reload)
  - [ ] Desktop/mobile preview toggle works
  - [ ] Save Draft button saves changes to database
  - [ ] Publish button publishes to live site
  - [ ] Version history shows last 10 changes
  - [ ] Revert to previous version works

- [ ] **Booking Engine**
  - [ ] "Book Now" button visible in sticky header
  - [ ] Booking modal opens with date/guest selectors
  - [ ] Room availability calculation works correctly
  - [ ] Price calculation includes taxes
  - [ ] Guest details form captures name, email, phone
  - [ ] Stripe payment integration works
  - [ ] Deposit vs. full payment based on policy
  - [ ] Confirmation page shows booking details
  - [ ] Confirmation email sent to guest
  - [ ] Confirmation email sent to hotel
  - [ ] SMS confirmation sent to guest

- [ ] **Reservation Integration**
  - [ ] Booking creates Reservation record in database
  - [ ] Room inventory decreases (occupancy updates)
  - [ ] Reservation appears in PMS dashboard "Check-ins Today"
  - [ ] Revenue stats update
  - [ ] Housekeeping task created
  - [ ] Calendar updated

- [ ] **AI Content**
  - [ ] Things To Do: 10-15 items generated during onboarding
  - [ ] Events: 5-10 items generated during onboarding
  - [ ] Content uses hotel geolocation + seasonality
  - [ ] Photos from Google Places or AI-generated
  - [ ] Descriptions are compelling (150 words)

- [ ] **SEO**
  - [ ] Meta tags dynamically generated per page
  - [ ] Open Graph tags for social media
  - [ ] Sitemap.xml generated and accessible
  - [ ] robots.txt configured
  - [ ] Schema.org JSON-LD markup on all pages
  - [ ] Canonical URLs set correctly
  - [ ] Page load time < 3 seconds

- [ ] **Payment Processing**
  - [ ] Stripe Connect sub-account created during onboarding
  - [ ] Payment Intent created correctly
  - [ ] Commission routed to Stayfull platform account
  - [ ] Hotel payout routed to sub-account
  - [ ] Webhooks handle payment_intent.succeeded
  - [ ] Webhooks handle payment_intent.failed
  - [ ] Refunds processed correctly

### Technical Requirements

- [ ] **Code Quality**
  - [ ] All code follows `.architect/DEVELOPMENT_STANDARDS.md`
  - [ ] Multi-tenancy isolation verified (no cross-organization data leakage)
  - [ ] Test coverage > 80% for new code
  - [ ] No hardcoded secrets (all in environment variables)
  - [ ] Code reviewed by architect

- [ ] **Security**
  - [ ] CSRF protection on all POST endpoints
  - [ ] Stripe webhook signature verification
  - [ ] Rate limiting on public endpoints
  - [ ] Input validation on all forms
  - [ ] SQL injection prevention (Django ORM)
  - [ ] XSS prevention (Django templates auto-escape)

- [ ] **Performance**
  - [ ] Database queries optimized (select_related, prefetch_related)
  - [ ] Images optimized (WebP, lazy loading)
  - [ ] CDN configured for static assets
  - [ ] Django template fragment caching
  - [ ] Page load time < 3 seconds

- [ ] **Deployment**
  - [ ] Deployed to Railway
  - [ ] Environment variables configured
  - [ ] Database migrations applied
  - [ ] Static files collected and served via CDN
  - [ ] Email/SMS services configured (SendGrid, Twilio)
  - [ ] Stripe webhooks endpoint configured

### User Acceptance Testing

- [ ] **Complete User Journey**
  - [ ] Complete F-002 onboarding (10 minutes)
  - [ ] See success page with two CTAs
  - [ ] Click "View Hotel Website" → website loads
  - [ ] Website shows all sections with content
  - [ ] Things To Do and Events sections populated
  - [ ] Click "Book Now" → booking modal opens
  - [ ] Select dates, room, enter guest details
  - [ ] Complete payment → confirmation page
  - [ ] Receive confirmation email + SMS
  - [ ] Hotel receives notification email
  - [ ] Check PMS dashboard → see new reservation
  - [ ] Edit website via Website Manager
  - [ ] Publish changes → live site updates
  - [ ] Revert to previous version → works correctly

- [ ] **Cross-Browser Testing**
  - [ ] Chrome (desktop + mobile)
  - [ ] Firefox (desktop)
  - [ ] Safari (desktop + iOS)
  - [ ] Edge (desktop)

- [ ] **Accessibility**
  - [ ] WCAG AA compliant
  - [ ] Keyboard navigation works
  - [ ] Screen reader tested
  - [ ] Color contrast ratios meet standards

### Documentation

- [ ] **Developer Documentation**
  - [ ] README updated with F-003 setup instructions
  - [ ] API documentation for booking endpoints
  - [ ] Stripe integration guide
  - [ ] SEO configuration guide

- [ ] **User Documentation** (Future)
  - [ ] Website Manager user guide
  - [ ] How to customize theme
  - [ ] How to add/edit content
  - [ ] Booking management guide

---

## 🎯 Success Metrics

**F-003 is successful when:**

1. **Time to Launch**: Hotel goes live in <10 minutes (including onboarding)
2. **Booking Conversion**: >2% of website visitors complete bookings
3. **SEO Performance**: Hotels rank on page 1 for "[hotel name] [city]" within 30 days
4. **Payment Success**: >95% payment success rate (Stripe)
5. **User Satisfaction**: Hotels rate Website Manager 4.5+ stars
6. **Technical Performance**: Page load <3 seconds, 99.9% uptime

---

**This is the KILLER FEATURE. Make it fast, beautiful, and profitable.** 🚀

**Questions? Review with product owner before starting development.**
