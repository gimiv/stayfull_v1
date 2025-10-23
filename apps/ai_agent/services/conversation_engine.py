"""
Conversation Engine - State Machine for Onboarding Flow

Manages the 5-state onboarding process:
1. HOTEL_BASICS - Name, location, website, contact
2. ROOM_TYPES - Room categories, pricing, occupancy
3. POLICIES - Payment, cancellation, check-in/out
4. REVIEW - Preview and confirm everything
5. COMPLETE - Generate hotel and finish
"""

from enum import Enum
from typing import Dict, Optional, Tuple
from django.utils import timezone


class OnboardingState(Enum):
    """States in the onboarding flow"""
    HOTEL_BASICS = "hotel_basics"
    ROOM_TYPES = "room_types"
    POLICIES = "policies"
    REVIEW = "review"
    COMPLETE = "complete"


class OnboardingEngine:
    """
    Manages onboarding state transitions and progress tracking.

    Responsibilities:
    - Track current state
    - Determine next state based on data completeness
    - Calculate progress percentage
    - Generate state-specific questions
    """

    # Required fields for each state
    REQUIRED_FIELDS = {
        OnboardingState.HOTEL_BASICS: [
            "hotel_name",
            "city",
            "country",
            "contact_email",
        ],
        OnboardingState.ROOM_TYPES: [
            "room_types",  # List of at least 1 room type
        ],
        OnboardingState.POLICIES: [
            "deposit_amount",
            "deposit_timing",
            "cancellation_policy",
            "checkin_time",
            "checkout_time",
        ],
        OnboardingState.REVIEW: [
            "review_confirmed",  # Boolean flag
        ],
    }

    # Progress percentages for each state
    STATE_PROGRESS = {
        OnboardingState.HOTEL_BASICS: 0,
        OnboardingState.ROOM_TYPES: 25,
        OnboardingState.POLICIES: 50,
        OnboardingState.REVIEW: 75,
        OnboardingState.COMPLETE: 100,
    }

    # PHASE 4.5: Sections structure for progress tracker with progressive disclosure
    SECTIONS = [
        {
            'id': 'property_info',
            'name': 'Property Info',
            'state': OnboardingState.HOTEL_BASICS,
            'steps': [
                {'field': 'hotel_name', 'label': 'Hotel name'},
                {'field': 'city', 'label': 'City'},
                {'field': 'country', 'label': 'Country'},
                {'field': 'contact_email', 'label': 'Contact email'},
            ],
            'weight': 25  # % of overall progress
        },
        {
            'id': 'rooms_setup',
            'name': 'Rooms Setup',
            'state': OnboardingState.ROOM_TYPES,
            'steps': [
                {'field': 'room_types', 'label': 'Room types'},
            ],
            'weight': 45
        },
        {
            'id': 'policies',
            'name': 'Policies',
            'state': OnboardingState.POLICIES,
            'steps': [
                {'field': 'deposit_amount', 'label': 'Deposit amount'},
                {'field': 'deposit_timing', 'label': 'Deposit timing'},
                {'field': 'cancellation_policy', 'label': 'Cancellation policy'},
                {'field': 'checkin_time', 'label': 'Check-in time'},
                {'field': 'checkout_time', 'label': 'Check-out time'},
            ],
            'weight': 20
        },
        {
            'id': 'review',
            'name': 'Review & Launch',
            'state': OnboardingState.REVIEW,
            'steps': [
                {'field': 'review_confirmed', 'label': 'Confirm details'},
            ],
            'weight': 10
        }
    ]

    def __init__(self, task_state: Dict):
        """
        Initialize engine with current task state.

        Args:
            task_state: NoraContext.task_state dict
        """
        self.task_state = task_state
        self.current_state = self._get_current_state()

    def _get_current_state(self) -> OnboardingState:
        """Get current state from task_state"""
        state_str = self.task_state.get("step", "hotel_basics")
        return OnboardingState(state_str)

    def is_state_complete(self, state: OnboardingState) -> bool:
        """
        Check if a state has all required fields.

        Args:
            state: State to check

        Returns:
            True if all required fields are present
        """
        if state == OnboardingState.COMPLETE:
            return True

        required = self.REQUIRED_FIELDS.get(state, [])

        for field in required:
            if field == "room_types":
                # Special case: need at least 1 room type
                room_types = self.task_state.get("room_types", [])
                if not room_types or len(room_types) == 0:
                    return False
            elif field == "review_confirmed":
                # Special case: boolean flag
                if not self.task_state.get("review_confirmed", False):
                    return False
            else:
                # Regular field check
                if not self.task_state.get(field):
                    return False

        return True

    def get_next_state(self) -> Optional[OnboardingState]:
        """
        Determine next state based on current state completion.

        Returns:
            Next OnboardingState, or None if complete
        """
        # State transition order
        state_order = [
            OnboardingState.HOTEL_BASICS,
            OnboardingState.ROOM_TYPES,
            OnboardingState.POLICIES,
            OnboardingState.REVIEW,
            OnboardingState.COMPLETE,
        ]

        # If current state is not complete, stay in it
        if not self.is_state_complete(self.current_state):
            return self.current_state

        # Find next state in order
        try:
            current_index = state_order.index(self.current_state)
            if current_index < len(state_order) - 1:
                return state_order[current_index + 1]
            else:
                return None  # Already at COMPLETE
        except ValueError:
            # Invalid state, default to HOTEL_BASICS
            return OnboardingState.HOTEL_BASICS

    def transition_to_next_state(self) -> Tuple[OnboardingState, int]:
        """
        Transition to next state and update task_state.

        Returns:
            Tuple of (new_state, progress_percentage)
        """
        next_state = self.get_next_state()

        if next_state is None:
            # Already complete
            return OnboardingState.COMPLETE, 100

        # Update task_state
        self.task_state["step"] = next_state.value
        self.task_state["progress_percentage"] = self.STATE_PROGRESS[next_state]
        self.task_state["last_transition_at"] = timezone.now().isoformat()

        self.current_state = next_state

        return next_state, self.STATE_PROGRESS[next_state]

    def get_progress_percentage(self) -> int:
        """Get current progress percentage (0-100)"""
        return self.STATE_PROGRESS.get(self.current_state, 0)

    def get_missing_fields(self) -> list:
        """
        Get list of missing required fields for current state.

        Returns:
            List of field names that are missing
        """
        if self.current_state == OnboardingState.COMPLETE:
            return []

        required = self.REQUIRED_FIELDS.get(self.current_state, [])
        missing = []

        for field in required:
            if field == "room_types":
                room_types = self.task_state.get("room_types", [])
                if not room_types or len(room_types) == 0:
                    missing.append(field)
            elif field == "review_confirmed":
                if not self.task_state.get("review_confirmed", False):
                    missing.append(field)
            else:
                if not self.task_state.get(field):
                    missing.append(field)

        return missing

    def update_field(self, field: str, value) -> bool:
        """
        Update a field in task_state.

        Args:
            field: Field name
            value: New value

        Returns:
            True if this completed the current state
        """
        self.task_state[field] = value
        self.task_state["last_update_at"] = timezone.now().isoformat()

        return self.is_state_complete(self.current_state)

    def get_state_summary(self) -> Dict:
        """
        Get summary of current onboarding status.

        Returns:
            Dict with state, progress, missing fields
        """
        return {
            "current_state": self.current_state.value,
            "progress_percentage": self.get_progress_percentage(),
            "is_complete": self.is_state_complete(self.current_state),
            "missing_fields": self.get_missing_fields(),
            "next_state": self.get_next_state().value if self.get_next_state() else None,
        }

    def get_progress_data(self) -> Dict:
        """
        Get progress data with progressive disclosure for UI tracker.

        Progressive Disclosure Rules:
        - Completed sections: Show summary only (collapsed by default)
        - Active section: Show completed steps + current step + remaining COUNT
        - Future sections: Show only "Not started" (collapsed)

        Returns:
            Dict with sections data and overall progress
        """
        sections_data = []
        overall_progress = self.get_progress_percentage()

        for section in self.SECTIONS:
            section_data = {
                'id': section['id'],
                'name': section['name'],
                'weight': section['weight'],
            }

            # Determine if this section is complete, active, or pending
            if section['state'] == self.current_state:
                # ACTIVE SECTION - Progressive disclosure
                section_data['status'] = 'active'
                section_data['progress_pct'] = self._calculate_section_progress(section)
                
                # Separate completed and pending steps
                completed_steps = []
                pending_steps = []
                
                for step in section['steps']:
                    field = step['field']
                    if field in self.task_state and self.task_state[field]:
                        completed_steps.append({
                            'field': field,
                            'label': step['label'],
                            'value': self._format_field_value(field, self.task_state[field])
                        })
                    else:
                        pending_steps.append({
                            'field': field,
                            'label': step['label']
                        })
                
                section_data['completed_steps'] = completed_steps
                section_data['current_step'] = pending_steps[0] if pending_steps else None
                section_data['remaining_count'] = len(pending_steps) - 1 if len(pending_steps) > 1 else 0

            elif self._is_section_complete(section):
                # COMPLETED SECTION - Collapsed summary
                section_data['status'] = 'complete'
                section_data['progress_pct'] = 100
                section_data['completed_count'] = len(section['steps'])
                section_data['steps'] = [
                    {
                        'field': step['field'],
                        'label': step['label'],
                        'value': self._format_field_value(step['field'], self.task_state.get(step['field']))
                    }
                    for step in section['steps']
                ]

            else:
                # PENDING SECTION - Not started
                section_data['status'] = 'pending'
                section_data['progress_pct'] = 0

            sections_data.append(section_data)

        return {
            'sections': sections_data,
            'overall_progress': overall_progress
        }

    def _calculate_section_progress(self, section: Dict) -> int:
        """Calculate percentage complete for a section"""
        total_steps = len(section['steps'])
        completed = sum(
            1 for step in section['steps']
            if step['field'] in self.task_state and self.task_state[step['field']]
        )
        return int((completed / total_steps) * 100) if total_steps > 0 else 0

    def _is_section_complete(self, section: Dict) -> bool:
        """Check if all steps in a section are complete"""
        return all(
            step['field'] in self.task_state and self.task_state[step['field']]
            for step in section['steps']
        )

    def _format_field_value(self, field: str, value) -> str:
        """Format field value for display"""
        if value is None:
            return ""
        
        if field == 'room_types' and isinstance(value, list):
            return f"{len(value)} room type(s)"
        
        if isinstance(value, bool):
            return "✓ Confirmed" if value else "Pending"
        
        if isinstance(value, (list, dict)):
            return f"{len(value)} items"
        
        return str(value)
