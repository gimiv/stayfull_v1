# F-002: AI Onboarding Agent (10-Minute Hotel Setup)

**Feature ID**: F-002
**Priority**: P1 - Foundation (Killer Feature)
**Type**: AI-Powered User Experience
**Status**: Approved - Ready for Development
**Effort**: 42 hours (~1 week)
**Created**: 2025-10-23
**Decision**: #009

---

## 🎯 Executive Summary

**The Problem**:
- Traditional PMS onboarding takes 60-90 minutes
- Complex forms, unclear fields, high abandonment
- Requires technical knowledge
- Support-intensive

**The Solution**:
- AI-powered conversational onboarding
- Natural language Q&A (guided questions)
- Hotel operational in **10 minutes**
- Zero technical knowledge required

**The Impact**:
- 10x faster than competitors
- 90%+ completion rate (vs 40% industry standard)
- Minimal support burden
- Primary competitive differentiation
- Viral "wow moment" for marketing

---

## 📋 Business Requirements

### Target User Journey (10-12 Minutes):

```
Minute 0-2: Sign Up
├─ User creates account
├─ System creates Organization + default staff
└─ Redirect to AI onboarding chat

Minute 2-10: AI Conversation (Guided Q&A)
├─ State 1: Hotel Basics (2 min)
│   └─ Name, location, contact, type, timezone
├─ State 2: Room Types (4 min)
│   └─ For each type: name, beds, amenities, occupancy, price
├─ State 3: Room Inventory (1 min)
│   └─ Auto-generate room numbers, confirm count
├─ State 4: Policies (2 min)
│   └─ Check-in/out times, cancellation, deposits
└─ State 5: Review & Confirm (1 min)
    └─ Show summary, user confirms

Minute 10-11: Data Generation (30 sec)
├─ Create Hotel record
├─ Create RoomType records
├─ Bulk-create Room records
├─ Set up policies
└─ Assign stock photos

Minute 11-12: Success & Next Steps
├─ "Your hotel is live!"
├─ Quick tour of admin
├─ Link to booking engine
└─ Suggested next steps
```

### What Gets Created (Operational Hotel):

**Core Records**:
- ✅ Organization (from signup)
- ✅ Hotel (complete with all details)
- ✅ Staff (hotel owner account)
- ✅ RoomTypes (all defined types with amenities, beds, pricing)
- ✅ Rooms (all individual units, auto-numbered)
- ✅ Policies (check-in/out, cancellation)

**Auto-Generated**:
- ✅ Stock room photos (from library or AI-generated)
- ✅ Room numbers (101-150, 201-250, etc.)
- ✅ Default settings (currency, timezone)

**NOT Created (Can Add Later)**:
- ❌ Custom photos (user uploads later)
- ❌ Integrations (payment, channel manager)
- ❌ Additional staff accounts
- ❌ Guest records

**Result**: Hotel can accept first booking immediately after onboarding.

---

## 🏗️ Technical Architecture

### Component Overview:

```
┌──────────────────────────────────────────────────────────────┐
│                    F-002 Architecture                         │
└──────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Frontend   │─────▶│   Backend     │─────▶│   OpenAI API    │
│  Chat UI     │◀─────│  Conversation │◀─────│   GPT-4o        │
│  (HTMX)      │      │  Engine       │      │                 │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │  (Session)   │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  (F-001 DB)  │
                     └──────────────┘
```

---

## 🎨 Frontend: Chat Interface

### Location:
**Django Template** (not separate Next.js app for MVP)
- Path: `/onboarding/` (after signup)
- Template: `apps/onboarding/templates/onboarding/chat.html`
- Tech: Django + HTMX for real-time chat updates

### UI Components:

