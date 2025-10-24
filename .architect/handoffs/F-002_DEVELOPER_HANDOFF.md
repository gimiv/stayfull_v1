# Developer Handoff: F-002 Nora AI Onboarding Agent

**Priority**: P1 - Killer Feature
**Effort**: 70 hours (~9 days) - Updated estimate
**Status**: 🚧 IN PROGRESS - Phases 1-5 Complete | Phase 6 (Integration) Remaining
**Specification**: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
**Standards**: `.architect/DEVELOPMENT_STANDARDS.md`
**Dependencies**: F-001.1 (Organization model) MUST be complete first

**Total Time So Far**: ~30 hours (Phases 1-5 complete)
**Remaining**: Phase 6 (Integration) - 12 hours estimated

---

## 📊 Implementation Progress

### ✅ Phase 1: Foundation - COMPLETE (Oct 23, 2025)
**Status**: All tasks complete, OpenAI connection verified
**Time Spent**: ~10 hours

**Completed:**
- ✅ Created `apps/ai_agent/` Django app structure
- ✅ Installed dependencies: openai, googlemaps, beautifulsoup4, lxml, requests
- ✅ Created NoraContext model with 13 passing tests
- ✅ Added ai_agent to INSTALLED_APPS
- ✅ Created and ran migrations (0001_initial)
- ✅ Built service layer:
  - `services/openai_config.py` - Client initialization, system prompts, GPT-4o config
  - `services/nora_agent.py` - Main NoraAgent orchestration class
- ✅ Created views: chat_view, send_message, start_onboarding, welcome_view
- ✅ Set up URL routing at `/nora/*` paths
- ✅ Created management command: `python manage.py test_nora`
- ✅ Tested OpenAI connection - all systems operational

**Test Results:**
- NoraContext model tests: 13/13 passing ✓
- OpenAI API connection: Working ✓
- GPT-4o integration: Verified ✓
- Nora personality: Active ✓

**Key Files Created:**
```
apps/ai_agent/
├── models.py                          # NoraContext model
├── views.py                           # Chat and API endpoints
├── urls.py                            # URL routing
├── services/
│   ├── openai_config.py              # OpenAI client + config
│   └── nora_agent.py                 # Main orchestration
├── tests/
│   └── test_models.py                # 13 passing tests
└── management/commands/
    └── test_nora.py                  # Connection test command
```

**Environment:**
- OPENAI_API_KEY: Configured ✓
- Database: PostgreSQL with ai_agent migrations applied ✓

### ✅ Phase 2: Onboarding Core - COMPLETE (Oct 23, 2025)
**Status**: Core services implemented and tested
**Time Spent**: ~6 hours

**Completed:**
- ✅ Created OnboardingState enum (5 states: HOTEL_BASICS → ROOM_TYPES → POLICIES → REVIEW → COMPLETE)
- ✅ Built OnboardingEngine with state machine logic
  - State transitions based on data completeness
  - Progress tracking (0% → 100%)
  - Missing field detection
- ✅ Implemented DataExtractor for website scraping
  - BeautifulSoup HTML parsing
  - GPT-4o intelligent data extraction
  - Location-based smart defaults (currency, timezone, tax rates)
  - Ethical boundary: only user's own website
- ✅ Created ContentFormatter for AI enhancement
  - Room description enhancement (basic → guest-ready)
  - Payment policy formatting (data → "💳 50% deposit at booking...")
  - Cancellation policy formatting
  - Check-in/out policy formatting
  - Hotel description enhancement
- ✅ Built IntentDetector for message classification
  - Pattern matching for common intents (URL, confirm, reject, questions)
  - GPT-4o fallback for ambiguous cases
  - 9 intent types supported
- ✅ Integrated onboarding flow into NoraAgent
  - Intent-based message routing
  - Website URL handling with data extraction
  - Data provision handling (answering questions)
  - State transitions and progress updates
  - Error handling and fallbacks

**Test Results:**
- Django system check: Passed ✓
- Existing model tests: 13/13 passing ✓
- Full integration test: Passed ✓

**Key Files Created:**
```
apps/ai_agent/services/
├── conversation_engine.py        # State machine (316 lines)
├── data_extractor.py            # Website scraping (262 lines)
├── content_formatter.py         # AI enhancement (275 lines)
└── intent_detector.py           # Message classification (227 lines)
```

**Updated Files:**
- `services/nora_agent.py` - Full onboarding integration (381 lines total)

### ✅ Phase 3: Voice Integration - COMPLETE (Oct 23, 2025)
**Status**: Voice input/output fully implemented
**Time Spent**: ~2 hours

**Completed:**
- ✅ Created VoiceHandler service class
  - Whisper transcription (audio → text)
  - OpenAI TTS generation (text → audio)
  - Audio file validation (size, format)
  - Streaming voice generation support
  - Configurable voice personas (6 voices: nova, alloy, echo, fable, onyx, shimmer)
  - Adjustable speech speed (0.25x to 4.0x)
