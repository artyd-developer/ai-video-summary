[English](README.md) | [Русский](README.ru.md)

# AI Video Summary

Автоматизированная платформа обработки видео на базе **n8n + FastAPI + PostgreSQL + Whisper**.

В текущем виде проект предоставляет полный pipeline для загрузки видео, извлечения аудио, транскрибации речи с помощью Whisper, сохранения статусов обработки и отправки отчётов через Telegram-бота.
<table>
  <tr>
    <td valign="top">
      <img src="https://github.com/user-attachments/assets/ee544494-b1ef-4d47-b655-1fbc55db4a44" width="606">
        <br>
      <img src="https://github.com/user-attachments/assets/18d101a4-6e7b-4963-b367-afe559076a44" width="606">
    </td>
    <td valign="top">
      <img src="https://github.com/user-attachments/assets/bc25582a-e8f7-4321-9756-dd5eba5973fa" width="522">
    </td>
  </tr>
</table>

---

# Возможности

- Загрузка видео через веб-интерфейс.
- Автоматическая AI-транскрибация видео.
- Получение отчётов транскрибации в Telegram.
- Отслеживание статуса обработки.
- Хранение обработанных видео и аудио.
- Готовые workflow n8n для импорта.

---

# Архитектура

<img width="1230" height="722" alt="hub4" src="https://github.com/user-attachments/assets/07f46fa0-ca28-464d-b1c8-4a3b416fe5a6" />

---

# Компоненты

## n8n

Проект содержит два workflow:

n8n_workflows/

├── Players Activity Report.json  
└── Processing Video Error Handler.json

<img width="1440" height="900" alt="scheme" src="https://github.com/user-attachments/assets/36e825b6-4291-442c-86bd-8a4d6e07909c" />

---

## Players Activity Report Workflow

Основной pipeline обработки видео:

1. Получает загруженный видеофайл.
2. Сохраняет видеофайл на диск.
3. Извлекает аудиодорожку.
4. Сохраняет аудиофайл.
5. Отправляет аудио в сервис Whisper.
6. Получает текст транскрибации.
7. Отправляет отчёт транскрибации в Telegram.
8. Обновляет статус операции в PostgreSQL.

---

## Processing Video Error Handler

Workflow отвечает за обработку ошибок:

- перехватывает неудачные выполнения;
- сохраняет состояние операции;
- отправляет уведомления об ошибках.

---

# Веб-интерфейс

Веб-сайт реализован на FastAPI.

Текущая функциональность:

## Страница загрузки видео

Позволяет пользователям загружать видеофайлы для обработки.

## Страница результатов

Отображает результаты обработки видео и сгенерированные данные.

---

# Требования

Перед установкой убедитесь, что у вас установлены:

- Docker
- Docker Compose

---

# Переменные окружения (.env)

Проект использует переменные окружения, хранящиеся в файле `.env`.

Создайте файл конфигурации:

cp .env.example .env

Заполните необходимые значения:

| Переменная | Описание | Пример |
|---|---|---|
| POSTGRES_USER | Имя пользователя PostgreSQL. Используется n8n и FastAPI. | admin |
| POSTGRES_PASSWORD | Пароль PostgreSQL. Используется PostgreSQL, n8n и FastAPI. | mySecurePassword123 |
| POSTGRES_DB | Имя базы данных PostgreSQL. | aivideosummary |
| TELEGRAM_BOT_TOKEN | Токен Telegram-бота, полученный через @BotFather. | 123456:ABCDEF... |
| TELEGRAM_CHAT_ID | ID Telegram-чата, куда будут отправляться отчёты. | -100123456789 |

---

# Сервис Whisper

Whisper запускается локально как Docker-сервис:

whisper:9000

Внутренний URL сервиса:

http://whisper:9000

Внешний API-ключ не требуется.

---

# Установка

## 1. Клонирование репозитория

git clone <repository_url>

cd aivideosummary


---

## 2. Создание файла окружения

Скопируйте пример конфигурации:

cp .env.example .env

Отредактируйте `.env` и заполните необходимые параметры.

---

## 3. Запуск Docker-контейнеров

docker compose up -d --build

После запуска:

Веб-сайт:

http://localhost

Интерфейс n8n:

http://localhost:5678

---

# Настройка n8n

После первого запуска импортируйте workflow.

Файлы workflow:

n8n_workflows/

Импортируйте:

Players Activity Report.json

Processing Video Error Handler.json

---

## Настройка Error Workflow

После импорта workflow необходимо подключить обработчик ошибок к основному workflow.

Откройте основной workflow:

Players Activity Report

Перейдите:

Workflow Settings
→ Error Workflow

Выберите:

Processing Video Error Handler

После этой настройки все ошибки выполнения основного workflow будут автоматически передаваться в Error Handler workflow.

Error Handler выполняет:

- получение информации об ошибке через узел `Error Trigger`;
- сохранение статуса ошибки в PostgreSQL;
- отправку уведомлений об ошибках в Telegram.

---

# Настройка Credentials в n8n

После импорта workflow необходимо создать два credential.

---

## PostgreSQL Account

Тип credential:

Postgres

Настройки:

Host:

postgres

Port:

5432

Database:

{{ $env.POSTGRES_DB }}

User:

{{ $env.POSTGRES_USER }}

Password:

{{ $env.POSTGRES_PASSWORD }}

---

## Telegram Report

Тип credential:

Telegram API

Bot Token:

{{ $env.TELEGRAM_BOT_TOKEN }}

API URL:

https://api.telegram.org

Назначьте эти credentials соответствующим узлам в обоих workflow. После этого запустите workflow в режиме отладки или production-режиме.
