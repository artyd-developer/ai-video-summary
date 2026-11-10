
[English](README.md) | [Русский](README.ru.md)

# AI Video Summary

Automated video processing platform based on **n8n + FastAPI + PostgreSQL + Whisper**.

Currently, the project provides a complete pipeline for uploading videos, extracting audio, transcribing speech using Whisper, storing processing states, and sending reports through a Telegram bot.
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

# Features

- Upload videos through a web interface.
- Automatic video transcription using AI.
- Receive transcription reports in Telegram.
- Track processing status.
- Store processed videos, audio.
- Ready-to-use n8n automation workflows.

---

# Architecture

<img width="1230" height="722" alt="hub4" src="https://github.com/user-attachments/assets/07f46fa0-ca28-464d-b1c8-4a3b416fe5a6" />



---

# Components

## n8n

The project contains two workflows:

```
n8n_workflows/
├── Players Activity Report.json
└── Processing Video Error Handler.json
```
<img width="1440" height="900" alt="scheme" src="https://github.com/user-attachments/assets/36e825b6-4291-442c-86bd-8a4d6e07909c" />

---

## Players Activity Report Workflow

Main video processing pipeline:

1. Receives uploaded video.
2. Saves video file to disk.
3. Extracts audio track.
4. Saves audio file.
5. Sends audio to Whisper service.
6. Receives transcription text.
7. Sends transcription report to Telegram.
8. Updates operation status in PostgreSQL.

---

## Processing Video Error Handler

Workflow responsible for error processing:

* catches failed executions;
* stores operation state;
* sends error notifications.

---

# Web Interface

The website is implemented using FastAPI.

Current functionality:

## Video Upload Page

Allows users to upload video files for processing.

## Results Page

Displays processed video results and generated data.

---

# Requirements

Before installation, make sure you have:

* Docker
* Docker Compose

---

# Environment Variables (.env)

The project uses environment variables stored in the `.env` file.

Create your configuration file:

```bash
cp .env.example .env
```

Fill in the required values:

| Variable             | Description                                               | Example               |
| -------------------- | --------------------------------------------------------- | --------------------- |
| `POSTGRES_USER`      | PostgreSQL username. Used by n8n and FastAPI.             | `admin`               |
| `POSTGRES_PASSWORD`  | PostgreSQL password. Used by PostgreSQL, n8n and FastAPI. | `mySecurePassword123` |
| `POSTGRES_DB`        | PostgreSQL database name.                                 | `aivideosummary`      |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token received from @BotFather.              | `123456:ABCDEF...`    |
| `TELEGRAM_CHAT_ID`   | Telegram chat ID where reports will be sent.              | `-100123456789`       |

---

# Whisper Service

Whisper runs locally as a Docker service:

```
whisper:9000
```

Internal service URL:

```
http://whisper:9000
```

No external API key is required.

---

# Installation

## 1. Clone repository

```bash
git clone <repository_url>

cd aivideosummary
```

---

## 2. Create environment file

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` and fill required parameters.

---

## 3. Start Docker containers

```bash
docker compose up -d --build
```

After startup:

Website:

```
http://localhost
```

n8n interface:

```
http://localhost:5678
```

---

# n8n Setup

After the first launch, import workflows.

Workflow files:

```
n8n_workflows/
```

Import:

```
Players Activity Report.json

Processing Video Error Handler.json
```

---

## Configure Error Workflow

After importing the workflows, connect the error handler workflow to the main processing workflow.

Open the main workflow:

```
Players Activity Report
```

Go to:

```
Workflow Settings
    → Error Workflow
```

Select:

```
Processing Video Error Handler
```

After this configuration, all execution errors from the main workflow will automatically trigger the Error Handler workflow.

The Error Handler performs:

* receiving error information through the `Error Trigger` node;
* storing error status in PostgreSQL;
* sending error notifications to Telegram.

---

# n8n Credentials Setup

After importing workflows, create two credentials.

---

## PostgreSQL Account

Credential type:

```
Postgres
```

Configuration:

Host:

```
postgres
```

Port:

```
5432
```

Database:

```
{{ $env.POSTGRES_DB }}
```

User:

```
{{ $env.POSTGRES_USER }}
```

Password:

```
{{ $env.POSTGRES_PASSWORD }}
```

---

## Telegram Report

Credential type:

```
Telegram API
```

Bot Token:

```
{{ $env.TELEGRAM_BOT_TOKEN }}
```

API URL:

```
https://api.telegram.org
```

Assign these credentials to the nodes in both workflows. Then run the workflows in debug or production mode.
