#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import time
import argparse
import platform
import sys

def get_cache_info():
    """
    Dynamically retrieve cache information from the system
    Returns a dictionary with L1, L2 cache sizes and cache line size in bytes
    """
    cache_info = {
        'L1_size': None,  # L1 data cache size in bytes (per core)
        'L2_size': None,  # L2 cache size in bytes (per core)
        'cache_line': None  # Cache line size in bytes
    }
    
    system = platform.system()
    
    if system == 'Linux':
        try:
            # Try using lscpu to get cache information
            output = subprocess.check_output(['lscpu'], universal_newlines=True)
            
            print("Analyzing system cache information")
            
            # Try the instance-based format first
            l1d_pattern = r'L1d:\s+(\d+(?:\.\d+)?)\s+([KMG])iB\s+\((\d+)\s+instances\)'
            l2_pattern = r'L2:\s+(\d+(?:\.\d+)?)\s+([KMG])iB\s+\((\d+)\s+instances\)'
            
            l1d_match = re.search(l1d_pattern, output)
            l2_match = re.search(l2_pattern, output)
            
            if l1d_match:
                size = float(l1d_match.group(1))
                unit = l1d_match.group(2)
                instances = int(l1d_match.group(3))
                multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                total_size = size * multiplier
                cache_info['L1_size'] = int(total_size / instances)
                print(f"Found L1d cache: {size} {unit}iB total across {instances} instances")
                print(f"Calculated per-core L1d cache: {cache_info['L1_size']/1024:.1f} KB")
            
            if l2_match:
                size = float(l2_match.group(1))
                unit = l2_match.group(2)
                instances = int(l2_match.group(3))
                multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                total_size = size * multiplier
                cache_info['L2_size'] = int(total_size / instances)
                print(f"Found L2 cache: {size} {unit}iB total across {instances} instances")
                print(f"Calculated per-core L2 cache: {cache_info['L2_size']/1024:.1f} KB")
            
            # Get CPU core count
            cores_per_socket = 1
            sockets = 1
            cores_match = re.search(r'Core\(s\) per socket:\s+(\d+)', output)
            sockets_match = re.search(r'Socket\(s\):\s+(\d+)', output)
            
            if cores_match:
                cores_per_socket = int(cores_match.group(1))
            if sockets_match:
                sockets = int(sockets_match.group(1))
            
            total_cores = cores_per_socket * sockets
            
            # If the first pattern didn't match, try alternative formats
            if cache_info['L1_size'] is None:
                # Try the simple format: "L1d: 480 KiB"
                simple_l1d_pattern = r'L1d:\s+(\d+(?:\.\d+)?)\s+([KMG])iB'
                simple_match = re.search(simple_l1d_pattern, output)
                if simple_match:
                    size = float(simple_match.group(1))
                    unit = simple_match.group(2)
                    multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                    total_size = size * multiplier
                    cache_info['L1_size'] = int(total_size / total_cores)
                    print(f"Using alternative pattern - L1d cache: {size} {unit}iB")
                    print(f"Detected {total_cores} cores, calculated per-core L1d cache: {cache_info['L1_size']/1024:.1f} KB")
                else:
                    # Try the older format: "L1d cache:"
                    alt_l1d_pattern = r'L1d\s+cache:\s+(\d+(?:\.\d+)?)\s+([KMG])iB'
                    alt_match = re.search(alt_l1d_pattern, output)
                    if alt_match:
                        size = float(alt_match.group(1))
                        unit = alt_match.group(2)
                        multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                        total_size = size * multiplier
                        cache_info['L1_size'] = int(total_size / total_cores)
                        print(f"Using older pattern - L1d cache: {size} {unit}iB")
                        print(f"Detected {total_cores} cores, calculated per-core L1d cache: {cache_info['L1_size']/1024:.1f} KB")
            
            if cache_info['L2_size'] is None:
                # Try the simple format for L2
                simple_l2_pattern = r'L2:\s+(\d+(?:\.\d+)?)\s+([KMG])iB'
                simple_match = re.search(simple_l2_pattern, output)
                if simple_match:
                    size = float(simple_match.group(1))
                    unit = simple_match.group(2)
                    multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                    total_size = size * multiplier
                    cache_info['L2_size'] = int(total_size / total_cores)
                    print(f"Using alternative pattern - L2 cache: {size} {unit}iB")
                    print(f"Detected {total_cores} cores, calculated per-core L2 cache: {cache_info['L2_size']/1024:.1f} KB")
                else:
                    # Try the older format for L2
                    alt_l2_pattern = r'L2\s+cache:\s+(\d+(?:\.\d+)?)\s+([KMG])iB'
                    alt_match = re.search(alt_l2_pattern, output)
                    if alt_match:
                        size = float(alt_match.group(1))
                        unit = alt_match.group(2)
                        multiplier = {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                        total_size = size * multiplier
                        cache_info['L2_size'] = int(total_size / total_cores)
                        print(f"Using older pattern - L2 cache: {size} {unit}iB")
                        print(f"Detected {total_cores} cores, calculated per-core L2 cache: {cache_info['L2_size']/1024:.1f} KB")
            
            # Find cache line size
            # First try CLFLUSH size format
            cl_pattern = r'CLFLUSH\s+size:\s+(\d+)'
            cl_match = re.search(cl_pattern, output)
            if cl_match:
                cache_info['cache_line'] = int(cl_match.group(1))
                print(f"Found cache line size from CLFLUSH: {cache_info['cache_line']} bytes")
            
            # Try alternative cache line size formats
            if cache_info['cache_line'] is None:
                cache_line_pattern = r'cache\s+line\s+size:\s+(\d+)'
                cl_match = re.search(cache_line_pattern, output, re.IGNORECASE)
                if cl_match:
                    cache_info['cache_line'] = int(cl_match.group(1))
                    print(f"Found cache line size directly: {cache_info['cache_line']} bytes")
            
            # Try using getconf command
            if cache_info['cache_line'] is None:
                try:
                    cl_output = subprocess.check_output(['getconf', 'LEVEL1_DCACHE_LINESIZE'], universal_newlines=True)
                    if cl_output.strip() and cl_output.strip() != '0':
                        cache_info['cache_line'] = int(cl_output.strip())
                        print(f"Found cache line size using getconf: {cache_info['cache_line']} bytes")
                except:
                    pass
            
            # Default to 64 bytes if we still don't have a value
            if cache_info['cache_line'] is None:
                cache_info['cache_line'] = 64
                print(f"Using default cache line size: {cache_info['cache_line']} bytes")
            
        except Exception as e:
            print(f"Error retrieving cache information: {e}")
    
    elif system == 'Darwin':  # macOS
        try:
            # Get L1 data cache size
            output = subprocess.check_output(['sysctl', 'hw.l1dcachesize'], universal_newlines=True)
            cache_info['L1_size'] = int(output.split(':')[1].strip())
            
            # Get L2 cache size
            output = subprocess.check_output(['sysctl', 'hw.l2cachesize'], universal_newlines=True)
            cache_info['L2_size'] = int(output.split(':')[1].strip())
            
            # Adjust for per-core values if needed
            try:
                # Get number of physical cores
                cores_output = subprocess.check_output(['sysctl', 'hw.physicalcpu'], universal_newlines=True)
                num_cores = int(cores_output.split(':')[1].strip())
                
                # Check if we have per-processor cache values
                try:
                    per_proc_output = subprocess.check_output(['sysctl', 'hw.perprocessorcaches.size'], universal_newlines=True, stderr=subprocess.DEVNULL)
                    if 'hw.perprocessorcaches.size' in per_proc_output:
                        # Values are already per-core
                        pass
                    else:
                        # Divide by number of cores to get per-core value
                        cache_info['L1_size'] = cache_info['L1_size'] // num_cores
                        cache_info['L2_size'] = cache_info['L2_size'] // num_cores
                except:
                    # Assume default values are per-core
                    pass
            except:
                # If we can't determine, assume system default is already per-core
                pass
            
            # Get cache line size
            output = subprocess.check_output(['sysctl', 'hw.cachelinesize'], universal_newlines=True)
            cache_info['cache_line'] = int(output.split(':')[1].strip())
        except Exception as e:
            print(f"Error retrieving cache information on macOS: {e}")
    
    elif system == 'Windows':
        try:
            # Get CPU core count
            output = subprocess.check_output(['wmic', 'cpu', 'get', 'NumberOfCores'], universal_newlines=True)
            lines = output.strip().split('\n')
            num_cores = 1  # Default
            if len(lines) >= 2:
                try:
                    num_cores = int(lines[1].strip())
                except:
                    pass
            
            # Get cache information
            output = subprocess.check_output(['wmic', 'cpu', 'get', 'L1CacheSize,L2CacheSize,CacheLineSize'], universal_newlines=True)
            lines = output.strip().split('\n')
            if len(lines) >= 2:
                values = lines[1].split()
                if len(values) >= 3:
                    # Convert from total KB to per-core bytes
                    total_l1 = int(values[0]) * 1024
                    total_l2 = int(values[1]) * 1024
                    
                    # Divide by number of cores to get per-core cache sizes
                    cache_info['L1_size'] = total_l1 // num_cores
                    cache_info['L2_size'] = total_l2 // num_cores
                    cache_info['cache_line'] = int(values[2])
        except Exception as e:
            print(f"Error retrieving cache information on Windows: {e}")
    
    # Fallback values if we couldn't retrieve the information
    if cache_info['L1_size'] is None:
        cache_info['L1_size'] = 32 * 1024  # 32KB as default per core
        print("Warning: Could not determine L1 cache size, using default value of 32KB per core")
    
    if cache_info['L2_size'] is None:
        cache_info['L2_size'] = 256 * 1024  # 256KB as default per core
        print("Warning: Could not determine L2 cache size, using default value of 256KB per core")
    
    if cache_info['cache_line'] is None:
        cache_info['cache_line'] = 64  # 64B as default
        print("Warning: Could not determine cache line size, using default value of 64B")
    
    print(f"Cache information retrieved: L1={cache_info['L1_size']/1024:.1f}KB, "
          f"L2={cache_info['L2_size']/1024:.1f}KB, Line={cache_info['cache_line']}B")
    
    return cache_info

def get_physical_cores():
    """获取物理核心数的多平台方法"""
    try:
        # 方法1：使用psutil（如果已安装）
        import psutil
        return psutil.cpu_count(logical=False)
    except ImportError:
        pass
        
    # 方法2：Linux系统解析lscpu
    if platform.system() == 'Linux':
        try:
            output = subprocess.check_output(['lscpu'], universal_newlines=True)
            cores_per_socket = int(re.search(r'Core\(s\) per socket:\s+(\d+)', output).group(1))
            sockets = int(re.search(r'Socket\(s\):\s+(\d+)', output).group(1))
            return cores_per_socket * sockets
        except Exception:
            pass
        
    # 方法3：macOS系统
    if platform.system() == 'Darwin':
        try:
            output = subprocess.check_output(['sysctl', '-n', 'hw.physicalcpu'], universal_newlines=True)
            return int(output.strip())
        except Exception:
            pass
        
    # 方法4：Windows系统
    if platform.system() == 'Windows':
        try:
            output = subprocess.check_output(
                ['wmic', 'cpu', 'get', 'NumberOfCores'], 
                universal_newlines=True
            )
            return sum(int(line) for line in output.splitlines() if line.strip().isdigit())
        except Exception:
            pass
        
    # 保底方案：返回物理核心数（假设没有超线程）
    return os.cpu_count() // 2 if os.cpu_count() else 1

def create_cache_benchmark_code(l1_size, l2_size):
    """
    Create a C program to measure L1 and L2 cache access latencies and operation times
    Returns the generated C file name
    """
    c_code = f"""
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
    #include <stdint.h>
    
    // Using actual cache sizes from system
    #define L1_SIZE ({l1_size})      // L1 cache size (bytes)
    #define L2_SIZE ({l2_size})      // L2 cache size (bytes)
    
    // Measure L1 cache access latency
    double benchmark_l1_access() {{
        const int array_size = L1_SIZE / sizeof(int) / 2; // Ensure array fits in L1
        int *array = (int*) malloc(array_size * sizeof(int));
        
        // Initialize array with each element pointing to next access position
        for (int i = 0; i < array_size - 1; i++) {{
            array[i] = (i + 1) % array_size;
        }}
        array[array_size - 1] = 0; // Create a cycle
        
        // Warm up the cache
        int index = 0;
        for (int i = 0; i < array_size; i++) {{
            index = array[index];
        }}
        
        // Start measurement
        struct timespec start, end;
        const int iterations = 10000000;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        index = 0;
        for (int i = 0; i < iterations; i++) {{
            index = array[index];
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (index == -1) printf("This will never print: %d\\n", index);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        double time_per_access = elapsed_ns / iterations;
        
        free(array);
        return time_per_access;
    }}
    
    // Measure L2 cache access latency
    double benchmark_l2_access() {{
        // Array size larger than L1 but smaller than L2
        const int array_size = (L1_SIZE * 3) / sizeof(int);
        int *array = (int*) malloc(array_size * sizeof(int));
        
        // Initialize with stride to avoid prefetching
        const int stride = 16;
        for (int i = 0; i < array_size - stride; i++) {{
            array[i] = (i + stride) % array_size;
        }}
        for (int i = array_size - stride; i < array_size; i++) {{
            array[i] = 0; // Create a cycle
        }}
        
        // Warm up the cache
        int index = 0;
        for (int i = 0; i < array_size / stride; i++) {{
            index = array[index];
        }}
        
        // Start measurement
        struct timespec start, end;
        const int iterations = 5000000;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        index = 0;
        for (int i = 0; i < iterations; i++) {{
            index = array[index];
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (index == -1) printf("This will never print: %d\\n", index);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        double time_per_access = elapsed_ns / iterations;
        
        free(array);
        return time_per_access;
    }}
    
    // Measure double addition latency
    double benchmark_add_double() {{
        const int iterations = 100000000;
        double a = 1.1, b = 2.2, c = 0.0;
        
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        for (int i = 0; i < iterations; i++) {{
            c = a + b;
            a = b + c;
            b = c + a;
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (c < 0) printf("This will never print: %f\\n", c);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        return elapsed_ns / (iterations * 3); // 3 additions per iteration
    }}
    
    // Measure double multiplication latency
    double benchmark_mul_double() {{
        const int iterations = 100000000;
        double a = 1.1, b = 1.01, c = 1.0;
        
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        for (int i = 0; i < iterations; i++) {{
            c = a * b;
            a = b * c;
            b = c * a;
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (c < 0) printf("This will never print: %f\\n", c);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        return elapsed_ns / (iterations * 3); // 3 multiplications per iteration
    }}
    
    // Measure float addition latency
    float benchmark_add_float() {{
        const int iterations = 100000000;
        float a = 1.1f, b = 2.2f, c = 0.0f;
        
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        for (int i = 0; i < iterations; i++) {{
            c = a + b;
            a = b + c;
            b = c + a;
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (c < 0) printf("This will never print: %f\\n", c);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        return (float)(elapsed_ns / (iterations * 3)); // 3 additions per iteration
    }}
    
    // Measure float multiplication latency
    float benchmark_mul_float() {{
        const int iterations = 100000000;
        float a = 1.1f, b = 1.01f, c = 1.0f;
        
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        for (int i = 0; i < iterations; i++) {{
            c = a * b;
            a = b * c;
            b = c * a;
        }}
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        // Prevent compiler optimization
        if (c < 0) printf("This will never print: %f\\n", c);
        
        double elapsed_ns = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
        return (float)(elapsed_ns / (iterations * 3)); // 3 multiplications per iteration
    }}
    
    int main() {{
        // Run each benchmark multiple times and average
        int num_runs = 5;
        double total_l1 = 0.0;
        double total_l2 = 0.0;
        double total_add_double = 0.0;
        double total_mul_double = 0.0;
        float total_add_float = 0.0;
        float total_mul_float = 0.0;
        
        printf("Running latency benchmarks...\\n");
        
        for (int i = 0; i < num_runs; i++) {{
            printf("Run %d of %d...\\n", i+1, num_runs);
            
            total_l1 += benchmark_l1_access();
            total_l2 += benchmark_l2_access();
            total_add_double += benchmark_add_double();
            total_mul_double += benchmark_mul_double();
            total_add_float += benchmark_add_float();
            total_mul_float += benchmark_mul_float();
        }}
        
        double avg_l1 = total_l1 / num_runs;
        double avg_l2 = total_l2 / num_runs;
        double avg_add_double = total_add_double / num_runs;
        double avg_mul_double = total_mul_double / num_runs;
        float avg_add_float = total_add_float / num_runs;
        float avg_mul_float = total_mul_float / num_runs;
        
        printf("BENCHMARK_RESULTS:\\n");
        printf("T_L1=%.2f\\n", avg_l1);
        printf("T_L2=%.2f\\n", avg_l2);
        printf("T_add_double=%.2f\\n", avg_add_double);
        printf("T_mul_double=%.2f\\n", avg_mul_double);
        printf("T_add_float=%.2f\\n", avg_add_float);
        printf("T_mul_float=%.2f\\n", avg_mul_float);
        
        return 0;
    }}
    """
    
    filename = "cache_benchmark.c"
    with open(filename, "w") as f:
        f.write(c_code)
    
    return filename

def measure_cache_and_operation_latencies(cache_info):
    """
    Measure the latency of cache accesses and floating point operations
    Returns a dictionary with the measured latencies
    """
    latencies = {
        'T_L1': None,               # L1 cache access latency (ns)
        'T_L2': None,               # L2 cache access latency (ns)
        'T_add_double': None,       # Double addition latency (ns)
        'T_mul_double': None,       # Double multiplication latency (ns)
        'T_add_float': None,        # Float addition latency (ns)
        'T_mul_float': None,        # Float multiplication latency (ns)
        'data_size': 8              # Default to double precision (8 bytes)
    }
    
    try:
        # Create the benchmark C file
        c_file = create_cache_benchmark_code(cache_info['L1_size'], cache_info['L2_size'])
        
        # Compile the benchmark program
        print("Compiling cache benchmark code...")
        compile_cmd = ["gcc", "-O3", c_file, "-o", "cache_benchmark", "-lm"]
        subprocess.run(compile_cmd, check=True)
        
        # Run the benchmark
        print("Running cache and operation latency benchmarks...")
        result = subprocess.run(["./cache_benchmark"], check=True, capture_output=True, text=True)
        
        # Parse the results
        for line in result.stdout.split('\n'):
            if line.startswith("T_L1="):
                latencies['T_L1'] = float(line.split('=')[1])
            elif line.startswith("T_L2="):
                latencies['T_L2'] = float(line.split('=')[1])
            elif line.startswith("T_add_double="):
                latencies['T_add_double'] = float(line.split('=')[1])
            elif line.startswith("T_mul_double="):
                latencies['T_mul_double'] = float(line.split('=')[1])
            elif line.startswith("T_add_float="):
                latencies['T_add_float'] = float(line.split('=')[1])
            elif line.startswith("T_mul_float="):
                latencies['T_mul_float'] = float(line.split('=')[1])
        
        # Clean up
        os.remove(c_file)
        os.remove("cache_benchmark")
        
    except Exception as e:
        print(f"Error measuring operation latencies: {e}")
        # Use default values if measurement fails
        latencies['T_L1'] = 1.0       # Default L1 access latency 1ns
        latencies['T_L2'] = 10.0      # Default L2 access latency 10ns
        latencies['T_add_double'] = 3.0
        latencies['T_mul_double'] = 5.0
        latencies['T_add_float'] = 2.0
        latencies['T_mul_float'] = 4.0
        
        print("Using default operation latency values")
    
    return latencies

def find_header_file(source_file):
    """
    Find the corresponding header file in the same directory as the source file
    Returns the path to the header file if found, None otherwise
    """
    base_filename = os.path.splitext(os.path.basename(source_file))[0]
    dir_path = os.path.dirname(source_file)
    
    # If source file is in current directory, dir_path will be empty, so use "."
    if not dir_path:
        dir_path = "."
    
    # Try exact matching header file first (e.g., "gemm.c" -> "gemm.h")
    header_path = os.path.join(dir_path, f"{base_filename}.h")
    if os.path.exists(header_path):
        print(f"Found matching header file: {header_path}")
        return header_path
    
    # If not found, check for any .h files in the same directory
    # with preference for files containing the source filename
    header_files = []
    for file in os.listdir(dir_path):
        if file.endswith(".h"):
            full_path = os.path.join(dir_path, file)
            # Prioritize header files that contain the base filename
            if base_filename.lower() in file.lower():
                print(f"Found related header file: {full_path}")
                return full_path
            header_files.append(full_path)
    
    # If no matching header is found but there are other header files, return the first one
    if header_files:
        print(f"Using alternative header file: {header_files[0]}")
        return header_files[0]
    
    print("No header files found in the source directory")
    return None

def detect_data_type(source_file):
    """
    Detect whether the source code uses single or double precision
    Returns 'double' or 'float' and the size in bytes
    """
    data_type = None
    data_size = None
    
    # 首先查找关联的头文件
    header_file = find_header_file(source_file)
    if header_file:
        try:
            with open(header_file, 'r') as f:
                header_content = f.read()
                
            # 查找数据类型定义
            # 常见模式：typedef float DATA_TYPE 或 #define DATA_TYPE float
            typedef_match = re.search(r'typedef\s+(float|double)\s+DATA_TYPE', header_content, re.IGNORECASE)
            define_match = re.search(r'#define\s+DATA_TYPE\s+(float|double)', header_content, re.IGNORECASE)
            
            if typedef_match:
                data_type = typedef_match.group(1).lower()
                print(f"Found data type in header (typedef): {data_type}")
            elif define_match:
                data_type = define_match.group(1).lower()
                print(f"Found data type in header (#define): {data_type}")
        except Exception as e:
            print(f"Error reading header file: {e}")
    
    # 如果头文件中没有找到，则分析源代码
    if not data_type:
        try:
            with open(source_file, 'r') as f:
                source_content = f.read()
            
            # 查找主要数组的声明
            # 尝试找到A、B、C数组的声明
            array_pattern = r'(float|double)\s+(A|B|C|alpha|beta)\b'
            matches = re.findall(array_pattern, source_content, re.IGNORECASE)
            
            if matches:
                # 统计float和double的出现次数
                type_count = {}
                for match in matches:
                    dtype = match[0].lower()
                    if dtype not in type_count:
                        type_count[dtype] = 0
                    type_count[dtype] += 1
                
                # 选择出现次数最多的类型
                if type_count.get('float', 0) > type_count.get('double', 0):
                    data_type = 'float'
                else:
                    data_type = 'double'
                
                print(f"Determined data type from source code: {data_type}")
            else:
                # 如果没有找到明确的数组声明，查找所有float和double关键字
                float_count = len(re.findall(r'\bfloat\b', source_content))
                double_count = len(re.findall(r'\bdouble\b', source_content))
                
                if float_count > double_count:
                    data_type = 'float'
                else:
                    data_type = 'double'
                
                print(f"Estimated data type based on keyword frequency: {data_type}")
        except Exception as e:
            print(f"Error analyzing source file: {e}")
    
    # 设置数据大小
    if data_type == 'float':
        data_size = 4
    else:  # default to double
        data_type = 'double'
        data_size = 8
    
    print(f"Using data type: {data_type} ({data_size} bytes)")
    return data_type, data_size


def get_tileable_dimensions(source_file):
    """
    Run detect_dimension.py to get information about which dimensions are tileable
    
    Args:
        source_file: Path to the source file to analyze
        
    Returns:
        Dictionary mapping filter IDs to lists of tileable dimensions
    """
    print("\nDetecting tileable dimensions...")
    try:
        # Run detect_dimension.py script on the same source file
        detect_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dimension_detect.py")
        if not os.path.exists(detect_script):
            print(f"Warning: detect_dimension.py not found at {detect_script}")
            return {}
            
        cmd = [sys.executable, detect_script, source_file]
        print(f"Executing command: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error running detect_dimension.py: {stderr}")
            return {}
            
        # Parse the output to extract tileable dimensions
        tileable_dimensions = {}
        
        # Pattern to match dimension info lines like:
        # "  - Filter 1, Dimension 0: (i)"
        pattern = r'\s*-\s*Filter\s+(\d+),\s*Dimension\s+(\d+):\s*\(([^)]+)\)'
        
        for line in stdout.split('\n'):
            match = re.search(pattern, line)
            if match:
                filter_id = int(match.group(1))
                dimension = int(match.group(2))
                var_name = match.group(3)
                
                if filter_id not in tileable_dimensions:
                    tileable_dimensions[filter_id] = []
                
                # Store the dimension and the variable name
                tileable_dimensions[filter_id].append((dimension, var_name))
                print(f"Found tileable dimension: Filter {filter_id}, Dimension {dimension}: ({var_name})")
        
        # Sort dimensions within each filter
        for filter_id in tileable_dimensions:
            tileable_dimensions[filter_id].sort(key=lambda x: x[0])
        
        return tileable_dimensions
    
    except Exception as e:
        print(f"Error detecting tileable dimensions: {e}")
        import traceback
        traceback.print_exc()
        return {}

def map_filters_to_blocks(tileable_dimensions, loop_info):
    """
    Map filters from detect_dimension.py to blocks from loop analysis
    
    Args:
        tileable_dimensions: Dictionary of filter_id -> list of (dimension, var_name)
        loop_info: Loop structure analysis information
        
    Returns:
        Dictionary mapping block indices to dictionaries of loop variables with tileable status
    """
    print("\nMapping filters to blocks...")
    
    # 将返回结构从列表修改为字典，包含是否可平铺的信息
    block_tileable_status = {}
    
    # Early return if no tileable dimensions found
    if not tileable_dimensions:
        print("No tileable dimensions found to map")
        return block_tileable_status
    
    # Get blocks and their loop variables
    blocks = loop_info.get('blocks', [])
    block_to_vars = loop_info.get('block_to_vars', {})
    orig_to_unique = loop_info.get('orig_to_unique', {})
    
    # Assume 1-to-1 mapping between filters and blocks based on order
    if len(blocks) >= len(tileable_dimensions):
        for filter_id, dims in tileable_dimensions.items():
            # Convert to 0-based index if filters are 1-based
            block_idx = filter_id - 1 if filter_id > 0 else filter_id
            
            # Skip if block_idx is invalid
            if block_idx < 0 or block_idx >= len(blocks):
                print(f"Warning: Filter {filter_id} maps to invalid block index {block_idx}")
                continue
            
            # Get block-specific variables
            block_vars = block_to_vars.get(block_idx, [])
            
            if not block_vars:
                print(f"Warning: No variables found for block {block_idx}")
                continue
            
            print(f"Mapping Filter {filter_id} to Block {block_idx}")
            print(f"  Block variables: {block_vars}")
            print(f"  Filter dimensions: {dims}")
            
            # 初始化这个块的所有变量状态 - 默认为不可平铺
            block_tileable_status[block_idx] = {}
            for var in block_vars:
                block_tileable_status[block_idx][var] = False
            
            # For each variable in the block, determine if it's tileable
            for i, var in enumerate(block_vars):
                # Get original variable name without block suffix
                orig_var = var.split('_b')[0] if '_b' in var else var
                
                # Try to find this variable in the filter's tileable dimensions
                is_tileable = False
                
                for dim_idx, dim_var in dims:
                    # Check if variable names match
                    if dim_var == orig_var:
                        is_tileable = True
                        block_tileable_status[block_idx][var] = True
                        print(f"  Variable {var} (orig: {orig_var}) at position {i} matches filter dimension {dim_idx}: TILEABLE")
                        break
                
                if not is_tileable:
                    print(f"  Variable {var} (orig: {orig_var}) at position {i} is NOT TILEABLE")
    else:
        print(f"Warning: Number of filters ({len(tileable_dimensions)}) does not match number of blocks ({len(blocks)})")
        # Try a more sophisticated matching approach here if needed
    
    return block_tileable_status

def extract_computation_code(source_file):
    """
    Extract the computation code from source file with enhanced logic for loop block detection:
    1. First try #pragma scop and #pragma endscop markers
    2. Then identify independent nested loop blocks within the scop region
    
    Returns a list of code blocks representing different computation kernels
    """
    try:
        with open(source_file, 'r') as f:
            content = f.read()
        
        print("Extracting computation code from source...")

        # 方法1: 查找 scop 区域
        if "#pragma scop" in content and "#pragma endscop" in content:
            # 获取scop区域内的内容
            scop_pattern = r'#pragma\s+scop(.*?)#pragma\s+endscop'
            scop_match = re.search(scop_pattern, content, re.DOTALL)
            
            if scop_match:
                scop_content = scop_match.group(1).strip()
                print(f"Found code section between #pragma scop and #pragma endscop")
                
                # 步骤1: 以行为单位分析scop内容
                lines = scop_content.split('\n')
                
                # 步骤2: 寻找真正的顶层for循环起始位置
                top_level_for_positions = []
                brace_levels = []  # 存储每行的大括号层级
                
                # 计算每行的大括号层级
                current_brace_level = 0
                for i, line in enumerate(lines):
                    # 计算本行大括号变化
                    open_braces = line.count('{')
                    close_braces = line.count('}')
                    
                    # 当前行开始的层级
                    brace_levels.append(current_brace_level)
                    
                    # 更新层级
                    current_brace_level += open_braces - close_braces
                
                # 找出所有大括号层级为0并且包含for的行
                for i, line in enumerate(lines):
                    stripped = line.lstrip()
                    # 找出缩进级别为0(或很小)且大括号层级为0的for循环
                    if stripped.startswith('for ') and brace_levels[i] == 0:
                        indent = len(line) - len(stripped)
                        if indent <= 8:  # 允许少量缩进
                            top_level_for_positions.append(i)
                            print(f"Found top-level for at line {i}: {line}")
                
                # 步骤3: 根据顶层for位置分离代码块
                blocks = []
                if len(top_level_for_positions) > 0:
                    for i, pos in enumerate(top_level_for_positions):
                        start_line = pos
                        
                        # 找出此块的结束位置(下一个顶层for之前或整个scop结束)
                        if i < len(top_level_for_positions) - 1:
                            end_line = top_level_for_positions[i+1] - 1
                        else:
                            end_line = len(lines) - 1
                        
                        # 提取代码块
                        block_text = '\n'.join(lines[start_line:end_line+1])
                        blocks.append(block_text)
                        print(f"Extracted block {i+1} from lines {start_line} to {end_line}")
                    
                    print(f"Successfully extracted {len(blocks)} top-level loop blocks")
                    return blocks
                
                # 如果上面的方法失败，尝试通过大括号平衡来分离块
                print("Trying alternate method: separating blocks by balanced braces...")
                blocks = []
                current_block = []
                brace_level = 0
                in_top_level_for = False
                
                for i, line in enumerate(lines):
                    stripped = line.lstrip()
                    
                    # 检测新的顶层for循环开始
                    if stripped.startswith('for ') and brace_level == 0:
                        # 如果已经在处理一个块，先结束它
                        if in_top_level_for and current_block:
                            blocks.append('\n'.join(current_block))
                            current_block = []
                        
                        in_top_level_for = True
                    
                    # 跟踪大括号
                    for char in line:
                        if char == '{':
                            brace_level += 1
                        elif char == '}':
                            brace_level -= 1
                            # 如果回到顶层，且当前行结束了一个块，可能是块结束
                            if brace_level == 0 and '}' in stripped and in_top_level_for:
                                current_block.append(line)
                                blocks.append('\n'.join(current_block))
                                current_block = []
                                in_top_level_for = False
                                continue
                    
                    # 将当前行添加到当前块
                    if in_top_level_for or current_block:
                        current_block.append(line)
                
                # 添加最后处理的块(如果有)
                if current_block:
                    blocks.append('\n'.join(current_block))
                
                if blocks:
                    print(f"Alternate method extracted {len(blocks)} blocks")
                    return blocks
                
                # 最后尝试根据连续的顶层closing braces分离
                print("Final attempt: separating by consecutive top-level closing braces...")
                blocks = []
                current_block_lines = []
                
                for i, line in enumerate(lines):
                    current_block_lines.append(line)
                    
                    # 如果这是一个单独的右大括号行，且下一行是for，这是一个分界点
                    if line.strip() == '}' and i+1 < len(lines) and lines[i+1].lstrip().startswith('for '):
                        blocks.append('\n'.join(current_block_lines))
                        current_block_lines = []
                
                # 添加最后一个块
                if current_block_lines:
                    blocks.append('\n'.join(current_block_lines))
                
                if len(blocks) > 1:
                    print(f"Final method extracted {len(blocks)} blocks")
                    return blocks
                
                # 所有方法都失败，返回整个scop内容
                print("All methods failed, returning entire scop content as one block")
                return [scop_content]
        
        # 方法2: 识别独立的嵌套循环块
        print("No scop markers found, looking for nested loop blocks...")
        
        # 首先标记所有函数的范围，避免跨函数边界提取循环
        function_blocks = []
        func_pattern = r'(\w+(?:\s+\w+)*\s+\w+\s*\([^)]*\)\s*\{)'
        for match in re.finditer(func_pattern, content):
            func_start = match.start()
            func_name = match.group(1).split()[-1].split('(')[0]
            
            # 找到这个函数的结束括号
            open_braces = 0
            func_end = -1
            for i, char in enumerate(content[func_start:], func_start):
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        func_end = i + 1
                        break
            
            if func_end > func_start:
                function_blocks.append((func_start, func_end, func_name))
        
        print(f"Identified {len(function_blocks)} function blocks in source code")
        
        # 在每个函数内部查找嵌套循环
        blocks = []
        for func_start, func_end, func_name in function_blocks:
            func_content = content[func_start:func_end]
            print(f"Analyzing function: {func_name}")
            
            # 标记函数体内所有for循环的起始位置
            loop_starts = []
            for match in re.finditer(r'for\s*\(', func_content):
                loop_starts.append(match.start())
            
            # 排序以确保我们从前向后处理
            loop_starts.sort()
            
            # 跟踪已处理的循环范围，避免重复
            processed_ranges = []
            
            # 识别独立的顶层循环块
            for loop_start in loop_starts:
                # 检查这个位置是否已经在之前处理过的循环中
                skip = False
                for start, end in processed_ranges:
                    if start <= loop_start < end:
                        skip = True
                        break
                
                if skip:
                    continue
                
                # 找到完整的循环块（可能包含嵌套循环）
                open_parens = 0
                header_end = -1
                for i, char in enumerate(func_content[loop_start:], loop_start):
                    if char == '(':
                        open_parens += 1
                    elif char == ')':
                        open_parens -= 1
                        if open_parens == 0:
                            header_end = i + 1
                            break
                
                if header_end == -1:
                    continue  # 循环头格式不完整
                
                # 找到循环体
                body_start = -1
                for i in range(header_end, len(func_content)):
                    if func_content[i] == '{':
                        body_start = i
                        break
                    elif func_content[i] not in [' ', '\t', '\n']:
                        # 单语句循环，没有花括号
                        body_start = i
                        break
                
                if body_start == -1:
                    continue  # 没找到循环体开始
                
                # 如果是使用花括号的循环体，找到匹配的闭合括号
                if func_content[body_start] == '{':
                    open_braces = 1
                    body_end = -1
                    for i in range(body_start + 1, len(func_content)):
                        if func_content[i] == '{':
                            open_braces += 1
                        elif func_content[i] == '}':
                            open_braces -= 1
                            if open_braces == 0:
                                body_end = i + 1
                                break
                    
                    if body_end == -1:
                        continue  # 循环体不完整
                else:
                    # 单语句循环，找到分号
                    body_end = -1
                    for i in range(body_start, len(func_content)):
                        if func_content[i] == ';':
                            body_end = i + 1
                            break
                    
                    if body_end == -1:
                        continue  # 没找到语句结束
                
                # 提取完整的循环块
                full_loop = func_content[loop_start:body_end]
                
                # 确定这是否是一个独立的顶层循环
                is_independent_loop = True
                
                # 检查是否是另一个循环的一部分
                for prev_start, prev_end in processed_ranges:
                    # 如果这个循环已经完全包含在之前处理过的循环中，跳过它
                    if prev_start < loop_start and body_end < prev_end:
                        is_independent_loop = False
                        break
                
                # 只处理独立的顶层循环，且必须是嵌套循环（至少有2个for）
                if is_independent_loop and full_loop.count("for") >= 2:
                    # 计算代码起始位置在原始文件中的绝对位置
                    abs_start = func_start + loop_start
                    abs_end = func_start + body_end
                    
                    # 记录已处理的范围
                    processed_ranges.append((loop_start, body_end))
                    
                    # 检查嵌套深度
                    nesting_depth = 0
                    current_depth = 0
                    for char in full_loop:
                        if char == '{':
                            current_depth += 1
                            nesting_depth = max(nesting_depth, current_depth)
                        elif char == '}':
                            current_depth -= 1
                    
                    # 只有嵌套深度大于1的循环块才视为计算核心
                    if nesting_depth > 1:
                        print(f"Found nested loop block at {abs_start}:{abs_end} in function {func_name} with nesting depth {nesting_depth}")
                        blocks.append(full_loop)
        
        if blocks:
            print(f"Found {len(blocks)} independent nested loop blocks using structural analysis")
            return blocks
        
        # 方法3: 最后尝试找到包含矩阵计算特征的代码段
        print("Looking for matrix computation patterns...")
        matrix_calc_blocks = []
        
        # 寻找常见的矩阵计算模式：索引访问和赋值操作
        # 例如 A[i][j] = B[i][k] * C[k][j]
        matrix_pattern = r'([A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]+\])+)\s*(?:=|\+=|\*=)\s*([^;]+);'
        
        # 在每个函数内搜索
        for func_start, func_end, func_name in function_blocks:
            func_content = content[func_start:func_end]
            matches = re.finditer(matrix_pattern, func_content)
            
            for match in matches:
                # 找到匹配位置前后的上下文
                ctx_start = max(0, match.start() - 200)
                ctx_end = min(len(func_content), match.end() + 200)
                context = func_content[ctx_start:ctx_end]
                
                # 如果上下文中包含for循环且看起来是矩阵操作
                if "for" in context and ("[" in context and "]" in context):
                    # 提取包含这个矩阵操作的最小for循环块
                    inner_loop_start = context.rfind("for", 0, match.start() - ctx_start)
                    if inner_loop_start >= 0:
                        # 找到最外层的for循环
                        outer_loop_start = inner_loop_start
                        while True:
                            prev_for = context.rfind("for", 0, outer_loop_start - 1)
                            if prev_for >= 0 and prev_for > outer_loop_start - 50:  # 假设相关for循环应该相对接近
                                outer_loop_start = prev_for
                            else:
                                break
                        
                        # 尝试提取完整的for循环块
                        if outer_loop_start >= 0:
                            # 扩展到包含整个for循环
                            open_braces = 0
                            loop_end = -1
                            in_loop = False
                            
                            for i, char in enumerate(context[outer_loop_start:], outer_loop_start):
                                if char == '(':
                                    open_braces += 1
                                    in_loop = True
                                elif char == ')' and in_loop:
                                    open_braces -= 1
                                    if open_braces == 0:
                                        in_loop = False
                                elif char == '{' and not in_loop:
                                    open_braces += 1
                                elif char == '}' and not in_loop:
                                    open_braces -= 1
                                    if open_braces == 0:
                                        loop_end = i + 1
                                        break
                            
                            if loop_end > outer_loop_start:
                                loop_block = context[outer_loop_start:loop_end]
                                # 只添加明确包含嵌套循环的块
                                if loop_block.count("for") >= 2:
                                    matrix_calc_blocks.append(loop_block)
        
        if matrix_calc_blocks:
            # 去重，因为可能有重叠
            unique_blocks = []
            for block in matrix_calc_blocks:
                if block not in unique_blocks:
                    unique_blocks.append(block)
            
            print(f"Found {len(unique_blocks)} matrix computation blocks with nested loops")
            return unique_blocks
        
        print("Warning: Could not extract computation code using any method")
        return None
        
    except Exception as e:
        print(f"Error extracting computation code: {e}")
        import traceback
        traceback.print_exc()
        return None
    

def analyze_loop_structure(code_blocks):
    """
    Analyze loop structure to identify dimensions and iterations
    Process multiple independent loop blocks and add block identifiers to variables
    Returns a dictionary containing loop information
    """
    if not code_blocks:
        return {'loops': [], 'statements': [], 'dimensions': [], 'loop_vars': [], 
                'raw_loop_vars': [], 'blocks': [], 'block_to_vars': {}, 
                'loop_vars_to_bounds': {}, 'loop_var_to_size': {}, 
                'loop_levels': {}, 'orig_to_unique': {}, 'loop_bounds': {}, 'loop_sizes': {}}
    
    # Initialize necessary data structures
    loop_info = {
        'loops': [],          # List of loop information
        'statements': [],     # List of computation statements
        'dimensions': [],     # List of identified dimensions
        'loop_vars': [],      # List of loop variables (with block identifiers)
        'raw_loop_vars': [],  # List of original loop variables (without block identifiers)
        'blocks': [],         # Information about each code block
        'block_to_vars': {},  # Mapping from block index to variable list
        'loop_vars_to_bounds': {},  # Mapping from loop variables to dimension upper bounds
        'loop_var_to_size': {},    # Mapping from loop variables to sizes
        'loop_levels': {},     # Mapping from loop variables to nesting levels
        'orig_to_unique': {},  # Mapping from original variable names to block-specific names
        'loop_bounds': {},     # Mapping from loop variables to upper bounds
        'loop_sizes': {}       # Mapping from loop variables to sizes
    }
    
    # If code_blocks is a string, convert to a list
    if isinstance(code_blocks, str):
        code_blocks = [code_blocks]
    
    # Process each code block directly
    for block_idx, code_block in enumerate(code_blocks):
        print(f"\nProcessing block {block_idx} directly")
        
        # Check if OpenMP is used
        is_openmp = "#pragma omp parallel for" in code_block
        
        # Find all loops
        loop_pattern = r'for\s*\(\s*(?:int|long|float|double)?\s*(\w+)\s*=\s*([^;]+);\s*\1\s*([<>]=?|!=|==)\s*([^;]+);\s*([^)]+)\)'
        loops_found = list(re.finditer(loop_pattern, code_block))
        print(f"Found {len(loops_found)} loops in block {block_idx}")
        
        # Initialize block info
        block_info = {
            'code': code_block,
            'loops': len(loops_found),
            'has_nested_loops': False,  # Will be updated later
            'statements': [],
            'loop_vars': []
        }
        
        # Analyze loop nesting structure
        loop_levels = {}   # variable -> nesting level
        loop_bounds = {}   # variable -> upper bound
        loop_sizes = {}    # variable -> size
        
        for i, match in enumerate(loops_found):
            var = match.group(1)  # Original loop variable
            # Add block identifier
            unique_var = f"{var}_b{block_idx}"
            
            # Update mapping from original variable to unique variable
            if var not in loop_info['orig_to_unique']:
                loop_info['orig_to_unique'][var] = []
            if unique_var not in loop_info['orig_to_unique'][var]:
                loop_info['orig_to_unique'][var].append(unique_var)
            
            start = match.group(2).strip()
            op = match.group(3)
            end = match.group(4).strip()
            increment = match.group(5).strip()
            
            print(f"Loop variable: {var} (unique: {unique_var}), range: {start} {op} {end}, increment: {increment}")
            
            # Store upper bound information
            loop_bounds[unique_var] = end
            loop_info['loop_bounds'][unique_var] = end
            
            # Try to extract upper bound dimension name
            bound_match = re.search(r'(_PB_)?(\w+)', end)
            if bound_match:
                bound_name = bound_match.group(2)
                loop_info['loop_vars_to_bounds'][unique_var] = bound_name
            else:
                try:
                    # If it's a numeric value, use it directly
                    bound_value = int(end)
                    loop_info['loop_vars_to_bounds'][unique_var] = str(bound_value)
                except:
                    loop_info['loop_vars_to_bounds'][unique_var] = "unknown"
            
            # Parse numeric range
            try:
                # Check if start/end are numeric constants
                # 处理起始值
                if start.isdigit():
                    start_val = int(start)
                else:
                    # 起始值是变量引用，尝试找到对应的循环变量的起始值（不是大小）
                    start_match = re.search(r'(\w+)', start)
                    if start_match:
                        start_var = start_match.group(1)
                        start_var_unique = f"{start_var}_b{block_idx}"
                        
                        # 直接使用变量的起始值，如果有记录的话
                        if start_var_unique in loop_info.get('loop_var_to_start', {}):
                            start_val = loop_info['loop_var_to_start'][start_var_unique]
                            print(f"Using start value of {start_var_unique} ({start_val}) for start value of {unique_var}")
                        else:
                            # 如果找不到变量的起始值，默认使用0
                            start_val = 0
                            print(f"Start variable {start_var} not found, using default value 0")
                    else:
                        # 无法解析起始值表达式
                        start_val = 0
                
                # 处理结束值
                if end.isdigit():
                    end_val = int(end)
                else:
                    # 结束值是变量引用，尝试找到对应的循环变量值
                    end_match = re.search(r'(\w+)', end)
                    if end_match:
                        end_var = end_match.group(1)
                        # 查找当前块中已处理的循环变量
                        end_var_found = False
                        
                        # 遍历已处理的循环变量
                        for var_name, var_size in loop_sizes.items():
                            # 提取原始变量名和块ID
                            if '_b' in var_name:
                                orig_var = var_name.split('_b')[0]
                                var_block = var_name.split('_b')[1]
                                
                                # 检查是否是同一块中的匹配变量
                                if var_block == str(block_idx) and orig_var == end_var:
                                    end_val = var_size
                                    print(f"Using size of {var_name} ({var_size}) for upper bound of {unique_var}")
                                    end_var_found = True
                                    break
                        
                        if not end_var_found:
                            # 变量没找到，使用默认值
                            print(f"Using default size for variable bound {end}")
                            end_val = 1000
                    else:
                        # 无法解析结束值，使用默认值
                        end_val = 1000
                
                # 解析增量
                inc_val = 1  # 默认增量
                inc_match = re.search(r'(\w+)\s*(\+\+|\+=\s*(\d+))', increment)
                if inc_match and inc_match.group(3):
                    inc_val = int(inc_match.group(3))
                
                # 计算循环大小
                if op == "<=":
                    # 对于 c2 = c1; c2 <= 998 这种情况
                    # 如果 c1 > 998，则循环大小为0
                    if start_val > end_val:
                        loop_size = 0
                        print(f"Start value {start_val} > end value {end_val}, setting loop size to 0")
                    else:
                        loop_size = (end_val - start_val) // inc_val + 1
                elif op == "<":
                    # 对于 c2 = c1; c2 < 998 这种情况
                    # 如果 c1 >= 998，则循环大小为0
                    if start_val >= end_val:
                        loop_size = 0
                        print(f"Start value {start_val} >= end value {end_val}, setting loop size to 0")
                    else:
                        loop_size = (end_val - start_val) // inc_val
                else:
                    loop_size = end_val  # 默认值
                
                # 存储计算出的大小
                loop_sizes[unique_var] = loop_size
                loop_info['loop_sizes'][unique_var] = loop_size
                loop_info['loop_var_to_size'][unique_var] = loop_size
                # 同时存储起始值，方便后续使用
                loop_info['loop_var_to_start'] = loop_info.get('loop_var_to_start', {})
                loop_info['loop_var_to_start'][unique_var] = start_val
                print(f"Calculated size for {unique_var}: {loop_size}")
            except (ValueError, TypeError) as e:
                print(f"Could not calculate size for {unique_var}: {e}")
                # 设置默认大小
                loop_sizes[unique_var] = 1000
                loop_info['loop_sizes'][unique_var] = 1000
                loop_info['loop_var_to_size'][unique_var] = 1000
                # 设置默认起始值
                loop_info['loop_var_to_start'] = loop_info.get('loop_var_to_start', {})
                loop_info['loop_var_to_start'][unique_var] = 0
            
            # Determine nesting level
            loop_start = match.start()
            level = 0

            # Based on environment choose different nesting detection method
            if is_openmp:
                # OpenMP: Determine nesting based on OpenMP blocks and loop positions
                openmp_blocks = []
                openmp_pattern = r'#pragma\s+omp\s+parallel\s+for(.*?)(?=#pragma|$)'
                for omp_match in re.finditer(openmp_pattern, code_block, re.DOTALL):
                    openmp_blocks.append((omp_match.start(), omp_match.end()))
                
                # Determine which OpenMP block this loop belongs to
                for block_start, block_end in openmp_blocks:
                    if block_start <= loop_start < block_end:
                        # Find all loops in this OpenMP block
                        block_content = code_block[block_start:block_end]
                        block_loops = list(re.finditer(loop_pattern, block_content))
                        
                        # If this is the first loop in the block, it's outer
                        if block_loops and block_start + block_loops[0].start() == loop_start:
                            level = 0
                            print(f"Loop {unique_var} is the outermost loop in OpenMP block")
                        else:
                            level = 1
                            print(f"Loop {unique_var} is an inner loop in OpenMP block")
                        break
            else:
                # Non-OpenMP: Use traditional method to detect nesting
                for prev_match in loops_found[:i]:
                    prev_start = prev_match.start()
                    prev_var = prev_match.group(1)
                    prev_unique = f"{prev_var}_b{block_idx}"
                    
                    # Determine previous loop's range
                    body_text = code_block[prev_start:]
                    open_braces = 0
                    close_pos = -1
                    
                    # Find the end of the loop header
                    header_end = -1
                    open_parens = 0
                    for pos, char in enumerate(body_text):
                        if char == '(':
                            open_parens += 1
                        elif char == ')':
                            open_parens -= 1
                            if open_parens == 0:
                                header_end = pos + 1
                                break
                    
                    if header_end == -1:
                        continue
                        
                    # Find the loop body range
                    pos = header_end
                    while pos < len(body_text) and body_text[pos] in ' \t\n':
                        pos += 1
                        
                    if pos < len(body_text) and body_text[pos] == '{':
                        # Loop body with braces
                        open_braces = 1
                        for p in range(pos + 1, len(body_text)):
                            if body_text[p] == '{':
                                open_braces += 1
                            elif body_text[p] == '}':
                                open_braces -= 1
                                if open_braces == 0:
                                    close_pos = prev_start + p
                                    break
                    else:
                        # Single statement loop body
                        for p in range(pos, len(body_text)):
                            if body_text[p] == ';':
                                close_pos = prev_start + p
                                break
                    
                    # If current loop is within the range of a previous loop, it's nested
                    if close_pos != -1 and prev_start < loop_start < close_pos:
                        prev_level = loop_levels.get(prev_unique, 0)
                        level = max(level, prev_level + 1)
                        print(f"Loop {unique_var} is nested inside {prev_unique}")
            
            loop_levels[unique_var] = level
            loop_info['loop_levels'][unique_var] = level
            
            # Record loop information
            loop_info['loops'].append({
                'var': unique_var,         # Variable name with block identifier
                'orig_var': var,           # Original variable name
                'block_idx': block_idx,    # Code block index
                'start': start,
                'op': op,
                'end': end, 
                'increment': increment,
                'level': level,
                'size': loop_sizes.get(unique_var),
                'bound_name': loop_info['loop_vars_to_bounds'].get(unique_var, "")
            })
            
            # Add to various loop variable lists
            loop_info['loop_vars'].append(unique_var)
            loop_info['raw_loop_vars'].append(var)
            block_info['loop_vars'].append(unique_var)
        
        # Store loop variables for this block
        loop_info['block_to_vars'][block_idx] = block_info['loop_vars']
        
        # Extract statements
        # 提取循环声明
        loop_pattern = r'for\s*\(\s*(?:int|long|float|double)?\s*(\w+)\s*=\s*([^;]+);\s*[^;]*;\s*[^\)]*\)'
        loops = re.findall(loop_pattern, code_block)

        # 排除循环声明后提取赋值语句
        # 首先去除所有循环头
        cleaned_code = re.sub(r'for\s*\([^)]*\)', '', code_block)
        # 然后提取赋值语句
        statement_pattern = r'(\w+(?:\[\w+\])*)\s*(\+=|=|\*=|\/=)\s*([^;]+);'
        all_statements = []

        # 查找所有匹配项
        for match in re.finditer(statement_pattern, code_block):
            lhs = match.group(1)
            op = match.group(2)
            rhs = match.group(3)
            all_statements.append((lhs, op, rhs))

        print(f"All extracted statements in block {block_idx}: {len(all_statements)}")
        for i, (lhs, op, rhs) in enumerate(all_statements):
            print(f"  Statement {i}: {lhs} {op} {rhs}")

        # 过滤包含数组访问的语句
        statements = []
        for lhs, op, rhs in all_statements:
            # 检查左侧或右侧是否包含数组访问
            has_array = bool(re.search(r'\w+\[\w+\]', lhs + ' ' + rhs))
            print(f"  Checking '{lhs} {op} {rhs}': {'Has array access' if has_array else 'No array access'}")
            if has_array:
                # 转换回原始格式 (lhs, rhs)
                statements.append((lhs, rhs))

        print(f"Filtered statements with array access: {len(statements)}")
        
        block_info['statements'] = [lhs + " = " + rhs for lhs, rhs in statements]
        loop_info['statements'].extend(block_info['statements'])
        
        # Check if there are nested loops in this block
        if len(loop_levels) >= 2 and max(loop_levels.values()) > 0:
            block_info['has_nested_loops'] = True
            print(f"Block {block_idx} has nested loops (max level: {max(loop_levels.values())})")
        
        # Add block information to global information
        loop_info['blocks'].append(block_info)
    
    # Print summary information
    print("\n=== Loop Structure Analysis Summary ===")
    print(f"Total loops found: {len(loop_info['loops'])}")
    print(f"Unique loop variables (with block identifiers): {loop_info['loop_vars']}")
    print(f"Original loop variables: {list(dict.fromkeys(loop_info['raw_loop_vars']))}")
    
    # Block information
    print("\nBlock information:")
    for i, block in enumerate(loop_info['blocks']):
        num_loops = block.get('loops', 0)
        has_nested = "with nested loops" if block.get('has_nested_loops', False) else "with sequential loops"
        print(f"Block {i}: {num_loops} loops {has_nested}, {len(block.get('statements', []))} statements")
        print(f"  Loop variables: {block.get('loop_vars', [])}")
    
    return loop_info

def analyze_array_accesses(code_blocks, latencies, data_type, loop_info):
    """
    分析计算语句中的数组访问模式和操作符号，并计算每个语句的成本
    考虑全局数组访问历史，提高缓存访问延迟计算的准确性
    适配多循环块的结构
    """
    # 初始化全局数组写入集合
    global_arrays_written = set()
        
    access_info = {
        'arrays': {},  # 数组名 -> {'reads': 计数, 'writes': 计数}
        'operations': {
            'add': 0,
            'mul': 0,
            'other': 0,
            'total': 0
        },
        'statements': [],  # 存储每条语句的详细信息
        'global_arrays_written': global_arrays_written.copy(),  # 复制当前全局状态
        'blocks_info': []  # 每个块的独立分析信息
    }
    
    # 使用正确的延迟值
    if data_type == 'double':
        add_latency = latencies['T_add_double']
        mul_latency = latencies['T_mul_double']
    else:
        add_latency = latencies['T_add_float']
        mul_latency = latencies['T_mul_float']
    
    # 处理所有代码块
    block_id = 0
    stmt_id = 0
    
    # 如果传入的是单个代码块，转换为列表
    if isinstance(code_blocks, str):
        code_blocks = [code_blocks]
    
    # 获取循环块信息
    blocks = loop_info.get('blocks', [])
    if not blocks and code_blocks:
        # 如果loop_info中没有blocks信息，将code_blocks转换为简单的块结构
        blocks = [{'code': block, 'block_idx': i} for i, block in enumerate(code_blocks)]
    
    # 处理每个代码块
    for block in blocks:
        block_idx = block.get('block_idx', block_id)
        code_block = block.get('code', '')
        
        print(f"\n==== Analyzing Array Access for Block {block_idx} ====")
        
        block_access_info = {
            'arrays': {},  # 数组名 -> {'reads': 计数, 'writes': 计数}
            'operations': {
                'add': 0,
                'mul': 0,
                'other': 0,
                'total': 0
            },
            'statements': [],  # 存储每条语句的详细信息
            'block_idx': block_idx,  # 记录这个分析属于哪个代码块
            'raw_code': code_block  # 保存原始代码以便后续分析
        }
        
        # 提取所有赋值语句
        # 首先去除所有循环头
        cleaned_code = re.sub(r'for\s*\([^)]*\)', '', code_block)
        # 然后提取赋值语句
        statement_pattern = r'(\w+(?:\[\w+\])*)\s*(\+=|=|\*=|\/=)\s*([^;]+);'
        all_statements = []

        # 查找所有匹配项
        for match in re.finditer(statement_pattern, cleaned_code):
            lhs = match.group(1)
            op = match.group(2)
            rhs = match.group(3)
            all_statements.append((lhs, op, rhs))

        # 过滤包含数组访问的语句
        statements = []
        for lhs, op, rhs in all_statements:
            # 检查左侧或右侧是否包含数组访问
            has_array = bool(re.search(r'\w+\[\w+\]', lhs + ' ' + rhs))
            if has_array:
                statements.append((lhs, op, rhs))

        # 处理每条语句
        for idx, (lhs, op, rhs) in enumerate(statements):
            stmt_info = {
                'id': stmt_id,
                'local_id': idx,
                'block_idx': block_idx,
                'lhs': lhs,
                'op': op,
                'rhs': rhs,
                'arrays_read': [],
                'arrays_written': [],
                'l1_accesses': 0,
                'l2_accesses': 0,
                'add_ops': 0,
                'mul_ops': 0,
                'div_ops': 0,
                'cost': 0.0,
                'in_loops': set(),
                'loop_vars': []
            }

            # 首先识别左侧（写入的数组）
            lhs_array = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', lhs).group(1)

            # 检查是否真的是数组访问 (有索引)
            is_array_access = bool(re.search(r'\[\w+\]', lhs))

            if is_array_access:
                # 如果是数组访问，记录为写入数组
                if lhs_array not in access_info['arrays']:
                    access_info['arrays'][lhs_array] = {'reads': 0, 'writes': 0}
                if lhs_array not in block_access_info['arrays']:
                    block_access_info['arrays'][lhs_array] = {'reads': 0, 'writes': 0}
                    
                access_info['arrays'][lhs_array]['writes'] += 1
                block_access_info['arrays'][lhs_array]['writes'] += 1
                stmt_info['arrays_written'].append(lhs_array)
            
            # 如果是 += 或 *= 操作，左侧数组也被读取
            if op in ('+=', '*=', '/='):
                if is_array_access:  # 只有当左侧是数组时才计数为读取
                    access_info['arrays'][lhs_array]['reads'] += 1
                    block_access_info['arrays'][lhs_array]['reads'] += 1
                    stmt_info['arrays_read'].append(lhs_array)
                # 这些操作还隐含一个相应的操作
                if op == '+=':
                    stmt_info['add_ops'] += 1
                    access_info['operations']['add'] += 1
                    block_access_info['operations']['add'] += 1
                elif op == '*=':
                    stmt_info['mul_ops'] += 1
                    access_info['operations']['mul'] += 1
                    block_access_info['operations']['mul'] += 1
                elif op == '/=':
                    stmt_info['div_ops'] += 1
                    access_info['operations']['other'] += 1
                    block_access_info['operations']['other'] += 1
            
            # 处理右侧（读操作）
            rhs_arrays = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*\[', rhs)
            for array in rhs_arrays:
                if array not in access_info['arrays']:
                    access_info['arrays'][array] = {'reads': 0, 'writes': 0}
                if array not in block_access_info['arrays']:
                    block_access_info['arrays'][array] = {'reads': 0, 'writes': 0}
                    
                access_info['arrays'][array]['reads'] += 1
                block_access_info['arrays'][array]['reads'] += 1
                if array not in stmt_info['arrays_read']:
                    stmt_info['arrays_read'].append(array)
            
            # 创建一个没有数组索引表达式的干净版本的RHS
            clean_rhs = re.sub(r'\[[^\]]+\]', '[]', rhs)
            
            # 解析出实际的操作符
            # 对于 '+' 和 '-'，我们只计算操作符，而不是数组索引中的表达式
            add_ops = len(re.findall(r'(?<!\[)[+\-](?!\])', clean_rhs))
            mul_ops = clean_rhs.count('*')
            div_ops = clean_rhs.count('/')
            
            stmt_info['add_ops'] += add_ops
            stmt_info['mul_ops'] += mul_ops
            stmt_info['div_ops'] += div_ops
            
            access_info['operations']['add'] += add_ops
            access_info['operations']['mul'] += mul_ops
            access_info['operations']['other'] += div_ops
            access_info['operations']['total'] += add_ops + mul_ops + div_ops
            
            block_access_info['operations']['add'] += add_ops
            block_access_info['operations']['mul'] += mul_ops
            block_access_info['operations']['other'] += div_ops
            block_access_info['operations']['total'] += add_ops + mul_ops + div_ops
            
            # 重置L1和L2计数器以确保正确计算
            l1_count = 0
            l2_count = 0
            
            print(f"  Before stmt {idx} in block {block_idx}, global_arrays_written = {global_arrays_written}")
            
            # 先处理右侧的数组（读取）
            for array in stmt_info['arrays_read']:
                # 特殊情况：如果数组在当前语句中既读又写
                if array in stmt_info['arrays_written']:
                    l2_count += 2  # 读+写操作都使用L2缓存
                    print(f"  Array {array} read+write in stmt {idx} of block {block_idx}: 2*L2 access (read-write in same statement)")
                # 如果已经在全局写入数组中
                elif array in global_arrays_written:
                    l2_count += 1  # 使用L2缓存访问
                    print(f"  Array {array} read in stmt {idx} of block {block_idx}: L2 access (previously written)")
                # 只读数组
                else:
                    l1_count += 1  # 使用L1缓存
                    print(f"  Array {array} read in stmt {idx} of block {block_idx}: L1 access (read-only array)")
            
            # 处理左侧的数组（写入），但不重复计算已经统计过的读+写数组
            for array in stmt_info['arrays_written']:
                if array not in stmt_info['arrays_read']:
                    l2_count += 1  # 只写操作使用L2缓存
                    print(f"  Array {array} write-only in stmt {idx} of block {block_idx}: L2 access")
                    
                # 更新全局写入数组集合
                global_arrays_written.add(array)
            
            # 最终设置该语句的L1/L2访问计数
            stmt_info['l1_accesses'] = l1_count
            stmt_info['l2_accesses'] = l2_count
            
            # 计算语句成本：缓存访问 + 计算操作
            stmt_info['cost'] = (
                l1_count * latencies['T_L1'] +
                l2_count * latencies['T_L2'] +
                stmt_info['add_ops'] * add_latency +
                stmt_info['mul_ops'] * mul_latency +
                stmt_info['div_ops'] * (mul_latency * 2)
            )
            
            print(f"  Stmt {idx} in block {block_idx} calculated cost: {stmt_info['cost']:.2f} ns with {l1_count} L1, {l2_count} L2")

            total_adds = add_ops + (1 if op == '+=' else 0)
            total_muls = mul_ops + (1 if op == '*=' else 0)
            total_divs = div_ops + (1 if op == '/=' else 0)
            print(f"  Operations: {total_adds} adds, {total_muls} muls, {total_divs} divs")
            
            # 添加到语句列表
            access_info['statements'].append(stmt_info)
            block_access_info['statements'].append(stmt_info)
            
            # 增加全局语句ID
            stmt_id += 1
        
        # 更新全局数组写入状态
        access_info['global_arrays_written'] = global_arrays_written.copy()
        block_access_info['global_arrays_written'] = global_arrays_written.copy()
        
        # 添加块的分析信息
        access_info['blocks_info'].append(block_access_info)
        
        # 打印分析结果
        print(f"Found {len(block_access_info['statements'])} computation statements in block {block_idx}")
        for array, counts in block_access_info['arrays'].items():
            reads = counts['reads']
            writes = counts['writes']
            # 使用全局数组写入历史来判断缓存类型
            cache_type = "L2" if array in global_arrays_written else "L1"
            print(f"Array {array} in block {block_idx}: {reads} reads, {writes} writes, global cache type: {cache_type}")
        
        print(f"Operations in block {block_idx}: {block_access_info['operations']['add']} adds, {block_access_info['operations']['mul']} muls, {block_access_info['operations']['other']} other ops")
        
        # 增加块ID计数器
        block_id += 1
    
    # 确定每个语句所在的循环
    print("\n=== Determining Loop Variables for Each Statement ===")
    
    # Get each block's loop variables
    block_to_vars = loop_info.get('block_to_vars', {})
    orig_to_unique = loop_info.get('orig_to_unique', {})
        
    # Process each statement to determine if it should be skipped for tiling
    # When determining if tiling should be skipped
    for stmt in access_info['statements']:
        block_idx = stmt['block_idx']
        block_vars = block_to_vars.get(block_idx, [])
            
        # Complete statement
        full_stmt = stmt['lhs'] + ' ' + stmt['op'] + ' ' + stmt['rhs']
            
        # Find loop variables used in the statement
        stmt_loop_vars = []
            
        # First check original loop variables like i, j, k
        for orig_var, unique_vars in orig_to_unique.items():
            if re.search(r'\b' + re.escape(orig_var) + r'\b', full_stmt):
                # Find variables belonging to the current block
                for unique_var in unique_vars:
                    if f"_b{block_idx}" in unique_var and unique_var in block_vars:
                        stmt_loop_vars.append(unique_var)
                        print(f"  Found loop variable {orig_var} (mapped to {unique_var}) in statement {stmt['id']} in block {block_idx}")
            
        # Store the loop variables found
        stmt['loop_vars'] = stmt_loop_vars
        
        # Change here: Check if any statement in this block has nested loops
        # If so, don't skip tiling for any statement in this block
        block_has_nested_loops = False
        max_level = 0
        for var in block_vars:
            level = loop_info.get('loop_levels', {}).get(var, 0)
            max_level = max(max_level, level)
        
        if max_level >= 1:  # If any loop in this block is nested
            block_has_nested_loops = True
            
        # Determine if tiling should be skipped based on loop context
        if block_has_nested_loops:
            # Don't skip tiling for any statement in blocks with nested loops
            stmt['skip_tiling'] = False
            print(f"Statement {stmt['id']} in block {block_idx}: Block contains nested loops - Consider for tiling")
        elif len(stmt_loop_vars) <= 1:
            # Only skip if not in block with nested loops AND in single/no loop
            is_outermost = True
            for var in stmt_loop_vars:
                level = loop_info.get('loop_levels', {}).get(var, 0)
                if level > 0:
                    is_outermost = False
                    break
                
            if len(stmt_loop_vars) == 0 or (len(stmt_loop_vars) == 1 and is_outermost):
                stmt['skip_tiling'] = True
                print(f"Statement {stmt['id']} in block {block_idx}: {'Not in any loop' if not stmt_loop_vars else 'In single outermost loop'} - SKIP TILING")
            else:
                stmt['skip_tiling'] = False
                print(f"Statement {stmt['id']} in block {block_idx}: In single nested loop - Consider for tiling")
        else:
            stmt['skip_tiling'] = False
            print(f"Statement {stmt['id']} in block {block_idx}: In {len(stmt_loop_vars)} loops - Consider for tiling")
            
        # Print the loop variables for this statement
        print(f"  Loop variables for statement {stmt['id']} in block {block_idx}: {', '.join(stmt_loop_vars)}")

    # Create a mapping from arrays to the statements that use them
    array_to_statements = {}
    for stmt in access_info['statements']:
        # Collect all arrays used in this statement
        arrays_used = list(set(stmt['arrays_read'] + stmt['arrays_written']))
        for array in arrays_used:
            if array not in array_to_statements:
                array_to_statements[array] = []
            array_to_statements[array].append(stmt)

    # Categorize arrays based on the statements they appear in
    single_loop_only_arrays = set()
    multi_loop_arrays = set()

    print("\n=== Categorizing Arrays for Tiling ===")
    for array, stmts in array_to_statements.items():
        # Check if the array is used ONLY in statements that should be skipped
        only_in_skip_stmts = True
        for stmt in stmts:
            if not stmt.get('skip_tiling', False):
                only_in_skip_stmts = False
                break
        
        if only_in_skip_stmts:
            single_loop_only_arrays.add(array)
            print(f"Array {array} is used ONLY in statements to be skipped (single loop or no loop)")
        else:
            multi_loop_arrays.add(array)
            print(f"Array {array} is used in multi-loop statements - will generate constraints")

    # Add to access_info
    access_info['single_loop_arrays'] = single_loop_only_arrays
    access_info['multi_loop_arrays'] = multi_loop_arrays

    print(f"\nArrays used ONLY in single/no loop contexts (will skip constraints): {single_loop_only_arrays}")
    print(f"Arrays used in multi-loop statements (will generate constraints): {multi_loop_arrays}")
    
    return access_info

def generate_objective_function(loop_info, access_info, matrix_info):
    """
    基于循环结构和语句分析生成动态的ILP目标函数
    使用循环变量名称作为分块名称
    处理多循环块结构，每个块单独生成目标函数
    """
    print("\n=== Generating Improved Objective Function ===")
    
    # 获取所有语句
    statements = access_info['statements']
    
    # 按块来组织目标函数
    block_cost_terms = {}  # block_idx -> 成本项列表
    
    # 获取块到变量的映射
    block_to_vars = loop_info.get('block_to_vars', {})
    
    # 处理每个语句
    for stmt in statements:
        # 获取语句所在的块
        block_idx = stmt.get('block_idx', 0)
        
        # 确保块索引存在于映射中
        if block_idx not in block_cost_terms:
            block_cost_terms[block_idx] = []
        
        # 检查是否应该跳过单层循环语句
        if stmt.get('skip_tiling', False):
            print(f"Skipping Statement {stmt['id']} for objective function (single loop or no loop)")
            continue
        
        # 获取语句的循环变量
        stmt_loop_vars = stmt.get('loop_vars', [])
        
        # 如果变量列表为空，尝试确定
        if not stmt_loop_vars:
            # 获取该块所有的变量
            block_loop_vars = block_to_vars.get(block_idx, [])
            
            # 获取语句文本
            lhs = stmt.get('lhs', '')
            rhs = stmt.get('rhs', '')
            full_stmt = lhs + ' ' + rhs
            
            # 检查文本中是否包含变量
            for var in block_loop_vars:
                # 获取原始变量名
                orig_var = var.split('_b')[0] if '_b' in var else var
                
                # 检查变量是否在语句中
                if re.search(r'\b' + re.escape(orig_var) + r'\b', full_stmt):
                    stmt_loop_vars.append(var)
                    print(f"Found loop variable {orig_var} (mapped to {var}) in statement {stmt['id']}")
        
        # 转换循环变量到对应的分块因子和tile大小因子
        block_factors = []  # 块数因子
        tile_factors = []   # tile大小因子
        
        for var in stmt_loop_vars:
            # 确保我们只使用当前块的循环变量
            if f"_b{block_idx}" in var:
                # 检查变量是否可平铺
                block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                is_tileable = var in block_tileable_status and block_tileable_status[var]
                
                if is_tileable:
                    block_factors.append(f"{var}_blocks")
                    tile_factors.append(f"{var}_tile")
                    print(f"Variable {var} in statement {stmt['id']} is TILEABLE - adding both block and tile factors")
                else:
                    # 对于不可平铺的维度，tile大小固定为1，块数等于原始循环大小
                    loop_size = loop_info.get('loop_sizes', {}).get(var, 1)
                    print(f"Variable {var} in statement {stmt['id']} is NOT TILEABLE - using original loop size {loop_size} as block count")
                    # 添加原始循环大小作为执行因子
                    block_factors.append(str(loop_size))
                    # 无需添加tile因子，因为tile大小固定为1
        
        # 如果没有找到任何执行因子，默认为一次执行
        if not block_factors:
            block_factors = ['1']
        
        # 构建这个语句的成本项
        cost = stmt.get('cost', 0)
        blocks_expr = ' * '.join(block_factors)
        
        # 添加tile因子
        if tile_factors:
            tile_expr = ' * '.join(tile_factors)
            cost_term = f"{blocks_expr} * {tile_expr} * {cost:.2f}"
            print(f"Statement {stmt['id']} in block {block_idx}: Cost {cost:.2f} ns, Block factors: {block_factors}, Tile factors: {tile_factors}")
        else:
            # 如果没有tile因子，只使用block因子
            cost_term = f"{blocks_expr} * {cost:.2f}"
            print(f"Statement {stmt['id']} in block {block_idx}: Cost {cost:.2f} ns, Block factors: {block_factors}, No tile factors")
        
        block_cost_terms[block_idx].append(cost_term)
    
    # 为每个块生成单独的目标函数
    block_objective_functions = {}
    
    for block_idx, cost_terms in block_cost_terms.items():
        # 尝试进行代数简化 (合并同类项)
        try:
            # 查找所有相同执行因子的项
            factor_groups = {}
            for term in cost_terms:
                parts = term.split(' * ')
                if len(parts) > 1:
                    cost = float(parts[-1])
                    factor = ' * '.join(parts[:-1])
                    
                    if factor not in factor_groups:
                        factor_groups[factor] = 0
                    factor_groups[factor] += cost
            
            # 如果有多个项具有相同的执行因子，合并它们
            if factor_groups:
                simplified_terms = []
                for factor, total_cost in factor_groups.items():
                    simplified_terms.append(f"{factor} * {total_cost:.2f}")
                
                # 如果有简化，使用简化后的表达式
                if simplified_terms:
                    block_obj_function = " + ".join(simplified_terms)
                    block_objective_functions[block_idx] = block_obj_function
                    print(f"Block {block_idx} objective function (simplified): {block_obj_function}")
                    continue
        except Exception as e:
            print(f"Error simplifying objective function for block {block_idx}: {e}")
        
        # 如果没有有效的成本项或简化失败，使用默认形式
        if cost_terms:
            block_obj_function = " + ".join(cost_terms)
        else:
            # 获取这个块的循环变量
            block_vars = block_to_vars.get(block_idx, [])
            
            if len(block_vars) >= 2:
                # 使用前两个循环变量的块数和tile大小
                var0 = block_vars[0]
                var1 = block_vars[1]
                
                # 检查变量是否可平铺
                block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                var0_tileable = var0 in block_tileable_status and block_tileable_status[var0]
                var1_tileable = var1 in block_tileable_status and block_tileable_status[var1]
                
                block_factors = []
                tile_factors = []
                
                if var0_tileable:
                    block_factors.append(f"{var0}_blocks")
                    tile_factors.append(f"{var0}_tile")
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var0, 1)
                    block_factors.append(str(loop_size))
                
                if var1_tileable:
                    block_factors.append(f"{var1}_blocks")
                    tile_factors.append(f"{var1}_tile")
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var1, 1)
                    block_factors.append(str(loop_size))
                
                blocks_expr = ' * '.join(block_factors)
                if tile_factors:
                    tile_expr = ' * '.join(tile_factors)
                    block_obj_function = f"{blocks_expr} * {tile_expr} * T_op1"
                else:
                    block_obj_function = f"{blocks_expr} * T_op1"
            elif len(block_vars) == 1:
                # 只有一个循环变量
                var = block_vars[0]
                
                # 检查变量是否可平铺
                block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                is_tileable = var in block_tileable_status and block_tileable_status[var]
                
                if is_tileable:
                    block_obj_function = f"{var}_blocks * {var}_tile * T_op1"
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var, 1)
                    block_obj_function = f"{loop_size} * T_op1"
            else:
                # 没有循环变量
                block_obj_function = "T_op1"
        
        block_objective_functions[block_idx] = block_obj_function
        print(f"Block {block_idx} objective function: {block_obj_function}")
    
    # 首先，对每个块的目标函数单独应用优化
    optimized_block_functions = {}
    for block_idx, func in block_objective_functions.items():
        # 对块内的目标函数应用优化
        optimized_func = optimize_objective_function(func)
        optimized_block_functions[block_idx] = optimized_func
        print(f"Optimized Block {block_idx} objective function: {optimized_func}")
    
    # 合并所有块的优化后的目标函数
    if optimized_block_functions:
        # 创建一个完整的目标函数
        all_terms = []
        for block_idx, func in optimized_block_functions.items():
            # 用括号包围每个块的目标函数，避免运算符优先级问题
            all_terms.append(f"({func})")
        
        combined_objective_function = " + ".join(all_terms)
        print(f"Combined objective function: {combined_objective_function}")
        
        # 保存每个块的单独目标函数和优化后的目标函数，以便后续处理
        return combined_objective_function, optimized_block_functions
    else:
        # 如果没有有效的成本项，使用默认形式
        print("No valid cost terms found, using default objective function")
        
        # 尝试从各个块构建默认的目标函数
        default_blocks = {}
        
        for block_idx, vars_list in block_to_vars.items():
            if len(vars_list) >= 2:
                # 使用前两个循环变量
                var0 = vars_list[0]
                var1 = vars_list[1]
                
                # 检查变量是否可平铺
                block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                var0_tileable = var0 in block_tileable_status and block_tileable_status[var0]
                var1_tileable = var1 in block_tileable_status and block_tileable_status[var1]
                
                block_factors = []
                tile_factors = []
                
                if var0_tileable:
                    block_factors.append(f"{var0}_blocks")
                    tile_factors.append(f"{var0}_tile")
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var0, 1)
                    block_factors.append(str(loop_size))
                
                if var1_tileable:
                    block_factors.append(f"{var1}_blocks")
                    tile_factors.append(f"{var1}_tile")
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var1, 1)
                    block_factors.append(str(loop_size))
                
                blocks_expr = ' * '.join(block_factors)
                if tile_factors:
                    tile_expr = ' * '.join(tile_factors)
                    default_blocks[block_idx] = f"{blocks_expr} * {tile_expr} * T_op1"
                else:
                    default_blocks[block_idx] = f"{blocks_expr} * T_op1"
            elif len(vars_list) == 1:
                # 只有一个循环变量
                var = vars_list[0]
                
                # 检查变量是否可平铺
                block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                is_tileable = var in block_tileable_status and block_tileable_status[var]
                
                if is_tileable:
                    default_blocks[block_idx] = f"{var}_blocks * {var}_tile * T_op1"
                else:
                    loop_size = loop_info.get('loop_sizes', {}).get(var, 1)
                    default_blocks[block_idx] = f"{loop_size} * T_op1"
            else:
                # 没有循环变量
                default_blocks[block_idx] = "T_op1"
        
        # 优化每个默认块的目标函数，然后再合并
        optimized_default_blocks = {}
        for block_idx, func in default_blocks.items():
            optimized_func = optimize_objective_function(func)
            optimized_default_blocks[block_idx] = optimized_func
        
        # 合并所有默认块的目标函数
        if optimized_default_blocks:
            combined_default = " + ".join([f"({func})" for func in optimized_default_blocks.values()])
            print(f"Combined default objective function: {combined_default}")
            return combined_default, optimized_default_blocks
        else:
            # 真的没有任何可用信息，使用最基本的默认函数
            print("Using basic default objective function: T_op1")
            return "T_op1", {"0": "T_op1"}


