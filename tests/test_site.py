import os
import tomllib
import unittest

from klyuchnik import scan
from tools import build_extension

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SiteTests(unittest.TestCase):

    def test_every_key_rule_has_advice(self):
        with open(os.path.join(ROOT, "site", "advice.js"), encoding="utf-8") as f:
            advice = f.read()
        with open(scan.CONFIG, "rb") as f:
            rules = tomllib.load(f)["rules"]

        ids = []
        for rule in rules:
            if "key" in rule.get("tags", []):
                ids.append(rule["id"])
        for rule in build_extension.EXTRA_RULES:
            ids.append(rule["id"])

        for rule_id in ids:
            with self.subTest(rule=rule_id):
                self.assertIn('"' + rule_id + '"', advice)

    def test_site_engine_is_fresh(self):
        for name in ["rules.js", "checks.js", "detect.js"]:
            with open(os.path.join(ROOT, "extension", name), encoding="utf-8") as f:
                original = f.read()
            with open(os.path.join(ROOT, "site", "engine", name), encoding="utf-8") as f:
                copy = f.read()
            with self.subTest(file=name):
                self.assertEqual(original, copy, "запустите: python tools/build_extension.py")


if __name__ == "__main__":
    unittest.main()