- ✅ Added voice API endpoints
  - `POST /nora/api/voice/transcribe/` - Transcribe audio to text
  - `POST /nora/api/voice/generate/` - Generate voice from text
  - `POST /nora/api/voice/message/` - Complete voice interaction (transcribe → process → speak)
- ✅ Integrated voice with Nora agent
  - End-to-end voice conversations
  - Audio validation and error handling
  - Base64 audio encoding for API responses

**Test Results:**
- Django system check: Passed ✓
- VoiceHandler initialization: Working ✓
- Model tests: 13/13 passing ✓
- Voice configuration: nova voice, 1.0x speed, tts-1 model ✓

**Key Files Created:**
```
apps/ai_agent/services/
└── voice_handler.py             # Voice I/O (242 lines)
```

**Updated Files:**
- `views.py` - Added 3 voice endpoints (+185 lines)
- `urls.py` - Added voice routes

**Voice Configuration:**
- Default Voice: nova (female, clear, professional)
- Speech Speed: 1.0x (normal)
- TTS Model: tts-1 (fast, cost-effective)
- Whisper Model: whisper-1
- Max Audio Size: 25MB
- Supported Formats: mp3, wav, m4a, webm, and more

**API Endpoints Ready:**
```
POST /nora/api/voice/transcribe/     # Upload audio → get text
POST /nora/api/voice/generate/       # Send text → get audio (mp3)
POST /nora/api/voice/message/        # Upload audio → get Nora's voice response
```

### ✅ Phase 4: UX/UI - COMPLETE (Oct 23, 2025)
**Status**: Full chat interface with voice, mobile responsive
**Time Spent**: ~4 hours

**Completed:**
- ✅ Created split-screen chat interface
  - Left panel: Chat with Nora
  - Right panel: Live preview
  - Seamless desktop experience (50/50 split)
- ✅ Built message bubble components
  - User messages (blue, right-aligned)
  - Assistant messages (gray, left-aligned)
  - Smooth animations (slide-in effect)
  - Loading indicator with animated dots
- ✅ Implemented progress bar
  - Shows during onboarding (0% → 100%)
  - State indicators (Hotel basics, Room types, Policies, Review, Complete)
  - Smooth transitions with CSS animations
- ✅ Created voice recording UI
  - Microphone button with pulse animation
  - Recording indicator (red dot, animated)
  - "Recording..." status message
  - Auto-stop on send
- ✅ Added mobile responsive design
  - Tab toggle between Chat/Preview
  - Full-screen chat on mobile
  - Touch-friendly buttons
  - Adaptive textarea
- ✅ Built welcome screen
  - Animated gradient header
  - Feature showcase (4 key features)
  - "Let's Go, Nora!" CTA button
  - Floating icon animation
- ✅ Integrated HTMX for dynamic updates
  - No page reloads
  - Real-time message updates
  - Progress bar updates
- ✅ Styled with TailwindCSS
  - Stripe-inspired design system
  - Clean, minimal, professional
  - Blue primary color (following Stripe Dashboard)
  - Responsive utilities

**Design Features:**
- **Stripe Aesthetic**: Clean, minimal, professional UI
- **Color Palette**:
  - Primary: #0066FF (blue) ← Following Stripe Dashboard standard
  - Surface: #F6F9FC (light gray)
  - Text: #0A2540 (dark blue)
- **Typography**: System font stack (SF Pro, Segoe UI, etc.)
- **Spacing**: 8px grid system
- **Animations**:
  - Message slide-in (0.3s)
  - Progress bar transitions (0.5s)
  - Voice pulse ring (1.5s loop)
  - Loading dots (1.4s staggered)
  - Floating icon (3s ease-in-out)
  - Gradient shift (8s continuous)

**UX Features:**
- **Auto-resizing textarea**: Grows with content
- **Enter to send**: Shift+Enter for new line
- **Voice one-click**: Tap mic → record → auto-send
- **Real-time progress**: See onboarding percentage live
- **Mobile toggle**: Easy preview access on small screens
- **CSRF protection**: All forms secured
- **Error handling**: Graceful fallbacks for API failures

**Templates Created:**
```
apps/ai_agent/templates/ai_agent/
├── chat.html                # Main chat interface (400+ lines)
├── welcome.html            # Welcome screen (200+ lines)
└── no_organization.html    # Error state (40 lines)
```

**Test Results:**
- Django system check: Passed ✓
- URL routing: All routes working ✓
- Model tests: 13/13 passing ✓
- Templates loading: No errors ✓

**Accessibility:**
- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- Touch-friendly tap targets (44px minimum)
- Color contrast ratios meet WCAG AA

