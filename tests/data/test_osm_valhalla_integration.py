"""Verify tile-tool failures and actual child-process cancellation locally."""

import asyncio
import os
import sys

import pytest

from data.osm_valhalla import OsmTileBuildError, apply_osm_valhalla_command


@pytest.mark.integration
@pytest.mark.parametrize("cancel", [False, True])
def test_cancellation_or_deadline_reaps_the_builder(tmp_path, cancel):
    pid_path = tmp_path / "pid"
    script = tmp_path / "invented_builder.py"
    script.write_text("import os, time\nfrom pathlib import Path\nPath(" + repr(str(pid_path)) + ").write_text(str(os.getpid()))\ntime.sleep(60)\n")

    async def run():
        deadline = asyncio.get_running_loop().time() + (60 if cancel else 0.3)
        task = asyncio.create_task(apply_osm_valhalla_command((sys.executable, str(script)), deadline))
        async with asyncio.timeout(2):
            while not pid_path.exists():
                await asyncio.sleep(0.01)
        if cancel:
            task.cancel()
        with pytest.raises(asyncio.CancelledError if cancel else OsmTileBuildError):
            await task

    asyncio.run(run())
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_path.read_text()), 0)


@pytest.mark.integration
@pytest.mark.parametrize("arguments", [("/invented/missing-tool",), (sys.executable, "-c", "raise SystemExit(1)")])
def test_unavailable_or_failed_tool_has_named_error(arguments):
    async def run():
        with pytest.raises(OsmTileBuildError):
            await apply_osm_valhalla_command(arguments, asyncio.get_running_loop().time() + 60)

    asyncio.run(run())
