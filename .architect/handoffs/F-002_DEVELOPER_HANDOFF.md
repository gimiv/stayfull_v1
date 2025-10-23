# Developer Handoff: F-002 AI Onboarding Agent

**Priority**: P1 - Killer Feature
**Effort**: 42 hours (~1 week)
**Status**: Spec Complete - Build After F-001.1
**Specification**: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
**Dependencies**: F-001.1 (Organization model) must be complete

---

## 🎯 What to Build

**10-minute AI-powered hotel onboarding** that replaces 60-90 minute manual forms with conversational Q&A.

**User Experience**:
1. User signs up → creates account
2. AI guides them through 5 conversation states
3. Hotel is operational in 10 minutes
4. Can accept first booking immediately

---

## 📋 Implementation Checklist

### Phase 1: Foundation (8 hours)
- [ ] Create `onboarding` Django app: `python manage.py startapp onboarding`
- [ ] Add to `INSTALLED_APPS` in settings
- [ ] Install Redis: `pip install redis hiredis`
- [ ] Configure Redis connection in settings
- [ ] Create `apps/onboarding/services/session_manager.py` (Redis CRUD)
- [ ] Create `apps/onboarding/services/state_machine.py` (5 states + transitions)
- [ ] Write tests for state machine (10+ tests)
- [ ] Run tests - ensure all pass

### Phase 2: AI Integration (10 hours)
- [ ] Install OpenAI: `pip install openai`
- [ ] Add `OPENAI_API_KEY` to `.env`
- [ ] Create `apps/onboarding/services/conversation_engine.py`
- [ ] Implement `OnboardingConversationEngine` class
- [ ] Create extraction prompts for each state (5 prompts)
- [ ] Implement `_extract_data_with_gpt4o()` method
- [ ] Implement validation logic `_validate_data()`
- [ ] Test extraction accuracy with sample messages
- [ ] Write 15+ tests for conversation engine
- [ ] Run tests - achieve 95%+ extraction accuracy

### Phase 3: Frontend Chat UI (8 hours)
- [ ] Create template: `apps/onboarding/templates/onboarding/chat.html`
- [ ] Install HTMX: Add to base template
- [ ] Create chat CSS (Tailwind)
- [ ] Add progress bar component
- [ ] Create message bubbles (AI vs User)
- [ ] Add auto-scroll to latest message
- [ ] Make mobile-responsive
- [ ] Test on desktop, tablet, mobile

### Phase 4: Data Generation (8 hours)
- [ ] Create `apps/onboarding/services/data_generator.py`
- [ ] Implement `OnboardingDataGenerator` class
- [ ] Implement `generate_hotel_from_session()` method
- [ ] Implement room number generation logic
- [ ] Add stock photo library (Unsplash URLs)
- [ ] Test bulk room creation (test with 200+ rooms)
- [ ] Verify all F-001 validations work
- [ ] Write 10+ tests for data generation

### Phase 5: Integration & Polish (8 hours)
- [ ] Create onboarding URL routes
- [ ] Create views for chat page and message endpoint
- [ ] Integrate with signup flow (redirect after account creation)
- [ ] Add success page with "Your hotel is ready!"
- [ ] Add error handling (AI timeout, validation errors)
- [ ] Add analytics tracking (onboarding completion rate)
- [ ] End-to-end testing (full onboarding flow)
- [ ] Load test (simulate 10 concurrent onboardings)
- [ ] Write documentation
- [ ] Deploy to Railway

---

## 🔑 Key Implementation Details

### State Machine Flow:
```
HOTEL_BASICS → ROOM_TYPES → ROOM_INVENTORY → POLICIES → REVIEW → COMPLETE
```

### Redis Session Key:
```python
SESSION_KEY = f"onboarding:{session_id}"
TTL = 86400  # 24 hours
```

### GPT-4o Configuration:
```python
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_object"},  # Force JSON
    temperature=0.1,  # Low for consistency
)
```

### Stock Photos:
Use Unsplash API or curated list of royalty-free images.

---

## 📚 Reference Files

**Full Specification**: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`

**Key Files to Create**:
- `apps/onboarding/services/session_manager.py` - Redis operations
- `apps/onboarding/services/state_machine.py` - State flow logic
- `apps/onboarding/services/conversation_engine.py` - GPT-4o integration
- `apps/onboarding/services/data_generator.py` - Create F-001 records
- `apps/onboarding/templates/onboarding/chat.html` - Chat UI
- `apps/onboarding/views.py` - Django views
- `apps/onboarding/urls.py` - URL routing

**Dependencies**:
```bash
pip install openai redis hiredis
```

**Environment Variables**:
```bash
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/0
```

---

## ✅ Definition of Done

- All 5 phases complete
- User can complete onboarding in 10-12 minutes
- Hotel is operational (can accept bookings)
- 95%+ data extraction accuracy
- 85%+ test coverage
- Mobile-responsive UI
- Deployed to Railway
- Documentation complete

---

## 🚀 Start After F-001.1

**DO NOT START** until F-001.1 (Organization model) is complete and deployed.

**When ready**:
1. Read full spec: `.architect/features/F-002_AI_ONBOARDING_AGENT.md`
2. Set up OpenAI API key
3. Start with Phase 1 (Foundation)
4. Ask architect if you have questions

**Target Completion**: 42 hours from start

---

**Good luck! This is the killer feature. 🚀**
