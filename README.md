# compton_reconstruction

3D LM-MLEM Compton image reconstruction framework with Scene Data Fusion (SDF) for the H3D M400 detector mounted on a Spot robot.

This package consumes ROS topics published by the existing M400 driver
(`m400_driver` in the same workspace) and produces 3D radioactive source maps in the world frame, optionally constrained by an Octomap of the scene.

## Workspace layout

This package lives in `Gamma_Survey/src/` alongside the M400 driver and the Spot stack. Each subdirectory is a separate git repo, sharing the workspace.

```
~/Gamma_Survey/
└── src/
    ├── compton_camera/         # M400 driver (separate repo)
    ├── compton_reconstruction/ # this package (separate repo)
    ├── spot_ros/
    ├── spot_manipulation/
    └── maps/                   # lab_april_2026.ot
```

`m400_interfaces` is built in the same workspace, so a single sourcing line is enough at runtime:

```bash
source ~/Gamma_Survey/install/setup.bash
```

## Build

```bash
cd ~/Gamma_Survey
colcon build --packages-select compton_reconstruction --symlink-install
```

## Test

```bash
cd ~/Gamma_Survey
colcon test --packages-select compton_reconstruction
colcon test-result --verbose
```

## Bagging (Phase 1)

Two CLI entry points, installed as ROS 2 console scripts:

```bash
ros2 run compton_reconstruction record_bag [options]
ros2 run compton_reconstruction replay_bag <bag_path> [options]
```

`record_bag` wraps `ros2 bag record` and applies the QoS overrides in `config/qos_overrides.yaml` so the recorder's subscription matches the driver's `transient_local + reliable + keep_last(200)` publisher.

Default recorded topics (`compton_reconstruction/topics.py`):

| Required                          | Optional (`--include-extra`)        |
|-----------------------------------|-------------------------------------|
| `/m400/gamma_event_packet`        | `/m400/compton_image/compressed`    |
| `/tf`                             | `/odom`                             |
| `/tf_static`                      | `/vision`                           |
| `/spot_driver/joint_states`       | `/spot/odometry`                    |

The Octomap is **not** bagged — `lab_april_2026.ot` is a single map reused across all testing and is loaded directly from disk in Phase 7.

`replay_bag` reads bag metadata via the `rosbag2_py` Python API and prints a topic-presence sanity report (counts per topic, required/optional/extra), then plays the bag with `ros2 bag play`. Use `--inspect-only` to skip playback. Use `--qos-overrides <yaml>` to apply playback-side QoS overrides (off by default).

### Capture protocol

For initial validation (Phase 2 TF audit + Phase 4 reconstruction), capture two bags with the same known check source (e.g., ¹³⁷Cs or ²²Na) at a measured location:

1. **Static capture** (~2 min) — Spot stationary, source 1–2 m away at a measured XYZ. Used to verify TF rotation correctness (mean cone axis should point at the source).
   ```bash
   ros2 run compton_reconstruction record_bag -o cs137_static --duration 120
   ```
2. **Roving capture** (~2 min) — Spot walks a 2 m × 2 m square around the same source. Used to validate multi-view fusion (Phase 5).
   ```bash
   ros2 run compton_reconstruction record_bag -o cs137_roving --duration 120 --include-extra
   ```

Inspect a bag without playing it:
```bash
ros2 run compton_reconstruction replay_bag cs137_static --inspect-only
```

## Status

Phase 0 (bootstrap) and Phase 1 (bagging & replay) complete. See `/home/nrg-positron/.claude/plans/shiny-gliding-balloon.md` for the master plan and phase roadmap.
