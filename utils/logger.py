# utils/logger.py
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SEED, RESULTS_PATH, DP_ENABLED, HE_ENABLED,
    NOISE_MULTIPLIER, MAX_GRAD_NORM, DELTA,
    K_ANONYMITY, L_DIVERSITY, FL_ROUNDS,
    N_CLIENTS, EXPERIMENT_NAME
)

def log_result(client_id, metrics: dict):
    """
    Appends one result entry to results/EXPERIMENT_NAME.jsonl
    Never overwrites — every run adds a new line.
    """
    os.makedirs(RESULTS_PATH, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "experiment": EXPERIMENT_NAME,
        "client_id": client_id,
        "seed": SEED,
        "config": {
            "dp_enabled": DP_ENABLED,
            "he_enabled": HE_ENABLED,
            "noise_multiplier": NOISE_MULTIPLIER,
            "max_grad_norm": MAX_GRAD_NORM,
            "delta": DELTA,
            "k_anonymity": K_ANONYMITY,
            "l_diversity": L_DIVERSITY,
            "fl_rounds": FL_ROUNDS,
            "n_clients": N_CLIENTS,
        },
        "metrics": metrics
    }

    filepath = os.path.join( RESULTS_PATH, f"{EXPERIMENT_NAME}_seed{SEED}.jsonl")
    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[LOG] Saved → results/{EXPERIMENT_NAME}.jsonl")
    return entry


def log_round(client_id, fl_round, val_accuracy,
              train_loss, val_loss, epsilon, elapsed_seconds):
    """Convenience wrapper for per-round logging."""
    log_result(
        client_id=client_id,
        metrics={
            "fl_round": fl_round,
            "val_accuracy": val_accuracy,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "epsilon": epsilon,
            "training_time_seconds": elapsed_seconds
        }
    )