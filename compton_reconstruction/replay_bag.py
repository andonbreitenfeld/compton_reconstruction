"""Wrapper around `ros2 bag play` with a pre-flight topic-presence report.

Inspects the bag via the rosbag2_py Python API, compares against the
curated topic set from compton_reconstruction.topics, and warns about
anything missing before starting playback.
"""

import argparse
import os
import shutil
import subprocess
import sys

from compton_reconstruction.topics import OPTIONAL_TOPICS, REQUIRED_TOPICS


def _check_m400_interfaces_sourced() -> bool:
    try:
        import m400_interfaces.msg  # noqa: F401
        return True
    except ImportError:
        return False


def _bag_info(path: str) -> list[tuple[str, str, int]]:
    """Read bag metadata via rosbag2_py.Info. Returns (topic, type, count)."""
    try:
        from rosbag2_py import Info  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "rosbag2_py is not importable. Install ros-<distro>-rosbag2-py "
            "or source a workspace that provides it."
        ) from e
    metadata = Info().read_metadata(path, "")  # "" = storage autodetect
    return [
        (entry.topic_metadata.name,
         entry.topic_metadata.type,
         entry.message_count)
        for entry in metadata.topics_with_message_count
    ]


def _print_report(found: list[tuple[str, str, int]]) -> bool:
    found_topics = {t[0] for t in found}
    print("\nTopic-presence report:")
    print("-" * 70)
    print(f"{'topic':40s}  {'count':>8s}   status")
    print("-" * 70)
    ok = True
    counts = {t[0]: t[2] for t in found}
    for t in REQUIRED_TOPICS:
        present = t in found_topics
        status = "OK" if present else "MISSING (required)"
        if not present:
            ok = False
        c = counts.get(t, 0)
        print(f"{t:40s}  {c:>8d}   {status}")
    for t in OPTIONAL_TOPICS:
        present = t in found_topics
        status = "OK" if present else "absent (optional)"
        c = counts.get(t, 0)
        print(f"{t:40s}  {c:>8d}   {status}")
    extras = found_topics - set(REQUIRED_TOPICS) - set(OPTIONAL_TOPICS)
    if extras:
        print("-" * 70)
        print("Other topics in bag:")
        for t in sorted(extras):
            print(f"  {t}  (count {counts.get(t, 0)})")
    print("-" * 70)
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bag", help="Path to bag directory.")
    parser.add_argument(
        "--rate", type=float, default=1.0,
        help="Playback rate multiplier (default 1.0).",
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="Loop the bag.",
    )
    parser.add_argument(
        "--inspect-only", action="store_true",
        help="Print the topic-presence report and exit (no playback).",
    )
    parser.add_argument(
        "--allow-missing", action="store_true",
        help="Play even if required topics are missing.",
    )
    parser.add_argument(
        "--qos-overrides", default=None,
        help=(
            "Optional QoS override YAML to apply on the playback publication "
            "side. Useful if a downstream subscriber needs durable replay."
        ),
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.bag):
        print(f"ERROR: bag path does not exist: {args.bag}", file=sys.stderr)
        return 1
    if shutil.which("ros2") is None:
        print("ERROR: ros2 CLI not found on PATH.", file=sys.stderr)
        return 1
    if not _check_m400_interfaces_sourced():
        print(
            "WARNING: m400_interfaces is not importable. Source the driver "
            "workspace or playback subscribers will fail to deserialize "
            "GammaEventPacket messages.",
            file=sys.stderr,
        )

    try:
        found = _bag_info(args.bag)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    ok = _print_report(found)

    if args.inspect_only:
        return 0 if ok else 2

    if not ok and not args.allow_missing:
        print(
            "Required topics missing. Re-run with --allow-missing to "
            "proceed anyway.",
            file=sys.stderr,
        )
        return 2

    cmd = ["ros2", "bag", "play", args.bag, "--rate", str(args.rate)]
    if args.loop:
        cmd.append("--loop")
    if args.qos_overrides:
        if not os.path.exists(args.qos_overrides):
            print(
                f"ERROR: --qos-overrides file not found: {args.qos_overrides}",
                file=sys.stderr,
            )
            return 1
        cmd += ["--qos-profile-overrides-path", args.qos_overrides]
    print(f"\nPlaying: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd).returncode or 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
