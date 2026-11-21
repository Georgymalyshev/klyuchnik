import base64
import datetime
import json
import re


def only_digits(text):
    result = ""
    for c in text:
        if c in "0123456789":
            result += c
    return result


def snils_ok(text):
    digits = only_digits(text)
    if len(digits) != 11:
        return False

    number = digits[:9]
    control = int(digits[9:])

    if int(number) <= 1001998:
        return False

    total = 0
    for i in range(9):
        total += int(number[i]) * (9 - i)

    if total < 100:
        right = total
    elif total == 100 or total == 101:
        right = 0
    else:
        right = total % 101
        if right == 100:
            right = 0

    return control == right


def inn_ok(text):
    digits = only_digits(text)
    if len(digits) != 12:
        return False
    if digits[:2] == "00":
        return False

    weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

    sum1 = 0
    for i in range(10):
        sum1 += int(digits[i]) * weights1[i]

    sum2 = 0
    for i in range(11):
        sum2 += int(digits[i]) * weights2[i]

    control1 = sum1 % 11 % 10
    control2 = sum2 % 11 % 10
    return control1 == int(digits[10]) and control2 == int(digits[11])


def luhn_ok(digits):
    total = 0
    reverse = digits[::-1]
    for i in range(len(reverse)):
        d = int(reverse[i])
        if i % 2 == 1:
            d = d * 2
            if d > 9:
                d = d - 9
        total += d
    return total % 10 == 0


def mir_card_ok(text):
    digits = only_digits(text)
    if len(digits) != 16:
        return False
    if digits[:4] < "2200" or digits[:4] > "2204":
        return False
    return luhn_ok(digits)


def oms_ok(text):
    digits = only_digits(text)
    if len(digits) != 16:
        return False
    if digits == "0000000000000000":
        return False
    return luhn_ok(digits)


def passport_ok(text):
    digits = only_digits(text)
    if len(digits) != 10:
        return False
    if digits[:2] == "00":
        return False
    if int(digits[4:]) < 101:
        return False

    year = int(digits[2:4])
    this_year = datetime.date.today().year % 100
    if year > this_year + 1 and year < 97:
        return False
    return True


UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def gigachat_key_ok(text):
    try:
        decoded = base64.b64decode(text, validate=True).decode("ascii")
    except Exception:
        return False

    parts = decoded.split(":")
    if len(parts) != 2:
        return False
    return UUID.match(parts[0]) is not None and UUID.match(parts[1]) is not None


def looks_random(text):
    upper = 0
    lower = 0
    digits = 0
    for c in text:
        if c.isupper():
            upper += 1
        if c.islower():
            lower += 1
        if c.isdigit():
            digits += 1
    return upper >= 2 and lower >= 2 and digits >= 2


def prefixed_key_ok(text):
    body = text.split("_", 1)[-1]
    if text.startswith("t."):
        body = text[2:]
    return looks_random(body)


def jwt_payload(text):
    parts = text.split(".")
    if len(parts) != 3:
        return None
    middle = parts[1]
    middle += "=" * (-len(middle) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(middle))
    except Exception:
        return None


def wb_token_ok(text):
    payload = jwt_payload(text)
    if not isinstance(payload, dict):
        return False
    return "sid" in payload and "acc" in payload and "s" in payload
