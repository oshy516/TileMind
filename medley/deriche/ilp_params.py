# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 48683  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes


# Parallelization information
num_threads = 16  # Number of physical cores

# OpenMP parallelizable blocks
# Block 2
# Block 5
# 
openmp_parallel_blocks = {
    2: True,
    5: True,
}

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1', 'c0_b2', 'c0_b3', 'c0_b4']
# c1_0 -> ['c1_0_b0', 'c1_0_b1', 'c1_0_b2', 'c1_0_b3', 'c1_0_b4']

loop_vars = ['c0_b0', 'c1_0_b0', 'c0_b1', 'c1_0_b1', 'c0_b2', 'c1_0_b2', 'c0_b3', 'c1_0_b3', 'c0_b4', 'c1_0_b4']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 1  # Non-tileable dimension
c1_0_b0_size = 1  # Non-tileable dimension
c0_b1_size = 7680  # Loop variable c0 in block 1
c1_0_b1_size = 4320  # Loop variable c1_0 in block 1
c0_b2_size = 1  # Non-tileable dimension
c1_0_b2_size = 1  # Non-tileable dimension
c0_b3_size = 1  # Non-tileable dimension
c1_0_b3_size = 1  # Non-tileable dimension
c0_b4_size = 7680  # Loop variable c0 in block 4
c1_0_b4_size = 4320  # Loop variable c1_0 in block 4

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_0_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_0_b1']
# 块 2 中的循环变量: ['c0_b2', 'c1_0_b2']
# 块 3 中的循环变量: ['c0_b3', 'c1_0_b3']
# 块 4 中的循环变量: ['c0_b4', 'c1_0_b4']


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b0': False,  # Variable CANNOT be tiled - use tile size 1
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_0_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b2': False,  # Variable CANNOT be tiled - use tile size 1
    },
    3: {
        'c0_b3': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b3': False,  # Variable CANNOT be tiled - use tile size 1
    },
    4: {
        'c0_b4': True,  # Variable can be tiled
        'c1_0_b4': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'imgIn': 'row_major',  # 2D array, dims: c0_b0, c1_0_b0
        'y1': 'row_major',  # 2D array, dims: c0_b0, c1_0_b0
        'y2': 'row_major',  # 2D array, dims: c0_b0, c1_0_b0
    },
    1: {
        # Multi-dimensional arrays
        'imgOut': 'row_major',  # 2D array, dims: c0_b1, c1_0_b1
        'y1': 'row_major',  # 2D array, dims: c0_b1, c1_0_b1
        'y2': 'row_major',  # 2D array, dims: c0_b1, c1_0_b1
    },
    2: {
        # Multi-dimensional arrays
        'imgOut': 'column_major',  # 2D array, dims: c0_b2, c1_0_b2
        'y2': 'column_major',  # 2D array, dims: c0_b2, c1_0_b2
    },
    3: {
        # Multi-dimensional arrays
        'imgOut': 'column_major',  # 2D array, dims: c0_b3, c1_0_b3
        'y1': 'column_major',  # 2D array, dims: c0_b3, c1_0_b3
    },
    4: {
        # Multi-dimensional arrays
        'imgOut': 'row_major',  # 2D array, dims: c0_b4, c1_0_b4
        'y1': 'row_major',  # 2D array, dims: c0_b4, c1_0_b4
        'y2': 'row_major',  # 2D array, dims: c0_b4, c1_0_b4
    },
}

