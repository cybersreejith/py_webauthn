from dataclasses import dataclass
from typing import Optional


@dataclass
class CredentialPropertiesOutput:
    """Output of the credProps extension (registration only, spec §10.4).

    `rk` is:
    - True  — credential is a client-side discoverable credential (passkey)
    - False — credential is a server-side credential
    - None  — browser could not determine discoverability
    """

    rk: Optional[bool] = None


@dataclass
class ClientExtensionResults:
    cred_props: Optional[CredentialPropertiesOutput] = None

