import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

from klyuchnik import checks

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "klyuchnik.toml")
OUR_BIN = os.path.join(os.path.expanduser("~"), ".klyuchnik", "bin")

CHECKS = {
    "klyuchnik-snils": checks.snils_ok,
    "klyuchnik-snils-bare": checks.snils_ok,
    "klyuchnik-inn": checks.inn_ok,
    "klyuchnik-mir-card": checks.mir_card_ok,
    "klyuchnik-oms": checks.oms_ok,
    "klyuchnik-passport": checks.passport_ok,
    "klyuchnik-gigachat-auth-key": checks.gigachat_key_ok,
    "klyuchnik-tinvest-token": checks.prefixed_key_ok,
    "klyuchnik-yookassa-secret-key": checks.prefixed_key_ok,
    "klyuchnik-wb-token": checks.wb_token_ok,
}

VALUE_RULES = [
    "klyuchnik-tbank-terminal-password", "klyuchnik-vk-token-old", "klyuchnik-dadata-key",
    "klyuchnik-ozon-seller-key", "klyuchnik-ozon-performance-secret", "klyuchnik-avito-secret",
    "klyuchnik-2gis-key", "klyuchnik-selectel-token", "klyuchnik-selectel-password",
    "klyuchnik-cloudru-secret", "klyuchnik-kontur-focus-key",
    "klyuchnik-kontur-extern-key",
]
for rule_id in VALUE_RULES:
    CHECKS[rule_id] = checks.value_ok

WARN_ONLY = ["klyuchnik-phone"]


def find_gitleaks():
    path = shutil.which("gitleaks")
    if path:
        return path

    for name in ["gitleaks.exe", "gitleaks"]:
        exe = os.path.join(OUR_BIN, name)
        if os.path.exists(exe):
            return exe

    folder = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            if name.startswith("Gitleaks.Gitleaks"):
                exe = os.path.join(folder, name, "gitleaks.exe")
                if os.path.exists(exe):
                    return exe
    return None


def run_gitleaks(target, config, staged=False):
    gitleaks = find_gitleaks()
    if gitleaks is None:
        print("Ключник: не нашёл gitleaks. Установите его командой: python -m klyuchnik.install")
        sys.exit(2)

    with tempfile.TemporaryDirectory() as tmp:
        report = os.path.join(tmp, "report.json")
        if staged:
            command = [gitleaks, "git", target, "--pre-commit", "--staged"]
        else:
            command = [gitleaks, "dir", target]
        command += ["--report-format", "json", "--report-path", report,
                    "--exit-code", "0", "--no-banner", "--log-level", "error"]
        if config:
            command += ["--config", config]
        subprocess.run(command, check=True)

        with open(report, encoding="utf-8") as f:
            return json.load(f)


def keep(finding):
    rule = finding["RuleID"]
    if rule in CHECKS:
        return CHECKS[rule](finding["Secret"])
    return True


def scan(target, config=CONFIG, staged=False):
    result = []
    for finding in run_gitleaks(target, config, staged):
        if keep(finding):
            result.append(finding)
    return result


def hide(secret):
    if len(secret) <= 6:
        return "***"
    return secret[:4] + "***"


def print_findings(found, target):
    stop = 0
    for f in found:
        name = f["File"]
        if os.path.isdir(target) and os.path.isabs(name):
            name = os.path.relpath(name, target)
        if f["RuleID"] in WARN_ONLY:
            mark = "внимание"
        else:
            mark = "НАЙДЕНО"
            stop += 1
        print(f"  {mark}: {name}:{f['StartLine']}  {f['Description']}  ({hide(f['Secret'])})")
    return stop


def main():
    parser = argparse.ArgumentParser(description="Ключник: ищет российские ключи и персональные данные")
    parser.add_argument("target", nargs="?", default=".", help="файл или папка")
    parser.add_argument("--staged", action="store_true", help="проверить то, что готовится к коммиту")
    parser.add_argument("--only-gitleaks", action="store_true", help="только правила gitleaks, без Ключника")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    config = None if args.only_gitleaks else CONFIG
    found = scan(args.target, config, args.staged)
    found.sort(key=lambda f: (f["File"], f["StartLine"]))

    if args.staged:
        if not found:
            return
        print("Ключник проверил коммит:")
        stop = print_findings(found, args.target)
        if stop == 0:
            print("Это только предупреждение, коммит продолжается.")
            return
        print()
        print("⛔ Коммит остановлен: в коде секрет или персональные данные.")
        print("Что делать: уберите их из кода (например, в переменную окружения")
        print("или в файл .env, который добавлен в .gitignore) и сделайте коммит снова.")
        print("Если это точно не секрет, допишите в конце строки комментарий: gitleaks:allow")
        sys.exit(1)

    stop = print_findings(found, args.target)
    print()
    print(f"Всего находок: {len(found)}, из них опасных: {stop}")
    if stop > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
