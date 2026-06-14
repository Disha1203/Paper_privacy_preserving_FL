"""
python scripts/verify_run.py --experiment fl_anon_dp_he --seed 42 --rounds 10
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESULTS_PATH

def verify(experiment, seed, expected_rounds, n_clients=3):
    filename = f"{experiment}_seed{seed}.jsonl"
    path = os.path.join(RESULTS_PATH, filename)

    if not os.path.exists(path):
        print(f"[FAIL] File not found: {filename}")
        return False

    with open(path) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    # Check we have entries from all clients
    clients_seen = set(e["client_id"] for e in entries)
    if len(clients_seen) < n_clients:
        print(f"[FAIL] Only {len(clients_seen)} client(s) logged: {clients_seen}")
        return False

    # Check round count per client
    for client in clients_seen:
        client_entries = [e for e in entries if e["client_id"] == client]
        fl_rounds = [e["metrics"]["fl_round"] for e in client_entries
                     if e["metrics"].get("fl_round", 0) > 0]
        if not fl_rounds or max(fl_rounds) < expected_rounds:
            print(f"[FAIL] {client} only reached round {max(fl_rounds) if fl_rounds else 0}")
            return False

    # Print final accuracies
    print(f"\n[OK] {filename}")
    print(f"     Clients logged : {sorted(clients_seen)}")
    for client in sorted(clients_seen):
        fl_entries = [e for e in entries
                      if e["client_id"] == client
                      and e["metrics"].get("fl_round", 0) > 0]
        if fl_entries:
            last = max(fl_entries, key=lambda e: e["metrics"]["fl_round"])
            acc = last["metrics"]["val_accuracy"]
            rnd = last["metrics"]["fl_round"]
            eps = last["metrics"].get("epsilon", "N/A")
            print(f"     {client}: round {rnd}, val_acc={acc:.4f}, ε={eps}")
    return True

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--experiment", required=True)
    p.add_argument("--seed",       type=int, required=True)
    p.add_argument("--rounds",     type=int, default=10)
    args = p.parse_args()
    ok = verify(args.experiment, args.seed, args.rounds)
    sys.exit(0 if ok else 1)