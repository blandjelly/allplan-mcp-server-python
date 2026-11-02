"""The parallel CI runner covers every test module exactly once."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_tests_parallel", ROOT / "utils/run_tests_parallel.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ParallelRunnerTests(unittest.TestCase):
    def test_discovers_the_same_top_level_modules_as_unittest_discover(self):
        names = runner.modules()
        self.assertIn("test_mcp_smoke", names)
        self.assertIn("test_run_tests_parallel", names)
        self.assertNotIn("trace_test_support", names)
        loaded = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
        discovered = {test.id().split(".")[0] for test in runner.flatten(loaded)}
        self.assertEqual(discovered, set(names))

    def test_plan_assigns_every_module_once_and_chunks_heavy_modules_completely(self):
        weights = {"a": 100, "b": 10, "c": 10, "d": 1}
        for workers in (1, 2, 3, 4, 8):
            with self.subTest(workers=workers):
                buckets = runner.plan(list(weights), workers, weights.__getitem__)
                units = [unit for bucket in buckets for unit in bucket]
                self.assertEqual(len(units), len(set(units)))
                self.assertLessEqual(len(buckets), workers)
                by_module = {}
                for unit in units:
                    name, _, chunk = unit.partition("@")
                    by_module.setdefault(name, []).append(chunk)
                self.assertEqual(set(by_module), set(weights))
                for name, chunks in by_module.items():
                    if chunks == [""]:
                        continue
                    count = int(chunks[0].split("/")[1])
                    self.assertEqual(sorted(chunks), sorted(f"{i}/{count}" for i in range(count)))
        self.assertIn("a@0/2", [u for b in runner.plan(list(weights), 2, weights.__getitem__) for u in b])


if __name__ == "__main__":
    unittest.main()
