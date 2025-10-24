#!/usr/bin/env python
"""
Test script to simulate a full onboarding conversation with Nora
and audit the results for accuracy.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from apps.ai_agent.services.nora_agent import NoraAgent
from apps.ai_agent.models import NoraContext
from apps.core.models import Organization

User = get_user_model()

# ANSI color codes for better readability
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_message(role, message):
    """Print a message in the conversation"""
    if role == "user":
        print(f"{Colors.OKCYAN}{Colors.BOLD}USER:{Colors.ENDC} {message}")
    else:
        print(f"{Colors.OKGREEN}{Colors.BOLD}NORA:{Colors.ENDC} {message}")
    print()

def print_data(label, data):
    """Print data with formatting"""
    print(f"{Colors.WARNING}{Colors.BOLD}{label}:{Colors.ENDC}")
    print(json.dumps(data, indent=2, default=str))
    print()

def audit_state(agent, step_name):
    """Audit the current state and print results"""
    print(f"\n{Colors.OKBLUE}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{Colors.BOLD}AUDIT CHECKPOINT: {step_name}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'─'*80}{Colors.ENDC}")

    # Print current task state
    print(f"\n{Colors.BOLD}Task State:{Colors.ENDC}")
    important_fields = [
        'hotel_name', 'full_address', 'street_address', 'city', 'state', 'state_code',
        'country', 'country_code', 'phone', 'website', 'contact_email',
        'latitude', 'longitude', 'google_place_id'
    ]

    for field in important_fields:
        value = agent.context.task_state.get(field)
        if value:
            print(f"  ✓ {field}: {value}")
        else:
            print(f"  ✗ {field}: {Colors.FAIL}MISSING{Colors.ENDC}")

    # Check for data issues
    issues = []

    # Check for state/country confusion
    state = agent.context.task_state.get('state')
    country = agent.context.task_state.get('country')
    if state and country:
        us_states = ['NH', 'NY', 'CA', 'FL', 'TX', 'MA', 'PA']
        if state in us_states and country != 'United States':
            issues.append(f"⚠️  State is '{state}' but country is '{country}' - possible confusion")

    # Check for missing address
    if agent.context.task_state.get('city') and not agent.context.task_state.get('full_address'):
        issues.append("⚠️  City is set but full_address is missing")

    # Check for New Hampshire issue specifically
    if country == 'New Hampshire' or country == 'NH':
        issues.append(f"❌ CRITICAL: Country is set to '{country}' - should be a state!")

    if issues:
        print(f"\n{Colors.FAIL}{Colors.BOLD}Issues Found:{Colors.ENDC}")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n{Colors.OKGREEN}✓ No issues detected{Colors.ENDC}")

    print(f"{Colors.OKBLUE}{'─'*80}{Colors.ENDC}\n")

def run_conversation():
    """Run a full onboarding conversation"""

    print_section("NORA ONBOARDING TEST - FULL CONVERSATION AUDIT")

    # Get or create test user
    try:
        user = User.objects.get(email='demo@example.com')
        staff = user.staff_positions.first()

        if not staff:
            print(f"{Colors.FAIL}Error: User {user.email} has no staff positions{Colors.ENDC}")
            return

        organization = staff.organization

        print(f"{Colors.BOLD}Test User:{Colors.ENDC} {user.email}")
        print(f"{Colors.BOLD}Organization:{Colors.ENDC} {organization.name}\n")

        # Clear existing context for clean test
        NoraContext.objects.filter(user=user, organization=organization).delete()
        print(f"{Colors.WARNING}Cleared existing Nora context for clean test{Colors.ENDC}\n")

    except User.DoesNotExist:
        print(f"{Colors.FAIL}Error: demo@example.com user not found{Colors.ENDC}")
        print("Please create a user first or update the script with a valid email.")
        return

    # Initialize Nora agent
    agent = NoraAgent(user=user, organization=organization)

    # ============================================================================
    # STEP 1: Start Onboarding
    # ============================================================================
    print_section("STEP 1: Start Onboarding")

    response = agent.start_onboarding()
    print_message("nora", response['message'])
    audit_state(agent, "After Starting Onboarding")

    # ============================================================================
    # STEP 2: Provide Hotel Name and Location
    # ============================================================================
    print_section("STEP 2: Provide Hotel Name and Location")

    user_message = "The Inn at Woodstock, North Woodstock, NH"
    print_message("user", user_message)

    response = agent.process_message(user_message)
    print_message("nora", response['message'])
    print_data("Response Data", response.get('data', {}))
    audit_state(agent, "After Providing Hotel Name and Location")

    # ============================================================================
    # STEP 3: Confirm Address (if Google Places triggered)
    # ============================================================================
    print_section("STEP 3: Address Confirmation")

    # Check if awaiting address confirmation
    if agent.context.task_state.get('_awaiting_address_confirmation'):
        print(f"{Colors.WARNING}System is awaiting address confirmation{Colors.ENDC}\n")

        user_message = "Yes, that's correct"
        print_message("user", user_message)

        response = agent.process_message(user_message)
        print_message("nora", response['message'])
        audit_state(agent, "After Address Confirmation")
    else:
        print(f"{Colors.WARNING}No address confirmation needed (manual flow){Colors.ENDC}\n")

    # ============================================================================
    # STEP 4: Provide Contact Email
    # ============================================================================
    print_section("STEP 4: Provide Contact Email")

    user_message = "info@innwoodstock.com"
    print_message("user", user_message)

    response = agent.process_message(user_message)
    print_message("nora", response['message'])
    audit_state(agent, "After Providing Email")

    # ============================================================================
    # STEP 5: Room Types
    # ============================================================================
    print_section("STEP 5: Provide Room Types")

    user_message = "We have 3 room types: Standard Queen, Deluxe King, and Suite"
    print_message("user", user_message)

    response = agent.process_message(user_message)
    print_message("nora", response['message'])
    audit_state(agent, "After Providing Room Types")

    # ============================================================================
    # STEP 6: Room Type Details (if needed)
    # ============================================================================
    print_section("STEP 6: Room Type Details")

    # Check if Nora is asking for room details
    if 'room' in response['message'].lower() and ('price' in response['message'].lower() or 'detail' in response['message'].lower()):
        user_message = "Standard Queen is $150/night with 2 guests, Deluxe King is $200/night with 2 guests, Suite is $350/night with 4 guests"
        print_message("user", user_message)

        response = agent.process_message(user_message)
        print_message("nora", response['message'])
        audit_state(agent, "After Room Details")

    # ============================================================================
    # STEP 7: Policies
    # ============================================================================
    print_section("STEP 7: Payment and Cancellation Policies")

    # Payment policy
    user_message = "50% deposit at booking, rest on arrival"
    print_message("user", user_message)

    response = agent.process_message(user_message)
    print_message("nora", response['message'])

    # Cancellation policy (if asked)
    if 'cancel' in response['message'].lower():
        user_message = "Free cancellation up to 48 hours before check-in"
        print_message("user", user_message)

        response = agent.process_message(user_message)
        print_message("nora", response['message'])

    # Check-in times (if asked)
    if 'check' in response['message'].lower():
        user_message = "Check-in at 3 PM, check-out at 11 AM"
        print_message("user", user_message)

        response = agent.process_message(user_message)
        print_message("nora", response['message'])

    audit_state(agent, "After Policies")

    # ============================================================================
    # FINAL AUDIT
    # ============================================================================
    print_section("FINAL AUDIT REPORT")

    print(f"{Colors.BOLD}Complete Task State:{Colors.ENDC}")
    print(json.dumps(agent.context.task_state, indent=2, default=str))
    print()

    # Critical checks
    print(f"{Colors.BOLD}{Colors.UNDERLINE}Critical Field Verification:{Colors.ENDC}\n")

    checks = [
        ('hotel_name', 'Hotel Name', 'The Inn at Woodstock'),
        ('city', 'City', 'North Woodstock'),
        ('state', 'State', 'NH or New Hampshire'),
        ('country', 'Country', 'United States'),
        ('contact_email', 'Email', 'info@innwoodstock.com'),
    ]

    passed = 0
    failed = 0

    for field, label, expected in checks:
        value = agent.context.task_state.get(field)
        if value:
            print(f"  ✓ {Colors.OKGREEN}{label}: {value}{Colors.ENDC}")
            passed += 1
        else:
            print(f"  ✗ {Colors.FAIL}{label}: MISSING (expected: {expected}){Colors.ENDC}")
            failed += 1

    # Special check: Country should NOT be New Hampshire
    country = agent.context.task_state.get('country')
    if country in ['New Hampshire', 'NH']:
        print(f"  ✗ {Colors.FAIL}Country Validation: FAILED - Country is '{country}' (should be United States){Colors.ENDC}")
        failed += 1
    else:
        print(f"  ✓ {Colors.OKGREEN}Country Validation: PASSED{Colors.ENDC}")
        passed += 1

    # Summary
    print(f"\n{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"  Passed: {Colors.OKGREEN}{passed}{Colors.ENDC}")
    print(f"  Failed: {Colors.FAIL}{failed}{Colors.ENDC}")

    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL CHECKS PASSED!{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SOME CHECKS FAILED - REVIEW ABOVE{Colors.ENDC}")

    print()

if __name__ == "__main__":
    run_conversation()
