import pandas as pd
import pytest

from surveylayer.config import INDICATOR_PARQUET, SERIES_PARQUET


@pytest.fixture(scope="session")
def indicators():
    if not INDICATOR_PARQUET.exists():
        pytest.skip("survey layer not built — run `surveylayer build`")
    return pd.read_parquet(INDICATOR_PARQUET)


@pytest.fixture(scope="session")
def series():
    if not SERIES_PARQUET.exists():
        pytest.skip("survey layer not built — run `surveylayer build`")
    return pd.read_parquet(SERIES_PARQUET)
