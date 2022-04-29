import logging
from pyflowdroid.download import fetch
from pyflowdroid.install import install_deps
from pyflowdroid.analyze import analyze, analyze_apk, generate_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

__all__ = [
    'fetch',
    'install_deps',
    'analyze',
    'analyze_apk',
    'generate_report',
]

__version__ = '0.1.1'