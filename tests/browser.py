import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTENSION = os.path.join(ROOT, "extension")

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def find_browser():
    for path in BROWSERS:
        if os.path.exists(path):
            return path
    return None


def file_url(path):
    path = os.path.abspath(path).replace("\\", "/")
    if path.startswith("/"):
        return "file://" + path
    return "file:///" + path


def script_tags(names):
    tags = ""
    for name in names:
        tags += '<script src="' + file_url(os.path.join(EXTENSION, name)) + '"></script>\n'
    return tags


def run_page(html_path):
    browser = find_browser()
    command = [browser, "--headless=new", "--disable-gpu", "--no-first-run",
               "--allow-file-access-from-files", "--virtual-time-budget=20000"]
    if os.name != "nt":
        command.append("--no-sandbox")
    result = subprocess.run(command + ["--dump-dom", file_url(html_path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=120)
    dom = result.stdout
    start = dom.find("<pre id=\"out\">")
    end = dom.find("</pre>", start)
    if start == -1 or end == -1:
        raise RuntimeError("Страница не выдала результат:\n" + dom[:2000] + result.stderr[-2000:])
    text = dom[start + len("<pre id=\"out\">"):end]
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")
