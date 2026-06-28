from typing import Any, Dict, Optional

from webauthn.helpers.exceptions import InvalidExtensionResults

from .models import ClientExtensionResults, CredentialPropertiesOutput


def parse_client_extension_results(raw: Optional[Dict[str, Any]]) -> Optional[ClientExtensionResults]:
    """Parse clientExtensionResults into typed models.

    Supported extension (first pass):
    - ``credProps`` (registration, spec §10.4) — exposes whether the created
      credential is a client-side discoverable credential via the ``rk`` flag.

    Future extensions can be added here without breaking existing callers.
    """
    if not raw:
        return None

    # ---- credProps --------------------------------------------------------
    # Input:  True  (caller just requests it; browser handles the rest)
    # Output: {"rk": <bool|None>}
    cred_props = raw.get("credProps")
    if isinstance(cred_props, dict):
        rk = cred_props.get("rk")
        if rk is not None and not isinstance(rk, bool):
            raise InvalidExtensionResults("credProps.rk must be a boolean")
        return ClientExtensionResults(cred_props=CredentialPropertiesOutput(rk=rk))

    return None

