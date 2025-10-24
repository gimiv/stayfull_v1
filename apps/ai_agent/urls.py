"""
URL configuration for Nora AI Agent
"""

from django.urls import path
from . import views

app_name = "ai_agent"

urlpatterns = [
    # Welcome/intro screen
    path("welcome/", views.welcome_view, name="welcome"),

    # Main chat interface
    path("chat/", views.chat_view, name="chat"),

    # API endpoints - Text
    path("api/message/", views.send_message, name="send_message"),
    path("api/start-onboarding/", views.start_onboarding, name="start_onboarding"),
    path("api/process-hotel-search/", views.process_hotel_search, name="process_hotel_search"),
    path("api/accept-hotel-details/", views.accept_hotel_details, name="accept_hotel_details"),

    # API endpoints - Voice
    path("api/voice/transcribe/", views.transcribe_audio, name="transcribe_audio"),
    path("api/voice/generate/", views.generate_voice, name="generate_voice"),
    path("api/voice/message/", views.voice_message, name="voice_message"),

    # API endpoints - Edit Modals (Phase 5)
    path("api/edit/payment-policy/", views.get_edit_payment_policy_modal, name="get_edit_payment_policy_modal"),
    path("api/save/payment-policy/", views.save_payment_policy, name="save_payment_policy"),
    path("api/edit/cancellation-policy/", views.get_edit_cancellation_policy_modal, name="get_edit_cancellation_policy_modal"),
    path("api/save/cancellation-policy/", views.save_cancellation_policy, name="save_cancellation_policy"),
    path("api/edit/checkin-times/", views.get_edit_checkin_times_modal, name="get_edit_checkin_times_modal"),
    path("api/save/checkin-times/", views.save_checkin_times, name="save_checkin_times"),
    path("api/preview/policy/", views.generate_policy_preview, name="generate_policy_preview"),

    # API endpoints - Progress Tracker (Phase 4.5)
    path("api/progress/", views.get_progress, name="get_progress"),
    path("api/accept-field/", views.accept_field, name="accept_field"),
    path("api/update-field/", views.update_field, name="update_field"),

    # API endpoints - Integration & Polish (Phase 6)
    path("api/complete-onboarding/", views.complete_onboarding, name="complete_onboarding"),
    path("success/", views.success_view, name="success"),
]
