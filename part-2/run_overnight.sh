#!/usr/bin/env bash
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs logs/samples

run_one () {
  name="$1"
  lr="$2"
  sched="$3"
  warm="$4"
  epochs="$5"
  patience="$6"

  echo "===== START ${name} ====="
  echo "$(date) START ${name}" | tee -a logs/summary.txt

  python train_t5.py \
    --finetune \
    --learning_rate "${lr}" \
    --scheduler_type "${sched}" \
    --num_warmup_epochs "${warm}" \
    --max_n_epochs "${epochs}" \
    --patience_epochs "${patience}" \
    --experiment_name "${name}" \
    2>&1 | tee "logs/train_${name}.log"

  code=$?
  if [ ${code} -ne 0 ]; then
    echo "$(date) FAIL ${name} train_exit=${code}" | tee -a logs/summary.txt
    return
  fi

  python evaluate.py \
    --predicted_sql "results/t5_ft_${name}_dev.sql" \
    --predicted_records "records/t5_ft_${name}_dev.pkl" \
    --development_sql data/dev.sql \
    --development_records records/ground_truth_dev.pkl \
    2>&1 | tee "logs/eval_${name}.log"

  grep -E "Epoch [0-9]+: Dev loss|Dev set results|generated outputs led to SQL errors" "logs/train_${name}.log" > "logs/metrics_${name}.txt" || true

  EXP_NAME="${name}" python - << 'PY'
import os
import random

exp = os.environ["EXP_NAME"]

def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]

nl = read_lines("data/dev.nl")
gold = read_lines("data/dev.sql")
pred_path = f"results/t5_ft_{exp}_dev.sql"
if not os.path.exists(pred_path):
    raise SystemExit(f"Missing {pred_path}")
pred = read_lines(pred_path)

n = min(len(nl), len(gold), len(pred))

with open(f"logs/samples/{exp}_first20.txt", "w", encoding="utf-8") as f:
    for i in range(min(20, n)):
        f.write(f"[{i}] NL: {nl[i]}\n")
        f.write(f"[{i}] GOLD: {gold[i]}\n")
        f.write(f"[{i}] PRED: {pred[i]}\n\n")

random_count = 20 if n >= 20 else n
idx = sorted(random.Random(2590).sample(range(n), random_count))
with open(f"logs/samples/{exp}_random20.txt", "w", encoding="utf-8") as f:
    for i in idx:
        f.write(f"[{i}] NL: {nl[i]}\n")
        f.write(f"[{i}] GOLD: {gold[i]}\n")
        f.write(f"[{i}] PRED: {pred[i]}\n\n")

bad_idx = []
for i, s in enumerate(pred[:n]):
    t = s.strip().upper()
    if not (t.startswith("SELECT") or t.startswith("WITH")):
        bad_idx.append(i)
bad_idx = bad_idx[:20]

with open(f"logs/samples/{exp}_bad20.txt", "w", encoding="utf-8") as f:
    for i in bad_idx:
        f.write(f"[{i}] NL: {nl[i]}\n")
        f.write(f"[{i}] GOLD: {gold[i]}\n")
        f.write(f"[{i}] PRED: {pred[i]}\n\n")
PY

  echo "$(date) DONE ${name}" | tee -a logs/summary.txt
  echo "===== END ${name} ====="
}

run_one ft_lr1e5_linear 1e-5 linear 1 20 6
run_one ft_lr2e5_linear 2e-5 linear 1 20 6
run_one ft_lr3e5_linear 3e-5 linear 1 20 6
run_one ft_lr5e5_linear 5e-5 linear 1 20 6
run_one ft_lr2e5_cosine 2e-5 cosine 1 20 6
run_one ft_lr2e5_none 2e-5 none 0 20 6

echo "All experiments finished at $(date)" | tee -a logs/summary.txt
