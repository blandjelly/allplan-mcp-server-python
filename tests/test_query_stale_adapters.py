"""Positive stale-adapter filtering for semantic M1 scans."""
import sys
import types
import unittest
from unittest.mock import patch

import test_model_query as fixtures


class QueryStaleAdapterTests(unittest.TestCase):
    setUp = fixtures.QueryTests.setUp
    prepare_context = fixtures.QueryTests.prepare_context
    prepare = fixtures.QueryTests.prepare
    adapter = fixtures.QueryTests.adapter
    request = fixtures.QueryTests.request
    query = fixtures.QueryTests.query

    def native(self, adapters):
        self.prepare(adapters)
        self.parents = {}
        self.adapter_module = types.SimpleNamespace(
            BaseElementAdapterParentElementService=types.SimpleNamespace(
                GetParentElement=lambda element: self.parents.get(
                    id(element), types.SimpleNamespace(IsNull=lambda: True))))
        modules = patch.dict(sys.modules, {
            "NemAll_Python_IFW_ElementAdapter": self.adapter_module})
        modules.start()
        self.addCleanup(modules.stop)

    def semantic_query(self):
        return self.query(component_kind="semantic_component", fields=["family"])

    def test_positive_null_or_deleted_wrapper_is_skipped_before_broken_parent_walk(self):
        live = self.adapter(ident=1)
        live.IsNull.return_value = False
        live.IsDeleted.return_value = False
        stale = self.adapter(ident=2)
        stale.GetElementAdapterType.return_value.GetTypeName.return_value = "Text_TypeUUID"
        stale.IsNull.return_value = False
        stale.IsDeleted.return_value = True
        self.native([live, stale])
        parent_reads = []

        def parent(element):
            parent_reads.append(element)
            if element is stale:
                raise RuntimeError("deleted wrapper has no hierarchy")
            return types.SimpleNamespace(IsNull=lambda: True)

        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = parent
        result = self.semantic_query()

        self.assertEqual(result["counts"]["stale_adapters_skipped"], 1)
        self.assertEqual(result["counts"]["hierarchy_not_checked"], 0)
        self.assertTrue(result["coverage"]["requested_scope_complete"])
        self.assertEqual(len(result["elements"]), 1)
        self.assertNotIn(stale, parent_reads)
        stale.GetAttributes.assert_not_called()

    def test_unknown_hierarchy_remains_incomplete_when_lifecycle_is_unavailable(self):
        live = self.adapter(ident=1)
        live.GetElementAdapterType.return_value.GetTypeName.return_value = "Text_TypeUUID"
        live.IsNull.side_effect = RuntimeError("lifecycle API unavailable")
        live.IsDeleted.side_effect = RuntimeError("lifecycle API unavailable")
        self.native([live])
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = (
            lambda element: (_ for _ in ()).throw(RuntimeError("parent unavailable")))

        result = self.semantic_query()

        self.assertEqual(result["counts"]["stale_adapters_skipped"], 0)
        self.assertEqual(result["counts"]["hierarchy_not_checked"], 1)
        self.assertFalse(result["coverage"]["requested_scope_complete"])
        self.assertEqual(result["elements"], [])

    def test_lifecycle_read_failures_do_not_block_a_resolvable_live_adapter(self):
        live = self.adapter(ident=1)
        live.IsNull.side_effect = RuntimeError("lifecycle API unavailable")
        live.IsDeleted.side_effect = RuntimeError("lifecycle API unavailable")
        self.native([live])

        result = self.semantic_query()

        self.assertEqual(result["counts"]["stale_adapters_skipped"], 0)
        self.assertEqual(result["counts"]["hierarchy_not_checked"], 0)
        self.assertTrue(result["coverage"]["requested_scope_complete"])
        self.assertEqual(len(result["elements"]), 1)


if __name__ == "__main__":
    unittest.main()
