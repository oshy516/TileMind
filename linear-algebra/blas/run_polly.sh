#!/bin/bash

# Polly Benchmark Script
# 支持分块/不分块对比、预热、多次实验和缓存数据收集

# 默认参数
SOURCE_FILE="gemm.c"
UTILS_PATH="../../../utilities"
USE_TILING=0
WARMUP_RUNS=3
TIMING_RUNS=10
ENABLE_VECTORIZER=0
ENABLE_PARALLEL=0
PERF_EVENTS="cache-references,cache-misses,L1-dcache-load-misses,LLC-load-misses"

# 显示使用说明
show_usage() {
    cat << USAGE
Usage: $0 <source_file.c> [OPTIONS]

Options:
  -tile               Enable Polly tiling optimization (default: disabled)
  -vec                Enable Polly vectorizer (requires -tile)
  -parallel           Enable Polly parallelization (requires -tile and -fopenmp)
  -warmup N           Number of warmup runs (default: 3)
  -runs N             Number of timing runs (default: 10)
  -events "e1,e2,..." Custom perf events (default: cache-references,cache-misses,L1-dcache-load-misses,LLC-load-misses)
  -h, --help          Show this help message

Perf Events Examples:
  Basic cache:        "L1-dcache-load-misses,LLC-load-misses,cache-misses"
  Full cache:         "cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses"
  With instructions:  "cache-misses,cycles,instructions,branches,branch-misses"

Examples:
  # Basic: Polly without tiling
  $0 gemm.c

  # Enable tiling
  $0 gemm.c -tile

  # Tiling + vectorization + 5 warmup + 20 runs
  $0 gemm.c -tile -vec -warmup 5 -runs 20

  # Custom perf events
  $0 gemm.c -tile -events "L1-dcache-load-misses,LLC-load-misses"

  # Full optimization
  $0 gemm.c -tile -vec -parallel -warmup 5 -runs 15
USAGE
}

# 解析命令行参数
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

SOURCE_FILE=$1
shift

while [ $# -gt 0 ]; do
    case "$1" in
        -tile)
            USE_TILING=1
            ;;
        -vec)
            ENABLE_VECTORIZER=1
            ;;
        -parallel)
            ENABLE_PARALLEL=1
            ;;
        -warmup)
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                WARMUP_RUNS=$1
            else
                echo "Error: Invalid warmup count"
                exit 1
            fi
            ;;
        -runs)
            shift
            if [[ $1 =~ ^[0-9]+$ ]]; then
                TIMING_RUNS=$1
            else
                echo "Error: Invalid timing runs count"
                exit 1
            fi
            ;;
        -events)
            shift
            PERF_EVENTS="$1"
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Warning: Unknown option: $1"
            ;;
    esac
    shift
done

# 检查源文件是否存在
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '$SOURCE_FILE' not found"
    exit 1
fi

# 提取基础文件名
BASE_NAME=$(basename "$SOURCE_FILE" .c)

# 构建编译命令
COMPILE_CMD="clang -O3 -DPOLYBENCH_TIME -mllvm -polly"
OUTPUT_NAME="${BASE_NAME}_polly"

# 添加优化选项
if [ $USE_TILING -eq 1 ]; then
    COMPILE_CMD="$COMPILE_CMD -mllvm -polly-tiling"
    OUTPUT_NAME="${OUTPUT_NAME}_tile"
    
    if [ $ENABLE_VECTORIZER -eq 1 ]; then
        COMPILE_CMD="$COMPILE_CMD -mllvm -polly-vectorizer=stripmine"
        OUTPUT_NAME="${OUTPUT_NAME}_vec"
    fi
    
    if [ $ENABLE_PARALLEL -eq 1 ]; then
        COMPILE_CMD="$COMPILE_CMD -mllvm -polly-parallel -fopenmp"
        OUTPUT_NAME="${OUTPUT_NAME}_par"
    fi
else
    OUTPUT_NAME="${OUTPUT_NAME}_default"
fi

# 完成编译命令
COMPILE_CMD="$COMPILE_CMD $SOURCE_FILE ${UTILS_PATH}/polybench.c -o $OUTPUT_NAME -I${UTILS_PATH} -I. -lm"

