#!/usr/bin/env bash

set -euxo pipefail

echo "building image..."
docker buildx build -t arifwn/chromium-html-to-pdf-server .

echo "pushing image..."
docker push arifwn/chromium-html-to-pdf-server

echo "done!"
