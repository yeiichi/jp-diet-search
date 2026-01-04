import importlib


def test_import_package():
    pkg = importlib.import_module("jp_diet_search")
    assert pkg is not None
    assert hasattr(pkg, "DietClient")
