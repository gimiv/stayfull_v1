# Workflow Analysis: OneRedOak Patterns for Stayfull

**Source**: https://github.com/OneRedOak/claude-code-workflows
**Date**: 2025-10-23
**Purpose**: Extract and adapt review workflows for Stayfull development

---

## Executive Summary

OneRedOak implements a **dual-loop architecture** combining:
1. **Inner Loop**: Slash commands + subagents for iterative development
2. **Outer Loop**: GitHub Actions for automated PR validation

Their three workflows (code review, security review, design review) share common patterns we can adapt to Stayfull's Django/Python/hospitality PMS context.

---

## 1. Code Review Workflow

### What They Check

**Automated Checks:**
- ✅ Syntax validation
- ✅ Completeness
- ✅ Style guide adherence
- ✅ Bug detection
- ✅ Architectural alignment

**Human-Reserved:**
- ⚠️ Business logic soundness
- ⚠️ Strategic architectural decisions

### Implementation Pattern

**Dual-Loop Architecture:**
```
Inner Loop (Development):
├─ Slash commands: /review
├─ Subagents: @agent-code-reviewer
└─ Iterative feedback during coding

Outer Loop (Validation):
├─ GitHub Actions on every PR
├─ Automated inline comments
└─ Pre-merge quality gates
```

### Adaptation for Stayfull

**What We'll Check:**
- ✅ Python/Django syntax (PEP 8, Django conventions)
- ✅ F-001 model validation rules
- ✅ Multi-tenancy isolation (critical security)
- ✅ Database query optimization (N+1 queries)
- ✅ Hotel domain logic correctness
- ✅ API security (authentication, authorization)

**Stayfull-Specific Standards:**
- Organization-level data isolation (no cross-hotel leaks)
- PMS domain validations (occupancy rules, pricing logic)
- Stripe/Airbnb UX pattern adherence
- F-001 through F-021 feature consistency

**Implementation:**
```bash
# Slash command
/code-review

# Checks:
# 1. Django model validators present?
# 2. Organization filter on all queries?
# 3. Follows Stripe UI patterns (admin) or Airbnb (consumer)?
# 4. Test coverage >80%?
# 5. No hardcoded secrets?
```

---

## 2. Security Review Workflow

### What They Check

**OWASP Top 10 Focus:**
- Exposed secrets and credentials
- Potential attack vectors
- Known dependency vulnerabilities
- Sensitive information exposure

**Severity Classification:**
- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Low

### Adaptation for Stayfull

**Hospitality PMS-Specific Threats:**

**🔴 Critical:**
- Cross-hotel data leakage (Organization isolation broken)
- Credit card data exposure (PCI compliance)
- Guest PII exposure (GDPR/CCPA)
- Authentication bypass (hotel staff access)

**🟠 High:**
- SQL injection in booking queries
- XSS in guest-facing forms
- CSRF on payment endpoints
- Insecure API key storage (Stripe, OpenAI)

**🟡 Medium:**
- Rate limiting missing (brute force attacks)
- Session timeout too long
- Verbose error messages (info disclosure)
- Missing HTTPS enforcement

**🟢 Low:**
- Outdated dependencies (non-critical)
- Missing security headers
- Weak password requirements

**Stayfull Security Checklist:**
```python
# Multi-Tenancy Isolation
✓ All queries filter by Organization?
✓ Row-level security enforced?
✓ No cross-hotel data in API responses?

# PII Protection
✓ Guest data encrypted at rest?
✓ PII redacted in logs?
✓ GDPR compliance (right to deletion)?

# Payment Security
✓ Stripe keys in environment variables?
✓ No credit card storage (PCI scope reduced)?
✓ Payment webhooks verified?

# Authentication
✓ JWT tokens expire?
✓ Password hashing (bcrypt/Argon2)?
✓ MFA available for hotel staff?

# API Security
✓ Rate limiting on all endpoints?
✓ CORS configured correctly?
✓ Input validation on all forms?
```

**Implementation:**
```bash
# Slash command
/security-review

# Automated GitHub Action
# Runs on every PR touching:
# - apps/hotels/models.py (multi-tenancy)
# - apps/bookings/views.py (payment handling)
# - apps/auth/* (authentication)
```

---

## 3. Design Review Workflow

