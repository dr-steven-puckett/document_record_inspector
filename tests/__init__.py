# This __init__.py makes tests/ a proper package so pytest can resolve
# ``from tests.conftest import ...`` against the local tool repo root
# rather than any other ``tests`` package on sys.path.
