# Decision 009: F-002 AI Onboarding Agent Architecture

**Date**: 2025-10-23
**Status**: Approved
**Feature**: F-002 AI Onboarding Agent
**Impact**: High - Primary competitive differentiation

---

## Context

Traditional PMS onboarding takes 60-90 minutes with complex forms, resulting in:
- 40% completion rate (high abandonment)
- High support burden
- Poor first impression
- Barrier to customer acquisition

User identified 10-minute onboarding as primary competitive advantage.

---

## Decision

Build AI-powered conversational onboarding that creates operational hotel in 10 minutes.

### Key Choices:

**1. Onboarding Depth: Operational Hotel (10-12 min)**
- Creates complete Hotel + RoomTypes + All Rooms + Policies
- Hotel can accept bookings immediately
- Stock photos (user can customize later)
- NOT production-ready with custom photos (that's 15-20 min)

**Why**: Fulfills "10 minute" promise while making hotel truly operational.

---

**2. Information Collection: Guided Questions**
- AI asks specific questions, one at a time
- User answers each question
- Validates in real-time
- NOT pure conversation (too error-prone)
- NOT hybrid (too complex for MVP)

**Why**:
- Reliable (95%+ accuracy vs 70% for pure conversation)
- Clear to user what's being collected
- Easier to test and debug
- Can evolve to hybrid in F-002.1

---

**3. AI Model: OpenAI GPT-4o**
- Use GPT-4o for structured data extraction
- JSON mode for reliable output
- $0.075 per onboarding (negligible vs $999/month revenue)
- NOT Claude (for MVP - may switch at scale)
- NOT self-hosted LLM (not worth complexity for MVP)

**Why**:
- Fast to implement
- Excellent structured output mode
- Proven reliability
- Cost is trivial compared to conversion value

---

**4. Timeline: Spec Now, Build After F-001.1**
- Create F-002 specification immediately (done)
- Developer builds F-001.1 first (10 hours)
- Then builds F-002 (42 hours)
- Total time: ~52 hours / 6.5 days

**Why**:
- Parallel work (architect specs while dev codes)
- F-002 depends on Organization model from F-001.1
- No blocked time

---

## Technical Architecture

```
Frontend: Django Template + HTMX (chat interface)
Backend: Django + OpenAI API (conversation engine)
State: Redis (session storage, 24hr TTL)
Data: F-001 models (Hotel, RoomType, Room, etc.)
```

**State Machine**: 5 states
1. HOTEL_BASICS → collect name, location, contact
2. ROOM_TYPES → collect room type details (can loop)
3. ROOM_INVENTORY → generate room numbers
4. POLICIES → check-in/out times, cancellation
5. REVIEW → show summary, confirm, create

---

## What Gets Created

After 10-minute onboarding, hotel has:
- ✅ Complete Hotel record
- ✅ All RoomTypes (with beds, amenities, pricing)
- ✅ All Room units (auto-numbered)
- ✅ Policies configured
- ✅ Stock photos
- ✅ Staff account (hotel owner)
- ✅ Can accept bookings

Does NOT have:
- ❌ Custom photos (can upload later)
- ❌ Integrations (Stripe, etc.)
- ❌ Additional staff

**Result**: Operational hotel, ready for first booking.

---

## Alternatives Considered

### Alternative 1: Minimal Setup (5-8 min)
- Only create hotel + basic room types
- NO individual rooms, photos, or policies
- User must "finish setup" later

**Rejected**: Breaks the promise of "ready to operate." Adds friction.

---

### Alternative 2: Production-Ready (15-20 min)
- Include custom photo upload
- Configure integrations
- Set up payment processing

**Rejected**: 15-20 min loses the "wow" of 10 minutes. Photos can be added later.

---

### Alternative 3: Pure Conversation (Magical AI)
- User describes hotel in natural language
- AI extracts everything in one shot

**Rejected**: Too error-prone (70% accuracy). Risky for production data.

---

## Success Metrics

- ✅ 10-12 minute completion time
- ✅ 90%+ completion rate (vs 40% industry)
- ✅ 95%+ data extraction accuracy
- ✅ <$0.10 AI cost per onboarding
- ✅ Zero support tickets for onboarding flow
- ✅ Positive user feedback

---

## Risks & Mitigations

**Risk 1: AI extraction errors**
- Mitigation: Validate each answer in real-time
- Mitigation: Use GPT-4o's structured output mode
- Mitigation: Allow user to review/edit before finalizing

**Risk 2: OpenAI API downtime**
- Mitigation: Add retry logic with exponential backoff
- Mitigation: Graceful degradation (save progress, resume later)
- Mitigation: Monitor uptime, have fallback to form mode

**Risk 3: Cost at scale**
- Mitigation: Monitor spend, set alerts
- Mitigation: Migrate to Claude (~5x cheaper) at 100+ hotels/month
- Mitigation: Self-host LLM at 1,000+ hotels/month

---

## Future Enhancements (F-002.1)

Post-MVP improvements:
1. Voice input (Whisper API) - speak instead of type
2. Hybrid conversation mode - long-form answers
3. Photo upload during onboarding - AI generates descriptions
4. Multi-language - onboard in Spanish, French, etc.
5. Smart defaults - infer pricing from location

---

## Business Impact

**Primary Differentiation**: 10x faster onboarding vs competitors

**Expected Outcomes**:
- Viral word-of-mouth ("Setup was so easy!")
- Higher conversion (90% vs 40%)
- Lower CAC (less support needed)
- Justifies premium pricing
- Creates "wow moment" for demos

**ROI**:
- Development: 42 hours
- Conversion lift: 2.25x (40% → 90%)
- Payback: First 20 customers

---

## Architect Notes

This is the **killer feature** - the one thing that makes Stayfull unique.

The 21 AI features are valuable, but F-002 is what gets hotels IN the door. Once they experience the magical 10-minute setup, they'll trust the platform with the rest of their operations.

Don't cut corners on UX. Make it delightful.

---

## References

- Specification: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
- Handoff: `.architect/handoffs/F-002_DEVELOPER_HANDOFF.md`
- Parent Feature: F-001 (PMS Core)
- Dependencies: F-001.1 (Organization model)

---

**Decision Maker**: User (Hotel Owner)
**Architect**: Approved
**Status**: ✅ Spec Complete, Ready to Build After F-001.1
