# ============================================================================
# CFG PACKAGE - Context-free grammar + parse table for the GAL parser
# ============================================================================
# Re-exports the three public artifacts so `from cfg import cfg, first_sets,
# predict_sets` keeps working unchanged after the restructure.
# ============================================================================

from .grammar import (  # noqa: F401
    cfg,
    first_sets,
    predict_sets,
    compute_first,
    compute_follow,
    compute_predict,
)
