from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def load(device: str, name: str = "config.conf") -> str:
    """Read a device config fixture from tests/fixtures/<device>/<name>."""
    return (FIXTURES / device / name).read_text(encoding="utf-8")
