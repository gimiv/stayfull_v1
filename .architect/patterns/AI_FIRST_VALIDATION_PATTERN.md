# AI-First Validation Pattern

**Pattern Type**: Core Platform Pattern
**Applies To**: All Features (F-001 through F-022)
**Status**: Foundation - Must be used universally
**Created**: 2025-10-24

---

## Pattern Overview

**The Rule**:
> If data CAN be discovered automatically, it MUST be discovered automatically.
> User validates, never provides from scratch.

**Examples of "discoverable" data**:
- ✅ Hotel address → Google Places
- ✅ Hotel description → Perplexity
- ✅ Room types → Website scraping
- ✅ Tax rates → Government databases / location lookup
- ✅ Timezone → GPS coordinates
- ✅ Currency → Country code
- ✅ Industry defaults → Standards databases
- ✅ Photos → Google Places / Website
- ✅ Amenities → Perplexity / Website
- ✅ Policies → Website / Industry standards

**The bar is HIGH**: Only ask if AI genuinely cannot find it.

---

## The Pattern (Step by Step)

### Step 1: Minimal User Input

**Collect ONLY what's needed to identify the entity.**

```python
# Example: Onboarding
user_input = {
    "hotel_name": "Inn 32",
    "city": "Woodstock",
    "state": "NH"  # Optional, improves search
}

# NOT this:
wrong_input = {
    "hotel_name": ...,
    "address": ...,        # ❌ AI can find this
    "phone": ...,          # ❌ AI can find this
    "amenities": [...],    # ❌ AI can find this
    "description": ...,    # ❌ AI can find this
}
```

**Principle**: User provides identity, AI finds everything else.

---

### Step 2: AI Research (Parallel)

**Launch all research simultaneously, don't wait.**

```python
async def research_entity(minimal_input):
    """
    Research entity from all available sources in parallel.
    """
    # Launch all sources simultaneously
    results = await asyncio.gather(
        # Primary sources (high quality, comprehensive)
        perplexity_search(minimal_input),

        # Secondary sources (verified data, specific fields)
        google_places_search(minimal_input),
        google_maps_lookup(minimal_input),

        # Tertiary sources (direct from source)
        website_scraping(minimal_input),

        # Public databases
        government_data_lookup(minimal_input),
        industry_database_lookup(minimal_input),

        # Context enrichment
        location_enrichment(minimal_input),
        market_data_lookup(minimal_input),

        return_exceptions=True  # Don't fail if one source fails
    )

    return results
```

**Show progress to user**:
```
🔍 Researching Inn 32...
  ✓ Found on Google Places
  ✓ Found detailed info on Perplexity
  ✓ Scraped website
  ✓ Located tax rate database
  ⏳ Analyzing data...
```

**Principle**: Maximize data discovery, minimize wait time.

---

### Step 3: Data Aggregation

**Merge results intelligently, resolve conflicts.**

```python
class DataAggregator:
    """
    Merge data from multiple sources with conflict resolution.
    """

    # Source priority (most trustworthy first)
    SOURCE_PRIORITY = [
        'government_database',  # Official data
        'google_places',        # Verified business info
        'perplexity',          # Comprehensive research
        'website_scraping',    # Direct from source
        'industry_defaults',   # Standards/fallback
    ]

    def merge(self, results: List[Dict]) -> Dict:
        """
        Merge results from multiple sources.

        Conflict resolution:
        1. Prefer higher-priority source
        2. If confidence equal, prefer more recent
        3. If values compatible, merge
        4. Track all sources for transparency
        """
        merged = {}

        for field in ALL_FIELDS:
            candidates = self._get_candidates(field, results)

            if not candidates:
                # No source had this field
                merged[field] = None
                continue

            # Choose best candidate
            best = self._choose_best_candidate(candidates)

            merged[field] = {
                'value': best.value,
                'source': best.source,
                'confidence': best.confidence,
                'alternatives': [c for c in candidates if c != best],
                'verified': False  # User hasn't confirmed yet
            }

        return merged
```

