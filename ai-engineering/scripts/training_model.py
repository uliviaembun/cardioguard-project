"""Training script for CardioGuard.

Advanced AI requirements covered:
- TensorFlow Functional API model
- Custom Layer: RiskFeatureGate
- Custom Loss Function: cardio_guard_loss
- Custom Callback-like monitor used manually in a full tf.GradientTape loop
- TensorBoard scalar logging
- Export trained model to .keras
- Save scaler, feature columns, threshold, and metrics for production inference
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pickle
import random
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model, layers, regularizers

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
AI_DIR = SCRIPT_DIR.parent
REPO_ROOT = AI_DIR.parent
DATA_DIR = AI_DIR / "data"
ARTIFACT_DIR = AI_DIR / "artifacts"
MODEL_DIR = AI_DIR / "models"
LOG_DIR = AI_DIR / "logs" / "fit" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")

for directory in [DATA_DIR, ARTIFACT_DIR, MODEL_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

FEATURE_COLUMNS = [
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
    "age_years",
    "bmi",
    "bp_cat",
    "pulse_pressure",
    "map",
    "age_bmi",
    "age_ap_hi",
    "age_cholesterol",
    "bmi_ap_hi",
    "is_obese",
    "is_high_bp",
    "is_high_cholesterol",
    "is_high_glucose",
    "lifestyle_risk",
]
TARGET_COLUMN = "cardio"


def bp_category(ap_hi: float, ap_lo: float) -> int:
    """Ordinal blood-pressure category.

    0: normal, 1: elevated, 2: hypertension stage 1, 3: hypertension stage 2.
    """
    if ap_hi < 120 and ap_lo < 80:
        return 0
    if 120 <= ap_hi < 130 and ap_lo < 80:
        return 1
    if (130 <= ap_hi < 140) or (80 <= ap_lo < 90):
        return 2
    return 3


def add_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "bmi" not in df.columns:
        df["bmi"] = df["weight"] / ((df["height"] / 100.0) ** 2)

    df["bp_cat"] = [bp_category(h, l) for h, l in zip(df["ap_hi"], df["ap_lo"])]
    df["pulse_pressure"] = df["ap_hi"] - df["ap_lo"]
    df["map"] = df["ap_lo"] + (df["pulse_pressure"] / 3.0)

    # extra risk features
    df["age_bmi"] = df["age_years"] * df["bmi"]
    df["age_ap_hi"] = df["age_years"] * df["ap_hi"]
    df["age_cholesterol"] = df["age_years"] * df["cholesterol"]
    df["bmi_ap_hi"] = df["bmi"] * df["ap_hi"]

    df["is_obese"] = (df["bmi"] >= 30).astype(int)
    df["is_high_bp"] = ((df["ap_hi"] >= 140) | (df["ap_lo"] >= 90)).astype(int)
    df["is_high_cholesterol"] = (df["cholesterol"] >= 2).astype(int)
    df["is_high_glucose"] = (df["gluc"] >= 2).astype(int)
    df["lifestyle_risk"] = df["smoke"] + df["alco"] + (1 - df["active"])
    return df


def prepare_data(test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create scaled train/test arrays from root data/processed/cardio_cleaned.csv."""
    raw_path = REPO_ROOT / "data" / "processed" / "cardio_cleaned.csv"
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Tidak menemukan {raw_path}. Pastikan file data/processed/cardio_cleaned.csv sudah ada."
        )

    df = pd.read_csv(raw_path)
    df = add_feature_engineering(df)

    missing = [col for col in FEATURE_COLUMNS + [TARGET_COLUMN] if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut belum ada di dataset: {missing}")

    X = df[FEATURE_COLUMNS].astype("float32")
    y = df[TARGET_COLUMN].astype("float32").values.reshape(-1, 1)

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X).astype("float32")

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=test_size,
        random_state=SEED,
        stratify=y,
    )

    pd.DataFrame(X_train, columns=FEATURE_COLUMNS).to_csv(DATA_DIR / "X_train_scaled.csv", index=False)
    pd.DataFrame(X_test, columns=FEATURE_COLUMNS).to_csv(DATA_DIR / "X_test_scaled.csv", index=False)
    pd.DataFrame(y_train, columns=[TARGET_COLUMN]).to_csv(DATA_DIR / "y_train.csv", index=False)
    pd.DataFrame(y_test, columns=[TARGET_COLUMN]).to_csv(DATA_DIR / "y_test.csv", index=False)

    with open(ARTIFACT_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(ARTIFACT_DIR / "feature_columns.json", "w", encoding="utf-8") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)

    return X_train, X_test, y_train, y_test


