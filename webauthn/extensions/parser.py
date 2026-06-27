from typing import Any, Dict, Optional

from webauthn.helpers.exceptions import InvalidExtensionResults

from .models import (
    AppIdExtension,
    ClientExtensionResults,
    CredentialPropertiesExtension,
    CredentialProtectionExtension,
    CredentialProtectionPolicy,
    HmacSecretExtension,
    LargeBlobExtension,
    PrfExtension,
    UserVerificationMethod,
)


def parse_client_extension_results(raw: Optional[Dict[str, Any]]) -> Optional[ClientExtensionResults]:
    if not raw:
        return None

    extensions = ClientExtensionResults()
    parsed_any = False

    cred_props = raw.get("credProps")
    if isinstance(cred_props, dict) and "rk" in cred_props:
        rk = cred_props["rk"]
        if isinstance(rk, bool):
            extensions.cred_props = CredentialPropertiesExtension(rk=rk)
            parsed_any = True
        else:
            raise InvalidExtensionResults("credProps.rk must be boolean")

    uvm = raw.get("uvm")
    if isinstance(uvm, list):
        parsed_uvm = []
        for entry in uvm:
            if isinstance(entry, list) and len(entry) == 3:
                method, key_protection, matcher_protection = entry
                if all(isinstance(item, int) for item in entry):
                    parsed_uvm.append(
                        UserVerificationMethod(
                            method=method,
                            key_protection=key_protection,
                            matcher_protection=matcher_protection,
                        )
                    )
                else:
                    raise InvalidExtensionResults("uvm entries must be integers")
            else:
                raise InvalidExtensionResults(
                    "uvm must be a list of [method, key_protection, matcher_protection] arrays"
                )
        extensions.uvm = parsed_uvm
        parsed_any = True

    cred_protect = raw.get("credProtect")
    if isinstance(cred_protect, dict):
        policy_value = cred_protect.get("credentialProtectionPolicy")
        if policy_value is not None:
            try:
                policy = CredentialProtectionPolicy(policy_value)
            except ValueError as exc:
                raise InvalidExtensionResults(
                    "credentialProtectionPolicy has an unsupported value"
                ) from exc
            extensions.cred_protect = CredentialProtectionExtension(policy=policy)
            parsed_any = True

    large_blob = raw.get("largeBlob")
    if isinstance(large_blob, dict):
        supported = large_blob.get("supported")
        blob = large_blob.get("blob")
        if supported is not None and not isinstance(supported, bool):
            raise InvalidExtensionResults("largeBlob.supported must be boolean")
        if blob is not None and not isinstance(blob, (bytes, bytearray)):
            raise InvalidExtensionResults("largeBlob.blob must be bytes")
        extensions.large_blob = LargeBlobExtension(
            supported=supported,
            blob=bytes(blob) if blob is not None else None,
        )
        parsed_any = True

    hmac_secret = raw.get("hmac-secret")
    if isinstance(hmac_secret, dict):
        enabled = hmac_secret.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            raise InvalidExtensionResults("hmac-secret.enabled must be boolean")
        extensions.hmac_secret = HmacSecretExtension(enabled=enabled)
        parsed_any = True

    prf = raw.get("prf")
    if isinstance(prf, dict):
        extensions.prf = PrfExtension(value=prf)
        parsed_any = True

    appid = raw.get("appid")
    if appid is not None:
        if isinstance(appid, bool):
            extensions.appid = AppIdExtension(appid=appid)
            parsed_any = True
        else:
            raise InvalidExtensionResults("appid must be boolean")

    return extensions if parsed_any else None
