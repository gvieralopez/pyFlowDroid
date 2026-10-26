import logging

from pyflowdroid.analyze import analyze, analyze_apk, generate_report
from pyflowdroid.install import install_deps

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
)

__all__ = ["analyze", "analyze_apk", "generate_report", "install_deps"]

__version__ = "0.9.0-beta0"
