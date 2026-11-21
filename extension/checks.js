function onlyDigits(text) {
  let result = "";
  for (const c of text) {
    if (c >= "0" && c <= "9") {
      result += c;
    }
  }
  return result;
}

function snilsOk(text) {
  const digits = onlyDigits(text);
  if (digits.length !== 11) return false;

  const number = digits.slice(0, 9);
  const control = Number(digits.slice(9));
  if (Number(number) <= 1001998) return false;

  let total = 0;
  for (let i = 0; i < 9; i++) {
    total += Number(number[i]) * (9 - i);
  }

  let right;
  if (total < 100) {
    right = total;
  } else if (total === 100 || total === 101) {
    right = 0;
  } else {
    right = total % 101;
    if (right === 100) right = 0;
  }
  return control === right;
}

function innOk(text) {
  const digits = onlyDigits(text);
  if (digits.length !== 12) return false;
  if (digits.slice(0, 2) === "00") return false;

  const weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8];
  const weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8];

  let sum1 = 0;
  for (let i = 0; i < 10; i++) sum1 += Number(digits[i]) * weights1[i];
  let sum2 = 0;
  for (let i = 0; i < 11; i++) sum2 += Number(digits[i]) * weights2[i];

  return (sum1 % 11) % 10 === Number(digits[10]) && (sum2 % 11) % 10 === Number(digits[11]);
}

function luhnOk(digits) {
  let total = 0;
  const reverse = digits.split("").reverse();
  for (let i = 0; i < reverse.length; i++) {
    let d = Number(reverse[i]);
    if (i % 2 === 1) {
      d = d * 2;
      if (d > 9) d = d - 9;
    }
    total += d;
  }
  return total % 10 === 0;
}

function mirCardOk(text) {
  const digits = onlyDigits(text);
  if (digits.length !== 16) return false;
  const start = digits.slice(0, 4);
  if (start < "2200" || start > "2204") return false;
  return luhnOk(digits);
}

function omsOk(text) {
  const digits = onlyDigits(text);
  if (digits.length !== 16) return false;
  if (digits === "0000000000000000") return false;
  return luhnOk(digits);
}

function passportOk(text) {
  const digits = onlyDigits(text);
  if (digits.length !== 10) return false;
  if (digits.slice(0, 2) === "00") return false;
  if (Number(digits.slice(4)) < 101) return false;

  const year = Number(digits.slice(2, 4));
  const thisYear = new Date().getFullYear() % 100;
  if (year > thisYear + 1 && year < 97) return false;
  return true;
}

const UUID = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

function gigachatKeyOk(text) {
  let decoded;
  try {
    decoded = atob(text);
  } catch (e) {
    return false;
  }
  const parts = decoded.split(":");
  if (parts.length !== 2) return false;
  return UUID.test(parts[0]) && UUID.test(parts[1]);
}

function looksRandom(text) {
  let upper = 0;
  let lower = 0;
  let digits = 0;
  for (const c of text) {
    if (c >= "A" && c <= "Z") upper++;
    if (c >= "a" && c <= "z") lower++;
    if (c >= "0" && c <= "9") digits++;
  }
  return upper >= 2 && lower >= 2 && digits >= 2;
}

function prefixedKeyOk(text) {
  let body = text.slice(text.indexOf("_") + 1);
  if (text.startsWith("t.")) body = text.slice(2);
  return looksRandom(body);
}

function jwtPayload(text) {
  const parts = text.split(".");
  if (parts.length !== 3) return null;
  let middle = parts[1].replace(/-/g, "+").replace(/_/g, "/");
  while (middle.length % 4 !== 0) middle += "=";
  try {
    return JSON.parse(atob(middle));
  } catch (e) {
    return null;
  }
}

function wbTokenOk(text) {
  const payload = jwtPayload(text);
  if (payload === null || typeof payload !== "object") return false;
  return "sid" in payload && "acc" in payload && "s" in payload;
}

const KLYUCHNIK_CHECKS = {
  "klyuchnik-snils": snilsOk,
  "klyuchnik-snils-bare": snilsOk,
  "klyuchnik-inn": innOk,
  "klyuchnik-mir-card": mirCardOk,
  "klyuchnik-oms": omsOk,
  "klyuchnik-passport": passportOk,
  "klyuchnik-gigachat-auth-key": gigachatKeyOk,
  "klyuchnik-tinvest-token": prefixedKeyOk,
  "klyuchnik-yookassa-secret-key": prefixedKeyOk,
  "klyuchnik-wb-token": wbTokenOk,
};
