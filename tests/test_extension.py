import base64
import json
import os
import random
import tempfile
import unittest
import uuid

from klyuchnik import checks
from tests import browser
from tests import test_rules

PAGE = """<!doctype html><meta charset="utf-8">
{scripts}
<pre id="out"></pre>
<script>
const CASES = {cases};
const NUMBERS = {numbers};
const result = {{scan: [], checks: {{}}}};
for (const text of CASES) {{
  const rules = [];
  for (const f of klyuchnikScan(text)) rules.push(f.rule);
  result.scan.push(rules);
}}
for (const name in NUMBERS) {{
  result.checks[name] = [];
  for (const value of NUMBERS[name]) result.checks[name].push(KLYUCHNIK_CHECK_BY_NAME[name](value));
}}
document.getElementById("out").textContent = JSON.stringify(result);
</script>"""

JS_NAMES = {
    "snils_ok": "snilsOk", "inn_ok": "innOk", "mir_card_ok": "mirCardOk", "oms_ok": "omsOk",
    "passport_ok": "passportOk", "gigachat_key_ok": "gigachatKeyOk", "prefixed_key_ok": "prefixedKeyOk",
    "wb_token_ok": "wbTokenOk",
}


def random_digits(n):
    s = ""
    for i in range(n):
        s += str(random.randint(0, 9))
    return s


def make_numbers():
    random.seed(7)
    numbers = {
        "snils_ok": [random_digits(11) for i in range(3000)] + ["112-233-445 95", "000-000-000 00"],  # gitleaks:allow
        "inn_ok": [random_digits(12) for i in range(3000)] + ["500100732259"],
        "mir_card_ok": ["220" + random.choice("0123456") + random_digits(12) for i in range(3000)],
        "oms_ok": [random_digits(16) for i in range(3000)],
        "passport_ok": [random_digits(10) for i in range(3000)],
        "gigachat_key_ok": [], "prefixed_key_ok": [], "wb_token_ok": [],
    }
    for i in range(300):
        numbers["gigachat_key_ok"].append(base64.b64encode((str(uuid.uuid4()) + ":" + str(uuid.uuid4())).encode()).decode())
        numbers["gigachat_key_ok"].append(base64.b64encode(os.urandom(73)).decode())
        numbers["prefixed_key_ok"].append("live_" + test_rules.rnd(test_rules.URLSAFE, 43))
        numbers["prefixed_key_ok"].append("test_" + test_rules.rnd("abcdefghijklmnopqrstuvwxyz_", 40))
        numbers["wb_token_ok"].append(test_rules.wb_token())
        numbers["wb_token_ok"].append(test_rules.jwt({"sub": "x", "exp": 1}))
    return numbers


@unittest.skipIf(browser.find_browser() is None, "нет браузера Edge или Chrome для запуска JavaScript")
class SameAnswersTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cases = [text for rule, text in test_rules.SHOULD_FIND] + test_rules.SHOULD_NOT_FIND
        cls.numbers = make_numbers()
        mapping = "const KLYUCHNIK_CHECK_BY_NAME = {" + ", ".join(
            '"' + py + '": ' + js for py, js in JS_NAMES.items()) + "};"
        html = PAGE.format(scripts=browser.script_tags(["rules.js", "checks.js", "detect.js"]),
                           cases=json.dumps(cls.cases, ensure_ascii=False),
                           numbers=json.dumps(cls.numbers))
        html = html.replace("<pre id=\"out\"></pre>", "<script>" + mapping + "</script>\n<pre id=\"out\"></pre>")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "page.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            cls.result = json.loads(browser.run_page(path))

    def test_scan_same_as_python(self):
        expected = [{rule} for rule, text in test_rules.SHOULD_FIND] + [set() for t in test_rules.SHOULD_NOT_FIND]
        for i in range(len(self.cases)):
            got = set(r for r in self.result["scan"][i] if r.startswith("klyuchnik-"))
            with self.subTest(text=self.cases[i][:60]):
                self.assertEqual(got, expected[i])

    def test_checks_same_as_python(self):
        for name in self.numbers:
            python_check = getattr(checks, name)
            for i in range(len(self.numbers[name])):
                value = self.numbers[name][i]
                with self.subTest(check=name, value=value[:40]):
                    self.assertEqual(self.result["checks"][name][i], python_check(value))


if __name__ == "__main__":
    unittest.main()
