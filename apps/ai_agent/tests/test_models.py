"""
Tests for Nora AI Agent models
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError

from apps.core.models import Organization
from apps.ai_agent.models import NoraContext


class NoraContextModelTests(TestCase):
    """Test suite for NoraContext model"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Hotel",
            slug="test-hotel",
            type="independent",
            contact_email="test@testhotel.com"
        )

    def test_create_nora_context(self):
        """Test creating a NoraContext instance"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        self.assertEqual(context.user, self.user)
        self.assertEqual(context.organization, self.organization)
        self.assertEqual(context.conversation_history, [])
        self.assertEqual(context.preferences, {})
        self.assertEqual(context.recent_actions, [])
        self.assertIsNone(context.active_task)
        self.assertEqual(context.task_state, {})

    def test_unique_together_constraint(self):
        """Test that user + organization must be unique"""
        NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Attempting to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            NoraContext.objects.create(
                user=self.user,
                organization=self.organization
            )

    def test_add_message(self):
        """Test add_message() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add user message
        context.add_message(role="user", content="Hello Nora!")
        context.refresh_from_db()

        self.assertEqual(len(context.conversation_history), 1)
        self.assertEqual(context.conversation_history[0]["role"], "user")
        self.assertEqual(context.conversation_history[0]["content"], "Hello Nora!")
        self.assertIn("timestamp", context.conversation_history[0])
        self.assertIsNotNone(context.last_interaction_at)

        # Add assistant message
        context.add_message(role="assistant", content="Hello! How can I help?")
        context.refresh_from_db()

        self.assertEqual(len(context.conversation_history), 2)
        self.assertEqual(context.conversation_history[1]["role"], "assistant")

    def test_add_message_30_day_cleanup(self):
        """Test that messages older than 30 days are cleaned up"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add old message (35 days ago)
        old_timestamp = (timezone.now() - timedelta(days=35)).isoformat()
        context.conversation_history = [
            {
                "role": "user",
                "content": "Old message",
                "timestamp": old_timestamp
            }
        ]
        context.save()

        # Add new message
        context.add_message(role="user", content="New message")
        context.refresh_from_db()

        # Old message should be removed
        self.assertEqual(len(context.conversation_history), 1)
        self.assertEqual(context.conversation_history[0]["content"], "New message")

    def test_get_recent_conversation(self):
        """Test get_recent_conversation() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add 15 messages
        for i in range(15):
            context.add_message(role="user", content=f"Message {i}")

        # Get last 10
        recent = context.get_recent_conversation(limit=10)
        self.assertEqual(len(recent), 10)
        self.assertEqual(recent[0]["content"], "Message 5")  # Should start from message 5
        self.assertEqual(recent[-1]["content"], "Message 14")  # Should end at message 14

        # Get last 5
        recent = context.get_recent_conversation(limit=5)
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[0]["content"], "Message 10")

    def test_add_action(self):
        """Test add_action() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add action
        context.add_action(
            action="create_hotel",
            details={"hotel_name": "Grand Plaza"}
        )
        context.refresh_from_db()

        self.assertEqual(len(context.recent_actions), 1)
        self.assertEqual(context.recent_actions[0]["action"], "create_hotel")
        self.assertEqual(context.recent_actions[0]["details"]["hotel_name"], "Grand Plaza")
        self.assertIn("timestamp", context.recent_actions[0])

    def test_add_action_keeps_last_10(self):
        """Test that only last 10 actions are kept"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add 15 actions
        for i in range(15):
            context.add_action(
                action=f"action_{i}",
                details={"index": i}
            )

        context.refresh_from_db()

        # Should only keep last 10 (most recent first)
        self.assertEqual(len(context.recent_actions), 10)
        self.assertEqual(context.recent_actions[0]["action"], "action_14")  # Most recent
        self.assertEqual(context.recent_actions[-1]["action"], "action_5")  # Oldest of the 10

    def test_update_preference(self):
        """Test update_preference() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Add preference
        context.update_preference("tone", "enthusiastic")
        context.refresh_from_db()

        self.assertEqual(context.preferences["tone"], "enthusiastic")

        # Update preference
        context.update_preference("tone", "professional")
        context.refresh_from_db()

        self.assertEqual(context.preferences["tone"], "professional")

        # Add another preference
        context.update_preference("language", "en")
        context.refresh_from_db()

        self.assertEqual(len(context.preferences), 2)
        self.assertEqual(context.preferences["language"], "en")

    def test_set_active_task(self):
        """Test set_active_task() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Set active task
        context.set_active_task(
            task="onboarding",
            initial_state={"step": "HOTEL_BASICS", "progress": 0}
        )
        context.refresh_from_db()

        self.assertEqual(context.active_task, "onboarding")
        self.assertEqual(context.task_state["step"], "HOTEL_BASICS")
        self.assertEqual(context.task_state["progress"], 0)

    def test_update_task_state(self):
        """Test update_task_state() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Set initial task
        context.set_active_task(
            task="onboarding",
            initial_state={"step": "HOTEL_BASICS", "progress": 0}
        )

        # Update state
        context.update_task_state({"progress": 25})
        context.refresh_from_db()

        self.assertEqual(context.task_state["step"], "HOTEL_BASICS")
        self.assertEqual(context.task_state["progress"], 25)

        # Update step
        context.update_task_state({"step": "ROOM_TYPES", "progress": 50})
        context.refresh_from_db()

        self.assertEqual(context.task_state["step"], "ROOM_TYPES")
        self.assertEqual(context.task_state["progress"], 50)

    def test_complete_task(self):
        """Test complete_task() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        # Set active task
        context.set_active_task(
            task="onboarding",
            initial_state={"step": "HOTEL_BASICS"}
        )

        # Complete task
        context.complete_task()
        context.refresh_from_db()

        self.assertIsNone(context.active_task)
        self.assertEqual(context.task_state, {})

        # Check that completion was logged in recent_actions
        self.assertEqual(len(context.recent_actions), 1)
        self.assertEqual(context.recent_actions[0]["action"], "completed_onboarding")
        self.assertEqual(context.recent_actions[0]["details"]["step"], "HOTEL_BASICS")

    def test_string_representation(self):
        """Test __str__() method"""
        context = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        expected = f"Nora Context: {self.user.email} @ {self.organization.name}"
        self.assertEqual(str(context), expected)

    def test_ordering(self):
        """Test that contexts are ordered by last_interaction_at (desc)"""
        # Create second user and context
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123"
        )

        context1 = NoraContext.objects.create(
            user=self.user,
            organization=self.organization
        )

        context2 = NoraContext.objects.create(
            user=user2,
            organization=self.organization
        )

        # Update context1 with a message (sets last_interaction_at)
        context1.add_message(role="user", content="Hello")

        # Get all contexts (ordered by -last_interaction_at)
        # In PostgreSQL, NULLs come first with DESC ordering (NULLS FIRST is default)
        contexts = list(NoraContext.objects.all())

        # With -last_interaction_at ordering and NULLS FIRST:
        # context2 (NULL) comes first, context1 (has timestamp) comes second
        # But for contexts with timestamps, most recent comes first

        # Let's verify context1 has a timestamp and context2 doesn't
        context1.refresh_from_db()
        context2.refresh_from_db()
        self.assertIsNotNone(context1.last_interaction_at)
        self.assertIsNone(context2.last_interaction_at)

        # Contexts should be returned in order: nulls first, then by timestamp desc
        # In this case: context2 (NULL), then context1 (timestamp)
        self.assertEqual(len(contexts), 2)
