"""Locate extension roots without depending on the process cwd."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = PACKAGE_ROOT / "schemas"
CONFIGS_DIR = PACKAGE_ROOT / "configs"
DEVELOPMENT_CONFIGS_DIR = CONFIGS_DIR / "development"
FIXTURES_DIR = PACKAGE_ROOT / "fixtures"
SRC_DIR = PACKAGE_ROOT / "src"
