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

    # Future extension parsers go here. Example:
    #
    # if "uvm" in raw:
    #     value = raw["uvm"]
    #     if not isinstance(value, list):
    #         raise InvalidExtensionResults("uvm must be an array")
    #     result.uvm = [parse_uvm_entry(entry) for entry in value]
    #     found_any = True

    return result if found_any else None

