# Onboarding Conversation Quality Test (Rigorous)

**Priority**: P0 - CRITICAL
**Assigned To**: Developer
**Due**: Before deployment
**Review**: Product Owner + Architect must approve

---

## 🚨 Why This Test Exists

**Previous Test Result**: Developer said "passed" ✅
**Actual Result**: Product owner found it "completely off" ❌

**Problems Found**:
- Sequence of Q&A is poor
- Not activating the right sections
- Not getting data dynamically (Google Places API, Perplexity)
- Bad conversational flow
- Doesn't persist when answers are incomplete
- Moves on without validating data

**Root Cause**: Developer doesn't understand this creates REAL, OPERATIONAL hotels.

**This Test**: Objective, verifiable, with specific expected behaviors

---

## 💰 WHY ACCURATE DATA CAPTURE MATTERS

### This Is Not A Demo. This Creates Real Businesses.

**What Happens After Onboarding**:

1. **Hotel Record Created** → Goes live in production database
2. **Website Generated** → Real customers see it and book rooms
3. **Payments Processed** → Real money flows through Stripe
4. **Guests Check In** → Real people show up expecting a room
5. **Reviews Written** → Bad data = bad reviews = business failure

### Real-World Impact of Bad Data

**If Address is Wrong**:
- ❌ Guests can't find the hotel
- ❌ Google Maps shows wrong location
- ❌ Delivery services can't deliver supplies
- ❌ Emergency services can't respond
- **Result**: Lost bookings, angry guests, 1-star reviews

**If Phone is Wrong**:
- ❌ Guests can't call to ask questions
- ❌ Lost bookings (unanswered calls)
- ❌ Can't confirm reservations
- **Result**: Revenue loss, bad reputation

**If Prices are Wrong**:
- ❌ Hotel loses money (prices too low)
- ❌ No bookings (prices too high)
- ❌ Stripe processes wrong amounts
- **Result**: Financial loss or legal issues