```html
<!-- Simple, clean chat interface -->
<div class="chat-container">
  <!-- Progress bar -->
  <div class="progress-bar">
    <div class="progress" style="width: 40%"></div>
    <span>Step 2 of 5: Room Types</span>
  </div>

  <!-- Chat messages -->
  <div class="messages" id="chat-messages">
    <div class="message ai">
      <div class="avatar">🤖</div>
      <div class="text">What's your hotel called?</div>
    </div>

    <div class="message user">
      <div class="text">Seaside Resort</div>
      <div class="avatar">👤</div>
    </div>
  </div>

  <!-- Input -->
  <form hx-post="/onboarding/message/" hx-target="#chat-messages" hx-swap="beforeend">
    <input type="text" name="message" placeholder="Type your answer..." autofocus>
    <button type="submit">Send</button>
  </form>
</div>
```

**Styling**: Clean, modern, mobile-responsive (Tailwind CSS)

---

## 🧠 Backend: Conversation Engine

### State Machine (5 States):

```python
# apps/onboarding/services/state_machine.py

class OnboardingState(Enum):
    HOTEL_BASICS = "hotel_basics"
    ROOM_TYPES = "room_types"
    ROOM_INVENTORY = "room_inventory"
    POLICIES = "policies"
    REVIEW = "review"
    COMPLETE = "complete"


class StateTransitions:
    """Defines state flow and validation"""

    FLOW = {
        OnboardingState.HOTEL_BASICS: {
            'next': OnboardingState.ROOM_TYPES,
            'required_fields': ['name', 'address', 'contact', 'timezone', 'currency'],
        },
        OnboardingState.ROOM_TYPES: {
            'next': OnboardingState.ROOM_INVENTORY,
            'required_fields': ['room_types'],  # At least 1
            'can_loop': True,  # User can add multiple room types
        },
        OnboardingState.ROOM_INVENTORY: {
            'next': OnboardingState.POLICIES,
            'required_fields': ['room_count_confirmed'],
        },
        OnboardingState.POLICIES: {
            'next': OnboardingState.REVIEW,
            'required_fields': ['check_in_time', 'check_out_time'],
        },
        OnboardingState.REVIEW: {
            'next': OnboardingState.COMPLETE,
            'required_fields': ['user_confirmed'],
        },
    }
```

---

### Conversation Engine (Core Logic):