### What They Check

**Standards:**
- Visual hierarchy
- Accessibility (WCAG AA+)
- Responsive design
- Interaction patterns

**Reference Implementations:**
- Stripe (admin interfaces)
- Airbnb (consumer interfaces)
- Linear (productivity tools)

**Automation:**
- Playwright MCP for browser testing
- Live UI interaction testing (not just static code)

### Adaptation for Stayfull

**Design Principles Established:**
1. **Hotel Admin (Stripe-style)**: Clean, minimal, professional dashboards
2. **Guest Booking (Airbnb-style)**: Visual, card-based, mobile-first

**Stayfull Design Checklist:**

**For Admin Interfaces (F-002, Dashboard, Reports):**
```
✓ Follows Stripe's component patterns?
  - Tables: sortable, filterable, searchable
  - Forms: inline validation, helpful errors
  - Modals: centered, escape to close
  - Navigation: left sidebar, top search

✓ Typography: System font stack (SF Pro/Inter)
✓ Colors: Blue primary, gray neutral, red error, green success
✓ Spacing: 8px grid system
✓ Loading states: Skeleton screens
✓ Empty states: Helpful illustrations + CTAs
```

**For Consumer Interfaces (F-003, Booking Engine):**
```
✓ Follows Airbnb's patterns?
  - Listing cards: large photos, clear pricing
  - Search/filters: sticky search, filter chips
  - Booking flow: step-by-step, summary sidebar
  - Mobile-first: thumb-friendly, bottom sheets

✓ Typography: Warm, approachable (Airbnb Cereal-like)
✓ Colors: Warm palette (red/coral primary)
✓ Photos: Full-width hero, gallery modal
✓ Trust signals: Reviews, ratings, cancellation policy
```

**Accessibility (Both):**
```
✓ WCAG AA compliance
✓ Keyboard navigation works
✓ Screen reader tested
✓ Color contrast >4.5:1
✓ Focus indicators visible
✓ Form labels present
```

**Implementation:**
```bash
# Slash command
/design-review

# Checks:
# 1. Component matches Stripe (admin) or Airbnb (consumer)?
# 2. WCAG AA compliant?
# 3. Mobile responsive?
# 4. Loading states present?
# 5. Error states handled?
```

**Playwright Test Example:**
```python
# Test: Nora chat interface (F-002)
# Should match: Stripe's clean, minimal chat aesthetic

def test_nora_chat_ui(page):
    page.goto('/onboarding/')

    # Visual hierarchy
    assert page.locator('.progress-bar').is_visible()
    assert page.locator('.chat-messages').is_visible()

    # Interaction
    page.fill('input[name="message"]', 'sunsetvilla.com')
    page.click('button:has-text("Send")')

    # Loading state
    assert page.locator('.loading-spinner').is_visible()

    # Response appears
    page.wait_for_selector('.message.ai')
    assert 'Scanning' in page.inner_text('.message.ai')
```

---

## 4. Documentation Pattern: CLAUDE.md

### What They Use

**CLAUDE.md files** store project-specific context:
- Design system standards
- Coding conventions
- Business rules
- Review criteria

**Why It Matters:**
Claude Code always references these files for consistent context.

### Adaptation for Stayfull

**We Already Have This!**
`.architect/` directory structure serves this purpose:

```
.architect/
├── features/          # F-001 through F-021 specs
├── decisions/         # Architecture decision records
├── handoffs/          # Developer handoff docs
├── memory/            # Context files
└── workflows/         # THIS FILE + review templates
```

**What We'll Add:**
```
.architect/workflows/
├── CODE_REVIEW.md           # Python/Django standards
├── SECURITY_REVIEW.md       # PMS threat model
├── DESIGN_REVIEW.md         # Stripe/Airbnb patterns
└── WORKFLOW_ANALYSIS.md     # This document
```

**Plus Slash Commands:**
```
.claude/commands/
├── code-review.md
├── security-review.md
└── design-review.md
```

---

## 5. Implementation Plan for Stayfull

### Phase 1: Documentation (Now - Before Development)

**Create Review Standards:**
- [ ] `.architect/workflows/CODE_REVIEW.md`
  - Python/Django best practices
  - F-001 model validation rules
  - Multi-tenancy patterns
  - Test coverage requirements

