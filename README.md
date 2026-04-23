# TileMind

TileMind is a tile size optimization tool based on **PPCG**, designed to automatically determine optimal tile sizes for polyhedral benchmarks (PolyBench). It provides both sequential and OpenMP parallel benchmarking workflows.

---

## Prerequisites

Before using TileMind, make sure **PPCG** is installed and properly configured on your system, as all benchmarking and tile size solving relies on it.

> All testing and tile size solving are based on PPCG. Please ensure it is available in your environment before proceeding.

---

## Directory Structure

Each benchmark directory (e.g., `datamining/correlation/`) contains the following key files:

```
<benchmark>/
├── benchmark_ilp_auto.py            # Tile size solver (sequential)
├── benchmark_ilp_auto_openmp.py     # Tile size solver (OpenMP parallel)
├── benchmark_preprocess.py          # Config file generator (sequential)
├── benchmark_preprocess_openmp.py   # Config file generator (OpenMP parallel)
├── <benchmark>_ilp_params_seq.py    # Config file for sequential (generated)
└── <benchmark>_ilp_params_openmp.py # Config file for OpenMP (generated)
```

---

## Workflow

TileMind supports two workflows depending on whether a configuration file already exists.

### ✅ Case 1: Config File Already Exists

If `<benchmark>_ilp_params_openmp.py` / `<benchmark>_ilp_params_seq.py` is already present, you can directly run the solver:

```bash
# For OpenMP parallel version
python benchmark_ilp_auto_openmp.py

# For sequential version
python benchmark_ilp_auto.py
```

### 🔧 Case 2: No Config File (First-time Setup)

If the config file does not exist locally, you must first run the preprocessing step to generate it, then proceed to solve for tile sizes.

**Step 1: Generate the config file**

```bash
# For OpenMP parallel version
python benchmark_preprocess_openmp.py

# For sequential version
python benchmark_preprocess.py
```

**Step 2: Run the tile size solver**

```bash
# For OpenMP parallel version
python benchmark_ilp_auto_openmp.py

# For sequential version
python benchmark_ilp_auto.py
```

---

## Quick Reference

| Scenario | Command |
|---|---|
| Config exists, solve tile size (OpenMP) | `python benchmark_ilp_auto_openmp.py` |
| Config exists, solve tile size (sequential) | `python benchmark_ilp_auto.py` |
| No config, generate first (OpenMP) | `python benchmark_preprocess_openmp.py` |
| No config, generate first (sequential) | `python benchmark_preprocess.py` |

---

## Notes

- All benchmarks are based on **PolyBench/C 4.2.1**.
- PPCG must be configured before running any script.
- The `_ilp_params_*.py` config files are generated locally and do not need to be committed to the repository.