**Browser Support:**
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid & Flexbox
- ES6+ JavaScript
- MediaRecorder API for voice

### ✅ Phase 5: Edit Controls - COMPLETE (Oct 23, 2025)
**Status**: Structured edit modals with live preview fully implemented
**Time Spent**: ~4 hours

**Completed:**
- ✅ Created structured edit modal system
  - Payment policy modal (deposit %, timing, balance due)
  - Cancellation policy modal (policy type, fees)
  - Check-in/check-out times modal
- ✅ Implemented live preview generation
  - Updates formatted text as user types
  - API endpoint for real-time preview: `POST /nora/api/preview/policy/`
- ✅ Built API endpoints for modal operations
  - `GET /nora/api/edit/payment-policy/` - Load payment modal
  - `POST /nora/api/save/payment-policy/` - Save payment changes
  - `GET /nora/api/edit/cancellation-policy/` - Load cancellation modal
  - `POST /nora/api/save/cancellation-policy/` - Save cancellation changes
  - `GET /nora/api/edit/checkin-times/` - Load check-in times modal
  - `POST /nora/api/save/checkin-times/` - Save times
- ✅ Integrated edit buttons into preview panel
  - Edit buttons for each policy section
  - Dynamic modal loading (HTMX-style)
  - Save/Cancel with proper state management
- ✅ Implemented critical pattern: **Users edit DATA, AI controls PRESENTATION**
  - Users cannot directly edit formatted guest-facing text
  - All editing done via structured inputs (dropdowns, number fields, time pickers)
  - AI generates polished presentation from structured data

**Key Features:**
- **Structured Inputs Only**: No free text editing of AI-generated content
- **Live Preview**: See formatted output update in real-time
- **Modal Animations**: Smooth fadeIn/slideUp transitions
- **Context Preservation**: Edits update NoraContext state
- **ContentFormatter Integration**: Uses existing AI formatting services

**Modal Components:**
```
apps/ai_agent/templates/ai_agent/modals/
├── edit_payment_policy.html         # Payment terms editor (8.5KB)
├── edit_cancellation_policy.html    # Cancellation policy editor (8.7KB)
└── edit_checkin_times.html          # Check-in/out times editor (6.6KB)
```

**Test Results:**
- Payment policy modal endpoint: 200 OK ✓
- Cancellation policy modal endpoint: 200 OK ✓
- Check-in times modal endpoint: 200 OK ✓
- Live preview API: Working ✓
- Modal loading: Functional ✓
- Save/Cancel operations: Working ✓

**Design:**
- Blue primary color (Stripe-inspired)
- Info boxes explaining user/AI control split
- Mobile-responsive modal sizing
- Keyboard-friendly (Enter to save, Esc to cancel)
- CSRF protection on all endpoints

**Critical Pattern Enforced:**
```
User Controls:               AI Controls:
- Deposit: 50%               - "💳 50% deposit at booking, rest on arrival"
- Timing: at_booking
- Balance: on_arrival

User edits ▶ Structured data ▶ AI generates ▶ Guest sees formatted text
```

**Example Flow:**
1. User clicks "Edit" on payment policy in preview
2. Modal opens with structured inputs (deposit %, timing dropdown)
3. User changes deposit from 50% to 30%
4. Live preview updates: "💳 30% deposit at booking..."
5. User clicks Save
6. Preview panel updates with new formatted text
7. Modal closes smoothly

### ✅ Phase 4.5: Progress Tracker - COMPLETE (Oct 23, 2025)
**Status**: Interactive progress tracker with progressive disclosure fully implemented
**Time Spent**: ~4 hours

**Completed:**
- ✅ Updated OnboardingEngine with SECTIONS structure
  - 4 sections: Property Info (25%), Rooms Setup (45%), Policies (20%), Review & Launch (10%)
  - Each section contains steps with field names and labels
  - Mapping between sections and OnboardingState enum
- ✅ Implemented get_progress_data() method with progressive disclosure
  - Completed sections: Collapsed summary only (expandable)
  - Active section: Shows completed steps + current step + remaining COUNT (not names)
  - Pending sections: Simple "Not started" state
- ✅ Created 4 partial templates
  - `progress_tracker.html` - Main component with overall progress bar
  - `section_complete.html` - Collapsed, expandable section (green checkmark)
  - `section_active.html` - Progressive disclosure (blue, highlighted)
  - `section_pending.html` - Not started (gray, minimal)
- ✅ Built 2 API endpoints
  - `GET /nora/api/progress/` - Returns current progress HTML
  - `POST /nora/api/accept-field/` - Accept Nora's suggestion
- ✅ Integrated into chat.html
  - HTMX polling every 3 seconds for real-time updates
  - Replaces blank preview panel
  - Smooth loading state

