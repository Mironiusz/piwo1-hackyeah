SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
APP ?= accessway
export APP
ENV := source scripts/env.sh

.PHONY: api-show api-emulator api-device api-offline api-set api-check run-device tiles tiles-sample mock props uninstall osm sample aw-osm aw-sample aw-build aw-run aw-test aw-logs aw-screenshot aw-reset emulator-fast crash-logs test help setup setup-deps doctor emulator emulator-headless emulator-stop sign build install launch run apply lint logs screenshot layout clean

help:
	@echo "EnableMe - Krakow bez barier (HarmonyOS app in accessway/)"
	@echo ""
	@echo "make setup-deps      apt-install qemu + JDK 17, then full setup (sudo)"
	@echo "make setup           install oniro-app CLI, SDK (API 20), cmdtools, emulator; sign the app"
	@echo "make doctor          print toolchain status"
	@echo "make emulator        start Oniro emulator (window) and wait for hdc"
	@echo "make emulator-headless  start emulator without window (VNC :5900)"
	@echo "make emulator-fast   start emulator with more vCPUs/RAM (EMU_SMP, EMU_MEM, EMU_RES to override)"
	@echo "make emulator-stop   stop emulator"
	@echo "make build           build signed .hap"
	@echo "make run             build + install + launch on emulator/device"
	@echo "make test            run unit tests (domain logic) on Node with the SDK compiler"
	@echo "make lint            run OpenHarmony codelinter"
	@echo "make logs            follow app hilog for 60 s"
	@echo "make screenshot      save device screenshot to docs/screenshots/"
	@echo "make uninstall       uninstall the app (clears its saved data)"
	@echo "make sample          regenerate the sample map data (Tauron Arena area)"
	@echo "make osm             download real OpenStreetMap data for Krakow centre into the app (needs internet)"
	@echo "make tiles           download the vector map of Krakow (tiles/krakow.pmtiles, ~35 MB, needs internet)"
	@echo "make tiles-sample    build a small tile archive of the sample area (no internet)"
	@echo "make mock            run the mock map tile server on port 8090 (the emulator sees it at 10.0.2.2:8090)"
	@echo ""
	@echo "API server the app talks to (config/api.json, built into the package - run make run afterwards):"
	@echo "make api-show       print the current setting"
	@echo "make api-emulator   real backend on this computer, seen from the emulator (API_PORT=$(API_PORT), tiles from make mock)"
	@echo "make api-device     real backend on this computer, seen from a Huawei phone on the same Wi-Fi (LAN IP)"
	@echo "make api-set API_URL=http://host:port [TILES_URL=...]   any server, e.g. the hosted demo"
	@echo "make api-offline    no server, everything on the device"
	@echo "make api-check      call the API operations the app uses from this computer"
	@echo "make run-device     api-device + api-check + build + install + launch on the USB-connected phone"
	@echo "make clean           remove build outputs"
	@echo "Aliases kept for older notes: aw-run, aw-build, aw-test, aw-logs, aw-screenshot, aw-reset, aw-osm, aw-sample"

setup:
	scripts/setup.sh

setup-deps:
	scripts/setup.sh --install-deps

doctor:
	scripts/doctor.sh

emulator:
	$(ENV); oniro emulator start --wait-for-hdc 300 --log "$$ROOT/.tools/emulator.log"

emulator-headless:
	$(ENV); oniro emulator start --headless --wait-for-hdc 300 --log "$$ROOT/.tools/emulator.log"

emulator-stop:
	$(ENV); oniro emulator stop

props:
	$(ENV); [ -f "$$APP_DIR/local.properties" ] || printf 'sdk.dir=%s\n' "$$ONIRO_SDK_ROOT_DIR/linux" > "$$APP_DIR/local.properties"

sign: props
	$(ENV); oniro sign --bootstrap "$$APP_DIR"

build: sign
	$(ENV); oniro build "$$APP_DIR"

install:
	$(ENV); oniro app install "$$APP_DIR"

launch:
	$(ENV); oniro app launch "$$APP_DIR"

run: build install launch

apply: build
	$(ENV); oniro app apply "$$APP_DIR"

