from pathlib import Path

PORT = "/dev/tty.usbmodem5A680115771"
ROBOT_ID = "chess_follower"

CELLS_FILE = Path("data/cells.json")
CELLS_IK_FILE = Path("data/cells_ik.json")
REST_FILE = Path("data/rest.json")
URDF_FILE = Path("data/so101_new_calib.urdf")
CORNERS_FILE = Path("corners.json")
Z_OFFSETS_FILE = Path("z_offsets.json")

HOVER_Z = 0.077

MOTOR_SPEED = 1000  # 0 = max speed (no limit); 1–32767 caps speed, smaller = slower

PLOCK_DEG = 22.0
GRIPPER_OPEN = 20.0
GRIPPER_CLOSED = 0.0
DEG_PER_CM = 8.0
