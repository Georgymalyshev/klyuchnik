(function () {
  const api = typeof chrome !== "undefined" && chrome.storage ? chrome : null;
  let enabled = true;
  let allowText = null;
  let lastBox = null;
  let windowOpen = false;

  if (api) {
    api.storage.local.get({ enabled: true }, (data) => { enabled = data.enabled; });
    api.storage.onChanged.addListener((changes) => {
      if (changes.enabled) enabled = changes.enabled.newValue;
    });
  }

  function count(what, findings) {
    if (!api) return;
    api.storage.local.get({ stats: {} }, (data) => {
      const stats = data.stats;
      if (!stats.since) stats.since = new Date().toISOString().slice(0, 10);
      stats[what] = (stats[what] || 0) + 1;
      if (findings) {
        stats.byRule = stats.byRule || {};
        for (const f of findings) stats.byRule[f.rule] = (stats.byRule[f.rule] || 0) + 1;
      }
      api.storage.local.set({ stats: stats });
    });
  }

  function boxOf(el) {
    if (!el || !el.closest) return null;
    return el.closest('textarea, input[type="text"], input[type="search"], input:not([type]), ' +
                      '[contenteditable="true"], [contenteditable=""], [contenteditable="plaintext-only"]');
  }

  function getText(box) {
    if (box.tagName === "TEXTAREA" || box.tagName === "INPUT") return box.value;
    return box.innerText;
  }

  function setText(box, text) {
    box.focus();
    if (box.tagName === "TEXTAREA" || box.tagName === "INPUT") {
      const proto = box.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, "value").set.call(box, text);
      box.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      document.execCommand("selectAll", false, null);
      document.execCommand("insertText", false, text);
    }
  }

  function maskText(text, findings) {
    const sorted = findings.slice().sort((a, b) => b.start - a.start);
    for (const f of sorted) {
      text = text.slice(0, f.start) + "[скрыто]" + text.slice(f.start + f.secret.length);
    }
    return text;
  }

  function hide(secret) {
    return secret.length <= 6 ? "***" : secret.slice(0, 4) + "…";
  }

  function dangerous(findings) {
    return findings.filter((f) => !f.warn);
  }

  const STYLE = `
    .back { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: flex;
            align-items: center; justify-content: center; z-index: 2147483647;
            font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
    .card { background: #fff; color: #1b1b1f; max-width: 460px; width: calc(100% - 32px);
            border-radius: 14px; padding: 20px 22px; box-shadow: 0 12px 40px rgba(0,0,0,.3); }
    h2 { margin: 0 0 8px; font-size: 18px; color: #b3261e; }
    p { margin: 0 0 10px; }
    ul { margin: 0 0 16px; padding-left: 20px; }
    li { margin: 3px 0; }
    .buttons { display: flex; gap: 8px; flex-wrap: wrap; }
    button { font: inherit; border-radius: 8px; padding: 8px 14px; cursor: pointer; border: 1px solid #c4c6d0; background: #fff; }
    .mask { background: #1f4ea0; color: #fff; border-color: #1f4ea0; }
    .send { margin-left: auto; color: #b3261e; }
    .toast { position: fixed; right: 16px; bottom: 16px; max-width: 360px; background: #1b1b1f; color: #fff;
             padding: 10px 14px; border-radius: 10px; z-index: 2147483647;
             font: 14px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; }
  `;

  function showToast(message) {
    const host = document.createElement("div");
    host.className = "klyuchnik-toast";
    const root = host.attachShadow({ mode: "open" });
    root.innerHTML = "<style>" + STYLE + "</style><div class='toast'></div>";
    root.querySelector(".toast").textContent = message;
    document.documentElement.appendChild(host);
    setTimeout(() => host.remove(), 6000);
  }

  function showWarning(findings, box, text, sendAgain) {
    windowOpen = true;
    count("alarms", findings);

    const host = document.createElement("div");
    host.id = "klyuchnik-warning";
    const root = host.attachShadow({ mode: "open" });
    root.innerHTML = "<style>" + STYLE + "</style>" +
      "<div class='back'><div class='card' role='alertdialog' aria-labelledby='t' aria-describedby='d'>" +
      "<h2 id='t'>Ключник: в сообщении есть секреты</h2>" +
      "<p id='d'>Если отправить, этот текст уйдёт на сервер ИИ-сервиса и может там сохраниться.</p>" +
      "<ul></ul>" +
      "<div class='buttons'>" +
      "<button class='mask'>Скрыть их</button>" +
      "<button class='cancel'>Вернуться</button>" +
      "<button class='send'>Всё равно отправить</button>" +
      "</div></div></div>";

    const list = root.querySelector("ul");
    for (const f of findings) {
      const li = document.createElement("li");
      li.textContent = f.description + ": " + hide(f.secret);
      list.appendChild(li);
    }
    document.documentElement.appendChild(host);

    function close() {
      host.remove();
      windowOpen = false;
      box.focus();
    }

    root.querySelector(".mask").onclick = () => {
      close();
      setText(box, maskText(text, findings));
      count("masked");
    };
    root.querySelector(".cancel").onclick = () => {
      close();
      count("cancelled");
    };
    root.querySelector(".send").onclick = () => {
      allowText = text;
      close();
      count("sentAnyway");
      sendAgain();
    };
    root.addEventListener("keydown", (e) => {
      if (e.key === "Escape") root.querySelector(".cancel").click();
      e.stopPropagation();
    });
    root.querySelector(".mask").focus();
  }

  function clickableNear(target, box) {
    let el = target;
    let button = null;
    for (let i = 0; el && i < 4; i++) {
      if (el.matches && el.matches('button, [role="button"], input[type="submit"]')) { button = el; break; }
      if (el.nodeType === 1 && getComputedStyle(el).cursor === "pointer") { button = el; break; }
      el = el.parentElement;
    }
    if (!button || box.contains(button)) return null;

    const label = (button.getAttribute("aria-label") || "") + " " + (button.title || "") + " " + (button.textContent || "");
    if (/отправ|send/i.test(label)) return button;

    let parent = box;
    for (let i = 0; parent && i < 3; i++) {
      if (parent.contains(button)) return button;
      parent = parent.parentElement;
    }
    return null;
  }

  document.addEventListener("focusin", (e) => {
    const box = boxOf(e.target);
    if (box) lastBox = box;
  }, true);

  window.addEventListener("keydown", (e) => {
    if (!enabled || windowOpen) return;
    if (e.key !== "Enter" || e.shiftKey || e.isComposing) return;
    const box = boxOf(e.target);
    if (!box) return;
    const text = getText(box);
    if (!text || text === allowText) return;

    const findings = klyuchnikScan(text);
    if (dangerous(findings).length === 0) return;

    e.preventDefault();
    e.stopImmediatePropagation();
    showWarning(findings, box, text, () => {
      box.dispatchEvent(new KeyboardEvent("keydown", {
        key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true,
      }));
      showToast("Если сообщение не ушло, нажмите Enter ещё раз: Ключник его пропустит.");
    });
  }, true);

  window.addEventListener("click", (e) => {
    if (!enabled || windowOpen) return;
    if (!lastBox || !lastBox.isConnected) return;
    const button = clickableNear(e.target, lastBox);
    if (!button) return;
    const text = getText(lastBox);
    if (!text || text === allowText) return;

    const findings = klyuchnikScan(text);
    if (dangerous(findings).length === 0) return;

    e.preventDefault();
    e.stopImmediatePropagation();
    const box = lastBox;
    showWarning(findings, box, text, () => button.click());
  }, true);

  document.addEventListener("paste", (e) => {
    if (!enabled) return;
    if (!boxOf(e.target) || !e.clipboardData) return;
    const findings = dangerous(klyuchnikScan(e.clipboardData.getData("text")));
    if (findings.length === 0) return;
    count("pasteWarnings");
    showToast("Ключник: во вставленном тексте есть «" + findings[0].description +
              "». Перед отправкой он спросит ещё раз.");
  }, true);
})();
