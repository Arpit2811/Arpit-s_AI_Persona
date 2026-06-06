# Minhash-LSH-Jaccard-Based-deduplication-on-parquet-datasets-pipeline

High-performance near-duplicate detection for large Parquet datasets using MinHash signatures and Locality-Sensitive Hashing (LSH). Designed for 50M+ row datasets on multi-core HPC clusters.

---

## How It Works

The pipeline runs in 5 sequential phases:

```
Phase 1 → MinHash      Generate signatures for every row (parallel)
Phase 2 → LSH          Find candidate near-duplicate pairs via LSH index
Phase 3 → Jaccard      Verify candidate pairs with exact Jaccard similarity (parallel)
Phase 4 → Keep Set     Mark duplicates — keep first occurrence, drop the rest
Phase 5 → Write        Stream clean rows to output Parquet
```

**Text input:** By default, `Question` and `Answer` columns are concatenated with `[SEP]` before hashing. Use `--question-only` to hash only the `Question` column.

**Duplicate policy:** For each confirmed near-duplicate pair `(a, b)` where `a < b`, row `b` is dropped. The first occurrence of each near-duplicate group is always kept.

---

## Requirements

```bash
pip install pyarrow datasketch numpy tqdm
```

---

## Usage

### Basic

```bash
python dedup.py --input /data/raw.parquet --output /data/deduped/
```

### Directory (processes all `.parquet` files recursively)

```bash
python dedup.py --input /data/raw/ --output /data/deduped/
```

### Common options

```bash
python dedup.py \
  --input   /data/raw/ \
  --output  /data/deduped/ \
  --workers 64 \
  --threshold 0.7 \
  --num-perm 128 \
  --chunk 500000 \
  --skip-existing
```

---

## Arguments

| Argument | Default | Description |
|---|---|---|
| `--input` | *(required)* | Input `.parquet` file or directory |
| `--output` | *(required)* | Output file or directory |
| `--workers` | `100` | Number of parallel worker processes |
| `--threshold` | `0.7` | Jaccard similarity threshold (0–1). Lower = more aggressive dedup |
| `--num-perm` | `128` | Number of MinHash permutations. Higher = more accurate, more RAM |
| `--ngram` | `3` | Character n-gram size for shingling |
| `--chunk` | `500000` | Rows per batch for reading/writing |
| `--no-verify` | `False` | Skip Jaccard verification — faster but less precise |
| `--question-only` | `False` | Hash only `Question` column instead of `Question + Answer` |
| `--skip-existing` | `False` | Skip output files that already exist |
| `--max-ram-per-worker` | `4.0` | GB RAM budget per Jaccard worker |
| `--tasks-per-worker` | `4` | Target Jaccard tasks per worker for load balancing |
| `--min-task-size` | `100000` | Minimum pairs per Jaccard task |
| `--max-task-size` | `10000000` | Maximum pairs per Jaccard task |

---

## Threshold Guide

| `--threshold` | Meaning | Use when |
|---|---|---|
| `0.95+` | Near-exact duplicates only | Text with minor edits (whitespace, punctuation) |
| `0.8–0.95` | High similarity | Paraphrased or lightly reworded content |
| `0.7` *(default)* | Moderate similarity | Standard deduplication |
| `0.5–0.7` | Loose similarity | Aggressive dedup, topic-level clustering |

---

## Architecture Details

### Phase 1 — MinHash (parallel)

Each row is converted to a set of character n-gram shingles, then hashed into a `num_perm`-dimensional MinHash signature. Work is split across `--workers` processes using `multiprocessing.Pool`.

Signatures are written to a **memory-mapped NumPy file** (`signatures.npy`) rather than held in RAM. This allows datasets larger than available RAM to be processed.

### Phase 2 — LSH

All signatures are streamed through a `MinHashLSH` index. For each row, the index is queried for near-neighbours before the row itself is inserted. This yields a set of **candidate pairs** — rows that are likely near-duplicates but not yet confirmed.

LSH is approximate by design — it trades a small number of false negatives for O(n) query time instead of O(n²).

### Phase 3 — Jaccard Verification (parallel)

Candidate pairs are verified by computing the exact Jaccard similarity from their MinHash signatures:

```
Jaccard ≈ (number of equal hash values) / num_perm
```

Pairs below `--threshold` are rejected. This step reads signatures from the memory-mapped file directly in each worker — **no signature data is pickled or sent over IPC**.

Task size is computed dynamically based on `--max-ram-per-worker` and `--tasks-per-worker` to avoid OOM errors.

### Phase 4 — Keep Set

For all confirmed pairs `(a, b)` with `a < b`, row `b` is added to a `duplicates` set. The keep set is `all_rows - duplicates`. This is O(n_pairs) with no graph traversal.

### Phase 5 — Write

The original file is re-read in chunks. Each chunk is filtered to keep only rows in the keep set, then written to the output Parquet file with Snappy compression.

---

## Memory Usage

| Component | Size |
|---|---|
| Signatures memmap | `total_rows × num_perm × 8 bytes` |
| Candidate pairs | `n_pairs × 8 bytes` (int32 × 2) |
| Jaccard RAM/worker | `task_size × num_perm × 16 bytes` |

**Example:** 10M rows, `num_perm=128` → signatures memmap ≈ **10 GB**. Use a fast local disk or tmpfs for the temp directory if possible.

---

## Output

- Output Parquet files are named `{stem}_deduped.parquet`
- Schema is preserved exactly from the input
- Compressed with Snappy
- Row order is preserved (first occurrence of each group is kept)

---

## Example Output Log

```
08:14:01 │ INFO │ Processing : /data/raw/qa_pairs.parquet
08:14:01 │ INFO │ Rows: 1,226,103  Workers: 64  Perm: 128  Threshold: 0.7
08:14:01 │ INFO │ Phase 1 – MinHash generation …
08:14:45 │ INFO │ Phase 1 done in 44.2s
08:14:45 │ INFO │ Phase 2 – LSH streaming insert + query …
08:16:01 │ INFO │ Phase 2 done — 48,231 candidate pairs in 76.3s
08:16:01 │ INFO │ Phase 3 – Jaccard verification (48,231 pairs)
08:16:04 │ INFO │ Phase 3 done — 31,847/48,231 confirmed in 3.1s
08:16:04 │ INFO │ Phase 4 – Building keep set from confirmed pairs …
08:16:04 │ INFO │   Duplicates : 28,412 (2.32%)  Unique : 1,197,691
08:16:04 │ INFO │ Phase 5 – Writing …
08:16:21 │ INFO │ DONE  qa_pairs.parquet  │  140.3s (2.3 min)
08:16:21 │ INFO │   Input : 1,226,103  →  Output : 1,197,691  (removed 28,412, 2.32%)
```

---

## Tips

**Speed up Phase 1** — increase `--workers` and `--chunk`. MinHash is CPU-bound and scales linearly with cores.

**Speed up Phase 2** — LSH is single-threaded and the bottleneck for very large datasets (10M+ rows). Lower `--num-perm` reduces LSH insert/query time at the cost of accuracy.

**Reduce memory** — lower `--num-perm` (try `64`) or `--max-ram-per-worker`.

**Stricter dedup** — raise `--threshold` toward `0.9`. Looser dedup — lower toward `0.5`.

**Large directories** — use `--skip-existing` to resume interrupted runs without reprocessing completed files.