```python
# apps/onboarding/services/conversation_engine.py

from openai import OpenAI
import json
from typing import Dict, Any


class OnboardingConversationEngine:
    """
    AI-powered conversation engine for hotel onboarding.

    Uses GPT-4o for:
    1. Extracting structured data from user messages
    2. Generating natural follow-up questions
    3. Validating user inputs
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = self.load_state_from_redis()
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message and return AI response.

        Flow:
        1. Get current state and context
        2. Use GPT-4o to extract data from user message
        3. Validate extracted data
        4. Update session state
        5. Generate next question
        6. Return response
        """

        # Get current state context
        current_state = self.state['current_step']
        conversation_history = self.state['conversation_history']

        # Build prompt for GPT-4o
        extraction_prompt = self._build_extraction_prompt(
            state=current_state,
            user_message=user_message,
            history=conversation_history
        )

        # Call GPT-4o to extract structured data
        extracted_data = self._extract_data_with_gpt4o(extraction_prompt)

        # Validate extracted data
        is_valid, validation_errors = self._validate_data(
            data=extracted_data,
            state=current_state
        )

        if is_valid:
            # Update session with extracted data
            self._update_session(extracted_data)

            # Determine if we should advance to next state
            can_advance = self._check_state_completion(current_state)

            if can_advance:
                next_state = self._get_next_state(current_state)
                self.state['current_step'] = next_state
                ai_response = self._generate_question_for_state(next_state)
            else:
                # Stay in current state, ask next question
                ai_response = self._generate_next_question_in_state(current_state)

        else:
            # Data invalid, ask for clarification
            ai_response = self._generate_clarification_message(validation_errors)

        # Save conversation history
        self._save_conversation_turn(user_message, ai_response)

        # Save state to Redis
        self._save_state_to_redis()

        return {
            'message': ai_response,
            'state': self.state['current_step'],
            'progress': self._calculate_progress(),
            'data_collected': self.state['data']
        }


    def _build_extraction_prompt(self, state: str, user_message: str, history: list) -> str:
        """
        Build prompt for GPT-4o to extract structured data.

        Uses JSON mode for reliable extraction.
        """

        if state == OnboardingState.HOTEL_BASICS:
            return f"""
You are helping onboard a hotel owner. Extract structured data from their message.

Current question context: We're collecting hotel basic information.

User said: "{user_message}"

Extract and return JSON with these fields (only include fields mentioned):
{{
  "name": "hotel name",
  "address": {{
    "street": "street address",
    "city": "city",
    "state": "state/province",
    "postal_code": "zip/postal code",
    "country": "country"
  }},
  "contact": {{
    "email": "email",
    "phone": "phone number"
  }},
  "timezone": "IANA timezone (e.g., America/New_York)",
  "currency": "ISO 4217 code (e.g., USD)"
}}

If user's message doesn't contain these fields, return empty object {{}}.
Be smart about inferring (e.g., "Miami" → city: Miami, state: FL, country: US).
"""

        elif state == OnboardingState.ROOM_TYPES:
            return f"""
You are helping collect room type information for a hotel.

User said: "{user_message}"

Extract room type details and return JSON:
{{
  "name": "room type name (e.g., Standard Room, Ocean Suite)",
  "code": "short code (e.g., STD, SUI) - generate if not provided",
  "count": "number of rooms of this type",
  "max_occupancy": "maximum total guests",
  "max_adults": "maximum adults",
  "max_children": "maximum children",
  "beds": [
    {{"type": "bed type (king/queen/twin/sofa_bed)", "count": 1}}
  ],
  "amenities": ["WiFi", "TV", "Mini Fridge", etc.],
  "base_price": "nightly rate (number)",
  "size_sqft": "room size in square feet (number, optional)"
}}

Be smart about inferring:
- "queen bed" → beds: [{{"type": "queen", "count": 1}}]
- "2 queens" → beds: [{{"type": "queen", "count": 2}}]
- "40 rooms at $150/night" → count: 40, base_price: 150

If not provided, use smart defaults:
- max_occupancy: 2 for standard, 4 for suites
- max_adults: same as max_occupancy
- max_children: half of max_occupancy
"""

        # Add similar prompts for other states...


    def _extract_data_with_gpt4o(self, prompt: str) -> Dict[str, Any]:
        """
        Call GPT-4o to extract structured data from user message.

        Uses JSON mode for reliable structured output.
        """

        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. Extract structured information from user messages and return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},  # Force JSON output
            temperature=0.1,  # Low temp for consistency
        )

        extracted_json = response.choices[0].message.content
        return json.loads(extracted_json)


    def _generate_question_for_state(self, state: str) -> str:
        """
        Generate the first question for a new state.

        Uses GPT-4o for natural, conversational phrasing.
        """

        # Predefined questions (can also use GPT-4o to generate)
        QUESTIONS = {
            OnboardingState.HOTEL_BASICS: "Let's get started! What's your hotel called?",
            OnboardingState.ROOM_TYPES: "Great! Now let's set up your rooms. How many different room types do you have? (For example: standard rooms, suites, etc.)",
            OnboardingState.ROOM_INVENTORY: "Perfect! I'll generate room numbers for you. How would you like me to number them? (e.g., 101-140, 201-250)",
            OnboardingState.POLICIES: "Almost done! What time can guests check in?",
            OnboardingState.REVIEW: "Here's what I've set up for you. Please review and confirm:",
        }

        return QUESTIONS.get(state, "Tell me more.")


    def _validate_data(self, data: Dict, state: str) -> tuple[bool, list]:
        """
        Validate extracted data using F-001 model validators.

        Returns: (is_valid, error_list)
        """

        errors = []

        if state == OnboardingState.HOTEL_BASICS:
            # Validate hotel name
            if 'name' in data:
                if len(data['name']) < 3:
                    errors.append("Hotel name must be at least 3 characters")

            # Validate email format
            if 'contact' in data and 'email' in data['contact']:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['contact']['email']):
                    errors.append("Invalid email format")

            # Validate timezone
            if 'timezone' in data:
                import pytz
                if data['timezone'] not in pytz.all_timezones:
                    errors.append(f"Invalid timezone: {data['timezone']}")

        elif state == OnboardingState.ROOM_TYPES:
            # Validate pricing
            if 'base_price' in data:
                try:
                    price = float(data['base_price'])
                    if price <= 0:
                        errors.append("Price must be greater than $0")
                except (ValueError, TypeError):
                    errors.append("Invalid price format")

            # Validate occupancy logic (from F-001)
            if all(k in data for k in ['max_occupancy', 'max_adults', 'max_children']):
                if data['max_adults'] > data['max_occupancy']:
                    errors.append("Max adults cannot exceed max occupancy")
                if data['max_children'] > data['max_occupancy']:
                    errors.append("Max children cannot exceed max occupancy")

        return (len(errors) == 0, errors)
```

