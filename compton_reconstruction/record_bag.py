"""Wrapper around `ros2 bag record` for Compton survey captures.

Records the curated topic set with QoS overrides matching the M400 driver's
transient_local + reliable + keep_last(200) publisher (see
config/qos_overrides.yaml).
"""

import argparse
import os
import shlex
import subprocess
import sys

from ament_index_python.packages import get_package_share_directory


REQUIRED_TOPICS = [
    "/m400/gamma_event_packet",
    "/tf",
    "/tf_static",
    "/spot_driver/joint_states",
]


def _qos_overrides_path() -> str:
    share = get_package_share_directory("compton_reconstruction")
    return os.path.join(share, "config", "qos_overrides.yaml")


def _build_command(output: str | None, duration: float, extra_topics: list[str]) -> list[str]:
    cmd = ["ros2", "bag", "record",
           "--qos-profile-overrides-path", _qos_overrides_path()]
    if output:
        cmd += ["-o", output]
    if duration > 0:
        cmd += ["-d", str(duration)]
    cmd += REQUIRED_TOPICS + extra_topics
    return cmd


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", help="Output bag directory.")
    parser.add_argument("-d", "--duration", type=float, default=0.0,
                        help="Auto-stop after N seconds (0 = run until Ctrl-C).")
    parser.add_argument("--topic", action="append", default=[],
                        help="Additional topic to record (repeatable).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the rosbag command without executing.")
    args = parser.parse_args(argv)

    cmd = _build_command(args.output, args.duration, args.topic)
    print("Command:", " ".join(shlex.quote(c) for c in cmd))
    if args.dry_run:
        return 0

    try:
        return subprocess.run(cmd).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
