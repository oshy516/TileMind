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
PERF_EVENTS="L1-dcache-load-misses,LLC-load-misses,cache-misses,cycles,instructions"

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
  -events "e1,e2,..." Custom perf events (default: L1-dcache-load-misses,LLC-load-misses,cache-misses,cycles,instructions)
  -h, --help          Show this help message

Perf Events Examples:
  Basic cache:        "L1-dcache-load-misses,LLC-load-misses,cache-misses"
  Full cache:         "L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses"
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
    # 检查 perf 权限
    if [ "$(cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null)" -gt 1 ]; then
        echo "Warning: perf may need elevated permissions."
        echo "Run: sudo sysctl -w kernel.perf_event_paranoid=-1"
        echo ""
    fi
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

# 存储结果的数组
declare -a execution_times
declare -a l1_misses
declare -a llc_misses
declare -a cache_misses
declare -a cycles_arr
declare -a instructions_arr

for i in $(seq 1 $TIMING_RUNS); do
    echo "-------------------------------------"
    echo "Run $i/$TIMING_RUNS"
    echo "-------------------------------------"
    
    if [ $USE_PERF -eq 1 ]; then
        # 使用临时文件存储输出
        TEMP_OUTPUT="/tmp/polly_perf_$$_$i.txt"
        
        # 运行 perf stat
        sudo perf stat -e $PERF_EVENTS ./$OUTPUT_NAME > /dev/null 2> "$TEMP_OUTPUT"
        
        # 提取执行时间
        exec_time=$(grep "seconds time elapsed" "$TEMP_OUTPUT" | awk '{print $1}')
        execution_times+=($exec_time)
        echo "Execution time: $exec_time seconds"
        
        # 提取各项指标
        l1_miss=$(grep "L1-dcache-load-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$l1_miss" ] && l1_misses+=($l1_miss) && echo "L1-dcache-load-misses: $l1_miss"
        
        llc_miss=$(grep "LLC-load-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$llc_miss" ] && llc_misses+=($llc_miss) && echo "LLC-load-misses: $llc_miss"
        
        cache_miss=$(grep -w "cache-misses" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$cache_miss" ] && cache_misses+=($cache_miss) && echo "cache-misses: $cache_miss"
        
        cycles=$(grep -w "cycles" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$cycles" ] && cycles_arr+=($cycles) && echo "cycles: $cycles"
        
        instructions=$(grep -w "instructions" "$TEMP_OUTPUT" | awk '{gsub(/,/,"",$1); print $1}')
        [ ! -z "$instructions" ] && instructions_arr+=($instructions) && echo "instructions: $instructions"
        
        # 删除临时文件
        rm -f "$TEMP_OUTPUT"
    else
        # 不使用 perf，只测时间
        start_time=$(date +%s.%N)
        ./$OUTPUT_NAME > /dev/null 2>&1
        end_time=$(date +%s.%N)
        exec_time=$(echo "$end_time - $start_time" | bc -l)
        execution_times+=($exec_time)
        echo "Execution time: $exec_time seconds"
    fi
    
    echo ""
done

# 计算统计数据
echo "=========================================="
echo "Performance Summary"
echo "=========================================="
echo ""

# 函数：计算平均值
calc_average() {
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
        echo "N/A"
    fi
}

# 函数：计算最小值
calc_min() {
    local min=999999999999
    for val in "$@"; do
        if [ ! -z "$val" ]; then
            if (( $(echo "$val < $min" | bc -l) )); then
                min=$val
            fi
        fi
    done
    echo "$min"
}

# 函数：计算最大值
calc_max() {
    local max=0
    for val in "$@"; do
        if [ ! -z "$val" ]; then
            if (( $(echo "$val > $max" | bc -l) )); then
                max=$val
            fi
        fi
    done
    echo "$max"
}

# 执行时间统计
if [ ${#execution_times[@]} -gt 0 ]; then
    avg_time=$(calc_average "${execution_times[@]}")
    min_time=$(calc_min "${execution_times[@]}")
    max_time=$(calc_max "${execution_times[@]}")
    
    echo "Execution Time:"
    echo "  Average: $avg_time seconds"
    echo "  Min:     $min_time seconds"
    echo "  Max:     $max_time seconds"
    echo ""
fi

# L1 Cache Miss 统计
if [ ${#l1_misses[@]} -gt 0 ]; then
    avg_l1=$(calc_average "${l1_misses[@]}")
    min_l1=$(calc_min "${l1_misses[@]}")
    max_l1=$(calc_max "${l1_misses[@]}")
    
    echo "L1-dcache-load-misses:"
    echo "  Average: $avg_l1"
    echo "  Min:     $min_l1"
    echo "  Max:     $max_l1"
    echo ""
fi

# LLC Miss 统计
if [ ${#llc_misses[@]} -gt 0 ]; then
    avg_llc=$(calc_average "${llc_misses[@]}")
    min_llc=$(calc_min "${llc_misses[@]}")
    max_llc=$(calc_max "${llc_misses[@]}")
    
    echo "LLC-load-misses:"
    echo "  Average: $avg_llc"
    echo "  Min:     $min_llc"
    echo "  Max:     $max_llc"
    echo ""
fi

# Cache Miss 统计
if [ ${#cache_misses[@]} -gt 0 ]; then
    avg_cache=$(calc_average "${cache_misses[@]}")
    min_cache=$(calc_min "${cache_misses[@]}")
    max_cache=$(calc_max "${cache_misses[@]}")
    
    echo "cache-misses:"
    echo "  Average: $avg_cache"
    echo "  Min:     $min_cache"
    echo "  Max:     $max_cache"
    echo ""
fi

# Cycles 统计
if [ ${#cycles_arr[@]} -gt 0 ]; then
    avg_cycles=$(calc_average "${cycles_arr[@]}")
    
    echo "Cycles:"
    echo "  Average: $avg_cycles"
    echo ""
fi

# Instructions 统计
if [ ${#instructions_arr[@]} -gt 0 ]; then
    avg_instructions=$(calc_average "${instructions_arr[@]}")
    
    echo "Instructions:"
    echo "  Average: $avg_instructions"
    echo ""
    
    # 计算 CPI (Cycles Per Instruction)
    if [ ${#cycles_arr[@]} -gt 0 ] && [ ! -z "$avg_cycles" ] && [ ! -z "$avg_instructions" ]; then
        cpi=$(echo "scale=4; $avg_cycles / $avg_instructions" | bc -l)
        echo "CPI (Cycles Per Instruction):"
        echo "  Average: $cpi"
        echo ""
    fi
fi

echo "=========================================="
echo "Benchmark Complete!"
echo "Binary saved as: $OUTPUT_NAME"
echo "=========================================="