lint:
	$(ENV); oniro lint "$$APP_DIR"

logs:
	$(ENV); oniro watch --bundle "$$BUNDLE_NAME" --for 60000

screenshot:
	$(ENV); mkdir -p docs/screenshots; oniro screenshot -o "docs/screenshots/$$(date +%Y%m%d-%H%M%S).jpeg"

layout:
	$(ENV); oniro dump layout --bundle "$$BUNDLE_NAME"

clean:
	rm -rf $(APP)/entry/build $(APP)/build $(APP)/.hvigor

test:
	$(ENV); ETS="$$(find "$$ONIRO_SDK_ROOT_DIR/linux" -maxdepth 2 -type d -name ets | head -1)"; node tools/run-unit-tests.js "$$ETS" "$(APP)"

crash-logs:
	scripts/collect-crash.sh

EMU_SMP ?= $(shell n=$$(nproc); s=$$((n - 2)); [ $$s -gt 12 ] && s=12; [ $$s -lt 2 ] && s=2; echo $$s)
EMU_MEM ?= $(shell m=$$(awk '/MemTotal/ {print int($$2/1048576)}' /proc/meminfo); if [ $$m -ge 30 ]; then echo 8G; elif [ $$m -ge 15 ]; then echo 6G; else echo 4G; fi)
EMU_RES ?= 450x900

emulator-fast:
	$(ENV); oniro emulator stop >/dev/null 2>&1 || true
	$(ENV); echo "Starting emulator: $(EMU_SMP) vCPUs, $(EMU_MEM) RAM, $(EMU_RES)"; nohup "$$ONIRO_EMULATOR_DIR/images/run.sh" -s $(EMU_SMP) -m $(EMU_MEM) -r $(EMU_RES) > "$$ROOT/.tools/emulator.log" 2>&1 &
	$(ENV); for i in $$(seq 1 60); do sleep 5; oniro emulator connect >/dev/null 2>&1 && oniro devices | grep -q . && { echo "Emulator connected"; exit 0; }; done; echo "Emulator did not connect in 5 min - see .tools/emulator.log"; exit 1

AW_DATA := accessway/entry/src/main/resources/rawfile/data

osm:
	python3 tools/accessway_fetch_osm.py $(AW_DATA)/osm_krakow.json

sample:
	python3 tools/accessway_sample.py $(AW_DATA)/osm_sample.json

tiles:
	tools/fetch_krakow_tiles.sh

tiles-sample:
	python3 tools/mock_backend/make_sample_tiles.py

MOCK_PORT ?= 8090
API_PORT ?= 8000
API_HOST ?=
TILES_URL ?=

api-show:
	python3 tools/api_target.py show

api-emulator:
	python3 tools/api_target.py emulator --api-port $(API_PORT) --tiles-port $(MOCK_PORT)

api-device:
	python3 tools/api_target.py device --api-port $(API_PORT) --tiles-port $(MOCK_PORT) --host "$(API_HOST)"

api-set:
	[ -n "$(API_URL)" ] || { echo "Give the address: make api-set API_URL=http://host:port"; exit 2; }
	if [ -n "$(TILES_URL)" ]; then python3 tools/api_target.py set --base-url "$(API_URL)" --tiles-url "$(TILES_URL)"; else python3 tools/api_target.py set --base-url "$(API_URL)"; fi

api-offline:
	python3 tools/api_target.py offline

api-check:
	python3 tools/api_target.py check

run-device: api-device
	python3 tools/api_target.py check || echo "WARNING: the API does not answer yet - the app will show connection errors until it does"
	$(MAKE) run

mock:
	python3 tools/mock_backend/server.py --port $(MOCK_PORT)

aw-osm: osm
aw-sample: sample
aw-build: build
aw-run: run
aw-test: test
aw-logs: logs
aw-screenshot: screenshot
aw-reset: uninstall

uninstall:
	$(ENV); HDC="$$(command -v hdc || find "$$ONIRO_SDK_ROOT_DIR" -name hdc -type f | head -1)"; "$$HDC" uninstall "$$BUNDLE_NAME" || true
