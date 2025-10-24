"""
Views for Nora AI Agent
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from apps.ai_agent.services.nora_agent import NoraAgent
from apps.ai_agent.services.voice_handler import VoiceHandler
from apps.ai_agent.services.data_generator import DataGenerator


@login_required
def chat_view(request):
    """
    Main chat interface for Nora.

    Renders split-screen layout (desktop) or tabbed layout (mobile).
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return render(request, "ai_agent/no_organization.html")

    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Initialize Nora agent
    agent = NoraAgent(user=request.user, organization=organization)

    # Get context summary for debugging
    context_summary = agent.get_context_summary()

    # Get Google Places API key from environment
    import os
    google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")

    context = {
        "organization": organization,
        "context_summary": context_summary,
        "GOOGLE_PLACES_API_KEY": google_places_api_key,
    }

    return render(request, "ai_agent/chat.html", context)


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """
    API endpoint for sending messages to Nora.

    Request:
        {
            "message": "User's message text"
        }

    Response:
        {
            "message": "Nora's response",
            "data": {...},
            "action": "..."
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        # Parse request
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Initialize Nora and process message
        agent = NoraAgent(user=request.user, organization=organization)
        response = agent.process_message(user_message)

        # Check if we should trigger Google Places search
        # (when user provides hotel name + location in first interaction)
        if (agent.context.active_task == "onboarding" and
            response.get("action") == "show_extracted_data"):

            # Extract hotel name and location from response data
            extracted = response.get("data", {}).get("extracted", {})
            hotel_name = extracted.get("hotel_name")
            city = extracted.get("city")

            # If we have both, trigger Google Places search
            if hotel_name and city:
                response["action"] = "trigger_google_places_search"
                response["data"]["search_query"] = {
                    "hotel_name": hotel_name,
                    "location": city
                }

        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse(
            {
                "error": "Internal server error",
                "message": "I'm having trouble right now. Let's try again in a moment.",
            },
            status=500
        )


@login_required
@require_http_methods(["POST"])
def start_onboarding(request):
    """
    API endpoint to start the onboarding process.

    Response:
        {
            "message": "Nora's initial greeting",
            "data": {"step": "HOTEL_BASICS", "progress": 0},
            "action": "show_progress"
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        agent = NoraAgent(user=request.user, organization=organization)
        response = agent.start_onboarding()
        return JsonResponse(response)

    except Exception as e:
        return JsonResponse(
            {"error": "Failed to start onboarding", "details": str(e)},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def process_hotel_search(request):
    """
    Process initial hotel search from Google Places + Perplexity research.

    This endpoint is called immediately after Google Places finds the hotel.
    It saves the data and calls Perplexity, then returns a conversational
    address confirmation message.

    Request body:
        {
            "hotel_name": str,
            "full_address": str,
            "city": str,
            ... (all Google Places fields)
        }

    Response:
        {
            "address_message": "Got it, I have that address as...",
            "perplexity_data": {...}
        }
    """
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        import json
        data = json.loads(request.body)

        # Initialize Nora agent
        agent = NoraAgent(user=request.user, organization=organization)
        from apps.ai_agent.services.conversation_engine import OnboardingEngine
        from apps.ai_agent.services.perplexity_service import PerplexityService

        # Save Google Places data to task_state
        update_data = {
            "hotel_name": data.get("hotel_name"),
            "full_address": data.get("full_address"),
            "street_address": data.get("street_address"),
            "city": data.get("city"),
            "state": data.get("state"),
            "state_code": data.get("state_code"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "postal_code": data.get("postal_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "phone": data.get("phone"),
            "website": data.get("website"),
            "google_place_id": data.get("google_place_id"),
            "_awaiting_address_confirmation": True,  # Flag to track confirmation
        }

        # Auto-infer country if state is provided but country is not
        if data.get("state") and not data.get("country"):
            us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
            state_code = str(data.get("state_code", '')).upper()

            if state_code in us_states:
                update_data["country"] = "United States"
                update_data["country_code"] = "US"
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"✅ Auto-inferred country: United States (from state: {state_code})")

        agent.context.task_state.update(update_data)

        # Call Perplexity for hotel research (in parallel conceptually)
        perplexity = PerplexityService()
        hotel_info = perplexity.get_hotel_information(
            hotel_name=data.get("hotel_name"),
            location=data.get("city")
        )

        # Store Perplexity data temporarily (will be confirmed later)
        if "error" not in hotel_info:
            agent.context.task_state["_perplexity_pending"] = hotel_info

        agent.context.save()

        # Log the action
        agent.context.add_action("google_places_found", data)
        if "error" not in hotel_info:
            agent.context.add_action("perplexity_research_pending", hotel_info)

        # Generate conversational address confirmation message
        address_message = f"Got it! I found {data.get('hotel_name')} at {data.get('full_address')}. Is that correct?"

        return JsonResponse({
            "address_message": address_message,
            "perplexity_data": hotel_info if "error" not in hotel_info else None
        })

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing hotel search: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": "Failed to process hotel search", "details": str(e)},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def accept_hotel_details(request):
    """
    API endpoint to accept hotel details from Google Places.

    Request body:
        {
            "hotel_name": str,
            "full_address": str,
            "street_address": str,
            "city": str,
            "state": str,
            "state_code": str,
            "country": str,
            "country_code": str,
            "postal_code": str,
            "latitude": float,
            "longitude": float,
            "phone": str,
            "website": str,
            "google_place_id": str
        }

    Response:
        {
            "message": "Confirmation message",
            "progress": int,
            "state": str
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        import json
        data = json.loads(request.body)

        # Initialize Nora agent
        agent = NoraAgent(user=request.user, organization=organization)
        from apps.ai_agent.services.conversation_engine import OnboardingEngine
        from apps.ai_agent.services.perplexity_service import PerplexityService

        # Update task_state with hotel details from Google Places
        agent.context.task_state.update({
            "hotel_name": data.get("hotel_name"),
            "full_address": data.get("full_address"),
            "street_address": data.get("street_address"),
            "city": data.get("city"),
            "state": data.get("state"),
            "state_code": data.get("state_code"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "postal_code": data.get("postal_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "phone": data.get("phone"),
            "website": data.get("website"),
            "google_place_id": data.get("google_place_id"),
        })

        # Enrich with Perplexity AI research (web-grounded hotel information)
        perplexity = PerplexityService()
        hotel_info = perplexity.get_hotel_information(
            hotel_name=data.get("hotel_name"),
            location=data.get("city")
        )

        # Add Perplexity research to task_state (if successful)
        if "error" not in hotel_info:
            agent.context.task_state.update({
                "general_info": hotel_info.get("general_info"),
                "amenities": hotel_info.get("amenities", []),
                "unique_features": hotel_info.get("unique_features"),
                "target_audience": hotel_info.get("target_audience"),
                "price_range": hotel_info.get("price_range"),
                "hotel_style": hotel_info.get("hotel_style"),
                "notable_facts": hotel_info.get("notable_facts"),
            })

        # Save updated context
        agent.context.save()

        # Log the action
        agent.context.add_action("google_places_accepted", data)
        if "error" not in hotel_info:
            agent.context.add_action("perplexity_research_complete", hotel_info)

        # Check what's still missing
        engine = OnboardingEngine(agent.context.task_state)
        missing = engine.get_missing_fields()

        # Generate appropriate message based on what's missing
        # Human-friendly field names
        human_friendly = {
            'contact_email': 'your email address',
            'phone': 'a phone number',
            'website': 'your website',
            'state': 'the state/province',
            'country': 'the country',
            'full_address': 'the full address',
        }

        if missing and 'contact_email' in missing:
            # Only ask for contact email if it's the only thing missing
            if len(missing) == 1:
                message = f"Perfect! I've saved all the details for {data.get('hotel_name')}. Last thing I need - what's the best email to reach you at?"
                return JsonResponse({
                    "message": message,
                    "progress": 20,  # Almost done with hotel basics
                    "state": "HOTEL_BASICS"
                })
            else:
                # Multiple things missing, ask for them
                missing_friendly = [human_friendly.get(field, field.replace('_', ' ')) for field in missing]
                message = f"Great! I've got {data.get('hotel_name')}. I still need {', '.join(missing_friendly)}. Can you share those with me?"
                return JsonResponse({
                    "message": message,
                    "progress": 15,
                    "state": "HOTEL_BASICS"
                })
        else:
            # Hotel basics complete! Move to room types
            message = f"Perfect! I've got everything for {data.get('hotel_name')}. Now let's set up your room types. How many different types of rooms do you have?"
            return JsonResponse({
                "message": message,
                "progress": 25,  # Hotel basics complete
                "state": "ROOM_TYPES"
            })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to save hotel details", "details": str(e)},
            status=500
        )


@login_required
def welcome_view(request):
    """
    Welcome screen with static intro (no video for MVP).

    Shows:
    - Welcome message
    - What Nora can do
    - "Let's Go, Nora!" CTA button
    """
    return render(request, "ai_agent/welcome.html")


@login_required
@require_http_methods(["POST"])
def transcribe_audio(request):
    """
    API endpoint for transcribing voice to text.

    Request:
        - Multipart form with audio file

    Response:
        {
            "text": "Transcribed text",
            "language": "en",
            "duration": 5.2,
            "success": true
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    try:
        # Get audio file from request
        if 'audio' not in request.FILES:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        audio_file = request.FILES['audio']

        # Initialize voice handler
        voice_handler = VoiceHandler()

        # Validate audio file
        validation = voice_handler.validate_audio_file(audio_file)
        if not validation['valid']:
            return JsonResponse({"error": validation['error']}, status=400)

        # Transcribe audio
        result = voice_handler.transcribe_audio(audio_file)

        if not result['success']:
            return JsonResponse(
                {"error": "Transcription failed", "details": result.get('error')},
                status=500
            )

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def generate_voice(request):
    """
    API endpoint for generating voice from text.

    Request:
        {
            "text": "Text to speak",
            "voice": "nova",  # optional
            "speed": 1.0      # optional
        }

    Response:
        Audio file (mp3) as binary stream
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    try:
        # Parse request
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse({"error": "Text cannot be empty"}, status=400)

        # Get optional parameters
        voice = data.get("voice", None)
        speed = data.get("speed", None)

        # Initialize voice handler
        voice_handler = VoiceHandler()

        # Generate voice
        audio_bytes = voice_handler.generate_voice(text, voice=voice, speed=speed)

        if not audio_bytes:
            return JsonResponse({"error": "Voice generation failed"}, status=500)

        # Return audio as base64-encoded JSON (for frontend playback)
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return JsonResponse({
            "success": True,
            "audio_base64": audio_base64,
            "text": text
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )


@login_required
@require_http_methods(["POST"])
def voice_message(request):
    """
    Complete voice interaction: transcribe input, process with Nora, generate voice response.

    Request:
        - Multipart form with audio file

    Response:
        {
            "transcribed_text": "What the user said",
            "message": "Nora's text response",
            "audio_url": "/api/nora/voice/response/<session_id>",
            "data": {...},
            "action": "..."
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        # Get audio file from request
        if 'audio' not in request.FILES:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        audio_file = request.FILES['audio']

        # Initialize handlers
        voice_handler = VoiceHandler()
        agent = NoraAgent(user=request.user, organization=organization)

        # 1. Transcribe audio to text
        transcription = voice_handler.transcribe_audio(audio_file)

        if not transcription['success']:
            return JsonResponse(
                {"error": "Transcription failed", "details": transcription.get('error')},
                status=500
            )

        transcribed_text = transcription['text']

        # 2. Process message with Nora
        response = agent.process_message(transcribed_text)

        # 3. Generate voice response
        audio_bytes = voice_handler.generate_voice(response['message'])

        # 4. Return both text and audio
        # For simplicity, we'll return audio as base64 for now
        # In production, could save to temp storage and return URL
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return JsonResponse({
            "transcribed_text": transcribed_text,
            "message": response['message'],
            "audio_base64": audio_base64,
            "data": response.get('data', {}),
            "action": response.get('action')
        })

    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )


# ============================================================================
# PHASE 5: EDIT CONTROLS - Structured Edit Modals
# ============================================================================

@login_required
@require_http_methods(["GET"])
def get_edit_payment_policy_modal(request):
    """
    Return HTML for payment policy edit modal.

    User edits structured data (deposit %, timing), NOT the formatted text.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Get current session data
    agent = NoraAgent(user=request.user, organization=organization)
    task_state = agent.context.task_state

    context = {
        "deposit_amount": task_state.get("deposit_amount", 50),
        "deposit_timing": task_state.get("deposit_timing", "at_booking"),
        "balance_timing": task_state.get("balance_timing", "on_arrival"),
    }

    return render(request, "ai_agent/modals/edit_payment_policy.html", context)


@login_required
@require_http_methods(["POST"])
def save_payment_policy(request):
    """
    Save payment policy changes and return updated preview text.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        data = json.loads(request.body)
        deposit_amount = data.get("deposit_amount")
        deposit_timing = data.get("deposit_timing")
        balance_timing = data.get("balance_timing")

        # Update task state
        agent = NoraAgent(user=request.user, organization=organization)
        agent.context.task_state["deposit_amount"] = deposit_amount
        agent.context.task_state["deposit_timing"] = deposit_timing
        agent.context.task_state["balance_timing"] = balance_timing
        agent.context.save()

        # Generate formatted preview text using ContentFormatter
        from apps.ai_agent.services.content_formatter import ContentFormatter
        formatter = ContentFormatter()

        formatted_text = formatter.format_payment_policy(
            deposit_amount=deposit_amount,
            deposit_timing=deposit_timing,
            balance_timing=balance_timing
        )

        return JsonResponse({
            "success": True,
            "formatted_text": formatted_text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_edit_cancellation_policy_modal(request):
    """
    Return HTML for cancellation policy edit modal.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Get current session data
    agent = NoraAgent(user=request.user, organization=organization)
    task_state = agent.context.task_state

    context = {
        "cancellation_policy": task_state.get("cancellation_policy", "free_72h"),
        "cancellation_fee": task_state.get("cancellation_fee", 0),
    }

    return render(request, "ai_agent/modals/edit_cancellation_policy.html", context)


@login_required
@require_http_methods(["POST"])
def save_cancellation_policy(request):
    """
    Save cancellation policy changes.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        data = json.loads(request.body)
        policy = data.get("cancellation_policy")
        fee = data.get("cancellation_fee", 0)

        # Update task state
        agent = NoraAgent(user=request.user, organization=organization)
        agent.context.task_state["cancellation_policy"] = policy
        agent.context.task_state["cancellation_fee"] = fee
        agent.context.save()

        # Generate formatted preview text
        from apps.ai_agent.services.content_formatter import ContentFormatter
        formatter = ContentFormatter()

        formatted_text = formatter.format_cancellation_policy(
            policy_type=policy,
            fee_amount=fee
        )

        return JsonResponse({
            "success": True,
            "formatted_text": formatted_text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_edit_checkin_times_modal(request):
    """
    Return HTML for check-in/check-out times edit modal.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Get current session data
    agent = NoraAgent(user=request.user, organization=organization)
    task_state = agent.context.task_state

    context = {
        "checkin_time": task_state.get("checkin_time", "15:00"),
        "checkout_time": task_state.get("checkout_time", "11:00"),
    }

    return render(request, "ai_agent/modals/edit_checkin_times.html", context)


@login_required
@require_http_methods(["POST"])
def save_checkin_times(request):
    """
    Save check-in/check-out times.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        data = json.loads(request.body)
        checkin = data.get("checkin_time")
        checkout = data.get("checkout_time")

        # Update task state
        agent = NoraAgent(user=request.user, organization=organization)
        agent.context.task_state["checkin_time"] = checkin
        agent.context.task_state["checkout_time"] = checkout
        agent.context.save()

        return JsonResponse({
            "success": True,
            "checkin_time": checkin,
            "checkout_time": checkout
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def generate_policy_preview(request):
    """
    Generate live preview of policy text as user types.

    Used for real-time updates in edit modals.
    """
    try:
        data = json.loads(request.body)
        preview_type = data.get("type")  # 'payment' or 'cancellation'

        from apps.ai_agent.services.content_formatter import ContentFormatter
        formatter = ContentFormatter()

        if preview_type == "payment":
            formatted_text = formatter.format_payment_policy(
                deposit_amount=data.get("deposit_amount"),
                deposit_timing=data.get("deposit_timing"),
                balance_timing=data.get("balance_timing")
            )
        elif preview_type == "cancellation":
            formatted_text = formatter.format_cancellation_policy(
                policy_type=data.get("cancellation_policy"),
                fee_amount=data.get("cancellation_fee", 0)
            )
        else:
            return JsonResponse({"error": "Invalid preview type"}, status=400)

        return JsonResponse({
            "success": True,
            "formatted_text": formatted_text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================================
# PHASE 4.5: PROGRESS TRACKER - API Endpoints
# ============================================================================

@login_required
@require_http_methods(["GET"])
def get_progress(request):
    """
    Return updated progress tracker HTML for HTMX polling.

    This endpoint is called periodically to update the progress tracker
    as the user completes onboarding steps.
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return HttpResponse("")

    staff = request.user.staff_positions.first()
    organization = staff.organization

    # Get NoraContext
    agent = NoraAgent(user=request.user, organization=organization)

    if agent.context.active_task == 'onboarding':
        from apps.ai_agent.services.conversation_engine import OnboardingEngine
        engine = OnboardingEngine(agent.context.task_state)
        progress_data = engine.get_progress_data()

        return render(request, "ai_agent/partials/progress_tracker.html", {'progress': progress_data})

    return HttpResponse("")


@login_required
@require_http_methods(["POST"])
def accept_field(request):
    """
    User accepted a field value - mark as confirmed.

    Request body:
        {
            "field": "hotel_name",
            "value": "Paradise Beach Resort"
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")

        # Update context
        agent = NoraAgent(user=request.user, organization=organization)

        # Mark field as confirmed (add to metadata)
        if not agent.context.task_state.get("_confirmed_fields"):
            agent.context.task_state["_confirmed_fields"] = []

        if field not in agent.context.task_state["_confirmed_fields"]:
            agent.context.task_state["_confirmed_fields"].append(field)

        agent.context.save()

        # Log the action
        agent.context.add_action("field_accepted", {"field": field, "value": value})

        # Human-friendly field names
        human_friendly = {
            'contact_email': 'email address',
            'hotel_name': 'hotel name',
            'city': 'city',
            'state': 'state/province',
            'country': 'country',
            'phone': 'phone number',
            'website': 'website',
            'full_address': 'address',
            'street_address': 'street address',
        }

        field_display = human_friendly.get(field, field.replace('_', ' '))

        return JsonResponse({
            "success": True,
            "field": field,
            "value": value,
            "message": f"Perfect! I've confirmed your {field_display}."
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_field(request):
    """
    User modified a field value - update and save.

    Request body:
        {
            "field": "hotel_name",
            "value": "New Hotel Name"
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization"}, status=403)

    staff = request.user.staff_positions.first()
    organization = staff.organization

    try:
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")

        if not field or not value:
            return JsonResponse({"error": "Missing field or value"}, status=400)

        # Update context
        agent = NoraAgent(user=request.user, organization=organization)

        # Store old value for logging
        old_value = agent.context.task_state.get(field)

        # Update the field
        agent.context.task_state[field] = value

        # Mark field as confirmed
        if not agent.context.task_state.get("_confirmed_fields"):
            agent.context.task_state["_confirmed_fields"] = []

        if field not in agent.context.task_state["_confirmed_fields"]:
            agent.context.task_state["_confirmed_fields"].append(field)

        agent.context.save()

        # Log the action
        agent.context.add_action("field_updated", {
            "field": field,
            "old_value": old_value,
            "new_value": value
        })

        # Generate friendly field name
        field_name = field.replace('_', ' ').title()

        return JsonResponse({
            "success": True,
            "field": field,
            "value": value,
            "message": f"Great! I've updated your {field_name} to \"{value}\"."
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================================================================
# PHASE 6: INTEGRATION & POLISH - Onboarding Completion
# ============================================================================

@login_required
@require_http_methods(["POST"])
def complete_onboarding(request):
    """
    Complete onboarding and generate Hotel/RoomType/Room records.
    
    This endpoint is called when the user finishes the onboarding flow
    (either automatically when COMPLETE state is reached, or manually
    via "Launch My Hotel" button).
    
    Returns:
        {
            "success": True/False,
            "hotel_id": UUID,
            "hotel_slug": "sunset-villa",
            "hotel_url": "https://sunset-villa.stayfull.com",
            "stats": {...},
            "redirect_url": "/nora/success/"
        }
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return JsonResponse({"error": "No organization associated with user"}, status=403)
    
    staff = request.user.staff_positions.first()
    organization = staff.organization
    
    try:
        # Get Nora context
        agent = NoraAgent(user=request.user, organization=organization)
        
        if agent.context.active_task != 'onboarding':
            return JsonResponse({
                "error": "Not currently in onboarding",
                "active_task": agent.context.active_task
            }, status=400)
        
        # Generate hotel from onboarding data
        generator = DataGenerator(user=request.user, organization=organization)
        result = generator.generate_hotel_from_onboarding(agent.context)
        
        if not result['success']:
            return JsonResponse({
                "error": "Failed to generate hotel",
                "details": result.get('errors', [])
            }, status=500)
        
        hotel = result['hotel']

        # Mark onboarding as complete (clear task_state now that hotel is generated)
        agent.context.task_state['hotel_id'] = str(hotel.id)
        agent.context.task_state['onboarding_completed_at'] = timezone.now().isoformat()
        agent.context.save()

        # NOW clear the task (hotel is safely in database)
        agent.context.complete_task()

        # Construct hotel URL (in production, would use actual domain)
        hotel_url = f"https://{hotel.slug}.stayfull.com"  # Placeholder

        return JsonResponse({
            "success": True,
            "hotel_id": str(hotel.id),
            "hotel_slug": hotel.slug,
            "hotel_name": hotel.name,
            "hotel_url": hotel_url,
            "stats": result['stats'],
            "redirect_url": "/nora/success/"
        })
    
    except Exception as e:
        return JsonResponse({
            "error": "Internal server error",
            "details": str(e)
        }, status=500)


@login_required
def success_view(request):
    """
    Success page after onboarding completion.
    
    Shows:
    - Hotel name and URL
    - Stats (rooms created, room types, etc.)
    - Next steps
    - "Take me to dashboard" button
    """
    # Get user's organization
    if not hasattr(request.user, "staff_positions") or not request.user.staff_positions.exists():
        return render(request, "ai_agent/no_organization.html")
    
    staff = request.user.staff_positions.first()
    organization = staff.organization
    
    # Get Nora context to retrieve hotel info
    agent = NoraAgent(user=request.user, organization=organization)
    
    # Get hotel from context (if just completed)
    hotel_id = agent.context.task_state.get('hotel_id')
    
    if not hotel_id:
        # No hotel found - redirect to welcome
        return redirect('/nora/welcome/')
    
    from apps.hotels.models import Hotel
    try:
        hotel = Hotel.objects.get(id=hotel_id, organization=organization)
    except Hotel.DoesNotExist:
        return redirect('/nora/welcome/')
    
    # Get stats
    room_types = hotel.room_types.count()
    total_rooms = hotel.rooms.count()
    
    context = {
        'hotel': hotel,
        'hotel_url': f"https://{hotel.slug}.stayfull.com",  # Placeholder
        'stats': {
            'room_types': room_types,
            'total_rooms': total_rooms,
            'completion_time': '10 minutes'  # Could calculate from timestamps
        },
        'onboarding_completed_at': agent.context.task_state.get('onboarding_completed_at')
    }
    
    return render(request, "ai_agent/success.html", context)
