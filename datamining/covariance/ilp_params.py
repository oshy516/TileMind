# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 48683  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

# Parallelization information
num_threads = 16  # Number of physical cores

openmp_parallel_blocks = {
    1: True,
    2: True,
    4: True,
    5: True,
    6: True,
}
# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1', 'c0_b2', 'c0_b3', 'c0_b4', 'c0_b5', 'c0_b6']
# c1 -> ['c1_b1', 'c1_b2', 'c1_b4', 'c1_b5', 'c1_b6']
# c2 -> ['c2_b5']

loop_vars = ['c0_b0', 'c0_b1', 'c1_b1', 'c0_b2', 'c1_b2', 'c0_b3', 'c0_b4', 'c1_b4', 'c0_b5', 'c1_b5', 'c2_b5', 'c0_b6', 'c1_b6']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 1  # Non-tileable dimension
c0_b1_size = 2600  # Loop variable c0 in block 1
c1_b1_size = 3000  # Loop variable c1 in block 1
c0_b2_size = 2600  # Loop variable c0 in block 2
c1_b2_size = 2600  # Loop variable c1 in block 2
c0_b3_size = 1  # Non-tileable dimension
c0_b4_size = 3000  # Loop variable c0 in block 4
c1_b4_size = 2600  # Loop variable c1 in block 4
c0_b5_size = 2600  # Loop variable c0 in block 5
c1_b5_size = 2600  # Loop variable c1 in block 5
c2_b5_size = 3000  # Loop variable c2 in block 5
c0_b6_size = 2600  # Loop variable c0 in block 6
c1_b6_size = 2600  # Loop variable c1 in block 6

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_b1']
# 块 2 中的循环变量: ['c0_b2', 'c1_b2']
# 块 3 中的循环变量: ['c0_b3']
# 块 4 中的循环变量: ['c0_b4', 'c1_b4']
# 块 5 中的循环变量: ['c0_b5', 'c1_b5', 'c2_b5']
# 块 6 中的循环变量: ['c0_b6', 'c1_b6']


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': True,  # Variable can be tiled
        'c1_b2': True,  # Variable can be tiled
    },
    3: {
        'c0_b3': False,  # Variable CANNOT be tiled - use tile size 1
    },
    4: {
        'c0_b4': True,  # Variable can be tiled
        'c1_b4': True,  # Variable can be tiled
    },
    5: {
        'c0_b5': True,  # Variable can be tiled
        'c1_b5': True,  # Variable can be tiled
        'c2_b5': True,  # Variable can be tiled
    },
    6: {
        'c0_b6': True,  # Variable can be tiled
        'c1_b6': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # One-dimensional arrays
        'mean': 'row_major',  # 1D array, dims: c0_b0
    },
    1: {
        # Multi-dimensional arrays
        'data': 'column_major',  # 2D array, dims: c0_b1, c1_b1
        # One-dimensional arrays
        'mean': 'row_major',  # 1D array, dims: c0_b1
    },
    2: {
        # Multi-dimensional arrays
        'cov': 'row_major',  # 2D array, dims: c0_b2, c1_b2
    },
    3: {
        # One-dimensional arrays
        'mean': 'row_major',  # 1D array, dims: c0_b3
    },
    4: {
        # Multi-dimensional arrays
        'data': 'row_major',  # 2D array, dims: c0_b4, c1_b4
        # One-dimensional arrays
        'mean': 'row_major',  # 1D array, dims: c1_b4
    },
    5: {
        # Multi-dimensional arrays
        'cov': 'row_major',  # 2D array, dims: c0_b5, c1_b5
        'data': 'column_major',  # 2D array, dims: c0_b5, c1_b5, c2_b5
    },
    6: {
        # Multi-dimensional arrays
        'cov': 'column_major',  # 2D array, dims: c0_b6, c1_b6
    },
}

