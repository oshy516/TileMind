# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 49152  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0']
# c1 -> ['c1_b0']
# c2 -> ['c2_b0']

loop_vars = ['c0_b0', 'c1_b0', 'c2_b0']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 4000  # Loop variable c0 in block 0
c1_b0_size = 4000  # Loop variable c1 in block 0
c2_b0_size = 4000  # Loop variable c2 in block 0

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c2_b0']


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b0, c1_b0, c2_b0
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        0: ['c0_b0', 'c1_b0', 'c2_b0'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: False,  # Block primarily uses row-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
    },
}

# Statement costs (nanoseconds)
T_op1 = 6.12  # Statement 1 cost (block 0)
T_op2 = 10.66  # Statement 2 cost (block 0)
T_op3 = 10.66  # Statement 3 cost (block 0)
T_op4 = 10.58  # Statement 4 cost (block 0)

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 6.12  # Statement 1 cost (block 0)
T_op2 = 10.66  # Statement 2 cost (block 0)
T_op3 = 10.66  # Statement 3 cost (block 0)
T_op4 = 10.58  # Statement 4 cost (block 0)

# Cache access latencies (nanoseconds)
T_L1 = 3.06  # L1 cache access latency
T_L2 = 7.30  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.75  # Double addition latency
T_sub = 0.74  # Double subtraction latency
T_mul = 1.48  # Double multiplication latency
T_div = 5.19  # Double division latency
T_sqrt = 7.52  # Double sqrt latency
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
        'sqrt': 7.52,
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
stmt_count = 4
# Block-specific objective functions
block_0_objective = "c0_b0_blocks * c1_b0_blocks * c1_b0_tile * 16.78 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c1_b0_tile * c2_b0_tile * 10.66 + c0_b0_blocks * 10.58"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c1_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c0_b0_tile * data_size + c0_b0_tile * c2_b0_tile * data_size + c1_b0_tile * c2_b0_tile * data_size)"
block_0_l1_lower_constraint = None
block_0_l2_upper_constraint = None
block_0_read_write_constraint = None

# Global constraints (aggregated across all blocks)
read_only_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c1_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c0_b0_tile * data_size + c0_b0_tile * c2_b0_tile * data_size + c1_b0_tile * c2_b0_tile * data_size)"
read_write_l1_constraint = None
read_write_l2_constraint = None
read_write_constraint = None

# Auto-generated objective function
objective_function = "(c0_b0_blocks * c1_b0_blocks * c1_b0_tile * 16.78 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c1_b0_tile * c2_b0_tile * 10.66 + c0_b0_blocks * 10.58)"
