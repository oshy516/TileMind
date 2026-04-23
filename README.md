# TileMind

TileMind is a tile size optimization tool designed to automatically determine optimal tile sizes. The method itself is **compiler-agnostic** and is not bound to any specific compiler infrastructure.

> **Note on this repository:** The test code currently included in this repository is built on top of **PolyBench/C**, and uses **PPCG** as the underlying compiler for benchmarking purposes. PPCG is a dependency of the test code only, not of the TileMind method itself.

---

## Prerequisites

To run the test code in this repository (based on PolyBench/C), **PPCG** must be installed and properly configured on your system.

> PPCG is required only for the PolyBench-based test code included here. The TileMind method itself is compiler-agnostic and can be adapted to other compiler backends.

---

## Hardware Parameters Notice

> ⚠️ **The hardware parameters in the auto-generated config files are profiled specifically for Intel Xeon Platinum 8538C.** If you are running on a different platform, you must update the following fields in the config file (`<benchmark>_ilp_params_*.py`) to match your hardware.

The test platform configuration is as follows:

| Parameter | Value |
|---|---|
| CPU | Intel Xeon Platinum 8538C |
| Architecture | x86\_64 |
| Physical Cores | 56 |
| Logical Processors | 112 (Hyper-Threading, 2 threads/core) |
| Base Frequency | ~2.7 GHz |
| L1 Data Cache | 2.6 MiB (46 KiB per core × 56) |
| L2 Cache | 112 MiB (2 MiB per core × 56) |
| L3 Cache | 280 MiB (shared) |
| NUMA Nodes | 2 (Node0: CPU 0–27, 56–83 / Node1: CPU 28–55, 84–111) |

**Cache & thread parameters (per-core values used in config):**
```python
# Cache parameters
L1_size = 49152      # L1 data cache size in bytes (~48 KiB per core)
L2_size = 2097152    # L2 cache size in bytes (2 MiB per core)
cache_line = 64      # Cache line size in bytes

# Parallelization information
num_threads = 8      # Number of threads used in current tests
                     # (Physical cores: 56, logical processors: 112, but only 8 used here)
```

**Cache & operation latencies:**
```python
# Cache access latencies (nanoseconds)
T_L1 = 3.13   # L1 cache access latency
T_L2 = 7.42   # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.76
T_sub = 0.82
T_mul = 1.55
T_div = 5.19
T_sqrt = 20.00
T_trig = 40.00
T_log_exp = 35.00
T_pow = 45.00
```

**Statement costs in the objective function** (the constant coefficients, e.g., in `gemm`):
```python
# Statement costs (nanoseconds)
T_op1 = 7.42   # Statement 1 cost (block 0)
T_op2 = 16.78  # Statement 2 cost (block 0)

# Block-specific objective functions
block_0_objective = "c0_b0_blocks * c1_b0_blocks * 7.42 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c2_b0_tile * 16.78"

# Auto-generated objective function
objective_function = "(c0_b0_blocks * c1_b0_blocks * 7.42 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c2_b0_tile * 16.78)"
```

These constants represent profiled per-statement execution costs and must be updated if you retarget to a different platform.

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

> **Single config file:** If only one `<benchmark>_ilp_params.py` exists (without `_seq` / `_openmp` suffix), it indicates that the loop structure is identical between the sequential and OpenMP versions — the only difference is the number of threads. In this case, the same config file can be used to solve both cases.

---

## Workflow

TileMind supports two workflows depending on whether a configuration file already exists.

### ✅ Case 1: Config File Already Exists

If the config file is already present, directly run the solver:

```bash
# Sequential version
python3 benchmark_ilp_auto.py <benchmark>_ilp_params_seq.py

# OpenMP parallel version
python3 benchmark_ilp_auto_openmp.py <benchmark>_ilp_params_openmp.py

# If only a single shared config exists
python3 benchmark_ilp_auto.py <benchmark>_ilp_params.py
python3 benchmark_ilp_auto_openmp.py <benchmark>_ilp_params.py
```

### 🔧 Case 2: No Config File (First-time Setup)

If no config file exists, first generate it via the preprocessing script, then run the solver.

**Step 1: Generate the config file**

```bash
# Sequential version
python3 benchmark_preprocess.py <benchmark>.c

# OpenMP parallel version
python3 benchmark_preprocess_openmp.py <benchmark>.c
```

**Step 2: Run the tile size solver**

```bash
# Sequential version
python3 benchmark_ilp_auto.py <benchmark>_ilp_params_seq.py

# OpenMP parallel version
python3 benchmark_ilp_auto_openmp.py <benchmark>_ilp_params_openmp.py
```

---

## Quick Reference

| Scenario | Command |
|---|---|
| Config exists, sequential | `python3 benchmark_ilp_auto.py <benchmark>_ilp_params_seq.py` |
| Config exists, OpenMP | `python3 benchmark_ilp_auto_openmp.py <benchmark>_ilp_params_openmp.py` |
| Single shared config, sequential | `python3 benchmark_ilp_auto.py <benchmark>_ilp_params.py` |
| Single shared config, OpenMP | `python3 benchmark_ilp_auto_openmp.py <benchmark>_ilp_params.py` |
| No config, generate (sequential) | `python3 benchmark_preprocess.py <benchmark>.c` |
| No config, generate (OpenMP) | `python3 benchmark_preprocess_openmp.py <benchmark>.c` |

---

## Notes

- All benchmarks are based on **PolyBench/C 4.2.1**.
- PPCG must be configured before running any script.
- The `_ilp_params_*.py` config files are generated locally and do not need to be committed to the repository.
- Hardware parameters in config files are profiled on **Intel Xeon Platinum 8538C**. Update them if testing on a different platform.