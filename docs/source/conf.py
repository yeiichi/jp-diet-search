import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
else:
    sys.path.insert(0, str(ROOT))

project = "jp-diet-search"
author = "Eiichi Yamamoto"
copyright = "2026, Eiichi Yamamoto"
try:
    release = package_version("jp-diet-search")
except PackageNotFoundError:
    release = "0.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]
html_title = f"{project} {release}"

html_theme_options = {
    "sidebar_hide_name": False,
}

autosummary_generate = True