def optimize_objective_function(objective_function):
    """
    优化目标函数，消去公共的tile因子
    如果某个tile变量在所有项中都出现，我们可以将其设为1（即消去）
    """
    print("\n=== Optimizing Objective Function ===")
    print(f"Input objective function: {objective_function}")
    
    # If there's no + sign, treat it as a single term
    if not objective_function:
        print("Empty objective function, nothing to optimize")
        return objective_function
    
    # Process single term (no + sign) case
    if '+' not in objective_function:
        print("Processing single term expression")
        # Extract all variables from the single term
        all_variables = set()
        for factor in objective_function.split('*'):
            factor = factor.strip()
            # Only include variable names, not numeric constants
            if factor and not factor.replace('.', '').isdigit():
                all_variables.add(factor)
        
        # Find tile variables
        tile_vars = {var for var in all_variables if '_tile' in var}
        
        if tile_vars:
            print(f"Found tile variables in single term: {tile_vars}")
            # Remove tile variables from expression
            for var in tile_vars:
                # Replace the variable and surrounding operators
                objective_function = re.sub(r'\s*\*\s*' + re.escape(var) + r'\s*\*\s*', ' * ', objective_function)
                # Handle beginning of expression
                objective_function = re.sub(r'^' + re.escape(var) + r'\s*\*\s*', '', objective_function)
                # Handle end of expression
                objective_function = re.sub(r'\s*\*\s*' + re.escape(var) + r'$', '', objective_function)
                # Handle case where variable is the entire expression
                objective_function = re.sub(r'^' + re.escape(var) + r'$', '1', objective_function)
            
            # Clean up
            objective_function = re.sub(r'\s+\*\s+', ' * ', objective_function)
            objective_function = re.sub(r'\s+', ' ', objective_function)
            
            print(f"Optimized single term expression: {objective_function}")
        else:
            print("No tile variables found in single term")
        
        return objective_function
    
    # 将目标函数字符串分割成各个项
    if '(' in objective_function:
        # 如果有括号，需要特殊处理
        terms_with_brackets = objective_function.split(') + (')
        terms = []
        for term in terms_with_brackets:
            # 去除前后的括号
            term = term.strip('()')
            terms.append(term)
    else:
        # 简单情况，直接按+分割
        terms = [term.strip() for term in objective_function.split('+')]
    
    # 提取每个项中的所有变量
    all_vars_in_terms = []
    for term in terms:
        # 分割乘法表达式
        vars_in_term = set()
        for factor in term.split('*'):
            factor = factor.strip()
            # 只保留变量名，不包括数字常量
            if factor and not factor.replace('.', '').isdigit():
                vars_in_term.add(factor)
        all_vars_in_terms.append(vars_in_term)
    
    # 找出所有项中共有的tile变量
    if not all_vars_in_terms:
        print("No terms found in objective function")
        return objective_function
    
    common_vars = set.intersection(*all_vars_in_terms) if all_vars_in_terms else set()
    common_tile_vars = {var for var in common_vars if '_tile' in var}
    
    if common_tile_vars:
        print(f"Found common tile variables in all terms: {common_tile_vars}")
        
        # 从目标函数中移除这些共同的tile变量
        for var in common_tile_vars:
            # 使用正则表达式替换变量及其前后的乘号
            objective_function = re.sub(r'\s*\*\s*' + re.escape(var) + r'\s*\*\s*', ' * ', objective_function)
            # 处理变量在表达式开头的情况
            objective_function = re.sub(r'^' + re.escape(var) + r'\s*\*\s*', '', objective_function)
            # 处理变量在表达式结尾的情况
            objective_function = re.sub(r'\s*\*\s*' + re.escape(var) + r'$', '', objective_function)
            # 处理变量是表达式中唯一因子的情况
            objective_function = re.sub(r'^' + re.escape(var) + r'$', '1', objective_function)
        
        # 清理多余的空格和星号
        objective_function = re.sub(r'\s+\*\s+', ' * ', objective_function)
        objective_function = re.sub(r'\s+', ' ', objective_function)
        
        print(f"Optimized objective function: {objective_function}")
    else:
        print("No common tile variables found across all terms")
    
    return objective_function

