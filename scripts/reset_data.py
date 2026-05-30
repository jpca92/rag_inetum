from pathlib import Path
import shutil


paths = [
    "data/raw",
    "data/clean",
    "data/chroma",
    "database/conversations.db",
]


for path in paths:
    current_path = Path(path)

    if current_path.is_dir():
        shutil.rmtree(current_path)
        current_path.mkdir(parents=True, exist_ok=True)

    elif current_path.exists():
        current_path.unlink()


print("Local data reset completed.")