**Example**:
```json
{
  "address": {
    "value": "180 N Main Street, Woodstock, NH 03262",
    "source": "google_places",
    "confidence": 0.95,
    "alternatives": [
      {"value": "180 Main St, North Woodstock, NH", "source": "perplexity"},
      {"value": "180 Main Street", "source": "website"}
    ],
    "verified": false
  },
  "tax_rate": {
    "value": 9.0,
    "source": "nh_government_database",
    "confidence": 0.99,
    "alternatives": [],
    "verified": false
  }
}
```

**Principle**: Use best data available, show alternatives for transparency.

---

### Step 4: Intelligent Defaults

**For missing data, apply smart defaults (if safe).**

```python
def apply_intelligent_defaults(data, context):
    """
    Fill gaps with intelligent defaults when appropriate.
    """
    defaults = {}

    # Safe defaults (industry standards, low risk)
    if not data.get('check_in_time'):
        defaults['check_in_time'] = {
            'value': '3:00 PM',
            'source': 'industry_standard',
            'confidence': 0.90,
            'note': 'Standard hotel check-in time'
        }

    if not data.get('check_out_time'):
        defaults['check_out_time'] = {
            'value': '11:00 AM',
            'source': 'industry_standard',
            'confidence': 0.90,
            'note': 'Standard hotel check-out time'
        }

    # Location-based defaults
    if not data.get('currency') and context.get('country'):
        defaults['currency'] = {
            'value': get_currency_for_country(context['country']),
            'source': 'country_code_map',
            'confidence': 0.99
        }

    # Context-based defaults
    if not data.get('timezone') and context.get('gps'):
        defaults['timezone'] = {
            'value': get_timezone_from_gps(context['gps']),
            'source': 'gps_timezone_api',
            'confidence': 0.99
        }

    # Market-based defaults (for non-critical data)
    if not data.get('base_price') and context.get('city'):
        defaults['base_price'] = {
            'value': estimate_price_from_market(context),
            'source': 'market_data_estimate',
            'confidence': 0.70,
            'note': 'Estimated from similar hotels in area'
        }

    # NEVER default critical financial/legal data
    # (pricing, policies, legal terms, payment info)

    return {**data, **defaults}
```

**Safe to default**:
- ✅ Check-in/out times (industry standard)
- ✅ Timezone (from GPS)
- ✅ Currency (from country)
- ✅ Tax rates (from government databases)
- ✅ Industry-standard policies

**NOT safe to default**:
- ❌ Pricing (too variable)
- ❌ Cancellation penalties (legal implications)
- ❌ Payment terms (contractual)
- ❌ Room quantities (operational impact)

**Principle**: Default when safe, ask when critical.

---

### Step 5: Present Findings

**Show user what AI found in clear, scannable format.**

#### Visual Design

```
┌────────────────────────────────────────────┐
│  📍 LOCATION                               │
├────────────────────────────────────────────┤
│                                            │
│  ✓ 180 N Main Street, Woodstock, NH       │
│  ✓ Timezone: America/New_York             │
│  ✓ GPS: 44.0317°N, 71.6856°W              │
│                                            │
│  Source: Google Places (95% confident)    │
│                                            │
│              [APPROVE] [EDIT]              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  💰 TAX & CURRENCY                         │
├────────────────────────────────────────────┤
│                                            │
│  ✓ Currency: USD                          │
│  ✓ Tax Rate: 9% (NH hotel tax)            │
│                                            │
│  Source: NH Government Database (99%)     │
│                                            │
│              [APPROVE] [EDIT]              │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  📝 DESCRIPTION                            │
├────────────────────────────────────────────┤
│                                            │
│  Inn 32 is a newly revitalized boutique   │
│  motel in North Woodstock, New Hampshire, │
│  located at 180 Main St, just off I-93... │
│                                            │
│  Source: Perplexity (85% confident)       │
│                                            │
│        [APPROVE] [EDIT] [REGENERATE]       │
└────────────────────────────────────────────┘
```

#### Presentation Rules

1. **Group by category** (Location, Description, Rooms, etc.)
2. **Show confidence** ("95% confident" or just show source)
3. **Mark verified** (✓ for AI-found, ✓✓ for user-approved)
4. **Enable editing** (Always show [EDIT] button)
5. **Show sources** ("Found on Google Places")