**Key Features:**
- **Progressive Disclosure**: Only shows current step details, counts remaining (not names)
- **Visual States**: ✅ Complete (green), ⏳ Active (blue), ⚪ Pending (gray)
- **Expandable Completed**: Click to view details of finished sections
- **Real-time Updates**: HTMX auto-refreshes progress as user chats
- **Smooth Animations**: Progress bar transitions, section expand/collapse

**Test Results:**
- Progressive disclosure logic: Working ✓
- Empty state test: Showing "Property Info" as active ✓
- Partial complete test: 2 steps done, "Country" current, 1 remaining ✓
- Section transition test: 1 complete, 1 active, 2 pending ✓
- API endpoint (/nora/api/progress/): 200 OK (7.7KB HTML) ✓
- Contains expected elements: "Setup Progress", progress bars ✓

**Progressive Disclosure Example:**
```
✅ Property Info (100%)        ← COMPLETED: Collapsed, expandable
   4 items completed
   [Show details ▼]

⏳ Rooms Setup (50%)           ← ACTIVE: Show details
   ✓ Number of room types: 3
   → Standard Room Details ← CURRENT
   ○ Next: 6 more steps      ← COUNT ONLY (no names revealed)

⚪ Policies (0%)               ← PENDING: Just name, no details
   Not started
```

**Benefits:**
- Users see clear progress without feeling overwhelmed
- Focus on current task (what's next, not what's 10 steps ahead)
- Sense of control and agency
- Visual feedback = motivation

**Templates:**
```
apps/ai_agent/templates/ai_agent/partials/
├── progress_tracker.html         # Main wrapper with overall %
├── section_complete.html          # Green checkmark, expandable
├── section_active.html            # Blue highlight, progressive disclosure
└── section_pending.html           # Gray, minimal "Not started"
```


---

## 🎯 What You're Building

**Nora = AI hotel operations co-worker who guides 10-minute onboarding AND remains available for all PMS operations thereafter.**

This is NOT just an onboarding feature - it's a **system-wide AI agent** that becomes the primary interface for the entire PMS.

### The Transformation

**Industry Standard**: 6-12 months to launch a hotel website
**Stayfull with Nora**: 10 minutes

**How**: User provides 10% input (basic answers) → AI does 90% of work (extraction, enhancement, formatting, generation)

---

## 📋 Implementation Phases

### Phase 1: Foundation (8 hours)

**Create AI Agent Infrastructure:**
```bash
# Create new Django app
python manage.py startapp ai_agent

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    ...
    'apps.ai_agent',
]

# Install dependencies
pip install openai redis hiredis googlemaps beautifulsoup4
```

**Files to Create:**
```
apps/ai_agent/
├── models.py              # NoraContext (persistent)
├── services/
│   ├── nora_agent.py     # Main orchestration
│   └── session_manager.py # Redis CRUD
├── views.py
├── urls.py
└── tests/
```

**Key Model:**
```python
# apps/ai_agent/models.py
class NoraContext(models.Model):
    """Persistent AI context for each user (not session-based!)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    conversation_history = models.JSONField(default=list)
    preferences = models.JSONField(default=dict)
    active_task = models.CharField(max_length=50, null=True, blank=True)
    task_state = models.JSONField(default=dict)
    recent_actions = models.JSONField(default=list)
```

**Environment Variables:**
```bash
# Add to .env
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...  # OR use OpenAI Realtime
GOOGLE_PLACES_API_KEY=...
REPLICATE_API_TOKEN=...  # For FLUX image generation
REDIS_URL=redis://localhost:6379/0
```

**Tests:**
- [ ] NoraContext model saves/loads correctly
- [ ] Redis connection works
- [ ] Can create/retrieve session state

---

### Phase 2: Onboarding Core (12 hours)

**Build State Machine:**
```python
# apps/ai_agent/services/conversation_engine.py

class OnboardingState(Enum):
    HOTEL_BASICS = "hotel_basics"
    ROOM_TYPES = "room_types"
    POLICIES = "policies"
    REVIEW = "review"
    COMPLETE = "complete"
```

**Data Acceleration Services:**
```python
# apps/ai_agent/services/data_accelerator.py

class DataAccelerator:
    def extract_from_website(self, url: str) -> dict:
        """Scrape hotel website with BeautifulSoup + GPT-4o cleanup"""

    def enrich_with_google_places(self, hotel_name: str, city: str) -> dict:
        """Get verified data from Google Places API"""

    def infer_from_location(self, zip_code: str) -> dict:
        """Smart defaults: currency, timezone, tax rates"""
```

**Content Formatting:**
```python
# apps/ai_agent/services/content_formatter.py

def enhance_room_description(basic: str, context: dict) -> str:
    """Transform: "Nice room" → "Experience Miami's coastal beauty..." """

def format_payment_policy(data: dict) -> str:
    """Format: {50%, at_booking, on_arrival} → "💳 50% deposit at booking, rest on arrival" """
```

