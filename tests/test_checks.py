import base64
import uuid
import unittest

from klyuchnik import checks


class SnilsTests(unittest.TestCase):

    def test_good(self):
        for text in ["112-233-445 95", "11223344595", "112 233 445 95",  # gitleaks:allow
                     "123-456-789 64", "100-356-355 00", "100-079-190 00", "106-897-449 00"]:  # gitleaks:allow
            with self.subTest(text=text):
                self.assertTrue(checks.snils_ok(text))

    def test_bad(self):
        for text in ["112-233-445 96", "112-233-454 95", "123-456-789 01",
                     "112-233-445 9", "000-000-000 00", "001-001-998 00", ""]:
            with self.subTest(text=text):
                self.assertFalse(checks.snils_ok(text))


class InnTests(unittest.TestCase):

    def test_good(self):
        for text in ["500100732259", "540612345667", "770198765434"]:
            with self.subTest(text=text):
                self.assertTrue(checks.inn_ok(text))

    def test_bad(self):
        for text in ["540612345668", "500100732250", "000000000000",
                     "7707083893", "12345678901", ""]:
            with self.subTest(text=text):
                self.assertFalse(checks.inn_ok(text))


class CardTests(unittest.TestCase):

    def test_luhn(self):
        self.assertTrue(checks.luhn_ok("4276123456789014"))
        self.assertFalse(checks.luhn_ok("4276123456789015"))

    def test_mir_good(self):
        for text in ["2200123456789019", "2200 1234 5678 9019", "2204-1234-5678-9015"]:  # gitleaks:allow
            with self.subTest(text=text):
                self.assertTrue(checks.mir_card_ok(text))

    def test_mir_bad(self):
        for text in ["2200123456789010", "2205123456789014", "4276123456789014",
                     "220012345678901", ""]:
            with self.subTest(text=text):
                self.assertFalse(checks.mir_card_ok(text))


def oms_control_digit_like_foms(first15):
    odd = ""
    even = ""
    reverse = first15[::-1]
    for i in range(len(reverse)):
        if i % 2 == 0:
            odd += reverse[i]
        else:
            even += reverse[i]
    number = even + str(int(odd) * 2)
    total = 0
    for c in number:
        total += int(c)
    return (10 - total % 10) % 10


class OmsTests(unittest.TestCase):

    def test_example_from_foms_method(self):
        self.assertEqual(oms_control_digit_like_foms("540000123456789"), 2)
        self.assertTrue(checks.oms_ok("5400001234567892"))  # gitleaks:allow
        self.assertTrue(checks.oms_ok("5400 0012 3456 7892"))  # gitleaks:allow

    def test_bad(self):
        for text in ["5400001234567893", "0000000000000000", "540000123456789", ""]:
            with self.subTest(text=text):
                self.assertFalse(checks.oms_ok(text))

    def test_foms_method_is_luhn(self):
        import random
        random.seed(79)
        for i in range(10000):
            first15 = ""
            for j in range(15):
                first15 += str(random.randint(0, 9))
            control = oms_control_digit_like_foms(first15)
            self.assertTrue(checks.luhn_ok(first15 + str(control)))


class PassportTests(unittest.TestCase):

    def test_good(self):
        for text in ["4506 123456", "45 06 123456", "4506123456", "5098 765432", "5426 112233"]:
            with self.subTest(text=text):
                self.assertTrue(checks.passport_ok(text))

    def test_bad(self):
        for text in ["4550 123456", "0006 123456", "4506 000000", "4506 000100", "4506 12345", ""]:
            with self.subTest(text=text):
                self.assertFalse(checks.passport_ok(text))


class GigachatTests(unittest.TestCase):

    def make_key(self):
        raw = str(uuid.uuid4()) + ":" + str(uuid.uuid4())
        return base64.b64encode(raw.encode()).decode()

    def test_good(self):
        for i in range(20):
            self.assertTrue(checks.gigachat_key_ok(self.make_key()))

    def test_bad(self):
        not_uuid = base64.b64encode(b"hello:world").decode()
        one_uuid = base64.b64encode(str(uuid.uuid4()).encode()).decode()
        for text in [not_uuid, one_uuid, "not base64 at all!", "", "eyJhbGciOiJIUzI1NiJ9"]:
            with self.subTest(text=text):
                self.assertFalse(checks.gigachat_key_ok(text))


if __name__ == "__main__":
    unittest.main()
