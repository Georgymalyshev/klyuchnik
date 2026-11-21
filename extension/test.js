function randomFrom(chars, n) {
  let s = "";
  const bytes = crypto.getRandomValues(new Uint8Array(n));
  for (const b of bytes) s += chars[b % chars.length];
  return s;
}

const URLSAFE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-";

function example(name) {
  if (name === "gigachat") {
    return "Почему не работает?\nfrom gigachat import GigaChat\ngiga = GigaChat(credentials=\"" +
           btoa(crypto.randomUUID() + ":" + crypto.randomUUID()) + "\")";
  }
  if (name === "snils") return "Заполни заявление: Иванов Иван, СНИЛС 112-233-445 95";  // gitleaks:allow
  if (name === "passport") return "Составь доверенность, паспорт 4506 123456 выдан ОВД Центрального района";  // gitleaks:allow
  if (name === "card") return "Переведи деньги на карту 2200 1234 5678 9019";  // gitleaks:allow
  if (name === "dadata") return "Объясни ошибку 403 в DaData, мой токен " + randomFrom("0123456789abcdef", 40);
  if (name === "vk") return "VK_TOKEN = \"vk1.a." + "Ab3" + randomFrom(URLSAFE, 200) + "\"";
  if (name === "badsnils") return "Номер 112-233-445 96 (контрольное число неправильное, это не СНИЛС)";
  return "Как написать функцию на Python, которая проверяет контрольную сумму?";
}

function addMessage(text) {
  const log = document.getElementById("log");
  const empty = log.querySelector(".empty");
  if (empty) empty.remove();
  const div = document.createElement("div");
  div.className = "msg";
  div.textContent = "Отправлено: " + text;
  log.appendChild(div);
}

const input = document.getElementById("input");
const editable = document.getElementById("editable");

function sendFromInput() {
  if (!input.value.trim()) return;
  addMessage(input.value);
  input.value = "";
}

function sendFromEditable() {
  if (!editable.innerText.trim()) return;
  addMessage(editable.innerText);
  editable.textContent = "";
}

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendFromInput();
  }
});
editable.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendFromEditable();
  }
});
document.getElementById("send").addEventListener("click", sendFromInput);
document.getElementById("send2").addEventListener("click", sendFromEditable);

for (const button of document.querySelectorAll("[data-example]")) {
  button.addEventListener("click", () => {
    input.value = example(button.dataset.example);
    input.focus();
  });
}
