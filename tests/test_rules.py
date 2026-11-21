import base64
import json
import os
import random
import tempfile
import unittest

from klyuchnik import scan

random.seed(2026)

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
HEX = "0123456789abcdef"
URLSAFE = LETTERS + DIGITS + "_-"


def rnd(chars, n):
    s = ""
    for i in range(n):
        s += random.choice(chars)
    return s


def rnd_key(n):
    return rnd(LETTERS[:26], 1) + rnd(LETTERS[26:], 1) + rnd(DIGITS, 1) + rnd(URLSAFE, n - 3)


def uuid4():
    return rnd(HEX, 8) + "-" + rnd(HEX, 4) + "-4" + rnd(HEX, 3) + "-" + rnd("89ab", 1) + rnd(HEX, 3) + "-" + rnd(HEX, 12)


def b64url(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")


def jwt(payload):
    header = {"alg": "ES256", "kid": "20260101v1", "typ": "JWT"}
    return b64url(header) + "." + b64url(payload) + "." + rnd(URLSAFE, 86)


def gigachat_key():
    return base64.b64encode((uuid4() + ":" + uuid4()).encode()).decode()


def wb_token():
    return jwt({"ent": 1, "exp": 1800000000, "id": uuid4(), "s": 1073741950,
                "sid": uuid4(), "t": False, "acc": 3, "for": "self"})


SHOULD_FIND = [
    ("klyuchnik-gigachat-auth-key", 'GIGACHAT_CREDENTIALS="' + gigachat_key() + '"'),
    ("klyuchnik-gigachat-auth-key", 'settings = {"gigachat": "' + gigachat_key() + '"}'),
    ("klyuchnik-gigachat-auth-key", "const giga = new GigaChat({ credentials: '" + gigachat_key() + "' });"),
    ("klyuchnik-tinvest-token", 'INVEST_TOKEN = "t.' + rnd_key(72) + '"'),
    ("klyuchnik-tinvest-token", 'with Client("t.' + rnd_key(86) + '") as client:'),
    ("klyuchnik-tbank-terminal-password", 'TERMINAL_PASSWORD = "' + rnd_key(16) + '"'),
    ("klyuchnik-yookassa-secret-key", "Configuration.secret_key = 'live_" + rnd_key(43) + "'"),
    ("klyuchnik-yookassa-secret-key", "YOOKASSA_KEY=test_" + rnd_key(43)),
    ("klyuchnik-vk-token", 'VK_TOKEN = "vk1.a.' + rnd_key(200) + '"'),
    ("klyuchnik-vk-token", "https://api.vk.com/method/users.get?v=5.199&access_token=vk1.a." + rnd_key(180)),
    ("klyuchnik-vk-token-old", 'vk_group_token = "' + rnd(HEX, 85) + '"'),
    ("klyuchnik-dadata-key", 'dadata = Dadata("' + rnd(HEX, 40) + '", "' + rnd(HEX, 40) + '")'),
    ("klyuchnik-dadata-key", "DADATA_API_KEY=" + rnd(HEX, 40)),
    ("klyuchnik-ozon-seller-key", 'requests.post("https://api-seller.ozon.ru/v3/product/list", headers={"Client-Id": "1234567", "Api-Key": "' + uuid4() + '"})'),
    ("klyuchnik-ozon-performance-secret", '{"client_id": "12345-1234567890@advertising.performance.ozon.ru", "client_secret": "' + rnd_key(60) + '"}'),
    ("klyuchnik-wb-token", 'WB_API_TOKEN = "' + wb_token() + '"'),
    ("klyuchnik-wb-token", "headers = {'Authorization': '" + wb_token() + "'}"),
    ("klyuchnik-avito-secret", 'AVITO_CLIENT_SECRET = "' + rnd_key(40) + '"'),
    ("klyuchnik-2gis-key", "const map = new mapgl.Map('map', { center: [82.9, 55.0], key: '" + uuid4() + "' });"),
    ("klyuchnik-2gis-key", "url = 'https://catalog.api.2gis.com/3.0/items?q=cafe&key=" + uuid4() + "'"),
    ("klyuchnik-selectel-token", 'SEL_TOKEN = "' + rnd(LETTERS + DIGITS, 12) + '_123456"'),
    ("klyuchnik-selectel-password", "OS_AUTH_URL=https://cloud.api.selcloud.ru/identity/v3/\nOS_PASSWORD=" + rnd_key(16)),
    ("klyuchnik-timeweb-token", "export TWC_TOKEN=" + jwt({"sub": "user", "exp": 1800000000})),
    ("klyuchnik-cloudru-secret", 'CLOUDRU_KEY_SECRET = "' + rnd_key(32) + '"'),
    ("klyuchnik-kontur-focus-key", "r = requests.get('https://focus-api.kontur.ru/api3/req?key=" + rnd(HEX, 40) + "&inn=7707083893')"),
    ("klyuchnik-kontur-diadoc-key", "Authorization: DiadocAuth ddauth_api_client_id=test-" + rnd(HEX, 32)),
    ("klyuchnik-kontur-extern-key", '{"X-Kontur-Apikey": "' + uuid4() + '"}'),
    ("klyuchnik-snils", 'client = {"name": "Иван Петров", "snils": "112-233-445 95"}'),  # gitleaks:allow
    ("klyuchnik-snils-bare", "СНИЛС: 11223344595"),  # gitleaks:allow
    ("klyuchnik-inn", '"inn": "540612345667"'),  # gitleaks:allow
    ("klyuchnik-inn", "ИНН 500100732259"),  # gitleaks:allow
    ("klyuchnik-passport", "паспорт 4506 123456"),  # gitleaks:allow
    ("klyuchnik-passport", "Паспорт: серия 45 06 № 123456"),  # gitleaks:allow
    ("klyuchnik-mir-card", 'card = "2200 1234 5678 9019"'),  # gitleaks:allow
    ("klyuchnik-oms", "полис ОМС 5400 0012 3456 7892"),  # gitleaks:allow
    ("klyuchnik-phone", "Телефон: +7 (913) 123-45-67"),  # gitleaks:allow
    ("klyuchnik-phone", "call 8-913-123-45-67"),  # gitleaks:allow
    ("klyuchnik-ozon-seller-key", "<?php // Ozon\n$config['OZON_API_KEY'] = '" + uuid4() + "';"),
    ("klyuchnik-timeweb-token", "package main // timeweb\nTWC_TOKEN := \"" + jwt({"sub": "u", "exp": 1800000000}) + "\""),
    ("klyuchnik-avito-secret", "avito:\n  avito_secret: \"" + rnd_key(40) + "\""),
    ("klyuchnik-2gis-key", "DGIS_API_KEY=" + uuid4()),
    ("klyuchnik-selectel-token", "{'SELECTEL_TOKEN': '" + rnd(LETTERS + DIGITS, 14) + "_654321'}"),
    ("klyuchnik-kontur-focus-key", 'FOCUS_API_KEY = "' + rnd(HEX, 40) + '"'),
]

SHOULD_NOT_FIND = [
    "def test_snils_returns_false_for_invalid_checksum_value():",
    "live_reload_enabled_for_development_server_mode = True",
    "value = t.someVeryLongPropertyNameThatGoesOnAndOnForeverAndEverAndEverMore",
    'blob = "' + base64.b64encode(bytes(random.randrange(256) for i in range(73))).decode() + '"',
    'GIGACHAT_CREDENTIALS="<your_authorization_key>"',
    "Configuration.secret_key = 'live_thisKeyIsNotReal'",
    'snils = "112-233-445 96"',
    'inn = "7707083893"',
    'inn = "540612345668"',
    'card = "4276 1234 5678 9014"',
    'card = "2200 1234 5678 9010"',
    '"passport": "45 50 123456"',
    'commit = "' + rnd(HEX, 40) + '"',
    '"Api-Key": "' + uuid4() + '"',
    'token = "' + jwt({"sub": "someone", "exp": 1800000000}) + '"',
    "# DaData\nDADATA_API_KEY=CHANGE_ME",
    "OS_AUTH_URL=https://cloud.api.selcloud.ru/identity/v3/\nOS_PASSWORD=${OS_PASSWORD}",
    "# 2gis\nrow_id = '" + uuid4() + "'",
    "полис ОМС 1234 5678 9012 3456",
    "order_number = 79131234567890",
    'avito = AvitoClient(client_secret="fake-secret-for-tests")',
    "OS_AUTH_URL=https://cloud.api.selcloud.ru/identity/v3/\npassword = os.getenv('OS_PASSWORD')",
    "# selcloud\nPASSWORD = self.password_from_vault",
    'ozon = {"Api-Key": "12345678-1234-1234-1234-123456789012"}',
    'selectel_api_token = "0000000000_000000"',
    '# dadata\n"reference": "' + rnd(HEX, 40) + '",',
]


def write_samples(folder, samples):
    names = []
    for i in range(len(samples)):
        name = "sample_" + str(i) + ".txt"
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(samples[i] + "\n")
        names.append(name)
    return names


def our_rules_by_file(folder):
    result = {}
    for finding in scan.scan(folder):
        rule = finding["RuleID"]
        if not rule.startswith("klyuchnik-"):
            continue
        name = os.path.basename(finding["File"])
        if name not in result:
            result[name] = set()
        result[name].add(rule)
    return result


class RulesTests(unittest.TestCase):

    def test_lock_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "composer.lock"), "w", encoding="utf-8") as f:
                f.write('{"name": "hflabs/dadata", "token": "' + rnd(HEX, 40) + '"}\n')
            self.assertEqual(our_rules_by_file(folder), {})

    def test_should_find(self):
        texts = []
        for rule, text in SHOULD_FIND:
            texts.append(text)
        with tempfile.TemporaryDirectory() as folder:
            names = write_samples(folder, texts)
            found = our_rules_by_file(folder)
        for i in range(len(SHOULD_FIND)):
            rule, text = SHOULD_FIND[i]
            with self.subTest(rule=rule, text=text[:60]):
                self.assertEqual(found.get(names[i], set()), {rule})

    def test_should_not_find(self):
        with tempfile.TemporaryDirectory() as folder:
            names = write_samples(folder, SHOULD_NOT_FIND)
            found = our_rules_by_file(folder)
        for i in range(len(SHOULD_NOT_FIND)):
            with self.subTest(text=SHOULD_NOT_FIND[i][:60]):
                self.assertEqual(found.get(names[i], set()), set())


if __name__ == "__main__":
    unittest.main()