def extract_used_dimensions(code_block):
    """
    从代码块中提取实际使用的维度
    返回一个包含使用的维度的集合
    """
    used_dims = set()
    
    # 检查代码中使用的PB维度
    pb_pattern = r'_PB_(\w+)'
    for match in re.findall(pb_pattern, code_block):
        if match in ['N', 'NJ']:
            used_dims.add('N')
        elif match in ['M', 'NI']:
            used_dims.add('M')
        elif match in ['K', 'NK']:
            used_dims.add('K')
    
    # 如果没有找到PB维度，尝试查找循环变量
    if not used_dims:
        loop_pattern = r'for\s*\(\s*(\w+)\s*=.*?;\s*\1\s*<.*?;\s*\1.*?\)'
        loop_vars = re.findall(loop_pattern, code_block)
        
        # 根据循环变量名推断维度
        for var in loop_vars:
            if var == 'i':
                used_dims.add('M')
            elif var == 'j':
                used_dims.add('N')
            elif var == 'k':
                used_dims.add('K')
    
    print(f"Extracted used dimensions from code: {used_dims}")
    return used_dims

def extract_dimensions_from_header(header_file, loop_info=None):
    """
    从头文件中提取维度大小，同时可以使用loop_info中的上界信息
    返回一个包含各维度大小的字典
    """
    dimensions = {}  # 存储所有维度的大小
    
    try:
        with open(header_file, 'r') as f:
            content = f.read()
        
        print("Analyzing header file to extract dimension information")
        
        # 获取需要查找的维度名称
        search_dims = []
        if loop_info and 'loop_vars_to_bounds' in loop_info:
            # 从循环信息中提取需要搜索的维度名称
            search_dims = list(set(loop_info['loop_vars_to_bounds'].values()))
            print(f"Looking for dimensions in header: {search_dims}")
        
        # 确定使用的数据集大小
        dataset_size = "LARGE_DATASET"  # 默认数据集大小
        for size in ["MINI_DATASET", "SMALL_DATASET", "MEDIUM_DATASET", "LARGE_DATASET", "EXTRALARGE_DATASET"]:
            if f"#  define {size}" in content and f"#ifndef {size}" not in content:
                dataset_size = size
                print(f"Detected use of {dataset_size}")
                break
        
        # 查找指定数据集下的维度定义
        dataset_section = ""
        sections = content.split("#  ifdef")
        for section in sections:
            if section.strip().startswith(dataset_size):
                dataset_section = section
                break
        
        # 搜索指定的维度
        for dim_name in search_dims:
            # 在数据集部分或整个文件中搜索维度定义
            pattern = r'#\s*define\s+(_PB_)?' + dim_name + r'\s+(\d+)'
            if dataset_section:
                match = re.search(pattern, dataset_section)
            else:
                match = re.search(pattern, content)
            
            if match:
                value = int(match.group(2))
                dimensions[dim_name] = value
                print(f"Found dimension {dim_name} in header: {value}")
            else:
                # 尝试查找没有_PB_前缀的版本
                pattern = r'#\s*define\s+' + dim_name + r'\s+(\d+)'
                if dataset_section:
                    match = re.search(pattern, dataset_section)
                else:
                    match = re.search(pattern, content)
                
                if match:
                    value = int(match.group(1))
                    dimensions[dim_name] = value
                    print(f"Found dimension {dim_name} (no prefix) in header: {value}")
        
    except Exception as e:
        print(f"Error extracting dimensions from header file: {e}")
    
    return dimensions


