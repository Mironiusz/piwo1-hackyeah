#!/usr/bin/env bash
# One-time environment setup on a Linux x86_64 host:
# checks prerequisites, installs the oniro-app CLI locally, the OpenHarmony SDK (API 20),
# the command-line tools (hvigorw, ohpm, hdc, codelinter) and the QEMU-based Oniro emulator.
#
# Usage: scripts/setup.sh [--install-deps] [--no-emulator]
#   --install-deps  install qemu + JDK 17 with apt (asks for sudo)
#   --no-emulator   skip the emulator download (e.g. when testing on a physical device)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

INSTALL_DEPS=0
WITH_EMULATOR=1
for arg in "$@"; do
  case "$arg" in
    --install-deps) INSTALL_DEPS=1 ;;
    --no-emulator) WITH_EMULATOR=0 ;;
    *) die "Unknown option: $arg" ;;
  esac
done

[[ "$(uname -s)" == "Linux" && "$(uname -m)" == "x86_64" ]] || die "This setup targets Linux x86_64."

if [[ $INSTALL_DEPS -eq 1 ]]; then
  command -v apt-get >/dev/null || die "--install-deps supports apt-based distros only. Install qemu-system-x86 and a JDK 17+ manually."
  log "Installing system packages (sudo)..."
  sudo apt-get update
  sudo apt-get install -y qemu-system-x86 openjdk-17-jdk-headless unzip curl
fi

log "Checking prerequisites..."
missing=0
command -v node >/dev/null || { warn "node not found (need >= 20, e.g. via nvm)"; missing=1; }
if command -v node >/dev/null; then
  node_major="$(node -p 'process.versions.node.split(".")[0]')"
  (( node_major >= 20 )) || { warn "node $(node -v) is too old, need >= 20"; missing=1; }
fi
command -v npm >/dev/null || { warn "npm not found"; missing=1; }
command -v java >/dev/null || { warn "java not found (need JDK 17+, used for signing)"; missing=1; }
command -v keytool >/dev/null || { warn "keytool not found (comes with the JDK)"; missing=1; }
command -v unzip >/dev/null || { warn "unzip not found"; missing=1; }
if [[ $WITH_EMULATOR -eq 1 ]]; then
  command -v qemu-system-x86_64 >/dev/null || { warn "qemu-system-x86_64 not found (apt: qemu-system-x86)"; missing=1; }
  if [[ ! -e /dev/kvm ]]; then
    warn "/dev/kvm missing - enable virtualization (VT-x) in BIOS"; missing=1
  elif [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
    warn "no access to /dev/kvm. Run: sudo usermod -aG kvm \$USER  and log out/in"; missing=1
  fi
fi
(( missing == 0 )) || die "Fix the prerequisites above (or rerun with --install-deps) and run setup again."

free_gb="$(df -BG --output=avail "$HOME" | tail -1 | tr -dc '0-9')"
if (( free_gb < 15 )); then
  warn "Only ${free_gb} GB free in \$HOME. SDK + tools + emulator need roughly 10-15 GB."
fi

log "Installing @oniroproject/oniro-app@$ONIRO_APP_VERSION into $TOOLS_DIR ..."
mkdir -p "$TOOLS_DIR"
npm install --prefix "$TOOLS_DIR" --no-fund --no-audit "@oniroproject/oniro-app@$ONIRO_APP_VERSION"
oniro --version

log "Installing OpenHarmony SDK $OHOS_SDK_VERSION (API $OHOS_SDK_API) into $ONIRO_SDK_ROOT_DIR ..."
oniro sdk install "$OHOS_SDK_VERSION"

log "Installing command-line tools (hvigorw, ohpm, hdc, codelinter) into $ONIRO_CMD_TOOLS_PATH ..."
oniro cmdtools install

if [[ $WITH_EMULATOR -eq 1 ]]; then
  log "Installing Oniro emulator (OpenHarmony 6.1, QEMU) into $ONIRO_EMULATOR_DIR ..."
  oniro emulator install
fi

log "Writing $APP/local.properties ..."
printf 'sdk.dir=%s\n' "$ONIRO_SDK_ROOT_DIR/linux" > "$APP_DIR/local.properties"

log "Signing the app with the local OpenHarmony debug keystore ..."
oniro sign --bootstrap "$APP_DIR"

log "Done. Next: make emulator (in one terminal), then make run"