---

## 📊 Session State (Redis)

### Data Structure:

```python
# Stored in Redis with 24-hour TTL
SESSION_KEY = f"onboarding:{session_id}"

session_data = {
    "session_id": "uuid",
    "user_id": 123,
    "organization_id": 456,
    "current_step": "room_types",
    "progress": 0.4,  # 40% complete

    "conversation_history": [
        {"role": "ai", "message": "What's your hotel called?", "timestamp": "..."},
        {"role": "user", "message": "Seaside Resort", "timestamp": "..."},
        {"role": "ai", "message": "Where is Seaside Resort located?", "timestamp": "..."},
        # ... full conversation
    ],

    "data": {
        "hotel_basics": {
            "name": "Seaside Resort",
            "address": {
                "street": "123 Ocean Drive",
                "city": "Miami",
                "state": "FL",
                "postal_code": "33139",
                "country": "US"
            },
            "contact": {
                "email": "info@seaside.com",
                "phone": "+1-305-555-1234"
            },
            "type": "independent",
            "timezone": "America/New_York",
            "currency": "USD"
        },

        "room_types": [
            {
                "name": "Standard Room",
                "code": "STD",
                "count": 40,
                "max_occupancy": 2,
                "max_adults": 2,
                "max_children": 1,
                "beds": [{"type": "queen", "count": 1}],
                "amenities": ["WiFi", "TV", "Mini Fridge"],
                "base_price": 150.00,
                "size_sqft": 300
            },
            {
                "name": "Ocean View Suite",
                "code": "OVS",
                "count": 10,
                "max_occupancy": 4,
                "max_adults": 2,
                "max_children": 2,
                "beds": [
                    {"type": "king", "count": 1},
                    {"type": "sofa_bed", "count": 1}
                ],
                "amenities": ["WiFi", "TV", "Ocean View", "Balcony", "Mini Bar", "Safe"],
                "base_price": 350.00,
                "size_sqft": 550
            }
        ],

        "room_inventory": {
            "numbering_scheme": "sequential",
            "starting_number": 101
        },

        "policies": {
            "check_in_time": "15:00:00",
            "check_out_time": "11:00:00",
            "cancellation_hours": 24,
            "deposit_percent": 0  # Optional
        }
    },

    "created_at": "2025-10-23T12:00:00Z",
    "updated_at": "2025-10-23T12:08:00Z"
}
```

---

## 🏭 Data Generation Engine

### Final Step: Create All Records

