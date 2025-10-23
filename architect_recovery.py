#!/usr/bin/env python3
"""
Stayfull Architect Recovery Script
Recovers architect state after context loss
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime


def recover_state():
    """Attempt to recover the last known good state"""
    architect_home = Path(".architect")

    print("🔄 Attempting Stayfull Architect Recovery...")
    print("=" * 60)

    # 1. Check git for last commits
    print("\n📝 Recent Git Activity:")
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except:
        print("   (No git history found)")

    # 2. Check for handoff file
    handoff_file = architect_home / "memory" / "CONTEXT_HANDOFF.json"
    if handoff_file.exists():
        print("\n🤝 Found Context Handoff:")
        print("-" * 60)
        handoff = json.loads(handoff_file.read_text())
        print(f"   Session ended: {handoff.get('session_ended')}")
        print(f"   Feature: {handoff.get('current_feature')}")
        print(f"   Last task: {handoff.get('last_task')}")
        print(f"   Status: {handoff.get('status')}")
        print(f"\n   Next Actions:")
        for i, action in enumerate(handoff.get("next_actions", [])[:5], 1):
            print(f"     {i}. {action}")
        print(f"\n   Blockers: {handoff.get('blockers') or 'None'}")
    else:
        print("\n⚠️  No context handoff found")

    # 3. Check persistent memory
    memory_file = architect_home / "memory" / "PERSISTENT_MEMORY.json"
    if memory_file.exists():
        print("\n🧠 Persistent Memory:")
        print("-" * 60)
        memory = json.loads(memory_file.read_text())
        context = memory.get("context", {})
        print(f"   Last file: {context.get('last_file')}")
        print(f"   Last task: {context.get('last_task')}")
        print(f"   Last success: {context.get('last_success')}")
        print(f"\n   Completed today:")
        for item in context.get("completed_today", []):
            print(f"     ✓ {item}")
    else:
        print("\n⚠️  No persistent memory found")

    # 4. Check current sprint
    sprint_file = architect_home / "sprints" / "CURRENT_SPRINT.md"
    if sprint_file.exists():
        print("\n🏃 Current Sprint Status:")
        print("-" * 60)
        sprint_content = sprint_file.read_text()
        # Extract in-progress tasks
        lines = sprint_content.split("\n")
        in_progress = False
        for line in lines:
            if "In Progress" in line:
                in_progress = True
            elif in_progress and line.startswith("###"):
                break
            elif in_progress and line.strip():
                print(f"   {line}")

    # 5. Check working directory
    print("\n📂 Working Directory:")
    print("-" * 60)
    try:
        result = subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("   (Working directory clean)")
    except:
        print("   (Not a git repository)")

    # 6. Generate recovery prompt
    print("\n" + "=" * 60)
    print("💊 RECOVERY PROMPT FOR CLAUDE CODE:")
    print("=" * 60)
    print(
        """
I need to restore my context as the Stayfull Senior Product Architect.

Please execute this restoration sequence:

1. Read .architect/CLAUDE_INTERFACE.md (loads my identity and protocols)
2. Read .architect/memory/CONTEXT_HANDOFF.json (critical last session state)
3. Load .architect/memory/PERSISTENT_MEMORY.json (full persistent memory)
4. Check .architect/sprints/CURRENT_SPRINT.md (current tasks)
5. Run: git status && git log --oneline -5

Then confirm:
- What feature I was working on
- What task I was doing
- What file I was editing
- What my next actions are
- Any blockers

After restoration, announce: "Context successfully restored" and show me a brief summary
of where we are and what we need to do next.
    """
    )

    print("\n" + "=" * 60)
    print("✅ Recovery information gathered")
    print("\nCopy the RECOVERY PROMPT above and paste it to Claude Code.")


if __name__ == "__main__":
    try:
        recover_state()
    except Exception as e:
        print(f"\n❌ Recovery error: {e}")
        print("\nManual recovery:")
        print("  1. Read .architect/memory/CONTEXT_HANDOFF.json")
        print("  2. Read .architect/memory/PERSISTENT_MEMORY.json")
        print("  3. Read .architect/CLAUDE_INTERFACE.md")
