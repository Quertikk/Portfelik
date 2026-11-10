"""NF7: portfel z 1000 wydatkami ładuje się poniżej 1 s (pomiar po stronie aplikacji)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import perf_check  # noqa: E402


def test_wallet_with_1000_expenses_loads_under_one_second():
    _, worst = perf_check.measure(1000)
    assert worst < perf_check.LIMIT_S
