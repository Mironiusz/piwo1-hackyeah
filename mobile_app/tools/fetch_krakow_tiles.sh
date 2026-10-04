#!/usr/bin/env bash
# Downloads the vector map of Kraków for the mock tile server: one PMTiles archive cut out of the daily
# Protomaps build of OpenStreetMap data (plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md D-5 in
# piwo1-hackyeah), zoom 0-15, about 35 MB. Needs internet; the build of the newest day available is used.
#
# Usage: tools/fetch_krakow_tiles.sh            (writes tiles/krakow.pmtiles and tiles/krakow.pmtiles.build)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="1.31.2"
BBOX="19.7922355,49.9676668,20.2173455,50.1261338"
OUT_DIR="$ROOT/tiles"
BIN_DIR="$ROOT/.tools/pmtiles"
BIN="$BIN_DIR/pmtiles"

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) ASSET="go-pmtiles_${VERSION}_Linux_x86_64.tar.gz" ;;
  Linux-aarch64|Linux-arm64) ASSET="go-pmtiles_${VERSION}_Linux_arm64.tar.gz" ;;
  Darwin-x86_64) ASSET="go-pmtiles-${VERSION}_Darwin_x86_64.zip" ;;
  Darwin-arm64) ASSET="go-pmtiles-${VERSION}_Darwin_arm64.zip" ;;
  *) echo "Unsupported system $(uname -s)-$(uname -m); on Windows run this script in WSL2." >&2; exit 1 ;;
esac

if [[ ! -x "$BIN" ]]; then
  echo "==> Downloading go-pmtiles $VERSION"
  mkdir -p "$BIN_DIR"
  TMP="$(mktemp -d)"
  curl -fsSL -o "$TMP/$ASSET" "https://github.com/protomaps/go-pmtiles/releases/download/v${VERSION}/${ASSET}"
  if [[ "$ASSET" == *.zip ]]; then
    unzip -q -o "$TMP/$ASSET" -d "$TMP"
  else
    tar -xzf "$TMP/$ASSET" -C "$TMP"
  fi
  mv "$TMP/pmtiles" "$BIN"
  chmod +x "$BIN"
  rm -rf "$TMP"
fi

mkdir -p "$OUT_DIR"
for back in 0 1 2 3 4 5 6 7; do
  DAY="$(date -u -d "-$back day" +%Y%m%d 2>/dev/null || date -u -v-"$back"d +%Y%m%d)"
  URL="https://build.protomaps.com/${DAY}.pmtiles"
  if curl -fsI -o /dev/null "$URL"; then
    echo "==> Extracting Kraków from the build $DAY (zoom 0-15)"
    "$BIN" extract "$URL" "$OUT_DIR/krakow.pmtiles" --bbox="$BBOX" --maxzoom=15
    echo "$DAY" > "$OUT_DIR/krakow.pmtiles.build"
    ls -la "$OUT_DIR/krakow.pmtiles"
    echo "Done. Start the server with: make mock"
    exit 0
  fi
done
echo "No Protomaps build found for the last 8 days at https://build.protomaps.com/" >&2
exit 1
