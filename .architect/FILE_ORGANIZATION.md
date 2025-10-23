# 📁 Stayfull File Organization Guidelines

**Version**: 1.0
**Owner**: Senior Product Architect
**Last Updated**: 2025-10-22

---

## 🎯 Purpose

Maintain a clean, organized codebase as Stayfull grows from 1 feature to 22 features.

---

## 📂 Root Directory Structure

### What BELONGS in Root:

#### Operational Scripts (Like Django's manage.py)
```
architect_commands.py     ✅ CLI for architect/developer mode switching
architect_recovery.py     ✅ Emergency context recovery
manage.py                 ✅ Django management (developer uses this)
```

**Rationale**: Quick access, parallel to Django's manage.py convention

#### Configuration Files
```
.env                      ✅ Environment variables (never commit!)
.gitignore               ✅ Git exclusions
pytest.ini               ✅ Test configuration
```

#### Directories
```
.architect/              ✅ All architect/planning files
apps/                    ✅ Django applications
config/                  ✅ Django settings
requirements/            ✅ Python dependencies
venv/                    ✅ Virtual environment (gitignored)
.git/                    ✅ Git repository
```

### What SHOULD NOT Be in Root:

```
❌ Documentation files (use .architect/docs/ or docs/)
❌ Scratch/temp files (use .architect/scratch/)
❌ Random Python scripts (organize into .architect/scripts/ or apps/)
❌ Test output (htmlcov/, .coverage - these are OK but gitignored)
❌ One-off setup scripts (archive after use)
```

---

## 🗂️ .architect/ Directory Structure

```
.architect/
├── ARCHITECTURE.md                    # System architecture
├── MASTER_CONTROL.md                  # 22-feature roadmap
├── CLAUDE_INTERFACE.md                # Architect identity/protocols
├── DEVELOPER_INTERFACE.md             # Developer identity/protocols
├── ARCHITECT_DEVELOPER_COMMS.md       # Communication log
├── FILE_ORGANIZATION.md               # This file
│
├── decisions/                         # Architecture Decision Records (ADRs)
│   ├── 001_*.md
│   ├── 002_*.md
│   └── ...
│
├── features/
│   ├── current/                       # Active feature specs
│   │   ├── F-001-*.spec.md
│   │   └── F-002-*.spec.md
│   └── archive/                       # Completed feature specs
│
├── handoffs/                          # Architect → Developer handoffs
│   ├── F-001-developer-handoff.md
│   ├── F-002-developer-handoff.md
│   └── ARCHITECT_TO_DEVELOPER_HANDOFF.md
│
├── memory/                            # Session persistence
│   ├── PERSISTENT_MEMORY.json         # Architect memory
│   ├── DEVELOPER_CONTEXT.json         # Developer memory
│   └── CONTEXT_HANDOFF.json           # Session handoffs
│
├── sprints/                           # Sprint tracking
│   ├── CURRENT_SPRINT.md
│   └── archive/
│       ├── SPRINT_01.md
│       └── ...
│
├── scripts/                           # Architect utility scripts
│   └── (future automation scripts)
│
└── scratch/                           # Temporary work
    └── (gitignored temp files)
```

---

## 🏗️ Django apps/ Directory Structure

```
apps/
├── core/                              # Shared utilities
│   ├── models.py                      # BaseModel
│   ├── mixins.py
│   └── utils.py
│
├── hotels/                            # F-001: Core PMS
│   ├── models.py                      # Hotel, RoomType, Room
│   ├── serializers.py
│   ├── views.py
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   ├── admin.py
│   └── factories.py
│
├── guests/                            # F-001: Guest management
├── reservations/                      # F-001: Reservations
├── staff/                             # F-001: Staff
│
├── ai_onboarding/                     # F-002: AI Onboarding Agent
├── commerce/                          # F-003: Dynamic Commerce
├── chatbot/                           # F-004: AI Chat Bot
│
└── integrations/                      # Third-party integrations
    ├── payments/
    │   └── stripe_adapter.py
    ├── iot/
    │   └── seam_adapter.py
    └── channels/
        └── channex_adapter.py
```

**Naming Convention**:
- Use underscores: `ai_onboarding` not `aiOnboarding`
- Keep names short but descriptive
- Match feature names from MASTER_CONTROL.md

---

## 🧪 Test Organization

