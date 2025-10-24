# F-002: Nora AI Onboarding Agent (Revised)

**Status**: Spec Complete - Ready for User Review
**Priority**: P1 - Killer Feature
**Effort**: TBD (after review)
**Dependencies**: F-001.1 (Organization model)
**Created**: 2025-10-23 (Original)
**Revised**: 2025-10-23 (Complete Rewrite After Discovery)

---

## 🔄 What Changed from Original Spec

**Original Understanding** (Built in isolation):
- ❌ Just an onboarding feature
- ❌ Included website builder/templates (that's F-003)
- ❌ Session-based, one-time use
- ❌ Missed data acceleration opportunities
- ❌ No concept of editable vs. locked fields
- ❌ Voice as "maybe later"

**New Understanding** (After collaborative discovery):
- ✅ **Nora = System-wide AI agent** (powers all 21+ features)
- ✅ **Persistent context** (remembers, learns, always available)
- ✅ **Aggressive data extraction** (website scraping, Google Places, smart defaults)
- ✅ **Opinionated UX** (user controls data, Stayfull controls presentation)
- ✅ **Voice + text from day one**
- ✅ **Real-time preview with edit controls**
- ✅ **"Play Me First" intro video** (builds immediate trust)

---

## Executive Summary

**What This Is**: Nora, your AI hotel operations co-worker who guides hotel owners through 10-minute onboarding and remains available for all system operations thereafter.

**The Transformation**:
- Industry standard: 6-12 months to launch
- Stayfull with Nora: 10 minutes

**The Wow Factor**:
- User provides 10% input (basic answers)
- AI does 90% of work (extraction, enhancement, formatting, generation)
- Fully operational website at end of conversation
- Professional photos, enhanced descriptions, formatted policies

**The Strategy**: Intentionally polarizing. AI-first approach filters customers - those scared of AI self-select out on day one, saving both parties time.

---

## 1. The Problem

**Traditional PMS Onboarding:**
- 60-90 minute forms
- Complex, unclear fields
- 40% abandonment rate
- High support burden
- Requires technical skills
- No immediate value
- Barrier to customer acquisition

**Mews Example** (User's experience):
- 3-4 weeks calendar time (could be 1 day without waiting)
- 20-room hotel setup
- Language confusion ("spaces" vs "rooms")
- Low-tech users struggled
- Multiple staff needed

---

## 2. The Solution: Nora

### 2.1 Core Concept

**Nora = Expert-level AI co-worker, available 24/7 for ALL hotel operations**

She's not a feature - she's the primary interface for the entire PMS.

**Architecture Inspirations:**
- **Airbnb's templates**: Standardized design, custom content only
- **Shopify's commerce**: Platform is commerce-aware from ground up
- **ChatGPT's interface**: Natural language for complex operations

### 2.2 First Impression: "Play Me First"

**User Journey:**
1. User signs up → creates account
2. Lands on welcome screen with large play button
3. 45-second video introduces Nora
4. Onboarding begins immediately after
5. 10 minutes later: operational hotel website

**Video Script (45 seconds):**
```
NORA (enthusiastic, professional):

"Hi! I'm Nora, your AI co-worker here at Stayfull.

Think of me as your expert-level teammate who knows
everything about hotel operations - from setting up
your property to managing daily bookings and beyond.

Here's what makes me different: You can talk to me
just like you'd talk to a co-worker. Need to create
a booking? Just ask. Want to check tomorrow's arrivals?
I've got it. Curious about your revenue this month?
I'll pull that up for you.

I work through text OR voice - whatever feels natural
to you.

Right now, let's get your hotel set up together.
It'll take about 10 minutes, and I'll guide you
through every step.

And remember: I'm always here. Anytime you need help,
just click my icon and ask. I can do pretty much
anything in the system for you.

Ready? Let's build your hotel!"

[Button appears: "Let's Go, Nora!" 🚀]
```

**Technical Specs:**
- **Voice**: ElevenLabs OR OpenAI Realtime (configurable, swappable)
- **Avatar**: Static illustration (professional, friendly)
- **Video**: MP4, max 5MB, plays once on first login
- **Can replay**: Available in settings
- **Skippable**: User can skip to setup

**Voice Persona:**
- **Default Tone**: Enthusiastic (but professional)
- **Customizable in Settings**:
  - Option 1: Enthusiastic (default)
  - Option 2: Professional & Calm
  - Option 3: Casual & Friendly
- **Voice Type**: Female, clear articulation
- **Speaking Pace**: 150-160 WPM (conversational)
- **Language**: English only (MVP)

---

## 3. Onboarding Architecture

### 3.1 UX Layout

**Desktop (Split Screen - 50/50):**
```
┌──────────────────────────────────────────────────────────┐
│ Progress: [████████░░░░░░░] 60% - Room Types           │
├────────────────────────┬─────────────────────────────────┤
│                        │                                 │
│  NORA (Left 50%)       │  LIVE PREVIEW (Right 50%)      │
│                        │                                 │
│  [Chat messages]       │  [Guest-facing website]        │
│  [Voice 🎤 / Text ⌨️]  │  [Updates in real-time]        │
│                        │  [Edit buttons on hover]       │
│                        │                                 │
└────────────────────────┴─────────────────────────────────┘
```

**Mobile (Tab/Toggle):**
```
┌─────────────────────────┐
│  [Chat] | [Preview]     │ ← Toggle tabs
├─────────────────────────┤
│                         │
│  Active tab full screen │
│                         │
│  (Chat OR Preview)      │
│                         │
├─────────────────────────┤
│  Tab switcher at bottom │
└─────────────────────────┘
```

### 3.2 The "10% Input, 90% AI" Principle

**Priority Order for Data Collection:**

1. **Website scraping** (if user has website)
   - Extracts: Name, address, contact, room types, pricing, photos, policies
   - Time saved: ~8 minutes

2. **Google Places API** (validate/enhance data)
   - Gets: Verified address, phone, high-res photos, timezone
   - Time saved: ~3 minutes

3. **OTA import** (if listed on Booking.com/Expedia)
   - Imports: Professional room descriptions, policies, photos
   - Time saved: ~5 minutes

4. **Smart defaults** (infer from location)
   - Sets: Currency, tax rates, check-in/out times, typical pricing
   - Time saved: ~2 minutes

5. **CSV upload** (if they have spreadsheet)
   - Imports: Room types, inventory, pricing
   - Time saved: ~4 minutes

6. **Manual Q&A** (only for missing data)
   - Guided questions one at a time
   - Nora asks minimum required questions

**Example Acceleration:**
```
NORA: What's your hotel website?
USER: sunsetvilla.com
NORA: 🔍 Scanning website... [8 seconds]
      🔍 Cross-referencing Google Places...
      🔍 Analyzing similar hotels in Miami...

      🎉 Found everything! Extracted:
      ✅ Sunset Villa, Miami, FL
      ✅ Contact info
      ✅ 3 room types with pricing
      ✅ 12 photos
      ✅ Policies

      That saved us 8 minutes! Let me show you...
      [Shows live preview with all data]

      Just need to confirm a few things:
      1. How many rooms do you have total?
```

---

## 4. Core Principle: Editable Data vs. Locked Presentation

### 4.1 The Philosophy

**"Protect hotel operators from bad UX while enforcing their business rules as defined."**

Hotel owners are terrible marketers. If we let them write free-form policy text, they'll hurt their own conversion rates. Instead:

- **User controls**: Business rules, data, values, content
- **Stayfull controls**: Formatting, presentation, guest-facing UX

### 4.2 Visual Pattern

**In Live Preview (During Onboarding):**
```
┌─── LIVE PREVIEW ──────────────────────────────────┐
│                                                   │
│  💳 50% deposit at booking, rest on arrival       │
│     ↑ User CANNOT edit this text directly         │
│                                                   │
│      [Edit deposit rules] ← Button appears hover │
│         ↑ Opens structured form                   │
└───────────────────────────────────────────────────┘
```

**Clicking [Edit] Opens Structured Modal:**
```
┌─── EDIT PAYMENT POLICY ───────────────────────────┐
│                                                   │
│  Deposit Amount:                                  │
│  [50] [% ▼]  or  [$] [___]                       │ ✅ Edit
│                                                   │
│  Deposit Due:                                     │
│  [At booking ▼]                                   │ ✅ Edit
│     Options: At booking, X days before arrival   │
│                                                   │
│  Remaining Balance Due:                           │
│  [On arrival ▼]                                   │ ✅ Edit
│     Options: On arrival, X days before, At booking│
│                                                   │
│  ─────────────────────────────────────────────    │
│                                                   │
│  ✨ Guest Will See:                               │
│  ┌─────────────────────────────────────────────┐ │
│  │ 💳 50% deposit at booking, rest on arrival  │ │ ❌ Locked
│  └─────────────────────────────────────────────┘ │
│     ↑ AI-generated, updates live as you edit     │
│                                                   │
│  [Cancel]  [Save Changes]                         │
└───────────────────────────────────────────────────┘
```

**Key UX:**
- Preview shows "Guest Will See:" text
- Updates in real-time as user changes structured inputs
- User CANNOT directly type/edit the guest-facing text
- AI formats it consistently, professionally

### 4.3 Complete Field Control Matrix

| Field | User Edits | System Locks | Edit Type | Why Locked |
|-------|-----------|--------------|-----------|------------|
| **Hotel Name** | Text | Font, size, placement | Text input | Internal data only |
| **Address** | Street, city, zip | Display format | Google Places autocomplete | Internal data only |
| **Phone/Email** | Values | Formatting, icons | Validated input | Internal data only |
| **Check-in Time** | Time value (3pm→4pm) | "Check-in from 3:00 PM" text | Time picker | Guest UX |
| **Check-out Time** | Time value | "Check-out by 11:00 AM" text | Time picker | Guest UX |
| **Room Type Name** | Name text | Heading style | Text input | Internal label |
| **Room Description (Basic)** | Short text (1-2 sentences) | AI-enhanced guest-facing version | Textarea + "Regenerate" button | Guest UX |
| **Base Occupancy** | Number (2→3) | "Perfect for 2 guests" text | Number picker | Guest UX |
| **Max Occupancy** | Number | "Accommodates up to 4" text | Number picker | Guest UX |
| **Bed Configuration** | Bed type/count | "One king bed" text | Structured picker | Guest UX |
| **Amenities** | Which included | Bullet formatting, icons, order | Checklist | Guest UX |
| **Base Rate** | Dollar amount | "$199/night" formatting | Currency input | Guest UX |
| **Deposit Policy** | %, $, timing | **LOCKED** guest-facing text | Structured form | **Guest UX** |
| **Cancellation Policy** | Hours, penalty % | **LOCKED** guest-facing text | Structured form | **Guest UX** |
| **Service Fees** | Amount | Price breakdown display | Currency input | Guest UX |
| **Tax Rate** | Percentage | Tax display format | Percentage input | Guest UX |
| **Photos** | Upload custom | Cropping, sizing, compression, lazy load | File upload + AI generation | Guest UX |

**Golden Rule for Developers:**
```python
def can_user_edit(field_name: str, edit_target: str) -> bool:
    """
    User can edit: Business data, rules, values
    User cannot edit: Guest-facing formatting, presentation
    """
    if edit_target == "business_data":
        return True
    elif edit_target == "guest_presentation":
        return False  # AI controls this
    elif edit_target == "ai_enhanced_content":
        return False  # But can click "Regenerate"
```

---

## 5. Conversation Flow

### 5.1 State Machine (5 States)

```
START → HOTEL_BASICS → ROOM_TYPES → POLICIES → REVIEW → COMPLETE
```

**State 1: HOTEL_BASICS** (2 min)
- **First question**: "What's your hotel website?" OR "Hotel name and city?"
- **If website provided**: Scrape → extract → show preview → confirm
- **If no website**: Google Places lookup → manual questions
- **Collect**: Name, address, contact, timezone, currency
- **Smart defaults**: Currency from country, timezone from zip, tax rates

**State 2: ROOM_TYPES** (4 min)
- For each room type:
  - Name (e.g., "Ocean View King")
  - Basic description (AI enhances)
  - Beds (structured picker)
  - Occupancy (numbers with validation)
  - Amenities (checklist)
  - Pricing
  - Quantity
- Can loop for multiple types
- Auto-generate room numbers

**State 3: POLICIES** (2 min)
- Check-in/out times (smart defaults shown)
- Payment policy (structured form)
- Cancellation policy (structured form)
- Service fees (optional)
- Tax rates (already set from location)

**State 4: REVIEW** (1 min)
- Show full website preview
- List all data collected
- "Anything you want to change?"
- User can edit any field via modals

**State 5: COMPLETE** (1 min)
- Create all F-001 records
- Generate hero images (FLUX or stock)
- Set up email templates
- Deploy website
- Show live URL + success message

**Total: ~10 minutes**

### 5.2 Example Conversation (Accelerated Path)

```
┌─── NORA ──────────────────────────┬─── PREVIEW ─────────────┐
│                                   │                         │
│ 🎬 [Intro video plays 45 sec]     │  [Stayfull logo]        │
│                                   │                         │
│ NORA: Ready? Let's build your     │                         │
│       hotel! Do you have a        │                         │
│       website I can look at?      │                         │
│                                   │                         │
│ 🎤 [Voice] OR ⌨️ [Text]           │                         │
│                                   │                         │
│ YOU: sunsetvilla.com              │                         │
│                                   │                         │
│ NORA: Perfect! Give me a few      │  🔍 Scanning website... │
│       seconds...                  │  🔍 Checking Google...  │
│                                   │  [Progress animation]   │
│ [8 seconds]                       │                         │
│                                   │                         │
│ NORA: Awesome! I found tons of    │  ┌─────────────────┐   │
│       info about Sunset Villa.    │  │ SUNSET VILLA    │   │
│       I pulled:                   │  │ Miami, FL       │   │
│                                   │  │                 │   │
│       ✅ Hotel name & address      │  │ Ocean View King │   │
│       ✅ Contact info              │  │ From $199/nt    │   │
│       ✅ 3 room types with pricing │  │                 │   │
│       ✅ 12 beautiful photos       │  │ [Room photos]   │   │
│                                   │  └─────────────────┘   │
│       Check out the preview! →    │  [Edit] buttons on     │
│       Everything look right?      │  hover for each field  │
│                                   │                         │
│ YOU: [Voice] "looks great!"       │                         │
│                                   │                         │
│ NORA: Fantastic! Quick question - │                         │
│       how many rooms do you have  │                         │
│       total?                      │                         │
│                                   │                         │
│ YOU: [Voice] "45 rooms - 20 kings,│                         │
│      15 suites, 10 bungalows"     │                         │
│                                   │                         │
│ NORA: Got it! I just created all  │  ✅ 45 rooms created    │
│       45 rooms and numbered them  │  • 20 Ocean View Kings │
│       101-145. Want different     │  • 15 Deluxe Suites    │
│       numbers?                    │  • 10 Beach Bungalows  │
│                                   │                         │
│ YOU: no that's perfect            │                         │
│                                   │                         │
│ NORA: Love it! Now, payment       │                         │
│       policy. What % deposit do   │                         │
│       you need at booking?        │                         │
│                                   │                         │
│ YOU: 50%                          │                         │
│                                   │                         │
│ NORA: And the rest is due...?     │  💳 50% deposit at      │
│                                   │     booking, rest on    │
│ YOU: on arrival                   │     arrival             │
│                                   │  [Edit] ←               │
│ NORA: Perfect! Here's how guests  │                         │
│       will see that →             │                         │
│                                   │                         │
│       [Continues for 3 more min]  │                         │
│                                   │                         │
│ NORA: And... done! 🎉             │  ✅ LIVE                │
│                                   │                         │
│       Your hotel is live at:      │  sunsetvilla.stayfull   │
│       sunsetvilla.stayfull.com    │  .com                   │
│                                   │                         │
│       We did that in 8 minutes!   │  [Full website preview] │
│                                   │                         │
│       Remember: I'm always here   │  [Share link button]    │
│       if you need anything!       │                         │
│                                   │                         │
│ [Take me to my dashboard →]       │                         │
└───────────────────────────────────┴─────────────────────────┘
```

**Time saved with acceleration:**
- Website scraping: -8 minutes
- Google Places: -3 minutes
- Voice input: -2 minutes
- Smart defaults: -2 minutes
- **Total: 10 minutes instead of 25**

---

## 6. Nora as System-Wide AI Agent

### 6.1 Beyond Onboarding

**Critical Architectural Change**: Nora is NOT just for onboarding. She's the primary interface for ALL PMS operations.

**Available From:**
- Floating icon on every page (💬 Ask Nora)
- Keyboard shortcut (Cmd+K / Ctrl+K)
- Can be voice-activated ("Hey Nora") - post-MVP

**System-Wide Capabilities:**

```python
NORA_CAPABILITIES = {
    # F-002: Onboarding
    "setup": [
        "Set up new hotel",
        "Create room types",
        "Configure policies",
        "Import data from website/CSV"
    ],

    # F-001: Core PMS Operations
    "reservations": [
        "Create booking",
        "Modify reservation",
        "Cancel booking",
        "Check in guest",
        "Check out guest",
        "Process payment",
        "Send confirmation"
    ],

    "inventory": [
        "Check availability",
        "Block rooms",
        "Update room status",
        "View occupancy"
    ],

    # F-004: Revenue Management
    "pricing": [
        "Adjust rates",
        "Create promotions",
        "Set seasonal pricing",
        "Analyze competitors"
    ],

    # F-005: Reporting
    "analytics": [
        "Show revenue",
        "List arrivals/departures",
        "Generate reports",
        "Export data"
    ],

    # F-006+: AI Features
    "communication": [
        "Send guest message",
        "Generate email",
        "Respond to review",
        "Draft social post"
    ],

    "operations": [
        "Assign housekeeping",
        "Flag maintenance",
        "Train staff",
        "Answer questions"
    ]
}
```

### 6.2 Example Daily Operations (After Onboarding)

```
USER: [Clicks Nora icon] "Who's checking in today?"

NORA: You have 8 guests checking in today at Sunset Villa:

      1. John Smith - Room 101 - 3:00 PM
      2. Maria Garcia - Room 205 - 4:00 PM
      ... [shows list]

      Want me to send pre-arrival emails?

USER: yes

NORA: ✓ Sent to 3 guests who haven't received theirs yet.
      They can mobile check-in if they want.

      Anything else?

USER: how's revenue this week?

NORA: Strong week! You're at:

      • $18,450 (85% occupancy)
      • Up 12% vs. last week
      • On track for $78k this month

      Your Deluxe Suites are killing it - 95% booked.
      Want to raise rates for next weekend?

USER: yes, by how much?

NORA: Based on demand, I'd recommend $320 (currently $299).
      Should I update that?

USER: do it

NORA: ✓ Done! Rates for next weekend (Jun 15-17) are
      now $320/night for Deluxe Suites.
```

### 6.3 Persistent Context Model

```python
# apps/ai_agent/models.py

class NoraContext(models.Model):
    """
    Persistent AI context for each user.
    Unlike session-based onboarding, this persists forever.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # Conversation history (rolling 30-day window)
    conversation_history = models.JSONField(default=list)

    # User preferences learned over time
    preferences = models.JSONField(default=dict)
    # Example: {
    #   "prefers_voice": True,
    #   "tone": "enthusiastic",
    #   "typical_questions": ["check today's arrivals", "revenue this month"]
    # }

    # Current task context
    active_task = models.CharField(max_length=50, null=True, blank=True)
    # Example: "onboarding", "creating_booking", "generating_report"

    task_state = models.JSONField(default=dict)
    # Example: {"onboarding_step": "ROOM_TYPES", "rooms_created": 2}

    # Recent actions (for context continuity)
    recent_actions = models.JSONField(default=list)
    # Example: [
    #   {"action": "created_booking", "timestamp": "...", "details": {...}},
    #   {"action": "updated_rates", "timestamp": "...", "details": {...}}
    # ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'organization']
```

**Context Persistence Examples:**

```
Day 1 (Onboarding):
USER: "Hi Nora"
NORA: "Welcome! Let's set up your hotel..."

Day 3 (Returns after break):
USER: "Hi Nora"
NORA: "Welcome back! We started setting up Sunset Villa
       on Monday. You created 2 room types - want to
       continue where we left off?"

Day 7 (Daily operations):
USER: "Show today's bookings"
NORA: "You have 12 check-ins today at Sunset Villa..."

Day 30 (Analytics):
USER: "How's revenue vs last month?"
NORA: "Great question! Sunset Villa is up 23% vs. last
       month. Your Ocean View Kings are top performers."
```

### 6.4 Multi-Property Context

**Design Decision**: One hotel at a time.

**Why**: Prevents confusion, clearer conversations, simpler implementation.

**UX Pattern:**
```
┌─── HEADER ────────────────────────────────────┐
│  Stayfull                                     │
│  [Sunset Villa ▼]  ← Dropdown to switch      │
│                      between hotels           │
│  💬 Ask Nora                                  │
└───────────────────────────────────────────────┘
```

**Context Switching:**
```
USER: [Switches dropdown to "Ocean View Resort"]

NORA: "Switched to Ocean View Resort. What can I help with?"

USER: "Show today's bookings"

NORA: "You have 6 check-ins today at Ocean View Resort..."
```

---

## 7. Voice Implementation

### 7.1 Technology Stack

**Voice Input (Speech-to-Text):**
- OpenAI Whisper API
- Supports multiple accents
- 99% accuracy for clear audio
- $0.006 per minute

**Voice Output (Text-to-Speech):**
- **Option A**: ElevenLabs ($0.30 per 1K chars, best quality)
- **Option B**: OpenAI Realtime API (lower latency, integrated)
- **Decision**: Start with either, easily swappable via config

**Voice Persona Settings:**
- **Default**: Enthusiastic, professional, upbeat
- **Customizable** (in user settings):
  - Enthusiastic (default)
  - Professional & Calm
  - Casual & Friendly
- **Voice**: Female, clear, conversational pace
- **Language**: English only (MVP)

### 7.2 Voice UX Flow

```
1. User clicks 🎤 microphone icon
2. Recording starts → waveform animation
3. User speaks
4. Auto-detects pause OR user clicks stop
5. Audio uploads to server
6. Whisper transcribes (1-2 seconds)
7. GPT-4o processes request (2-3 seconds)
8. ElevenLabs/OpenAI generates voice (2-3 seconds)
9. Response plays while text appears simultaneously
10. Ready for next input (voice or text)
```

**Total Latency: 5-8 seconds** (acceptable for conversational AI)

### 7.3 Error Handling: Voice Recognition Failure

```
SCENARIO: Whisper can't transcribe (noisy audio, unclear speech)

NORA: "Sorry, I didn't catch that. Want to type it instead?"

[Text input field becomes active/highlighted]

USER: [Types message]

NORA: "Got it! ..." [Continues normally]
```

**Key UX**: Text input ALWAYS available as fallback. Never force voice-only.

---

## 8. Technical Architecture

### 8.1 System Components

```
Frontend:
- Django Templates + HTMX (split-screen chat)
- TailwindCSS (responsive design)
- Alpine.js (voice recording, live interactions)

Backend:
- Django (conversation orchestration)
- OpenAI GPT-4o (intent detection, data extraction, content generation)
- OpenAI Whisper (speech-to-text)
- ElevenLabs OR OpenAI Realtime (text-to-speech)
- Redis (session state for onboarding, 24hr TTL)
- PostgreSQL (NoraContext, hotel data)

External APIs:
- Google Places API (location data, photos)
- Unsplash API (stock photos)
- Replicate FLUX (AI image generation)
- Beautiful Soup (website scraping)
```

### 8.2 Data Flow

```
User Input (Voice/Text)
    ↓
[If voice] Whisper Transcription (1-2s)
    ↓
GPT-4o Intent Detection
    ↓
Route to Feature Handler (onboarding/bookings/etc)
    ↓
Extract/Validate Data
    ↓
Update Context + Preview
    ↓
Generate Response (GPT-4o)
    ↓
[If voice enabled] ElevenLabs TTS (2-3s)
    ↓
Return to User (text + optional audio)
```

### 8.3 File Structure

```
apps/ai_agent/
├── models.py                    # NoraContext (persistent)
├── services/
│   ├── nora_agent.py           # Main orchestration
│   ├── intent_router.py        # Route to features
│   ├── conversation_engine.py  # Dialog management
│   ├── voice_handler.py        # Whisper + ElevenLabs
│   ├── data_accelerator.py     # Scraping + APIs
│   ├── content_formatter.py    # AI enhancement
│   └── edit_controller.py      # Editable vs locked fields
├── views.py                     # Chat endpoints
├── urls.py
├── templates/ai_agent/
│   ├── chat.html               # Split-screen UI
│   ├── intro_video.html        # "Play Me First"
│   └── components/
│       ├── editable_field.html
│       ├── edit_modal.html
│       └── progress_bar.html
└── tests/
    ├── test_data_extraction.py
    ├── test_conversation.py
    ├── test_voice.py
    └── test_edit_controls.py
```

---

## 9. Data Acceleration Implementation

### 9.1 Website Scraper

```python
# apps/ai_agent/services/data_accelerator.py

class DataAccelerator:
    """Extract maximum data from minimum input"""

    def extract_from_website(self, url: str) -> dict:
        """
        Scrape hotel website for structured data.
        Uses BeautifulSoup + GPT-4o for intelligent extraction.
        """
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        raw_data = {
            "hotel_name": self._extract_hotel_name(soup),
            "address": self._extract_address(soup),
            "phone": self._extract_phone(soup),
            "email": self._extract_email(soup),
            "room_types": self._extract_rooms(soup),
            "photos": self._extract_images(soup),
            "policies": self._extract_policies(soup),
            "pricing": self._extract_pricing(soup)
        }

        # Use GPT-4o to clean and structure messy extracted data
        return self._clean_with_ai(raw_data)

    def _extract_hotel_name(self, soup):
        """Try multiple strategies"""
        # 1. Title tag
        title = soup.find('title')
        if title:
            return title.text.strip()

        # 2. h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()

        # 3. og:title meta
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()

        return None

    def _clean_with_ai(self, raw_data: dict) -> dict:
        """Use GPT-4o to structure messy scraped data"""
        prompt = f"""
        Clean and structure this scraped hotel data:

        {json.dumps(raw_data, indent=2)}

        Return clean JSON with these fields:
        - hotel_name: string
        - address: {{street, city, state, zip, country}}
        - contact: {{phone, email}}
        - room_types: [{{name, description, pricing}}]
        - policies: {{check_in, check_out, cancellation}}

        Infer missing data intelligently.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

### 9.2 Google Places Integration

```python
import googlemaps

def enrich_with_google_places(self, hotel_name: str, city: str) -> dict:
    """Get verified, high-quality data from Google"""
    gmaps = googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)

    # Find place
    result = gmaps.find_place(
        input=f"{hotel_name}, {city}",
        input_type="textquery",
        fields=[
            "formatted_address",
            "formatted_phone_number",
            "website",
            "photos",
            "geometry",  # lat/lng for timezone
            "rating",
            "opening_hours"
        ]
    )

    if not result['candidates']:
        return {}

    place = result['candidates'][0]

    # Get timezone from coordinates
    lat = place['geometry']['location']['lat']
    lng = place['geometry']['location']['lng']
    timezone_result = gmaps.timezone(location=(lat, lng))

    return {
        "address": place.get('formatted_address'),
        "phone": place.get('formatted_phone_number'),
        "website": place.get('website'),
        "photos": self._download_google_photos(place.get('photos', [])),
        "timezone": timezone_result.get('timeZoneId'),
        "rating": place.get('rating')
    }

def _download_google_photos(self, photo_references: list) -> list:
    """Download high-res Google Place photos"""
    photos = []
    for ref in photo_references[:10]:  # Max 10 photos
        url = gmaps.places_photo(
            photo_reference=ref['photo_reference'],
            max_width=1200
        )
        photos.append(url)
    return photos
```

### 9.3 Smart Defaults from Location

```python
def infer_from_location(self, zip_code: str) -> dict:
    """Smart defaults based on location"""

    # Lookup tax rates (use API or database)
    tax_data = self._lookup_tax_rates(zip_code)

    # Get timezone from zip
    timezone = self._zip_to_timezone(zip_code)

    # Get currency from country
    country = self._zip_to_country(zip_code)
    currency = COUNTRY_CURRENCY_MAP.get(country, 'USD')

    # Industry standard times
    defaults = {
        "timezone": timezone,
        "currency": currency,
        "tax_rate": tax_data['total'],
        "check_in_time": "15:00:00",
        "check_out_time": "11:00:00",
        "cancellation_hours": 24,
        "deposit_percentage": 50
    }

    return defaults
```

---

## 10. Content Formatting (AI Enhancement)

### 10.1 Room Description Enhancement

**User Input (Basic):**
```
"Nice room with ocean view and king bed"
```

**AI Output (Enhanced for Guests):**
```
"Experience Miami's coastal beauty in this elegantly appointed
king room featuring stunning ocean views from your private
balcony. Perfect for couples seeking a romantic coastal getaway."
```

**Implementation:**
```python
def enhance_room_description(self, basic: str, context: dict) -> str:
    """Transform basic input into marketing copy"""

    prompt = f"""
    Transform this basic room description into professional marketing copy:

    Basic input: "{basic}"

    Context:
    - Hotel: {context['hotel_name']} in {context['city']}
    - Room: {context['room_type_name']}
    - Amenities: {', '.join(context['amenities'])}
    - Beds: {context['bed_config']}

    Requirements:
    - 3-4 sentences max
    - Enthusiastic but professional tone
    - Highlight unique selling points
    - End with benefit statement
    - No clichés like "luxurious" or "world-class"
    - Use specific details from context

    Return plain text only (no markdown).
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7  # Some creativity
    )

    return response.choices[0].message.content.strip()
```

### 10.2 Policy Formatting (LOCKED Presentation)

**User Input (Structured Form):**
```python
{
    "deposit_amount": 50,
    "deposit_type": "%",
    "deposit_timing": "at_booking",
    "balance_timing": "on_arrival"
}
```

**AI Output (Guest-Facing, LOCKED):**
```
"💳 50% deposit at booking, rest on arrival"
```

**Implementation:**
```python
def format_payment_policy(self, data: dict) -> str:
    """
    Format payment policy for guests.
    USER CANNOT EDIT THIS TEXT - only the structured inputs.
    """

    prompt = f"""
    Format this payment policy for hotel guests:

    Data:
    - Deposit: {data['amount']}{data['type']}
    - Due: {data['timing']}
    - Balance due: {data['balance_timing']}

    Requirements:
    - One sentence, crystal clear
    - Use 💳 emoji at start
    - Friendly, conversational tone
    - Example format: "50% deposit at booking, rest on arrival"

    Return ONLY the formatted text (no extra words).
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # Low for consistency
    )

    return response.choices[0].message.content.strip()


