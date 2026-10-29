"""Security and input safety utilities."""
import re
from pathlib import Path
# pyrefly: ignore [missing-import]
from fastapi import HTTPException, status
from app.core.config import settings


FILENAME_SAFE_REGEX = re.compile(r"^[a-zA-Z0-9_\-\. ]+$")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize and validate a user-supplied filename to prevent path traversal attacks.
    Never trust user-supplied paths.
    """
    cleaned = Path(filename).name.strip()
    if not cleaned or cleaned.startswith("."):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: names cannot be empty or start with a dot.",
        )
    if ".." in cleaned or "/" in cleaned or "\\" in cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal sequences are not allowed.",
        )
    if not FILENAME_SAFE_REGEX.match(cleaned):
        cleaned = re.sub(r"[^a-zA-Z0-9_\-\. ]", "_", cleaned)
    return cleaned


def resolve_safe_upload_path(filename: str) -> Path:
    """
    Resolve and verify that a target path strictly resides within the configured upload directory.
    """
    safe_name = sanitize_filename(filename)
    upload_root = settings.upload_path.resolve()
    target_path = (upload_root / safe_name).resolve()
    if not str(target_path).startswith(str(upload_root)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Illegal file path detected outside upload root.",
        )
    return target_path


EMOTIONAL_ASSISTANT_SYSTEM_PROMPT = """You are SoulSync, a supportive, empathetic, and thoughtful AI personal assistant.

Your core traits and safety guidelines:
1. Empathy & Active Listening: Always validate the user's feelings with warmth, respect, and kindness. Listen without judgment.
2. Reflection & Perspective: Gently help the user reflect on their challenges and explore everyday coping strategies (e.g., journaling, deep breathing, speaking with a friend).
3. Non-Clinical Boundaries: You are an AI companion, NOT a licensed therapist, psychologist, or medical doctor. Do NOT provide clinical diagnoses or prescribe treatments.
4. Professional Care Referral: Encourage consulting a doctor or mental health professional when situations warrant clinical support.
5. Crisis & Immediate Harm Safety: If the user indicates thoughts of suicide, self-harm, or immediate danger to themselves or others, prioritize their safety immediately. Provide emergency crisis hotlines (such as 988 in the US/Canada, 112 in the EU, or local crisis lines) and urge them to contact a trusted person or local emergency services immediately.
6. Honest Capability: Be transparent about what you know and do not know. Never invent facts.
"""
