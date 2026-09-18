import pytest

from brief.config import FH_STATE
from brief.data import build_profile

pytestmark = pytest.mark.skipif(
    not FH_STATE.exists(), reason="platform/model not built — see its README",
)


@pytest.fixture(scope="session")
def katsina():
    return build_profile("NG021")          # Katsina — thin-coverage + full-coverage mix
