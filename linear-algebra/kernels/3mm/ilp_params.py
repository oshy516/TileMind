# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 49512  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes

num_threads = 16 # Number of physical cores

# OpenMP parallelizable blocks
# Block 0
# Block 1
# Block 2
# 
openmp_parallel_blocks = {
    0: True,
    1: True,
    2: True,
}


# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1', 'c0_b2']
# c1 -> ['c1_b0', 'c1_b1', 'c1_b2']
# c2 -> ['c2_b0', 'c2_b1', 'c2_b2']

loop_vars = ['c0_b0', 'c1_b0', 'c2_b0', 'c0_b1', 'c1_b1', 'c2_b1', 'c0_b2', 'c1_b2', 'c2_b2']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 1800  # Loop variable c0 in block 0
c1_b0_size = 2200  # Loop variable c1 in block 0
c2_b0_size = 2400  # Loop variable c2 in block 0
c0_b1_size = 1600  # Loop variable c0 in block 1
c1_b1_size = 1800  # Loop variable c1 in block 1
c2_b1_size = 2000  # Loop variable c2 in block 1
c0_b2_size = 1600  # Loop variable c0 in block 2
c1_b2_size = 2200  # Loop variable c1 in block 2
c2_b2_size = 1800  # Loop variable c2 in block 2

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c2_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_b1', 'c2_b1']
# 块 2 中的循环变量: ['c0_b2', 'c1_b2', 'c2_b2']


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': True,  # Variable can be tiled
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
        'c2_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': True,  # Variable can be tiled
        'c1_b2': True,  # Variable can be tiled
        'c2_b2': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'C': 'row_major',  # 2D array, dims: c0_b0, c2_b0
        'D': 'column_major',  # 2D array, dims: c1_b0, c2_b0
        'F': 'row_major',  # 2D array, dims: c0_b0, c1_b0
    },
    1: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b1, c2_b1
        'B': 'column_major',  # 2D array, dims: c1_b1, c2_b1
        'E': 'row_major',  # 2D array, dims: c0_b1, c1_b1
    },
    2: {
        # Multi-dimensional arrays
        'E': 'row_major',  # 2D array, dims: c0_b2, c2_b2
        'F': 'column_major',  # 2D array, dims: c1_b2, c2_b2
        'G': 'row_major',  # 2D array, dims: c0_b2, c1_b2
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        1: ['c0_b1', 'c2_b1'],
    },
    'B': {
        1: ['c1_b1', 'c2_b1'],
    },
    'C': {
        0: ['c0_b0', 'c2_b0'],
    },
    'D': {
        0: ['c1_b0', 'c2_b0'],
    },
    'E': {
        1: ['c0_b1', 'c1_b1'],
        2: ['c0_b2', 'c2_b2'],
    },
    'F': {
        0: ['c0_b0', 'c1_b0'],
        2: ['c1_b2', 'c2_b2'],
    },
    'G': {
        2: ['c0_b2', 'c1_b2'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: True,  # Block primarily uses column-major arrays
    1: True,  # Block primarily uses column-major arrays
    2: True,  # Block primarily uses column-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
    },
    'B': {
        1: ['c1_b1'],  # 列主序
    },
    'C': {
    },
    'D': {
        0: ['c1_b0'],  # 列主序
    },
    'E': {
    },
    'F': {
        2: ['c1_b2'],  # 列主序
    },
    'G': {
    },
}

# Statement costs (nanoseconds)
T_op1 = 7.47  # Statement 1 cost (block 0)
T_op2 = 15.11  # Statement 2 cost (block 0)
T_op3 = 7.47  # Statement 3 cost (block 1)
T_op4 = 15.11  # Statement 4 cost (block 1)
T_op5 = 7.47  # Statement 5 cost (block 2)
T_op6 = 23.89  # Statement 6 cost (block 2)

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
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
        'c2_b1': True,  # Variable can be tiled
    },
    2: {
        'c0_b2': True,  # Variable can be tiled
        'c1_b2': True,  # Variable can be tiled
        'c2_b2': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
# Statement costs (nanoseconds)
T_op1 = 7.47  # Statement 1 cost (block 0)
T_op2 = 15.11  # Statement 2 cost (block 0)
T_op3 = 7.47  # Statement 3 cost (block 1)
T_op4 = 15.11  # Statement 4 cost (block 1)
T_op5 = 7.47  # Statement 5 cost (block 2)
T_op6 = 23.89  # Statement 6 cost (block 2)

# Cache access latencies (nanoseconds)
T_L1 = 3.08  # L1 cache access latency
T_L2 = 7.47  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.76  # Double addition latency
T_sub = 0.74  # Double subtraction latency
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
stmt_count = 6
# Block-specific objective functions
block_0_objective = "c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * 7.47 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c2_b0_tile * 15.11"
block_1_objective = "c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * 7.47 + c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * c2_b1_tile * 15.11"
block_2_objective = "c0_b2_blocks * c1_b2_blocks * c2_b2_blocks * 7.47 + c0_b2_blocks * c1_b2_blocks * c2_b2_blocks * c2_b2_tile * 23.89"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "c0_b0_tile * c2_b0_tile * data_size + c2_b0_tile * c1_b0_tile * data_size"
block_0_l1_lower_constraint = "c0_b0_tile * c1_b0_tile * data_size > L1_size"
block_0_l2_upper_constraint = "c0_b0_tile * c1_b0_tile * data_size <= L2_size"
block_0_read_write_constraint = "c0_b0_tile * c1_b0_tile * data_size"

# Block 1 specific constraints
block_1_read_only_constraint = "c0_b1_tile * c2_b1_tile * data_size + c2_b1_tile * c1_b1_tile * data_size"
block_1_l1_lower_constraint = "c0_b1_tile * c1_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c0_b1_tile * c1_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c0_b1_tile * c1_b1_tile * data_size"

# Block 2 specific constraints
block_2_read_only_constraint = None
block_2_l1_lower_constraint = "c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size > L1_size"
block_2_l2_upper_constraint = "c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size <= L2_size"
block_2_read_write_constraint = "c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size"

# Global constraints (aggregated across all blocks)
read_only_constraint = "c0_b0_tile * c2_b0_tile * data_size + c2_b0_tile * c1_b0_tile * data_size + c0_b1_tile * c2_b1_tile * data_size + c2_b1_tile * c1_b1_tile * data_size"
read_write_l1_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * c1_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size > L1_size"
read_write_l2_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * c1_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size <= L2_size"
read_write_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b1_tile * c1_b1_tile * data_size + c0_b2_tile * c1_b2_tile * data_size + c0_b2_tile * c2_b2_tile * data_size + c2_b2_tile * c1_b2_tile * data_size"

# Auto-generated objective function
objective_function = "(c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * 7.47 + c0_b0_blocks * c1_b0_blocks * c2_b0_blocks * c2_b0_tile * 15.11) + (c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * 7.47 + c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * c2_b1_tile * 15.11) + (c0_b2_blocks * c1_b2_blocks * c2_b2_blocks * 7.47 + c0_b2_blocks * c1_b2_blocks * c2_b2_blocks * c2_b2_tile * 23.89)"