---

### Step 6: User Validation

**User reviews and validates (not provides) data.**

#### Validation Actions

```python
class ValidationAction(Enum):
    APPROVE = "approve"        # Accept AI's finding
    EDIT = "edit"             # Correct specific fields
    REGENERATE = "regenerate"  # Ask AI to try again
    SKIP = "skip"             # Not applicable/optional
```

#### Validation UI Flow

```
[User sees AI findings]

ACTION: User clicks [APPROVE]
RESULT: Lock category, move to next
        └─> Mark as verified
        └─> Log approval for learning
        └─> Show next category

ACTION: User clicks [EDIT]
RESULT: Open field editor
        └─> Allow field-level changes
        └─> Keep AI data as placeholder
        └─> Log correction for learning
        └─> Save and continue

ACTION: User clicks [REGENERATE]
RESULT: AI tries again
        └─> Use different prompt
        └─> Try different source
        └─> Show new version
        └─> User validates again
```

#### Validation Code

```python
async def handle_validation(category: str, action: ValidationAction, edits: Dict = None):
    """
    Handle user validation of AI findings.
    """
    if action == ValidationAction.APPROVE:
        # User approved AI's work
        mark_verified(category)
        log_approval(category, ai_data[category])
        return next_category()

    elif action == ValidationAction.EDIT:
        # User correcting AI
        for field, new_value in edits.items():
            old_value = ai_data[category][field]['value']

            # Apply edit
            ai_data[category][field]['value'] = new_value
            ai_data[category][field]['verified'] = True
            ai_data[category][field]['user_edited'] = True

            # Log for learning
            log_correction(
                field=field,
                ai_value=old_value,
                user_value=new_value,
                source=ai_data[category][field]['source'],
                context=get_context()
            )

        return next_category()

    elif action == ValidationAction.REGENERATE:
        # User wants AI to try again
        new_data = await regenerate_category(category, attempt=2)
        return present_findings(category, new_data)
```

**Principle**: Make validation fast (single click), editing easy.

---

### Step 7: AI Execution

**With validated data, AI executes the action.**

```python
async def execute_with_validated_data(validated_data):
    """
    AI executes action using user-validated data.
    """
    # All data is verified, safe to proceed
    result = await create_entity(validated_data)

    # Post-execution actions
    await asyncio.gather(
        notify_user(result),
        log_success(validated_data),
        update_learning_models(validated_data),
        trigger_downstream_actions(result)
    )

    return result
```

---

## Measuring Success

### Automation Metrics

```python
class AutomationMetrics:
    """Track AI automation effectiveness."""

    def calculate_automation_rate(self, ai_data, user_edits):
        """
        Automation Rate = Fields AI found / Total fields needed
        """
        total_fields = len(REQUIRED_FIELDS)
        ai_found = len([f for f in ai_data if f['value'] is not None])
        return (ai_found / total_fields) * 100

    def calculate_approval_rate(self, validations):
        """
        Approval Rate = Approved / (Approved + Edited)
        """
        approved = len([v for v in validations if v == 'approve'])
        edited = len([v for v in validations if v == 'edit'])
        return (approved / (approved + edited)) * 100

    def calculate_time_saved(self, ai_time, manual_time):
        """
        Time Saved = Manual time - AI time
        """
        return manual_time - ai_time
```

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Automation Rate** | 90%+ | % of fields AI found vs total needed |
| **Approval Rate** | 90%+ | % of AI findings user approved without edit |
| **Accuracy** | 95%+ | % of AI findings that were correct |
| **Time Saved** | 10x faster | Manual time / AI time |
| **User Satisfaction** | NPS 50+ | Post-task survey |

---

## Implementation Checklist

### For Every Feature

When implementing ANY feature, verify:

**Research Phase** ✓
- [ ] Identified all possible data sources
- [ ] Mapped data availability by source
- [ ] Designed fallback chain (primary → secondary → tertiary → default → manual)
- [ ] Estimated automation rate (target 80%+)

