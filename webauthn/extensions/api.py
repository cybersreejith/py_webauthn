from typing import Any, Dict, Optional


def normalize_extension_inputs(raw: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Pass extension inputs through unchanged.

    `credProps` input is simply the boolean ``True`` per spec §10.4 — no
    normalization is required.  This function exists as an extension point so
    future extensions that need server-side normalization can be handled here
    without touching the option generators.
    """
    if not raw:
        return None
    return dict(raw)

