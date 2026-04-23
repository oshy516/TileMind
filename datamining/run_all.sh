#!/bin/bash

# Script to generate kernels and run comprehensive benchmarks
# Usage: ./run_all.sh <kernel.c>
# Example: ../run_all.sh symm.c

if [ $# -lt 1 ]; then
    echo "Usage: $0 <kernel.c> [OPTIONS]"
    echo "Options:"
    echo "  -seq      Generate sequential code variants (PPCG Tiled, PolyCC Tiled)"
    echo "  -par      Generate parallel code variants (OpenMP)"
    echo "  -srun     Run performance tests for sequential variants"
    echo "  -prun     Run performance tests for parallel variants"
    echo "  -polly    Run Polly benchmarks"
    echo ""
    echo "  If no options provided, all steps are executed."
    exit 1
fi

SOURCE_FILE=$1
BASENAME=$(basename "$SOURCE_FILE" .c)
shift

# Default: if no flags provided, set all to true
if [ $# -eq 0 ]; then
    DO_SEQ_GEN=1
    DO_PAR_GEN=1
    DO_SEQ_RUN=1
    DO_PAR_RUN=1
    DO_POLLY=1
else
    DO_SEQ_GEN=0
    DO_PAR_GEN=0
    DO_SEQ_RUN=0
    DO_PAR_RUN=0
    DO_POLLY=0
    
    while [ $# -gt 0 ]; do
        case "$1" in
            -seq) DO_SEQ_GEN=1 ;;
            -par) DO_PAR_GEN=1 ;;
            -srun) DO_SEQ_RUN=1 ;;
            -prun) DO_PAR_RUN=1 ;;
            -polly) DO_POLLY=1 ;;
            *) echo "Unknown option: $1"; exit 1 ;;
        esac
        shift
    done
fi

# Locate the companion scripts in the same directory as this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RUN_TEST_SCRIPT="${SCRIPT_DIR}/run_test.sh"
RUN_POLLY_SCRIPT="${SCRIPT_DIR}/run_polly.sh"

# Check if companion scripts exist
if [ ! -f "$RUN_TEST_SCRIPT" ] || [ ! -f "$RUN_POLLY_SCRIPT" ]; then
    echo "Error: run_test.sh or run_polly.sh not found in ${SCRIPT_DIR}"
    exit 1
fi

# Define paths to tools
PPCG_CMD="/home/shihany/workspace/lnlamp/ppcg"
POLYCC_CMD="/home/shihany/workspace/pluto/polycc"

# Check if tools exist
if [ ! -x "$PPCG_CMD" ]; then
    echo "Warning: ppcg not found at $PPCG_CMD. Trying 'ppcg' from PATH."
    PPCG_CMD="ppcg"
fi
if [ ! -x "$POLYCC_CMD" ]; then
    echo "Warning: polycc not found at $POLYCC_CMD. Trying 'polycc' from PATH."
    POLYCC_CMD="polycc"
fi

INCLUDE_FLAGS="-I../../utilities -I."

if [ "$DO_SEQ_GEN" -eq 1 ]; then
    echo "==================================================================="
    echo "Generating Sequential Variants for $BASENAME..."
    echo "==================================================================="

    # 1. Generate PPCG Tiled
    echo "Generating ${BASENAME}_ppcg_tile_ex.c (PPCG Tiled)..."
    $PPCG_CMD --target c --no-automatic-mixed-precision --tile $INCLUDE_FLAGS "$SOURCE_FILE" -o "${BASENAME}_ppcg_tile_ex.c"

    # 2. Generate PolyCC Tiled (TSS)
    echo "Generating ${BASENAME}_tss_tile_ex.c (PolyCC Tiled)..."
    $POLYCC_CMD "$SOURCE_FILE" --tile --determine-tile --noparallel -o "${BASENAME}_tss_tile_ex.c"
fi

