"""Loads the curated topic set from config/topics.yaml.

Single source of truth for both record_bag and replay_bag. Editing
config/topics.yaml is the supported way to change the survey topic set.
"""

import os

import yaml
from ament_index_python.packages import get_package_share_directory


def _load_required_topics() -> list[str]:
    cfg = os.path.join(
        get_package_share_directory("compton_reconstruction"),
        "config",
        "topics.yaml",
    )
    with open(cfg) as f:
        data = yaml.safe_load(f)
    return list(data["required_topics"])


REQUIRED_TOPICS = _load_required_topics()
