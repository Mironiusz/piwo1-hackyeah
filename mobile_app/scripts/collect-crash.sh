#!/usr/bin/env bash
# Collects everything needed to debug an app crash into .tools/crash/ (hilog, fault logs, device info).
# Usage: launch the app, reproduce the crash, then run: make crash-logs
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

OUT="$ROOT/.tools/crash"
rm -rf "$OUT"; mkdir -p "$OUT/faultlog"
HDC="$ONIRO_CMD_TOOLS_PATH/sdk/default/openharmony/toolchains/hdc"
[[ -x "$HDC" ]] || HDC="$(find "$ONIRO_CMD_TOOLS_PATH" "$ONIRO_SDK_ROOT_DIR" -type f -name hdc 2>/dev/null | head -1)"
[[ -x "$HDC" ]] || die "hdc not found"
echo "hdc: $HDC" > "$OUT/info.txt"
"$HDC" list targets >> "$OUT/info.txt" 2>&1

"$HDC" shell "hilog -x" > "$OUT/hilog_all.txt" 2>&1
grep -a -i -E "accessway|AccessWay|JsCrash|crash|exception|Error" "$OUT/hilog_all.txt" | tail -400 > "$OUT/hilog_filtered.txt"

"$HDC" shell "ls -lt /data/log/faultlog/faultlogger/ 2>/dev/null; ls -lt /data/log/faultlog/temp/ 2>/dev/null" > "$OUT/faultlog_list.txt" 2>&1
for f in $("$HDC" shell "ls -t /data/log/faultlog/faultlogger/ 2>/dev/null" | tr -d '\r' | head -5); do
  "$HDC" file recv "/data/log/faultlog/faultlogger/$f" "$OUT/faultlog/$f" >/dev/null 2>&1
done
"$HDC" shell "ps -ef | grep -i accessway" > "$OUT/ps.txt" 2>&1
"$HDC" shell "param get const.ohos.apiversion; param get const.product.software.version" >> "$OUT/info.txt" 2>&1
log "Crash data saved to $OUT"
ls -la "$OUT" "$OUT/faultlog"
