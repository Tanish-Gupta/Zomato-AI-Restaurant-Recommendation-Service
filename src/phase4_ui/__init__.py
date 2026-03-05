"""Phase 4: User Interface - Gradio web application."""

from .recommend_logic import get_cuisines, get_locations, recommend

__all__ = ["get_cuisines", "get_locations", "recommend"]

# Optional Gradio UI (import separately to avoid pulling in gradio when unused)
def __getattr__(name):
    if name in ("build_ui", "run_ui"):
        from .gradio_app import build_ui, run_ui
        return run_ui if name == "run_ui" else build_ui
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
