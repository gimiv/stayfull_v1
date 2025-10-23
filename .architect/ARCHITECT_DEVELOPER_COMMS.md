# 🔄 Architect ↔️ Developer Communication Log

**Purpose**: Direct communication between architect and developer sessions
**Instructions**: Both roles update this file, user just notifies the other to check it

---

## Format:

```
## [ROLE] [TIMESTAMP] - [TOPIC]
**Message**: ...
**Status**: PENDING / ANSWERED / RESOLVED
```

---

## Active Communications

### [ARCHITECT] 2025-10-22 23:45 - Phase 3 Questions Answered

**Status**: ANSWERED - Ready to Proceed

**Developer Questions & Architect Responses:**

---

**Q1: Which Django encryption library should I use for Guest ID documents?**

**A**: Use **`django-cryptography`** (https://github.com/georgemarshall/django-cryptography)

**Rationale**:
- Built on Python's `cryptography` library (industry standard)
- Simple field-level encryption: `from django_cryptography.fields import encrypt`
- Transparent encryption/decryption (works like normal CharField)
- FIPS 140-2 compliant
- Active maintenance

**Implementation**:
```python
from django_cryptography.fields import encrypt

class Guest(BaseModel):
    id_document_number = encrypt(models.CharField(max_length=50, blank=True))
```

**Installation**: Add to `requirements/base.txt`:
```
django-cryptography>=1.1
```

**Key Management**: Use environment variable for encryption key:
```python
# .env
FIELD_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

---

**Q2: What permissions structure for Staff?**

**A**: Use a **flexible JSON structure** for future F-002+ features

**Recommended Structure**:
```python
# Staff.permissions (JSONField)
{
    "reservations": {
        "can_create": true,
        "can_view": true,
        "can_edit": true,
        "can_delete": false,
        "can_cancel": true
    },
    "guests": {
        "can_create": true,
        "can_view": true,
        "can_edit": true,
        "can_delete": false
    },
    "rooms": {
        "can_create": false,  # Only managers
        "can_view": true,
        "can_edit_status": true,  # Housekeeping
        "can_delete": false
    },
    "reports": {
        "can_view_financial": false,  # Only managers
        "can_view_operational": true
    },
    "settings": {
        "can_edit_hotel": false,  # Only managers
        "can_manage_staff": false  # Only managers
    }
}
```

**Role-Based Defaults**:

For now, implement a helper method to generate default permissions:

```python
class Staff(BaseModel):
    # ... fields ...

    def set_default_permissions_for_role(self):
        """Set default permissions based on role"""
        defaults = {
            'manager': {
                'reservations': {'can_create': True, 'can_view': True, 'can_edit': True, 'can_delete': True, 'can_cancel': True},
                'guests': {'can_create': True, 'can_view': True, 'can_edit': True, 'can_delete': True},
                'rooms': {'can_create': True, 'can_view': True, 'can_edit_status': True, 'can_delete': True},
                'reports': {'can_view_financial': True, 'can_view_operational': True},
                'settings': {'can_edit_hotel': True, 'can_manage_staff': True}
            },
            'receptionist': {
                'reservations': {'can_create': True, 'can_view': True, 'can_edit': True, 'can_delete': False, 'can_cancel': True},
                'guests': {'can_create': True, 'can_view': True, 'can_edit': True, 'can_delete': False},
                'rooms': {'can_create': False, 'can_view': True, 'can_edit_status': True, 'can_delete': False},
                'reports': {'can_view_financial': False, 'can_view_operational': True},
                'settings': {'can_edit_hotel': False, 'can_manage_staff': False}
            },
            'housekeeping': {
                'reservations': {'can_create': False, 'can_view': True, 'can_edit': False, 'can_delete': False, 'can_cancel': False},
                'guests': {'can_create': False, 'can_view': True, 'can_edit': False, 'can_delete': False},
                'rooms': {'can_create': False, 'can_view': True, 'can_edit_status': True, 'can_delete': False},
                'reports': {'can_view_financial': False, 'can_view_operational': True},
                'settings': {'can_edit_hotel': False, 'can_manage_staff': False}
            },
            'maintenance': {
                'reservations': {'can_create': False, 'can_view': True, 'can_edit': False, 'can_delete': False, 'can_cancel': False},
                'guests': {'can_create': False, 'can_view': False, 'can_edit': False, 'can_delete': False},
                'rooms': {'can_create': False, 'can_view': True, 'can_edit_status': True, 'can_delete': False},
                'reports': {'can_view_financial': False, 'can_view_operational': True},
                'settings': {'can_edit_hotel': False, 'can_manage_staff': False}
            }
        }
        self.permissions = defaults.get(self.role, {})
```

**For Phase 3**: Just implement the structure and the helper method. We'll use these permissions in F-002+ features.

---

**Additional Phase 3 Guidance:**

**Guest Model - Additional Requirements:**
- Add `full_name` property: `@property def full_name(self): return f"{self.first_name} {self.last_name}"`
- Add `__str__`: `return self.full_name`
- Default `account_status` to `"active"`
- Default `loyalty_points` to `0`

**Staff Model - Additional Requirements:**
- Add `__str__`: `return f"{self.user.get_full_name()} - {self.hotel.name} ({self.role})"`
- Override `save()` to call `set_default_permissions_for_role()` if permissions is empty
- Add `is_manager` property: `@property def is_manager(self): return self.role == 'manager'`

---

**YES - Proceed with Phase 3 (Guest & Staff models) now.**

Use the encryption library and permissions structure above.

**Architect Approval**: ✅ Ready to implement Phase 3

---

### [ARCHITECT] 2025-10-22 23:35 - Phase 2 Complete - Outstanding Work! 🎉

**Status**: RESOLVED - Moved to Archive

**Review of Phase 2 Deliverables**:
✅ **EXCEPTIONAL WORK** - Far exceeded expectations!

**Achievements**:
- 34/34 tests passing (target was 15+, you delivered 226%!)
- 98% overall coverage (target was 80%, you delivered 123%!)
- All 3 models (Hotel, RoomType, Room) fully implemented
- Django Admin configured with comprehensive settings
- Test factories created (best practice!)
- Admin tests added (proactive excellence!)
- Atomic commits maintained (clean git history)

**Architectural Review**:
✅ Hotel model: All business rules enforced
✅ RoomType model: Correct unique constraint (`hotel` + `code`)
✅ Room model: Proper multi-tenancy relationships
✅ Test coverage: Models 96%, Overall 98%

**Correction Noted & Approved**:
Good catch on RoomType using `code` not `name` for uniqueness per spec. This shows attention to detail.

---

**NEXT INSTRUCTIONS - Phase 3: Guest & Staff Models**

**Objective**: Implement Guest and Staff models with same TDD excellence

**Priority Order**:
1. Guest model (higher priority - used in reservations)
2. Staff model

**Guest Model Requirements** (from F-001 spec):

**Key Fields**:
- first_name, last_name, email (unique), phone
- date_of_birth, nationality, language_preference
- id_document_type, id_document_number (ENCRYPT THIS!)
- address (JSON), preferences (JSON)
- loyalty_points (integer, default 0)
- account_status (enum: active, inactive, blocked)

**Critical Business Rules**:
1. Email must be globally unique
2. `id_document_number` MUST be encrypted (use Django encryption library)
3. `loyalty_points` cannot be negative
4. `date_of_birth` validation: Guest must be 18+ years old
5. Phone should follow international format

**Security Note**:
Since we're dealing with PII (Personally Identifiable Information), ensure:
- `id_document_number` encrypted at field level
- Consider GDPR/data privacy implications
- Add `created_at`, `updated_at` via BaseModel

**Tests to Write** (minimum):
- Email uniqueness
- Encryption of id_document_number
- Age validation (18+)
- Loyalty points cannot be negative
- Account status transitions
- Guest __str__ method

**Staff Model Requirements**:

**Key Fields**:
- user (ForeignKey to Django User model)
- hotel (ForeignKey to Hotel)
- role (enum: manager, receptionist, housekeeping, maintenance)
- permissions (JSON)
- is_active (boolean)

**Critical Business Rules**:
1. One User can work at multiple hotels (many-to-many via Staff)
2. `unique_together = [['user', 'hotel']]` - user can't have duplicate Staff entries for same hotel
3. Role-based permissions for future features

**Tests to Write** (minimum):
- User can have multiple Staff entries (different hotels)
- Cannot create duplicate Staff (same user + hotel)
- Role assignment
- Permission management

---

**Estimated Time**: 1-2 days (based on your velocity, probably faster!)

**Expected Output**:
- 2 models (Guest, Staff)
- 12-15+ tests (following your high standards)
- Django Admin for both
- Test factories for both
- Migrations
- Atomic commits

**Questions/Clarifications Needed?**
- Guest encryption strategy (which Django encryption library?)
- Staff permissions structure (which permissions to include?)

**Proceed when ready!** 🚀

**Architect Signature**: Senior Product Architect

---

## Archive (Resolved)

### [ARCHITECT] 2025-10-22 23:10 - Phase 2 Approval

**Message**:
Hotel model implementation APPROVED. Excellent TDD work, all 9 tests passing.

**Instructions**:
1. Commit Hotel model now (atomic commits)
2. Proceed with RoomType model (TDD)
3. Key specs for RoomType:
   - `unique_together = [['hotel', 'name']]`
   - `base_price` must be positive
   - `max_occupancy >= 1`
   - Don't forget Django Admin registration

**Status**: RESOLVED

**Developer Response [2025-10-22 23:30]**:
✅ All instructions completed successfully!

**Completed Work**:
1. ✅ Hotel model committed (commit: 50209c6)
2. ✅ RoomType model implemented with TDD (6 tests)
3. ✅ Room model implemented with TDD (4 tests)
4. ✅ All models registered in Django Admin with comprehensive configurations
5. ✅ RoomType and Room models committed (commit: 41d4e30)
6. ✅ Created test factories using factory_boy for all 3 models (5 factory tests)
7. ✅ Created admin configuration tests (10 admin tests)

**Test Results**:
- Total: 34/34 tests passing
- Model coverage: 96%
- Overall coverage: 98%

**Test Breakdown**:
- 19 model tests (Hotel: 9, RoomType: 6, Room: 4)
- 5 factory tests
- 10 admin tests

**Note**: RoomType spec correction applied:
- Used `unique_together = [['hotel', 'code']]` (not 'name') per F-001 spec
- All business rules implemented and validated

---

## Developer → Architect Questions Queue

**How to use**:
Developer adds questions here, architect responds inline

### Example Format:
```
**Q**: Should RoomType.name be case-sensitive for uniqueness?
**Context**: Implementing unique_together constraint
**A**: (Architect will answer here)
```

---

## Architect → Developer Guidance Queue

**How to use**:
Architect adds guidance/clarifications here

### Example Format:
```
**Topic**: Multi-tenancy reminder
**Message**: Remember to filter by hotel_id in all RoomType queries
```

---

## Quick Status Updates

Developer can drop quick updates here without waiting for architect review:

### [DEVELOPER] 2025-10-22 23:55 - Phase 3 BLOCKER: Encryption Library Compatibility
**Status**: ⚠️ BLOCKER - Need architect guidance
**Progress**: Guest model 90% complete, 12 tests written (TDD)
**Issue**: Django 5.0 encryption library incompatibility

**Attempted Solutions**:
1. ❌ django-cryptography (1.1) - ImportError: `baseconv` removed in Django 4.0
2. ❌ django-fernet-fields (0.6) - ImportError: `force_text` renamed in Django 3.0

**Proposed Solution**:
Create custom EncryptedCharField using `cryptography` library directly (already installed)
- More control over encryption
- Direct Fernet encryption/decryption
- Compatible with Django 5.0
- Implementation: ~30 lines of code

**Question for Architect**:
Should I proceed with custom encryption field implementation, or would you prefer:
- Option A: Custom EncryptedCharField (recommended)
- Option B: Store encrypted in separate table
- Option C: Temporary: Use regular CharField, encrypt in Phase 4

**Current State**:
- Guest model fully written (all fields, validations, properties)
- 12 comprehensive tests written covering all business rules
- Just need encryption field working
- Can complete in 15-20 minutes with direction

**Awaiting guidance to unblock Phase 3** 🚦

---

### [DEVELOPER] 2025-10-22 23:45 - Starting Phase 3 (Guest & Staff)
**Status**: ✅ Acknowledged architect's Phase 3 instructions
**Current Task**: Implementing Guest & Staff models
**Approach**:
- Following TDD (tests first)
- Using django-cryptography for Guest ID encryption
- Implementing role-based permissions structure for Staff
- Will answer encryption/permissions questions inline as I implement

**Questions Answered**:
✅ Encryption: Using django-cryptography with environment-based key management
✅ Permissions: Using provided role-based JSON structure

**Starting now!** 🚀

---

### [DEVELOPER] 2025-10-22 23:30 - Phase 2 Complete
**Status**: Phase 2 (Hotel Models) fully implemented and tested
**Next Phase**: Ready for Phase 3 or next feature per architect's direction
**Commits**:
- 50209c6: Hotel model
- 41d4e30: RoomType and Room models
- 9284616: Test factories and admin tests
