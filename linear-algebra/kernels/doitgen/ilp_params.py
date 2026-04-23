# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 49152  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0']
# c1 -> ['c1_b0']
# c4 -> ['c4_b0']
# c5 -> ['c5_b0']

loop_vars = ['c0_b0', 'c1_b0', 'c4_b0', 'c5_b0']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 250  # Loop variable c0 in block 0
c1_b0_size = 220  # Loop variable c1 in block 0
c4_b0_size = 270  # Non-tileable dimension
c5_b0_size = 270  # Non-tileable dimension

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c4_b0', 'c5_b0']

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


num_threads = 8  # Number of physical cores
# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c4_b0', 'c5_b0']

openmp_parallel_blocks = {
    0: True,
}

openmp_parallel_dims = {
    0: ['c4_b0'],  # Parallel
}



# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
        'c4_b0': True,  # Variable CANNOT be tiled - use tile size 1
        'c5_b0': True,  # Variable CANNOT be tiled - use tile size 1
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b0, c1_b0
        'C4': 'column_major',  # 2D array, dims: c4_b0, c5_b0
        # One-dimensional arrays
        'sum': 'row_major',  # 1D array, dims: c4_b0
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        0: ['c0_b0', 'c1_b0'],
    },
    'C4': {
        0: ['c4_b0', 'c5_b0'],
    },
    'sum': {
        0: ['c4_b0'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0:True,  # Block primarily uses column-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
    },
    'C4': {
        0: ['c4_b0'],  # 列主序
    },
    'sum': {
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 7.2  # Statement 1 cost (block 0)
T_op2 = 18.810000000000002  # Statement 2 cost (block 0)
T_op3 = 14.4  # Statement 3 cost (block 0)

# Cache access latencies (nanoseconds)
T_L1 = 2.93  # L1 cache access latency
T_L2 = 7.20  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.75  # Double addition latency
T_sub = 0.80  # Double subtraction latency
T_mul = 1.48  # Double multiplication latency
T_div = 5.19  # Double division latency
T_sqrt = 20.00  # Double sqrt latency
T_trig = 40.00  # Double trig function latency
T_log_exp = 35.00  # Double log/exp latency
T_pow = 45.00  # Double power function latency

# Math function mappings
# Math function type to function name mapping
math_func_type_map = {
    'sqrt': ['sqrt', 'sqrtf'],
    'trig': ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
             'sinf', 'cosf', 'tanf', 'asinf', 'acosf', 'atanf'],
    'log_exp': ['log', 'log10', 'exp', 'logf', 'log10f', 'expf'],
    'pow': ['pow', 'powf']
}

# Detailed math function latency mapping
math_func_latency_map = {
    'double': {
        'sqrt': 20.00,
        'sin': 40.00,
        'cos': 40.00,
        'tan': 40.00,
        'asin': 40.00,
        'acos': 40.00,
        'atan': 40.00,
        'log': 35.00,
        'log10': 35.00,
        'exp': 35.00,
        'pow': 45.00
    }
}


# Detailed operation costs
stmt_count = 3
# Block-specific objective functions
block_0_objective = "270 * c0_b0_blocks * c1_b0_blocks * 21.6 + c0_b0_blocks * c1_b0_blocks * c4_b0_blocks * c5_b0_blocks * 18.81 " 


# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = " c4_b0_tile * c5_b0_tile * data_size"
block_0_l1_lower_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *   data_size) > L1_size"
block_0_l2_upper_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *   data_size) <= L2_size"
block_0_read_write_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *   data_size)"

# Global constraints (aggregated across all blocks)
read_only_constraint = "c4_b0_tile * c5_b0_tile * data_size"
read_write_l1_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size )> L1_size"
read_write_l2_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *  data_size) <= L2_size"
read_write_constraint = "c4_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *  data_size)"

# # Block 0 specific constraints 全L1
# block_0_read_only_constraint = " c4_b0_tile * c5_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *   data_size) + c4_b0_tile * data_size"
# block_0_l1_lower_constraint = None
# block_0_l2_upper_constraint = None
# block_0_read_write_constraint = None

# # Global constraints (aggregated across all blocks)
# read_only_constraint = "c4_b0_tile * c5_b0_tile * data_size + (c0_b0_tile * c1_b0_tile * c5_b0_tile * data_size + c0_b0_tile * c1_b0_tile *   data_size) + c4_b0_tile * data_size"
# read_write_l1_constraint = None
# read_write_l2_constraint = None
# read_write_constraint = None


# Auto-generated objective function
objective_function = "270 * c0_b0_blocks * c1_b0_blocks * 21.6 + c0_b0_blocks * c1_b0_blocks * c4_b0_blocks * c5_b0_blocks * 18.81 "
