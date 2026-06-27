import re
from unittest import TestCase

from webauthn.extensions import (
    AppIdExtension,
    ClientExtensionResults,
    CredentialPropertiesExtension,
    CredentialProtectionExtension,
    CredentialProtectionPolicy,
    HmacSecretExtension,
    LargeBlobExtension,
    PrfExtension,
    UserVerificationMethod,
    parse_client_extension_results,
)
from webauthn.helpers.exceptions import InvalidExtensionResults
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json


class TestWebAuthnExtensions(TestCase):
    def test_parse_registration_credential_client_extension_results(self) -> None:
        credential = parse_registration_credential_json(
            {
                "id": "credential-id",
                "rawId": "Y3JlZGVudGlhbC1pZA",
                "response": {
                    "clientDataJSON": "Y2xpZW50LWRhdGE",
                    "attestationObject": "YXR0ZXN0YXRpb24tb2JqZWN0",
                    "clientExtensionResults": {"credProps": {"rk": True}},
                },
                "type": "public-key",
            }
        )

        self.assertEqual(
            credential.response.client_extension_results,
            {"credProps": {"rk": True}},
        )

    def test_parse_authentication_credential_client_extension_results(self) -> None:
        credential = parse_authentication_credential_json(
            {
                "id": "credential-id",
                "rawId": "Y3JlZGVudGlhbC1pZA",
                "response": {
                    "clientDataJSON": "Y2xpZW50LWRhdGE",
                    "authenticatorData": "YXV0aGVudGljYXRvci1kYXRh",
                    "signature": "c2lnbmF0dXJl",
                    "clientExtensionResults": {"credProtect": {"credentialProtectionPolicy": 3}},
                },
                "type": "public-key",
            }
        )

        self.assertEqual(
            credential.response.client_extension_results,
            {"credProtect": {"credentialProtectionPolicy": 3}},
        )

    def test_parse_client_extension_results_supports_all_extensions(self) -> None:
        extensions = parse_client_extension_results(
            {
                "credProps": {"rk": True},
                "uvm": [[1, 2, 3]],
                "credProtect": {"credentialProtectionPolicy": 3},
                "largeBlob": {"supported": True, "blob": b"abc"},
                "hmac-secret": {"enabled": True},
                "prf": {"enabled": True, "results": {"first": "abc"}},
                "appid": True,
            }
        )

        self.assertEqual(
            extensions,
            ClientExtensionResults(
                cred_props=CredentialPropertiesExtension(rk=True),
                uvm=[UserVerificationMethod(method=1, key_protection=2, matcher_protection=3)],
                cred_protect=CredentialProtectionExtension(
                    policy=CredentialProtectionPolicy.USER_VERIFICATION_REQUIRED
                ),
                large_blob=LargeBlobExtension(supported=True, blob=b"abc"),
                hmac_secret=HmacSecretExtension(enabled=True),
                prf=PrfExtension(value={"enabled": True, "results": {"first": "abc"}}),
                appid=AppIdExtension(appid=True),
            ),
        )

    def test_parse_client_extension_results_rejects_invalid_values(self) -> None:
        invalid_cases = [
            ({"credProps": {"rk": "yes"}}, "credProps.rk must be boolean"),
            ({"uvm": [[1, 2]]}, "uvm must be a list of [method, key_protection, matcher_protection] arrays"),
            ({"credProtect": {"credentialProtectionPolicy": 99}}, "credentialProtectionPolicy has an unsupported value"),
            ({"largeBlob": {"supported": "yes"}}, "largeBlob.supported must be boolean"),
            ({"largeBlob": {"blob": "abc"}}, "largeBlob.blob must be bytes"),
            ({"hmac-secret": {"enabled": "yes"}}, "hmac-secret.enabled must be boolean"),
            ({"appid": "yes"}, "appid must be boolean"),
        ]

        for payload, message in invalid_cases:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(InvalidExtensionResults, re.escape(message)):
                    parse_client_extension_results(payload)

    def test_parse_client_extension_results_returns_none_for_unrecognized_or_empty_data(self) -> None:
        self.assertIsNone(parse_client_extension_results({"unexpected": True}))
        self.assertIsNone(parse_client_extension_results(None))
        self.assertIsNone(parse_client_extension_results({}))
