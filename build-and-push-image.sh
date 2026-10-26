#!/usr/bin/env bash

set -euxo pipefail

echo "building image..."
docker buildx build -t arifwn/chromium-html-to-pdf-server:1.0.1 .
docker buildx build -t arifwn/chromium-html-to-pdf-server:latest .

echo "pushing image..."
docker push arifwn/chromium-html-to-pdf-server:1.0.1
docker push arifwn/chromium-html-to-pdf-server:latest

echo "done!"
