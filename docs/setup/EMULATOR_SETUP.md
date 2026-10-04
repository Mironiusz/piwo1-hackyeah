# Emulator setup for the HarmonyOS client (Linux and Windows)

Instructions for a fresh session (human or agent) that has to install the OpenHarmony toolchain and the Oniro
emulator, then build and run the HarmonyOS client of this repository, the OpenHarmony project
`mobile_app/accessway/` (the product EnableMe, bundle `pl.hackyeah.accessway`). Everything is driven by
`mobile_app/Makefile`, so every `make` command below runs in `mobile_app/`, and every path is relative to it;
the toolchain versions are pinned in `mobile_app/scripts/env.sh`. The short path from a clean clone is in
`mobile_app/README.md`.

## What gets installed

| Item | Version / location | Installed by |
|---|---|---|
| `@oniroproject/oniro-app` CLI | 0.11.0, in `.tools/` of the repo | `make setup` |
| OpenHarmony SDK | 6.0, API 20, in `~/setup-ohos-sdk` (`ONIRO_SDK_ROOT_DIR`) | `make setup` |
| Command-line tools (hvigorw, ohpm, hdc, codelinter) | `~/command-line-tools` (`ONIRO_CMD_TOOLS_PATH`) | `make setup` |
| Oniro emulator (QEMU image, OpenHarmony 6.1) | `~/oniro-emulator` (`ONIRO_EMULATOR_DIR`) | `make setup` |
| Debug signing material | `accessway/signatures/`, `accessway/build-profile.json5` | `make sign` (also run by `make build`) |

The three home-directory paths can be overridden with the environment variables above before running any target.
Do not commit `accessway/local.properties`, `accessway/signatures/` or any keystore: they are machine-specific
and listed in `mobile_app/.gitignore`. The repository keeps `accessway/build-profile.json5` with an empty
`signingConfigs`; `make sign` generates fresh debug keys on each machine and writes their entry, with the
encrypted passwords, into that file. Do not commit that change: restore the file with
`git restore mobile_app/accessway/build-profile.json5` before committing, or mark it once with
`git update-index --skip-worktree mobile_app/accessway/build-profile.json5`.

Needs about 15 GB of free disk space, 8 GB RAM or more (the emulator takes 4 to 8 GB), and hardware
virtualization (Intel VT-x or AMD-V) enabled in BIOS/UEFI.

## Linux (x86_64, apt-based, e.g. Ubuntu 22.04/24.04)

### 1. Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y qemu-system-x86 openjdk-17-jdk-headless unzip curl make git python3
sudo usermod -aG kvm "$USER"      # then log out and back in
ls -l /dev/kvm                    # must exist and be accessible to your user
```

Node.js 20 or newer is required (`node -v`). If the distribution ships an older one, install it with nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
. ~/.nvm/nvm.sh && nvm install 20
```

`make setup-deps` runs the apt part for you and then the full setup.

### 2. Toolchain and emulator

From `mobile_app/`:

```bash
cd mobile_app
make setup        # oniro-app CLI, SDK 6.0 (API 20), command-line tools, emulator image,
                  # accessway/local.properties and signing
make doctor       # prints node, java, qemu, kvm, SDK and cmdtools status
```

`make sign` (run by every build) recreates `accessway/local.properties` when it is missing.

### 3. Start the emulator

```bash
make emulator-fast EMU_RES=540x1080     # recommended: more vCPUs and RAM, phone-like resolution
# or
make emulator                           # default settings, opens a window, waits for hdc
make emulator-headless                  # no window; view it with a VNC client on localhost:5900
```

`emulator-fast` picks vCPUs and RAM from the host (`EMU_SMP`, `EMU_MEM`, override if needed) and waits up to
5 minutes for `hdc`. The first boot takes 1 to 2 minutes. Log: `.tools/emulator.log`. Stop with
`make emulator-stop`.

Check the connection:

```bash
source scripts/env.sh && oniro devices          # should list one device
# manual fallback: ~/command-line-tools/sdk/default/openharmony/toolchains/hdc tconn 127.0.0.1:55555
```

### 4. Build, install and run EnableMe

