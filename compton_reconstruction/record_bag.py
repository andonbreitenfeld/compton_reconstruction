"""Wrapper around `ros2 bag record` for Compton survey captures.

Records the curated topic set defined in compton_reconstruction.topics with
QoS overrides that match the M400 driver's transient_local + keep_last(200)
publisher (see config/qos_overrides.yaml).
"""

import argparse
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime

from ament_index_python.packages import get_package_share_directory

from compton_reconstruction.topics import REQUIRED_TOPICS


def _qos_overrides_path() -> str:
    share = get_package_share_directory("compton_reconstruction")
    return os.path.join(share, "config", "qos_overrides.yaml")


def _check_m400_interfaces_sourced() -> bool:
    try:
        import m400_interfaces.msg  # noqa: F401
        return True
    except ImportError:
        return False


def _build_command(output: str, topics: list[str], qos_overrides: str | None) -> list[str]:
    cmd = ["ros2", "bag", "record", "-o", output]
    if qos_overrides and os.path.exists(qos_overrides):
        cmd += ["--qos-profile-overrides-path", qos_overrides]
    cmd += topics
    return cmd


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output",
        help="Output bag directory. Defaults to ./compton_bag_<timestamp>.",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=0.0,
        help="Auto-stop after N seconds. 0 = run until SIGINT.",
    )
    parser.add_argument(
        "--topic", action="append", default=[],
        help="Additional topic to record (repeatable).",
    )
    parser.add_argument(
        "--no-qos-overrides", action="store_true",
        help="Skip the M400 QoS override file (not recommended).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the rosbag command without executing.",
    )
    args = parser.parse_args(argv)

    if not _check_m400_interfaces_sourced():
        print(
            "WARNING: m400_interfaces is not importable. Source the driver "
            "workspace before recording or playback will fail to deserialize "
            "GammaEventPacket messages.",
            file=sys.stderr,
        )

    if shutil.which("ros2") is None:
        print("ERROR: ros2 CLI not found on PATH.", file=sys.stderr)
        return 1

    output = args.output or f"compton_bag_{datetime.now():%Y%m%d_%H%M%S}"
    if os.path.exists(output):
        print(f"ERROR: output path already exists: {output}", file=sys.stderr)
        return 1

    topics = list(REQUIRED_TOPICS) + args.topic

    qos_overrides = None if args.no_qos_overrides else _qos_overrides_path()
    cmd = _build_command(output, topics, qos_overrides)

    print("Recording topics:")
    for t in topics:
        print(f"  {t}")
    print(f"Output: {output}")
    if qos_overrides:
        print(f"QoS overrides: {qos_overrides}")
    print(f"Command: {' '.join(shlex.quote(c) for c in cmd)}")
    if args.dry_run:
        return 0

    proc = subprocess.Popen(cmd, start_new_session=True)
    try:
        if args.duration > 0:
            print(f"Auto-stop in {args.duration:.1f} s. Ctrl-C to stop early.")
            time.sleep(args.duration)
            os.killpg(proc.pid, signal.SIGINT)
            proc.wait(timeout=10)
        else:
            print("Recording. Ctrl-C to stop.")
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        try:
            os.killpg(proc.pid, signal.SIGINT)
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait()
    rc = proc.returncode or 0
    print(f"Bag closed: {output} (rc={rc})")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
