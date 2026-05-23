# ============================================================================
# ICG PACKAGE - Intermediate Code Generation (Three-Address Code, display-only)
# ============================================================================
# Re-exports generate_icg so external callers (server.py) can keep using:
#     from icg import generate_icg
# unchanged after the restructure.
# ============================================================================

from .generator import generate_icg, ICGenerator, TACInstruction  # noqa: F401