```bash
make run         # build signed .hap, install, launch
make test        # domain unit tests on Node (no emulator needed)
make logs        # follow the app log for 60 s
make screenshot
make uninstall   # clears saved needs, reports, votes and local accounts
```

The signed package ends up in `accessway/entry/build/default/outputs/default/entry-default-signed.hap`.

## Windows 10/11

Two ways. The first (WSL2) is recommended because the project's `Makefile` and scripts are bash-only and the
command-line tools are downloaded automatically only on Linux.

### Option A: WSL2 (recommended)

1. In an administrator PowerShell:

   ```powershell
   wsl --install -d Ubuntu-24.04
   wsl --update
   ```

   Reboot if asked, start Ubuntu once and create the Linux user.

2. Make KVM available inside WSL2 (nested virtualization). On Windows 11 it is on by default; to be sure,
   create or edit `%UserProfile%\.wslconfig`:

   ```ini
   [wsl2]
   nestedVirtualization=true
   memory=12GB
   processors=6
   ```

   Then run `wsl --shutdown` in PowerShell and open Ubuntu again. Inside Ubuntu:

   ```bash
   ls -l /dev/kvm
   sudo usermod -aG kvm "$USER"    # close and reopen the WSL terminal afterwards
   ```

   If `/dev/kvm` does not exist, nested virtualization is not available (Windows 10, some Home editions,
   or virtualization disabled in BIOS). Use option B for the emulator then.

3. Clone the repository inside the Linux file system (for example `~/piwo1-hackyeah`), not under `/mnt/c/...`;
   builds on `/mnt/c` are very slow and file permissions break signing.

4. Follow the Linux section above unchanged (steps 1 to 4). The emulator window opens through WSLg on
   Windows 11. Without WSLg use `make emulator-headless` and connect a VNC viewer on Windows to
   `localhost:5900`.

### Option B: native Windows emulator

Use this when WSL2 has no `/dev/kvm`. The emulator runs natively; the app is built either in WSL2 (no KVM
needed for building) or on another Linux machine, and installed with `hdc`.

1. Enable the Windows feature "Windows Hypervisor Platform" (Control Panel, Turn Windows features on or off),
   reboot.
2. Install QEMU for Windows from https://www.qemu.org/download/ and add its folder (for example
   `C:\Program Files\qemu`) to `PATH`. Check: `qemu-system-x86_64 --version`.
3. Install Git for Windows (provides Git Bash, which the emulator launcher needs) and Node.js 20+.
4. Get the emulator image: download
   https://github.com/eclipse-oniro4openharmony/device_board_oniro/releases/latest/download/oniro_emulator.zip
   and unpack it, for example to `C:\oniro-emulator`. Alternatively `npx @oniroproject/oniro-app@0.11.0
   emulator install`.
5. Start it from the `images` folder: `.\run.bat` (in Git Bash: `./run.sh`). Options: `-s <vCPUs>`,
   `-m <RAM, e.g. 6G>`, `-r 540x1080`, `--headless` (then VNC on `localhost:5900`).
6. `hdc` for Windows comes with the OpenHarmony command-line tools, which on Windows must be downloaded
   manually from the Huawei developer site (Command Line Tools for HarmonyOS, needs a Huawei ID) and can be
   registered with `oniro-app cmdtools install --from-zip <zip>`. Then:

   ```powershell
   hdc tconn 127.0.0.1:55555
   hdc list targets
   ```

7. Build the signed `.hap` in WSL2 or on Linux (`make build`), copy
   `entry-default-signed.hap` to Windows and install:

   ```powershell
   hdc install -r entry-default-signed.hap
   hdc shell aa start -a EntryAbility -b pl.hackyeah.accessway
   ```

   When WSL2 and the native emulator run on the same machine, WSL2 can usually reach it directly with
   `hdc tconn <Windows host IP>:55555` (the host IP is the `nameserver` in `/etc/resolv.conf` inside WSL,
   or `localhost` with WSL mirrored networking), so `make run` works from WSL as well.

Untested on our side: option B. Option A was not tried on a real Windows machine either; the Linux steps it
reuses were.

## The service and the map on the emulator

