from importlib.metadata import PackageNotFoundError, version

try:
    # the version is set in pyproject.toml only
    __version__ = version("settlement")
except PackageNotFoundError:
    __version__ = "unknown"
