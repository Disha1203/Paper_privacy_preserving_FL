# Hybrid Privacy-Preserving Federated Learning for Healthcare

> A prototype federated learning framework combining **Data Anonymization**, **Differential Privacy**, and **Homomorphic Encryption** in a Federated Learning pipeline for mental health risk stratification.


## What This Project Does

This project proposes and implements a layered privacy-preserving Federated Learning (FL) framework applied to the DASS (Depression, Anxiety and Stress Scales) mental health dataset. The core idea is that no single privacy technique is sufficient on its own — so we combine three complementary methods, each protecting a different stage of the pipeline:

| Stage | Technique | What It Protects |
|---|---|---|
| Data preprocessing | k-Anonymity (k=3) + l-Diversity (l=2) | Re-identification from raw records |
| Local model training | Differential Privacy via Opacus (ε≈1.86, δ=1e-5) | Gradient leakage from individual samples |
| Gradient communication | Homomorphic Encryption — CKKS via TenSEAL | Interception and tampering in transit |
| Server aggregation | Encrypted FedAvg (no server-side decryption) | Zero-trust server behavior |

The output is a 5-class depression risk stratification model: **Normal / Mild / Moderate / Severe / Extremely Severe**


## Repository Structure

```
hybrid-privacy-fl-healthcare/
│
├── README.md
│
├── data/
│   ├── anonymized/               # Pre-anonymized hospital datasets (3 clients)
│   │     Final_Depression1_anonymised.csv
│   │     Final_Depression2_anonymised.csv
│   │     Final_Depression3_anonymised.csv
│   │     Test_set_Depression1_anonymised.csv
│   ├── raw/                      # Place depression.csv here (not tracked)
│   └── synthetic/
│         synthetic_test_set.csv
│
├── preprocessing/                # Step 1 — run these first
│     Data_cleaning.ipynb
│     Depression1_Anonymization.ipynb
│     Depression2_Anonymization.ipynb
│     Depression3_Anonymization.ipynb
│     Depression_Anonymization_evaluation.ipynb
│
├── server/                       # Step 2 — start this before clients
│     Global_Server.ipynb         ← Main server (with HE)
│     Global_Server_without_HE.ipynb
│
├── clients/
│   ├── main_framework/           # Step 3 — run all 3 simultaneously
│   │     MLP_depression1_model.ipynb   ← Hospital 1 (FL + Anon + DP + HE)
│   │     MLP_depression2_model.ipynb   ← Hospital 2
│   │     MLP_depression3_model.ipynb   ← Hospital 3
│   ├── variant_no_HE/            # Variant: FL + Anonymization + DP only
│   │     MLP_depression1_without_HE.ipynb
│   │     MLP_depression2_without_HE.ipynb
│   │     MLP_depression3_without_HE.ipynb
│   └── baseline/                 # Baseline: no privacy
│         MLP_Depression_original.ipynb
│         MLP_Without_DP.ipynb
│
├── aggregation/                  # Step 4 — run after all 3 clients finish
│     Aggregate.ipynb             ← Encrypted aggregation (with HE)
│     Aggregate_without_HE.ipynb
│
├── attacks/
│   ├── byzantine/                # Replace Client 1 with this to test Byzantine
│   │     Byzantine_Client1.ipynb
│   └── mitm/                     # Run proxy server + client variants to test MITM
│         MITM_proxy_server.ipynb
│         client_MITM.ipynb       ← Client with HE (attack fails)
│         client_MITM_raw.ipynb   ← Client without HE (attack succeeds)
│
├── evaluation/                   # Global model evaluation
│     MLP_depression_model_evaluation.ipynb
│     MLP_depression_model_evaluation_original.ipynb
│   └── randomforest/
│         randomforest_depression2_model.ipynb
│         randomforest_depression3_model.ipynb
│
└── docs/
      Final Review PPT.pdf
```


## How to Run — Step by Step

### Prerequisites

```bash
pip install torch opacus tenseal flask scikit-learn imbalanced-learn pandas numpy matplotlib seaborn requests
```

You also need SSL certificates for the Flask server. Generate them once:

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

Place `cert.pem` and `key.pem` inside the `server/` folder.


### Step 1 — Preprocess and Anonymize Data

Run these notebooks **in order**, once:

```
preprocessing/Data_cleaning.ipynb
preprocessing/Depression1_Anonymization.ipynb
preprocessing/Depression2_Anonymization.ipynb
preprocessing/Depression3_Anonymization.ipynb
```

Each anonymization notebook applies the following pipeline to its hospital split:
- Remove direct identifiers (country, email, full_name)
- Generalize age into categories (Child / Teen / Adult / Senior)
- Tokenize quasi-identifiers using MD5 hash (hashlib)
- Derive `Condition` label from DASS depression subscale score
- Apply **k-Anonymity** (k=3) on quasi-identifiers: gender, education, urban, age, race, religion
- Apply **l-Diversity** (l=2) on sensitive attribute: orientation

