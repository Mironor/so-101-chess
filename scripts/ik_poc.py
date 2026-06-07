"""
POC: FK/IK round-trip on cells.json using placo. No robot connection needed.

For each cell: convert joint angles → 3D position (FK), then back → joint angles (IK),
and report the round-trip error. If errors are small (<1°), IK is viable.
"""

import json
import numpy as np
from pathlib import Path

from lerobot.model.kinematics import RobotKinematics

URDF = "data/so101_new_calib.urdf"
JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]


def joints_array(pos: dict) -> np.ndarray:
    return np.array([pos[j] for j in JOINT_NAMES])


def main():
    cells = json.loads(Path("data/cells.json").read_text())
    kin = RobotKinematics(
        urdf_path=URDF,
        target_frame_name="gripper_frame_link",
        joint_names=JOINT_NAMES,
    )

    print(f"{'cell':>5}  {'x (m)':>8}  {'y (m)':>8}  {'z (m)':>8}  {'IK err max (°)':>16}")
    print("-" * 60)

    errors = []
    for cell, pos in sorted(cells.items()):
        joints = joints_array(pos)
        T = kin.forward_kinematics(joints)
        xyz = T[:3, 3]
        joints_ik = kin.inverse_kinematics(joints, T)
        err = float(np.max(np.abs(joints_ik - joints)))
        errors.append(err)
        print(f"  {cell}  {xyz[0]:8.4f}  {xyz[1]:8.4f}  {xyz[2]:8.4f}  {err:16.4f}")

    print("-" * 60)
    print(f"  mean error: {np.mean(errors):.4f}°   max: {np.max(errors):.4f}°")
    print()
    if np.max(errors) < 1.0:
        print("Round-trip looks good — IK is viable for this setup.")
    else:
        print("High round-trip error — IK may not be reliable for some cells.")


if __name__ == "__main__":
    main()
