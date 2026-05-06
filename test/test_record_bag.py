"""Smoke tests for record_bag / replay_bag wiring.

These don't actually run rosbag (no detector required); they verify the
modules import, the config file is present, and the dry-run command
contains the expected pieces.
"""
import os

from compton_reconstruction import record_bag, replay_bag, topics


def test_topics_loaded_from_yaml():
    assert "/m400/gamma_event_packet" in topics.REQUIRED_TOPICS
    assert "/tf" in topics.REQUIRED_TOPICS
    assert "/tf_static" in topics.REQUIRED_TOPICS
    assert "/spot_driver/joint_states" in topics.REQUIRED_TOPICS
    assert all(t.startswith("/") for t in topics.REQUIRED_TOPICS)


def test_qos_overrides_installed():
    path = record_bag._qos_overrides_path()
    assert os.path.exists(path), f"missing installed qos file: {path}"
    with open(path) as f:
        body = f.read()
    assert "/m400/gamma_event_packet" in body
    assert "transient_local" in body
    assert "depth: 200" in body


def test_record_command_includes_required_topics(tmp_path):
    out = str(tmp_path / "bag")
    cmd = record_bag._build_command(
        output=out,
        topics=topics.REQUIRED_TOPICS,
        qos_overrides=record_bag._qos_overrides_path(),
    )
    assert cmd[:3] == ["ros2", "bag", "record"]
    assert "--qos-profile-overrides-path" in cmd
    for t in topics.REQUIRED_TOPICS:
        assert t in cmd


def test_replay_module_importable():
    assert hasattr(replay_bag, "main")
    assert hasattr(replay_bag, "_print_report")
