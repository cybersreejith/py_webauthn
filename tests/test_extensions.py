import re
from unittest import TestCase

from webauthn.extensions import (
    ClientExtensionResults,
    CredPropsExtension,
    CredPropsOutput,
    build_extension_inputs,
    parse_client_extension_results,
)
from webauthn.helpers.exceptions import InvalidExtensionResults
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json


class TestCredPropsExtensionInput(TestCase):

    def test_extension_id(self) -> None:
        self.assertEqual(CredPropsExtension().extension_id, "credProps")

    def test_input_value_is_true(self) -> None:
        self.assertTrue(CredPropsExtension().input_value())

    def test_build_extension_inputs_from_list(self) -> None:
        result = build_extension_inputs([CredPropsExtension()])
        self.assertEqual(result, {"credProps": True})

    def test_build_extension_inputs_from_dict_passthrough(self) -> None:
        result = build_extension_inputs({"credProps": True})
        self.assertEqual(result, {"credProps": True})

    def test_build_extension_inputs_none(self) -> None:
        self.assertIsNone(build_extension_inputs(None))

    def test_build_extension_inputs_empty_list(self) -> None:
        self.assertIsNone(build_extension_inputs([]))


class TestCredPropsOutput(TestCase):
    """Browser clientExtensionResults are preserved and parseable."""

    def test_parse_registration_credential_preserves_raw_results(self) -> None:
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

    def test_rk_absent_unknown(self) -> None:
        result = parse_client_extension_results({"credProps": {}})
        self.assertEqual(result, ClientExtensionResults(cred_props=CredPropsOutput(rk=None)))

    def test_invalid_rk(self) -> None:
        with self.assertRaisesRegex(InvalidExtensionResults, re.escape("credProps.rk must be a boolean")):
            parse_client_extension_results({"credProps": {"rk": "yes"}})


class TestParserForwardCompatibility(TestCase):
    """Unrecognised extension keys are silently ignored so the library stays
    compatible with future browser extensions without requiring a new release."""

    def test_returns_none_for_empty_or_none(self) -> None:
        self.assertIsNone(parse_client_extension_results({}))
        self.assertIsNone(parse_client_extension_results(None))

    def test_unknown_extensions_are_ignored(self) -> None:
        self.assertIsNone(parse_client_extension_results({"uvm": [[2, 4, 2]]}))
        self.assertIsNone(parse_client_extension_results({"largeBlob": {"supported": True}}))
        self.assertIsNone(parse_client_extension_results({"hmac-secret": {"enabled": True}}))
        self.assertIsNone(parse_client_extension_results({"appid": True}))
        self.assertIsNone(parse_client_extension_results({"unexpected": True}))