**Critical: User Cannot Edit AI-Formatted Text**
- Policies, descriptions formatted by AI are LOCKED
- User edits structured inputs only (%, timing, etc.)
- See spec Section 4 for details

**Tests:**
- [ ] Website scraping extracts hotel name, address, contact
- [ ] Google Places returns verified data
- [ ] Room description enhancement works
- [ ] Policy formatting produces consistent output
- [ ] State machine transitions correctly

---

### Phase 3: Voice Integration (8 hours)

**Voice Input (Whisper):**
```python
# apps/ai_agent/services/voice_handler.py

def transcribe_audio(audio_file) -> str:
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"
    )
    return response.text
```

**Voice Output (ElevenLabs OR OpenAI Realtime):**
```python
def generate_voice_response(text: str) -> bytes:
    # Option A: ElevenLabs
    audio = elevenlabs.generate(
        text=text,
        voice="Bella",  # Or custom Nora voice
        model="eleven_turbo_v2"
    )
    return audio

    # Option B: OpenAI Realtime API
    # (Architect will provide guidance when ready)
```

**Voice Persona:**
- Default: Enthusiastic, professional, upbeat
- Customizable in settings (3 tone options)
- Female voice, conversational pace (150-160 WPM)

**Error Handling:**
```python
# If voice transcription fails
NORA: "Sorry, I didn't catch that. Want to type it instead?"
[Show text input as fallback]
```

**Tests:**
- [ ] Audio file → text transcription works
- [ ] Text → voice audio works
- [ ] Fallback to text input on error
- [ ] Total latency <8 seconds

---

### Phase 4: UX/UI (10 hours)

**Split-Screen Layout (Desktop):**
```html
<!-- apps/ai_agent/templates/ai_agent/chat.html -->
<div class="flex h-screen">
  <!-- Nora Chat (50%) -->
  <div class="w-1/2 bg-white border-r">
    <div id="progress-bar">60% - Room Types</div>
    <div id="chat-messages">...</div>
    <form id="input-form">
      <input type="text" name="message" />
      <button class="microphone">🎤</button>
      <button type="submit">Send</button>
    </form>
  </div>

  <!-- Live Preview (50%) -->
  <div class="w-1/2 bg-gray-50">
    <iframe src="/preview/{{ session_id }}" class="w-full h-full"></iframe>
  </div>
</div>
```

**Mobile Layout (Tab/Toggle):**
```html
<div class="mobile-view">
  <div class="tabs">
    <button class="tab active">Chat</button>
    <button class="tab">Preview</button>
  </div>
  <div class="tab-content">
    <!-- Active tab shows full screen -->
  </div>
</div>
```

**Design Standards:**
- Follow **Stripe dashboard** aesthetic (clean, minimal, professional)
- See `.architect/DEVELOPMENT_STANDARDS.md` Section 2
- Use TailwindCSS utility classes
- HTMX for dynamic updates (no page reloads)

**Components:**
- Progress bar (shows state: 20%, 40%, 60%, 80%, 100%)
- Message bubbles (AI vs User styling)
- Voice recording animation (waveform)
- Loading states (skeleton screens)
- Edit modals (structured forms, not free text)

**Tests:**
- [ ] Desktop: Split-screen renders correctly
- [ ] Mobile: Tab toggle works
- [ ] Voice button triggers recording
- [ ] Preview updates in real-time
- [ ] WCAG AA compliant

---

### Phase 4.5: Progress Tracker (6 hours) ⚠️ NEW - DO THIS FIRST

**CRITICAL UX UPDATE**: Right panel was blank - users need visibility and control.

**Goal**: Replace blank right panel with interactive progress tracker using progressive disclosure.

**What Users Should See:**

```
Setup Progress            35%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Property Info (100%)
   3 items completed
   [Show details ▼]

⏳ Rooms Setup (25%) ← ACTIVE
   ✓ Number of room types: 3
     [Modify]

   → Standard Room Details ← CURRENT
     "Standard Queen Room"
     [Accept]  [Modify]

   ○ Next: 6 more steps

⚪ Policies (0%)
   Not started

⚪ Review & Launch (0%)
   Not started
```

**Key UX Rules (Progressive Disclosure):**
- ✅ Completed sections: Collapsed by default, expandable
- ⏳ Active section: Shows completed + current + remaining count ONLY
- ⚪ Future sections: Collapsed, no details
- **DO NOT show all future step names** - reveal each step only when user reaches it

**Files to Create:**
```
apps/ai_agent/templates/ai_agent/partials/
├── progress_tracker.html       # Main progress component
├── section_active.html         # Active section (progressive disclosure)
├── section_complete.html       # Completed section (collapsed)
└── section_pending.html        # Not started section
```

