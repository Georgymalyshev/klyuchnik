import base64
import os
import subprocess
import sys
import tempfile
import unittest
import uuid

from klyuchnik import install, scan

PACKAGE_PARENT = os.path.dirname(scan.HERE)


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test@example.com",
                           "-c", "core.autocrlf=false"] + list(args),
                          cwd=repo, capture_output=True, text=True, encoding="utf-8")


def commit_file(repo, name, text):
    with open(os.path.join(repo, name), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    git(repo, "add", name)
    return git(repo, "commit", "-m", "add " + name)


def run_install(repo, *extra):
    env = dict(os.environ, PYTHONPATH=PACKAGE_PARENT, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-m", "klyuchnik.install", repo] + list(extra),
                          capture_output=True, text=True, encoding="utf-8", env=env)


def gigachat_key():
    return base64.b64encode((str(uuid.uuid4()) + ":" + str(uuid.uuid4())).encode()).decode()


class GuardTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q", "-b", "main")
        result = run_install(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_commit_passes(self):
        result = commit_file(self.repo, "ok.py", 'print("hello")')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_key_is_stopped(self):
        result = commit_file(self.repo, "bot.py", 'settings = {"gigachat": "' + gigachat_key() + '"}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Коммит остановлен", result.stdout + result.stderr)

    def test_snils_is_stopped(self):
        result = commit_file(self.repo, "client.py", 'snils = "112-233-445 95"')  # gitleaks:allow
        self.assertNotEqual(result.returncode, 0)

    def test_wrong_snils_passes(self):
        result = commit_file(self.repo, "client.py", 'snils = "112-233-445 96"')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_allow_comment_passes(self):
        result = commit_file(self.repo, "example.py",
                             'EXAMPLE = "' + gigachat_key() + '"  # gitleaks:allow')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_phone_is_only_warning(self):
        result = commit_file(self.repo, "contacts.py", 'phone = "+7 913 123-45-67"')  # gitleaks:allow
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("предупреждение", result.stdout + result.stderr)

    def test_uninstall(self):
        run_install(self.repo, "--uninstall")
        result = commit_file(self.repo, "bot.py", 'settings = {"gigachat": "' + gigachat_key() + '"}')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_foreign_hook_is_not_overwritten(self):
        hook = os.path.join(self.repo, ".git", "hooks", "pre-commit")
        with open(hook, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\necho my own hook\n")
        result = run_install(self.repo)
        self.assertNotEqual(result.returncode, 0)
        with open(hook, encoding="utf-8") as f:
            self.assertIn("my own hook", f.read())


@unittest.skipUnless(os.environ.get("KLYUCHNIK_NET_TESTS"), "нужен интернет: KLYUCHNIK_NET_TESTS=1")
class DownloadTests(unittest.TestCase):

    def test_download_and_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            exe = install.download_gitleaks(folder)
            result = subprocess.run([exe, "version"], capture_output=True, text=True)
            self.assertIn(install.GITLEAKS_VERSION, result.stdout)


if __name__ == "__main__":
    unittest.main()
