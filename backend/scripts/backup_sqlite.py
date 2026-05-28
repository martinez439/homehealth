"""Create a timestamped backup of the local SQLite database."""
from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "homehealth.db"
BACKUPS = ROOT / "backups"

if not DB.exists():
    raise SystemExit("No local homehealth.db found to back up.")
BACKUPS.mkdir(exist_ok=True)
target = BACKUPS / f"homehealth-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.db"
shutil.copy2(DB, target)
print(f"SQLite backup created: {target}")