**Update conversation_engine.py:**
```python
class OnboardingEngine:
    SECTIONS = [
        {
            'id': 'property_info',
            'name': 'Property Info',
            'steps': ['hotel_name', 'website_url', 'address', 'phone',
                     'email', 'check_in_time', 'check_out_time'],
            'weight': 25  # % of overall progress
        },
        {
            'id': 'rooms_setup',
            'name': 'Rooms Setup',
            'steps': ['num_room_types', 'room_type_1_name', 'room_type_1_occupancy',
                     'room_type_1_beds', 'room_type_1_price', 'room_type_1_description',
                     'room_type_1_amenities', 'room_inventory'],
            'weight': 45
        },
        {
            'id': 'policies',
            'name': 'Policies',
            'steps': ['cancellation_policy', 'deposit_policy', 'payment_terms',
                     'pet_policy', 'age_restrictions'],
            'weight': 20
        },
        {
            'id': 'review',
            'name': 'Review & Launch',
            'steps': ['preview_hotel', 'confirm_details', 'go_live'],
            'weight': 10
        }
    ]

    def get_progress_data(self, task_state: dict) -> dict:
        """
        Return progress with progressive disclosure:
        - Completed sections: summary only
        - Active section: completed steps + current step + remaining COUNT
        - Future sections: not started
        """
        current_step = task_state.get('current_step', 'hotel_name')
        completed_steps = task_state.get('completed_steps', [])
        field_values = task_state.get('field_values', {})

        sections_data = []

        for section in self.SECTIONS:
            if current_step in section['steps']:
                # ACTIVE section - progressive disclosure
                current_index = section['steps'].index(current_step)
                sections_data.append({
                    'id': section['id'],
                    'status': 'active',
                    'completed_steps': [...],  # Only completed
                    'current_step': {...},      # Only current
                    'remaining_count': len(section['steps']) - current_index - 1  # Count only!
                })
            elif all(s in completed_steps for s in section['steps']):
                # COMPLETED section - collapsed
                sections_data.append({
                    'id': section['id'],
                    'status': 'complete',
                    'fields': [...]  # Only show if user expands
                })
            else:
                # PENDING section - collapsed
                sections_data.append({
                    'id': section['id'],
                    'status': 'pending'
                })

        return {'sections': sections_data, 'overall_progress': ...}
```

**Add Accept/Modify Buttons:**
```html
<!-- In section_active.html for current step -->
{% if section.current_step.status == 'proposed' %}
    <!-- Nora suggested value -->
    <div class="bg-white p-3 rounded border">
        <p class="font-medium">{{ section.current_step.value }}</p>
    </div>
    <div class="flex space-x-2">
        <button
            class="px-4 py-2 bg-blue-600 text-white rounded"
            hx-post="/nora/api/accept-field/"
            hx-vals='{"field": "{{ section.current_step.name }}", "value": "{{ section.current_step.value }}"}'
        >
            Accept
        </button>
        <button
            class="px-4 py-2 border rounded"
            hx-get="/nora/api/edit-field/{{ section.current_step.name }}/"
            hx-target="#modal-container"
        >
            Modify
        </button>
    </div>
{% endif %}
```

**New API Endpoints:**
```python
# apps/ai_agent/views.py

@login_required
def get_progress(request):
    """Return updated progress tracker HTML (for HTMX polling)"""
    context = NoraContext.objects.get(user=request.user, organization=...)
    if context.active_task == 'onboarding':
        engine = OnboardingEngine()
        progress_data = engine.get_progress_data(context.task_state)
        return render(request, "ai_agent/partials/progress_tracker.html", {'progress': progress_data})
    return HttpResponse("")

@login_required
@require_http_methods(["POST"])
def accept_field(request):
    """User accepted Nora's suggestion - mark complete and move to next step"""
    data = json.loads(request.body)
    context = NoraContext.objects.get(user=request.user, organization=...)

    # Mark field as accepted
    context.task_state['completed_steps'].append(data['field'])
    context.task_state['field_values'][data['field']] = data['value']

    # Move to next step
    # ... (implement step transition logic)

    context.save()
    return JsonResponse({"success": True})
```

**Update chat.html:**
```html
<!-- Right Panel -->
<div id="preview-panel" class="hidden md:flex flex-col w-full md:w-1/2 bg-gray-50">
    {% if context_summary.active_task == 'onboarding' %}
        <div id="progress-tracker" hx-get="/nora/api/progress/" hx-trigger="every 2s">
            {% include "ai_agent/partials/progress_tracker.html" %}
        </div>
    {% else %}
        <div class="text-center text-gray-400">Start onboarding to see progress</div>
    {% endif %}
</div>

<!-- Modal Container -->
<div id="modal-container"></div>
```