**Design Phase** ✓
- [ ] Designed minimal user input (just identity)
- [ ] Designed AI research flow (parallel sources)
- [ ] Designed presentation UI (approve/edit/regenerate)
- [ ] Designed editing interface (field-level)
- [ ] Designed fallback to manual

**Implementation Phase** ✓
- [ ] Built data source integrations
- [ ] Built aggregation/merge logic
- [ ] Built confidence scoring
- [ ] Built validation UI
- [ ] Built learning feedback loop
- [ ] Built fallback chain

**Testing Phase** ✓
- [ ] Tested automation rate (≥80%)
- [ ] Tested approval rate (≥90%)
- [ ] Tested accuracy (≥95%)
- [ ] Tested time savings (≥10x)
- [ ] Tested all fallback paths
- [ ] Tested with diverse real-world data

---

## Code Examples

### Research Orchestrator

```python
class ResearchOrchestrator:
    """
    Coordinates research across multiple sources.
    Implements the AI-First Validation Pattern.
    """

    def __init__(self):
        self.sources = {
            'perplexity': PerplexityService(),
            'google_places': GooglePlacesService(),
            'website': WebScrapingService(),
            'government': GovernmentDataService(),
            'industry': IndustryDatabaseService(),
        }

    async def research(self, entity_type: str, minimal_input: Dict) -> Dict:
        """
        Research entity from all sources, return merged data.
        """
        # Step 1: Identify which sources are applicable
        applicable_sources = self._get_applicable_sources(entity_type)

        # Step 2: Launch research in parallel
        tasks = [
            source.search(minimal_input)
            for source in applicable_sources
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Step 3: Aggregate results
        aggregated = DataAggregator.merge(results)

        # Step 4: Apply intelligent defaults
        complete = self._apply_defaults(aggregated, minimal_input)

        # Step 5: Calculate confidence scores
        scored = self._score_confidence(complete)

        return scored
```

### Validation Handler

```python
class ValidationHandler:
    """
    Handles user validation of AI findings.
    """

    async def present_for_validation(
        self,
        category: str,
        ai_findings: Dict
    ) -> Dict:
        """
        Present AI findings to user for validation.
        """
        return {
            'category': category,
            'findings': ai_findings,
            'confidence': self._calculate_confidence(ai_findings),
            'sources': self._get_sources(ai_findings),
            'actions': ['approve', 'edit', 'regenerate'],
            'ui_template': 'validation_card'
        }

    async def handle_validation_response(
        self,
        category: str,
        action: str,
        edits: Dict = None
    ) -> Dict:
        """
        Process user's validation response.
        """
        if action == 'approve':
            return await self._handle_approve(category)
        elif action == 'edit':
            return await self._handle_edit(category, edits)
        elif action == 'regenerate':
            return await self._handle_regenerate(category)
```

---

## Anti-Patterns to Avoid

### ❌ Asking Before Researching

**WRONG**:
```python
def get_hotel_info():
    name = ask_user("What's your hotel name?")
    address = ask_user("What's your address?")  # ❌ Should research
    phone = ask_user("What's your phone?")      # ❌ Should research
```

**RIGHT**:
```python
async def get_hotel_info():
    name, city = await ask_user("Hotel name and city?")

    # AI researches everything
    findings = await research_hotel(name, city)

    # User validates
    validated = await present_for_validation(findings)

    return validated
```

### ❌ Hiding AI Work

**WRONG**:
```python
# User never sees that AI did research
data = await ai_research()
return data  # Just show final result
```

**RIGHT**:
```python
# User sees AI at work
ui.show_progress("Researching...")
data = await ai_research()
ui.show_findings(data, sources=True)  # Show what AI found
return await user_validates(data)
```

### ❌ Not Providing Fallback

**WRONG**:
```python
data = await ai_research()
if not data:
    raise Exception("Could not find data")  # ❌ No fallback
```

**RIGHT**:
```python
data = await ai_research()
if not data:
    # Graceful fallback to manual
    data = await fallback_to_manual_entry()
return data
```

---

## This Pattern is Mandatory

**Every feature must implement this pattern.**

**Every code review must verify this pattern.**

**This is the Stayfull architecture.**

---

**Questions? Refer to `.architect/CORE_PHILOSOPHY.md`**
