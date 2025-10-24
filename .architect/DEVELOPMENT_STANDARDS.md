# Stayfull Development Standards

**Purpose**: Essential guidelines for building production-ready PMS software
**Audience**: Developers, architect (for reviews)
**Status**: Active - Reference during all development

---

## 1. Security Essentials (Non-Negotiable)

### Multi-Tenancy Isolation (Critical)
```python
# ✅ ALWAYS filter by Organization
hotels = Hotel.objects.filter(organization=request.user.organization)

# ❌ NEVER query without Organization filter
hotels = Hotel.objects.all()  # Data leakage risk!
```

**Checklist:**
- [ ] All model queries filter by `organization`?
- [ ] API endpoints validate Organization ownership?
- [ ] No cross-hotel data in responses?

### PII Protection
- [ ] Guest data encrypted at rest (Django's `EncryptedField`)
- [ ] PII redacted in logs (`email → e***@***.com`)
- [ ] GDPR compliance (data deletion endpoints exist)

### Payment Security
- [ ] Stripe keys in environment variables (never hardcoded)
- [ ] No credit card storage (PCI scope minimized)
- [ ] Payment webhooks verify signatures

### Authentication
- [ ] Passwords hashed (Django default: PBKDF2)
- [ ] JWT tokens expire (24-hour max)
- [ ] Rate limiting on login endpoints

---

## 2. Design Principles

### ⚠️ **CRITICAL: Accessibility First**

**All features must follow senior-friendly design standards.**

**Target User**: 60-year-old independent innkeeper with high school diploma

**Reference Documents**:
- **`.architect/ACCESSIBILITY_STANDARDS.md`** - Complete accessibility guide (READ THIS FIRST)
- **`.architect/QUICK_ACCESSIBILITY_REFERENCE.md`** - Quick reference card (print and keep visible)

**Non-Negotiable Minimums**:
- Body text: 17px minimum
- Buttons: 56px tall minimum, 18px text
- Touch targets: 56x56px minimum
- Color contrast: 7:1 ratio (WCAG AAA)
- Language: 8th-grade reading level, no jargon
- Button text: Specific actions (never "Submit" or "OK")

**The Innkeeper Test**: Can a 60-year-old use it without help?
- If NO → Redesign before shipping

---

### Admin Interfaces (Hotel Users)
**Reference**: Stripe Dashboard (with accessibility enhancements)

**Components:**
- Tables: Sortable, filterable, searchable
- Forms: Inline validation, helpful errors
- Modals: Centered, escape to close, clear actions
- Navigation: Left sidebar, top search bar
- Colors: Blue primary, gray neutral, red error, green success
- Typography: System font (SF Pro/Inter)
- Spacing: 8px grid system

### Consumer Interfaces (Guests)
**Reference**: Airbnb

**Components:**
- Listing cards: Large photos, clear pricing, ratings
- Search/filters: Sticky search, filter chips
- Booking flow: Step-by-step, summary sidebar
- Mobile-first: Thumb-friendly, bottom sheets
- Colors: Warm palette (red/coral primary)
- Typography: Approachable, clear hierarchy
- Trust signals: Reviews, cancellation policy, host info

### Accessibility (Both)
- [ ] WCAG AA compliance (contrast >4.5:1)
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] Form labels present

---

## 3. Django Best Practices

### Models
```python
# ✅ Use validators
max_occupancy = models.IntegerField(
    validators=[MinValueValidator(1)]
)

# ✅ Override clean() for complex validation
def clean(self):
    if self.max_adults > self.max_occupancy:
        raise ValidationError("Max adults cannot exceed occupancy")

# ✅ Add help_text
name = models.CharField(
    max_length=100,
    help_text="Room type name (e.g., 'Deluxe Suite')"
)
```

### Queries
```python
# ✅ Use select_related for ForeignKeys (avoid N+1)
rooms = Room.objects.select_related('hotel', 'room_type').all()

# ✅ Use prefetch_related for ManyToMany
hotels = Hotel.objects.prefetch_related('room_types').all()

# ✅ Bulk operations for performance
Room.objects.bulk_create(rooms_list)
```

### Views
```python
# ✅ Use Django's built-in views
from django.views.generic import ListView, CreateView

# ✅ Add permission checks
from django.contrib.auth.mixins import LoginRequiredMixin

# ✅ Filter by Organization
def get_queryset(self):
    return Hotel.objects.filter(
        organization=self.request.user.organization
    )
```

### Testing
- [ ] Test coverage >80%
- [ ] Test multi-tenancy isolation
- [ ] Test model validators
- [ ] Test edge cases (occupancy rules, pricing logic)

---

## 4. Code Quality

### Style
- Use `black` for formatting (PEP 8)
- Use `isort` for import sorting
- Use `flake8` for linting
- Max line length: 100 characters

### Naming
```python
# ✅ Clear, descriptive names
def calculate_total_price_with_taxes(base_rate, tax_rate, nights):
    return base_rate * nights * (1 + tax_rate)

# ❌ Cryptic abbreviations
def calc_tot(br, tr, n):
    return br * n * (1 + tr)
```

### Comments
```python
# ✅ Explain WHY, not WHAT
# Use ceiling division to ensure minimum 1-day charge
days = math.ceil(hours / 24)

# ❌ State the obvious
# Add 1 to x
x = x + 1
```

---

## 5. Git Workflow

### Commits
```bash
# ✅ Clear, descriptive messages
git commit -m "fix: Prevent cross-hotel data leakage in Room query

- Add Organization filter to Room.objects.filter()
- Add test for multi-tenancy isolation
- Fixes #42"

# ❌ Vague messages
git commit -m "fix stuff"
```

### Branches
```bash
# Feature branches
git checkout -b feature/f-002-nora-chat-ui

# Bug fixes
git checkout -b fix/room-occupancy-validation

# Hotfixes
git checkout -b hotfix/security-organization-leak
```

---

## 6. When to Ask Architect

**Ask Before Building:**
- ⚠️ New model or major schema change
- ⚠️ New external API integration
- ⚠️ New UI pattern not in Stripe/Airbnb
- ⚠️ Security-sensitive code (auth, payments)
- ⚠️ Performance concern (complex queries)

**Don't Need to Ask:**
- ✅ Following established patterns
- ✅ Writing tests
- ✅ Fixing obvious bugs
- ✅ Styling per Stripe/Airbnb guidelines
- ✅ Adding help_text or comments

---

## 7. Definition of Done

Before marking task complete:
- [ ] Code written and tested locally
- [ ] Tests written (>80% coverage for new code)
- [ ] Multi-tenancy validated (if applicable)
- [ ] Follows design principles (Stripe or Airbnb)
- [ ] No hardcoded secrets
- [ ] Documentation updated (if public API)
- [ ] Architect reviewed (for major features)

---

## Quick Reference

**Security Checklist:**
1. Organization filter? ✓
2. PII encrypted? ✓
3. Secrets in env vars? ✓
4. Payment security? ✓

**Design Checklist:**
1. Stripe pattern (admin) or Airbnb (consumer)? ✓
2. WCAG AA compliant? ✓
3. Mobile responsive? ✓
4. Loading/error states? ✓

**Code Checklist:**
1. Models have validators? ✓
2. Queries use select_related? ✓
3. Tests written? ✓
4. Black/isort/flake8 pass? ✓

---

**Last Updated**: 2025-10-23
**Version**: 1.0 - MVP Standards
**Next Review**: After F-002 ships to production