def load_prepared_data_or_create(rebuild_data: bool = False):
    required = [
        DATA_DIR / "X_train_scaled.csv",
        DATA_DIR / "X_test_scaled.csv",
        DATA_DIR / "y_train.csv",
        DATA_DIR / "y_test.csv",
        ARTIFACT_DIR / "scaler.pkl",
        ARTIFACT_DIR / "feature_columns.json",
    ]

    if rebuild_data or not all(path.exists() for path in required):
        return prepare_data()

    X_train = pd.read_csv(DATA_DIR / "X_train_scaled.csv").values.astype("float32")
    X_test = pd.read_csv(DATA_DIR / "X_test_scaled.csv").values.astype("float32")
    y_train = pd.read_csv(DATA_DIR / "y_train.csv").values.astype("float32")
    y_test = pd.read_csv(DATA_DIR / "y_test.csv").values.astype("float32")
    return X_train, X_test, y_train, y_test


@tf.keras.utils.register_keras_serializable(package="CardioGuard")
class RiskFeatureGate(layers.Layer):
    """Trainable feature-wise gate to help the model emphasize useful risk features."""

    def build(self, input_shape):
        feature_dim = int(input_shape[-1])
        self.gate_logits = self.add_weight(
            name="gate_logits",
            shape=(feature_dim,),
            initializer="zeros",
            trainable=True,
        )
        super().build(input_shape)

    def call(self, inputs):
        gate = tf.nn.sigmoid(self.gate_logits)
        return inputs * gate

    def get_config(self):
        config = super().get_config()
        return config


@tf.keras.utils.register_keras_serializable(package="CardioGuard")
def cardio_guard_loss(y_true, y_pred):
    """BCE + false-negative penalty.

    For early disease-risk screening, false negatives are more dangerous than false positives,
    so the loss penalizes positive patients predicted as low risk.
    """
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-7, 1.0 - 1e-7)
    bce = tf.keras.backend.binary_crossentropy(y_true, y_pred)
    false_negative_penalty = tf.reduce_mean(y_true * tf.square(1.0 - y_pred), axis=-1)
    return bce + 0.05 * false_negative_penalty


def build_model(input_dim: int) -> Model:
    inputs = layers.Input(shape=(input_dim,), name="cardio_features")
    gated = RiskFeatureGate(name="risk_feature_gate")(inputs)
    x = layers.Concatenate(name="raw_plus_gated_features")([inputs, gated])
    x = layers.Dense(
        256,
        activation="swish",
        kernel_regularizer=regularizers.l2(1e-5),
        name="dense_256",
    )(x)
    x = layers.BatchNormalization(name="bn_256")(x)
    x = layers.Dropout(0.15, name="dropout_256")(x)
    x = layers.Dense(
        128,
        activation="swish",
        kernel_regularizer=regularizers.l2(1e-5),
        name="dense_128",
    )(x)
    x = layers.BatchNormalization(name="bn_128")(x)
    x = layers.Dropout(0.10, name="dropout_128")(x)
    residual = layers.Dense(64, activation="swish", name="residual_projection")(x)
    x = layers.Dense(64, activation="swish", name="dense_64")(x)
    x = layers.BatchNormalization(name="bn_64")(x)
    x = layers.Add(name="residual_add")([x, residual])
    x = layers.Dropout(0.10, name="dropout_64")(x)
    x = layers.Dense(32, activation="swish", name="dense_32")(x)
    x = layers.Dense(16, activation="swish", name="dense_16")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="risk_probability")(x)
    return Model(inputs=inputs, outputs=outputs, name="cardioguard_risk_model")


