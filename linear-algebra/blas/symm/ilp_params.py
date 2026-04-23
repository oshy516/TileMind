# Auto-generated parameters for ILP tiling

# Cache parameters
L1_size = 49152  # L1 data cache size in bytes
L2_size = 2097152  # L2 cache size in bytes
cache_line = 64  # Cache line size in bytes


# Parallelization information
num_threads = 16  # Number of physical cores

# 循环变量信息
# 原始变量到唯一变量的映射
# c0 -> ['c0_b0', 'c0_b1']
# c1 -> ['c1_b0', 'c1_b1']
# c2 -> ['c2_b0', 'c2_b1']

loop_vars = ['c0_b0', 'c1_b0', 'c2_b0', 'c0_b1', 'c1_b1', 'c2_b1']  # 循环变量列表

# 循环变量尺寸
c0_b0_size = 2000  # 循环变量 c0 在块 0 中的维度大小
c1_b0_size = 2600  # 循环变量 c1 在块 0 中的维度大小
c2_b0_size = 2000  # 循环变量 c2 在块 0 中的维度大小
c0_b1_size = 2600  # 循环变量 c0 在块 1 中的维度大小
c1_b1_size = 1999  # 循环变量 c1 在块 1 中的维度大小
c2_b1_size = 2000  # 循环变量 c2 在块 1 中的维度大小

# 按块组织的循环变量
# 块 0 中的循环变量: ['c0_b0', 'c1_b0', 'c2_b0']
# 块 1 中的循环变量: ['c0_b1', 'c1_b1', 'c2_b1']

# Data type information
data_type = 'double'
data_size = 8  # Size in bytes

openmp_parallel_blocks = {
    0: False,
    1: True,
}


# Tileable dimensions for each block
block_tileable_dims = {
    0: {
        'c0_b0': True,  # Variable can be tiled
        'c1_b0': True,  # Variable can be tiled
        'c2_b0': False,  # Variable CANNOT be tiled - use tile size 1
    },
    1: {
        'c0_b1': True,  # Variable can be tiled
        'c1_b1': True,  # Variable can be tiled
        'c2_b1': True,  # Variable can be tiled
    },
}

# Block-specific array layout information
block_array_layout = {
    0: {
        # Multi-dimensional arrays
        'A': 'row_major',  # 2D array, dims: c0_b0, c2_b0
        'B': 'column_major',  # 2D array, dims: c0_b0, c1_b0, c2_b0
        'C': 'row_major',  # 2D array, dims: c0_b0, c1_b0
    },
    1: {
        # Multi-dimensional arrays
        'A': 'column_major',  # 2D array, dims: c1_b1, c2_b1
        'B': 'column_major',  # 2D array, dims: c0_b1, c2_b1
        'C': 'column_major',  # 2D array, dims: c0_b1, c1_b1
    },
}

# Array dimension variables information
array_dimension_vars = {
    'A': {
        0: ['c0_b0', 'c2_b0'],
        1: ['c1_b1', 'c2_b1'],
    },
    'B': {
        0: ['c0_b0', 'c1_b0', 'c2_b0'],
        1: ['c0_b1', 'c2_b1'],
    },
    'C': {
        0: ['c0_b0', 'c1_b0'],
        1: ['c0_b1', 'c1_b1'],
    },
}

# Block-specific column-major layout information
block_is_column_major = {
    0: True,  # Block primarily uses column-major arrays
    1: True,  # Block primarily uses column-major arrays
}

# 数组的列主序关键维度
array_column_major_dims = {
    'A': {
        1: ['c1_b1'],  # 列主序
    },
    'B': {
        0: ['c1_b0'],  # 列主序
        1: ['c0_b1'],  # 列主序
    },
    'C': {
        1: ['c0_b1'],  # 列主序
    },
}

# Statement costs (nanoseconds)
T_op1 = 8.44  # Statement 1 cost (block 0)
T_op2 = 28.5  # Statement 2 cost (block 0)
T_op3 = 24.669999999999998  # Statement 3 cost (block 1)

# Cache access latencies (nanoseconds)
T_L1 = 3.07  # L1 cache access latency
T_L2 = 7.35  # L2 cache access latency

# Operation latencies (nanoseconds)
T_add = 0.77  # Double addition latency
T_mul = 1.53  # Double multiplication latency

# Detailed operation costs
stmt_count = 3
# Block-specific objective functions
block_0_objective = "c0_b0_blocks * c1_b0_blocks * 2000 * 8.44 + c0_b0_blocks * c1_b0_blocks * 28.50"
block_1_objective = "c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * 24.67"

# Combined cache constraints for ILP model
# Cache constraints for ILP model

# Block 0 specific constraints
block_0_read_only_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c0_b0_tile * data_size"
block_0_l1_lower_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size) > L1_size"
block_0_l2_upper_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size) <= L2_size"
block_0_read_write_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size)"

# Block 1 specific constraints
block_1_read_only_constraint = "c2_b1_tile * c0_b1_tile * data_size + c2_b1_tile * c1_b1_tile * data_size"
block_1_l1_lower_constraint = "c1_b1_tile * c0_b1_tile * data_size > L1_size"
block_1_l2_upper_constraint = "c1_b1_tile * c0_b1_tile * data_size <= L2_size"
block_1_read_write_constraint = "c1_b1_tile * c0_b1_tile * data_size"

# Global constraints (aggregated across all blocks)
read_only_constraint = "c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c0_b0_tile * data_size + c2_b1_tile * c0_b1_tile * data_size + c2_b1_tile * c1_b1_tile * data_size"
read_write_l1_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size) + c1_b1_tile * c0_b1_tile * data_size > L1_size"
read_write_l2_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size) + c1_b1_tile * c0_b1_tile * data_size <= L2_size"
read_write_constraint = "(c0_b0_tile * c1_b0_tile * data_size + c0_b0_tile * c1_b0_tile * data_size) + c1_b1_tile * c0_b1_tile * data_size"

# Auto-generated objective function
objective_function = "(c0_b0_blocks * c1_b0_blocks * 2000 * 8.44 + c0_b0_blocks * c1_b0_blocks * 28.50) + (c0_b1_blocks * c1_b1_blocks * c2_b1_blocks * 24.67)"