def parse_matrix_info(source_file):
    """
    从源代码中提取矩阵维度和数据类型信息
    返回一个包含矩阵信息的字典，使用循环变量名称作为键
    """
    matrix_info = {
        'data_type': 'double',  # 默认数据类型
        'data_size': 8,         # 默认数据大小 (bytes)
        'dimensions': {}        # 各维度的大小
    }
    
    try:
        # 提取计算核心代码
        comp_code = extract_computation_code(source_file)
        loop_info = None
        
        if comp_code:
            # 分析循环结构，使用循环变量名称作为分块命名基础
            loop_info = analyze_loop_structure(comp_code)
            
            # 保存循环信息供后续处理
            matrix_info['loop_info'] = loop_info
            
            # 提取各个循环变量及其对应的维度上界
            loop_vars = loop_info.get('loop_vars', [])
            loop_vars_to_bounds = loop_info.get('loop_vars_to_bounds', {})
            loop_var_to_size = loop_info.get('loop_var_to_size', {})
            # 在返回循环变量之前，确保去重
            if 'loop_vars' in loop_info:
                # 保持原始顺序的去重
                seen = set()
                loop_info['loop_vars'] = [var for var in loop_info['loop_vars'] if not (var in seen or seen.add(var))]
                print(f"去重后的循环变量列表: {loop_info['loop_vars']}")
            
            # 从头文件中提取维度大小
            header_file = find_header_file(source_file)
            if header_file:
                dimensions = extract_dimensions_from_header(header_file, loop_info)
                
                # 将维度大小添加到matrix_info
                matrix_info['dimensions'] = dimensions
                
                # 将循环变量映射到其实际维度大小
                var_to_size = {}
                for var, bound in loop_vars_to_bounds.items():
                    if bound in dimensions:
                        # 使用头文件中的值
                        var_to_size[var] = dimensions[bound]
                    elif var in loop_var_to_size:
                        # 使用从循环结构计算出的值
                        var_to_size[var] = loop_var_to_size[var]
                    else:
                        # 尝试从上界计算尺寸
                        try:
                            var_to_size[var] = int(bound) + 1  # 假设是 <= 比较
                        except ValueError:
                            # 无法解析的情况，跳过
                            pass
                
                matrix_info['var_to_size'] = var_to_size
                print(f"循环变量到维度大小映射: {var_to_size}")
            else:
                # 如果没有找到头文件，使用从循环结构计算的值
                matrix_info['var_to_size'] = loop_var_to_size
                print(f"使用循环结构计算的维度大小: {loop_var_to_size}")
            
            # 将循环变量到尺寸的映射添加到matrix_info
            matrix_info['loop_var_to_size'] = loop_var_to_size
            
        # 检测数据类型
        data_type, data_size = detect_data_type(source_file)
        matrix_info['data_type'] = data_type
        matrix_info['data_size'] = data_size
        
        # 获取物理核心数
        matrix_info['num_threads'] = get_physical_cores()
        print(f"Calculated physical cores: {matrix_info['num_threads']}")
        
    except Exception as e:
        print(f"Error parsing matrix information: {e}")
    
    return matrix_info