class CustomTrainingMonitor(tf.keras.callbacks.Callback):
    """Custom callback used manually because training uses a GradientTape loop."""

    def __init__(self, best_model_path: Path):
        super().__init__()
        self.best_model_path = best_model_path
        self.best_val_accuracy = 0.0
        self.best_val_auc = 0.0
        self.best_val_mae = float("inf")

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        val_accuracy = float(logs.get("val_accuracy", 0.0))
        val_auc = float(logs.get("val_auc", 0.0))
        val_mae = float(logs.get("val_mae_prob", float("inf")))
        improved = (
            val_accuracy > self.best_val_accuracy
            or (
                np.isclose(val_accuracy, self.best_val_accuracy)and val_auc > self.best_val_auc
            )
        )

        if improved:
            self.best_val_accuracy = val_accuracy
            self.best_val_auc = val_auc
            self.best_val_mae = val_mae
            self.model.save(self.best_model_path)
            print(
                f"  -> Best model updated | "
                f"val_accuracy={val_accuracy:.4f}, "
                f"val_auc={val_auc:.4f}, "
                f"val_mae_prob={val_mae:.4f}"
            )

def make_dataset(X, y, batch_size: int, training: bool = True):
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    if training:
        dataset = dataset.shuffle(buffer_size=len(X), seed=SEED, reshuffle_each_iteration=True)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

def compute_class_weights(y_train: np.ndarray) -> Dict[int, float]:
    positives = float(np.sum(y_train == 1))
    negatives = float(np.sum(y_train == 0))
    total = positives + negatives
    return {
        0: total / (2.0 * max(negatives, 1.0)),
        1: total / (2.0 * max(positives, 1.0)),
    }


def find_best_threshold(y_true: np.ndarray, y_prob: np.ndarray):
    y_true = y_true.reshape(-1).astype(int)
    y_prob = y_prob.reshape(-1)
    candidates = np.round(np.arange(0.20, 0.81, 0.01), 2)
    best = {"threshold": 0.5, "accuracy": 0.0, "mae_label": 1.0}

    for threshold in candidates:
        y_pred = (y_prob >= threshold).astype(int)
        accuracy = float(np.mean(y_pred == y_true))
        mae_label = float(np.mean(np.abs(y_pred - y_true)))
        if accuracy > best["accuracy"]:
            best = {
                "threshold": float(threshold),
                "accuracy": accuracy,
                "mae_label": mae_label,
            }
    return best


def evaluate_model(model, dataset, threshold: float = 0.5):
    loss_metric = tf.keras.metrics.Mean()
    acc_metric = tf.keras.metrics.BinaryAccuracy(threshold=threshold)
    mae_metric = tf.keras.metrics.MeanAbsoluteError()
    auc_metric = tf.keras.metrics.AUC(curve="ROC")
    precision_metric = tf.keras.metrics.Precision(thresholds=threshold)
    recall_metric = tf.keras.metrics.Recall(thresholds=threshold)

    all_y = []
    all_prob = []

    for x_batch, y_batch in dataset:
        y_prob = model(x_batch, training=False)
        loss_value = tf.reduce_mean(cardio_guard_loss(y_batch, y_prob))
        loss_metric.update_state(loss_value)
        acc_metric.update_state(y_batch, y_prob)
        mae_metric.update_state(y_batch, y_prob)
        auc_metric.update_state(y_batch, y_prob)
        precision_metric.update_state(y_batch, y_prob)
        recall_metric.update_state(y_batch, y_prob)
        all_y.append(y_batch.numpy())
        all_prob.append(y_prob.numpy())

    y_true = np.vstack(all_y)
    y_prob = np.vstack(all_prob)
    return {
        "loss": float(loss_metric.result().numpy()),
        "accuracy": float(acc_metric.result().numpy()),
        "mae_prob": float(mae_metric.result().numpy()),
        "auc": float(auc_metric.result().numpy()),
        "precision": float(precision_metric.result().numpy()),
        "recall": float(recall_metric.result().numpy()),
        "y_true": y_true,
        "y_prob": y_prob,
    }


