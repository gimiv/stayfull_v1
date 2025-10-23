"""
AI Agent models for Nora - Persistent conversation context
"""

from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel


class NoraContext(BaseModel):
    """
    Persistent AI context for each user (NOT session-based).

    Stores conversation history, preferences, and task state
    so Nora can remember context across sessions and provide
    continuity over days/weeks/months.

    Business Rules:
    - One context per user per organization
    - Conversation history kept for 30 days (rolling window)
    - Task state persists indefinitely until completed
    - Preferences learned over time
    """

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="nora_contexts",
        help_text="User this context belongs to"
    )
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.CASCADE,
        related_name="nora_contexts",
        help_text="Organization this context is scoped to"
    )

    # Conversation History (rolling 30-day window)
    conversation_history = models.JSONField(
        default=list,
        blank=True,
        help_text="List of messages with timestamps, roles, content"
    )
    # Example structure:
    # [
    #   {"role": "user", "content": "Hi Nora", "timestamp": "2025-10-23T10:00:00Z"},
    #   {"role": "assistant", "content": "Hello! How can I help?", "timestamp": "..."},
    # ]

    # User Preferences (learned over time)
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences learned from interactions"
    )
    # Example structure:
    # {
    #   "prefers_voice": True,
    #   "tone": "enthusiastic",  # enthusiastic, professional, casual
    #   "typical_questions": ["check today's arrivals", "revenue this month"],
    #   "response_style": "concise"  # concise, detailed
    # }

    # Current Task Context
    active_task = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Current active task (e.g., 'onboarding', 'creating_booking')"
    )
    # Options: onboarding, creating_booking, generating_report, etc.

    task_state = models.JSONField(
        default=dict,
        blank=True,
        help_text="Current state of active task"
    )
    # Example for onboarding:
    # {
    #   "step": "HOTEL_BASICS",
    #   "hotel_data": {...},
    #   "room_types_created": 2,
    #   "total_rooms": 45,
    #   "progress_percentage": 60
    # }

    # Recent Actions (for context continuity)
    recent_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Recent actions taken (last 10)"
    )
    # Example:
    # [
    #   {"action": "created_booking", "timestamp": "...", "details": {"guest": "John", ...}},
    #   {"action": "updated_rates", "timestamp": "...", "details": {"room_type": "Suite", ...}}
    # ]

    # Metadata
    last_interaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last interaction with Nora"
    )

    class Meta:
        verbose_name = "Nora Context"
        verbose_name_plural = "Nora Contexts"
        unique_together = [["user", "organization"]]
        ordering = ["-last_interaction_at"]
        indexes = [
            models.Index(fields=["user", "organization"]),
            models.Index(fields=["active_task"]),
            models.Index(fields=["last_interaction_at"]),
        ]

    def __str__(self):
        return f"Nora Context: {self.user.email} @ {self.organization.name}"

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        from django.utils import timezone

        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": timezone.now().isoformat()
        }

        self.conversation_history.append(message)

        # Keep only last 30 days of conversation
        cutoff = timezone.now() - timezone.timedelta(days=30)
        self.conversation_history = [
            msg for msg in self.conversation_history
            if timezone.datetime.fromisoformat(msg["timestamp"]) > cutoff
        ]

        self.last_interaction_at = timezone.now()
        self.save()

    def add_action(self, action: str, details: dict):
        """Add action to recent actions (keep last 10)"""
        from django.utils import timezone

        action_entry = {
            "action": action,
            "timestamp": timezone.now().isoformat(),
            "details": details
        }

        self.recent_actions.insert(0, action_entry)
        self.recent_actions = self.recent_actions[:10]  # Keep only last 10
        self.save()

    def update_preference(self, key: str, value):
        """Update user preference"""
        self.preferences[key] = value
        self.save()

    def set_active_task(self, task: str, initial_state: dict = None):
        """Set active task and initial state"""
        self.active_task = task
        self.task_state = initial_state or {}
        self.save()

    def update_task_state(self, updates: dict):
        """Update task state (merge with existing)"""
        self.task_state.update(updates)
        self.save()

    def complete_task(self):
        """Mark current task as complete"""
        if self.active_task:
            self.add_action(
                action=f"completed_{self.active_task}",
                details=self.task_state
            )

        self.active_task = None
        self.task_state = {}
        self.save()

    def get_recent_conversation(self, limit: int = 10) -> list:
        """Get recent conversation messages"""
        return self.conversation_history[-limit:] if self.conversation_history else []
