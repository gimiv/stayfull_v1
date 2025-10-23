# 006: Explicit Documentation of Anthropic/Claude AI Principles

**Date**: 2025-10-23
**Status**: APPROVED
**Decision Maker**: Senior Product Architect (with user delegation)

---

## 🎯 Decision

Explicitly document Anthropic's Claude best practices within `.architect/CLAUDE_INTERFACE.md` to ensure consistent, high-quality AI reasoning across all architect sessions.

---

## 📊 Context

**User Question**: "Do you have all the Anthropic best principles built into your MD file?"

**Architect Assessment**:
- Existing docs had **role-specific** behaviors (be opinionated, enforce quality)
- Lacked **AI-specific** reasoning principles (chain-of-thought, uncertainty acknowledgment)
- Base Claude system prompts include these, but not explicitly documented in project
- Long-term project needs reproducible, consistent architect behavior

---

## 🤔 Options Considered

### Option A: Create New File `.architect/ANTHROPIC_PRINCIPLES.md`
**Pros**:
- Dedicated focus on AI principles
- Easy to update independently

**Cons**:
- Yet another file to read on startup
- Fragments documentation across files
- Maintenance burden (multiple sources of truth)

### Option B: Update Existing `CLAUDE_INTERFACE.md` ⭐ **CHOSEN**
**Pros**:
- ✅ Single source of truth for architect behavior
- ✅ Consolidates role + methodology
- ✅ Easy to reference on startup
- ✅ Maintains clean file structure

**Cons**:
- Longer file (acceptable trade-off)

### Option C: Don't Document (Rely on Base Prompts)
**Pros**:
- No redundancy
- Less to maintain

**Cons**:
- ❌ No transparency for team
- ❌ Harder to debug unexpected behavior
- ❌ No project-specific customization
- ❌ Future sessions may not be consistent

---

## ✅ Decision Rationale

**Why Option B**:

1. **Long-term project** (22 features, multi-year)
2. **Team transparency** - Developers/stakeholders should understand AI reasoning
3. **Consistency** - Explicit principles ensure reproducible behavior
4. **Debugging** - Reference point when behavior seems unexpected
5. **Already invested** - Robust `.architect/` system in place
6. **Single source** - All architect guidance in one place

---

## 📝 What Was Added

Added **8 AI Reasoning Principles** to `CLAUDE_INTERFACE.md`:

1. **Explicit Reasoning** - Chain-of-thought, step-by-step, rationale-first
2. **Acknowledge Uncertainty** - Be honest, quantify confidence, offer alternatives
3. **Avoid Hallucination** - Never invent, verify before stating, admit when checking
4. **Tool Use Strategy** - Read before editing, search before assuming, test before concluding
5. **Structured Communication** - Headings, code blocks, lists, visual separators
6. **Constitutional AI Alignment** - Helpful, harmless, honest
7. **Context & Memory Management** - Update tracking files, create handoffs, maintain continuity
8. **Error Handling** - Debug systematically, one change at a time, test after fixes

Plus:
- **Quality check** criteria for every response
- **Examples** of good vs bad practices
- **Application guidelines** for consistent behavior

---

## 🎯 Expected Outcomes

**Immediate**:
- ✅ Architect behavior explicitly documented
- ✅ Team understands AI reasoning methodology
- ✅ Future sessions have clear guidance

**Long-term**:
- ✅ Consistent architect behavior across sessions
- ✅ Easier onboarding for new team members
- ✅ Debugging reference when behavior unexpected
- ✅ Foundation for customizing AI behavior per project needs

---

## 📚 References

- Original file: `.architect/CLAUDE_INTERFACE.md` (lines 121-219)
- Anthropic's Claude best practices (implicit in base system prompts)
- Constitutional AI principles (helpful, harmless, honest)

---

## 🔄 Review & Updates

**Next Review**: When Anthropic releases new Claude best practices or guidelines

**Update Trigger**:
- Major Claude version updates
- Project team reports inconsistent architect behavior
- New AI reasoning patterns discovered

---

**Architect Decision**: ✅ Approved - This improves long-term project quality and team collaboration

**User Delegation**: "I'll take your guidance so you decide" - User trusted architect judgment

---

**Implementation**: Complete (2025-10-23)
**Lines Added**: ~100 lines to CLAUDE_INTERFACE.md
**Status**: ACTIVE - All future architect sessions will reference these principles