def train(args):
    X_train, X_test, y_train, y_test = load_prepared_data_or_create(args.rebuild_data)

    train_ds = make_dataset(X_train, y_train, args.batch_size, training=True)
    val_ds = make_dataset(X_test, y_test, args.batch_size, training=False)

    model = build_model(X_train.shape[1])
    optimizer = tf.keras.optimizers.Adam(learning_rate=args.learning_rate)
    class_weights = compute_class_weights(y_train)
    writer = tf.summary.create_file_writer(str(LOG_DIR))
    monitor = CustomTrainingMonitor(MODEL_DIR / "cardioguard_best_model.keras")
    monitor.set_model(model)

    @tf.function
    def train_step(x_batch, y_batch):
        with tf.GradientTape() as tape:
            y_prob = model(x_batch, training=True)
            per_sample_loss = cardio_guard_loss(y_batch, y_prob)
            sample_weights = tf.where(
                tf.equal(y_batch, 1.0),
                tf.cast(class_weights[1], tf.float32),
                tf.cast(class_weights[0], tf.float32),
            )
            loss_value = tf.reduce_mean(per_sample_loss * tf.squeeze(sample_weights, axis=-1))

        grads = tape.gradient(loss_value, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))
        return loss_value, y_prob

    print("Mulai training CardioGuard...")
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    print(f"TensorBoard log dir: {LOG_DIR}")

    for epoch in range(args.epochs):
        train_loss_metric = tf.keras.metrics.Mean()
        train_acc_metric = tf.keras.metrics.BinaryAccuracy(threshold=0.5)
        train_mae_metric = tf.keras.metrics.MeanAbsoluteError()

        for x_batch, y_batch in train_ds:
            loss_value, y_prob = train_step(x_batch, y_batch)
            train_loss_metric.update_state(loss_value)
            train_acc_metric.update_state(y_batch, y_prob)
            train_mae_metric.update_state(y_batch, y_prob)

        val_result = evaluate_model(model, val_ds, threshold=0.5)

        logs = {
            "train_loss": float(train_loss_metric.result().numpy()),
            "train_accuracy": float(train_acc_metric.result().numpy()),
            "train_mae_prob": float(train_mae_metric.result().numpy()),
            "val_loss": val_result["loss"],
            "val_accuracy": val_result["accuracy"],
            "val_mae_prob": val_result["mae_prob"],
            "val_auc": val_result["auc"],
            "val_precision": val_result["precision"],
            "val_recall": val_result["recall"],
        }

        with writer.as_default():
            for key, value in logs.items():
                tf.summary.scalar(key, value, step=epoch)
            writer.flush()

        monitor.on_epoch_end(epoch, logs)

        if (epoch + 1) % args.print_every == 0 or epoch == 0:
            print(
                f"Epoch {epoch + 1:03d}/{args.epochs} | "
                f"loss={logs['train_loss']:.4f} | acc={logs['train_accuracy']:.4f} | "
                f"val_acc={logs['val_accuracy']:.4f} | val_mae_prob={logs['val_mae_prob']:.4f} | "
                f"val_auc={logs['val_auc']:.4f}"
            )

    final_eval = evaluate_model(model, val_ds, threshold=0.5)
    threshold_info = find_best_threshold(final_eval["y_true"], final_eval["y_prob"])
    tuned_eval = evaluate_model(model, val_ds, threshold=threshold_info["threshold"])

    metrics = {
        "default_threshold_0_5": {
            "accuracy": final_eval["accuracy"],
            "mae_prob": final_eval["mae_prob"],
            "auc": final_eval["auc"],
            "precision": final_eval["precision"],
            "recall": final_eval["recall"],
        },
        "tuned_threshold": {
            "threshold": threshold_info["threshold"],
            "accuracy": tuned_eval["accuracy"],
            "mae_prob": tuned_eval["mae_prob"],
            "mae_label": threshold_info["mae_label"],
            "auc": tuned_eval["auc"],
            "precision": tuned_eval["precision"],
            "recall": tuned_eval["recall"],
        },
        "notes": {
            "mae_prob": "MAE antara label 0/1 dan probabilitas risiko.",
            "mae_label": "MAE antara label 0/1 dan prediksi kelas thresholded; pada binary classification ini sama dengan error rate.",
        },
    }

    model_path = MODEL_DIR / "cardioguard_model.keras"
    model.save(model_path)

    with open(ARTIFACT_DIR / "threshold.json", "w", encoding="utf-8") as f:
        json.dump(threshold_info, f, indent=2)
    with open(ARTIFACT_DIR / "training_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\nTraining selesai.")
    print(f"Model final: {model_path}")
    print(f"Model terbaik: {MODEL_DIR / 'cardioguard_best_model.keras'}")
    print(f"Scaler: {ARTIFACT_DIR / 'scaler.pkl'}")
    print(f"Metrics: {ARTIFACT_DIR / 'training_metrics.json'}")
    print(f"Best threshold: {threshold_info}")
    print(f"Jalankan TensorBoard: tensorboard --logdir {AI_DIR / 'logs'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=5e-4)
    parser.add_argument("--print-every", type=int, default=5)
    parser.add_argument("--rebuild-data", action="store_true")
    train(parser.parse_args())
