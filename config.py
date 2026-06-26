import os

# ── Reproducibility ──────────────────────────────────────────
SEED = 42

# ── Paths ─────────────────────────────────────────────────────
# BASE_PATH is the project root — derived from this file's own location.
# Every other path is relative to BASE_PATH so the repo is fully portable.
BASE_PATH     = os.path.dirname(os.path.abspath(__file__))
DATA_PATH     = os.path.join(BASE_PATH, "data", "anonymized")
NONIID_PATH   = os.path.join(BASE_PATH, "data", "noniid")
RESULTS_PATH  = os.path.join(BASE_PATH, "results")

CERT_FILE     = os.path.join(BASE_PATH, "server", "cert.pem")
KEY_FILE      = os.path.join(BASE_PATH, "server", "key.pem")
CHUNKS_FOLDER = os.path.join(BASE_PATH, "server", "received_chunks_bin")
AGG_CHUNKS_FOLDER = os.path.join(BASE_PATH, "server", "aggregated_chunks_bin")

# The single shared file written by Aggregate and read by all clients.
# Stored at the project root so all notebooks see the same path.
AGGREGATED_GRAD_FILE = os.path.join(
    BASE_PATH, "aggregated_gradient_global_encrypted.pkl"
)

# ── Federation ────────────────────────────────────────────────
N_CLIENTS   = 3
FL_ROUNDS   = 10
SERVER_URL  = "https://127.0.0.1:5055"
SERVER_PORT = 5055

# ── Anonymization ─────────────────────────────────────────────
K_ANONYMITY = 3
L_DIVERSITY = 2

# ── Model ─────────────────────────────────────────────────────
HIDDEN_DIM_1            = 128
HIDDEN_DIM_2            = 64
OUTPUT_DIM              = 5
LEARNING_RATE           = 1e-3
MAX_EPOCHS              = 50
EARLY_STOPPING_PATIENCE = 25
BATCH_SIZE              = 32

# ── Differential Privacy ──────────────────────────────────────
DP_ENABLED       = True
NOISE_MULTIPLIER = 1.0
MAX_GRAD_NORM    = 1.0
DELTA            = 1e-5

# ── Homomorphic Encryption ────────────────────────────────────
HE_ENABLED          = True
POLY_MODULUS_DEGREE = 8192
COEFF_MOD_BITS      = [60, 40, 40, 60]
GLOBAL_SCALE        = 2**40
CHUNK_SIZE          = 8000

# ── Attack Simulation ─────────────────────────────────────────
IS_BYZANTINE           = False
BYZANTINE_SCALE_FACTOR = 5000
CLIPPING_ENABLED       = True

# ── Experiment Label ──────────────────────────────────────────
# Change this every time you switch variants. Options:
#   centralised_baseline | local_only | fl_anon_only
#   fl_anon_he | fl_anon_dp | fl_anon_dp_he   ← current
#   epsilon_sweep | byzantine_attack | mitm_attack
#   noniid | scalability_2clients | scalability_5clients
EXPERIMENT_NAME = "fl_he_dp" # includes seed