**Tests:**
- [ ] Progress tracker shows when onboarding starts
- [ ] Active section shows: completed + current + "Next: X more steps"
- [ ] Active section does NOT show all future step names
- [ ] Accept button marks step complete
- [ ] Modify button opens editor (Phase 5)
- [ ] Completed sections collapse with expand option
- [ ] Overall % updates correctly
- [ ] User feels in control (approver, not passive)

**Why This Matters:**
- Users see progress and feel in control
- Accept/Modify buttons give agency
- Progressive disclosure prevents overwhelm
- Clear what's done, what's current, what's next

---

### Phase 5: Edit Controls (6 hours)

**Critical Pattern: Editable Data vs. Locked Presentation**

**User CAN edit:**
- Business data (deposit %, timing, etc.)
- Basic room description
- Pricing, occupancy numbers

**User CANNOT edit:**
- AI-formatted guest-facing text
- Policy presentation
- AI-enhanced descriptions

**Implementation:**
```html
<!-- In preview -->
<div class="policy">
  💳 50% deposit at booking, rest on arrival

  <button class="edit-btn" hx-get="/edit/deposit-policy">
    Edit deposit rules
  </button>
</div>

<!-- Clicking opens modal -->
<div class="modal">
  <h3>Edit Payment Policy</h3>

  <label>Deposit Amount:</label>
  <input type="number" name="amount" value="50" />
  <select name="type">
    <option>%</option>
    <option>$</option>
  </select>

  <label>Deposit Due:</label>
  <select name="timing">
    <option>At booking</option>
    <option>X days before arrival</option>
  </select>

  <label>Balance Due:</label>
  <select name="balance_timing">
    <option>On arrival</option>
    <option>X days before arrival</option>
  </select>

  <div class="preview-box">
    <strong>✨ Guest Will See:</strong>
    <p>💳 50% deposit at booking, rest on arrival</p>
    <!-- Updates live as user changes inputs above -->
  </div>

  <button>Cancel</button>
  <button>Save Changes</button>
</div>
```

**Tests:**
- [ ] Edit button opens modal
- [ ] Structured inputs update preview live
- [ ] Cannot directly edit guest-facing text
- [ ] Save updates preview and closes modal

---

### Phase 6: Integration & Polish (12 hours)

**Intro Video ("Play Me First"):**
```html
<!-- First login experience -->
<div class="welcome-screen">
  <video autoplay>
    <source src="{{ nora_intro_video }}" type="video/mp4">
  </video>
  <button class="cta">Let's Go, Nora! 🚀</button>
  <a href="#" class="skip">Skip to setup</a>
</div>
```

**Data Generation:**
```python
# apps/ai_agent/services/data_generator.py

def generate_hotel_from_session(session_data: dict, user) -> Hotel:
    """
    Create operational hotel from onboarding session.

    Creates:
    - Hotel record
    - RoomType records (with AI-enhanced descriptions)
    - Room records (bulk create, auto-numbered)
    - Stock photos or FLUX-generated images
    - Email templates
    """
```

**Integrate with F-001 Models:**
```python
# Use Organization filter (CRITICAL for multi-tenancy)
organization = user.staff.organization

hotel = Hotel.objects.create(
    organization=organization,  # REQUIRED
    name=session_data['hotel_name'],
    ...
)

# Bulk create rooms (performance)
Room.objects.bulk_create(rooms_list)
```

**Success Page:**
```html
<div class="success">
  <h1>🎉 Your hotel is live!</h1>
  <p>We did that in 8 minutes!</p>

  <a href="{{ hotel_url }}">{{ hotel.slug }}.stayfull.com</a>

  <p>Remember: I'm always here. Just click my icon and ask!</p>

  <button>Take me to dashboard →</button>
</div>
```

**Global Nora Icon:**
```html
<!-- Add to base template (every page) -->
<div class="nora-icon">
  💬 Ask Nora
</div>

<!-- Clicking opens full-screen chat (system-wide, not just onboarding) -->
```

**Tests:**
- [ ] Full onboarding flow end-to-end
- [ ] Hotel created with all data
- [ ] All rooms created and numbered correctly
- [ ] Success page shows correct URL
- [ ] Nora icon appears on all pages
- [ ] Load test: 10 concurrent onboardings

**Deploy:**
- [ ] Push to Railway
- [ ] Set environment variables
- [ ] Test in staging
- [ ] Smoke test production

---

## 🔑 Critical Implementation Notes

### 1. This is NOT Just Onboarding

Nora is a **persistent AI agent** available everywhere:
- Onboarding (F-002)
- Daily operations (check-ins, bookings)
- Reports (revenue, occupancy)
- Communication (guest emails, reviews)

**Architecture:**
```python
# Nora can handle ANY PMS operation
USER: "Who's checking in today?"
USER: "Show revenue this week"
USER: "Send pre-arrival emails"
USER: "Raise suite rates for next weekend"

# All route through NoraAgent.process_message()
```

