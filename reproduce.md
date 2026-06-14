# Basic  version - Have to improve this


# Reproducing the paper results

## Environment setup (once)
conda env create -f environment.yml
conda activate privfedhealth
python scripts/setup.py

## Data
Download depression.csv from https://openpsychometrics.org/...
Place it at: data/raw/depression.csv
Run preprocessing notebooks in order: preprocessing/Depression{1,2,3}_Anonymization.ipynb

## Main experiment (Variant 6: FL + Anon + DP + HE, Seed 42)
Set in config.py: EXPERIMENT_NAME = "fl_anon_dp_he", SEED = 42

Tab 1: server/Global_Server.ipynb         → Run All, wait for "[SERVER] Listening"
Tabs 2-4: clients/main_framework/MLP_depression{1,2,3}_model.ipynb → Kernel Restart → Run All
After all clients send Round 1 chunks:
Tab 5: aggregation/Aggregate.ipynb        → Run All
Repeat Tab 5 for each of the 10 rounds.

## Expected output
results/fl_anon_dp_he.jsonl — one JSON line per round per client
Final val accuracy: ~77–82% (variance across seeds is expected)

## Running all 18 ablation variants
See config.py — change EXPERIMENT_NAME and toggle DP_ENABLED / HE_ENABLED per the
ablation table in the paper (Table 2). Repeat the above for each variant × seed combination.