def analyze_array_dimensions(access_info, loop_info):
    """
    Analyze each array's dimension usage patterns and return cache constraint expressions
    Consider global array access history, but process dimensions by block
    """
    print("\n=== Array Dimensions Analysis ===")
    
    # Get global array write information
    global_arrays_written = access_info.get('global_arrays_written', set())
    
    # Get single-loop and multi-loop arrays
    single_loop_arrays = access_info.get('single_loop_arrays', set())
    multi_loop_arrays = access_info.get('multi_loop_arrays', set())
    
    # Get original to unique variable mapping
    orig_to_unique = loop_info.get('orig_to_unique', {})
    
    # All arrays dimension information - stored by block
    block_array_dimensions = {}  # block_idx -> {array_name -> set of dimension tuples}
    block_array_access_patterns = {}  # block_idx -> {array_name -> list of access pattern tuples}
    array_types = {}  # array_name -> 'read_only' or 'read_write'
    
    # Analyze array accesses in each block
    for block_info in access_info.get('blocks_info', []):
        block_idx = block_info.get('block_idx', 0)
        code_block = block_info.get('raw_code', '')
        
        print(f"\nAnalyzing dimensions for arrays in block {block_idx}")
        
        # Initialize block dimension dictionary
        if block_idx not in block_array_dimensions:
            block_array_dimensions[block_idx] = {}
        
        if block_idx not in block_array_access_patterns:
            block_array_access_patterns[block_idx] = {}
        
        # Get loop variables for this block
        block_vars = loop_info.get('block_to_vars', {}).get(block_idx, [])
        
        # Improved regex to capture multi-dimensional array access
        # This matches pattern like: array[idx1][idx2][idx3]...
        array_access_pattern = r'(\w+)(\s*\[\s*([^\]]+)\s*\])+' 
        
        # Find all array accesses 
        for match in re.finditer(array_access_pattern, code_block):
            full_match = match.group(0)
            array_name = match.group(1)
            
            # Skip single-loop arrays when needed
            if array_name in single_loop_arrays:
                print(f"  Array {array_name} is used only in single-loop contexts - will track dimensions but not generate constraints")
            
            # Initialize array entries in dictionaries
            if array_name not in block_array_dimensions[block_idx]:
                block_array_dimensions[block_idx][array_name] = set()
            
            if array_name not in block_array_access_patterns[block_idx]:
                block_array_access_patterns[block_idx][array_name] = []
            
            # Extract all indices from this array access
            indices = re.findall(r'\[\s*([^\]]+)\s*\]', full_match)
            
            # Create access pattern as a tuple of dimensions used
            access_pattern_vars = []
            
            # For each index expression, find which loop variables it uses
            for idx_expr in indices:
                idx_vars = []  # Variables used in this specific index
                
                for var in block_vars:
                    # Get original variable name
                    orig_var = var.split('_b')[0] if '_b' in var else var
                    
                    # Check if variable appears in this index expression
                    if re.search(r'\b' + re.escape(orig_var) + r'\b', idx_expr):
                        idx_vars.append(var)
                        print(f"  Found loop variable {orig_var} (mapped to {var}) in index expression '{idx_expr}' for array {array_name}")
                
                # Add variables for this index to the pattern
                # If no variables found, use None as placeholder
                if idx_vars:
                    access_pattern_vars.append(tuple(idx_vars))
                else:
                    access_pattern_vars.append((None,))
            
            # Store the full access pattern
            if access_pattern_vars:
                access_pattern = tuple(access_pattern_vars)
                block_array_access_patterns[block_idx][array_name].append(access_pattern)
                
                # Also store individual dimensions for backward compatibility
                for idx_vars in access_pattern_vars:
                    for var in idx_vars:
                        if var is not None:
                            block_array_dimensions[block_idx][array_name].add(var)
        
        # Analyze array read/write types
        for array, counts in block_info.get('arrays', {}).items():
            # Determine type based on global write history
            if array in global_arrays_written:
                array_types[array] = 'read_write'
                print(f"Array {array} in block {block_idx}: read/write - {counts['reads']} reads, {counts['writes']} writes (globally written)")
            else:
                array_types[array] = 'read_only'
                print(f"Array {array} in block {block_idx}: read-only - {counts['reads']} reads, {counts['writes']} writes")
    
    # Print final array dimension analysis
    print("\nFinal array dimensions analysis:")
    for block_idx, arrays in block_array_dimensions.items():
        for array, dims in arrays.items():
            dims_list = sorted(list(dims))  # Sort for consistency
            print(f"Array {array} in block {block_idx} uses dimensions: {', '.join(dims_list)}")
    
    # Print final array access patterns
    print("\nFinal array access patterns:")
    for block_idx, arrays in block_array_access_patterns.items():
        for array, patterns in arrays.items():
            print(f"Array {array} in block {block_idx} access patterns:")
            for pattern in patterns:
                # Properly format each access pattern as a single tuple with all dimensions
                flat_vars = []
                for idx_vars in pattern:
                    if isinstance(idx_vars, tuple) and idx_vars:
                        # Add only non-None variables from each index
                        flat_vars.extend([var for var in idx_vars if var is not None])
                
                # Print as a single tuple containing all dimensions
                pattern_str = "'" + "','".join(flat_vars) + "'"
                print(f"  ({pattern_str})")
    
    # Generate cache constraints by block
    block_constraints = {}
    all_read_only_exprs = []
    all_read_write_exprs = []
    expr_to_array = {}  # Track expression to array mapping
    
    for block_idx, arrays in block_array_access_patterns.items():
        read_only_exprs = []
        read_write_exprs = []
        
        print(f"\nGenerating constraints for block {block_idx}:")
        
        for array, patterns in arrays.items():
            # Skip arrays only used in single-loop contexts
            if array in single_loop_arrays:
                print(f"Skipping constraint generation for array {array} - used only in single-loop contexts")
                continue
            
            # Skip if no access patterns found
            if not patterns:
                print(f"No access patterns for array {array} in block {block_idx}, skipping")
                continue
            
            # Process each unique access pattern
            size_expressions = []

            for pattern in patterns:
                # Check if pattern has any non-tileable dimensions
                pattern_has_untileable = False
                untileable_dimensions = []
                
                # Flatten the pattern to get all variables
                all_vars = []
                for idx_tuple in pattern:
                    for var in idx_tuple:
                        if var is not None:
                            all_vars.append(var)
                
                # Check if any dimension is non-tileable
                for var in all_vars:
                    block_tileable_status = loop_info.get('block_tileable_dims', {}).get(block_idx, {})
                    is_tileable = var in block_tileable_status and block_tileable_status[var]
                    
                    if not is_tileable:
                        pattern_has_untileable = True
                        untileable_dimensions.append(var)
                        print(f"Dimension {var} in block {block_idx} for array {array} is NOT TILEABLE")
                
                # Skip this access pattern if it has non-tileable dimensions
                if pattern_has_untileable:
                    print(f"  Skipping access pattern with non-tileable dimensions: {untileable_dimensions}")
                    continue
                
                # Build size expression using only tileable dimensions
                pattern_factors = []
                
                # Process each index's variables
                for idx_vars in pattern:
                    idx_factors = []
                    
                    for var in idx_vars:
                        if var is not None:
                            # We already checked above that all dimensions are tileable
                            idx_factors.append(f"{var}_tile")
                    
                    # If factors for this index, multiply them
                    if idx_factors:
                        if len(idx_factors) > 1:
                            pattern_factors.append(" * ".join(idx_factors))
                        else:
                            pattern_factors.append(idx_factors[0])
                
                # Build complete expression for this pattern
                if pattern_factors:
                    pattern_expr = " * ".join(pattern_factors) + " * data_size"
                    size_expressions.append(pattern_expr)
            
            # Combine all patterns for this array
            if size_expressions:
                if len(size_expressions) > 1:
                    array_expr = "(" + " + ".join(size_expressions) + ")"
                else:
                    array_expr = size_expressions[0]
                
                # Classify based on array type
                if array in global_arrays_written:
                    read_write_exprs.append(array_expr)
                    all_read_write_exprs.append(array_expr)
                    expr_to_array[array_expr] = array
                    print(f"Added read/write constraint for {array} in block {block_idx}: {array_expr}")
                else:
                    read_only_exprs.append(array_expr)
                    all_read_only_exprs.append(array_expr)
                    expr_to_array[array_expr] = array
                    print(f"Added read-only constraint for {array} in block {block_idx}: {array_expr}")
        
        # Store constraints for this block
        if read_only_exprs or read_write_exprs:
            block_constraints[block_idx] = {
                'read_only': " + ".join(read_only_exprs) if read_only_exprs else None,
                'read_write': " + ".join(read_write_exprs) if read_write_exprs else None,
                'l1_lower': f"{' + '.join(read_write_exprs)} > L1_size" if read_write_exprs else None,
                'l2_upper': f"{' + '.join(read_write_exprs)} <= L2_size" if read_write_exprs else None
            }
    
    # Return complete constraint information
    return {
        'read_only': all_read_only_exprs,
        'read_write': all_read_write_exprs,
        'expr_to_array': expr_to_array,
        'array_types': array_types,
        'block_array_dimensions': block_array_dimensions,
        'block_array_access_patterns': block_array_access_patterns,
        'single_loop_arrays': single_loop_arrays,
        'multi_loop_arrays': multi_loop_arrays,
        'block_constraints': block_constraints
    }

