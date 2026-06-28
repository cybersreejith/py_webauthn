from typing import Any, Dict, Optional

from webauthn.helpers.exceptions import InvalidExtensionResults

from .cred_props import CredPropsOutput
from .models import ClientExtensionResults


def parse_client_extension_results(
    raw: Optional[Dict[str, Any]],
) -> Optional[ClientExtensionResults]:

    if not raw:
        return None

    result = ClientExtensionResults()
    found_any = False

    # Parse credProps if present
    if "credProps" in raw:
        value = raw["credProps"]
        if not isinstance(value, dict):
            raise InvalidExtensionResults("credProps must be an object")
        rk = value.get("rk")
        if rk is not None and not isinstance(rk, bool):
            raise InvalidExtensionResults("credProps.rk must be a boolean")
        result.cred_props = CredPropsOutput(rk=rk)
        found_any = True

    return result if found_any else None