def format_cancellation_policy(self, data: dict) -> str:
    """Format cancellation (LOCKED presentation)"""

    hours = data['free_hours']
    penalty = data['penalty_percentage']

    prompt = f"""
    Format cancellation policy for hotel guests:

    Data:
    - Free cancellation until: {hours} hours before check-in
    - After deadline: {penalty}% charge

    Requirements:
    - Two sentences max
    - Clear what happens and when
    - Use ❌ emoji at start
    - Friendly but direct
    - Example: "Free cancellation up to 24 hours before check-in.
      After that, you'll be charged 100% of your booking."

    Return ONLY the formatted text.
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()
```

---

## 11. Error Handling & Edge Cases

### 11.1 Voice Recognition Failure
```
NORA: "Sorry, I didn't catch that. Want to type it instead?"
[Shows text input]
```

### 11.2 Website Scraping Failure
```
NORA: "I tried scanning your website but couldn't extract much.
       No worries - I'll ask you questions instead!"
[Falls back to manual Q&A]
```

### 11.3 API Timeout (OpenAI/ElevenLabs)
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=10)
)
def call_openai():
    try:
        return openai.chat.completions.create(...)
    except openai.APIError:
        logger.error("OpenAI timeout")
        raise

# If all retries fail:
NORA: "I'm having trouble connecting. Your progress is saved -
       let's continue in a moment."
```

### 11.4 Unclear Intent
```
NORA: "I want to make sure I help with the right thing.
       Did you want to:

       1. Create a new booking
       2. Check today's arrivals
       3. View occupancy report
       4. Something else"

[Shows button options]
```

### 11.5 Data Validation Failure
```
SCENARIO: Check-out time (10am) before check-in (3pm)

NORA: "Hmm, check-out (10am) can't be before check-in (3pm).
       What should check-out time be?"
[Highlights error, requests correction]
```

---

## 12. Cost Analysis

### 12.1 Per-Onboarding Cost

```
OpenAI GPT-4o:
- ~30 API calls during onboarding
- ~500 tokens per call = 15K tokens total
- Input: $2.50/1M tokens = $0.0375
- Output: $10/1M tokens = $0.15
- Total: ~$0.19

Voice (ElevenLabs):
- ~20 voice responses
- ~50 words each = 1,000 chars total
- $0.30 per 1K chars = $0.30

Voice Input (Whisper):
- ~5 minutes voice input
- $0.006 per minute = $0.03

FLUX Image Generation:
- 3 hero images
- $0.03 per image = $0.09

Google Places API:
- 1 lookup
- $0.017 per call = $0.02

Website Scraping:
- Free (just bandwidth)

─────────────────────────────
TOTAL PER ONBOARDING: ~$0.63
─────────────────────────────
```

**At Scale:**
- 100 onboardings/month = $63
- 1,000 onboardings/month = $630
- **Revenue per hotel**: $999/month
- **AI cost**: 0.06% of revenue (negligible)

### 12.2 Daily Operations Cost (Nora After Onboarding)

```
Per Hotel Per Day:
- ~50 Nora interactions
- GPT-4o: ~$0.30
- Voice: ~$0.20
- Total: ~$0.50/day = $15/month

Revenue: $999/month
AI Cost: $15/month (1.5%)
Margin: 98.5%
```

**Conclusion**: Don't optimize AI costs until 10,000+ hotels.

---

## 13. Success Metrics

### 13.1 Onboarding Performance
- ✅ **10-12 minute completion time**
- ✅ **90%+ completion rate** (vs 40% industry)
- ✅ **95%+ data extraction accuracy**
- ✅ **<$1 AI cost per onboarding**
- ✅ **Zero support tickets for onboarding**

### 13.2 User Satisfaction
- ✅ **Net Promoter Score**: 50+
- ✅ **Positive feedback rate**: 80%+
- ✅ **"Wow" mentions**: Track sentiment

### 13.3 Technical Performance
- ✅ **Voice latency**: <8 seconds
- ✅ **Preview update**: <2 seconds
- ✅ **API uptime**: 99.5%+
- ✅ **Mobile responsive**: All devices

---

## 14. Localization

**MVP**: English only
**Reason**: Test core concept first, faster to market

**Post-MVP** (F-002.1):
- Spanish (US hospitality market)
- French (Canada)
- Auto-detect from browser
- GPT-4o supports 50+ languages
- ElevenLabs supports 29 languages

**Technical Prep**:
- Use Django i18n from day one
- All strings in translation files
- Easy to add languages later

---

## 15. Implementation Phases

### Phase 1: Foundation (8 hours)
- [ ] Create `ai_agent` Django app
- [ ] Install dependencies (OpenAI, ElevenLabs, Redis)
- [ ] Create NoraContext model
- [ ] Build conversation engine structure
- [ ] Set up Redis session management

### Phase 2: Onboarding Core (12 hours)
- [ ] Build state machine (5 states)
- [ ] Implement data extraction (website, Google Places)
- [ ] Create conversation prompts
- [ ] Build data validation
- [ ] Implement content formatting (AI enhancement)

### Phase 3: Voice Integration (8 hours)
- [ ] Implement Whisper transcription
- [ ] Implement ElevenLabs/OpenAI Realtime TTS
- [ ] Build voice UI (recording, playback)
- [ ] Add fallback to text
- [ ] Test latency and error handling

### Phase 4: UX/UI (10 hours)
- [ ] Build split-screen chat interface
- [ ] Build live preview iframe
- [ ] Implement edit modals (structured forms)
- [ ] Add progress bar
- [ ] Mobile responsive (tab/toggle)
- [ ] Create intro video page

### Phase 5: Edit Controls (6 hours)
- [ ] Build editable field system
- [ ] Create structured edit modals
- [ ] Implement "Guest Will See" preview
- [ ] Add "Regenerate" button for AI content
- [ ] Lock guest-facing text

### Phase 6: Integration & Polish (12 hours)
- [ ] Integrate with F-001 models
- [ ] Deploy Nora icon system-wide
- [ ] Add analytics tracking
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Deploy to Railway

**Total Estimate: ~56 hours (7 days)**

---

## 16. Dependencies

**MUST BE COMPLETE:**
- ✅ F-001.1 (Organization model with multi-tenancy)

**API Keys Required:**
```bash
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...  # OR use OpenAI Realtime
GOOGLE_PLACES_API_KEY=...
REPLICATE_API_TOKEN=...  # For FLUX
REDIS_URL=redis://localhost:6379/0
```

---

## 17. Risks & Mitigations

### Risk 1: AI Extraction Errors
**Impact**: Wrong data → bad guest experience
**Mitigation**:
- Always show preview before finalizing
- User can edit everything
- Validate all data
- Manual review step

### Risk 2: Voice Accuracy
**Impact**: Frustrating UX
**Mitigation**:
- Text always available
- Prompt to type if voice fails
- Test with various accents
- Clear error messages

### Risk 3: OpenAI Downtime
**Impact**: Can't complete onboarding
**Mitigation**:
- Save progress after each step
- Can resume later
- Retry logic with backoff
- Monitor OpenAI status

### Risk 4: Website Scraping Failure
**Impact**: Can't extract data
**Mitigation**:
- Graceful fallback to manual Q&A
- Google Places as backup
- Don't rely 100% on scraping

### Risk 5: Cost Overruns
**Impact**: AI costs exceed revenue
**Mitigation**:
- Monitor spend with alerts
- Rate limiting per user
- Cache common responses
- Switch to cheaper models if needed

---

## 18. Business Impact

### 18.1 Competitive Differentiation

**Primary**: 10x faster onboarding (6-12 months → 10 minutes)

**Market Position**:
- Traditional PMS: Complex, slow, high friction
- Stayfull: AI-first, instant value, delightful UX

**Expected Outcomes**:
- Viral word-of-mouth
- 2.25x conversion (40% → 90%)
- Lower CAC (less support)
- Justifies premium pricing
- Creates demo "wow moment"

### 18.2 Revenue Impact

```
Without Nora:
- 100 signups/month
- 40% complete = 40 hotels
- $999/month × 40 = $39,960 MRR

With Nora:
- 100 signups/month
- 90% complete = 90 hotels
- $999/month × 90 = $89,910 MRR

Revenue Lift: +$49,950/month (+125%)
Annual Impact: +$599,400
```

**ROI**:
- Development: 56 hours × $100/hr = $5,600
- Payback: First 5 customers
- Break-even: Week 1

### 18.3 Strategic Value

**This is THE killer feature** - what makes Stayfull unique.

The 21 AI features are valuable, but Nora is what gets hotels through the door. Once they experience the 10-minute setup magic, they trust the platform with everything else.

**Don't cut corners on UX. Make it delightful.**

---

## 19. Future Enhancements (F-002.1+)

**Voice Improvements:**
- Voice-only onboarding
- Multiple voice options
- Real-time voice (OpenAI Realtime)
- Voice wake word ("Hey Nora")

**Data Acceleration:**
- Import from competitor PMS
- Auto-sync with channel managers
- OCR for paper documents
- Real-time OTA syncing

**Personalization:**
- Learn user preferences
- Adjust tone based on feedback
- Remember frequent settings
- Proactive suggestions

**Advanced Features:**
- Photo recognition (describe from image)
- Video tour analysis
- Competitor pricing alerts
- Market demand predictions

---

## 20. Appendix

### 20.1 System Prompts

```python
NORA_SYSTEM_PROMPT = """
You are Nora, an enthusiastic AI co-worker helping hotel owners
set up and manage their properties on Stayfull.