- [ ] `.architect/workflows/SECURITY_REVIEW.md`
  - PMS threat model
  - OWASP Top 10 for hospitality
  - Multi-tenancy security checklist
  - PII protection requirements

- [ ] `.architect/workflows/DESIGN_REVIEW.md`
  - Stripe component library (admin)
  - Airbnb patterns (consumer)
  - Accessibility standards
  - Responsive breakpoints

**Create Slash Commands:**
- [ ] `/code-review` - Instant PR-style review
- [ ] `/security-review` - Threat analysis
- [ ] `/design-review` - UI/UX validation

### Phase 2: Automation (After F-002 Development)

**GitHub Actions:**
- [ ] `.github/workflows/code-review.yml`
  - Runs on every PR
  - Django linting (flake8, black, isort)
  - Test coverage check (>80%)
  - Multi-tenancy pattern validation

- [ ] `.github/workflows/security-review.yml`
  - Runs on PRs touching sensitive code
  - Secret scanning (detect hardcoded keys)
  - Dependency vulnerability check (safety, pip-audit)
  - SQL injection pattern detection

- [ ] `.github/workflows/design-review.yml`
  - Runs on PRs with template changes
  - Playwright visual regression tests
  - Accessibility audit (axe-core)
  - Mobile responsive check

### Phase 3: Continuous Improvement (Ongoing)

**Learning Loop:**
- Track common issues caught in reviews
- Update standards based on real bugs
- Refine threat model as features ship
- Expand Playwright test coverage

---

## 6. Key Takeaways

### What Works for Stayfull

✅ **Dual-Loop Architecture**
- Inner loop (slash commands) = Fast iteration during development
- Outer loop (GitHub Actions) = Consistent quality gates

✅ **Severity Classification**
- Critical/High/Medium/Low makes prioritization clear
- Especially important for security issues

✅ **Design System Reference**
- "Use Stripe patterns" is clearer than subjective design feedback
- "Use Airbnb patterns" for consumer UX
- Removes ambiguity from reviews

✅ **Automated + Human**
- AI handles routine checks (syntax, style, patterns)
- Humans focus on business logic and architecture

### What We'll Adapt

🔧 **PMS-Specific Security**
- Multi-tenancy isolation is our #1 threat
- PII protection (guest data)
- PCI compliance (payment handling)

🔧 **Hospitality Domain Validation**
- Occupancy rules
- Pricing logic
- Booking state machines
- Hotel operational constraints

🔧 **Reference Implementations**
- Stripe (not generic admin templates)
- Airbnb (not generic booking sites)
- Specific, actionable guidance

---

## 7. Success Metrics

**Code Quality:**
- Test coverage >80%
- Zero critical security issues in production
- <10 design revision requests per feature

**Development Speed:**
- Reviews complete in <24 hours
- Developers self-correct before PR (inner loop works)
- Fewer back-and-forth cycles

**Security:**
- Zero data leakage incidents
- Zero PCI compliance violations
- All OWASP Top 10 mitigated

**UX Consistency:**
- Admin interfaces match Stripe aesthetic
- Consumer interfaces match Airbnb patterns
- WCAG AA compliance on all pages

---

## 8. Next Steps

**Immediate (This Session):**
1. ✅ Analyze OneRedOak workflows (DONE)
2. Create `.architect/workflows/CODE_REVIEW.md`
3. Create `.architect/workflows/SECURITY_REVIEW.md`
4. Create `.architect/workflows/DESIGN_REVIEW.md`
5. Document Stripe/Airbnb design principles

**Before F-002 Development:**
1. Create slash commands in `.claude/commands/`
2. Review with user for approval
3. Developer references during build

**After F-002 UAT:**
1. Set up GitHub Actions
2. Run first automated reviews
3. Refine based on false positives/negatives

---

## 9. References

- **Source Repo**: https://github.com/OneRedOak/claude-code-workflows
- **Stripe Design**: https://stripe.com/docs/development
- **Airbnb Design**: https://airbnb.design/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **WCAG AA**: https://www.w3.org/WAI/WCAG2AA-Conformance

---

**Status**: Analysis Complete - Ready to Create Review Templates
**Next**: Build `.architect/workflows/CODE_REVIEW.md` based on this analysis
