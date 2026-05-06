# compton_reconstruction

3D LM-MLEM Compton image reconstruction with Scene Data Fusion for the H3D M400 detector on a Spot robot. Consumes ROS topics published by the M400 driver (`m400_driver`) and produces 3D source maps in `spot_nav/map`.

Lives in the `Gamma_Survey` workspace alongside the M400 driver and Spot stack.

## Build & test

```bash
cd ~/Gamma_Survey
colcon build --packages-select compton_reconstruction --symlink-install
source install/setup.bash
colcon test --packages-select compton_reconstruction
```

## Bagging

Two CLI tools:

```bash
ros2 run compton_reconstruction record_bag [-o OUT] [-d DURATION] [--topic /extra]
ros2 run compton_reconstruction replay_bag <bag> [--inspect-only] [--rate R] [--loop]
```

`record_bag` wraps `ros2 bag record` and applies the QoS overrides in `config/qos_overrides.yaml` so the recorder's subscription matches the driver's `transient_local + reliable + keep_last(200)` publisher. The recorded topic set is the constant `REQUIRED_TOPICS` in `record_bag.py`:

- `/m400/gamma_event_packet`
- `/tf`
- `/tf_static`

The detector is body-mounted, so `base_link → m400_crystal_array` is a static transform; no joint angles affect the detector's pose. `/tf` and `/tf_static` together carry every transform reconstruction needs (`spot_nav/map → odom → base_link → m400_crystal_array`).

`replay_bag` checks every required topic is present (via `rosbag2_py.Info`) before playing; refuses to play with required topics missing unless `--allow-missing` is passed.

The lab Octomap (`Gamma_Survey/src/maps/lab_april_2026.ot`) is **not** bagged — it is loaded directly from disk by Phase 7.

## Status

Phases 0 (bootstrap) and 1 (bagging & replay) complete. Master plan lives outside this repo.
