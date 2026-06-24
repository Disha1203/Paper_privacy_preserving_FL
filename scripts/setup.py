"""
Run once after cloning:          python scripts/setup.py
Run before each new experiment:  python scripts/setup.py --clean
"""
import os, subprocess, sys, shutil, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "server", "cert.pem")
KEY  = os.path.join(ROOT, "server", "key.pem")


def generate_certs():
    if os.path.exists(CERT) and os.path.exists(KEY):
        print("[SETUP] Certs already exist — skipping.")
        return
    os.makedirs(os.path.dirname(CERT), exist_ok=True)
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", KEY, "-out", CERT,
        "-days", "365", "-nodes", "-subj", "/CN=127.0.0.1"
    ], check=True)
    print("[SETUP] Certs written to server/")


def make_results_dir():
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    print("[SETUP] results/ directory ready.")


def check_python():
    major, minor = sys.version_info[:2]
    if (major, minor) != (3, 10):
        print(f"[SETUP] WARNING: expected Python 3.10, got {major}.{minor}")


def clean_experiment_state():
    """Delete all runtime state so the next experiment starts completely fresh."""
    targets = {
        "files": [
            os.path.join(ROOT, "results", "context.ser"),
            os.path.join(ROOT, "aggregated_gradient_global_encrypted.pkl"),
        ],
        "dirs": [
            os.path.join(ROOT, "server", "received_chunks_bin"),
            os.path.join(ROOT, "server", "aggregated_chunks_bin"),
        ],
        "glob_results_pth": ROOT,  # handled separately below
    }

    for path in targets["files"]:
        if os.path.exists(path):
            os.remove(path)
            print(f"[CLEAN] Removed {os.path.relpath(path, ROOT)}")
        else:
            print(f"[CLEAN] Not found (ok): {os.path.relpath(path, ROOT)}")

    for d in targets["dirs"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"[CLEAN] Cleared {os.path.relpath(d, ROOT)}/")
        else:
            print(f"[CLEAN] Not found (ok): {os.path.relpath(d, ROOT)}/")

    # Remove any .pth model files written to results/ by previous runs
    results_dir = os.path.join(ROOT, "results")
    pth_files = [f for f in os.listdir(results_dir) if f.endswith(".pth")]
    if pth_files:
        for f in pth_files:
            path = os.path.join(results_dir, f)
            os.remove(path)
            print(f"[CLEAN] Removed results/{f}")
    else:
        print("[CLEAN] No .pth model files to remove.")

    print("[CLEAN] State clean — safe to start new run.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete all runtime artifacts before starting a new experiment"
    )
    args = parser.parse_args()

    check_python()
    generate_certs()
    make_results_dir()

    if args.clean:
        clean_experiment_state()

    print("[SETUP] Done. Run: jupyter notebook")