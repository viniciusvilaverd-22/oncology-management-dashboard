#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/oncology-management-dashboard"
WEB_DIR="/var/www/html/oncology-dashboard"
NODE_BIN="${NODE_BIN:-$(command -v node)}"
NODE_DIR="$(dirname "$NODE_BIN")"

cd "$APP_DIR/backend"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

deactivate
cd "$APP_DIR/frontend"
npm ci
sudo env PATH="$NODE_DIR:/usr/bin:/bin" \
  VITE_API_BASE=/oncology-dashboard \
  npm run build -- --base=/oncology-dashboard/

sudo mkdir -p "$WEB_DIR"
sudo rsync -a --delete dist/ "$WEB_DIR/"

echo "Install the example systemd and Apache configuration files after reviewing users, paths and TLS settings for your environment."
