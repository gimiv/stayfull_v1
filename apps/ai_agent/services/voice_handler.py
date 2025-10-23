"""
Voice Handler - Speech-to-Text and Text-to-Speech

Handles voice interactions with Nora using:
1. Whisper API for speech-to-text (voice input)
2. OpenAI TTS API for text-to-speech (voice output)

Features:
- Audio transcription with language detection
- Voice generation with customizable persona
- Error handling and fallbacks
- Audio file format conversion
"""

from typing import Optional, Dict, BinaryIO
import io
import os
from pathlib import Path

from .openai_config import get_openai_client, VOICE_CONFIG


class VoiceHandler:
    """
    Handle voice input/output for Nora.

    Usage:
        handler = VoiceHandler()

        # Speech to text
        text = handler.transcribe_audio(audio_file)

        # Text to speech
        audio_bytes = handler.generate_voice(text)
    """

    def __init__(self):
        self.client = get_openai_client()
        self.voice_name = VOICE_CONFIG["tts_voice"]
        self.tts_model = VOICE_CONFIG["tts_model"]
        self.tts_speed = VOICE_CONFIG["tts_speed"]
        self.whisper_model = VOICE_CONFIG["model"]

    def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: str = "en",
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_file: Audio file object (wav, mp3, m4a, webm, etc.) or Django UploadedFile
            language: Language code (default: "en")
            prompt: Optional prompt to guide transcription

        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected language
                - duration: Audio duration in seconds (if available)
                - confidence: Transcription confidence (if available)
        """
        try:
            # Handle Django UploadedFile objects
            # OpenAI client expects (filename, file_content, mime_type) tuple
            if hasattr(audio_file, 'read') and hasattr(audio_file, 'name'):
                # Django UploadedFile - convert to tuple format
                file_content = audio_file.read()
                filename = getattr(audio_file, 'name', 'audio.webm')

                # Reset file pointer if it's seekable (for potential reuse)
                if hasattr(audio_file, 'seek'):
                    try:
                        audio_file.seek(0)
                    except:
                        pass

                # Create tuple format expected by OpenAI
                file_tuple = (filename, file_content, 'audio/webm')
            else:
                # Already in correct format
                file_tuple = audio_file

            # Call Whisper API
            transcription = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=file_tuple,
                language=language,
                response_format="verbose_json",  # Get detailed info
                prompt=prompt  # Optional context for better accuracy
            )

            return {
                "text": transcription.text,
                "language": transcription.language if hasattr(transcription, 'language') else language,
                "duration": transcription.duration if hasattr(transcription, 'duration') else None,
                "success": True
            }

        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

    def generate_voice(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None
    ) -> bytes:
        """
        Generate voice audio from text using OpenAI TTS.

        Args:
            text: Text to convert to speech
            voice: Voice name (default: from config, usually "nova")
            speed: Speech speed 0.25-4.0 (default: from config, usually 1.0)

        Returns:
            Audio bytes (mp3 format)
        """
        voice = voice or self.voice_name
        speed = speed or self.tts_speed

        try:
            # Call TTS API
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Stream audio bytes
            audio_bytes = b""
            for chunk in response.iter_bytes():
                audio_bytes += chunk

            return audio_bytes

        except Exception as e:
            print(f"TTS generation error: {e}")
            # Return empty bytes on error
            return b""

    def generate_voice_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None
    ):
        """
        Generate voice audio with streaming (for faster playback start).

        Args:
            text: Text to convert to speech
            voice: Voice name
            speed: Speech speed

        Yields:
            Audio chunks as they're generated
        """
        voice = voice or self.voice_name
        speed = speed or self.tts_speed

        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Stream chunks
            for chunk in response.iter_bytes():
                yield chunk

        except Exception as e:
            print(f"TTS streaming error: {e}")
            yield b""

    def save_audio_file(
        self,
        audio_bytes: bytes,
        output_path: str,
        format: str = "mp3"
    ) -> bool:
        """
        Save audio bytes to file.

        Args:
            audio_bytes: Audio data
            output_path: Path to save file
            format: Audio format (mp3, wav, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Write audio file
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            return True

        except Exception as e:
            print(f"Error saving audio file: {e}")
            return False

    def validate_audio_file(self, audio_file: BinaryIO) -> Dict:
        """
        Validate audio file format and size.

        Args:
            audio_file: Audio file object

        Returns:
            Dict with:
                - valid: bool
                - error: str (if invalid)
                - size_mb: float
        """
        try:
            # Check file size
            audio_file.seek(0, 2)  # Seek to end
            size_bytes = audio_file.tell()
            audio_file.seek(0)  # Reset to beginning

            size_mb = size_bytes / (1024 * 1024)

            # OpenAI limits: 25MB for Whisper
            max_size_mb = 25

            if size_mb > max_size_mb:
                return {
                    "valid": False,
                    "error": f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)",
                    "size_mb": size_mb
                }

            # Check file has content
            if size_bytes == 0:
                return {
                    "valid": False,
                    "error": "File is empty",
                    "size_mb": 0
                }

            return {
                "valid": True,
                "size_mb": size_mb
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "size_mb": 0
            }

    def set_voice(self, voice_name: str):
        """
        Change the TTS voice.

        Args:
            voice_name: One of OpenAI's TTS voices:
                - alloy (neutral)
                - echo (male)
                - fable (neutral)
                - onyx (male)
                - nova (female, clear) <- Default for Nora
                - shimmer (female, warm)
        """
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        if voice_name in valid_voices:
            self.voice_name = voice_name
        else:
            raise ValueError(f"Invalid voice. Choose from: {', '.join(valid_voices)}")

    def set_speed(self, speed: float):
        """
        Change the TTS speed.

        Args:
            speed: Speech speed (0.25 to 4.0)
                - 0.5 = half speed (very slow)
                - 1.0 = normal speed (default)
                - 1.5 = 1.5x speed (faster)
                - 2.0 = double speed (very fast)
        """
        if 0.25 <= speed <= 4.0:
            self.tts_speed = speed
        else:
            raise ValueError("Speed must be between 0.25 and 4.0")

    def get_voice_info(self) -> Dict:
        """
        Get current voice configuration.

        Returns:
            Dict with voice settings
        """
        return {
            "voice": self.voice_name,
            "speed": self.tts_speed,
            "model": self.tts_model,
            "whisper_model": self.whisper_model
        }