The client talks to `docs/product/api_contract.md` at `base_url` and reads the map from one PMTiles archive of
Kraków at `tiles_url`, both in `accessway/entry/src/main/resources/rawfile/config/api.json`. The address of the
hosted demo is never committed: set it locally before the build and restore the file afterwards. For development
without the service, the mock of the host of the project serves the same contract and the archive:

```bash
make tiles        # tiles/krakow.pmtiles, about 35 MB, needs internet
make mock         # http://0.0.0.0:8090, API under /api, archive at /krakow.pmtiles
```

Inside the emulator the computer is `10.0.2.2`, so `base_url` is `http://10.0.2.2:8090` and `tiles_url`
`http://10.0.2.2:8090/krakow.pmtiles`. `python3 tools/mock_backend/contract_check.py` checks a running service
against the contract.

## Known behaviour of the emulator

- No GPU: rendering uses software OpenGL (llvmpipe; softpipe without KVM, see below). EnableMe draws its maps with Canvas for this reason;
  ArkGraphics 3D scenes may crash on the emulator.
- No GPS: "My location" ("Moja lokalizacja") shows an error message on the emulator. Use the address search or
  "Point on the map" ("Punkt na mapie") instead.
- Internet works from the guest through QEMU user networking; the host is `10.0.2.2` from inside the
  emulator.
- The first launch opens the "Your needs" ("Twoje potrzeby") screen. Pick a set or Skip ("Pomiń").
- Without a service (`base_url` empty in `accessway/entry/src/main/resources/rawfile/config/api.json`) the
  app works on bundled sample data around Tauron Arena in Kraków; the demo scenario is in `accessway/README.md`.
  The local moderator role is given to an account named `moderator` (Menu, Account, Create an account).

## Without KVM (cloud machines, nested VMs)

The image runs under plain TCG emulation, about ten times slower, with these adjustments (tested with QEMU 8.2 on
2026-10-04):

- CPU model: `-cpu Haswell-v4`. System services need AVX2 (`foundation` crashes with SIGILL on older models),
  and `-cpu max` makes the software renderer crash.
- Software renderer without a JIT: llvmpipe crashes on AVX2 code emulated by TCG, so switch Mesa to softpipe with
  an extra init file in `system.img`, written with `debugfs` while the emulator is stopped:
  `{"jobs":[{"name":"pre-init","cmds":["export GALLIUM_DRIVER softpipe","export DRAW_USE_LLVM 0"]}]}` as
  `/etc/init/softgl.cfg` (`debugfs -w -R "write softgl.cfg /etc/init/softgl.cfg" system.img`).
- Longer lifecycle limits and no freeze kill for the app, after every boot:
  `hdc shell param set persist.sys.abilityms.timeout_unit_time_ratio 10` and
  `hdc shell param set hiviewdfx.appfreeze.filter_bundle_name pl.hackyeah.accessway`.
- Keep the screen on: `hdc shell "power-shell wakeup; power-shell setmode 602"`, then swipe up to unlock.
- Screenshots: `snapshot_display` returns stale frames; use the QEMU monitor `screendump` instead. Its rows are
  1352 bytes long for a 450 px wide screen, so crop each row to 1350 bytes before reading it as RGB.
- Expect about 2 minutes to the first screen of the app and 10 to 30 s per screen change.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `make doctor` says `kvm: no access` | `sudo usermod -aG kvm $USER`, log out and in (WSL: close the terminal, `wsl --shutdown`) |
| `Emulator did not connect in 5 min` | Read `.tools/emulator.log`; check free RAM; try `make emulator-stop` then `make emulator-fast EMU_MEM=4G` |
| `oniro devices` empty although the window is up | `hdc tconn 127.0.0.1:55555`, then retry `make run` |
| Build fails with "sdk.dir" or SDK not found | Delete `accessway/local.properties` and run `make sign` |
| Install fails with a signature error | `make sign` then `make run`; if an older build with a different key is installed, `make uninstall` first |
| Screen too small | Restart with `make emulator-fast EMU_RES=540x1080` (or another `WxH`) |
| App shows stale data after an update | `make uninstall` then `make run` |

## Quick reference for an agent

```bash
# Linux or WSL2
cd mobile_app
make setup-deps                     # or: make setup (if apt packages are already present)
make emulator-fast EMU_RES=540x1080
make run
```
