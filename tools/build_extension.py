import json
import os
import struct
import sys
import tomllib
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOML = os.path.join(ROOT, "klyuchnik", "klyuchnik.toml")
EXTENSION = os.path.join(ROOT, "extension")

EXTRA_RULES = [
    {"id": "telegram-bot-token", "description": "Токен Telegram-бота",
     "regex": r"\b(\d{5,16}:A[A-Za-z0-9_-]{34})\b", "keywords": []},
    {"id": "yandex-api-key", "description": "API-ключ Яндекс Облака",
     "regex": r"\b(AQVN[A-Za-z0-9_-]{35,38})\b", "keywords": []},
    {"id": "yandex-iam-token", "description": "IAM-токен Яндекс Облака",
     "regex": r"\b(t1\.[A-Za-z0-9_-]+=*\.[A-Za-z0-9_-]{86}=*)", "keywords": []},
    {"id": "yandex-static-key", "description": "Статический ключ доступа Яндекс Облака",
     "regex": r"\b(YC[A-Za-z0-9_-]{38})\b", "keywords": ["yandex", "яндекс"]},
]


def to_js(rule):
    pattern = rule["regex"]
    flags = "g"
    if pattern.startswith("(?i)"):
        pattern = pattern[4:]
        flags = "gi"
    if "(?" in pattern.replace("(?:", ""):
        sys.exit("Правило " + rule["id"] + ": конструкцию (?...) нельзя перевести в JavaScript")
    keywords = []
    for k in rule.get("keywords", []):
        keywords.append(k.lower())
    return {
        "id": rule["id"],
        "description": rule["description"],
        "pattern": pattern,
        "flags": flags,
        "group": rule.get("secretGroup", 1),
        "keywords": keywords,
        "entropy": rule.get("entropy", 0),
        "warn": "warn" in rule.get("tags", []),
    }


def png(size, pixels):
    raw = b""
    for y in range(size):
        raw += b"\x00"
        for x in range(size):
            raw += bytes(pixels(x, y))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def icon_pixel(size):
    def pixels(x, y):
        u = (x + 0.5) / size
        v = (y + 0.5) / size
        corner = 0.2
        dx = max(corner - u, 0, u - (1 - corner))
        dy = max(corner - v, 0, v - (1 - corner))
        if dx * dx + dy * dy > corner * corner:
            return (0, 0, 0, 0)
        in_circle = (u - 0.5) ** 2 + (v - 0.4) ** 2 < 0.14 ** 2
        half = 0.06 + (v - 0.45) * 0.25
        in_foot = 0.45 < v < 0.78 and abs(u - 0.5) < half
        if in_circle or in_foot:
            return (255, 255, 255, 255)
        return (31, 78, 160, 255)
    return pixels


def main():
    with open(TOML, "rb") as f:
        config = tomllib.load(f)

    rules = []
    for rule in config["rules"]:
        rules.append(to_js(rule))
    for rule in EXTRA_RULES:
        rules.append(to_js(rule))

    text = "// Создано автоматически: python tools/build_extension.py (из klyuchnik/klyuchnik.toml)\n"
    text += "// Не правьте руками: правьте klyuchnik.toml и запустите программу снова.\n"
    text += "const KLYUCHNIK_RULES = " + json.dumps(rules, ensure_ascii=False, indent=1) + ";\n"
    with open(os.path.join(EXTENSION, "rules.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    os.makedirs(os.path.join(EXTENSION, "icons"), exist_ok=True)
    for size in [16, 32, 48, 128]:
        with open(os.path.join(EXTENSION, "icons", "icon" + str(size) + ".png"), "wb") as f:
            f.write(png(size, icon_pixel(size)))

    engine = os.path.join(ROOT, "site", "engine")
    os.makedirs(engine, exist_ok=True)
    for name in ["rules.js", "checks.js", "detect.js"]:
        with open(os.path.join(EXTENSION, name), encoding="utf-8") as f:
            code = f.read()
        with open(os.path.join(engine, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(code)

    with open(os.path.join(ROOT, "site", "icon.png"), "wb") as f:
        f.write(png(128, icon_pixel(128)))

    print("Готово: " + str(len(rules)) + " правил записано в extension/rules.js и скопировано в site/engine/")


if __name__ == "__main__":
    main()
