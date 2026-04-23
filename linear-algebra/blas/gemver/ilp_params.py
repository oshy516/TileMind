# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 48683  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

# Parallelization information
num_threads = 16  # Number of physical cores

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1', 'c0_b2', 'c0_b3']
# c1 -> ['c1_b0', 'c1_b1', 'c1_b3']

loop_vars = ['c0_b0', 'c1_b0', 'c0_b1', 'c1_b1', 'c0_b2', 'c0_b3', 'c1_b3']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 4000  # Loop variable c0 in block 0
c1_b0_size = 4000  # Loop variable c1 in block 0
c0_b1_size = 4000  # Loop variable c0 in block 1
c1_b1_size = 4000  # Loop variable c1 in block 1
c0_b2_size = 1  # Non-tileable dimension
c0_b3_size = 4000  # Loop variable c0 in block 3
c1_b3_size = 4000  # Loop variable c1 in block 3

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_b1']
# 块 2 中的循环变量: ['c0_b2']
# 块 3 中的循环变量: ['c0_b3', 'c1_b3']


# OpenMP parallelizable blocks
# Block 0
# Block 1
# 
openmp_parallel_blocks = {
    0: True,
    1: True,
    2: True,
    3: True,
}

# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': False,  # Variable CANNOT be tiled - use tile size 1
    },
    3: {
        'c0_b3': True,  # Variable can be tiled
        'c1_b3': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b0, c1_b0
        # One-dimensional arrays
        'u1': 'row_major',  # 1D array, dims: c0_b0
        'u2': 'row_major',  # 1D array, dims: c0_b0
        'v1': 'row_major',  # 1D array, dims: c1_b0
        'v2': 'row_major',  # 1D array, dims: c1_b0
    },
    1: {
        # Multi-dimensional arrays
        'A': 'column_major',  # 2D array, dims: c0_b1, c1_b1
        # One-dimensional arrays
        'x': 'row_major',  # 1D array, dims: c0_b1
        'y': 'row_major',  # 1D array, dims: c1_b1
    },
    2: {
        # One-dimensional arrays
        'x': 'row_major',  # 1D array, dims: c0_b2
        'z': 'row_major',  # 1D array, dims: c0_b2
    },
    3: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b3, c1_b3
        # One-dimensional arrays
        'w': 'row_major',  # 1D array, dims: c0_b3
        'x': 'row_major',  # 1D array, dims: c1_b3
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        0: ['c0_b0', 'c1_b0'],
        1: ['c0_b1', 'c1_b1'],
        3: ['c0_b3', 'c1_b3'],
    },
    'u1': {
        0: ['c0_b0'],
    },
    'u2': {
        0: ['c0_b0'],
    },
    'v1': {
        0: ['c1_b0'],
    },
    'v2': {
        0: ['c1_b0'],
    },
    'w': {
        3: ['c0_b3'],
    },
    'x': {
        1: ['c0_b1'],
        2: ['c0_b2'],
        3: ['c1_b3'],
    },
    'y': {
        1: ['c1_b1'],
    },
    'z': {
        2: ['c0_b2'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: False,  # Block primarily uses row-major arrays
    1: True,  # Block primarily uses column-major arrays
    2: False,  # Block primarily uses row-major arrays
    3: False,  # Block primarily uses row-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
        1: ['c0_b1'],  # 列主序
    },
    'u1': {
    },
    'u2': {
    },
    'v1': {
    },
    'v2': {
    },
    'w': {
    },
    'x': {
    },
    'y': {
    },
    'z': {
    },
}

# Statement costs (nanoseconds)
T_op1 = 24.37  # Statement 1 cost (block 0)
T_op2 = 21.800000000000004  # Statement 2 cost (block 1)
T_op3 = 11.35  # Statement 3 cost (block 2)
T_op4 = 26.19  # Statement 4 cost (block 3)

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': False,  # Variable CANNOT be tiled - use tile size 1
    },
    3: {
        'c0_b3': True,  # Variable can be tiled
        'c1_b3': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 24.37  # Statement 1 cost (block 0)
T_op2 = 21.800000000000004  # Statement 2 cost (block 1)
T_op3 = 11.35  # Statement 3 cost (block 2)
T_op4 = 26.19  # Statement 4 cost (block 3)

# Cache access latencies (nanoseconds)
T_L1 = 3.10  # L1 cache access latency
T_L2 = 7.49  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.76  # Double addition latency
T_sub = 0.74  # Double subtraction latency
T_mul = 1.48  # Double multiplication latency
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
stmt_count = 4
# Block-specific objective functions
block_0_objective = "c0_b0_blocks * c1_b0_blocks * 24.37"
block_1_objective = "c0_b1_blocks * c1_b1_blocks * 21.80"
block_2_objective = "4000 * 11.35"
block_3_objective = "c0_b3_blocks * c1_b3_blocks * 26.19"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "c0_b0_tile * data_size + c1_b0_tile * data_size + c0_b0_tile * data_size + c1_b0_tile * data_size"
block_0_l1_lower_constraint = "c0_b0_tile * c1_b0_tile * data_size > L1_size"
block_0_l2_upper_constraint = "c0_b0_tile * c1_b0_tile * data_size <= L2_size"
block_0_read_write_constraint = "c0_b0_tile * c1_b0_tile * data_size"

# Block 1 specific constraints
block_1_read_only_constraint = "c1_b1_tile * data_size"
block_1_l1_lower_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size"

# Block 2 specific constraints
block_2_read_only_constraint = None
block_2_l1_lower_constraint = "data_size > L1_size"
block_2_l2_upper_constraint = "data_size <= L2_size"
block_2_read_write_constraint = "data_size"

# Block 3 specific constraints
block_3_read_only_constraint = None
block_3_l1_lower_constraint = "c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size > L1_size"
block_3_l2_upper_constraint = "c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size <= L2_size"
block_3_read_write_constraint = "c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size"

# Global constraints (aggregated across all blocks)
read_only_constraint = "c0_b0_tile * data_size + c1_b0_tile * data_size + c0_b0_tile * data_size + c1_b0_tile * data_size + c1_b1_tile * data_size"
read_write_l1_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size > L1_size"
read_write_l2_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size <= L2_size"
read_write_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size"

# Auto-generated objective function
objective_function = "(c0_b0_blocks * c1_b0_blocks * 24.37) + (c0_b1_blocks * c1_b1_blocks * 21.80) + (4000 * 11.35) + (c0_b3_blocks * c1_b3_blocks * 26.19)"