```python
# apps/onboarding/services/data_generator.py

from apps.core.models import Organization
from apps.hotels.models import Hotel, RoomType, Room
from apps.staff.models import Staff
from decimal import Decimal


class OnboardingDataGenerator:
    """
    Generates all F-001 records from onboarding session data.

    Creates:
    - Hotel
    - RoomTypes
    - Rooms (bulk create)
    - Default photos
    """

    def generate_hotel_from_session(self, session_data: dict, user) -> Hotel:
        """
        Create complete operational hotel from session data.

        Returns: Hotel instance (ready to accept bookings)
        """

        hotel_data = session_data['data']['hotel_basics']
        room_types_data = session_data['data']['room_types']
        policies_data = session_data['data']['policies']

        # 1. Get or create organization (from signup)
        organization = user.staff.organization

        # 2. Create Hotel
        hotel = Hotel.objects.create(
            organization=organization,
            name=hotel_data['name'],
            slug=self._generate_slug(hotel_data['name']),
            type=hotel_data['type'],
            address=hotel_data['address'],
            contact=hotel_data['contact'],
            timezone=hotel_data['timezone'],
            currency=hotel_data['currency'],
            languages=['en'],  # Default, can customize later
            check_in_time=policies_data['check_in_time'],
            check_out_time=policies_data['check_out_time'],
            total_rooms=sum(rt['count'] for rt in room_types_data),
            is_active=True,
        )

        # 3. Create RoomTypes
        for rt_data in room_types_data:
            room_type = RoomType.objects.create(
                hotel=hotel,
                name=rt_data['name'],
                code=rt_data['code'],
                description=f"{rt_data['name']} at {hotel.name}",
                max_occupancy=rt_data['max_occupancy'],
                max_adults=rt_data['max_adults'],
                max_children=rt_data['max_children'],
                base_price=Decimal(str(rt_data['base_price'])),
                size_sqm=self._sqft_to_sqm(rt_data.get('size_sqft', 0)),
                bed_configuration=rt_data['beds'],
                amenities=rt_data['amenities'],
                images=self._get_stock_photos(rt_data['name']),  # Stock photos
                is_active=True,
                display_order=0,
            )

            # 4. Generate Room records (bulk create for performance)
            rooms_to_create = []
            room_count = rt_data['count']

            # Generate room numbers (e.g., 101-140 for 40 rooms)
            room_numbers = self._generate_room_numbers(
                count=room_count,
                scheme=session_data['data']['room_inventory']['numbering_scheme']
            )

            for room_number in room_numbers:
                rooms_to_create.append(
                    Room(
                        hotel=hotel,
                        room_type=room_type,
                        room_number=room_number,
                        floor=int(room_number[0]) if room_number.isdigit() else 1,
                        status='available',
                        cleaning_status='clean',
                        is_active=True
                    )
                )

            # Bulk create (fast!)
            Room.objects.bulk_create(rooms_to_create)

        return hotel


    def _generate_room_numbers(self, count: int, scheme: str) -> list[str]:
        """
        Generate room numbers based on scheme.

        Schemes:
        - sequential: 101, 102, 103...
        - floor_based: 101-110 (floor 1), 201-210 (floor 2)
        """

        if scheme == 'sequential':
            return [str(100 + i + 1) for i in range(count)]

        elif scheme == 'floor_based':
            # Distribute across floors (10 rooms per floor)
            room_numbers = []
            floor = 1
            room_on_floor = 1

            for _ in range(count):
                room_numbers.append(f"{floor}{room_on_floor:02d}")
                room_on_floor += 1

                if room_on_floor > 10:  # Move to next floor
                    floor += 1
                    room_on_floor = 1

            return room_numbers


    def _get_stock_photos(self, room_type_name: str) -> list:
        """
        Return stock photos for room type.

        MVP: Use curated stock photo library
        Future: AI-generate images with DALL-E
        """

        # Stock photo library (Unsplash, Pexels, etc.)
        STOCK_PHOTOS = {
            'standard': [
                {'url': 'https://images.unsplash.com/photo-1...', 'alt': 'Standard Room'},
            ],
            'suite': [
                {'url': 'https://images.unsplash.com/photo-2...', 'alt': 'Suite'},
            ],
            'ocean': [
                {'url': 'https://images.unsplash.com/photo-3...', 'alt': 'Ocean View'},
            ],
        }

        # Match by keywords
        for keyword, photos in STOCK_PHOTOS.items():
            if keyword.lower() in room_type_name.lower():
                return photos

        return STOCK_PHOTOS['standard']  # Default
```

---

## 📊 Implementation Phases

### Phase 1: Foundation (8 hours)
- [ ] Create `onboarding` Django app
- [ ] Set up Redis connection for session storage
- [ ] Create session management service
- [ ] Create state machine logic
- [ ] Write unit tests for state transitions

### Phase 2: AI Integration (10 hours)
- [ ] Set up OpenAI API client
- [ ] Build conversation engine
- [ ] Create extraction prompts for each state
- [ ] Implement GPT-4o structured output
- [ ] Add validation logic
- [ ] Test extraction accuracy (95%+ target)

