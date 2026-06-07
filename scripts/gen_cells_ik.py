"""Generate data/cells_ik.json from data/cells.json using FK + fixed hover Z."""

import json
import numpy as np
from pathlib import Path

from lerobot.model.kinematics import RobotKinematics
from utils.config import CELLS_FILE, HOVER_Z, URDF_FILE

JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
OUT = Path("data/cells_ik.json")

cells = json.loads(CELLS_FILE.read_text())
kin = RobotKinematics(urdf_path=str(URDF_FILE), target_frame_name="gripper_frame_link", joint_names=JOINT_NAMES)

cells_ik = {}
for cell, pos in sorted(cells.items()):
    joints = np.array([pos[j] for j in JOINT_NAMES])
    T = kin.forward_kinematics(joints)
    T[2, 3] = HOVER_Z
    ik_joints = kin.inverse_kinematics(joints, T, orientation_weight=0.01)
    cells_ik[cell] = {
        "x": round(float(T[0, 3]), 6),
        "y": round(float(T[1, 3]), 6),
        "z": HOVER_Z,
        "hint": {name: round(float(val), 4) for name, val in zip(JOINT_NAMES, ik_joints)},
    }
    print(f"  {cell}  x={cells_ik[cell]['x']:.4f}  y={cells_ik[cell]['y']:.4f}  z={HOVER_Z}")

OUT.write_text(json.dumps(cells_ik, indent=2))
print(f"\nWritten {len(cells_ik)} cells to {OUT}")
