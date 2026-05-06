"""Wrapper around `ros2 bag play` with a pre-flight topic-presence report.

Inspects the bag via rosbag2_py.Info, compares against the required topic
set from record_bag, and refuses to play (without --allow-missing) if any
required topic is absent.
"""

import argparse
import os
import subprocess
import sys

from rosbag2_py import Info

from compton_reconstruction.record_bag import REQUIRED_TOPICS


def _bag_info(path: str) -> dict[str, int]:
    """Return {topic_name: message_count} for a bag."""
    metadata = Info().read_metadata(path, "")  # "" = storage autodetect
    return {
        e.topic_metadata.name: e.message_count
        for e in metadata.topics_with_message_count
    }


def _print_report(counts: dict[str, int]) -> bool:
    print("\nTopic-presence report:")
    ok = True
    for t in REQUIRED_TOPICS:
        present = t in counts
        if not present:
            ok = False
        print(f"  {t:40s} {counts.get(t, 0):>8d}  "
              f"{'OK' if present else 'MISSING'}")
    extras = sorted(set(counts) - set(REQUIRED_TOPICS))
    if extras:
        print("  --- other topics in bag ---")
        for t in extras:
            print(f"  {t:40s} {counts[t]:>8d}")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bag", help="Path to bag directory.")
    parser.add_argument("--rate", type=float, default=1.0,
                        help="Playback rate multiplier (default 1.0).")
    parser.add_argument("--loop", action="store_true", help="Loop the bag.")
    parser.add_argument("--inspect-only", action="store_true",
                        help="Print the report and exit without playing.")
    parser.add_argument("--allow-missing", action="store_true",
                        help="Play even if required topics are missing.")
    args = parser.parse_args(argv)

    if not os.path.exists(args.bag):
        print(f"ERROR: bag path does not exist: {args.bag}", file=sys.stderr)
        return 1

    ok = _print_report(_bag_info(args.bag))

    if args.inspect_only:
        return 0 if ok else 2
    if not ok and not args.allow_missing:
        print("Required topics missing. Use --allow-missing to play anyway.",
              file=sys.stderr)
        return 2

    cmd = ["ros2", "bag", "play", args.bag, "--rate", str(args.rate)]
    if args.loop:
        cmd.append("--loop")
    try:
        return subprocess.run(cmd).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
