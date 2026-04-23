#!/bin/bash

# run_batch.sh
# Script to run all benchmarks across blas, kernels, and solvers

ROOT_DIR=$(pwd)

# Ensure the master run_all.sh is propagated to other directories to ensure consistent logic
# We assume blas/run_all.sh is the up-to-date version with proper argument handling
if [ -f "blas/run_all.sh" ]; then
    echo "Syncing run_all.sh from blas/ to kernels/ and solvers/..."
    cp blas/run_all.sh kernels/
    cp blas/run_all.sh solvers/
    chmod +x kernels/run_all.sh solvers/run_all.sh
else
    echo "Error: blas/run_all.sh not found. Cannot proceed."
    exit 1
fi

# Categories to process
CATEGORIES=("blas" "kernels" "solvers" "../datamining")

for cat in "${CATEGORIES[@]}"; do
    if [ -d "$cat" ]; then
        echo "========================================"
        echo "Processing Category: $cat"
        echo "========================================"
    elif [ -d "../$cat" ]; then
        # Handle relative path ../datamining when we are in linear-algebra
         echo "========================================"
         echo "Processing Category: $cat"
         echo "========================================"
    else
        echo "Category directory $cat not found, skipping..."
        continue
    fi
    
    cd "$cat"
    
    # Iterate through each subdirectory (kernel)
    for k_dir in */; do
        k_name=$(basename "$k_dir")
        full_path="$cat/$k_name"
        
        # Check skip list
        case "$full_path" in
            blas/*|kernels/*|solvers/durbin)
                echo "Skipping excluded benchmark: $full_path"
                continue
                ;;
        esac
        
        if [ -d "$k_name" ]; then
            echo "Entering $k_name..."
            cd "$k_name"
            
            c_file="${k_name}.c"
            h_file="${k_name}.h"
            
            # Validation
            if [ ! -f "$c_file" ]; then
                echo "Warning: Source file $c_file not found in $k_name. Skipping."
                cd ..
                continue
            fi
            
            # Modify Header to ensure EXTRALARGE_DATASET
            if [ -f "$h_file" ]; then
                if ! grep -q "#define EXTRALARGE_DATASET" "$h_file"; then
                    # Prepend definition to the file
                    sed -i '1s/^/#define EXTRALARGE_DATASET\n/' "$h_file"
                    echo "  Modified $h_file: Added EXTRALARGE_DATASET"
                else
                    echo "  $h_file already has EXTRALARGE_DATASET defined."
                fi
            fi
            
            # 1. Run full benchmarks with OMP_NUM_THREADS=8
            echo "  Running benchmarks for $c_file (Threads=8)..."
            export OMP_NUM_THREADS=8
            ../run_all.sh "$c_file" -seq -srun -par -prun -polly > data8.txt 2>&1
            
            # 2. Run parallel benchmarks with OMP_NUM_THREADS=16
            echo "  Running benchmarks for $c_file (Threads=16)..."
            export OMP_NUM_THREADS=16
            ../run_all.sh "$c_file" -par -prun -polly > data16.txt 2>&1
            
            echo "  Finished $c_file"
            
            cd ..
        fi
    done
    
    cd "$ROOT_DIR"
done

echo "Batch processing completed."
