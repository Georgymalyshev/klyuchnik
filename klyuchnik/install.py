import argparse
import hashlib
import os
import platform
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

from klyuchnik import scan

GITLEAKS_VERSION = "8.30.1"
RELEASES = "https://github.com/gitleaks/gitleaks/releases/download/v" + GITLEAKS_VERSION + "/"
MARK = "# klyuchnik pre-commit hook"


def archive_name():
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in ["amd64", "x86_64"]:
        arch = "x64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        arch = machine

    if system == "windows":
        return "gitleaks_" + GITLEAKS_VERSION + "_windows_" + arch + ".zip"
    return "gitleaks_" + GITLEAKS_VERSION + "_" + system + "_" + arch + ".tar.gz"


def download(url, path):
    with urllib.request.urlopen(url) as response:
        with open(path, "wb") as f:
            f.write(response.read())


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def expected_sha256(checksums_path, name):
    with open(checksums_path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[1] == name:
                return parts[0]
    return None


def download_gitleaks(folder=scan.OUR_BIN):
    name = archive_name()
    print("Скачиваю gitleaks " + GITLEAKS_VERSION + ": " + name)
    os.makedirs(folder, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        archive = os.path.join(tmp, name)
        checksums = os.path.join(tmp, "checksums.txt")
        download(RELEASES + name, archive)
        download(RELEASES + "gitleaks_" + GITLEAKS_VERSION + "_checksums.txt", checksums)

        expected = expected_sha256(checksums, name)
        actual = sha256_of(archive)
        if expected is None or expected != actual:
            print("Контрольная сумма не совпала. Файл мог быть повреждён или подменён, ставить его нельзя.")
            sys.exit(3)
        print("Контрольная сумма SHA-256 совпала.")

        if name.endswith(".zip"):
            with zipfile.ZipFile(archive) as z:
                z.extract("gitleaks.exe", folder)
            exe = os.path.join(folder, "gitleaks.exe")
        else:
            with tarfile.open(archive) as t:
                t.extract("gitleaks", folder, filter="data")
            exe = os.path.join(folder, "gitleaks")
            os.chmod(exe, os.stat(exe).st_mode | stat.S_IEXEC)

    print("gitleaks установлен: " + exe)
    return exe


def hooks_folder(repo):
    result = subprocess.run(["git", "rev-parse", "--git-path", "hooks"],
                            cwd=repo, capture_output=True, text=True)
    if result.returncode != 0:
        print("Ключник: это не git-репозиторий: " + os.path.abspath(repo))
        sys.exit(4)
    return os.path.join(repo, result.stdout.strip())


def hook_text():
    python = sys.executable.replace("\\", "/")
    package_parent = os.path.dirname(scan.HERE).replace("\\", "/")
    return ("#!/bin/sh\n"
            + MARK + "\n"
            + 'PYTHONPATH="' + package_parent + '" "' + python + '" -m klyuchnik.scan --staged\n')


def install_hook(repo):
    folder = hooks_folder(repo)
    os.makedirs(folder, exist_ok=True)
    hook = os.path.normpath(os.path.join(folder, "pre-commit"))

    if os.path.exists(hook):
        with open(hook, encoding="utf-8", errors="replace") as f:
            old = f.read()
        if MARK not in old:
            print("В проекте уже есть свой pre-commit хук: " + hook)
            print("Чтобы не сломать его, допишите в него вручную строку:")
            print(hook_text().splitlines()[-1])
            sys.exit(5)

    with open(hook, "w", encoding="utf-8", newline="\n") as f:
        f.write(hook_text())
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IEXEC)
    print("Сторож установлен: " + hook)


def uninstall_hook(repo):
    hook = os.path.join(hooks_folder(repo), "pre-commit")
    if not os.path.exists(hook):
        print("Сторожа здесь нет.")
        return
    with open(hook, encoding="utf-8", errors="replace") as f:
        if MARK not in f.read():
            print("Этот pre-commit хук не наш, не трогаю его.")
            return
    os.remove(hook)
    print("Сторож удалён.")


def main():
    parser = argparse.ArgumentParser(description="Ключник: установить сторожа в git-проект")
    parser.add_argument("repo", nargs="?", default=".", help="папка проекта")
    parser.add_argument("--uninstall", action="store_true", help="удалить сторожа")
    parser.add_argument("--download-gitleaks", action="store_true", help="скачать gitleaks, даже если он уже есть")
    parser.add_argument("--gitleaks-only", action="store_true", help="только поставить gitleaks, без хука (для GitHub Actions)")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.gitleaks_only:
        if scan.find_gitleaks() is None:
            download_gitleaks()
        return

    if args.uninstall:
        uninstall_hook(args.repo)
        return

    if args.download_gitleaks or scan.find_gitleaks() is None:
        download_gitleaks()
    else:
        print("gitleaks уже есть: " + scan.find_gitleaks())

    install_hook(args.repo)
    print("Готово. Теперь при каждом коммите Ключник будет проверять код.")


if __name__ == "__main__":
    main()
