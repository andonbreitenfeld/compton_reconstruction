"""Curated topic sets for bag record and replay sanity checks.

Centralizing this list keeps record_bag.py and replay_bag.py in lockstep:
adding a new topic in one place is enough.
"""

REQUIRED_TOPICS = [
    "/m400/gamma_event_packet",
    "/tf",
    "/tf_static",
    "/spot_driver/joint_states",
]

OPTIONAL_TOPICS = [
    "/m400/compton_image/compressed",
    "/odom",
    "/vision",
    "/spot/odometry",
]

ALL_TOPICS = REQUIRED_TOPICS + OPTIONAL_TOPICS
