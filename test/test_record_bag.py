import os

from compton_reconstruction import record_bag


def test_qos_overrides_installed():
    assert os.path.exists(record_bag._qos_overrides_path())


def test_command_includes_required_topics_and_qos(tmp_path):
    cmd = record_bag._build_command(
        output=str(tmp_path / "bag"),
        duration=0.0,
        extra_topics=[],
    )
    assert cmd[:3] == ["ros2", "bag", "record"]
    assert "--qos-profile-overrides-path" in cmd
    for t in record_bag.REQUIRED_TOPICS:
        assert t in cmd