# 显示配置信息
echo "=========================================="
echo "Polly Benchmark Configuration"
echo "=========================================="
echo "Source file:       $SOURCE_FILE"
echo "Output binary:     $OUTPUT_NAME"
echo "Polly tiling:      $([ $USE_TILING -eq 1 ] && echo 'ENABLED' || echo 'DISABLED')"
echo "Vectorization:     $([ $ENABLE_VECTORIZER -eq 1 ] && echo 'ENABLED' || echo 'DISABLED')"
echo "Parallelization:   $([ $ENABLE_PARALLEL -eq 1 ] && echo 'ENABLED' || echo 'DISABLED')"
echo "Warmup runs:       $WARMUP_RUNS"
echo "Timing runs:       $TIMING_RUNS"
echo "Perf events:       $PERF_EVENTS"
echo "=========================================="
echo ""

# 编译
echo "Compiling..."
echo "Command: $COMPILE_CMD"
echo ""
eval $COMPILE_CMD

if [ $? -ne 0 ]; then
    echo "Error: Compilation failed"
    exit 1
fi

echo "Compilation successful!"
echo ""

# 检查 perf 是否可用
if ! command -v perf &> /dev/null; then
    echo "Warning: perf command not found. Install with:"
    echo "  sudo apt-get install linux-tools-common linux-tools-generic"
    echo ""
    echo "Running without perf statistics..."
    USE_PERF=0
else
    USE_PERF=1
fi

# 预热阶段
echo "=========================================="
echo "Warmup Phase ($WARMUP_RUNS runs)"
echo "=========================================="
for i in $(seq 1 $WARMUP_RUNS); do
    echo "  Warmup run $i/$WARMUP_RUNS..."
    ./$OUTPUT_NAME > /dev/null 2>&1
done
echo "Warmup complete!"
echo ""

# 性能测试阶段
echo "=========================================="
echo "Performance Testing ($TIMING_RUNS runs)"
echo "=========================================="

if [ ! -z "$OMP_NUM_THREADS" ]; then
    echo "Environment OMP_NUM_THREADS is set to: $OMP_NUM_THREADS"
else
    echo "Environment OMP_NUM_THREADS is NOT set (using default)."
fi

# 存储结果的数组
declare -a execution_times
declare -a cache_refs
declare -a cache_misses
declare -a l1_misses
declare -a llc_misses
declare -a l1_loads
declare -a llc_loads
declare -a cycles_arr
declare -a instructions_arr
declare -a branches_arr
declare -a branch_misses_arr