**If Room Quantities are Wrong**:
- ❌ Overbooking (sell rooms that don't exist)
- ❌ Guests arrive with no room available
- ❌ Hotel sued for breach of contract
- **Result**: Lawsuits, refunds, business closure

### Developer: This Is Not "Close Enough"

**BAD Mindset** (what we're seeing):
- "It works, the data gets in somehow" ✅
- "User can fix it later" ✅
- "It's good enough for a demo" ✅

**CORRECT Mindset** (required):
- "Every field must be accurate before moving on" ✅
- "User shouldn't have to fix what we can extract automatically" ✅
- "This creates a real business that will process real money" ✅

### The $100,000 Question

**Scenario**: Hotel completes onboarding. Wrong address saved. Guest books $200/night room for 5 nights. Arrives at wrong address. Can't find hotel. Demands full refund + compensation.

**Cost**:
- Refund: $1,000
- Compensation: $500
- Stripe fees (non-refundable): $50
- Customer service time: $100
- Reputation damage: Priceless

**Total**: $1,650 loss from ONE wrong field.

**Multiply by 1,000 hotels = $1.65 million in potential losses**

### Developer Responsibility

You are building a system that will:
- Create real businesses
- Process real payments
- Serve real customers
- Impact real livelihoods

**Every line of code you write has real-world consequences.**

**If you wouldn't trust it with YOUR hotel, don't ship it.**

---

## 📋 Test Requirements

### You Must Provide

1. **Complete Transcript**: Copy/paste of ENTIRE conversation (every message)
2. **Screenshots**: Progress tracker at 25%, 50%, 75%, 100%
3. **API Logs**: Proof that external APIs were called
4. **Database State**: Final records created
5. **Video Recording**: Screen recording of full onboarding flow

**Without ALL 5 items, test = FAIL automatically**

---

## 🎯 Test Scenario: The Reef House Inn

Use this REAL hotel data. This tests dynamic data extraction.

**Hotel**: The Reef House Inn
**Real Website**: https://www.reefhouseinn.com/ (fictional - use a real one you find)
**Location**: 123 Coastal Highway, Marathon, FL 33050

**What You'll Tell Nora**:
- Hotel name: "The Reef House Inn"
- Website: [Real hotel website URL you find online]
- Location: Marathon, FL

**What Nora MUST Do Automatically**:
- Extract hotel info from website (address, phone, amenities)
- Use Google Places API to enrich data
- Use Perplexity to research local attractions
- Infer timezone (America/New_York)
- Infer currency (USD)
- Suggest tax rate (~13% for Florida)
- Extract photos from website OR offer stock photos
- Research "Things To Do" near Marathon, FL
- Research events happening in Marathon, FL

---

## ✅ Part 1: Conversation Flow Quality (40 points)

### 1.1 Opening & Context Setting (5 points)

**Expected Behavior**:
```
NORA: Hi! I'm Nora, your AI assistant. I'm going to help you set up your hotel
      in about 10 minutes. I'll ask you some questions and do most of the work
      for you. Sound good?

USER: Yes

NORA: Perfect! Let's start with the basics. What's your hotel called?

USER: The Reef House Inn

NORA: The Reef House Inn - I love it! That has such a beautiful coastal feel.

      Do you have a website I can look at? If you do, I can pull a lot of
      information from there to save you time.
```

**Scoring**:
- [ ] Nora introduces herself warmly (1 point)
- [ ] Nora explains what will happen (1 point)
- [ ] Nora asks ONE question at a time (1 point)
- [ ] Nora acknowledges hotel name before moving on (1 point)
- [ ] Nora offers to extract data from website (1 point)

**Your Score**: ___ / 5

**Actual Opening** (paste your transcript):
```
[PASTE ACTUAL CONVERSATION HERE]
```

---

### 1.2 Website Data Extraction (10 points)

**Expected Behavior** (after you provide website URL):

```
USER: https://www.reefhouseinn.com

NORA: Great! Give me a moment to check out your website...

      [2-3 second pause]

      Awesome! I found some information:

      📍 Address: 123 Coastal Highway, Marathon, FL 33050
      📞 Phone: (305) 555-1234
      ✨ I also found 8 photos on your website I can use

      Does this look right?

USER: Yes

NORA: Perfect! Since you're in Marathon, Florida, I've set:
      - Timezone: Eastern (America/New_York)
      - Currency: USD
      - Tax rate: 13% (Florida hotel tax + local)

      You can change these later if needed.
```

**Scoring**:
- [ ] Nora tells user she's checking website (1 point)
- [ ] Nora extracts address from website (2 points) **CRITICAL**
- [ ] Nora extracts phone from website (1 point)
- [ ] Nora extracts photos from website (2 points) **CRITICAL**
- [ ] Nora infers timezone from location (1 point)
- [ ] Nora infers currency from location (1 point)
- [ ] Nora suggests appropriate tax rate (1 point)
- [ ] Nora confirms extracted data with user (1 point)

**Your Score**: ___ / 10

**Actual Website Extraction** (paste transcript):
```
[PASTE ACTUAL CONVERSATION HERE]
```

**API Evidence Required**:
```python
# Paste logs showing:
# 1. HTTP request to hotel website
# 2. BeautifulSoup parsing
# 3. GPT-4o extraction call
# 4. Extracted data (address, phone, etc.)

[PASTE API LOGS HERE]
```

**❌ If Nora just asks for address manually = 0/10 points**

---

### 1.3 Intelligent Question Sequencing (10 points)

**Expected Behavior**:
Nora should ask questions in LOGICAL ORDER and skip questions she already has answers for.

**Good Sequence**:
```
1. Hotel name
2. Website URL → [EXTRACTS: address, phone, email, photos]
3. Check-in time (not extracted)
4. Check-out time (not extracted)
5. Number of room types
6. [For each room type...]
```

**Bad Sequence** (what we DON'T want):
```
1. Hotel name
2. Website URL [but doesn't extract anything]
3. What's your address? [should have extracted this!]
4. What's your phone? [should have extracted this!]
5. What's your email? [should have extracted this!]
6. Upload photos [should have extracted these!]
```

**Scoring**:
- [ ] Nora asks for website URL early (1 point)
- [ ] Nora uses website to extract data (3 points) **CRITICAL**
- [ ] Nora does NOT ask for info she already has (3 points) **CRITICAL**
- [ ] Questions flow logically section by section (2 points)
- [ ] Nora doesn't jump between sections randomly (1 point)

**Your Score**: ___ / 10

**Question Sequence Analysis**:

List every question Nora asked in order:
1.
2.
3.
4.
5.
[continue...]

**Redundant Questions** (questions Nora asked that she should have extracted):
-
-

**Missing Extractions** (data available on website that Nora didn't extract):
-
-

---

### 1.4 Progress Tracker Accuracy (5 points)

**Expected Behavior**:
Progress tracker updates correctly as sections complete.

**Section Breakdown**:
- Property Info (25%): Hotel name, website, address, phone, email, check-in/out, photos
- Rooms Setup (45%): Room types, details, photos, quantities
- Policies (20%): Payment, cancellation, pet, age, tax
- Review (10%): Final review and confirmation

**Scoring**:
- [ ] Progress tracker shows at start (0%) (1 point)
- [ ] Property Info section marked active at start (1 point)
- [ ] After Property Info complete, shows 25% (1 point)
- [ ] After Rooms Setup complete, shows 70% (25% + 45%) (1 point)
- [ ] After Policies complete, shows 90% (1 point)

**Your Score**: ___ / 5

**Progress Tracker Screenshots** (attach):
- Screenshot at 0%:
- Screenshot at 25%:
- Screenshot at 70%:
- Screenshot at 90%:
- Screenshot at 100%:

**❌ If sections don't activate in order = 0/5 points**

---

### 1.5 Conversational Acknowledgment (5 points)

**Expected Behavior**:
Nora acknowledges EVERY answer before asking the next question.

**Good Example**:
```
NORA: What's your hotel called?

USER: Sunset Beach Resort

NORA: Sunset Beach Resort - beautiful name! I can picture it already.

      Do you have a website I can check out?
```

**Bad Example**:
```
NORA: What's your hotel called?

USER: Sunset Beach Resort

NORA: What is your address?  [❌ No acknowledgment!]
```

**Scoring**:
- [ ] Nora acknowledges hotel name (1 point)
- [ ] Nora acknowledges website URL (1 point)
- [ ] Nora acknowledges room type names (1 point)
- [ ] Nora shows enthusiasm appropriately (1 point)
- [ ] Nora uses user's answers in follow-up context (1 point)

**Your Score**: ___ / 5

**Examples of Good Acknowledgment** (paste from your transcript):
1.
2.
3.

**Examples of NO Acknowledgment** (paste from your transcript):
1.
2.
3.

---

### 1.6 Progressive Disclosure (5 points)

**Expected Behavior**:
Nora shows ONLY the current step in progress tracker, not all future steps.

**Good Example** (Active Section):
```
⏳ Rooms Setup (25%)
   ✓ Number of room types: 3
   → Standard Room Details (current)
   ○ Next: 6 more steps
   [Does NOT list all 6 step names]
```

**Bad Example** (Too Much Info):
```
⏳ Rooms Setup (25%)
   ✓ Number of room types: 3
   → Standard Room Details (current)
   ○ Deluxe Room Details
   ○ Premium Room Details
   ○ Room quantities
   ○ Room photos
   [Too much! User overwhelmed]
```

**Scoring**:
- [ ] Active section shows completed steps ✓ (1 point)
- [ ] Active section shows CURRENT step → (1 point)
- [ ] Active section shows remaining COUNT only (not names) (2 points) **CRITICAL**
- [ ] Completed sections collapsed by default (1 point)

**Your Score**: ___ / 5

**Progress Tracker Evidence** (screenshot of active section):
[ATTACH SCREENSHOT]

---

## ✅ Part 2: Dynamic Data Intelligence (30 points)

### 2.1 Google Places API Integration (10 points)

**Expected Behavior**:
When you mention "Marathon, FL", Nora should use Google Places API to enrich data.

**What Should Happen**:
```python
# Behind the scenes:
places_result = gmaps.places(
    query="The Reef House Inn Marathon FL",
    location=(24.7137, -81.0865),  # Marathon, FL coordinates
    radius=50000
)

# Nora should get:
# - Verified address
# - Phone number
# - Website (if different from provided)
# - Rating (if available)
# - Photos
# - Business hours
```

**How to Verify**:
Check application logs for Google Places API calls.

**Scoring**:
- [ ] Google Places API called with hotel name + location (3 points) **CRITICAL**
- [ ] Address verified against Places data (2 points)
- [ ] Phone verified against Places data (2 points)
- [ ] Photos enriched from Places (if available) (2 points)
- [ ] Rating/reviews pulled (if available) (1 point)

**Your Score**: ___ / 10

**API Logs Required**:
```python
# Paste server logs showing Google Places API call
# Must include:
# - API endpoint called
# - Query parameters
# - Response data received

[PASTE LOGS HERE]
```

**❌ If no Google Places API call found in logs = 0/10 points**

---

### 2.2 Perplexity API for Local Research (10 points)

**Expected Behavior**:
Nora uses Perplexity to research "Things To Do" and "Events" near Marathon, FL.

**What Should Happen**:
```python
# Behind the scenes:
things_to_do = perplexity_search(
    query="Best things to do in Marathon, Florida for tourists",
    location="Marathon, FL"
)

events = perplexity_search(
    query="Upcoming events in Marathon, Florida Keys",
    location="Marathon, FL"
)
```

**Expected Results**:
Nora should mention:
- Local attractions (e.g., "I found Dolphin Research Center, Turtle Hospital...")
- Events (e.g., "There's a Seafood Festival in March...")
- Activities (e.g., "Snorkeling, fishing, kayaking are popular...")

**Scoring**:
- [ ] Perplexity API called for Things To Do (3 points) **CRITICAL**
- [ ] Perplexity API called for Events (3 points) **CRITICAL**
- [ ] Nora mentions specific local attractions found (2 points)
- [ ] Nora mentions specific events found (2 points)

**Your Score**: ___ / 10

**API Logs Required**:
```python
# Paste server logs showing Perplexity API calls
# Must include:
# - API endpoint
# - Query sent
# - Results returned

[PASTE LOGS HERE]
```

**Evidence in Conversation**:
```
[Paste part of transcript where Nora mentions Things To Do/Events]
```

**❌ If no Perplexity API call found = 0/10 points**

---

### 2.3 GPT-4o for Data Enhancement (10 points)

**Expected Behavior**:
Nora uses GPT-4o to enhance room descriptions, format policies, etc.

**Example - Room Description**:
```
USER: Standard Queen Room

NORA: Standard Queen Room - got it! Let me create a description...

      [GPT-4o call behind the scenes]

      How about this:

      "Unwind in our Standard Queen Room featuring coastal-inspired décor,
      plush bedding, and stunning ocean views. Perfect for couples seeking
      a peaceful retreat in the Florida Keys."

      Does that capture the vibe?
```

**Scoring**:
- [ ] Room descriptions enhanced by AI (not just stored as-is) (3 points)
- [ ] Policy descriptions formatted professionally (3 points)
- [ ] Hotel description enhanced (if basic input provided) (2 points)
- [ ] AI enhancements feel natural (not robotic) (2 points)

**Your Score**: ___ / 10

**Evidence**:
Show before/after:
- **User Input**: "Nice room with bed"
- **AI Enhancement**: "[paste enhanced description]"

**API Logs**:
```python
# Paste GPT-4o API call for content enhancement
[PASTE LOGS HERE]
```

---

## ✅ Part 3: Technical Correctness (30 points)

### 3.1 Database Records Accurate (15 points)

After onboarding completes, verify database state:

```python
from apps.hotels.models import Hotel, RoomType, Room

# Get the hotel
hotel = Hotel.objects.get(name="The Reef House Inn")

# Verify Hotel data
print(f"Name: {hotel.name}")  # Should be "The Reef House Inn"
print(f"Address: {hotel.address}")  # Should be extracted from website
print(f"Phone: {hotel.contact['phone']}")  # Should be extracted
print(f"Timezone: {hotel.timezone}")  # Should be America/New_York
print(f"Currency: {hotel.currency}")  # Should be USD

# Verify Room Types
room_types = hotel.room_types.all()
print(f"Room types: {room_types.count()}")  # Should match what user said

for rt in room_types:
    print(f"- {rt.name}: ${rt.base_price}, {rt.max_occupancy} guests")

# Verify Rooms
total_rooms = hotel.rooms.count()
print(f"Total rooms: {total_rooms}")  # Should match sum of quantities
```

**Scoring**:
- [ ] Hotel name correct (1 point)
- [ ] Address extracted and stored (3 points) **CRITICAL**
- [ ] Phone extracted and stored (2 points)
- [ ] Timezone inferred correctly (2 points)
- [ ] Currency inferred correctly (1 point)
- [ ] All room types created (2 points)
- [ ] All rooms created with correct quantities (2 points)
- [ ] Room numbers auto-generated (101, 102, etc.) (2 points)

**Your Score**: ___ / 15

**Database Output** (paste results):
```
[PASTE DATABASE QUERY RESULTS HERE]
```

---

### 3.2 API Call Evidence (10 points)

You MUST provide server logs showing these API calls happened:

**Required API Calls**:
1. ✅ Website scraping (BeautifulSoup + requests)
2. ✅ Google Places API call
3. ✅ Perplexity API call (Things To Do)
4. ✅ Perplexity API call (Events)
5. ✅ GPT-4o API calls (content enhancement)

**Scoring**:
- [ ] Website scraping logged (2 points)
- [ ] Google Places API logged (2 points)
- [ ] Perplexity Things To Do logged (2 points)
- [ ] Perplexity Events logged (2 points)
- [ ] GPT-4o enhancement logged (2 points)

**Your Score**: ___ / 10

**Server Logs** (paste):
```bash
# Run your server with logging enabled
# Capture logs showing all API calls

[PASTE LOGS HERE]
```

**How to Generate Logs**:
```python
# Add to your services (if not already there):
import logging

logger = logging.getLogger(__name__)

# In DataExtractor:
logger.info(f"Scraping website: {url}")
response = requests.get(url)
logger.info(f"Extracted data: {extracted_data}")

# In Google Places call:
logger.info(f"Calling Google Places API: {query}")
result = gmaps.places(query)
logger.info(f"Places result: {result}")

# In Perplexity call:
logger.info(f"Calling Perplexity: {query}")
result = perplexity_api.search(query)
logger.info(f"Perplexity result: {result}")
```

**❌ If ANY required API call missing from logs = 0 points for that call**

---

### 3.3 No Manual Data Entry for Extractable Data (5 points)

**Critical Rule**: If data CAN be extracted automatically, Nora should NOT ask for it manually.

**Extractable Data** (from website, APIs, or inference):
- ✅ Address (from website)
- ✅ Phone (from website)
- ✅ Email (from website)
- ✅ Photos (from website)
- ✅ Timezone (from address)
- ✅ Currency (from country)
- ✅ Tax rate suggestion (from location)

**Must Ask Manually**:
- ❌ Hotel name (can't extract reliably)
- ❌ Check-in/out times (not standardized on websites)
- ❌ Room prices (not always on website)
- ❌ Room quantities (not on website)

**Scoring**:
- [ ] Did NOT ask for address if website provided (1 point)
- [ ] Did NOT ask for phone if website provided (1 point)
- [ ] Did NOT ask for email if website provided (1 point)
- [ ] Did NOT ask for timezone (inferred from location) (1 point)
- [ ] Did NOT ask for currency (inferred from location) (1 point)

**Your Score**: ___ / 5

**Manual Questions Nora Asked** (that should have been automatic):
1.
2.
3.

**❌ Each unnecessary manual question = -1 point**

---

## 📊 Scoring Summary

### Part 1: Conversation Flow Quality (40 points)
- 1.1 Opening & Context Setting: ___ / 5
- 1.2 Website Data Extraction: ___ / 10
- 1.3 Intelligent Question Sequencing: ___ / 10
- 1.4 Progress Tracker Accuracy: ___ / 5
- 1.5 Conversational Acknowledgment: ___ / 5
- 1.6 Progressive Disclosure: ___ / 5

**Part 1 Total**: ___ / 40

### Part 2: Dynamic Data Intelligence (30 points)
- 2.1 Google Places API Integration: ___ / 10
- 2.2 Perplexity API for Local Research: ___ / 10
- 2.3 GPT-4o for Data Enhancement: ___ / 10

**Part 2 Total**: ___ / 30

### Part 3: Technical Correctness (30 points)
- 3.1 Database Records Accurate: ___ / 15
- 3.2 API Call Evidence: ___ / 10
- 3.3 No Manual Data Entry for Extractable Data: ___ / 5

**Part 3 Total**: ___ / 30

---

## 🎯 Final Score

**Total Score**: ___ / 100

### Grade Scale

- **90-100**: Excellent - Ready for deployment ✅
- **80-89**: Good - Minor fixes needed ⚠️
- **70-79**: Fair - Major improvements required ❌
- **<70**: Poor - Significant rework needed ❌❌

**Your Grade**: ___

---

## 🚨 Critical Failures (Auto-Fail)

If ANY of these are true, **score = 0** (regardless of other points):

- [ ] **No website data extraction** (Nora asks for address manually)
- [ ] **No Google Places API call** (not in logs)
- [ ] **No Perplexity API call** (not in logs)
- [ ] **Progress tracker doesn't work** (stays at 0% or doesn't update)
- [ ] **Onboarding doesn't complete** (crashes or gets stuck)

**Critical Failures Found**: ___ (should be 0)

---

## 📋 Required Deliverables

Submit ALL of these or test = INCOMPLETE:

1. ✅ **Complete Conversation Transcript**
   - Every message from start to finish
   - Timestamps included
   - Copy/paste as plain text

2. ✅ **Progress Tracker Screenshots**
   - At 0%, 25%, 50%, 75%, 100%
   - Show which section is active
   - Show completed vs. pending sections

3. ✅ **API Call Logs**
   - Server logs showing all API calls
   - Website scraping
   - Google Places
   - Perplexity (2 calls minimum)
   - GPT-4o enhancement

4. ✅ **Database Query Results**
   - Hotel record
   - RoomType records
   - Room records
   - All extracted data visible

5. ✅ **Video Recording**
   - Screen recording of FULL onboarding flow
   - Show conversation, progress tracker, and preview
   - 5-15 minutes total
   - Upload to Loom/YouTube (unlisted)

6. ✅ **This Completed Scorecard**
   - Every section scored
   - All evidence attached
   - Total score calculated

---

## 🎬 How to Record Evidence

### Conversation Transcript

```bash
# Option 1: Copy from browser console
# Open DevTools → Network tab → Find WebSocket messages
# Copy all messages

# Option 2: Add logging to views.py
@login_required
def send_message(request):
    data = json.loads(request.body)
    user_message = data.get("message")

    # LOG USER MESSAGE
    print(f"USER: {user_message}")

    agent = NoraAgent(user=request.user, organization=organization)
    response = agent.process_message(user_message)

    # LOG NORA RESPONSE
    print(f"NORA: {response['message']}")

    return JsonResponse(response)
```

### API Logs

```bash
# In settings.py, enable logging:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.ai_agent': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Then in your services:
import logging
logger = logging.getLogger(__name__)

logger.info("Calling Google Places API...")
logger.info(f"Query: {query}")
logger.info(f"Result: {result}")
```

### Screen Recording

**Mac**:
```bash
# Use QuickTime Player
# File → New Screen Recording
# Record full onboarding flow
# Export as .mov file
```

**Windows**:
```bash
# Use Xbox Game Bar
# Windows + G
# Click Record
# Save video
```

**Upload**:
- Loom: https://loom.com
- YouTube: Upload as "Unlisted"
- Share link in deliverables

---

## ✅ Checklist Before Submitting

- [ ] Ran complete onboarding with The Reef House Inn scenario
- [ ] Provided website URL and Nora extracted data (not manual entry)
- [ ] Verified Google Places API was called (in logs)
- [ ] Verified Perplexity API was called 2x (in logs)
- [ ] Progress tracker activated sections correctly
- [ ] All 5 deliverables attached
- [ ] Scored every section honestly
- [ ] Calculated final score
- [ ] No critical failures

**Ready to Submit**: ✅ YES / ❌ NO

---

## 📝 Developer Declaration

I, [Developer Name], certify that:

1. I personally ran this test (not automated)
2. I provided actual logs (not fabricated)
3. I scored honestly (not inflated)
4. All evidence is from the same test run
5. I understand that the architect will verify these results

**Signature**: ________________
**Date**: ________________

---

## 👨‍💼 Architect Review

**Reviewed By**: ________________
**Date**: ________________

**Verification**:
- [ ] Reviewed full conversation transcript
- [ ] Verified API calls in logs
- [ ] Watched screen recording
- [ ] Checked database state
- [ ] Confirmed score is accurate

**Architect Score**: ___ / 100 (may differ from developer score)

**Approved for Deployment**: ✅ YES / ❌ NO

**Notes**:

---

## 🎯 What "Good" Looks Like

### Example of GOOD Conversation Flow

```
NORA: Hi! I'm Nora. I'll help you set up your hotel in about 10 minutes.
      Ready to get started?

USER: Yes

NORA: Awesome! What's your hotel called?

USER: The Reef House Inn

NORA: The Reef House Inn - I love it! That coastal vibe is perfect for
      the Florida Keys.

      Do you have a website? If you do, I can pull a lot of info from there
      to save you time.

USER: https://www.reefhouseinn.com

NORA: Perfect! Give me just a moment to check out your website...

      [2 seconds later]

      Great news! I found your address (123 Coastal Highway, Marathon, FL),
      phone number (305-555-1234), and 8 photos I can use.

      Since you're in Marathon, Florida, I've automatically set:
      • Timezone: Eastern
      • Currency: USD
      • Suggested tax rate: 13%

      Does all that look right?

USER: Yes

NORA: Perfect! I've also researched some local attractions near your hotel.
      I found the Dolphin Research Center, Turtle Hospital, and Crane Point
      are all popular with visitors. We'll add these to your website so guests
      know what's nearby.

      Now, let's talk about your rooms. How many different room types do you have?

[continues naturally...]
```

### Example of BAD Conversation Flow

```
NORA: What is your hotel name?

USER: The Reef House Inn

NORA: What is your address?  [❌ Should have asked for website first!]

USER: Can you get it from my website?

NORA: What is your website?  [❌ Should have offered this earlier!]

USER: https://www.reefhouseinn.com

NORA: What is your address?  [❌ Should extract from website!]

USER: 123 Coastal Highway, Marathon, FL

NORA: What is your phone number?  [❌ Should extract from website!]

[continues inefficiently...]
```

---

**This test is OBJECTIVE. Either Nora extracts data automatically or she doesn't. Either APIs are called or they're not. No grey area.**

**Questions? Ask the architect BEFORE running the test.**
