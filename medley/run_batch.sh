#!/bin/bash

# run_batch.sh
# Script to run all benchmarks across blas, kernels, and solvers

ROOT_DIR=$(pwd)

# Check if run_all.sh exists in current directory
if [ -f "run_all.sh" ]; then
    echo "Using local run_all.sh for datamining benchmarks..."
    chmod +x run_all.sh run_test.sh run_polly.sh
else
    echo "Error: run_all.sh not found in current directory. Cannot proceed."
    exit 1
fi

# Categories to process
CATEGORIES=(".")

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
            ./deriche|./floyd-warshall)
                # echo "Found valid medley benchmark: $full_path"
                ;;
            ./nussinov)
                echo "Skipping nussinov as requested."
                continue
                ;;
            *)
                echo "Skipping unknown directory/file: $full_path"
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
