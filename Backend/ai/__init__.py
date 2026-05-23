# ============================================================================
# AI PACKAGE - Chat-helper layer (Gemini integration + regex fallback)
# ============================================================================
# Contents:
#   fallback.py - rule-based regex/keyword responder used when Gemini is
#                 unavailable or rate-limited.
#   prompt.txt  - system prompt that teaches the LLM how to talk about GAL.
#
# This package is NOT part of the compiler pipeline; server.py consumes it
# only for the in-IDE "Ask" chat helper.
# ============================================================================

from .fallback import fallback_reply  # noqa: F401
