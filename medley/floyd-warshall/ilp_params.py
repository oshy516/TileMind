# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 48683  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0']
# c1 -> ['c1_b0']
# c2 -> ['c2_b0']

loop_vars = ['c0_b0', 'c1_b0', 'c2_b0']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 1  # Non-tileable dimension
c1_b0_size = 5600  # Loop variable c1 in block 0
c2_b0_size = 5600  # Loop variable c2 in block 0

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c2_b0']


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'path': 'column_major',  # 2D array, dims: c0_b0, c1_b0, c2_b0
    },
}

# Array dimension variables information
array_dimension_vars = {
    'path': {
        0: ['c0_b0', 'c1_b0', 'c2_b0'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: True,  # Block primarily uses column-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'path': {
        0: ['c0_b0'],  # 列主序
    },
}

# Statement costs (nanoseconds)
T_op1 = 39.065000000000005  # Statement 1 cost (block 0)

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 39.065000000000005  # Statement 1 cost (block 0)

# Cache access latencies (nanoseconds)
T_L1 = 3.08  # L1 cache access latency
T_L2 = 7.32  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.81  # Double addition latency
T_sub = 0.74  # Double subtraction latency
T_mul = 1.49  # Double multiplication latency
T_div = 5.20  # Double division latency
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
stmt_count = 1
# Block-specific objective functions
block_0_objective = "5600 * c1_b0_blocks * c2_b0_blocks * 39.07"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "(c1_b0_tile * c2_b0_tile * data_size + c1_b0_tile * data_size + c2_b0_tile * data_size)"
block_0_l1_lower_constraint = None
block_0_l2_upper_constraint = None
block_0_read_write_constraint = None

# Global constraints (aggregated across all blocks)
read_only_constraint = "(c1_b0_tile * c2_b0_tile * data_size + c1_b0_tile * data_size + c2_b0_tile * data_size)"
read_write_l1_constraint = None
read_write_l2_constraint = None
read_write_constraint = None

# Auto-generated objective function
objective_function = "(5600 * c1_b0_blocks * c2_b0_blocks * 39.07)"
