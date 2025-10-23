#!/usr/bin/env python3
"""Quick commands for interacting with your architect and developer"""

import json
from datetime import datetime
from pathlib import Path

ARCHITECT_HOME = Path(".architect")
MEMORY_FILE = ARCHITECT_HOME / "memory" / "PERSISTENT_MEMORY.json"
DEVELOPER_CONTEXT = ARCHITECT_HOME / "memory" / "DEVELOPER_CONTEXT.json"
SPRINT_FILE = ARCHITECT_HOME / "sprints" / "CURRENT_SPRINT.md"


def checkpoint(message):
    """Quick checkpoint command"""
    timestamp = datetime.now().strftime("%H:%M")
    with open(SPRINT_FILE, "a") as f:
        f.write(f"\n✓ [{timestamp}] {message}\n")
    print(f"✅ Checkpoint: {message}")


def update_position(file, line, task):
    """Update current working position"""
    memory = json.loads(MEMORY_FILE.read_text())
    memory["context"]["last_file"] = file
    memory["context"]["last_line"] = line
    memory["context"]["last_task"] = task
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))
    print(f"📍 Position updated: {file}:{line} - {task}")


def log_decision(decision, rationale):
    """Log an architectural decision"""
    decision_file = (
        ARCHITECT_HOME
        / "decisions"
        / f"{datetime.now().strftime('%Y%m%d')}_decisions.md"
    )
    with open(decision_file, "a") as f:
        f.write(f"\n## Decision: {decision}\n")
        f.write(f"**Time**: {datetime.now().strftime('%H:%M')}\n")
        f.write(f"**Rationale**: {rationale}\n")
        f.write("---\n")
    print(f"📝 Decision logged: {decision}")


def show_status():
    """Show current development status"""
    memory = json.loads(MEMORY_FILE.read_text())
    print("\n📊 Current Status")
    print("=" * 40)
    print(f"Sprint: {memory['project']['sprint']}")
    print(f"Phase: {memory['project']['phase']}")
    print(f"Last Task: {memory['context']['last_task']}")
    print(f"Features Complete: {len(memory['features']['completed'])}")
    print(f"In Progress: {len(memory['features']['in_progress'])}")
    print("=" * 40)


def switch_to_developer(feature_id="F-001"):
    """Generate prompt to switch Claude to developer mode"""
    print("\n" + "=" * 60)
    print("🛠️  SWITCHING TO DEVELOPER MODE")
    print("=" * 60)
    print(f"\nFeature: {feature_id}")
    print("\nCopy and paste this prompt to Claude Code:")
    print("\n" + "-" * 60)
    print(
        """
I need to switch from Architect mode to Developer mode.

Please execute this mode switch sequence:

1. Read .architect/DEVELOPER_INTERFACE.md (loads developer identity and protocols)
2. Read .architect/memory/DEVELOPER_CONTEXT.json (current implementation state)
3. Read .architect/handoffs/F-001-developer-handoff.md (your implementation guide)
4. Run: git status && git log --oneline -5

Then confirm:
- Your role (Senior Full-Stack Developer)
- Current feature (F-001: Stayfull PMS Core)
- Current phase and day (from DEVELOPER_CONTEXT.json)
- Next task to implement
- Any blockers

After restoration, announce: "🛠️ Developer Mode Active" and show me a brief summary
of where we are in the 15-day implementation plan and what task we're starting with.

Let's build F-001!
    """
    )
    print("-" * 60)
    print("\n✅ Prompt ready - paste it to Claude Code to activate developer mode\n")


def switch_to_architect():
    """Generate prompt to switch Claude to architect mode"""
    print("\n" + "=" * 60)
    print("🏛️  SWITCHING TO ARCHITECT MODE")
    print("=" * 60)
    print("\nCopy and paste this prompt to Claude Code:")
    print("\n" + "-" * 60)
    print(
        """
I need to switch from Developer mode to Architect mode.

Please execute this mode switch sequence:

1. Read .architect/CLAUDE_INTERFACE.md (loads architect identity and protocols)
2. Read .architect/memory/CONTEXT_HANDOFF.json (critical last session state)
3. Read .architect/memory/PERSISTENT_MEMORY.json (full persistent memory)
4. Check .architect/sprints/CURRENT_SPRINT.md (current tasks)
5. Run: git status && git log --oneline -5

Then confirm:
- Your role (Senior Product Architect)
- What feature you were working on
- What task you were doing
- What your next actions are
- Any blockers

After restoration, announce: "🏛️ Architect Mode Active" and show me a brief summary
of where we are and what we need to do next.
    """
    )
    print("-" * 60)
    print("\n✅ Prompt ready - paste it to Claude Code to activate architect mode\n")


def developer_status():
    """Show developer implementation status"""
    if not DEVELOPER_CONTEXT.exists():
        print("⚠️  Developer context not found. Run with --mode developer first.")
        return

    dev_context = json.loads(DEVELOPER_CONTEXT.read_text())
    progress = dev_context["implementation_progress"]
    metrics = dev_context["code_metrics"]

    print("\n🛠️  Developer Status")
    print("=" * 60)
    print(f"Feature: {dev_context['feature']['id']} - {dev_context['feature']['name']}")
    print(f"Status: {dev_context['feature']['status']}")
    print(
        f"Phase: {progress['phase']} ({progress['phase_number']}/{progress['total_phases']})"
    )
    print(f"Day: {progress['day']}")
    print(f"Progress: {progress['percent_complete']}%")
    print(f"\nCurrent Task: {progress['current_task']}")
    print(f"Next Task: {progress['next_task']}")

    print(f"\n📊 Code Metrics:")
    print(f"  Tests: {metrics['tests_passing']}/{metrics['tests_written']} passing")
    print(f"  Coverage: {metrics['test_coverage_percent']}%")
    print(f"  Models: {metrics['models_implemented']}/6")
    print(f"  API Endpoints: {metrics['api_endpoints_implemented']}/20+")

    if dev_context["blockers"]:
        print(f"\n🚨 Blockers: {len(dev_context['blockers'])}")
        for blocker in dev_context["blockers"]:
            print(f"  - {blocker}")
    else:
        print(f"\n✅ No blockers")

    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "status":
            show_status()
        elif cmd == "checkpoint" and len(sys.argv) > 2:
            checkpoint(" ".join(sys.argv[2:]))
        elif cmd == "--mode" and len(sys.argv) > 2:
            mode = sys.argv[2]
            if mode == "developer":
                feature = sys.argv[3] if len(sys.argv) > 3 else "F-001"
                switch_to_developer(feature)
            elif mode == "architect":
                switch_to_architect()
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: developer, architect")
        elif cmd == "dev-status":
            developer_status()
        else:
            print("Usage:")
            print(
                "  python architect_commands.py status              # Show architect status"
            )
            print(
                "  python architect_commands.py dev-status          # Show developer status"
            )
            print(
                "  python architect_commands.py --mode developer    # Switch to developer mode"
            )
            print(
                "  python architect_commands.py --mode architect    # Switch to architect mode"
            )
            print("  python architect_commands.py checkpoint <msg>    # Add checkpoint")
    else:
        print("Usage:")
        print(
            "  python architect_commands.py status              # Show architect status"
        )
        print(
            "  python architect_commands.py dev-status          # Show developer status"
        )
        print(
            "  python architect_commands.py --mode developer    # Switch to developer mode"
        )
        print(
            "  python architect_commands.py --mode architect    # Switch to architect mode"
        )
        print("  python architect_commands.py checkpoint <msg>    # Add checkpoint")
