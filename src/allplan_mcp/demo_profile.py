"""Packaged profile data; host validates schema and freshly resolves project IDs."""
from importlib.resources import files
import json


def load_demo_profile():
    return json.loads(files("allplan_mcp").joinpath("profiles/native-model-qa.demo.json").read_text(encoding="utf-8"))