### Phase 3: Frontend Chat UI (8 hours)
- [ ] Create Django template for chat interface
- [ ] Implement HTMX real-time messaging
- [ ] Add progress bar component
- [ ] Style with Tailwind CSS
- [ ] Make mobile-responsive
- [ ] Test UX flow

### Phase 4: Data Generation (8 hours)
- [ ] Build data generator service
- [ ] Implement room number generation
- [ ] Add stock photo library
- [ ] Create bulk room creation
- [ ] Test with various hotel configurations
- [ ] Verify F-001 model validation works

### Phase 5: Integration & Testing (8 hours)
- [ ] Integrate with signup flow
- [ ] End-to-end testing (full onboarding)
- [ ] Load testing (handle concurrent onboardings)
- [ ] Error handling and retry logic
- [ ] Add analytics tracking
- [ ] Documentation

---

## ✅ Success Criteria

### Functional:
- ✅ User completes onboarding in 10-12 minutes
- ✅ Hotel is operational (can accept bookings)
- ✅ All F-001 models created correctly
- ✅ 95%+ data extraction accuracy
- ✅ Graceful error handling
- ✅ Mobile-responsive UI

### Technical:
- ✅ GPT-4o integration working
- ✅ Redis session management
- ✅ <2 second response time per message
- ✅ Bulk room creation (handles 200+ rooms)
- ✅ Test coverage >85%

### Business:
- ✅ 90%+ completion rate
- ✅ <$0.10 AI cost per onboarding
- ✅ Zero support tickets for onboarding
- ✅ Positive user feedback

---

## 💰 Cost Analysis

### Per Onboarding:
```
GPT-4o API calls: ~25 requests
Tokens per onboarding: ~5,000 tokens
Cost: $0.075 per hotel

At scale:
- 100 hotels/month: $7.50/month
- 1,000 hotels/month: $75/month
- 10,000 hotels/month: $750/month

Revenue impact:
- Each hotel = $999/month
- AI cost = 0.0075% of revenue
- Negligible vs. 10x better conversion
```

**Recommendation**: Don't optimize AI costs until 1,000+ hotels/month.

---

## 🚀 Post-MVP Enhancements (F-002.1)

### Phase 2 Features:
1. **Voice Input** (Whisper API) - 8h
   - Speak answers instead of typing
   - Accessibility win

2. **Hybrid Conversation Mode** - 12h
   - Accept long-form answers
   - "Tell me about your hotel" → extracts everything

3. **Photo Upload & AI Description** - 10h
   - Upload photos during onboarding
   - AI generates descriptions

4. **Multi-Language Support** - 6h
   - Onboarding in Spanish, French, etc.
   - GPT-4o handles translation

5. **Smart Defaults from Location** - 4h
   - "Miami" → auto-fill timezone, currency
   - Suggest room prices based on market

---

## 📝 Notes

### Why GPT-4o?
- Structured output mode (JSON)
- Fast, reliable
- Good at following instructions
- Worth the cost for MVP

### Why Not Build Custom NLP?
- Too much effort
- Lower accuracy
- Slower iteration
- LLMs are better at this

### Why Guided Questions vs. Pure Conversation?
- Reliability: Guided = 95%+ accuracy, Pure = 70%
- User confidence: Clear what's being collected
- Easier to debug and test
- Can evolve to hybrid later

### Integration with F-001:
- Uses ALL F-001 models (Hotel, RoomType, Room, Staff)
- Validates using F-001 model validators
- Creates production-ready data
- No shortcuts or temp data

---

## 🎯 Ready for Development

**Estimated Effort**: 42 hours (~1 week)
**Dependencies**: F-001.1 complete (Organization model)
**Risk**: Low (well-understood tech stack)
**Business Impact**: HIGH (killer feature)

**Next**: Developer implements after F-001.1 ships.

---

**Architect Approval**: ✅ APPROVED
**User Approval**: ✅ APPROVED (All recommendations accepted)