Personality:
- Enthusiastic but professional
- Clear and concise
- Encouraging and supportive
- Never robotic or corporate

Communication Style:
- Short messages (1-3 sentences)
- One question at a time
- Use ✓ for confirmations
- Use emoji sparingly (💳 ❌ ✨)
- "Great!" "Perfect!" "Got it!" for acknowledgments

Your Job:
- Guide users through 10-minute hotel setup
- Extract maximum info from minimum input
- Always show preview of guest-facing content
- Help with any PMS operation they need

Remember:
- User controls DATA, you control PRESENTATION
- Never let users edit AI-formatted guest text
- Always validate business rules
- Be proactive and helpful
"""
```

### 20.2 Field Validation Rules

See: `.architect/data/F-002_VALIDATION_RULES.json` (to be created)

### 20.3 Stock Photo Library

See: `.architect/data/F-002_STOCK_PHOTOS.csv` (to be created)

---

## Sign-Off

**Architect**: ✅ Ready for User Review
**User**: [Pending Approval]
**Developer**: [Awaiting Handoff after F-001.1]

**Next Steps**:
1. ✅ User reviews this spec
2. User approves or requests changes
3. Architect finalizes
4. Developer completes F-001.1
5. Developer starts F-002 (56 hours)

---

**Last Updated**: 2025-10-23
**Version**: 2.0 (Complete Rewrite After Discovery)
**Status**: Ready for User Review