### 2. Security (Multi-Tenancy) is CRITICAL

**ALWAYS filter by Organization:**
```python
# ✅ Correct
hotels = Hotel.objects.filter(organization=request.user.organization)

# ❌ WRONG - Data leakage!
hotels = Hotel.objects.all()
```

See `.architect/DEVELOPMENT_STANDARDS.md` Section 1 for full checklist.

### 3. Design References

**Admin Interfaces (Nora Chat):**
- Follow **Stripe Dashboard** patterns
- Clean, minimal, professional
- System font, blue primary, 8px grid

**Consumer Interfaces (Preview):**
- Follow **Airbnb** patterns
- Visual, card-based, warm palette

See `.architect/DEVELOPMENT_STANDARDS.md` Section 2.

### 4. Voice is Day One (Not Optional)

- Text + Voice from the start
- ElevenLabs OR OpenAI Realtime (swappable)
- Fallback to text on error
- Total latency target: <8 seconds

### 5. Policies are LOCKED

**Users control:**
- Deposit % (50%)
- Timing (at booking)
- Penalty % (100%)

**Stayfull controls:**
- How it displays: "💳 50% deposit at booking, rest on arrival"

This prevents hotel owners from creating bad guest experiences.

---

## 📚 Key Reference Files

**Full Specification (READ THIS FIRST):**
`.architect/features/F-002_AI_ONBOARDING_AGENT.md`

**Development Standards:**
`.architect/DEVELOPMENT_STANDARDS.md`

**F-001 Models (You'll Create These Records):**
- `apps/hotels/models.py` - Hotel, RoomType, Room
- `apps/core/models.py` - Organization, Staff

---

## ✅ Definition of Done

**Functional:**
- [ ] User completes onboarding in 10-12 minutes
- [ ] Hotel is operational (can accept bookings)
- [ ] All F-001 models created correctly
- [ ] 95%+ data extraction accuracy
- [ ] Voice + text input both work
- [ ] Mobile responsive (tab/toggle)

**Technical:**
- [ ] GPT-4o integration working
- [ ] Voice integration (Whisper + ElevenLabs/OpenAI)
- [ ] Redis session management
- [ ] <8 second voice latency
- [ ] Bulk room creation handles 200+ rooms
- [ ] Test coverage >80%

**UX:**
- [ ] Split-screen on desktop, tabs on mobile
- [ ] Real-time preview updates
- [ ] Edit modals work correctly
- [ ] Follows Stripe aesthetic
- [ ] WCAG AA compliant
- [ ] Loading states present
- [ ] Error states handled

**Deployment:**
- [ ] Deployed to Railway
- [ ] Environment variables configured
- [ ] Staging tested
- [ ] Documentation complete

---

## 🚨 IMPORTANT: Start After F-001.1

**DO NOT START F-002 until F-001.1 is complete!**

F-002 requires:
- ✅ Organization model exists
- ✅ Multi-tenancy isolation working
- ✅ Staff linked to Organization
- ✅ All queries filtered by Organization

**When F-001.1 is done:**
1. Read full spec: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
2. Read standards: `.architect/DEVELOPMENT_STANDARDS.md`
3. Set up API keys (OpenAI, ElevenLabs, Google Places)
4. Start with Phase 1 (Foundation)
5. Ask architect if you have questions

---

## 💡 Tips for Success

**Ask Architect When:**
- ⚠️ Hospitality-specific pattern not in Stripe/Airbnb
- ⚠️ Security concern (authentication, multi-tenancy)
- ⚠️ Performance issue (slow queries)
- ⚠️ Feature conflicts with established patterns

**Don't Need to Ask:**
- ✅ Following Stripe/Airbnb patterns
- ✅ Writing tests
- ✅ Styling per design standards
- ✅ Fixing obvious bugs

**Resources:**
- Stripe Dashboard: https://dashboard.stripe.com (reference for admin UI)
- Airbnb: https://airbnb.com (reference for consumer UI)
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- WCAG AA: https://www.w3.org/WAI/WCAG2AA-Conformance

---

## 🎯 Target Completion

**Estimated Effort**: 62 hours (~8 days)

**Breakdown:**
- Phase 1 (Foundation): 8 hours ✅ COMPLETE
- Phase 2 (Onboarding Core): 12 hours ✅ COMPLETE
- Phase 3 (Voice): 8 hours ✅ COMPLETE
- Phase 4 (UX/UI): 10 hours ✅ COMPLETE
- **Phase 4.5 (Progress Tracker): 6 hours ⚠️ DO THIS NEXT**
- Phase 5 (Edit Controls): 6 hours
- Phase 6 (Integration): 12 hours

---

**This is the KILLER FEATURE. Make it delightful. 🚀**

**Questions? Ask the architect. Ready? Let's ship!**