def detect_array_layout(code_blocks, loop_info=None):
    """
    Detect whether arrays in the source code are stored in row-major or column-major order
    Analyze array access patterns - if the innermost loop variable appears in the first index, it's likely column-major
    
    Args:
        code_blocks: Extracted code blocks list
        loop_info: Loop structure analysis information
    
    Returns:
        layout_info: dict, array_name -> 'row_major' or 'column_major'
        block_layout_info: dict, block_idx -> {array -> layout}
        block_is_column_major: dict, block_idx -> True/False
        array_dimensions: dict, array_name -> dimension count (1, 2, etc.)
        array_dimension_vars: dict, array_name -> list of dimension variables
    """
    
    # Initialize layout information
    layout_info = {}  # Global array layout information
    block_layout_info = {}  # Block-specific array layout information
    array_dimensions = {}  # Track array dimensions: array_name -> dimension count
    array_dimension_vars = {}  # Track the dimension variables used by each array
    array_column_major_dims = {}  # array_name -> {block_idx -> [column_major_dimensions]}
    print("\n=== Analyzing Array Layout (Row-Major vs Column-Major) ===")
    
    # Convert to list if code_blocks is a string
    if isinstance(code_blocks, str):
        code_blocks = [code_blocks]
    
    # Ensure we have valid loop_info
    if not loop_info or 'blocks' not in loop_info:
        print("Warning: No valid loop_info provided, array layout detection may be limited")
        return {}, {}, {}, {}, {}
    
    # Get block information from loop_info
    blocks = loop_info['blocks']
    loop_levels = loop_info.get('loop_levels', {})
    block_to_vars = loop_info.get('block_to_vars', {})
    
    # Process each block
    for i, block in enumerate(blocks):
        # 获取正确的block_idx，避免覆盖
        if isinstance(block, dict):
            block_idx = block.get('block_idx', i)
            code_block = block.get('code', '')
        else:
            code_block = block
            block_idx = i
        
        # 初始化当前块的数组布局信息
        if block_idx not in block_layout_info:
            block_layout_info[block_idx] = {}
        
        print(f"\nAnalyzing layout for Block {block_idx}")
        
        # Get loop variables for this block
        block_vars = block_to_vars.get(block_idx, [])
        
        if not block_vars:
            print(f"  No loop variables found for Block {block_idx}, skipping layout analysis")
            continue
        
        # 改进循环变量层级识别，正确区分每一层的循环变量
        loop_vars_by_level = {}
        max_level = -1
        
        # 首先识别所有层级
        for var in block_vars:
            level = loop_levels.get(var, 0)
            max_level = max(max_level, level)
            if level not in loop_vars_by_level:
                loop_vars_by_level[level] = []
            loop_vars_by_level[level].append(var)
        
        # 更明确地区分内外层循环变量
        inner_loop_vars = []
        outer_loop_vars = []
        innermost_loop_vars = []  # 最内层循环变量
        
        # 定义内外层
        if max_level >= 0:
            innermost_loop_vars = loop_vars_by_level.get(max_level, [])
            inner_loop_vars = []
            # 收集所有比最外层深一层及以上的变量
            for level in range(1, max_level + 1):
                inner_loop_vars.extend(loop_vars_by_level.get(level, []))
            outer_loop_vars = loop_vars_by_level.get(0, [])
        
        print(f"  Loop variables: {block_vars}")
        print(f"  Loop variables by level: {loop_vars_by_level}")
        print(f"  Innermost loop variables (level {max_level}): {innermost_loop_vars}")
        print(f"  All inner loop variables: {inner_loop_vars}")
        print(f"  Outer loop variables: {outer_loop_vars}")
        
        # Extract all array accesses to determine array dimensions
        # Pattern matches both: array[idx1] and array[idx1][idx2]
        array_access_pattern = r'(\w+)\s*\[\s*([^\]]+)\s*\]\s*(?:\[\s*([^\]]+)\s*\])?'
        array_accesses = re.findall(array_access_pattern, code_block)
        
        # Determine array dimensions from access patterns
        arrays_in_block = {}  # array -> dimension count
        for match in array_accesses:
            array = match[0]
            # Count non-empty index expressions to determine dimension
            dimensions = sum(1 for idx in match[1:] if idx)
            
            if array not in arrays_in_block:
                arrays_in_block[array] = dimensions
            else:
                # Keep the highest dimension seen for this array
                arrays_in_block[array] = max(arrays_in_block[array], dimensions)
        
        # Update global array dimensions tracking
        for array, dims in arrays_in_block.items():
            array_dimensions[array] = max(dims, array_dimensions.get(array, 0))
            # Default all arrays to row-major initially
            if array not in layout_info:
                layout_info[array] = 'row_major'
            if array not in block_layout_info[block_idx]:
                block_layout_info[block_idx][array] = 'row_major'
        
        # Print all arrays found in this block with their dimensions
        print(f"  Arrays in Block {block_idx}:")
        for array, dims in arrays_in_block.items():
            print(f"    {array}: {dims}D array")
        
        # Analyze array access patterns for multi-dimensional arrays only
        access_patterns = {}
        array_loop_vars = {}  # 用于跟踪每个数组使用的循环变量        
        

        for match in re.finditer(array_access_pattern, code_block):
            array = match.group(1)
            idx1 = match.group(2)
            idx2 = match.group(3)
            
            # Initialize array_loop_vars for this array if needed
            if array not in array_loop_vars:
                array_loop_vars[array] = set()
            
            # Skip if we don't have both indices
            if idx2 is None:
                # For 1D arrays, still record the loop variables used
                for var in block_vars:
                    # Get original variable name (remove block suffix)
                    orig_var = var.split('_b')[0] if '_b' in var else var
                    
                    if re.search(r'\b' + re.escape(orig_var) + r'\b', idx1):
                        array_loop_vars[array].add(var)
                continue
                
            # Skip arrays that aren't in our tracking or aren't multi-dimensional
            if array not in arrays_in_block or arrays_in_block[array] < 2:
                continue
                
            # Initialize array's access pattern counter
            if array not in access_patterns:
                access_patterns[array] = {
                    'inner_in_first_idx': 0,   # 内层循环变量在第一索引
                    'inner_in_second_idx': 0,  # 内层循环变量在第二索引
                    'outer_in_first_idx': 0,   # 外层循环变量在第一索引
                    'outer_in_second_idx': 0,  # 外层循环变量在第二索引
                    'innermost_in_first_idx': 0,  # 最内层循环变量在第一索引
                    'innermost_in_second_idx': 0,  # 最内层循环变量在第二索引
                    'total_accesses': 0        # 总访问次数
                }
            
            # Count total accesses
            access_patterns[array]['total_accesses'] += 1
            
            # Check which loop variables appear in indices
            for inner_var in inner_loop_vars:
                # Get original variable name (remove block suffix)
                orig_var = inner_var.split('_b')[0] if '_b' in inner_var else inner_var
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx1):
                    access_patterns[array]['inner_in_first_idx'] += 1
                    array_loop_vars[array].add(inner_var)
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx2):
                    access_patterns[array]['inner_in_second_idx'] += 1
                    array_loop_vars[array].add(inner_var)
            
            for outer_var in outer_loop_vars:
                # Get original variable name (remove block suffix)
                orig_var = outer_var.split('_b')[0] if '_b' in outer_var else outer_var
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx1):
                    access_patterns[array]['outer_in_first_idx'] += 1
                    array_loop_vars[array].add(outer_var)
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx2):
                    access_patterns[array]['outer_in_second_idx'] += 1
                    array_loop_vars[array].add(outer_var)
        
            # 添加对最内层循环变量的检查
            for innermost_var in innermost_loop_vars:
                orig_var = innermost_var.split('_b')[0] if '_b' in innermost_var else innermost_var
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx1):
                    access_patterns[array]['innermost_in_first_idx'] += 1
                    array_loop_vars[array].add(innermost_var)
                
                if re.search(r'\b' + re.escape(orig_var) + r'\b', idx2):
                    access_patterns[array]['innermost_in_second_idx'] += 1
                    array_loop_vars[array].add(innermost_var)

        # Analyze collected access pattern data to determine row/column-major
        for array, pattern in access_patterns.items():
            if pattern['total_accesses'] == 0:
                continue
                
            # Calculate ratios for inner/outer variables in first/second indices
            inner_first_ratio = pattern['inner_in_first_idx'] / pattern['total_accesses']
            inner_second_ratio = pattern['inner_in_second_idx'] / pattern['total_accesses']
            outer_first_ratio = pattern['outer_in_first_idx'] / pattern['total_accesses']
            outer_second_ratio = pattern['outer_in_second_idx'] / pattern['total_accesses']

            # 计算最内层循环变量的比率
            innermost_first_ratio = pattern['innermost_in_first_idx'] / pattern['total_accesses']
            innermost_second_ratio = pattern['innermost_in_second_idx'] / pattern['total_accesses']

            # IMPROVED COLUMN-MAJOR DETERMINATION:
            # Column-major if:
            # 1. Inner loop variables predominantly in first index, OR
            # 2. Outer loop variables predominantly in second index
            is_column_major = False
            reasons = []

            
            # 1. 最内层循环变量在第一索引是强列主序指标 - 给较低阈值
            if innermost_first_ratio >= 0.3:
                is_column_major = True
                reasons.append(f"innermost loop in first index ({innermost_first_ratio:.2f})")
            
            # 2. 内层循环变量在第一索引 - 标准阈值
            if inner_first_ratio > 0.5 and inner_first_ratio >= inner_second_ratio:
                is_column_major = True
                reasons.append(f"inner loop in first index ({inner_first_ratio:.2f})")
            
            # 3. 外层循环变量在第二索引 - 标准阈值
            if outer_second_ratio > 0.5 and outer_second_ratio >= outer_first_ratio:
                is_column_major = True
                reasons.append(f"outer loop in second index ({outer_second_ratio:.2f})")
            
            # 4. 循环变量分布分析 - 如果循环变量在各个维度分布更均匀，考虑数据重用模式
            # 适用于矩阵乘法等复杂模式但不特定针对它们
            if (inner_first_ratio > 0.2 and inner_second_ratio > 0.2) or \
               (outer_first_ratio > 0.2 and outer_second_ratio > 0.2):
                # 数据重用分析：如果同一个变量出现在不同数组的不同维度，可能表明复杂的数据依赖
                # 通过分析索引模式中的变量重用情况来判断
                reuse_across_arrays = False
                
                # 简单启发式: 在复杂模式中，如果内层循环变量出现在第二维度的次数不少，
                # 且有良好的数据局部性，可能表明列主序tile更有利
                if inner_second_ratio >= 0.25 and innermost_first_ratio >= 0.25:
                    is_column_major = True
                    reasons.append(f"complex access pattern with balanced dimensionality")
            
            # Make final determination for this array in this block
            # 最终确定该数组在该块中的布局
            if is_column_major:
                block_layout_info[block_idx][array] = 'column_major'
                reasons_str = ", ".join(reasons)
                print(f"  Block {block_idx}, Array {array}: COLUMN-MAJOR due to {reasons_str}")
                print(f"    innermost_first: {innermost_first_ratio:.2f}, innermost_second: {innermost_second_ratio:.2f}")
                print(f"    inner_first: {inner_first_ratio:.2f}, inner_second: {inner_second_ratio:.2f}")
                print(f"    outer_first: {outer_first_ratio:.2f}, outer_second: {outer_second_ratio:.2f}")
                print(f"    dimension variables: {sorted(array_loop_vars.get(array, []))}")
            else:
                block_layout_info[block_idx][array] = 'row_major'
                print(f"  Block {block_idx}, Array {array}: ROW-MAJOR")
                print(f"    innermost_first: {innermost_first_ratio:.2f}, innermost_second: {innermost_second_ratio:.2f}")
                print(f"    inner_first: {inner_first_ratio:.2f}, inner_second: {inner_second_ratio:.2f}")
                print(f"    outer_first: {outer_first_ratio:.2f}, outer_second: {outer_second_ratio:.2f}")
                print(f"    dimension variables: {sorted(array_loop_vars.get(array, []))}")


        # 在确定数组布局后，识别列主序维度
        # 为每个数组初始化列维度信息（无论布局如何）
        for array in block_layout_info[block_idx]:
            if array not in array_column_major_dims:
                array_column_major_dims[array] = {}

        # 在确定数组布局后，为所有数组收集第二维度信息
        for array, layout in block_layout_info[block_idx].items():
            # 确保每个块都有一个条目，即使它不是列主序
            if block_idx not in array_column_major_dims[array]:
                array_column_major_dims[array][block_idx] = []
            
            # 只有列主序的数组才需要记录列维度
            if layout == 'column_major':
                # 对于列主序数组，识别关键维度（只关注第二个索引的维度）
                col_major_dims = []
                
                # 分析所有数组访问，找出第二个索引使用的维度
                for match in re.finditer(array_access_pattern, code_block):
                    # 确保是这个数组并且有第二个索引
                    if match.group(1) == array and match.group(3):
                        second_idx = match.group(3)
                        
                        # 检查哪些循环变量出现在第二个索引中
                        for var in block_vars:
                            orig_var = var.split('_b')[0] if '_b' in var else var
                            if re.search(r'\b' + re.escape(orig_var) + r'\b', second_idx):
                                if var not in col_major_dims:
                                    col_major_dims.append(var)
                                    print(f"  识别到 {var} 作为 {array} 的列主序关键维度 (位于第二索引)")
                
                # 存储识别出的列主序维度
                array_column_major_dims[array][block_idx] = col_major_dims
                print(f"  {array} 在块 {block_idx} 中的列主序维度: {col_major_dims}")
            else:
                # 对于非列主序数组，显式记录它们没有列维度
                print(f"  {array} 在块 {block_idx} 中不是列主序，没有列维度")

        # Add the dimension variables information
        for array, loop_vars in array_loop_vars.items():
            if array not in array_dimension_vars:
                array_dimension_vars[array] = {}
            array_dimension_vars[array][block_idx] = sorted(list(loop_vars))
    
    # Determine global array layout based on most frequent layout across blocks
    for array in array_dimensions:
        # Only process multi-dimensional arrays
        if array_dimensions[array] < 2:
            layout_info[array] = 'row_major'  # Default for 1D
            continue
            
        # Count column-major occurrences across blocks
        col_major_count = sum(1 for block_idx, arrays in block_layout_info.items() 
                              if array in arrays and arrays[array] == 'column_major')
        
        # Count total blocks where this array appears
        total_blocks = sum(1 for block_idx, arrays in block_layout_info.items() 
                           if array in arrays)
        
        # Determine dominant layout
        if total_blocks > 0 and col_major_count / total_blocks > 0.5:
            layout_info[array] = 'column_major'
        else:
            layout_info[array] = 'row_major'
    
    # Print global analysis results
    print("\nFinal array layout analysis:")
    multidim_arrays = {array: dims for array, dims in array_dimensions.items() if dims >= 2}
    onedim_arrays = {array: dims for array, dims in array_dimensions.items() if dims == 1}
    
    print(f"Multi-dimensional arrays: {list(multidim_arrays.keys())}")
    print(f"One-dimensional arrays: {list(onedim_arrays.keys())}")
    
    col_major_arrays = [array for array, layout in layout_info.items() 
                         if layout == 'column_major' and array in multidim_arrays]
    row_major_multidim_arrays = [array for array, layout in layout_info.items() 
                                  if layout == 'row_major' and array in multidim_arrays]
    
    if col_major_arrays:
        print(f"Column-major arrays: {', '.join(col_major_arrays)}")
    if row_major_multidim_arrays:
        print(f"Row-major multi-dimensional arrays: {', '.join(row_major_multidim_arrays)}")
    
    # Print block-specific layouts
    print("\nBlock-specific array layouts:")
    for block_idx, arrays in sorted(block_layout_info.items()):
        multidim_in_block = {array: layout for array, layout in arrays.items() 
                             if array in multidim_arrays}
        
        if not multidim_in_block:
            print(f"  Block {block_idx}: No multi-dimensional arrays")
            continue
            
        col_major = [a for a, l in multidim_in_block.items() if l == 'column_major']
        row_major = [a for a, l in multidim_in_block.items() if l == 'row_major']
        
        print(f"  Block {block_idx}:")
        if col_major:
            col_major_with_dims = []
            for a in col_major:
                dims = array_dimension_vars.get(a, {}).get(block_idx, [])
                col_major_with_dims.append(f"{a}({', '.join(dims)})")
            print(f"    Column-major: {', '.join(col_major_with_dims)}")
        if row_major:
            row_major_with_dims = []
            for a in row_major:
                dims = array_dimension_vars.get(a, {}).get(block_idx, [])
                row_major_with_dims.append(f"{a}({', '.join(dims)})")
            print(f"    Row-major: {', '.join(row_major_with_dims)}")
    
    # Determine if each block is primarily column-major (ONLY considering multi-dimensional arrays)
    block_is_column_major = {}
    for block_idx, arrays in block_layout_info.items():
        # Filter to only multi-dimensional arrays in this block
        multidim_in_block = {array: layout for array, layout in arrays.items() 
                             if array in multidim_arrays}
        
        if not multidim_in_block:
            # If no multi-dimensional arrays, default to row-major
            block_is_column_major[block_idx] = False
            print(f"Block {block_idx} has no multi-dimensional arrays - defaulting to row-major")
            continue
        
        # Calculate percentage of column-major arrays among multi-dimensional arrays
        col_major_count = sum(1 for layout in multidim_in_block.values() if layout == 'column_major')
        total_multidim = len(multidim_in_block)
        
        # Mark block as column-major if over 30% of multi-dimensional arrays are column-major
        if total_multidim > 0 and col_major_count / total_multidim > 0.3:
            block_is_column_major[block_idx] = True
            print(f"Block {block_idx} is primarily column-major ({col_major_count}/{total_multidim} multi-dimensional arrays)")
        else:
            block_is_column_major[block_idx] = False
            print(f"Block {block_idx} is primarily row-major ({total_multidim - col_major_count}/{total_multidim} multi-dimensional arrays)")


    return layout_info, block_layout_info, block_is_column_major, array_dimensions, array_dimension_vars, array_column_major_dims