# Array dimension variables information
array_dimension_vars = {
    'imgIn': {
        0: ['c0_b0', 'c1_0_b0'],
    },
    'imgOut': {
        1: ['c0_b1', 'c1_0_b1'],
        2: ['c0_b2', 'c1_0_b2'],
        3: ['c0_b3', 'c1_0_b3'],
        4: ['c0_b4', 'c1_0_b4'],
    },
    'y1': {
        0: ['c0_b0', 'c1_0_b0'],
        1: ['c0_b1', 'c1_0_b1'],
        3: ['c0_b3', 'c1_0_b3'],
        4: ['c0_b4', 'c1_0_b4'],
    },
    'y2': {
        0: ['c0_b0', 'c1_0_b0'],
        1: ['c0_b1', 'c1_0_b1'],
        2: ['c0_b2', 'c1_0_b2'],
        4: ['c0_b4', 'c1_0_b4'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: False,  # Block primarily uses row-major arrays
    1: False,  # Block primarily uses row-major arrays
    2: True,  # Block primarily uses column-major arrays
    3: True,  # Block primarily uses column-major arrays
    4: False,  # Block primarily uses row-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'imgIn': {
    },
    'imgOut': {
        2: ['c0_b2'],  # 列主序
        3: ['c0_b3'],  # 列主序
    },
    'y1': {
        3: ['c0_b3'],  # 列主序
    },
    'y2': {
        2: ['c0_b2'],  # 列主序
    },
}

# Statement costs (nanoseconds)
T_op1 = 15.52  # Statement 1 cost (block 0)
T_op2 = 18.61  # Statement 2 cost (block 0)
T_op3 = 3.09  # Statement 3 cost (block 0)
T_op4 = 7.31  # Statement 4 cost (block 0)
T_op5 = 7.31  # Statement 5 cost (block 0)
T_op6 = 3.09  # Statement 6 cost (block 0)
T_op7 = 24.169999999999998  # Statement 7 cost (block 1)
T_op8 = 15.52  # Statement 8 cost (block 2)
T_op9 = 7.31  # Statement 9 cost (block 2)
T_op10 = 7.31  # Statement 10 cost (block 2)
T_op11 = 22.83  # Statement 11 cost (block 3)
T_op12 = 7.31  # Statement 12 cost (block 3)
T_op13 = 7.31  # Statement 13 cost (block 3)
T_op14 = 24.169999999999998  # Statement 14 cost (block 4)

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b0': False,  # Variable CANNOT be tiled - use tile size 1
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_0_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b2': False,  # Variable CANNOT be tiled - use tile size 1
    },
    3: {
        'c0_b3': False,  # Variable CANNOT be tiled - use tile size 1
        'c1_0_b3': False,  # Variable CANNOT be tiled - use tile size 1
    },
    4: {
        'c0_b4': True,  # Variable can be tiled
        'c1_0_b4': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 15.52  # Statement 1 cost (block 0)
T_op2 = 18.61  # Statement 2 cost (block 0)
T_op3 = 3.09  # Statement 3 cost (block 0)
T_op4 = 7.31  # Statement 4 cost (block 0)
T_op5 = 7.31  # Statement 5 cost (block 0)
T_op6 = 3.09  # Statement 6 cost (block 0)
T_op7 = 24.169999999999998  # Statement 7 cost (block 1)
T_op8 = 15.52  # Statement 8 cost (block 2)
T_op9 = 7.31  # Statement 9 cost (block 2)
T_op10 = 7.31  # Statement 10 cost (block 2)
T_op11 = 22.83  # Statement 11 cost (block 3)
T_op12 = 7.31  # Statement 12 cost (block 3)
T_op13 = 7.31  # Statement 13 cost (block 3)
T_op14 = 24.169999999999998  # Statement 14 cost (block 4)

# Cache access latencies (nanoseconds)
T_L1 = 3.09  # L1 cache access latency
T_L2 = 7.31  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.75  # Double addition latency
T_sub = 0.74  # Double subtraction latency
T_mul = 1.49  # Double multiplication latency
T_div = 5.21  # Double division latency
T_sqrt = 20.00  # Double sqrt latency
T_trig = 40.00  # Double trig function latency
T_log_exp = 15.83  # Double log/exp latency
T_pow = 34.76  # Double power function latency

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
        'log': 15.83,
        'log10': 15.83,
        'exp': 15.83,
        'pow': 34.76
    }
}


# Detailed operation costs
stmt_count = 14
# Block-specific objective functions
block_0_objective = "7680 * 4320 * 54.93"
block_1_objective = "c0_b1_blocks * c1_0_b1_blocks * 24.17"
block_2_objective = "4320 * 7680 * 30.14"
block_3_objective = "4320 * 7680 * 37.45"
block_4_objective = "c0_b4_blocks * c1_0_b4_blocks * 24.17"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "data_size"
block_0_l1_lower_constraint = "data_size + data_size > L1_size"
block_0_l2_upper_constraint = "data_size + data_size <= L2_size"
block_0_read_write_constraint = "data_size + data_size"

# Block 1 specific constraints
block_1_read_only_constraint = None
block_1_l1_lower_constraint = "c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size"

# Block 2 specific constraints
block_2_read_only_constraint = None
block_2_l1_lower_constraint = "data_size + data_size > L1_size"
block_2_l2_upper_constraint = "data_size + data_size <= L2_size"
block_2_read_write_constraint = "data_size + data_size"

# Block 3 specific constraints
block_3_read_only_constraint = None
block_3_l1_lower_constraint = "data_size + data_size > L1_size"
block_3_l2_upper_constraint = "data_size + data_size <= L2_size"
block_3_read_write_constraint = "data_size + data_size"

# Block 4 specific constraints
block_4_read_only_constraint = None
block_4_l1_lower_constraint = "c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size > L1_size"
block_4_l2_upper_constraint = "c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size <= L2_size"
block_4_read_write_constraint = "c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size"

# Global constraints (aggregated across all blocks)
read_only_constraint = "data_size"
read_write_l1_constraint = "data_size + data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + data_size + data_size + data_size + data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size > L1_size"
read_write_l2_constraint = "data_size + data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + data_size + data_size + data_size + data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size <= L2_size"
read_write_constraint = "data_size + data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + c0_b1_tile * c1_0_b1_tile * data_size + data_size + data_size + data_size + data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size + c0_b4_tile * c1_0_b4_tile * data_size"

# Auto-generated objective function
objective_function = "(7680 * 4320 * 54.93) + (c0_b1_blocks * c1_0_b1_blocks * 24.17) + (4320 * 7680 * 30.14) + (4320 * 7680 * 37.45) + (c0_b4_blocks * c1_0_b4_blocks * 24.17)"