Output: `data/anonymized/Final_Depression1_anonymised.csv` (and 2, 3)


### Step 2 — Start the Global Server

Open `server/Global_Server.ipynb` in Jupyter and **run all cells**.

The server will start a Flask HTTPS app on `https://127.0.0.1:5055`

```
[SERVER] Listening securely on https://127.0.0.1:5055 ...
```

**Keep this running.** It waits to receive encrypted gradient chunks from clients via HTTPS POST. For each chunk received, it:
- Deserializes the payload (pickle)
- Validates the CKKS ciphertext (rejects tampered or malformed data)
- Saves it as `received_chunks_bin/{client_id}/chunk_{chunk_id}.bin`


### Step 3 — Run All 3 Hospital Clients Simultaneously

Open **three separate Jupyter Notebook instances** and run one per client:

```
clients/main_framework/MLP_depression1_model.ipynb  →  hospital_1
clients/main_framework/MLP_depression2_model.ipynb  →  hospital_2
clients/main_framework/MLP_depression3_model.ipynb  →  hospital_3
```

Each client independently does the following:

**Local Training (DP-aware):**
1. Loads its anonymized dataset
2. Label-encodes features, applies SMOTE for class balancing
3. Defines MLP model: `Input → 128 → ReLU → 64 → ReLU → 5 classes`
4. Initializes Opacus PrivacyEngine (`noise_multiplier=1.0`, `max_grad_norm=1.0`)
5. Trains for up to 50 epochs with early stopping (patience=25)
6. Reports validation accuracy + DP epsilon (ε ≈ 1.86, δ=1e-5)

**Gradient Encryption + Transmission:**
7. Flattens all model gradients into a single 1D vector
8. Chunks the vector (max 8000 elements per chunk — CKKS limit)
9. Encrypts each chunk using CKKS (TenSEAL, poly_modulus_degree=8192, scale=2^40)
10. Serializes each chunk with Pickle and sends via HTTPS POST to `https://127.0.0.1:5055`

You should see in the server terminal:
```
[SERVER] Received chunk 0 from hospital_1
[SERVER] Received chunk 1 from hospital_1
[SERVER] Received chunk 0 from hospital_2
...
```


### Step 4 — Aggregate Encrypted Gradients

Once all 3 clients have sent their chunks, run:

```
aggregation/Aggregate.ipynb
```

The aggregator:
1. Loads `context.ser` (public CKKS context)
2. Reads all `.bin` chunk files from `received_chunks_bin/`
3. Groups chunks by index across all clients
4. Homomorphically **adds** all CKKS vectors per chunk index
5. Divides the result by 3 (encrypted average — FedAvg)
6. Saves aggregated chunks to `aggregated_chunks_bin/`
7. Combines all into `aggregated_gradient_global_encrypted.pkl`
8. Cleans up `received_chunks_bin/`

The server **never decrypts** at any point — all operations happen on ciphertexts.

### Step 5 — Clients Receive and Update

The final cells in each client notebook:
1. Download `aggregated_gradient_global_encrypted.pkl`
2. Decrypt using their private CKKS context key
3. Reconstruct the full gradient vector
4. Clip gradient norm if > 1e2 (numerical stability)
5. Apply the global gradient to update local model weights
6. Evaluate updated model on validation set

**Repeat Steps 3–5** for the next FL round. The paper ran 10–12 rounds until convergence.

## System Architecture

```
Raw Data (DASS CSV)
       │
       ▼
[Preprocessing]
  └─ Remove identifiers
  └─ Generalize age
  └─ Tokenize QIs (hashlib MD5)
  └─ k-Anonymity (k=3)
  └─ l-Diversity  (l=2)
       │
       ▼
[Local Training — each hospital independently]
  └─ MLP: Input → 128 → ReLU → 64 → ReLU → 5 classes
  └─ Opacus DP-SGD: noise_multiplier=1.0, max_grad_norm=1.0
  └─ ε ≈ 1.86, δ = 1e-5
       │
       ▼
[Gradient Encryption]
  └─ Flatten gradients → 1D vector
  └─ Chunk (≤8000 per vector)
  └─ CKKS encrypt (TenSEAL, poly_modulus=8192)
       │
       ▼ HTTPS POST (SSL/TLS)
[Flask Server — https://127.0.0.1:5055]
  └─ Validates CKKS ciphertext (rejects tampered chunks)
  └─ Stores per-client chunk files
       │
       ▼
[Aggregation — Aggregate.ipynb]
  └─ Homomorphic addition across clients
  └─ Encrypted average (÷ num_clients)
  └─ Server NEVER decrypts
       │
       ▼ Broadcast aggregated ciphertext
[Clients — Decrypt + Update]
  └─ Private key stays on client only
  └─ Reshape gradient → update model weights
  └─ Ready for next FL round
```


## Running Attack Simulations

### Byzantine Attack

Replaces Client 1 with a malicious version that injects corrupted gradients.

