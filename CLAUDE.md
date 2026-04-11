# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS 2590 Homework 4 — two-part NLP assignment:
- **Part 1**: BPE tokenizer + BERT text classification on IMDb
- **Part 2**: Fine-tuning T5-small for text-to-SQL on a flight database (ATIS-style)

## Directory Layout

- `release/part-{1,2}/` — starter code (read-only reference)
- `hw4_original/part-2/` — main working Part 2 implementation (training, inference, evaluation)
- `part1/src/bpe.py` — BPE tokenizer implementation
- `cs2590_hw4/` — Gradescope submission bundle (output files only)
- `hw4_report_template/` — LaTeX report
- `hpc_logs/` — HPC experiment logs

## Build & Run

### Environment
```bash
conda create -n 2590-hw4 python=3.12.11
conda activate 2590-hw4
pip install -r requirements.txt
```

### Part 2 Training (run from `hw4_original/part-2/`)
```bash
python train_t5.py --finetune --learning_rate 1e-5 --scheduler_type linear \
  --max_n_epochs 20 --patience_epochs 6 --experiment_name v11_lr1e5_linear
```

Key flags: `--finetune`, `--learning_rate`, `--scheduler_type {cosine,linear,none}`, `--num_warmup_epochs`, `--max_n_epochs`, `--patience_epochs`, `--batch_size`, `--use_wandb`

### Part 2 Evaluation (standalone)
```bash
python evaluate.py -ps results/predicted.sql -pr records/predicted.pkl \
  -ds data/dev.sql -dr records/dev_gt_records.pkl
```

### Batch Experiments
```bash
bash run_overnight.sh   # runs 6 hyperparameter configs, logs to logs/
```

## Part 2 Architecture

### Data Flow
`data/{train,dev,test}.{nl,sql}` → `load_data.py` (T5Dataset with prompted input) → `train_t5.py` (train/eval/test) → `results/*.sql` + `records/*.pkl`

### Key Modules
- **train_t5.py**: Training loop, `eval_epoch()` (beam search + SQL reranking + retrieval fallback), `test_inference()`
- **load_data.py**: T5Dataset tokenization (encoder max 256 tokens), collate with dynamic padding
- **t5_utils.py**: Model init (T5-small), AdamW + scheduler, checkpoint save/load (best/last)
- **utils.py**: `compute_metrics()` (SQL EM, Record EM, Record F1), `compute_records()` (threaded SQLite execution), `save_queries_and_records()`

### SQL Generation Pipeline
1. Beam search (num_beams=10, num_return_sequences=6)
2. `clean_generated_sql()`: strip prompt artifacts, deduplicate tokens
3. `choose_best_sql()`: score candidates by SQL structure validity, question-token overlap, intent-operator alignment
4. Retrieval fallback: IDF-weighted token matching against train (+ dev for test) corpus

### Checkpoints & Outputs
```
checkpoints/ft_experiments/{name}/best/   # highest dev Record F1
checkpoints/ft_experiments/{name}/last/   # final epoch
results/t5_ft_{name}_{dev,test}.sql
records/t5_ft_{name}_{dev,test}.pkl
```

## Evaluation Metrics
- **SQL EM**: exact string match (very strict — case/space sensitive)
- **Record EM**: set equality of returned DB rows
- **Record F1**: precision/recall F1 over DB result sets
- **Error Rate**: % of generated SQL causing execution errors

## Submission (Gradescope)
Place in `cs2590_hw4/`:
- `t5_ft_experiment_test.sql` and `t5_ft_experiment_test.pkl` (must have exactly as many lines as `data/test.nl`)
- `out_original.txt`, `out_transformed.txt`, `out_augmented_original.txt`, `out_augmented_transformed.txt` (Part 1)
- `hw4-report.pdf`

## Critical Notes
- The `main()` in train_t5.py loads `best=True` checkpoint for final dev eval and test inference
- Ground truth records path is `records/dev_gt_records.pkl` (hw4_original) vs `records/ground_truth_dev.pkl` (release) — check which exists
- Database: `data/flight_database.db` (SQLite)
- SQL output must have balanced parentheses to avoid execution errors
