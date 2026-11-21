// Создано автоматически: python tools/build_extension.py (из klyuchnik/klyuchnik.toml)
// Не правьте руками: правьте klyuchnik.toml и запустите программу снова.
const KLYUCHNIK_RULES = [
 {
  "id": "klyuchnik-gigachat-auth-key",
  "description": "Ключ авторизации GigaChat / SaluteSpeech (Сбер)",
  "pattern": "(?:^|[^A-Za-z0-9+/])([A-Za-z0-9+/]{98}==)(?:[^A-Za-z0-9+/=]|$)",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-tinvest-token",
  "description": "Токен T-Invest API (Т-Банк)",
  "pattern": "(?:^|[^A-Za-z0-9_.-])(t\\.[A-Za-z0-9_-]{60,120})(?:[^A-Za-z0-9_.-]|$)",
  "flags": "g",
  "group": 1,
  "keywords": [
   "t."
  ],
  "entropy": 4.5,
  "warn": false
 },
 {
  "id": "klyuchnik-tbank-terminal-password",
  "description": "Пароль терминала Т-Кассы (Т-Банк)",
  "pattern": "(?:terminal_?password|terminalpassword)[\"']?\\s*[:=]\\s*[\"']?([A-Za-z0-9_!@#$%^&*+-]{8,64})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "terminal_password",
   "terminalpassword"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-yookassa-secret-key",
  "description": "Секретный ключ ЮKassa",
  "pattern": "(?:^|[^A-Za-z0-9_-])((?:live|test)_[A-Za-z0-9_-]{30,60})(?:[^A-Za-z0-9_-]|$)",
  "flags": "g",
  "group": 1,
  "keywords": [
   "live_",
   "test_"
  ],
  "entropy": 4.5,
  "warn": false
 },
 {
  "id": "klyuchnik-vk-token",
  "description": "Ключ доступа VK",
  "pattern": "(?:^|[^A-Za-z0-9_.-])(vk[12]\\.a\\.[A-Za-z0-9_-]{100,400})",
  "flags": "g",
  "group": 1,
  "keywords": [
   "vk1.a.",
   "vk2.a."
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-vk-token-old",
  "description": "Ключ доступа VK (старый вид)",
  "pattern": "(?:vk|access_token)[^\\n]{0,40}?\\b([0-9a-f]{85})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "vk",
   "access_token"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-dadata-key",
  "description": "Ключ DaData",
  "pattern": "\\b([0-9a-f]{40})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [
   "dadata"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-ozon-seller-key",
  "description": "Api-Key Ozon Seller API",
  "pattern": "api[-_]?key[\"']?\\s*[:=]?\\s*[\"']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "ozon"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-ozon-performance-secret",
  "description": "client_secret Ozon Performance API",
  "pattern": "client_?secret[\"']?\\s*[:=]\\s*[\"']?([A-Za-z0-9_-]{20,128})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "performance.ozon.ru"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-wb-token",
  "description": "Токен API Wildberries",
  "pattern": "\\b(eyJ[A-Za-z0-9_-]{10,}\\.eyJ[A-Za-z0-9_-]{20,}\\.[A-Za-z0-9_-]{20,})",
  "flags": "g",
  "group": 1,
  "keywords": [
   "eyj"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-avito-secret",
  "description": "client_secret Avito API",
  "pattern": "client_?secret[\"']?\\s*[:=]\\s*[\"']?([A-Za-z0-9_-]{16,128})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "avito"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-2gis-key",
  "description": "Ключ API 2ГИС",
  "pattern": "key[\"']?\\s*[:=]\\s*[\"']?([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "2gis",
   "mapgl"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-selectel-token",
  "description": "API-ключ Selectel (X-Token)",
  "pattern": "(?:sel_?token|selectel_?api_?token|x-token)[\"']?\\s*[:=]\\s*[\"']?([A-Za-z0-9]{10,64}_\\d{4,8})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "sel_token",
   "seltoken",
   "selectel",
   "x-token"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-selectel-password",
  "description": "Пароль сервисного пользователя Selectel",
  "pattern": "(?:os_password|password)[\"']?\\s*[:=]\\s*[\"']?([^\\s\"'<>${}]{8,128})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "selcloud"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-timeweb-token",
  "description": "API-токен Timeweb Cloud",
  "pattern": "(?:twc_token|timeweb_cloud_token|timeweb_token|token)[\"']?\\s*[:=]\\s*[\"']?(eyJ[A-Za-z0-9_-]{10,}\\.eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "timeweb",
   "twc_token",
   "twcrc"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-cloudru-secret",
  "description": "Секрет ключа доступа Cloud.ru",
  "pattern": "(?:cloudru_(?:key_)?secret|evolution_(?:service_account_key_)?secret|key_secret|auth_secret)[\"']?\\s*[:=]\\s*[\"']?([A-Za-z0-9_+/=-]{16,128})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "cloudru",
   "cloud.ru",
   "evolution_"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-kontur-focus-key",
  "description": "Ключ API Контур.Фокус",
  "pattern": "key[\"']?\\s*[:=]\\s*[\"']?([0-9a-f]{40})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "focus-api",
   "kontur"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-kontur-diadoc-key",
  "description": "Ключ разработчика Контур.Диадок",
  "pattern": "ddauth_api_client_id\\s*=\\s*([A-Za-z0-9_-]{10,64})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "ddauth_api_client_id"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-kontur-extern-key",
  "description": "Ключ API Контур.Экстерн",
  "pattern": "kontur[-_]apikey[\"']?\\s*[:=]\\s*[\"']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
  "flags": "gi",
  "group": 1,
  "keywords": [
   "kontur-apikey",
   "kontur_apikey"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-snils",
  "description": "СНИЛС",
  "pattern": "\\b(\\d{3}[- ]\\d{3}[- ]\\d{3}[- ]\\d{2})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-snils-bare",
  "description": "СНИЛС (без разделителей)",
  "pattern": "(?:снилс|snils)[^0-9\\n]{0,30}?\\b(\\d{11})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-inn",
  "description": "ИНН физического лица",
  "pattern": "(?:инн|inn)[^0-9\\n]{0,30}?(\\d{12})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-passport",
  "description": "Паспорт РФ",
  "pattern": "(?:паспорт|passport|серия)[^0-9\\n]{0,30}?(\\d{2} ?\\d{2}[^0-9\\n]{0,12}?\\d{6})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-mir-card",
  "description": "Карта «Мир»",
  "pattern": "\\b(220[0-4][ -]?\\d{4}[ -]?\\d{4}[ -]?\\d{4})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [
   "220"
  ],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-oms",
  "description": "Полис ОМС",
  "pattern": "(?:полис|омс|oms|polis|енп)[^0-9\\n]{0,30}?\\b(\\d{4}[ -]?\\d{4}[ -]?\\d{4}[ -]?\\d{4})\\b",
  "flags": "gi",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "klyuchnik-phone",
  "description": "Мобильный телефон",
  "pattern": "(?:\\+7|\\b8)[ (-]{0,2}(9\\d{2}[ )-]{0,2}\\d{3}[ -]?\\d{2}[ -]?\\d{2})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": true
 },
 {
  "id": "telegram-bot-token",
  "description": "Токен Telegram-бота",
  "pattern": "\\b(\\d{5,16}:A[A-Za-z0-9_-]{34})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "yandex-api-key",
  "description": "API-ключ Яндекс Облака",
  "pattern": "\\b(AQVN[A-Za-z0-9_-]{35,38})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "yandex-iam-token",
  "description": "IAM-токен Яндекс Облака",
  "pattern": "\\b(t1\\.[A-Za-z0-9_-]+=*\\.[A-Za-z0-9_-]{86}=*)",
  "flags": "g",
  "group": 1,
  "keywords": [],
  "entropy": 0,
  "warn": false
 },
 {
  "id": "yandex-static-key",
  "description": "Статический ключ доступа Яндекс Облака",
  "pattern": "\\b(YC[A-Za-z0-9_-]{38})\\b",
  "flags": "g",
  "group": 1,
  "keywords": [
   "yandex",
   "яндекс"
  ],
  "entropy": 0,
  "warn": false
 }
];
