const MAX_SIZE = 5 * 1024 * 1024;

function hide(secret) {
  return secret.length <= 6 ? "***" : secret.slice(0, 4) + "…";
}

function lineOf(text, position) {
  let line = 1;
  for (let i = 0; i < position; i++) {
    if (text[i] === "\n") line++;
  }
  return line;
}

function element(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text) el.textContent = text;
  return el;
}

function showResults(items) {
  const results = document.getElementById("results");
  results.innerHTML = "";

  let total = 0;
  let dangerous = 0;
  for (const item of items) {
    for (const f of item.findings) {
      total++;
      if (!f.warn) dangerous++;
    }
  }

  if (dangerous > 0) {
    results.appendChild(element("div", "summary bad", "Найдено опасного: " + dangerous + ". Ниже — что это и что делать."));
  } else if (total > 0) {
    results.appendChild(element("div", "summary good", "Ключей и документов не найдено. Есть только телефоны: проверьте, можно ли их публиковать."));
  } else {
    results.appendChild(element("div", "summary good", "Ничего не найдено. Проверено: " + items.length + " шт."));
  }

  for (const item of items) {
    for (const f of item.findings) {
      const card = element("div", "finding");
      const title = element("h3", null, f.description);
      const advice = adviceFor(f);
      const tag = f.warn ? element("span", "tag warn", "внимание") :
                  advice.type === "key" ? element("span", "tag key", "ключ") : element("span", "tag pd", "персональные данные");
      title.appendChild(tag);
      card.appendChild(title);

      const where = element("div", "where");
      where.appendChild(document.createTextNode(item.name + ", строка " + lineOf(item.text, f.start) + ": "));
      where.appendChild(element("span", "secret", hide(f.secret)));
      card.appendChild(where);

      if (advice.type === "key") {
        card.appendChild(element("p", "advice", advice.text));
        const how = element("p", "advice", "Где отозвать — " + advice.service + ": " + advice.how + " ");
        const link = element("a", null, "Документация");
        link.href = advice.link;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        how.appendChild(link);
        card.appendChild(how);
      } else if (!f.warn) {
        card.appendChild(element("p", "advice", advice.text));
      }
      results.appendChild(card);
    }
  }
}

function looksBinary(text) {
  return text.slice(0, 8000).indexOf("\u0000") !== -1;
}

async function checkFiles(files) {
  const items = [];
  for (const file of files) {
    if (file.size > MAX_SIZE) {
      items.push({ name: file.name + " (больше 5 МБ, пропущен)", text: "", findings: [] });
      continue;
    }
    const text = await file.text();
    if (looksBinary(text)) {
      items.push({ name: file.name + " (не текст, пропущен)", text: "", findings: [] });
      continue;
    }
    items.push({ name: file.name, text: text, findings: klyuchnikScan(text) });
  }
  showResults(items);
}

const drop = document.getElementById("drop");
const fileInput = document.getElementById("file");

drop.addEventListener("click", () => fileInput.click());
drop.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});
fileInput.addEventListener("change", () => checkFiles(fileInput.files));
drop.addEventListener("dragover", (e) => {
  e.preventDefault();
  drop.classList.add("over");
});
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("over");
  checkFiles(e.dataTransfer.files);
});

document.getElementById("check").addEventListener("click", () => {
  const text = document.getElementById("text").value;
  showResults([{ name: "Вставленный текст", text: text, findings: klyuchnikScan(text) }]);
});

document.getElementById("example").addEventListener("click", () => {
  const key = btoa(crypto.randomUUID() + ":" + crypto.randomUUID());
  document.getElementById("text").value =
    "# config.py (все значения выдуманные)\n" +
    "GIGACHAT_CREDENTIALS = \"" + key + "\"\n" +
    "client = {\"name\": \"Иван Петров\", \"snils\": \"112-233-445 95\", \"inn\": \"500100732259\"}\n" +  // gitleaks:allow
    "support_phone = \"+7 913 123-45-67\"\n";  // gitleaks:allow
  document.getElementById("check").click();
});
