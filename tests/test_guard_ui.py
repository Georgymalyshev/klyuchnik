import base64
import json
import os
import tempfile
import unittest
import uuid

from tests import browser

KEY = base64.b64encode((str(uuid.uuid4()) + ":" + str(uuid.uuid4())).encode()).decode()

PAGE = """<!doctype html><meta charset="utf-8">
<main>
<section><div><textarea id="input"></textarea><button id="send">Отправить</button></div></section>
<section><div><div id="editable" contenteditable="true"></div><button id="send2">Отправить</button></div></section>
<section><div><button id="other">Другая кнопка</button></div></section>
</main>
{scripts}
<pre id="out"></pre>
<script>
const KEY = "{key}";
const input = document.getElementById("input");
const editable = document.getElementById("editable");
let sent = [];
input.addEventListener("keydown", (e) => {{ if (e.key === "Enter") {{ sent.push(input.value); }} }});
editable.addEventListener("keydown", (e) => {{ if (e.key === "Enter") {{ sent.push(editable.innerText); }} }});
document.getElementById("send").addEventListener("click", () => sent.push(input.value));

function warning() {{ return document.getElementById("klyuchnik-warning"); }}
function press(box) {{
  box.focus();
  box.dispatchEvent(new FocusEvent("focusin", {{ bubbles: true }}));
  const e = new KeyboardEvent("keydown", {{ key: "Enter", code: "Enter", keyCode: 13, bubbles: true, cancelable: true }});
  box.dispatchEvent(e);
  return e.defaultPrevented;
}}
function button(name) {{ return warning().shadowRoot.querySelector("." + name); }}

const r = {{}};

sent = []; input.value = "Мой ключ: " + KEY;
r.keyEnterStopped = press(input) && warning() !== null && sent.length === 0;
r.warningText = warning() ? warning().shadowRoot.querySelector("ul").textContent : "";
button("mask").click();
r.masked = input.value === "Мой ключ: [скрыто]" && warning() === null;

sent = []; input.value = "Как дела?";
r.cleanEnterPasses = !press(input) && warning() === null && sent.length === 1;

sent = []; input.value = "СНИЛС 112-233-445 95";  // gitleaks:allow
input.focus(); input.dispatchEvent(new FocusEvent("focusin", {{ bubbles: true }}));
const click = new MouseEvent("click", {{ bubbles: true, cancelable: true }});
document.getElementById("send").dispatchEvent(click);
r.buttonStopped = click.defaultPrevented && warning() !== null && sent.length === 0;
button("cancel").click();
r.cancelKeepsText = input.value === "СНИЛС 112-233-445 95" && warning() === null && sent.length === 0;  // gitleaks:allow

document.getElementById("send").dispatchEvent(new MouseEvent("click", {{ bubbles: true, cancelable: true }}));
button("send").click();
r.sendAnywayWorks = sent.length === 1 && sent[0] === "СНИЛС 112-233-445 95" && warning() === null;  // gitleaks:allow

sent = []; input.value = "ИНН 500100732259";  // gitleaks:allow
input.dispatchEvent(new FocusEvent("focusin", {{ bubbles: true }}));
document.getElementById("other").dispatchEvent(new MouseEvent("click", {{ bubbles: true, cancelable: true }}));
r.otherButtonIgnored = warning() === null;
r.sameTextSendButtonStopped = (() => {{
  const c = new MouseEvent("click", {{ bubbles: true, cancelable: true }});
  document.getElementById("send").dispatchEvent(c);
  const stopped = c.defaultPrevented && warning() !== null;
  if (warning()) button("cancel").click();
  return stopped;
}})();

sent = []; editable.textContent = "паспорт 4506 123456";  // gitleaks:allow
r.editableStopped = press(editable) && warning() !== null && sent.length === 0;
button("mask").click();
r.editableMasked = editable.innerText.indexOf("123456") === -1 && editable.innerText.indexOf("[скрыто]") !== -1;

sent = []; input.value = "Номер 112-233-445 96";
r.badSnilsPasses = !press(input) && warning() === null;

sent = []; input.value = "Позвони мне +7 913 123-45-67";  // gitleaks:allow
r.phoneOnlyPasses = !press(input) && warning() === null;

sent = []; input.value = "<img src=x onerror=alert(1)> паспорт 4506 123456";  // gitleaks:allow
press(input);
r.noHtmlInjection = warning() !== null && warning().shadowRoot.querySelector("img") === null;
button("cancel").click();

document.getElementById("out").textContent = JSON.stringify(r);
</script>"""


@unittest.skipIf(browser.find_browser() is None, "нет браузера Edge или Chrome для запуска JavaScript")
class GuardUiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        html = PAGE.format(scripts=browser.script_tags(["rules.js", "checks.js", "detect.js", "guard.js"]), key=KEY)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "page.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            cls.r = json.loads(browser.run_page(path))

    def test_enter_with_key_is_stopped(self):
        self.assertTrue(self.r["keyEnterStopped"])
        self.assertIn("GigaChat", self.r["warningText"])

    def test_mask_replaces_secret(self):
        self.assertTrue(self.r["masked"])

    def test_clean_text_is_sent(self):
        self.assertTrue(self.r["cleanEnterPasses"])

    def test_send_button_is_stopped(self):
        self.assertTrue(self.r["buttonStopped"])

    def test_cancel_keeps_text(self):
        self.assertTrue(self.r["cancelKeepsText"])

    def test_send_anyway(self):
        self.assertTrue(self.r["sendAnywayWorks"])

    def test_other_button_ignored(self):
        self.assertTrue(self.r["otherButtonIgnored"])
        self.assertTrue(self.r["sameTextSendButtonStopped"])

    def test_contenteditable(self):
        self.assertTrue(self.r["editableStopped"])
        self.assertTrue(self.r["editableMasked"])

    def test_bad_snils_passes(self):
        self.assertTrue(self.r["badSnilsPasses"])

    def test_phone_only_passes(self):
        self.assertTrue(self.r["phoneOnlyPasses"])

    def test_no_html_injection(self):
        self.assertTrue(self.r["noHtmlInjection"])


if __name__ == "__main__":
    unittest.main()
