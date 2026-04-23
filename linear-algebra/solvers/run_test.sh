#!/bin/bash

# Script to compile and run PolyBench tests with timing
# Includes warm-up phase and NUMA node binding support

# Function: Calculate average (float)
calc_average_float() {
    local sum=0
    local count=0
    for val in "$@"; do
        if [ ! -z "$val" ]; then
            sum=$(echo "$sum + $val" | bc -l)
            count=$((count + 1))
        fi
    done
    if [ $count -gt 0 ]; then
        echo "scale=6; $sum / $count" | bc -l
    else
        echo ""
    fi
}

# Function: Calculate average (integer)
calc_average_int() {
    local sum=0
    local count=0
    for val in "$@"; do
        if [ ! -z "$val" ]; then
            sum=$(echo "$sum + $val" | bc -l)
            count=$((count + 1))
        fi
    done
    if [ $count -gt 0 ]; then
        # Round to integer
        printf "%.0f" $(echo "scale=6; $sum / $count" | bc -l)
    else
        echo ""
    fi
}

# Function to compile and run a test
run_test() {
    local source_file=$1
    local use_openmp=$2
    local numa_node=$3
    local warmup_runs=${4:-2}
    local timing_runs=${5:-3}
    local use_perf=${6:-0}
    local perf_events=${7:-""}
    
    # Extract base name without extension
    local base_name=$(basename "$source_file" .c)
    
    echo "==================================================================="
    echo "Processing $source_file..."
    if [ "$use_perf" -eq 1 ]; then
        echo "Perf monitoring: ENABLED ($perf_events)"
    fi
    echo "==================================================================="
    
    # Compile command
    compile_cmd="gcc -O3 -DPOLYBENCH_TIME"
    
    # Add OpenMP flag if requested
    if [ "$use_openmp" -eq 1 ]; then
        compile_cmd="$compile_cmd -fopenmp"
        echo "Using OpenMP for compilation"
    fi
    
    # Complete the compile command
    compile_cmd="$compile_cmd $source_file ../../../utilities/polybench.c -o $base_name -I../../../utilities -I. -lm"
    
    echo "Compiling: $compile_cmd"
    eval $compile_cmd
    
    if [ $? -ne 0 ]; then
        echo "Compilation failed for $source_file"
        return 1
    fi
    
    # Prepare execution command with optional NUMA binding
    local exec_cmd=""
    if [ ! -z "$numa_node" ]; then
        exec_cmd="numactl --cpunodebind=${numa_node} --membind=${numa_node}"
        echo "Using NUMA node binding: node ${numa_node}"
    fi
    
    echo "-------------------------------------"
    echo "Performing $warmup_runs warm-up runs..."
    echo "-------------------------------------"
    
    # Warm-up phase
    for i in $(seq 1 $warmup_runs); do
        echo "  Warm-up run $i..."
        if [ ! -z "$numa_node" ]; then
            $exec_cmd ./$base_name > /dev/null 2> /dev/null
        else
            ./$base_name > /dev/null 2> /dev/null
        fi
    done
    
    echo "-------------------------------------"
    echo "Running $timing_runs times for performance measurement..."
    echo "-------------------------------------"

    if [ ! -z "$OMP_NUM_THREADS" ]; then
        echo "Environment OMP_NUM_THREADS is set to: $OMP_NUM_THREADS"
    else
        echo "Environment OMP_NUM_THREADS is NOT set (using default)."
    fi
    
    # Arrays to store timing data
    declare -a times
    # Arrays for perf stats
    declare -a cache_refs
    declare -a cache_misses
    declare -a l1_misses
    declare -a llc_misses
    declare -a cycles_arr
    declare -a instructions_arr

    local total_time=0
    local run_count=0
    local min_time=9999999
    local max_time=0
    
    for i in $(seq 1 $timing_runs); do
        # Use unique temporary file name
        local temp_output="/tmp/polytime_${BASHPID}_${i}.txt"
        local perf_output="/tmp/polyperf_${BASHPID}_${i}.txt"
        
        # Execute with or without NUMA binding
        if [ "$use_perf" -eq 1 ]; then
             # Run with sudo perf, preserving OMP_NUM_THREADS if set
             if [ ! -z "$OMP_NUM_THREADS" ]; then
                 sudo OMP_NUM_THREADS="$OMP_NUM_THREADS" perf stat -e "$perf_events" -o "$perf_output" $exec_cmd ./$base_name > "$temp_output" 2> /dev/null
             else
                 sudo perf stat -e "$perf_events" -o "$perf_output" $exec_cmd ./$base_name > "$temp_output" 2> /dev/null
             fi
             
             # Extract perf stats
             local cache_ref=$(grep -w "cache-references" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$cache_ref" ] && cache_refs+=($cache_ref)

             local cache_miss=$(grep -w "cache-misses" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$cache_miss" ] && cache_misses+=($cache_miss)

             local l1_miss=$(grep "L1-dcache-load-misses" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$l1_miss" ] && l1_misses+=($l1_miss)

             local llc_miss=$(grep "LLC-load-misses" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$llc_miss" ] && llc_misses+=($llc_miss)

             local cycles_val=$(grep -w "cycles" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$cycles_val" ] && cycles_arr+=($cycles_val)
             
             local instr_val=$(grep -w "instructions" "$perf_output" | awk '{gsub(/,/,"",$1); print $1}')
             [ ! -z "$instr_val" ] && instructions_arr+=($instr_val)
             
             sudo rm -f "$perf_output"
        else
            if [ ! -z "$numa_node" ]; then
                $exec_cmd ./$base_name > "$temp_output" 2> /dev/null
            else
                ./$base_name > "$temp_output" 2> /dev/null
            fi
        fi
        
        # Extract time - look for any floating point number
        local time_value=""
        
        # Try to extract the first valid floating point number
        time_value=$(grep -oE "[0-9]+\.[0-9]+" "$temp_output" | head -1)
        
        # If that didn't work, try to get any numeric value
        if [ -z "$time_value" ]; then
            time_value=$(grep -oE "[0-9]*\.?[0-9]+" "$temp_output" | head -1)
        fi
        
        # Check if time_value is valid
        if [[ $time_value =~ ^[0-9]*\.?[0-9]+$ ]] && [ ! -z "$time_value" ]; then
            times[$run_count]=$time_value  # Store for std dev calculation
            total_time=$(echo "$total_time + $time_value" | bc -l)
            run_count=$((run_count + 1))
            echo "  Run $i: $time_value seconds"
            
            # Update min and max times
            if (( $(echo "$time_value < $min_time" | bc -l) )); then
                min_time=$time_value
            fi
            if (( $(echo "$time_value > $max_time" | bc -l) )); then
                max_time=$time_value
            fi
        else
            echo "  Run $i: Invalid time format or no time found"
        fi
        
        # Clean up temp file
        rm -f "$temp_output"
    done
    
    echo "-------------------------------------"
    echo "Performance Summary"
    echo "-------------------------------------"
    
    if [ $run_count -gt 0 ]; then
        local avg_time=$(echo "scale=6; $total_time / $run_count" | bc -l)
        echo "Average execution time for $base_name: $avg_time seconds (from $run_count valid runs)"
        echo "Min time: $min_time seconds"
        echo "Max time: $max_time seconds"
        
        # Calculate standard deviation using stored times
        if [ $run_count -gt 1 ]; then
            local sum_squared_diff=0
            
            for ((j=0; j<run_count; j++)); do
                local time_val=${times[$j]}
                local squared_diff=$(awk -v t="$time_val" -v avg="$avg_time" 'BEGIN {printf "%.10f", (t - avg)^2}')
                sum_squared_diff=$(awk -v sum="$sum_squared_diff" -v diff="$squared_diff" 'BEGIN {printf "%.10f", sum + diff}')
            done
            
            local std_dev=$(awk -v sum="$sum_squared_diff" -v n="$run_count" 'BEGIN {printf "%.6f", sqrt(sum / (n - 1))}')
            echo "Standard deviation: $std_dev seconds"
            
            # Calculate coefficient of variation (CV) for stability assessment
            local cv=$(awk -v sd="$std_dev" -v avg="$avg_time" 'BEGIN {printf "%.2f", (sd / avg) * 100}')
            echo "Coefficient of variation: $cv%"
        fi

        # Print Perf Stats if data available
        if [ "$use_perf" -eq 1 ]; then
             echo ""
             echo "Perf Counter Stats (Average over $run_count runs):"
             
             if [ ${#cache_refs[@]} -gt 0 ]; then
                 avg_cache_refs=$(calc_average_int "${cache_refs[@]}")
                 printf "%'15s      cache-references\n" "$avg_cache_refs"
             fi

             if [ ${#cache_misses[@]} -gt 0 ]; then
                 avg_cache_misses=$(calc_average_int "${cache_misses[@]}")
                 
                 if [ ${#cache_refs[@]} -gt 0 ] && [ ! -z "$avg_cache_refs" ] && [ "$avg_cache_refs" != "0" ]; then
                     avg_cache_refs_float=$(calc_average_float "${cache_refs[@]}")
                     avg_cache_misses_float=$(calc_average_float "${cache_misses[@]}")
                     if [ ! -z "$avg_cache_misses_float" ]; then
                         miss_rate=$(echo "scale=3; ($avg_cache_misses_float / $avg_cache_refs_float) * 100" | bc -l)
                         printf "%'15s      cache-misses                     #  %6.3f %% of all cache refs\n" "$avg_cache_misses" "$miss_rate"
                     else
                         printf "%'15s      cache-misses\n" "$avg_cache_misses"
                     fi
                 else
                     printf "%'15s      cache-misses\n" "$avg_cache_misses"
                 fi
             fi
             
             if [ ${#l1_misses[@]} -gt 0 ]; then
                 avg_l1_misses=$(calc_average_int "${l1_misses[@]}")
                 printf "%'15s      L1-dcache-load-misses\n" "$avg_l1_misses"
             fi
             
             if [ ${#llc_misses[@]} -gt 0 ]; then
                 avg_llc_misses=$(calc_average_int "${llc_misses[@]}")
                 printf "%'15s      LLC-load-misses\n" "$avg_llc_misses"
             fi
             
             if [ ${#cycles_arr[@]} -gt 0 ]; then
                 avg_cycles=$(calc_average_int "${cycles_arr[@]}")
                 printf "%'15s      cycles\n" "$avg_cycles"
             fi
             
             if [ ${#instructions_arr[@]} -gt 0 ]; then
                 avg_instr=$(calc_average_int "${instructions_arr[@]}")
                 
                 if [ ${#cycles_arr[@]} -gt 0 ] && [ ! -z "$avg_cycles" ] && [ "$avg_cycles" != "0" ]; then
                      avg_cycles_float=$(calc_average_float "${cycles_arr[@]}")
                      avg_instr_float=$(calc_average_float "${instructions_arr[@]}")
                      ipc=$(echo "scale=3; $avg_instr_float / $avg_cycles_float" | bc -l)
                      printf "%'15s      instructions                     #    %0.3f  insn per cycle\n" "$avg_instr" "$ipc"
                 else
                      printf "%'15s      instructions\n" "$avg_instr"
                 fi
             fi
        fi

    else
        echo "Could not calculate average time: no valid time measurements"
    fi
    
    return 0
}

# Main script logic
if [ $# -lt 1 ]; then
    echo "Usage: $0 <source_file.c> [-openmp] [-numa N] [-warmup N] [-runs M]"
    echo "Example: $0 gemm_tile.c -openmp -numa 0 -warmup 5 -runs 20"
    echo ""
    echo "Options:"
    echo "  -openmp       Enable OpenMP compilation"
    echo "  -numa N       Bind to NUMA node N (requires numactl)"
    echo "  -warmup N     Number of warm-up runs (default: 5)"
    echo "  -runs M       Number of timing runs (default: 10)"
    exit 1
fi

source_file=$1
use_openmp=0
numa_node=""
warmup_runs=2
timing_runs=3
use_perf=0
perf_events="cache-references,cache-misses,L1-dcache-load-misses,LLC-load-misses"

# Parse arguments
shift
while [ $# -gt 0 ]; do
    case "$1" in
        -openmp)
            use_openmp=1
            ;;
        -numa)
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                numa_node=$1
                # Check if numactl is available
                if ! command -v numactl &> /dev/null; then
                    echo "Error: numactl command not found."
                    echo ""
                    echo "To install numactl on Ubuntu/Debian:"
                    echo "  sudo apt-get install numactl"
                    echo ""
                    echo "To install numactl on CentOS/RHEL:"
                    echo "  sudo yum install numactl"
                    exit 1
                fi
            else
                echo "Error: Invalid NUMA node number"
                exit 1
            fi
            ;;
        -warmup)
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                warmup_runs=$1
            else
                echo "Warning: Invalid warmup count, using default: 5"
                warmup_runs=1
            fi
            ;;
        -runs)
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                timing_runs=$1
            else
                echo "Warning: Invalid timing runs count, using default: 10"
                timing_runs=2
            fi
            ;;
        -perf)
            use_perf=1
            ;;
        -events)
            shift
            perf_events="$1"
            ;;
        *)
            echo "Warning: Ignoring unknown parameter: $1"
            ;;
    esac
    shift
done

# Run the test
run_test "$source_file" $use_openmp "$numa_node" $warmup_runs $timing_runs $use_perf "$perf_events"

echo "==================================================================="
echo "Done!"
echo "==================================================================="