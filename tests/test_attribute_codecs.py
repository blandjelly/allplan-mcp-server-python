"""SDK-bound value metadata and exact enum label codecs."""
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HOST = Path(__file__).resolve().parents[1] / "python_host/PythonPartsScripts/PythonHost"


class AttributeCodecTests(unittest.TestCase):
    def setUp(self):
        package = types.ModuleType("test_attribute_codecs_host")
        package.__path__ = [str(HOST)]
        self.patch = patch.dict(sys.modules, {"test_attribute_codecs_host": package})
        self.patch.start()
        self.addCleanup(self.patch.stop)
        from test_attribute_codecs_host import attribute_codecs
        self.codecs = attribute_codecs

    def test_scalar_type_resolves_only_loaded_sdk_members(self):
        members = types.SimpleNamespace(String=11, Integer=12, Double=13, Boolean=14)
        base = types.SimpleNamespace(AttributeService=types.SimpleNamespace(AttributeType=members))
        for value, expected in ((11, ("text", "String")), (12, ("integer", "Integer")),
                                (13, ("real", "Double")), (14, ("boolean", "Boolean"))):
            with self.subTest(value=value):
                self.assertEqual(self.codecs.supported_scalar_type(base, value), expected)
        self.assertIsNone(self.codecs.supported_scalar_type(base, 999))

    def test_scalar_type_fails_closed_for_missing_or_ambiguous_members(self):
        missing = types.SimpleNamespace(String=11, Integer=12)
        base = types.SimpleNamespace(AttributeService=types.SimpleNamespace(AttributeType=missing))
        self.assertEqual(self.codecs.supported_scalar_type(base, 11), ("text", "String"))
        self.assertIsNone(self.codecs.supported_scalar_type(base, 13))

        duplicate = types.SimpleNamespace(String=11, Integer=11, Double=13, Boolean=14)
        base.AttributeService.AttributeType = duplicate
        self.assertIsNone(self.codecs.supported_scalar_type(base, 11))

    def test_enum_label_returns_only_after_exact_label_key_round_trip(self):
        service = types.SimpleNamespace(
            GetEnumIDFromValueString=lambda ident, value: {"New building": 0, "Existing": 3}[value],
            GetEnumValueStringFromID=lambda ident, key: {0: "New building", 3: "Existing"}[key],
        )
        base = types.SimpleNamespace(AttributeService=service)
        calls = []

        def read(api, callback):
            calls.append(api)
            return callback()

        self.assertEqual(self.codecs.bind_enum_label(base, 49, "New building", read),
                         {"enum_id": 0, "value": "New building"})
        self.assertEqual(calls, ["AttributeService.GetEnumIDFromValueString",
                                 "AttributeService.GetEnumValueStringFromID",
                                 "AttributeService.GetEnumIDFromValueString"])

    def test_enum_label_rejects_bad_key_or_nonexact_round_trip(self):
        for key, label in ((True, "New building"), (-1, "New building"),
                           (2**31, "New building"), (0, "New Building")):
            service = types.SimpleNamespace(
                GetEnumIDFromValueString=lambda ident, value, key=key: key,
                GetEnumValueStringFromID=lambda ident, enum_id, label=label: label,
            )
            base = types.SimpleNamespace(AttributeService=service)
            with self.subTest(key=key, label=label), self.assertRaises(ValueError):
                self.codecs.bind_enum_label(base, 49, "New building", lambda _api, callback: callback())

    def test_enum_lookup_exceptions_propagate_and_inputs_are_bounded(self):
        base = types.SimpleNamespace(AttributeService=types.SimpleNamespace(
            GetEnumIDFromValueString=lambda *_: (_ for _ in ()).throw(RuntimeError("native failure"))))
        with self.assertRaises(RuntimeError):
            self.codecs.bind_enum_label(base, 49, "New building", lambda _api, callback: callback())
        with self.assertRaises(ValueError):
            self.codecs.bind_enum_label(base, True, "New building", lambda _api, callback: callback())
        with self.assertRaises(ValueError):
            self.codecs.bind_enum_label(base, 49, "", lambda _api, callback: callback())

