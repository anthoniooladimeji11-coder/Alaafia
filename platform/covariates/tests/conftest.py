import pandas as pd
import pytest

from covariates.config import DICT_PARQUET, LGA_PARQUET


@pytest.fixture(scope="session")
def lga():
    if not LGA_PARQUET.exists():
        pytest.skip("covariates not built — run `covariates build`")
    return pd.read_parquet(LGA_PARQUET)


@pytest.fixture(scope="session")
def cov_dict():
    if not DICT_PARQUET.exists():
        pytest.skip("covariates not built — run `covariates build`")
    return pd.read_parquet(DICT_PARQUET)
