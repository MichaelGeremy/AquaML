"""Shared preprocessing utilities."""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, List


def create_lag_features(
    df: pd.DataFrame,
    target_col: str,
    lags: List[int] = [1, 2, 3, 7, 14],
    extra_cols: List[str] | None = None,
) -> pd.DataFrame:
    """Add lagged versions of the target (and optional extra columns)."""
    out = df.copy()
    for lag in lags:
        out[f"{target_col}_lag{lag}"] = out[target_col].shift(lag)
    if extra_cols:
        for col in extra_cols:
            for lag in lags[:3]:  # fewer lags for exogenous
                out[f"{col}_lag{lag}"] = out[col].shift(lag)
    return out.dropna().reset_index(drop=True)


def create_sequences(
    data: np.ndarray,
    target: np.ndarray,
    seq_len: int = 30,
    horizon: int = 1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build supervised sequences for LSTM-style models.
    data: (n_timesteps, n_features)
    target: (n_timesteps,)
    Returns X (n_samples, seq_len, n_features), y (n_samples, horizon)
    """
    X, y = [], []
    for i in range(len(data) - seq_len - horizon + 1):
        X.append(data[i : i + seq_len])
        y.append(target[i + seq_len : i + seq_len + horizon])
    return np.array(X), np.array(y)


def temporal_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.2,
    date_col: str = "date",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Respect temporal order – never shuffle time series."""
    df = df.sort_values(date_col).reset_index(drop=True)
    split_idx = int(len(df) * (1 - test_ratio))
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def scale_features(
    train: np.ndarray,
    test: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    scaler = StandardScaler()
    train_s = scaler.fit_transform(train)
    test_s = scaler.transform(test)
    return train_s, test_s, scaler
