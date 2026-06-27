from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class CredentialProtectionPolicy(Enum):
    USER_VERIFICATION_OPTIONAL = 1
    USER_VERIFICATION_OPTIONAL_WITH_LIST = 2
    USER_VERIFICATION_REQUIRED = 3


@dataclass
class CredentialPropertiesExtension:
    rk: bool


@dataclass
class CredentialProtectionExtension:
    policy: CredentialProtectionPolicy


@dataclass
class UserVerificationMethod:
    method: int
    key_protection: int
    matcher_protection: int


@dataclass
class LargeBlobExtension:
    supported: Optional[bool] = None
    blob: Optional[bytes] = None


@dataclass
class HmacSecretExtension:
    enabled: Optional[bool] = None


@dataclass
class PrfExtension:
    value: Optional[Any] = None


@dataclass
class AppIdExtension:
    appid: Optional[bool] = None


@dataclass
class ClientExtensionResults:
    cred_props: Optional[CredentialPropertiesExtension] = None
    uvm: Optional[List[UserVerificationMethod]] = None
    cred_protect: Optional[CredentialProtectionExtension] = None
    large_blob: Optional[LargeBlobExtension] = None
    hmac_secret: Optional[HmacSecretExtension] = None
    prf: Optional[PrfExtension] = None
    appid: Optional[AppIdExtension] = None
