import os
import sys
import shutil
import subprocess
from pathlib import Path

import tensorflow as tf

REPO_URL = "https://github.com/fadligg/cardioguard-project.git"
BRANCH = "feat/ai-model"

WORK_ROOT = Path("/kaggle/working/cardioguard-project")

print("TensorFlow:", tf.__version__)
print("GPU devices:", tf.config.list_physical_devices("GPU"))
print("Current directory:", os.getcwd())

if WORK_ROOT.exists():
    print(f"Removing existing folder: {WORK_ROOT}")
    shutil.rmtree(WORK_ROOT)

print(f"Cloning branch '{BRANCH}' from {REPO_URL}")

subprocess.check_call([
    "git",
    "clone",
    "--branch",
    BRANCH,
    "--single-branch",
    REPO_URL,
    str(WORK_ROOT),
])

AI_DIR = WORK_ROOT / "ai-engineering"
training_script = AI_DIR / "scripts" / "training_model.py"

print("Repo cloned to:", WORK_ROOT)
print("AI dir:", AI_DIR)
print("Training script:", training_script)
print("Training script exists:", training_script.exists())

if not training_script.exists():
    raise FileNotFoundError(
        f"Training script not found: {training_script}. "
        f"Pastikan branch '{BRANCH}' sudah dipush ke GitHub dan file scripts/training_model.py ada di branch itu."
    )

cmd = [
    sys.executable,
    str(training_script),
    "--rebuild-data",
    "--epochs",
    "100",
    "--batch-size",
    "64",
]

print("Running:", " ".join(cmd))
subprocess.check_call(cmd, cwd=str(AI_DIR))