```
apps/hotels/tests/
├── __init__.py
├── factories.py                       # pytest-factoryboy factories
├── test_models.py                     # Model tests
├── test_serializers.py                # Serializer tests
├── test_views.py                      # API endpoint tests
└── test_integration.py                # Integration tests
```

**Rules**:
- One test file per code file (test_models.py for models.py)
- Use descriptive test names: `test_hotel_slug_must_be_unique`
- Group tests by class: `TestHotelModel`, `TestRoomTypeModel`

---

## 📝 Documentation Organization

```
.architect/docs/                       # Architect documentation
├── api/                               # API documentation
├── deployment/                        # Deployment guides
└── onboarding/                        # New dev onboarding

# OR use root-level docs/ for public documentation
docs/                                  # Public documentation
├── api/
├── setup/
└── guides/
```

**Decision Needed**: Choose one approach (architect prefers .architect/docs/)

---

## 🚫 .gitignore Rules

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# Architect temporary files
.architect/scratch/

# IDE
.vscode/
.idea/
*.swp
```

---

## 🔄 Migration Files

```
apps/hotels/migrations/
├── __init__.py
├── 0001_initial.py
├── 0002_add_room_status.py
└── ...
```

**Rules**:
- ✅ Commit all migration files
- ✅ Use descriptive migration names (not auto-generated numbers only)
- ✅ Never edit migrations after committing
- ✅ Never delete migrations (unless reverting uncommitted work)

---

## 📦 Requirements Organization

```
requirements/
├── base.txt                           # Core dependencies (Django, DRF)
├── development.txt                    # Dev tools (pytest, black, etc.)
└── production.txt                     # Production-only (gunicorn, etc.)
```

**Usage**:
```bash
pip install -r requirements/development.txt  # Development
pip install -r requirements/production.txt   # Production
```

---

## 🎨 Static Files Organization (Future)

```
# When we add frontend later:
static/
├── css/
├── js/
└── images/

media/                                 # User uploads (gitignored)
└── hotel_images/
```

---

## 📋 File Naming Conventions

### Python Files
- Snake case: `ai_onboarding_agent.py`
- Test files: `test_*.py` prefix
- Factories: `factories.py`

### Markdown Files
- Title case: `ARCHITECTURE.md`, `MASTER_CONTROL.md`
- Feature specs: `F-001-stayfull-pms-core.spec.md`
- Handoffs: `F-001-developer-handoff.md`
- Decisions: `001_DECISION_NAME.md`

### JSON Files
- UPPERCASE: `PERSISTENT_MEMORY.json`, `CONTEXT_HANDOFF.json`

---

## 🧹 Cleanup Guidelines

### Monthly Review
- [ ] Move completed feature specs to `features/archive/`
- [ ] Move completed sprints to `sprints/archive/`
- [ ] Clean up `.architect/scratch/`
- [ ] Remove unused dependencies

### Per Feature Completion
- [ ] Archive feature spec
- [ ] Update MASTER_CONTROL.md
- [ ] Document lessons learned in feature spec
- [ ] Update DEVELOPER_CONTEXT.json

---

## ⚙️ Current Action Items

### Immediate (Based on Current State):

1. **Keep as-is:**
   - ✅ `architect_commands.py` in root (operational script)
   - ✅ `architect_recovery.py` in root (emergency access)
   - ✅ `.architect/` directory structure

2. **Decision Needed:**
   - ❓ `initialize_architect.py` - Still needed or archive?
     - **Recommendation**: Move to `.architect/scripts/archive/initialize_architect.py`
     - **Rationale**: Initial setup complete, keep for reference

3. **Add to .gitignore:**
   - ✅ Already done: `.coverage`, `htmlcov/`, `.pytest_cache/`

---

## 🎓 Principles

1. **Separation of Concerns**
   - Architect files in `.architect/`
   - Django code in `apps/`
   - Tests with code they test

2. **Discoverability**
   - New developers should find things easily
   - Clear naming conventions
   - Consistent structure

3. **Scalability**
   - Structure supports 22 features
   - Easy to add new apps
   - Archive completed work

4. **Clean Root**
   - Minimal files in root
   - Operational scripts only
   - Everything else organized

---

**Architect Signature**: Senior Product Architect
**Date**: 2025-10-22
**Status**: Active Guidelines - Update as Project Evolves
