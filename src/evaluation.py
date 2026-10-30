"""Domain-specific evaluation metrics for hydrological ML."""

from __future__ import annotations
import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix, mean_squared_error, r2_score
)


def nash_sutcliffe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Nash-Sutcliffe Efficiency (NSE). 1 = perfect, 0 = as good as mean, <0 = worse."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    numerator = np.sum((y_true - y_pred) ** 2)
    denominator = np.sum((y_true - np.mean(y_true)) ** 2)
    if denominator == 0:
        return np.nan
    return 1.0 - numerator / denominator


def kling_gupta(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Kling-Gupta Efficiency (KGE). 1 = perfect."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    r = np.corrcoef(y_true, y_pred)[0, 1]
    alpha = np.std(y_pred) / (np.std(y_true) + 1e-8)
    beta = np.mean(y_pred) / (np.mean(y_true) + 1e-8)
    return 1.0 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def regression_report(y_true, y_pred, prefix: str = "") -> dict:
    """Compact hydrological regression metrics."""
    return {
        f"{prefix}NSE": round(nash_sutcliffe(y_true, y_pred), 4),
        f"{prefix}KGE": round(kling_gupta(y_true, y_pred), 4),
        f"{prefix}RMSE": round(rmse(y_true, y_pred), 4),
        f"{prefix}MAE": round(mae(y_true, y_pred), 4),
        f"{prefix}R2": round(r2_score(y_true, y_pred), 4),
    }


def classification_metrics(y_true, y_pred, average: str = "weighted") -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "f1": round(f1_score(y_true, y_pred, average=average), 4),
        "precision": round(precision_score(y_true, y_pred, average=average, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, average=average, zero_division=0), 4),
    }


def dice_coefficient(y_true: np.ndarray, y_pred: np.ndarray, smooth: float = 1.0) -> float:
    """Dice score for binary or multi-class (macro) segmentation."""
    y_true = y_true.flatten().astype(bool)
    y_pred = y_pred.flatten().astype(bool)
    intersection = np.logical_and(y_true, y_pred).sum()
    return (2.0 * intersection + smooth) / (y_true.sum() + y_pred.sum() + smooth)


def iou_score(y_true: np.ndarray, y_pred: np.ndarray, smooth: float = 1.0) -> float:
    y_true = y_true.flatten().astype(bool)
    y_pred = y_pred.flatten().astype(bool)
    intersection = np.logical_and(y_true, y_pred).sum()
    union = np.logical_or(y_true, y_pred).sum()
    return (intersection + smooth) / (union + smooth)
