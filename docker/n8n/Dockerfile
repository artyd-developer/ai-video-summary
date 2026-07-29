ARG N8N_VERSION=latest
FROM n8nio/n8n:${N8N_VERSION}

USER root

# Установка ffmpeg через apk.static
RUN set -eux; \
  ALPINE_REPO="$(head -n 1 /etc/apk/repositories)"; \
  ALPINE_ARCH="$(cat /etc/apk/arch)"; \
  wget -qO /tmp/APKINDEX.tar.gz "${ALPINE_REPO}/${ALPINE_ARCH}/APKINDEX.tar.gz"; \
  APKTOOLS_VER="$(tar -xzO -f /tmp/APKINDEX.tar.gz APKINDEX | awk '$0 == "P:apk-tools-static" {found=1; next} found && /^V:/ {sub(/^V:/, ""); print; exit}')"; \
  if [ -z "${APKTOOLS_VER}" ]; then \
    echo >&2 "Failed to resolve apk-tools-static version"; \
    exit 1; \
  fi; \
  wget -qO /tmp/apk-tools-static.apk "${ALPINE_REPO}/${ALPINE_ARCH}/apk-tools-static-${APKTOOLS_VER}.apk"; \
  tar -xzf /tmp/apk-tools-static.apk -C /; \
  /sbin/apk.static add --no-cache ffmpeg; \
  rm -f /sbin/apk.static; \
  rm -rf /tmp/* /var/cache/apk/*

# Создаем рабочие директории
RUN mkdir -p /data/video /data/audio /data/result \
  && chown -R node:node /data \
  && chown -R node:node /home/node/.n8n

USER node