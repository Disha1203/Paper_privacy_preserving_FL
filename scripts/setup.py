# scripts/setup.py
"""Run once after cloning: python scripts/setup.py"""
import os, subprocess, sys

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
    print(f"[SETUP] Certs written to server/")

def make_results_dir():
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    print("[SETUP] results/ directory ready.")

def check_python():
    major, minor = sys.version_info[:2]
    if (major, minor) != (3, 10):
        print(f"[SETUP] WARNING: expected Python 3.10, got {major}.{minor}")

if __name__ == "__main__":
    check_python()
    generate_certs()
    make_results_dir()
    print("[SETUP] Done. Run: jupyter notebook")