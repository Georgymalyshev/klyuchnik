const KEY_ADVICE = "Ключ, который попал в интернет или в чужие руки, считайте украденным. Удалить его из файла мало: его нужно отозвать (перевыпустить), тогда старый перестанет работать.";

const PD_ADVICE = "Это персональные данные. Уберите их из файла. Если файл уже выложен в интернет, удалите его вместе с историей изменений и сообщите человеку, чьи это данные.";

const ADVICE = {
  "klyuchnik-gigachat-auth-key": { service: "GigaChat (Сбер)", how: "Перевыпустите ключ авторизации в личном кабинете разработчика Сбера (раздел проекта GigaChat API).", link: "https://developers.sber.ru/docs/ru/gigachat/api/authorization" },
  "klyuchnik-tinvest-token": { service: "Т-Инвестиции", how: "Удалите токен в настройках Т-Инвестиций и выпустите новый.", link: "https://developer.tbank.ru/invest/intro/intro/token" },
  "klyuchnik-tbank-terminal-password": { service: "Т-Касса", how: "Смените пароль терминала в личном кабинете Т-Бизнеса.", link: "https://developer.tbank.ru/eacq/intro/developer/token" },
  "klyuchnik-yookassa-secret-key": { service: "ЮKassa", how: "Перевыпустите секретный ключ в личном кабинете ЮKassa (раздел ключей API).", link: "https://yookassa.ru/docs/support/merchant/payments/implement/keys" },
  "klyuchnik-vk-token": { service: "VK", how: "Удалите ключ доступа: у сообщества — в разделе «Работа с API», у приложения — в настройках приложения.", link: "https://dev.vk.com/ru/api/access-token/getting-started" },
  "klyuchnik-vk-token-old": { service: "VK", how: "Удалите ключ доступа: у сообщества — в разделе «Работа с API», у приложения — в настройках приложения.", link: "https://dev.vk.com/ru/api/access-token/getting-started" },
  "klyuchnik-dadata-key": { service: "DaData", how: "Смените API-ключ и секретный ключ в личном кабинете DaData.", link: "https://dadata.ru/api/" },
  "klyuchnik-ozon-seller-key": { service: "Ozon Seller", how: "Удалите API-ключ в личном кабинете продавца (настройки, раздел API-ключей) и создайте новый.", link: "https://docs.ozon.ru/api/seller/" },
  "klyuchnik-ozon-performance-secret": { service: "Ozon Performance", how: "Перевыпустите client_secret в кабинете Ozon Performance.", link: "https://docs.ozon.ru/api/performance/" },
  "klyuchnik-wb-token": { service: "Wildberries", how: "Удалите токен в личном кабинете продавца (раздел доступа к API) и создайте новый.", link: "https://dev.wildberries.ru/openapi/api-information" },
  "klyuchnik-avito-secret": { service: "Avito", how: "Перевыпустите client_secret в разделе API для профессионалов.", link: "https://developers.avito.ru/" },
  "klyuchnik-2gis-key": { service: "2ГИС", how: "Отключите ключ в Platform Manager 2ГИС и выпустите новый.", link: "https://docs.2gis.com/ru/platform-manager/subscription/managing-keys" },
  "klyuchnik-selectel-token": { service: "Selectel", how: "Удалите API-ключ в панели управления Selectel (профиль, раздел доступа).", link: "https://docs.selectel.ru/api/authorization/" },
  "klyuchnik-selectel-password": { service: "Selectel", how: "Смените пароль сервисного пользователя в панели управления Selectel.", link: "https://docs.selectel.ru/api/authorization/" },
  "klyuchnik-timeweb-token": { service: "Timeweb Cloud", how: "Удалите API-токен в панели Timeweb Cloud (раздел API) и создайте новый.", link: "https://timeweb.cloud/api-docs" },
  "klyuchnik-cloudru-secret": { service: "Cloud.ru", how: "Удалите ключ доступа сервисного аккаунта в консоли Cloud.ru и создайте новый.", link: "https://cloud.ru/docs/console_api/ug/topics/guides__api_key" },
  "klyuchnik-kontur-focus-key": { service: "Контур.Фокус", how: "Запросите новый ключ в личном кабинете Фокус.API или через поддержку Контура.", link: "https://developer.kontur.ru/" },
  "klyuchnik-kontur-diadoc-key": { service: "Контур.Диадок", how: "Выпустите новый ключ в Кабинете интегратора Диадока.", link: "https://developer.kontur.ru/doc/diadoc-api/authentication" },
  "klyuchnik-kontur-extern-key": { service: "Контур.Экстерн", how: "Запросите новый api-key для Экстерна.", link: "https://developer.kontur.ru/" },
  "telegram-bot-token": { service: "Telegram", how: "Напишите @BotFather команду /revoke и выберите бота.", link: "https://core.telegram.org/bots/features#botfather" },
  "yandex-api-key": { service: "Яндекс Облако", how: "Удалите API-ключ сервисного аккаунта в консоли Яндекс Облака.", link: "https://yandex.cloud/ru/docs/iam/operations/api-key/delete" },
  "yandex-iam-token": { service: "Яндекс Облако", how: "IAM-токен живёт до 12 часов. Отзовите ключ, которым он был получен.", link: "https://yandex.cloud/ru/docs/iam/concepts/authorization/iam-token" },
  "yandex-static-key": { service: "Яндекс Облако", how: "Удалите статический ключ доступа в консоли Яндекс Облака.", link: "https://yandex.cloud/ru/docs/iam/operations/sa/delete-access-key" },
};

function adviceFor(finding) {
  if (ADVICE[finding.rule]) return { type: "key", text: KEY_ADVICE, ...ADVICE[finding.rule] };
  return { type: "pd", text: PD_ADVICE };
}