for i in $(seq 1 $TIMING_RUNS); do
    echo "-------------------------------------"
    echo "Run $i/$TIMING_RUNS"
    echo "-------------------------------------"
    
    if [ $USE_PERF -eq 1 ]; then
        # 使用临时文件存储输出
        TEMP_OUTPUT="/tmp/polly_perf_$$_$i.txt"
        
        # 运行 perf stat, preserving OMP_NUM_THREADS if set
        if [ ! -z "$OMP_NUM_THREADS" ]; then
            sudo OMP_NUM_THREADS="$OMP_NUM_THREADS" perf stat -e $PERF_EVENTS ./$OUTPUT_NAME > /dev/null 2> "$TEMP_OUTPUT"
        else
            sudo perf stat -e $PERF_EVENTS ./$OUTPUT_NAME > /dev/null 2> "$TEMP_OUTPUT"
        fi
        
        # 提取执行时间
        exec_time=$(grep "seconds time elapsed" "$TEMP_OUTPUT" | awk '{print $1}')
        execution_times+=($exec_time)
        
        # 提取各项指标
        cache_ref=$(grep -w "cache-references" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$cache_ref" ] && cache_refs+=($cache_ref)
        
        cache_miss=$(grep -w "cache-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$cache_miss" ] && cache_misses+=($cache_miss)
        
        l1_miss=$(grep "L1-dcache-load-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$l1_miss" ] && l1_misses+=($l1_miss)
        
        llc_miss=$(grep "LLC-load-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$llc_miss" ] && llc_misses+=($llc_miss)
        
        l1_load=$(grep "L1-dcache-loads" "$TEMP_OUTPUT" | grep -v "misses" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$l1_load" ] && l1_loads+=($l1_load)
        
        llc_load=$(grep "LLC-loads" "$TEMP_OUTPUT" | grep -v "misses" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$llc_load" ] && llc_loads+=($llc_load)
        
        cycles=$(grep -w "cycles" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$cycles" ] && cycles_arr+=($cycles)
        
        instructions=$(grep -w "instructions" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$instructions" ] && instructions_arr+=($instructions)
        
        branches=$(grep -w "branches" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$branches" ] && branches_arr+=($branches)
        
        branch_miss=$(grep "branch-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$branch_miss" ] && branch_misses_arr+=($branch_miss)
        
        # 显示当前运行的结果
        printf "Execution time: %.6f seconds\n" $exec_time
        echo ""
        
        # Cache References
        if [ ! -z "$cache_ref" ]; then
            printf "%'15s      cache-references\n" "$cache_ref"
        fi
        
        # Cache Misses (带百分比)
        if [ ! -z "$cache_miss" ]; then
            if [ ! -z "$cache_ref" ] && [ "$cache_ref" != "0" ]; then
                miss_rate=$(echo "scale=3; ($cache_miss / $cache_ref) * 100" | bc -l)
                printf "%'15s      cache-misses                     #  %6.3f %% of all cache refs\n" "$cache_miss" "$miss_rate"
            else
                printf "%'15s      cache-misses\n" "$cache_miss"
            fi
        fi
        
        # L1 dcache load misses
        if [ ! -z "$l1_miss" ]; then
            printf "%'15s      L1-dcache-load-misses\n" "$l1_miss"
        fi
        
        # L1 dcache loads
        if [ ! -z "$l1_load" ]; then
            printf "%'15s      L1-dcache-loads\n" "$l1_load"
        fi
        
        # LLC load misses
        if [ ! -z "$llc_miss" ]; then
            printf "%'15s      LLC-load-misses\n" "$llc_miss"
        fi
        
        # LLC loads
        if [ ! -z "$llc_load" ]; then
            printf "%'15s      LLC-loads\n" "$llc_load"
        fi
        
        # Cycles
        if [ ! -z "$cycles" ]; then
            printf "%'15s      cycles\n" "$cycles"
        fi
        
        # Instructions (带 IPC)
        if [ ! -z "$instructions" ]; then
            if [ ! -z "$cycles" ] && [ "$cycles" != "0" ]; then
                ipc=$(echo "scale=3; $instructions / $cycles" | bc -l)
                printf "%'15s      instructions                     #    %0.3f  insn per cycle\n" "$instructions" "$ipc"
            else
                printf "%'15s      instructions\n" "$instructions"
            fi
        fi
        
        # Branches
        if [ ! -z "$branches" ]; then
            printf "%'15s      branches\n" "$branches"
        fi
        
        # Branch misses (带百分比)
        if [ ! -z "$branch_miss" ]; then
            if [ ! -z "$branches" ] && [ "$branches" != "0" ]; then
                branch_miss_rate=$(echo "scale=3; ($branch_miss / $branches) * 100" | bc -l)
                printf "%'15s      branch-misses                    #  %6.3f %% of all branches\n" "$branch_miss" "$branch_miss_rate"
            else
                printf "%'15s      branch-misses\n" "$branch_miss"
            fi
        fi
        
        echo ""
        
        # 删除临时文件
        rm -f "$TEMP_OUTPUT"
    else
        # 不使用 perf，只测时间
        start_time=$(date +%s.%N)
        ./$OUTPUT_NAME > /dev/null 2>&1
        end_time=$(date +%s.%N)
        exec_time=$(echo "$end_time - $start_time" | bc -l)
        execution_times+=($exec_time)
        printf "Execution time: %.6f seconds\n" $exec_time
        echo ""
    fi
done

# 计算统计数据
echo "=========================================="
echo "Performance Summary (Average)"
echo "=========================================="
echo ""

# 函数：计算平均值（保留小数）
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

# 函数：计算平均值（整数）
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
        # 四舍五入到整数
        printf "%.0f" $(echo "scale=6; $sum / $count" | bc -l)
    else
        echo ""
    fi
}

# 执行时间统计
if [ ${#execution_times[@]} -gt 0 ]; then
    avg_time=$(calc_average_float "${execution_times[@]}")
    printf "Average execution time: %.6f seconds\n" $avg_time
    echo ""
fi

echo " Performance counter stats (averaged over $TIMING_RUNS runs):"
echo ""

# Cache References
if [ ${#cache_refs[@]} -gt 0 ]; then
    avg_cache_refs=$(calc_average_int "${cache_refs[@]}")
    printf "%'15s      cache-references\n" "$avg_cache_refs"
fi

# Cache Misses (带百分比)
if [ ${#cache_misses[@]} -gt 0 ]; then
    avg_cache_misses=$(calc_average_int "${cache_misses[@]}")
    
    # 计算 cache miss rate (使用浮点数平均值计算)
    if [ ${#cache_refs[@]} -gt 0 ] && [ ! -z "$avg_cache_refs" ] && [ "$avg_cache_refs" != "0" ]; then
        avg_cache_refs_float=$(calc_average_float "${cache_refs[@]}")
        avg_cache_misses_float=$(calc_average_float "${cache_misses[@]}")
        miss_rate=$(echo "scale=3; ($avg_cache_misses_float / $avg_cache_refs_float) * 100" | bc -l)
        printf "%'15s      cache-misses                     #  %6.3f %% of all cache refs\n" "$avg_cache_misses" "$miss_rate"
    else
        printf "%'15s      cache-misses\n" "$avg_cache_misses"
    fi
fi

# L1 dcache load misses
if [ ${#l1_misses[@]} -gt 0 ]; then
    avg_l1_misses=$(calc_average_int "${l1_misses[@]}")
    printf "%'15s      L1-dcache-load-misses\n" "$avg_l1_misses"
fi

# L1 dcache loads
if [ ${#l1_loads[@]} -gt 0 ]; then
    avg_l1_loads=$(calc_average_int "${l1_loads[@]}")
    printf "%'15s      L1-dcache-loads\n" "$avg_l1_loads"
fi

# LLC load misses
if [ ${#llc_misses[@]} -gt 0 ]; then
    avg_llc_misses=$(calc_average_int "${llc_misses[@]}")
    printf "%'15s      LLC-load-misses\n" "$avg_llc_misses"
fi

# LLC loads
if [ ${#llc_loads[@]} -gt 0 ]; then
    avg_llc_loads=$(calc_average_int "${llc_loads[@]}")
    printf "%'15s      LLC-loads\n" "$avg_llc_loads"
fi

# Cycles
if [ ${#cycles_arr[@]} -gt 0 ]; then
    avg_cycles=$(calc_average_int "${cycles_arr[@]}")
    printf "%'15s      cycles\n" "$avg_cycles"
fi

# Instructions (带 IPC)
if [ ${#instructions_arr[@]} -gt 0 ]; then
    avg_instructions=$(calc_average_int "${instructions_arr[@]}")
    
    # 计算 IPC (使用浮点数平均值计算)
    if [ ${#cycles_arr[@]} -gt 0 ] && [ ! -z "$avg_cycles" ] && [ "$avg_cycles" != "0" ]; then
        avg_cycles_float=$(calc_average_float "${cycles_arr[@]}")
        avg_instructions_float=$(calc_average_float "${instructions_arr[@]}")
        ipc=$(echo "scale=3; $avg_instructions_float / $avg_cycles_float" | bc -l)
        printf "%'15s      instructions                     #    %0.3f  insn per cycle\n" "$avg_instructions" "$ipc"
    else
        printf "%'15s      instructions\n" "$avg_instructions"
    fi
fi

# Branches
if [ ${#branches_arr[@]} -gt 0 ]; then
    avg_branches=$(calc_average_int "${branches_arr[@]}")
    printf "%'15s      branches\n" "$avg_branches"
fi

# Branch misses (带百分比)
if [ ${#branch_misses_arr[@]} -gt 0 ]; then
    avg_branch_misses=$(calc_average_int "${branch_misses_arr[@]}")
    
    # 计算 branch miss rate (使用浮点数平均值计算)
    if [ ${#branches_arr[@]} -gt 0 ] && [ ! -z "$avg_branches" ] && [ "$avg_branches" != "0" ]; then
        avg_branches_float=$(calc_average_float "${branches_arr[@]}")
        avg_branch_misses_float=$(calc_average_float "${branch_misses_arr[@]}")
        branch_miss_rate=$(echo "scale=3; ($avg_branch_misses_float / $avg_branches_float) * 100" | bc -l)
        printf "%'15s      branch-misses                    #  %6.3f %% of all branches\n" "$avg_branch_misses" "$branch_miss_rate"
    else
        printf "%'15s      branch-misses\n" "$avg_branch_misses"
    fi
fi

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "Binary saved as: $OUTPUT_NAME"
echo "=========================================="