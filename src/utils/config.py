from pathlib import Path

PORT = "/dev/tty.usbmodem5A680115771"
ROBOT_ID = "chess_follower"

CELLS_FILE = Path("data/cells.json")
CORNERS_FILE = Path("corners.json")
Z_OFFSETS_FILE = Path("z_offsets.json")

PLOCK_DEG = 22.0
GRIPPER_OPEN = 20.0
GRIPPER_CLOSED = 0.0
DEG_PER_CM = 8.0
