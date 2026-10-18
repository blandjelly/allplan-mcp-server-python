"""Opt-in computed attribute observations in model_query."""
import importlib
import unittest

import test_host_handler as host_fixtures
import test_model_query as query_fixtures


class ComputableQueryTests(unittest.TestCase):
    setUp = host_fixtures.HostHandlerTests.setUp
    prepare_context = host_fixtures.HostHandlerTests.prepare_context
    adapter = query_fixtures.QueryTests.adapter
    request = query_fixtures.QueryTests.request
    query = query_fixtures.QueryTests.query

    def prepare(self, adapters=None):
        self.prepare_context()
        self.base.ElementsSelectService.SelectAllElements.return_value = adapters or []
        self.base.eAttibuteReadState.ReadAll = "stored"
        self.base.eAttibuteReadState.ReadAllAndComputable = "computed"
        self.contracts = importlib.import_module("test_allplan_host.query_contracts")

    def test_opt_in_observes_computed_only_values_and_revalidates_them(self):
        adapter = self.adapter()
        reads = {"stored": [(83, "S02")], "computed": [(83, "S02"), (20017, "derived") ]}
        adapter.GetAttributes.side_effect = lambda mode: reads[mode]
        self.prepare([adapter])

        result = self.query(attribute_read_mode="all_and_computable", attribute_ids=[20017],
                            predicate={"field": "attribute:20017", "op": "eq", "value": "derived"})

        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(result["coverage"]["attribute_read_mode"], "all_and_computable")
        self.assertEqual(result["elements"][0]["fields"]["attribute:20017"],
                         {"status": "observed", "value": "derived", "computed_only": True,
                          "presence_proven": False})
        self.assertEqual(adapter.GetAttributes.call_args_list[0].args, ("stored",))
        self.assertEqual(adapter.GetAttributes.call_args_list[1].args, ("computed",))

        reads["computed"] = [(83, "S02"), (20017, "changed")]
        with self.assertRaises(self.module.BridgeError) as error:
            self.handler.handle("/model-query", {"schema_version": "m1-query-1", "action": "page",
                                                   "selection_id": result["selection_id"]})
        self.assertEqual(error.exception.code, "selection_stale")

    def test_default_stored_mode_keeps_legacy_reader_and_coverage(self):
        adapter = self.adapter()
        adapter.GetAttributes.return_value = [(83, "stored")]
        self.prepare([adapter])
        result = self.query(attribute_ids=[83])
        self.assertEqual(result["coverage"]["attribute_read_mode"], "stored")
        self.assertEqual(adapter.GetAttributes.call_count, 1)
        self.assertEqual(adapter.GetAttributes.call_args.args, ("stored",))

    def test_only_computed_inclusive_absence_supports_exists_and_is_unset(self):
        adapter = self.adapter()
        adapter.GetAttributes.return_value = []
        self.prepare([adapter])
        unset = {"field": "attribute:20017", "op": "is_unset"}

        proven = self.query(attribute_read_mode="all_and_computable", predicate=unset)
        self.assertEqual(proven["counts"]["matched_model_identities"], 1)
        self.assertEqual(proven["elements"][0]["fields"]["attribute:20017"]["status"], "absent")
        self.assertEqual(proven["elements"][0]["fields"]["attribute:20017"]["presence_proven"], True)

        stored = self.query(predicate=unset)
        self.assertEqual(stored["counts"]["predicate_not_checked"], 1)

    def test_invalid_mode_is_rejected_before_enumeration_and_contracts_match(self):
        self.prepare()
        with self.assertRaises(self.module.BridgeError) as error:
            self.handler.handle("/model-query", self.request(attribute_read_mode="computed"))
        self.assertEqual(error.exception.code, "invalid_payload")
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

        from allplan_mcp.query_models import QueryInput
        client = QueryInput.model_validate({"action": "query", "attribute_read_mode": "all_and_computable"})
        self.assertEqual(client.attribute_read_mode, "all_and_computable")
        with self.assertRaises(ValueError):
            QueryInput.model_validate({"action": "query", "attribute_read_mode": "computed"})
        with self.assertRaises(self.module.BridgeError):
            self.contracts.validate_request(self.request(attribute_read_mode="computed"))

