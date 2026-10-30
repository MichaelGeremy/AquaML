"""Consistent plotting helpers for AquaML notebooks."""

from __future__ import annotations
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

sns.set_theme(style="whitegrid", context="notebook", palette="deep")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 150
plt.rcParams["font.size"] = 11


def plot_timeseries_forecast(
    dates,
    y_true,
    y_pred,
    title: str = "Streamflow Forecast",
    ylabel: str = "Streamflow (m³/s)",
    save_path: Path | None = None,
):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(dates, y_true, label="Observed", color="#1f77b4", linewidth=1.5, alpha=0.9)
    ax.plot(dates, y_pred, label="Predicted", color="#ff7f0e", linewidth=1.5, alpha=0.85)
    ax.set_title(title, fontsize=14, fontweight="medium")
    ax.set_ylabel(ylabel)
    ax.legend(loc="upper right")
    ax.set_xlim(dates[0], dates[-1])
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig, ax


def plot_residuals(y_true, y_pred, title: str = "Residuals"):
    residuals = np.asarray(y_true) - np.asarray(y_pred)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].scatter(y_pred, residuals, alpha=0.5, s=15, edgecolor="none")
    axes[0].axhline(0, color="k", linestyle="--", linewidth=1)
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Residual (Obs − Pred)")
    axes[0].set_title("Residuals vs Predicted")
    axes[1].hist(residuals, bins=40, color="#2ca02c", edgecolor="white", alpha=0.85)
    axes[1].set_xlabel("Residual")
    axes[1].set_title("Residual Distribution")
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    return fig, axes


def plot_confusion_matrix(cm, class_names, title: str = "Confusion Matrix"):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names, ax=ax
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def plot_feature_importance(importances, feature_names, top_n: int = 12, title: str = "Feature Importance"):
    idx = np.argsort(importances)[::-1][:top_n]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(idx)), importances[idx][::-1], color="#1f77b4")
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([feature_names[i] for i in idx][::-1])
    ax.set_xlabel("Importance")
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def plot_segmentation_overlay(image, mask_true, mask_pred, alpha: float = 0.45):
    """Simple RGB image + true/pred mask side-by-side."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(image)
    axes[0].set_title("Input")
    axes[0].axis("off")
    axes[1].imshow(image)
    axes[1].imshow(mask_true, alpha=alpha, cmap="Blues")
    axes[1].set_title("Ground Truth")
    axes[1].axis("off")
    axes[2].imshow(image)
    axes[2].imshow(mask_pred, alpha=alpha, cmap="Oranges")
    axes[2].set_title("Prediction")
    axes[2].axis("off")
    fig.tight_layout()
    return fig, axes