if [ "$DO_PAR_GEN" -eq 1 ]; then
    echo "==================================================================="
    echo "Generating Parallel Variants for $BASENAME..."
    echo "==================================================================="

    # 3. Generate PPCG OpenMP
    echo "Generating ${BASENAME}_openmp_ex.c (PPCG OpenMP)..."
    $PPCG_CMD --target c --no-automatic-mixed-precision --openmp $INCLUDE_FLAGS "$SOURCE_FILE" -o "${BASENAME}_openmp_ex.c"

    # 4. Generate PPCG Tiled + OpenMP
    # Note: User request mentioned symm.c, but we default to SOURCE_FILE if specific original file not found
    INPUT_FOR_PPCG_OMP_TILE="$SOURCE_FILE"
    if [ -f "${BASENAME}.c" ]; then
        INPUT_FOR_PPCG_OMP_TILE="${BASENAME}.c"
    fi
    echo "Generating ${BASENAME}_ppcg_openmp_tile_ex.c (PPCG Tiled + OpenMP)..."
    $PPCG_CMD --target c --no-automatic-mixed-precision --tile --openmp $INCLUDE_FLAGS "$INPUT_FOR_PPCG_OMP_TILE" -o "${BASENAME}_ppcg_openmp_tile_ex.c"

    # 5. Generate PolyCC Tiled + OpenMP
    echo "Generating ${BASENAME}_tss_tile_openmp_ex.c (PolyCC Tiled + OpenMP)..."
    $POLYCC_CMD "$SOURCE_FILE" --tile --determine-tile -o "${BASENAME}_tss_tile_openmp_ex.c"
fi

echo ""
echo "==================================================================="
echo "Running Performance Tests..."
echo "==================================================================="

if [ "$DO_SEQ_RUN" -eq 1 ]; then
    echo "--- Sequential Tests ---"
    # 1. Original
    echo "[1/3] Testing Original..."
    "$RUN_TEST_SCRIPT" "$SOURCE_FILE" -numa 0

    # 2. PPCG Tiled
    echo "[2/3] Testing PPCG Tiled..."
    if [ -f "${BASENAME}_ppcg_tile_ex.c" ]; then
        "$RUN_TEST_SCRIPT" "${BASENAME}_ppcg_tile_ex.c" -numa 0 -perf
    else
        echo "Skipping: ${BASENAME}_ppcg_tile_ex.c not found"
    fi

    # 3. PolyCC Tiled
    echo "[3/3] Testing PolyCC Tiled..."
    if [ -f "${BASENAME}_tss_tile_ex.c" ]; then
        "$RUN_TEST_SCRIPT" "${BASENAME}_tss_tile_ex.c" -numa 0 -perf
    else
        echo "Skipping: ${BASENAME}_tss_tile_ex.c not found"
    fi
fi

if [ "$DO_PAR_RUN" -eq 1 ]; then
    echo "--- Parallel Tests ---"
    # 4. PPCG OpenMP
    echo "[1/3] Testing PPCG OpenMP..."
    if [ -f "${BASENAME}_openmp_ex.c" ]; then
        "$RUN_TEST_SCRIPT" "${BASENAME}_openmp_ex.c" -openmp -numa 0
    else
        echo "Skipping: ${BASENAME}_openmp_ex.c not found"
    fi

    # 5. PPCG Tiled + OpenMP
    echo "[2/3] Testing PPCG Tiled + OpenMP..."
    if [ -f "${BASENAME}_ppcg_openmp_tile_ex.c" ]; then
        "$RUN_TEST_SCRIPT" "${BASENAME}_ppcg_openmp_tile_ex.c" -openmp -numa 0 -perf
    else
        echo "Skipping: ${BASENAME}_ppcg_openmp_tile_ex.c not found"
    fi

    # 6. PolyCC Tiled + OpenMP
    echo "[3/3] Testing PolyCC Tiled + OpenMP..."
    if [ -f "${BASENAME}_tss_tile_openmp_ex.c" ]; then
        "$RUN_TEST_SCRIPT" "${BASENAME}_tss_tile_openmp_ex.c" -numa 0 -openmp -perf
    else
        echo "Skipping: ${BASENAME}_tss_tile_openmp_ex.c not found"
    fi
fi

if [ "$DO_POLLY" -eq 1 ]; then
    echo ""
    echo "==================================================================="
    echo "Running Polly Benchmarks..."
    echo "==================================================================="

    PERF_EVENTS="cache-references,cache-misses,L1-dcache-load-misses,LLC-load-misses"

    # 1. Polly Parallel + Tile
    echo "[1/2] Polly Parallel + Tile..."
    "$RUN_POLLY_SCRIPT" "$SOURCE_FILE" -parallel -tile -events "$PERF_EVENTS"

    # 2. Polly Tile Only
    echo "[2/2] Polly Tile Only..."
    "$RUN_POLLY_SCRIPT" "$SOURCE_FILE" -tile -events "$PERF_EVENTS"
fi

echo "==================================================================="
echo "All benchmarks completed for $BASENAME"
echo "==================================================================="
