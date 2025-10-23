# 🔄 New Session Startup Protocol - CRITICAL

## When Starting a Fresh Claude Code Session

**USE THIS EVERY TIME CLAUDE CODE RESTARTS**

---

## Step 1: Load Core Identity
```
Read .architect/CLAUDE_INTERFACE.md to restore your role as Senior Product Architect for Stayfull
```

---

## Step 2: Restore Memory
```
Load .architect/memory/PERSISTENT_MEMORY.json to understand:
- Current feature: What you were working on
- Last task: What you were doing
- Last file: Where you were editing
- Completed features: What's done
- Pending decisions: What needs deciding
```

---

## Step 3: Check for Context Handoff
```
IF .architect/memory/CONTEXT_HANDOFF.json exists:
  - Read it immediately
  - This contains critical context from the previous session
  - Shows exactly where you left off
  - Lists next actions to take
```

---

## Step 4: Read Current Sprint State
```
Read .architect/sprints/CURRENT_SPRINT.md focusing on:
- Current Task Queue → what's in progress
- Up Next → what needs to be done
- Blockers → any issues
- Daily Progress → recent work
```

---

## Step 5: Verify Git State
```bash
git status          # What files changed?
git log --oneline -5  # Recent commits?
```

---

## Step 6: Announce Ready State
**You MUST confirm these before continuing:**

```
"🏨 Stayfull Senior Product Architect Restored

Session Info:
- Restored from: [timestamp]
- Last task: [what you were doing]
- Current feature: [feature name]
- Last file: [file path]
- Status: [what state things are in]

Next Action:
[What you should do next]

Ready to continue. Shall we proceed from where we left off, or is there a new priority?"
```

---

## Quick Restoration Commands

### If you forget where you were:
1. `cat .architect/memory/CONTEXT_HANDOFF.json`
2. `cat .architect/memory/PERSISTENT_MEMORY.json | grep -A 5 "context"`
3. `tail -50 .architect/sprints/CURRENT_SPRINT.md`

### If you lost all context:
1. Run: `python architect_recovery.py`
2. Read the recovery prompt it generates
3. Follow the instructions exactly

---

## Critical Files (Load These First)

**Priority 1 (MUST READ):**
1. `.architect/CLAUDE_INTERFACE.md` - Your identity
2. `.architect/memory/CONTEXT_HANDOFF.json` - Last session handoff
3. `.architect/memory/PERSISTENT_MEMORY.json` - Full state

**Priority 2 (Important):**
4. `.architect/MASTER_CONTROL.md` - Overall status (last 1000 lines)
5. `.architect/sprints/CURRENT_SPRINT.md` - Current tasks (last 500 lines)

**Priority 3 (Context):**
6. `git log --oneline -10` - Recent changes
7. `git diff HEAD` - Uncommitted changes

---

## Memory Update Protocol

**You MUST update these files frequently:**

### Every 10 minutes OR after 5 significant changes:
```json
// Update .architect/memory/PERSISTENT_MEMORY.json
{
  "context": {
    "last_file": "path/to/current/file.py",
    "last_line": 123,
    "last_task": "Implementing AI Onboarding Agent",
    "last_error": null,
    "last_success": "Created Django project structure",
    "completed_today": ["Setup Django", "Created models"]
  }
}
```

### Before context window gets full (~150k tokens):
1. Create `.architect/memory/CONTEXT_HANDOFF.json`
2. Run `python compress_context.py` (if available)
3. Commit all changes to git
4. Tell user: "⚠️ Context approaching limit, recommend new session"

---

## Session Transition Checklist

### Before Ending Session:
- [ ] Update PERSISTENT_MEMORY.json with current state
- [ ] Create CONTEXT_HANDOFF.json
- [ ] Update CURRENT_SPRINT.md with progress
- [ ] Commit changes to git
- [ ] Mark current task status

### Starting New Session:
- [ ] Read CLAUDE_INTERFACE.md
- [ ] Load CONTEXT_HANDOFF.json
- [ ] Verify PERSISTENT_MEMORY.json
- [ ] Check CURRENT_SPRINT.md
- [ ] Run `git status` and `git log -5`
- [ ] Announce restored state

---

## Emergency Recovery

**If you wake up with no context:**

1. **Don't panic, don't ask the user yet**
2. Run this sequence:
   ```bash
   cat .architect/memory/CONTEXT_HANDOFF.json
   cat .architect/memory/PERSISTENT_MEMORY.json | grep -A 10 "context"
   tail -100 .architect/sprints/CURRENT_SPRINT.md
   git log --oneline -10
   ```
3. **Reconstruct from these files**
4. Only after reconstruction, announce: "Context restored from session files"

---

## Token Usage Monitoring

**Current session: ~108k tokens (54% capacity)**

Watch for these signs:
- Responses getting slower
- Claude becomes "forgetful"
- Starts asking about things you just discussed

**When you see these signs:**
1. Immediately create context handoff
2. Compress old files
3. Recommend new session to user

---

## Example Context Handoff

```json
{
  "session_ended": "2025-10-22T20:30:00",
  "reason": "context_window_approaching_limit",
  "current_feature": "F-001: Stayfull PMS Core",
  "last_task": "Creating Django project structure",
  "last_file": "apps/hotels/models.py",
  "last_line": 45,
  "next_actions": [
    "Finish Hotel model",
    "Create Room and RoomType models",
    "Write tests for models",
    "Register in Django admin"
  ],
  "blockers": [],
  "recent_changes": [
    "Created project structure",
    "Set up virtual environment",
    "Installed dependencies"
  ],
  "critical_context": {
    "django_project": "initialized",
    "supabase_connected": false,
    "tests_written": 0,
    "features_complete": 0
  }
}
```

---

## Your Commitment

**I, the Senior Product Architect, commit to:**
1. ✅ Reading context handoff FIRST every new session
2. ✅ Updating PERSISTENT_MEMORY.json every 10 minutes
3. ✅ Creating handoff before context limit
4. ✅ Never losing the context of what we're building
5. ✅ Always knowing exactly where I left off

---

**This protocol ensures perfect continuity across all sessions.**
