# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 49152  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes


# Parallelization information
num_threads = 16  # Number of physical cores

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1', 'c0_b2', 'c0_b3', 'c0_b4']
# c1 -> ['c1_b1', 'c1_b3']

loop_vars = ['c0_b0', 'c0_b1', 'c1_b1', 'c0_b2', 'c0_b3', 'c1_b3', 'c0_b4']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 1  # Non-tileable dimension
c0_b1_size = 2800  # Loop variable c0 in block 1
c1_b1_size = 2800  # Loop variable c1 in block 1
c0_b2_size = 1  # Non-tileable dimension
c0_b3_size = 2800  # Loop variable c0 in block 3
c1_b3_size = 2800  # Loop variable c1 in block 3
c0_b4_size = 1  # Non-tileable dimension

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_b1']
# 块 2 中的循环变量: ['c0_b2']
# 块 3 中的循环变量: ['c0_b3', 'c1_b3']
# 块 4 中的循环变量: ['c0_b4']

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes

openmp_parallel_blocks = {
    0: True,
    1: True,
    2: True,
    3: True,
    4: True,
}

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
        'c0_b2': False,  # Variable CANNOT be tiled - use tile size 1
    },
    3: {
        'c0_b3': True,  # Variable can be tiled
        'c1_b3': True,  # Variable can be tiled
    },
    4: {
        'c0_b4': False,  # Variable CANNOT be tiled - use tile size 1
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # One-dimensional arrays
        'tmp': 'row_major',  # 1D array, dims: c0_b0
    },
    1: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b1, c1_b1
        # One-dimensional arrays
        'tmp': 'row_major',  # 1D array, dims: c0_b1
        'x': 'row_major',  # 1D array, dims: c1_b1
    },
    2: {
        # One-dimensional arrays
        'y': 'row_major',  # 1D array, dims: c0_b2
    },
    3: {
        # Multi-dimensional arrays
        'B': 'row_major',  # 2D array, dims: c0_b3, c1_b3
        # One-dimensional arrays
        'x': 'row_major',  # 1D array, dims: c1_b3
        'y': 'row_major',  # 1D array, dims: c0_b3
    },
    4: {
        # One-dimensional arrays
        'tmp': 'row_major',  # 1D array, dims: c0_b4
        'y': 'row_major',  # 1D array, dims: c0_b4
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        1: ['c0_b1', 'c1_b1'],
    },
    'B': {
        3: ['c0_b3', 'c1_b3'],
    },
    'tmp': {
        0: ['c0_b0'],
        1: ['c0_b1'],
        4: ['c0_b4'],
    },
    'x': {
        1: ['c1_b1'],
        3: ['c1_b3'],
    },
    'y': {
        2: ['c0_b2'],
        3: ['c0_b3'],
        4: ['c0_b4'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: False,  # Block primarily uses row-major arrays
    1: False,  # Block primarily uses row-major arrays
    2: False,  # Block primarily uses row-major arrays
    3: False,  # Block primarily uses row-major arrays
    4: False,  # Block primarily uses row-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
    },
    'B': {
    },
    'tmp': {
    },
    'x': {
    },
    'y': {
    },
}

# Statement costs (nanoseconds)
T_op1 = 7.42  # Statement 1 cost (block 0)
T_op2 = 23.27  # Statement 2 cost (block 1)
T_op3 = 7.42  # Statement 3 cost (block 2)
T_op4 = 23.27  # Statement 4 cost (block 3)
T_op5 = 26.0  # Statement 5 cost (block 4)

# Cache access latencies (nanoseconds)
T_L1 = 3.09  # L1 cache access latency
T_L2 = 7.42  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.76  # Double addition latency
T_mul = 1.49  # Double multiplication latency

# Detailed operation costs
stmt_count = 5
# Block-specific objective functions
block_0_objective = "2800 * 7.42"
block_1_objective = "c0_b1_blocks * c1_b1_blocks * 23.27"
block_2_objective = "2800 * 7.42"
block_3_objective = "c0_b3_blocks * c1_b3_blocks * 23.27"
block_4_objective = "2800 * 26.00"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = None
block_0_l1_lower_constraint = "data_size > L1_size"
block_0_l2_upper_constraint = "data_size <= L2_size"
block_0_read_write_constraint = "data_size"

# Block 1 specific constraints tmp->L2
block_1_read_only_constraint = "c0_b1_tile * c1_b1_tile * data_size + c1_b1_tile * data_size"
block_1_l1_lower_constraint = "c0_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c0_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c0_b1_tile * data_size"

# # Block 1 specific constraints tmp->L1
# block_1_read_only_constraint = "c0_b1_tile * c1_b1_tile * data_size + c1_b1_tile * data_size +c0_b1_tile * data_size"
# block_1_l1_lower_constraint = None
# block_1_l2_upper_constraint = None
# block_1_read_write_constraint = None

# Block 2 specific constraints
block_2_read_only_constraint = None
block_2_l1_lower_constraint = "data_size > L1_size"
block_2_l2_upper_constraint = "data_size <= L2_size"
block_2_read_write_constraint = "data_size"

# Block 3 specific constraints y->L2
block_3_read_only_constraint = "c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size"
block_3_l1_lower_constraint = "c0_b3_tile * data_size > L1_size"
block_3_l2_upper_constraint = "c0_b3_tile * data_size <= L2_size"
block_3_read_write_constraint = "c0_b3_tile * data_size"

# # Block 3 specific constraints y->L1
# block_3_read_only_constraint = "c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size + c0_b3_tile * data_size"
# block_3_l1_lower_constraint = None
# block_3_l2_upper_constraint = None
# block_3_read_write_constraint = None

# Block 4 specific constraints
block_4_read_only_constraint = None
block_4_l1_lower_constraint = "data_size + data_size > L1_size"
block_4_l2_upper_constraint = "data_size + data_size <= L2_size"
block_4_read_write_constraint = "data_size + data_size"

# Global constraints (aggregated across all blocks)
read_only_constraint = "c0_b1_tile * c1_b1_tile * data_size + c1_b1_tile * data_size + c0_b3_tile * c1_b3_tile * data_size + c1_b3_tile * data_size"
read_write_l1_constraint = "data_size + c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + data_size + data_size > L1_size"
read_write_l2_constraint = "data_size + c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + data_size + data_size <= L2_size"
read_write_constraint = "data_size + c0_b1_tile * data_size + data_size + c0_b3_tile * data_size + data_size + data_size"

# Auto-generated objective function
objective_function = "(2800 * 7.42) + (c0_b1_blocks * c1_b1_blocks * 23.27) + (2800 * 7.42) + (c0_b3_blocks * c1_b3_blocks * 23.27) + (2800 * 26.00)"