def generate_cache_constraint_code(cache_constraints, access_info):
    """
    Generate cache constraint code expressions for ILP model
    Use loop variable names for block names
    Generate separate constraints for each block, plus combined constraints
    """
    constraint_code = "# Cache constraints for ILP model\n"
    
    # Get single-loop arrays
    single_loop_arrays = access_info.get('single_loop_arrays', set())
    
    print(f"Arrays used exclusively in single loops (skipping constraints): {single_loop_arrays}")
    
    # Generate constraints by block
    if 'block_constraints' in cache_constraints:
        block_constraints = cache_constraints['block_constraints']
        for block_idx, constraints in sorted(block_constraints.items()):
            constraint_code += f"\n# Block {block_idx} specific constraints\n"
            
            # Read-only array constraints
            if 'read_only' in constraints and constraints['read_only']:
                constraint_code += f"block_{block_idx}_read_only_constraint = \"{constraints['read_only']}\"\n"
                print(f"Block {block_idx} read-only constraint: {constraints['read_only']} <= L1_size")
            else:
                constraint_code += f"block_{block_idx}_read_only_constraint = None\n"
            
            # Read-write array L1 lower bound
            if 'l1_lower' in constraints and constraints['l1_lower']:
                constraint_code += f"block_{block_idx}_l1_lower_constraint = \"{constraints['l1_lower']}\"\n"
                print(f"Block {block_idx} L1 lower bound: {constraints['l1_lower']}")
            else:
                constraint_code += f"block_{block_idx}_l1_lower_constraint = None\n"
            
            # Read-write array L2 upper bound
            if 'l2_upper' in constraints and constraints['l2_upper']:
                constraint_code += f"block_{block_idx}_l2_upper_constraint = \"{constraints['l2_upper']}\"\n"
                print(f"Block {block_idx} L2 upper bound: {constraints['l2_upper']}")
            else:
                constraint_code += f"block_{block_idx}_l2_upper_constraint = None\n"
            
            # Keep original read-write constraint for compatibility
            if 'read_write' in constraints and constraints['read_write']:
                constraint_code += f"block_{block_idx}_read_write_constraint = \"{constraints['read_write']}\"\n"
            else:
                constraint_code += f"block_{block_idx}_read_write_constraint = None\n"
    
    # Global constraints (for backward compatibility)
    constraint_code += "\n# Global constraints (aggregated across all blocks)\n"
    
    # Process read-only array constraints
    if 'read_only' in cache_constraints and cache_constraints['read_only']:
        read_only_exprs = []
        skipped_exprs = []
        
        expr_to_array = cache_constraints.get('expr_to_array', {})
        
        for expr in cache_constraints['read_only']:
            # Skip expressions for single-loop arrays
            corresponding_array = expr_to_array.get(expr)
            if corresponding_array in single_loop_arrays:
                skipped_exprs.append(expr)
                continue
            
            read_only_exprs.append(expr)
        
        if skipped_exprs:
            print(f"Skipped {len(skipped_exprs)} read-only expressions from single-loop arrays")
        
        if read_only_exprs:
            read_only_sum = " + ".join(read_only_exprs)
            # Add full constraint: read-only arrays should fit in L1 cache
            constraint_code += f"read_only_constraint = \"{read_only_sum}\"\n"
            print(f"Global read-only arrays constraint: {read_only_sum} <= L1_size")
        else:
            constraint_code += "read_only_constraint = None\n"
            print("No global read-only array constraints after filtering")
    else:
        constraint_code += "read_only_constraint = None\n"
        print("No global read-only array constraints")
    
    # Process read-write array constraints - L1 lower bound and L2 upper bound
    if 'read_write' in cache_constraints and cache_constraints['read_write']:
        read_write_exprs = []
        skipped_exprs = []
        
        expr_to_array = cache_constraints.get('expr_to_array', {})
        
        for expr in cache_constraints['read_write']:
            # Skip expressions for single-loop arrays
            corresponding_array = expr_to_array.get(expr)
            if corresponding_array in single_loop_arrays:
                skipped_exprs.append(expr)
                continue
            
            read_write_exprs.append(expr)
        
        if skipped_exprs:
            print(f"Skipped {len(skipped_exprs)} read-write expressions from single-loop arrays")
        
        if read_write_exprs:
            read_write_sum = " + ".join(read_write_exprs)
            # Add two full constraints:
            # 1. L1 lower bound: working set should be larger than L1 cache
            constraint_code += f"read_write_l1_constraint = \"{read_write_sum} > L1_size\"\n"
            # 2. L2 upper bound: working set should fit in L2 cache
            constraint_code += f"read_write_l2_constraint = \"{read_write_sum} <= L2_size\"\n"
            
            # Keep original read_write_constraint for compatibility
            constraint_code += f"read_write_constraint = \"{read_write_sum}\"\n"
            
            print(f"Global read-write arrays L1 lower bound: {read_write_sum} > L1_size")
            print(f"Global read-write arrays L2 upper bound: {read_write_sum} <= L2_size")
        else:
            constraint_code += "read_write_l1_constraint = None\n"
            constraint_code += "read_write_l2_constraint = None\n"
            constraint_code += "read_write_constraint = None\n"
            print("No global read-write array constraints after filtering")
    else:
        constraint_code += "read_write_l1_constraint = None\n"
        constraint_code += "read_write_l2_constraint = None\n"
        constraint_code += "read_write_constraint = None\n"
        print("No global read-write array constraints")
    
    return constraint_code

