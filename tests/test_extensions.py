import re
from unittest import TestCase

from webauthn.extensions import (
    ClientExtensionResults,
    CredentialPropertiesOutput,
    parse_client_extension_results,
)
from webauthn.helpers.exceptions import InvalidExtensionResults
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json


class TestWebAuthnExtensions(TestCase):
    # ------------------------------------------------------------------ #
    # Raw browser credential JSON preserves clientExtensionResults         #
    # ------------------------------------------------------------------ #

    def test_parse_registration_credential_preserves_client_extension_results(self) -> None:
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

    def test_parse_authentication_credential_preserves_client_extension_results(self) -> None:
        # credProps is registration-only in practice but the raw field is preserved regardless
        credential = parse_authentication_credential_json(
            {
                "id": "credential-id",
                "rawId": "Y3JlZGVudGlhbC1pZA",
                "response": {
                    "clientDataJSON": "Y2xpZW50LWRhdGE",
                    "authenticatorData": "YXV0aGVudGljYXRvci1kYXRh",
                    "signature": "c2lnbmF0dXJl",
                    "clientExtensionResults": {"credProps": {"rk": True}},
                },
                "type": "public-key",
            }
        )
        self.assertEqual(
            credential.response.client_extension_results,
            {"credProps": {"rk": True}},
        )

    # ------------------------------------------------------------------ #
    # credProps parsing (spec §10.4)                                        #
    # ------------------------------------------------------------------ #

    def test_cred_props_rk_true(self) -> None:
        """Discoverable (passkey) credential."""
        result = parse_client_extension_results({"credProps": {"rk": True}})
        self.assertEqual(result, ClientExtensionResults(cred_props=CredentialPropertiesOutput(rk=True)))

    def test_cred_props_rk_false(self) -> None:
        """Server-side credential."""
        result = parse_client_extension_results({"credProps": {"rk": False}})
        self.assertEqual(result, ClientExtensionResults(cred_props=CredentialPropertiesOutput(rk=False)))

    def test_cred_props_rk_absent(self) -> None:
        """Browser omits rk when it cannot determine discoverability."""
        result = parse_client_extension_results({"credProps": {}})
        self.assertEqual(result, ClientExtensionResults(cred_props=CredentialPropertiesOutput(rk=None)))

    def test_cred_props_invalid_rk_type(self) -> None:
        with self.assertRaisesRegex(InvalidExtensionResults, re.escape("credProps.rk must be a boolean")):
            parse_client_extension_results({"credProps": {"rk": "yes"}})

    # ------------------------------------------------------------------ #
    # Edge cases                                                            #
    # ------------------------------------------------------------------ #

    def test_returns_none_for_empty_input(self) -> None:
        self.assertIsNone(parse_client_extension_results({}))
        self.assertIsNone(parse_client_extension_results(None))

    def test_returns_none_for_unrecognized_extensions(self) -> None:
        """Unknown extension keys are silently ignored; future extensions can be added
        to the parser without breaking existing callers.
        """
        self.assertIsNone(parse_client_extension_results({"uvm": [[2, 4, 2]]}))
        self.assertIsNone(parse_client_extension_results({"largeBlob": {"supported": True}}))
        self.assertIsNone(parse_client_extension_results({"appid": True}))
        self.assertIsNone(parse_client_extension_results({"unexpected": True}))
