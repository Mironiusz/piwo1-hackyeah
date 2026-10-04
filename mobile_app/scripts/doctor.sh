#!/usr/bin/env bash
# Prints the state of the toolchain - useful when something does not build.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

echo "node:    $(node -v 2>/dev/null || echo missing)"
echo "java:    $(java -version 2>&1 | head -1 || echo missing)"
echo "qemu:    $(qemu-system-x86_64 --version 2>/dev/null | head -1 || echo missing)"
echo "kvm:     $( [[ -r /dev/kvm && -w /dev/kvm ]] && echo ok || echo 'no access')"
echo "oniro:   $(oniro --version 2>/dev/null || echo 'not installed (make setup)')"
echo "SDK:     $ONIRO_SDK_ROOT_DIR"
oniro sdk list 2>/dev/null || true
echo "cmdtools:"
oniro cmdtools status 2>/dev/null || true
echo "devices:"
oniro devices 2>/dev/null || true