def write_parameters_to_file(params, output_file):
    """
    Write all parameters to a Python file that can be imported by the ILP model
    Enhanced to include block-specific information and constraints with improved formatting
    """
    with open(output_file, 'w') as f:
        f.write("# Auto-generated parameters for ILP tiling\n\n")
        
        # Write cache parameters
        f.write("# Cache parameters\n")
        f.write(f"L1_size = {params['L1_size']}  # L1 data cache size in bytes\n")
        f.write(f"L2_size = {params['L2_size']}  # L2 cache size in bytes\n")
        f.write(f"cache_line = {params['cache_line']}  # Cache line size in bytes\n\n")

        # Write thread count information
        f.write("\n# Parallelization information\n")
        f.write(f"num_threads = {params.get('num_threads', 1)}  # Number of physical cores\n\n")

        # Write loop variable information including block-specific details
        if 'loop_vars' in params:
            loop_vars = params['loop_vars']
            var_to_size = params.get('var_to_size', {})
            loop_var_to_size = params.get('loop_var_to_size', {})
            
            # Get original to unique variable mapping
            orig_to_unique = params.get('orig_to_unique', {})
            
            f.write("# 循环变量信息\n")
            
            # 以注释形式写入原始变量到唯一变量的映射
            if orig_to_unique:
                f.write("# 原始变量到唯一变量的映射\n")
                for orig, unique_vars in orig_to_unique.items():
                    if isinstance(unique_vars, list):
                        f.write(f"# {orig} -> {unique_vars}\n")
                    else:
                        # 处理可能的字符串情况
                        f.write(f"# {orig} -> {unique_vars}\n")
                f.write("\n")
            
            # Write loop variables list
            f.write(f"loop_vars = {repr(loop_vars)}  # 循环变量列表\n\n")
            
            # Write actual sizes for each loop variable
            f.write("# 循环变量尺寸\n")
            for var in loop_vars:
                size = None
                # First check loop_var_to_size which contains block-specific sizes
                if var in loop_var_to_size:
                    size = loop_var_to_size[var]
                # Then check var_to_size which might contain sizes from header file
                elif var in var_to_size:
                    size = var_to_size[var]
                
                if size is not None:
                    # Add comment to indicate block information if present
                    if '_b' in var:
                        orig_var = var.split('_b')[0]
                        block_idx = var.split('_b')[1]
                        f.write(f"{var}_size = {size}  # 循环变量 {orig_var} 在块 {block_idx} 中的维度大小\n")
                    else:
                        f.write(f"{var}_size = {size}  # {var} 维度大小\n")
            
            # Organize variables by block for clarity - as comments
            if 'block_to_vars' in params:
                block_to_vars = params['block_to_vars']
                if block_to_vars:
                    f.write("\n# 按块组织的循环变量\n")
                    for block_idx, vars_list in sorted(block_to_vars.items()):
                        f.write(f"# 块 {block_idx} 中的循环变量: {vars_list}\n")
            
            f.write("\n")

        # Write data type information
        f.write("# Data type information\n")
        f.write(f"data_type = '{params['data_type']}'\n")
        f.write(f"data_size = {params['data_size']}  # Size in bytes\n\n")

        # Write tileable dimensions information
        if 'block_tileable_dims' in params:
            f.write("\n# Tileable dimensions for each block\n")
            f.write("block_tileable_dims = {\n")
            for block_idx, tileable_status in sorted(params['block_tileable_dims'].items()):
                f.write(f"    {block_idx}: {{\n")
                for var, is_tileable in sorted(tileable_status.items()):
                    if is_tileable:
                        f.write(f"        '{var}': True,  # Variable can be tiled\n")
                    else:
                        f.write(f"        '{var}': False,  # Variable CANNOT be tiled - use tile size 1\n")
                f.write("    },\n")
            f.write("}\n\n")


        # 添加按块组织的数组布局信息，包括维度变量
        if 'block_layout' in params and 'array_dimension_vars' in params:
            f.write("# Block-specific array layout information\n")
            f.write("block_array_layout = {\n")
            for block_idx, arrays in sorted(params['block_layout'].items()):
                f.write(f"    {block_idx}: {{\n")
                
                # 分离多维数组和一维数组
                multidim_in_block = {}
                onedim_in_block = {}
                
                if 'array_dimensions' in params:
                    for array, layout in sorted(arrays.items()):
                        dims = params['array_dimensions'].get(array, 0)
                        if dims >= 2:
                            multidim_in_block[array] = layout
                        else:
                            onedim_in_block[array] = layout
                else:
                    multidim_in_block = arrays
                
                # 先写多维数组，包含维度变量信息
                if multidim_in_block:
                    f.write("        # Multi-dimensional arrays\n")
                    for array, layout in sorted(multidim_in_block.items()):
                        dims = params.get('array_dimensions', {}).get(array, 'unknown')
                        # 添加与数组相关的维度变量
                        dim_vars = params['array_dimension_vars'].get(array, {}).get(block_idx, [])
                        dim_vars_str = ", ".join(dim_vars) if dim_vars else "no dimension vars found"
                        f.write(f"        '{array}': '{layout}',  # {dims}D array, dims: {dim_vars_str}\n")
                
                # 再写一维数组
                if onedim_in_block:
                    f.write("        # One-dimensional arrays\n")
                    for array, layout in sorted(onedim_in_block.items()):
                        # 添加与数组相关的维度变量
                        dim_vars = params['array_dimension_vars'].get(array, {}).get(block_idx, [])
                        dim_vars_str = ", ".join(dim_vars) if dim_vars else "no dimension vars found"
                        f.write(f"        '{array}': '{layout}',  # 1D array, dims: {dim_vars_str}\n")
                
                f.write("    },\n")
            f.write("}\n\n")

            # 单独添加数组维度变量的字典
            f.write("# Array dimension variables information\n")
            f.write("array_dimension_vars = {\n")
            for array, block_dims in sorted(params['array_dimension_vars'].items()):
                f.write(f"    '{array}': {{\n")
                for block_idx, dims in sorted(block_dims.items()):
                    f.write(f"        {block_idx}: {dims},\n")
                f.write("    },\n")
            f.write("}\n\n")

        # Write array access pattern information
        if 'block_array_access_patterns' in params:
            f.write("\n# Array access patterns by block\n")
            f.write("block_array_access_patterns = {\n")
            for block_idx, arrays in sorted(params['block_array_access_patterns'].items()):
                f.write(f"    {block_idx}: {{\n")
                for array, patterns in sorted(arrays.items()):
                    f.write(f"        '{array}': [\n")
                    for pattern in patterns:
                        pattern_str = ", ".join(str(idx) for idx in pattern)
                        f.write(f"            ({pattern_str}),\n")
                    f.write("        ],\n")
                f.write("    },\n")
            f.write("}\n\n")

        # 添加块是否主要使用列主序的信息
        if 'block_is_column_major' in params:
            f.write("# Block-specific column-major layout information\n")
            f.write("block_is_column_major = {\n")
            for block_idx, is_col_major in sorted(params['block_is_column_major'].items()):
                # 添加注释说明判断依据
                if is_col_major:
                    f.write(f"    {block_idx}: {is_col_major},  # Block primarily uses column-major arrays\n")
                else:
                    f.write(f"    {block_idx}: {is_col_major},  # Block primarily uses row-major arrays\n")
            f.write("}\n\n")

        # 添加列主序维度信息
        if 'array_column_major_dims' in params:
            f.write("# 数组的列主序关键维度\n")
            f.write("array_column_major_dims = {\n")
            for array, block_dims in sorted(params['array_column_major_dims'].items()):
                # 始终为每个数组创建一个条目
                f.write(f"    '{array}': {{\n")
                # 写入每个块的维度信息，即使列表为空
                for block_idx, dims in sorted(block_dims.items()):
                    # 只有当这个数组在这个块中被识别为列主序时才有dims
                    if 'block_layout' in params and block_idx in params['block_layout'] and array in params['block_layout'][block_idx]:
                        layout = params['block_layout'][block_idx][array]
                        if layout == 'column_major':
                            f.write(f"        {block_idx}: {dims},  # 列主序\n")
                    else:
                        f.write(f"        {block_idx}: {dims},\n")
                f.write("    },\n")
            f.write("}\n\n")

        # Write statement costs 
        f.write("# Statement costs (nanoseconds)\n")
        
        # 首先从 operation_costs 中收集所有语句的成本
        stmt_costs = {}
        block_mapping = {}  # 存储语句到块的映射
        
        # 从 operation_costs 中提取所有 T_op 变量和块映射
        for key, value in params.get('operation_costs', {}).items():
            if key.startswith('T_op'):
                stmt_num = int(key[4:])
                stmt_costs[stmt_num] = value
            elif key.startswith('block_id_'):
                stmt_num = int(key[9:])
                block_mapping[stmt_num] = value
        
        # 确保所有语句都有成本 - 获取语句数量
        stmt_count = params.get('operation_costs', {}).get('stmt_count', 0)
        
        # 按语句编号顺序输出所有语句的成本
        for i in range(1, stmt_count + 1):
            if i in stmt_costs:
                # 如果有块信息，添加到输出
                if i in block_mapping:
                    block_id = block_mapping[i]
                    f.write(f"T_op{i} = {stmt_costs[i]}  # Statement {i} cost (block {block_id})\n")
                else:
                    f.write(f"T_op{i} = {stmt_costs[i]}\n")
            else:
                # 如果在 operation_costs 中找不到但存在于全局变量中
                var_name = f'T_op{i}'
                if var_name in globals():
                    if i in block_mapping:
                        block_id = block_mapping[i]
                        f.write(f"{var_name} = {globals()[var_name]}  # Statement {i} cost (block {block_id})\n")
                    else:
                        f.write(f"{var_name} = {globals()[var_name]}\n")
                else:
                    # 如果找不到此语句成本，记录警告
                    print(f"Warning: Could not find cost for statement {i}")
        
        f.write("\n")
        
        # Write cache access latencies
        f.write("# Cache access latencies (nanoseconds)\n")
        f.write(f"T_L1 = {params['T_L1']:.2f}  # L1 cache access latency\n")
        f.write(f"T_L2 = {params['T_L2']:.2f}  # L2 cache access latency\n\n")
        
        # Write operation latencies based on data type
        f.write("# Operation latencies (nanoseconds)\n")
        if params['data_type'] == 'double':
            f.write(f"T_add = {params['T_add_double']:.2f}  # Double addition latency\n")
            f.write(f"T_mul = {params['T_mul_double']:.2f}  # Double multiplication latency\n")
        else:
            f.write(f"T_add = {params['T_add_float']:.2f}  # Float addition latency\n")
            f.write(f"T_mul = {params['T_mul_float']:.2f}  # Float multiplication latency\n")
        
        # Write operation counts
        if 'operation_costs' in params:
            f.write("\n# Detailed operation costs\n")
            if 'stmt_count' in params['operation_costs']:
                f.write(f"stmt_count = {params['operation_costs']['stmt_count']}\n")
        
        # Write block-specific constraints if available
        if 'block_constraints' in params:
            f.write("\n# Block-specific cache constraints\n")
            for block_idx, constraints in sorted(params['block_constraints'].items()):
                f.write(f"# Block {block_idx} constraints\n")
                if 'read_only' in constraints:
                    f.write(f"block_{block_idx}_read_only_constraint = \"{constraints['read_only']}\"\n")
                if 'read_write' in constraints:
                    f.write(f"block_{block_idx}_read_write_constraint = \"{constraints['read_write']}\"\n")
                if 'l1_lower' in constraints:
                    f.write(f"block_{block_idx}_l1_lower_constraint = \"{constraints['l1_lower']}\"\n")
                if 'l2_upper' in constraints:
                    f.write(f"block_{block_idx}_l2_upper_constraint = \"{constraints['l2_upper']}\"\n")
                f.write("\n")
        
        # Write block-specific objective functions if available
        if 'block_objective_functions' in params:
            f.write("# Block-specific objective functions\n")
            block_obj_funcs = params['block_objective_functions']
            
            # Handle both dict and other formats
            if isinstance(block_obj_funcs, dict):
                for block_idx, obj_func in sorted(block_obj_funcs.items()):
                    # Ensure the objective function is a proper string
                    if isinstance(obj_func, (tuple, list, dict)):
                        obj_func = str(obj_func).replace("'", "")
                    f.write(f"block_{block_idx}_objective = \"{obj_func}\"\n")
            else:
                f.write(f"# Could not process block objective functions: {type(block_obj_funcs)}\n")
            f.write("\n")

        # Write overall cache constraint expressions
        if 'cache_constraints' in params:
            f.write("# Combined cache constraints for ILP model\n")
            f.write(params['cache_constraints'])

        # Write the overall objective function
        if 'objective_function' in params:
            f.write("\n# Auto-generated objective function\n")
            obj_func = params['objective_function']
            
            # Ensure objective function is a string
            if isinstance(obj_func, (tuple, list, dict)):
                obj_func = str(obj_func).replace("'", "")
                
            f.write(f"objective_function = \"{obj_func}\"\n")
            
        # # Write a dict for block objective functions for easier access
        # if 'block_objective_functions' in params:
        #     f.write("\n# Block objective functions dictionary\n")
        #     f.write("block_objective_functions = {\n")
        #     block_obj_funcs = params['block_objective_functions']
            
        #     if isinstance(block_obj_funcs, dict):
        #         for block_idx, obj_func in sorted(block_obj_funcs.items()):
        #             # Process the objective function to make it safer for string representation
        #             if isinstance(obj_func, (tuple, list, dict)):
        #                 obj_func = str(obj_func).replace("'", "")
        #             f.write(f"    \"{block_idx}\": \"{obj_func}\",\n")
        #     f.write("}\n")

def main():
    parser = argparse.ArgumentParser(description='Preprocess parameters for ILP tiling optimization')
    parser.add_argument('source_file', help='Source code file to analyze (e.g., gemm.c)')
    parser.add_argument('--output', default='ilp_params.py', help='Output file for parameters')
    args = parser.parse_args()
    
    print(f"Analyzing source file: {args.source_file}")
    
    # Get cache information
    print("\nGetting cache information...")
    cache_info = get_cache_info()
    num_threads = get_physical_cores()
    print(f"L1 cache: {cache_info['L1_size'] / 1024:.1f} KB")
    print(f"L2 cache: {cache_info['L2_size'] / 1024:.1f} KB")
    print(f"Cache line: {cache_info['cache_line']} bytes")
    print(f"Calculated physical cores: {num_threads}")
    
    # Measure operation latencies
    print("\nMeasuring operation latencies...")
    latencies = measure_cache_and_operation_latencies(cache_info)
    print(f"L1 cache access: {latencies['T_L1']:.2f} ns")
    print(f"L2 cache access: {latencies['T_L2']:.2f} ns")
    print(f"Double add latency: {latencies['T_add_double']:.2f} ns")
    print(f"Double multiply latency: {latencies['T_mul_double']:.2f} ns")
    print(f"Float add latency: {latencies['T_add_float']:.2f} ns")
    print(f"Float multiply latency: {latencies['T_mul_float']:.2f} ns")
    
    # Extract matrix dimensions and data type
    print("\nExtracting matrix information...")
    
    # 初始化all_params字典，确保包含必要的键
    all_params = {
        'L1_size': cache_info['L1_size'],
        'L2_size': cache_info['L2_size'],
        'cache_line': cache_info['cache_line'],
        'num_threads': num_threads
    }
    
    # 添加延迟信息
    all_params.update(latencies)
    
    # 检测数据类型
    data_type, data_size = detect_data_type(args.source_file)
    all_params['data_type'] = data_type
    all_params['data_size'] = data_size
    
    # Extract and analyze computation code
    print("\nAnalyzing computation structure...")
    code_blocks = extract_computation_code(args.source_file)
    
    objective_function = None
    operation_costs = None
    cache_constraint = None

    if code_blocks:
        print(f"Successfully extracted {len(code_blocks)} computation code blocks")
        
        # 分析循环结构
        print("\nAnalyzing loop structure...")
        loop_info = analyze_loop_structure(code_blocks)

        # 获取可分块维度信息
        tileable_dimensions = get_tileable_dimensions(args.source_file)
        block_tileable_dims = map_filters_to_blocks(tileable_dimensions, loop_info)
        
        # 将分块信息添加到loop_info中
        loop_info['block_tileable_dims'] = block_tileable_dims
        all_params['block_tileable_dims'] = block_tileable_dims
        # 分析数组布局
        print("\nAnalyzing array layout(row/column major)...")
        layout_info, block_layout_info, block_is_column_major, array_dimensions, array_dimension_vars, array_column_major_dims = detect_array_layout(code_blocks, loop_info)


        # 更新循环变量相关信息
        all_params['loop_vars'] = loop_info.get('loop_vars', [])
        all_params['raw_loop_vars'] = loop_info.get('raw_loop_vars', [])
        all_params['loop_var_to_size'] = loop_info.get('loop_var_to_size', {})
        all_params['loop_vars_to_bounds'] = loop_info.get('loop_vars_to_bounds', {})
        all_params['block_to_vars'] = loop_info.get('block_to_vars', {})
        all_params['orig_to_unique'] = loop_info.get('orig_to_unique', {})
        

        #添加数组布局信息
        all_params['array_layout'] = layout_info
        all_params['block_layout'] = block_layout_info
        all_params['block_is_column_major'] = block_is_column_major
        all_params['array_dimensions'] = array_dimensions
        all_params['array_dimension_vars'] = array_dimension_vars
        all_params['array_column_major_dims'] = array_column_major_dims
        # 分析数组访问
        print("\nAnalyzing array accesses...")
        access_info = analyze_array_accesses(code_blocks, latencies, data_type, loop_info)
        
        # 分析数组维度
        print("\nAnalyzing array dimensions...")
        cache_constraints = analyze_array_dimensions(access_info, loop_info)
        
        # 生成缓存约束代码
        print("\nGenerating cache constraints...")
        cache_constraint_code = generate_cache_constraint_code(cache_constraints, access_info)
        
        # 生成目标函数
        print("\nGenerating objective function...")
        obj_result = generate_objective_function(loop_info, access_info, {'data_type': data_type})

        # Fix: Handle both tuple and single return value formats
        if isinstance(obj_result, tuple) and len(obj_result) == 2:
            objective_function, block_objective_functions = obj_result
        else:
            # Backward compatibility
            objective_function = obj_result
            block_objective_functions = {}
        
        # Fix: Store both the combined objective function and individual block functions
        all_params['objective_function'] = objective_function
        all_params['block_objective_functions'] = block_objective_functions

        # 创建成本运算字典
        operation_costs = {'stmt_count': len(access_info['statements'])}
        
        # 添加每个语句的成本
        for stmt in access_info['statements']:
            operation_costs[f'T_op{stmt["id"]+1}'] = stmt['cost']
            operation_costs[f'block_id_{stmt["id"]+1}'] = stmt['block_idx']
        
        # 添加块数量信息
        operation_costs['block_count'] = len(loop_info.get('blocks', []))
        
        # 更新all_params
        all_params.update({
            'objective_function': objective_function,
            'cache_constraints': cache_constraint_code,
            'operation_costs': operation_costs,
            'single_loop_arrays': list(access_info.get('single_loop_arrays', [])),
            'multi_loop_arrays': list(access_info.get('multi_loop_arrays', []))
        })
        
        # 添加var_to_size
        var_to_size = {}
        for var in all_params['loop_vars']:
            if var in loop_info.get('loop_var_to_size', {}):
                var_to_size[var] = loop_info['loop_var_to_size'][var]
        
        all_params['var_to_size'] = var_to_size
    else:
        print("Warning: Could not extract computation code, using default objective function")
        # Standard GEMM model: m_blocks * n_blocks * (T_op1 + k_blocks * T_op2)
        if data_type == 'double':
            t_op1 = 2 * latencies['T_L2'] + latencies['T_add_double']
            t_op2 = 2 * latencies['T_L1'] + 2 * latencies['T_L2'] + 2 * latencies['T_mul_double'] + latencies['T_add_double']
        else:
            t_op1 = 2 * latencies['T_L2'] + latencies['T_add_float']
            t_op2 = 2 * latencies['T_L1'] + 2 * latencies['T_L2'] + 2 * latencies['T_mul_float'] + latencies['T_add_float']
            
        objective_function = f"m_blocks * n_blocks * ({t_op1:.2f} + k_blocks * {t_op2:.2f})"
        
        # 添加默认缓存约束
        cache_constraint_code = "# Default GEMM cache constraints\n"
        cache_constraint_code += "read_only_constraint = \"m_tile * k_tile * data_size + k_tile * n_tile * data_size <= L1_size\"\n"
        cache_constraint_code += "read_write_l1_constraint = \"m_tile * n_tile * data_size > L1_size\"\n"
        cache_constraint_code += "read_write_l2_constraint = \"m_tile * n_tile * data_size <= L2_size\"\n"
        cache_constraint_code += "read_write_constraint = \"m_tile * n_tile * data_size\"\n"
        
        all_params['objective_function'] = objective_function
        all_params['cache_constraints'] = cache_constraint_code
    
    # Calculate T_op1 and T_op2 for backward compatibility
    if data_type == 'double':
        all_params['T_op1'] = 2 * latencies['T_L2'] + latencies['T_add_double']
        all_params['T_op2'] = 2 * latencies['T_L1'] + 2 * latencies['T_L2'] + 2 * latencies['T_mul_double'] + latencies['T_add_double']
    else:
        all_params['T_op1'] = 2 * latencies['T_L2'] + latencies['T_add_float']
        all_params['T_op2'] = 2 * latencies['T_L1'] + 2 * latencies['T_L2'] + 2 * latencies['T_mul_float'] + latencies['T_add_float']
    
    # Add operation costs if available
    if operation_costs:
        all_params['operation_costs'] = operation_costs

    # Write parameters to file
    print(f"\nWriting parameters to {args.output}...")
    write_parameters_to_file(all_params, args.output)
    
    print("Parameter preprocessing completed successfully.")

if __name__ == "__main__":
    main()