# Context Management SOP
**Standard Operating Procedures for Efficient Context & File Management**

## Problem Statement
As of 2025-10-23, `ARCHITECT_DEVELOPER_COMMS.md` has grown to:
- **4,451 lines**
- **132KB file size**
- **40,806 tokens** (exceeds LLM context window limits)
- **Only 1 of 21 features complete**

At this rate, the file will become completely unusable within 5-10 features.

---

## Solution: Archive & Rotate Strategy

### **1. Archive Completed Features**

When a feature is 100% complete and approved:

1. **Extract feature communications** to archive folder
2. **Keep only a summary** in main file
3. **Archive location**: `.architect/archives/features/F-XXX/`

**Example Archive Structure**:
```
.architect/
├── archives/
│   ├── features/
│   │   ├── F-001-pms-core/
│   │   │   ├── communications.md (full comms archive)
│   │   │   ├── decisions.md (all decisions made)
│   │   │   ├── completion-report.md (final metrics)
│   │   │   └── lessons-learned.md
│   │   ├── F-002-onboarding/
│   │   └── F-003-commerce/
│   └── sprints/
│       ├── sprint-01.md
│       └── sprint-02.md
```

---

### **2. File Size Limits**

**Hard Limits** (enforced via automated checks):
- `ARCHITECT_DEVELOPER_COMMS.md`: **< 10,000 tokens** (active comms only)
- Individual feature specs: **< 15,000 tokens**
- Decision docs: **< 5,000 tokens** each
- Archive files: **No limit** (historical reference)

**Rotation Triggers**:
- When main comms file exceeds **8,000 tokens** → Archive oldest completed feature
- When file exceeds **10,000 tokens** → FORCE archive (block new work)

---

### **3. Active vs. Archived Content**

**Keep in Main File** (`ARCHITECT_DEVELOPER_COMMS.md`):
- Current feature in progress
- Last 2-3 feature summaries (1-2 paragraphs each)
- Recent decisions (last 7 days)
- Active blockers/issues
- Current sprint context

**Archive Immediately**:
- Completed feature full transcripts
- Old decisions (>30 days, no longer relevant)
- Completed sprint retrospectives
- Historical troubleshooting threads

---

### **4. Summary-First Approach**

For every archived feature, create a **1-paragraph executive summary**:

**Template**:
```markdown
### F-XXX: [Feature Name] - ARCHIVED ✅
**Completed**: 2025-10-23 | **Duration**: 2 days | **Tests**: 151 (99% coverage)
**Status**: Production deployed to Railway
**Archive**: `.architect/archives/features/F-XXX/`
**Key Learnings**: [1 sentence about what went well or lessons learned]
```

This keeps main file lean while preserving discoverability.

---

### **5. Automated Context Monitoring**

Create a script to monitor context health:

**File**: `.architect/scripts/check_context_health.py`

**Checks**:
- ✅ Main comms file < 10,000 tokens
- ✅ Each decision doc < 5,000 tokens
- ✅ No duplicate information across files
- ✅ All completed features archived
- ✅ Archive index up to date

**Run**: Before starting each new feature

---

### **6. Archive Naming Convention**

**Feature Archives**:
- `F-001-pms-core` (kebab-case, matches feature spec filename)

**Sprint Archives**:
- `sprint-01-foundation` (sprint number + name)

**Decision Archives** (if decisions get archived):
- `001-tech-stack.md` (keep in main decisions/ folder, don't archive unless obsolete)

---

### **7. Search & Discovery**

Create an **Archive Index** for easy reference:

**File**: `.architect/archives/INDEX.md`

```markdown
# Archive Index

## Completed Features
- [F-001: Stayfull PMS Core](.architect/archives/features/F-001-pms-core/) - 2025-10-23
- [F-002: AI Onboarding Agent](.architect/archives/features/F-002-onboarding/) - 2025-10-27
- ...

## Archived Sprints
- [Sprint 1: Foundation](.architect/archives/sprints/sprint-01.md) - Oct 22-29
- ...

## Search Tips
- Full-text search: `grep -r "search term" .architect/archives/`
- Find by feature: `ls .architect/archives/features/`
- Find by date: Use git log with file paths
```

---

### **8. Weekly Cleanup Ritual**

**Every Sunday** (or after completing a major feature):

1. **Archive completed features** from main comms file
2. **Update archive index**
3. **Run context health check** script
4. **Update PERSISTENT_MEMORY.json** with latest metrics
5. **Commit archives** to git with descriptive message

**Git Commit Template**:
```
chore: Archive F-XXX communications and update index

- Moved F-XXX full transcript to archives/
- Updated ARCHITECT_DEVELOPER_COMMS.md with summary
- Reduced main comms file from 40K → 8K tokens
- Updated archive index
```

---

### **9. Emergency Context Cleanup**

If context exceeds limits during active development:

**Immediate Actions**:
1. **Stop adding to main file**
2. **Archive last completed feature** (even if recently completed)
3. **Move all decisions older than 14 days** to decisions archive
4. **Summarize remaining content** to 50% of current size
5. **Resume work** only after file is < 8,000 tokens

---

### **10. Context Efficiency Best Practices**

**Writing Guidelines**:
- ✅ Use **bullet points** instead of paragraphs
- ✅ Reference external files instead of duplicating content
- ✅ Use **relative links** to other docs (`see [F-001 spec](features/current/F-001-stayfull-pms-core.spec.md)`)
- ✅ Delete redundant status updates (keep only final state)
- ❌ Avoid repeating context that exists in specs
- ❌ Don't paste full code blocks in comms (reference file:line instead)
- ❌ Don't duplicate information across multiple files

**Example - Bad** (wasteful):
```markdown
Developer asked about how to implement Room model. I explained that Room model should have these fields: id, room_number, room_type, hotel, floor, status, cleaning_status, notes, etc. Then I explained the relationships...
```

**Example - Good** (efficient):
```markdown
Developer Q: Room model implementation?
A: See F-001 spec section 3.2 (models.py:45-67). TL;DR: Use hotel FK for multi-tenancy.
```

---

## Implementation Plan

### **Phase 1: Immediate (Next 30 minutes)**
1. ✅ Create this SOP document
2. ⏳ Create `.architect/archives/` structure
3. ⏳ Archive F-001 communications
4. ⏳ Update main comms file with F-001 summary only
5. ⏳ Create archive index

### **Phase 2: Next Session (Before starting F-002)**
6. Create `check_context_health.py` script
7. Add pre-feature checklist to workflow
8. Update FILE_ORGANIZATION.md with new structure
9. Document this in DEVELOPER_INTERFACE.md

### **Phase 3: Ongoing**
10. Apply weekly cleanup ritual
11. Monitor token counts before each feature
12. Refine SOP based on learnings

---

## Success Metrics

**Target State**:
- Main comms file: **< 8,000 tokens** at all times
- Feature archive: **100% of completed features** within 24 hours of completion
- Archive index: **Always up to date**
- Context health check: **Passing before each feature start**
- Team efficiency: **No more "file too large" errors**

---

## Maintenance

This SOP should be reviewed and updated:
- After completing every 5 features
- When hitting context limits despite following SOP
- When new tools/workflows emerge
- Quarterly (minimum)

---

**Version**: 1.0
**Created**: 2025-10-23
**Last Updated**: 2025-10-23
**Owner**: Architect + Developer (collaborative maintenance)