# Array dimension variables information
array_dimension_vars = {
    'cov': {
        2: ['c0_b2', 'c1_b2'],
        5: ['c0_b5', 'c1_b5'],
        6: ['c0_b6', 'c1_b6'],
    },
    'data': {
        1: ['c0_b1', 'c1_b1'],
        4: ['c0_b4', 'c1_b4'],
        5: ['c0_b5', 'c1_b5', 'c2_b5'],
    },
    'mean': {
        0: ['c0_b0'],
        1: ['c0_b1'],
        3: ['c0_b3'],
        4: ['c1_b4'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: False,  # Block primarily uses row-major arrays
    1: True,  # Block primarily uses column-major arrays
    2: False,  # Block primarily uses row-major arrays
    3: False,  # Block primarily uses row-major arrays
    4: False,  # Block primarily uses row-major arrays
    5: True,  # Block primarily uses column-major arrays
    6: True,  # Block primarily uses column-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'cov': {
        6: ['c1_b6', 'c0_b6'],  # 列主序
    },
    'data': {
        1: ['c0_b1'],  # 列主序
        5: ['c0_b5', 'c1_b5'],  # 列主序
    },
    'mean': {
    },
}

# Statement costs (nanoseconds)
T_op1 = 7.48  # Statement 1 cost (block 0)
T_op2 = 14.96  # Statement 2 cost (block 1)
T_op3 = 7.48  # Statement 3 cost (block 2)
T_op4 = 7.48  # Statement 4 cost (block 3)
T_op5 = 14.96  # Statement 5 cost (block 4)
T_op6 = 23.94  # Statement 6 cost (block 5)
T_op7 = 8.27  # Statement 7 cost (block 6)
T_op8 = 7.48  # Statement 8 cost (block 6)

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': True,  # Variable can be tiled
        'c1_b2': True,  # Variable can be tiled
    },
    3: {
        'c0_b3': False,  # Variable CANNOT be tiled - use tile size 1
    },
    4: {
        'c0_b4': True,  # Variable can be tiled
        'c1_b4': True,  # Variable can be tiled
    },
    5: {
        'c0_b5': True,  # Variable can be tiled
        'c1_b5': True,  # Variable can be tiled
        'c2_b5': True,  # Variable can be tiled
    },
    6: {
        'c0_b6': True,  # Variable can be tiled
        'c1_b6': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 7.48  # Statement 1 cost (block 0)
T_op2 = 14.96  # Statement 2 cost (block 1)
T_op3 = 7.48  # Statement 3 cost (block 2)
T_op4 = 7.48  # Statement 4 cost (block 3)
T_op5 = 14.96  # Statement 5 cost (block 4)
T_op6 = 23.94  # Statement 6 cost (block 5)
T_op7 = 8.27  # Statement 7 cost (block 6)
T_op8 = 7.48  # Statement 8 cost (block 6)

# Cache access latencies (nanoseconds)
T_L1 = 3.13  # L1 cache access latency
T_L2 = 7.48  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.76  # Double addition latency
T_sub = 0.79  # Double subtraction latency
T_mul = 1.50  # Double multiplication latency
T_div = 5.32  # Double division latency
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
stmt_count = 8
# Block-specific objective functions
block_0_objective = "2600 * 7.48"
block_1_objective = "c0_b1_blocks * c1_b1_blocks * 14.96"
block_2_objective = "c0_b2_blocks * c1_b2_blocks * 7.48"
block_3_objective = "2600 * 7.48"
block_4_objective = "c0_b4_blocks * c1_b4_blocks * 14.96"
block_5_objective = "c0_b5_blocks * c1_b5_blocks * c2_b5_blocks * 23.94"
block_6_objective = "c0_b6_blocks * c1_b6_blocks * 15.75"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = None
block_0_l1_lower_constraint = "data_size > L1_size"
block_0_l2_upper_constraint = "data_size <= L2_size"
block_0_read_write_constraint = "data_size"

# Block 1 specific constraints
block_1_read_only_constraint = None
block_1_l1_lower_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size"

# Block 2 specific constraints
block_2_read_only_constraint = None
block_2_l1_lower_constraint = "c0_b2_tile * c1_b2_tile * data_size > L1_size"
block_2_l2_upper_constraint = "c0_b2_tile * c1_b2_tile * data_size <= L2_size"
block_2_read_write_constraint = "c0_b2_tile * c1_b2_tile * data_size"

# Block 3 specific constraints
block_3_read_only_constraint = None
block_3_l1_lower_constraint = "data_size > L1_size"
block_3_l2_upper_constraint = "data_size <= L2_size"
block_3_read_write_constraint = "data_size"

# Block 4 specific constraints
block_4_read_only_constraint = None
block_4_l1_lower_constraint = "c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size > L1_size"
block_4_l2_upper_constraint = "c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size <= L2_size"
block_4_read_write_constraint = "c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size"

# Block 5 specific constraints
block_5_read_only_constraint = None
block_5_l1_lower_constraint = "c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size) > L1_size"
block_5_l2_upper_constraint = "c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size) <= L2_size"
block_5_read_write_constraint = "c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size)"

# Block 6 specific constraints
block_6_read_only_constraint = None
block_6_l1_lower_constraint = "(c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size) > L1_size"
block_6_l2_upper_constraint = "(c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size) <= L2_size"
block_6_read_write_constraint = "(c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size)"

# Global constraints (aggregated across all blocks)
read_only_constraint = None
read_write_l1_constraint = "data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + data_size + c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size + c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size) + (c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size) > L1_size"
read_write_l2_constraint = "data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + data_size + c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size + c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size) + (c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size) <= L2_size"
read_write_constraint = "data_size + c0_b1_tile * data_size + c1_b1_tile * c0_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + data_size + c0_b4_tile * c1_b4_tile * data_size + c1_b4_tile * data_size + c0_b5_tile * c1_b5_tile * data_size + (c2_b5_tile * c0_b5_tile * data_size + c2_b5_tile * c1_b5_tile * data_size) + (c0_b6_tile * c1_b6_tile * data_size + c1_b6_tile * c0_b6_tile * data_size)"

# Auto-generated objective function
objective_function = "(2600 * 7.48) + (c0_b1_blocks * c1_b1_blocks * 14.96) + (c0_b2_blocks * c1_b2_blocks * 7.48) + (2600 * 7.48) + (c0_b4_blocks * c1_b4_blocks * 14.96) + (c0_b5_blocks * c1_b5_blocks * c2_b5_blocks * 23.94) + (c0_b6_blocks * c1_b6_blocks * 15.75)"