```
1. Start server/Global_Server.ipynb
2. Run attacks/byzantine/Byzantine_Client1.ipynb  (IS_BYZANTINE=True, strategy="scale" ×5000)
3. Run clients/main_framework/MLP_depression2_model.ipynb  (honest)
4. Run clients/main_framework/MLP_depression3_model.ipynb  (honest)
5. Run aggregation/Aggregate.ipynb
```

**Results:**

| Setup | Validation Accuracy |
|---|---|
| Without gradient clipping | ~33–34% (model collapses) |
| With gradient clipping (our DP framework) | ~81–82% (stable) |

Gradient clipping (part of Opacus DP) neutralizes the attack by capping gradient norms before encryption.


### Man-in-the-Middle (MITM) Attack

A proxy server intercepts gradient traffic between a client and the real server.

```
1. Start server/Global_Server.ipynb  (real server, port 5055)
2. Start attacks/mitm/MITM_proxy_server.ipynb  (proxy, port 9090)

To test WITH HE (attack fails):
3. Run attacks/mitm/client_MITM.ipynb  (client sends to proxy port 9090)

To test WITHOUT HE (attack succeeds):
3. Run attacks/mitm/client_MITM_raw.ipynb
```

**Results:**

| Setup | What happens |
|---|---|
| With HE enabled | MITM sees only binary ciphertext. Reports: *"Could not tamper — data is encrypted"*. Attack fails. |
| Without HE | MITM intercepts plaintext gradients, scales them ×100, injects noise. Other clients drop to 10–18% accuracy. Client 1 remains at ~79%. |


## Key Results Summary

### Accuracy Across Framework Variants (Client 1, after 10–12 FL rounds)

| Framework Variant | Initial Accuracy | Final Accuracy |
|---|---|---|
| Base Model (Centralised) | — | 82.07% |
| Base Model (Decentralised, no privacy) | — | 86.78% |
| FL + Anonymization only (BM+A) | — | 87.47% |
| FL + Anonymization + DP (BM+A+DP) | — | 79.73% |
| FL + Anonymization + DP + HE (main) | 76.35% | 77.87–82.26% |
| FL + Anonymization + HE (no DP) | — | 80–89% |

### ARX Risk Analysis (anonymized dataset)

| Risk Metric | Value |
|---|---|
| Average prosecutor risk | 2.9681% |
| Highest prosecutor risk | 20% |
| Records affected by highest risk | 1.19968% |
| Sample uniques | 0% |
| Population uniques | 0% |

### Homogeneity Attack

| Setup | Groups Vulnerable | Proportion Leaking |
|---|---|---|
| k-Anonymity only | 30 / 364 | 8.24% |
| k-Anonymity + l-Diversity | 0 / 334 | 0.00% |

### Privacy Budget

`ε = 1.86, δ = 1e-5` (noise_multiplier=1.0, max_grad_norm=1.0, Opacus RDP accountant)


## Limitations

- **Simulated environment:** All 3 clients run on a single machine. True cross-hospital distributed deployment is future work.
- **Shared CKKS context:** The current prototype uses one shared public context. Per-client key management (threshold HE) is a planned improvement.
- **IID data split:** Dataset is split uniformly across 3 clients. Non-IID distributions (which reflect real hospital demographics) are not tested.
- **3-client prototype:** Performance with more clients is not benchmarked.

---

## Tech Stack

| Component | Library / Tool |
|---|---|
| Federated Learning | Custom (PyTorch + Flask) |
| Differential Privacy | Opacus |
| Homomorphic Encryption | TenSEAL (CKKS scheme) |
| Anonymization | Pandas + hashlib |
| Model Architecture | PyTorch MLP (3-layer) |
| Class Balancing | imbalanced-learn (SMOTE) |
| Communication | Flask + HTTPS/SSL (self-signed cert) |
| Risk Analysis | ARX (external tool) |
| Visualization | Matplotlib, Seaborn |


## Dataset

**DASS — Depression, Anxiety and Stress Scales**  
Source: [OpenPsychometrics.org](https://openpsychometrics.org/) (open-access psychological research data)  
Format: CSV — Likert scale responses (1–4) to 42 questions  
Split: Divided into 3 equal parts to simulate 3 hospital clients  
Target: 5-class depression severity derived from DASS subscale (Q3A, Q5A, Q10A, Q13A, Q16A, Q17A, Q21A, Q24A, Q26A, Q31A, Q34A, Q37A, Q38A, Q42A)

> The raw dataset is **not tracked** in this repository. Download from OpenPsychometrics and place as `data/raw/depression.csv` before running preprocessing.


## Authors

**Diya D Bhat** (PES2UG23CS183)  
**Disha R** (PES2UG23CS179)   
**Supervisor:** Prof. Shruthi L, Dept. of CSE, PES University  
**Center:** CCNCS — Center for Computer Networks and Cyber Security, PES University, Electronic City Campus
