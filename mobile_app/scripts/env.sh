#!/usr/bin/env bash
# Shared configuration for all project scripts. Source it, do not execute it.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${APP:-accessway}"
APP_DIR="$ROOT/$APP"
TOOLS_DIR="$ROOT/.tools"

ONIRO_APP_VERSION="0.11.0"
OHOS_SDK_VERSION="6.0"
OHOS_SDK_API="20"
BUNDLE_NAME="$(sed -n 's/.*"bundleName": *"\([^"]*\)".*/\1/p' "$APP_DIR/AppScope/app.json5" 2>/dev/null | head -1)"
BUNDLE_NAME="${BUNDLE_NAME:-pl.hackyeah.accessway}"
HAP_PATH="$APP_DIR/entry/build/default/outputs/default/entry-default-signed.hap"

export ONIRO_SDK_ROOT_DIR="${ONIRO_SDK_ROOT_DIR:-$HOME/setup-ohos-sdk}"
export ONIRO_CMD_TOOLS_PATH="${ONIRO_CMD_TOOLS_PATH:-$HOME/command-line-tools}"
export ONIRO_EMULATOR_DIR="${ONIRO_EMULATOR_DIR:-$HOME/oniro-emulator}"

ONIRO_BIN="$TOOLS_DIR/node_modules/.bin/oniro-app"

oniro() {
  if [[ ! -x "$ONIRO_BIN" ]]; then
    echo "oniro-app is not installed. Run: make setup" >&2
    return 1
  fi
  "$ONIRO_BIN" "$@"
}

log() { printf '\033[1;34m==>\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }
