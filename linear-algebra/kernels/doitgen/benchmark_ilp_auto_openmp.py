import pulp
import math
import numpy as np
import subprocess
import os
import sys
import itertools  # 添加这一行导入itertools模块
import time

# Run benchmark_preprocess_openmp.py if parameters file doesn't exist or argument provided
# if not os.path.exists('ilp_params.py') or len(sys.argv) > 1:
#     source_file = sys.argv[1] if len(sys.argv) > 1 else 'gemm.c'
#     print(f"Running benchmark_preprocess_openmp.py on {source_file}...")
#     subprocess.run(['python3', 'benchmark_preprocess_openmp.py', source_file])

# Import parameters from the generated file
try:
    from ilp_params import *
    print("Successfully imported parameters from ilp_params.py")
    # 调试输出
    print("\n=== Debug imported parameters ===")
    if 'objective_function' in globals():
        print(f"Found objective_function: {objective_function}")
    else:
        print("objective_function NOT found in globals()")
    
    # 检查ilp_params模块中的所有变量
    import ilp_params
    print("\nAll variables in ilp_params module:")
    for var in dir(ilp_params):
        if not var.startswith('__'):
            print(f"  {var}: {getattr(ilp_params, var)}")

except ImportError:
    print("Could not import ilp_params.py. Please run benchmark_preprocess_openmp.py first.")
    sys.exit(1)  # 如果找不到参数文件，直接退出
# 初始化一些默认值（如果需要）
if 'data_type' not in globals():
    data_type = 'double'
    data_size = 8
    
if 'T_L1' not in globals() or 'T_L2' not in globals():
    T_L1 = 1.0
    T_L2 = 10.0
    T_add = 3.0
    T_mul = 5.0

# 初始化 T_op 值（如果需要）
if 'T_op1' not in globals():
    if data_type == 'double':
        T_op1 = 2 * T_L2 + T_add
        T_op2 = 2 * T_L1 + 2 * T_L2 + 2 * T_mul + T_add
    else:
        T_op1 = 2 * T_L2 + T_add
        T_op2 = 2 * T_L1 + 2 * T_L2 + 2 * T_mul + T_add

# 初始化缓存约束变量
if 'read_only_constraint' not in globals():
    read_only_constraint = None
if 'read_write_constraint' not in globals():
    read_write_constraint = None


# Print loaded parameters for verification
print("\n=== Using the following parameters ===")
# 打印循环变量和维度大小
if 'loop_vars' in globals():
    loop_vars = list(dict.fromkeys(loop_vars))
    print("Loop variables and dimensions:")
    for var in loop_vars:
        var_size_name = f"{var}_size"
        if var_size_name in globals():
            print(f"  {var}: {globals()[var_size_name]}")
        else:
            print(f"  {var}: size not defined")
else:
    print("No loop variables found in parameters")

print(f"Cache: L1={L1_size/1024:.1f}KB, L2={L2_size/1024:.1f}KB, Line={cache_line}B")
print(f"Data type: {data_type} ({data_size} bytes)")
print(f"Cache latencies (ns): L1={T_L1:.2f}, L2={T_L2:.2f}")
print(f"Operation latencies (ns): Add={T_add:.2f}, Mul={T_mul:.2f}")
# 打印所有语句的成本
i = 1
while True:
    op_name = f'T_op{i}'
    if op_name in globals():
        print(f"Statement {i-1} cost: {globals()[op_name]:.2f} ns")
        i += 1
    else:
        break
print("=======================================\n")

def find_divisors(n):
    """Find all divisors of n"""
    divisors = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return sorted(divisors)

# # 过滤除数函数
# def filter_divisors(divisors, min_size=1, max_size=None):
#     """Filter divisors to be within practical limits"""
#     if max_size is None:
#         max_size = max(divisors)
#     return [d for d in divisors if min_size <= d <= max_size]

# # 为每个循环变量计算有效的分块大小
# valid_tiles = {}
# if 'loop_vars' in globals():
#     unique_loop_vars = list(dict.fromkeys(loop_vars))
#     for var in unique_loop_vars:
#         var_size_name = f"{var}_size"
#         if var_size_name in globals():
#             var_size = globals()[var_size_name]
#             tiles = find_divisors(var_size)
                
#             valid_tiles[var] = filter_divisors(tiles)
#             print(f"Valid tile sizes for {var}: {valid_tiles[var]}")
#         else:
#             # 如果找不到大小，使用默认值[1]
#             valid_tiles[var] = [1]
#             print(f"No size found for {var}, using default tile size [1]")
# else:
#     print("No loop variables found, cannot calculate tile sizes")
#     sys.exit(1)

# 修改filter_divisors函数，增加是否为并行块最外层循环的参数
# def filter_divisors(divisors, var, data_size, cache_line, min_size=1, max_size=None, is_outer_parallel=False):
#     """
#     过滤除数，确保它们与缓存行对齐（除非是并行块的最外层维度）
    
#     参数:
#     - divisors: 所有可能的分块大小列表
#     - var: 循环变量名
#     - data_size: 数据类型大小(字节)
#     - cache_line: 缓存行大小(字节)
#     - min_size: 最小分块大小
#     - max_size: 最大分块大小
#     - is_outer_parallel: 是否是并行块的最外层维度
    
#     返回:
#     - 过滤后的分块大小列表
#     """
#     if max_size is None:
#         max_size = max(divisors)
    
#     # 基本过滤：保留在指定范围内的值
#     filtered = [d for d in divisors if min_size <= d <= max_size]
    
#     # 如果是并行块的最外层维度，跳过缓存行对齐约束
#     if is_outer_parallel:
#         print(f"Skipping cache alignment for parallel outer dimension {var}")
#         return filtered
    
#     # 缓存行对齐过滤
#     # 计算一个缓存行可以容纳的元素数量
#     elements_per_line = cache_line // data_size
#     # print(f"Debug: cache_line={cache_line}, data_size={data_size}, elements_per_line={elements_per_line}")
#     # 对齐的分块大小列表
#     aligned = []
#     for d in filtered:
#         # 检查这个分块大小是否导致内存访问与缓存行对齐
#         if d % elements_per_line == 0 or elements_per_line % d == 0:
#             aligned.append(d)
    
#     # 如果没有找到对齐的值，返回原始过滤结果
#     if not aligned:
#         # print(f"Warning: No cache-aligned tile sizes found for {var}. Using unaligned sizes.")
#         return filtered
    
#     return aligned

# # 为每个循环变量计算有效的分块大小
# valid_tiles = {}
# if 'loop_vars' in globals():
#     unique_loop_vars = list(dict.fromkeys(loop_vars))
    
#     # 遍历每个循环变量
#     for var in unique_loop_vars:
#         var_size_name = f"{var}_size"
#         if var_size_name in globals():
#             var_size = globals()[var_size_name]
#             tiles = find_divisors(var_size)
            
#             # 检查这个变量是否是并行块的最外层循环
#             is_outer_parallel = False
#             if '_b' in var:
#                 block_idx = var.split('_b')[1]
#                 block_vars = [v for v in unique_loop_vars if f"_b{block_idx}" in v]
                
#                 # 如果当前变量是该块的第一个变量，并且该块是并行块
#                 if block_vars and var == block_vars[0] and 'openmp_parallel_blocks' in globals():
#                     block_idx_int = int(block_idx)
#                     if block_idx_int in globals()['openmp_parallel_blocks'] and globals()['openmp_parallel_blocks'][block_idx_int]:
#                         is_outer_parallel = True
#                         print(f"Identified {var} as parallel outer dimension of block {block_idx}")
            
#             # 对所有维度应用适当的过滤
#             valid_tiles[var] = filter_divisors(tiles, var, data_size, cache_line, is_outer_parallel=is_outer_parallel)
#             print(f"Valid tile sizes for {var}: {valid_tiles[var]}")
#         else:
#             # 如果找不到大小，使用默认值[1]
#             valid_tiles[var] = [1]
#             print(f"No size found for {var}, using default tile size [1]")
# else:
#     print("No loop variables found, cannot calculate tile sizes")
#     sys.exit(1)

def filter_divisors(divisors, var, data_size, cache_line, min_size=1, max_size=None):
    """
    智能筛选tile sizes，包括两类值:
    1. 维度大小的精选除数（智能筛选）
    2. 同时满足缓存行倍数和2的幂次的特殊值
    
    Args:
        divisors: 所有可能的分块大小列表（维度的除数）
        var: 循环变量名
        data_size: 数据类型大小（字节）
        cache_line: 缓存行大小（字节）
        min_size: 最小分块大小
        max_size: 最大分块大小
    
    Returns:
        筛选后的有效分块大小列表
    """
    if max_size is None:
        max_size = max(divisors)
    
    # 基本过滤：保留在指定范围内的除数
    raw_divisors = [d for d in divisors if min_size <= d <= max_size]
    
    # 计算一个缓存行可以容纳的元素数量
    elements_per_line = cache_line // data_size
    print(f"缓存行可容纳 {elements_per_line} 个元素（每个元素 {data_size} 字节）")
    
    # 获取变量尺寸（如果可用）
    var_size_name = f"{var}_size"
    var_size = 0
    if var_size_name in globals():
        var_size = globals()[var_size_name]
    else:
        # 如果找不到变量尺寸，使用最大除数作为近似
        var_size = max(raw_divisors) if raw_divisors else max_size
    
    max_val = min(var_size, max_size) if var_size > 0 else max_size
    
    # 智能筛选除数（而不是使用所有除数）
    filtered_divisors = smart_select_divisors(raw_divisors, var_size, elements_per_line)
    
    # 打印详细的过滤信息
    filtered_out = set(raw_divisors) - set(filtered_divisors)
    print(f"\n过滤详情（{var}）:")
    print(f"  原始除数列表（{len(raw_divisors)}个）: {raw_divisors}")
    print(f"  智能筛选后的除数（{len(filtered_divisors)}个）: {filtered_divisors}")
    print(f"  被过滤掉的除数（{len(filtered_out)}个）: {sorted(list(filtered_out))}")
    
    # 生成所有可能的2的幂次值（直到max_val）
    all_powers_of_2 = []
    power = 1
    while power <= max_val:
        all_powers_of_2.append(power)
        power *= 2
    
    # 生成所有可能的缓存行倍数（直到max_val）
    all_cache_multiples = []
    for i in range(1, (max_val // elements_per_line) + 1):
        val = i * elements_per_line
        if val <= max_val:
            all_cache_multiples.append(val)
    
    # 找出同时是缓存行倍数和2的幂次的特殊值
    special_tiles = set(all_cache_multiples) & set(all_powers_of_2)
    special_tiles_list = sorted(list(special_tiles))
    
    # 记录特殊值中哪些是新增的（不在原始除数中）
    new_special_tiles = special_tiles - set(raw_divisors)
    existing_special_tiles = special_tiles & set(raw_divisors)
    
    print(f"  特殊值（同时是缓存行倍数和2的幂次）（{len(special_tiles_list)}个）: {special_tiles_list}")
    print(f"  新增的特殊值（不在原始除数中）（{len(new_special_tiles)}个）: {sorted(list(new_special_tiles))}")
    print(f"  已存在的特殊值（也是原始除数）（{len(existing_special_tiles)}个）: {sorted(list(existing_special_tiles))}")
    
    # 合并两个集合：智能筛选的除数和特殊值
    all_tiles = set(filtered_divisors) | special_tiles
    
    # 与原始除数对比，看增加了哪些值，减少了哪些值
    added_values = all_tiles - set(raw_divisors)
    removed_values = set(raw_divisors) - all_tiles
    
    print(f"  最终结果与原始除数对比:")
    print(f"  - 新增值（{len(added_values)}个）: {sorted(list(added_values))}")
    print(f"  - 移除值（{len(removed_values)}个）: {sorted(list(removed_values))}")
    
    # 转换为排序列表
    result = sorted(list(all_tiles))
    
    # 打印统计信息
    print(f"\n{var} 的分块大小统计:")
    print(f"  - 原始除数: {len(raw_divisors)} 个")
    print(f"  - 智能筛选后的除数: {len(filtered_divisors)} 个")
    print(f"  - 2的幂次值: {len(all_powers_of_2)} 个")
    print(f"  - 缓存行倍数: {len(all_cache_multiples)} 个")
    print(f"  - 特殊值（同时是缓存行倍数和2的幂次）: {len(special_tiles_list)} 个")
    print(f"  - 合并后总计: {len(result)} 个有效分块大小")
    
    # 突出显示特殊值
    if special_tiles_list:
        print(f"  - 特殊值（同时是缓存行倍数和2的幂次）: {special_tiles_list}")
    
    # 如果没有找到有效的分块大小，使用合理的默认值
    if not result:
        print(f"警告: 没有找到 {var} 的有效分块大小。使用默认值。")
        # 尝试找到合理的默认值 - 优先使用缓存行大小
        if elements_per_line <= max_size:
            return [elements_per_line]
        else:
            return [min(raw_divisors)] if raw_divisors else [1]
    
    return result

def smart_select_divisors(divisors, dim_size, elements_per_line):
    """
    智能筛选除数，保留最有价值的选项
    
    策略:
    1. 总是保留小的除数（1-16）因为它们对于小的分块很重要
    2. 总是保留大的除数（dim_size/2, dim_size/4）因为它们对于减少块数很重要
    3. 优先保留接近缓存行倍数的除数
    4. 优先保留2的幂次或其附近的值
    5. 对于中等大小的除数，通过对数间隔进行抽样
    
    最多返回约20个值
    """
    if len(divisors) <= 20:
        return divisors  # 如果除数已经很少，则全部保留
    
    selected = set()
    
    # 记录每个策略选择的除数，用于调试
    small_divisors = [d for d in divisors if d <= 16]
    print(f"\n智能筛选过程细节:")
    print(f"  策略1 - 保留小除数: {small_divisors}")
    selected.update(small_divisors)
    
    # 2. 总是保留大的除数
    large_divisors = []
    if dim_size > 0:
        large_vals = [dim_size//4, dim_size//3, dim_size//2, dim_size]
        large_divisors = [d for d in divisors if d in large_vals or d >= dim_size/4]
        print(f"  策略2 - 保留大除数 (大于{dim_size}/4={dim_size/4}): {large_divisors}")
    else:
        # 如果不知道维度大小，保留最大的几个除数
        large_divisors = sorted(divisors)[-4:]
        print(f"  策略2 - 保留最大的几个除数: {large_divisors}")
    
    selected.update(large_divisors)
    
    # 3. 优先保留接近缓存行倍数的除数
    cache_related = []
    for i in range(1, 6):  # 检查前5个缓存行倍数
        cache_val = elements_per_line * i
        # 找出最接近的除数
        closest = min(divisors, key=lambda x: abs(x - cache_val))
        cache_related.append((closest, f"接近{cache_val}"))
        
        # 同时检查这个缓存行倍数的一半和两倍
        half_val = cache_val // 2
        double_val = cache_val * 2
        
        closest_half = min(divisors, key=lambda x: abs(x - half_val))
        cache_related.append((closest_half, f"接近{half_val}"))
        
        closest_double = min(divisors, key=lambda x: abs(x - double_val) if x <= dim_size else float('inf'))
        if closest_double <= dim_size:
            cache_related.append((closest_double, f"接近{double_val}"))
    
    print(f"  策略3 - 保留接近缓存行倍数的值: {cache_related}")
    selected.update([x[0] for x in cache_related])
    
    # 4. 优先保留2的幂次或其附近的值
    power_related = []
    power = 1
    while power <= max(divisors):
        # 找出最接近的除数
        closest = min(divisors, key=lambda x: abs(x - power))
        power_related.append((closest, f"接近2^{int(math.log2(power))}={power}"))
        power *= 2
    
    print(f"  策略4 - 保留接近2的幂次的值: {power_related}")
    selected.update([x[0] for x in power_related])
    
    # 5. 对于中等大小的除数，通过对数间隔进行抽样
    samples = []
    if len(selected) < 20:
        remaining = [d for d in divisors if d not in selected]
        remaining.sort()
        
        # 计算需要多少额外的值
        extra_needed = min(20 - len(selected), len(remaining))
        
        if extra_needed > 0 and remaining:
            if extra_needed == 1:
                # 如果只需要一个额外的值，选择中间的元素
                samples.append(remaining[len(remaining) // 2])
            else:
                # 对数间隔抽样
                indices = [int(i * (len(remaining) - 1) / (extra_needed - 1)) for i in range(extra_needed)]
                for idx in indices:
                    if idx < len(remaining):
                        samples.append(remaining[idx])
    
    print(f"  策略5 - 对数间隔抽样: {samples}")
    selected.update(samples)
    
    # 确保结果是排序的列表
    return sorted(list(selected))

# 更新调用filter_divisors的代码部分
valid_tiles = {}
if 'loop_vars' in globals():
    unique_loop_vars = list(dict.fromkeys(loop_vars))
    for var in unique_loop_vars:
        var_size_name = f"{var}_size"
        if var_size_name in globals():
            var_size = globals()[var_size_name]
            # 首先生成所有除数
            tiles = find_divisors(var_size)
            
            # 应用我们的组合筛选方法
            valid_tiles[var] = filter_divisors(tiles, var, data_size, cache_line)
            
            # 增强输出以便更好地理解结果
            print(f"\n{var} 的有效分块大小: {valid_tiles[var]}")
            
            # 检查除数
            divisor_tiles = [t for t in valid_tiles[var] if var_size % t == 0]
            print(f"  除数: {divisor_tiles}")
            
            # 检查缓存行倍数
            elements_per_line = cache_line // data_size
            cache_tiles = [t for t in valid_tiles[var] if t % elements_per_line == 0]
            print(f"  缓存行倍数: {cache_tiles}")
            
            # 检查2的幂次值
            power_tiles = []
            for tile in valid_tiles[var]:
                power = math.log2(tile)
                if power.is_integer():
                    power_tiles.append((tile, int(power)))
            
            print(f"  2的幂次: {[p[0] for p in power_tiles]}")
            
            # 检查特殊值（同时是缓存行倍数和2的幂次）
            special_tiles = [t for t in cache_tiles if math.log2(t).is_integer()]
            if special_tiles:
                print(f"  ★ 特殊值（同时是缓存行倍数和2的幂次）: {special_tiles}")
            
        else:
            # 如果找不到大小，使用默认值[1]
            valid_tiles[var] = [1]
            print(f"未找到 {var} 的大小，使用默认分块大小 [1]")
else:
    print("未找到循环变量，无法计算分块大小")
    sys.exit(1)

def apply_cache_constraints(prob, tile_vars, valid_tiles, loop_vars):
    """
    应用缓存约束到ILP模型
    使用循环变量名称作为分块名称
    """
    print("Applying cache constraints to ILP model...")
    
    try:
        # 应用只读数组L1缓存约束
        if 'read_only_constraint' in globals() and read_only_constraint is not None:
            print(f"Applying read-only L1 constraint: {read_only_constraint} <= L1_size")
            
            # 生成所有分块大小组合
            combinations = []
            for var in loop_vars:
                combinations.append([(var, t) for t in valid_tiles[var]])
            
            all_combinations = list(itertools.product(*combinations))
            
            for combo in all_combinations:
                # 设置每个变量的分块大小
                eval_vars = {}
                for var, t in combo:
                    eval_vars[f"{var}_tile"] = t
                
                # 评估约束
                try:
                    locals().update(eval_vars)
                    constraint_value = eval(read_only_constraint)
                    
                    if constraint_value > L1_size:
                        # 如果违反约束，创建一个限制这种组合的约束
                        constraint_name = f"ro_L1_" + "_".join([f"{var}_{t}" for var, t in combo])
                        prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                except Exception as e:
                    print(f"Error evaluating read-only constraint: {e}")
        
        # 应用读写数组L1和L2缓存约束
        if 'read_write_constraint' in globals() and read_write_constraint is not None:
            print(f"Applying read-write L1 and L2 constraints with expression: L1_size < {read_write_constraint} <= L2_size")
    
        # 生成所有分块大小组合
        combinations = []
        for var in loop_vars:
            combinations.append([(var, t) for t in valid_tiles[var]])
        
        all_combinations = list(itertools.product(*combinations))
        
        # L1下限约束: 工作集大小 > L1_size
        for combo in all_combinations:
            # 设置每个变量的分块大小
            eval_vars = {}
            for var, t in combo:
                eval_vars[f"{var}_tile"] = t
            
            # 评估约束
            try:
                locals().update(eval_vars)
                constraint_value = eval(read_write_constraint)
                
                # print(f"  Evaluating combo {combo}: {read_write_constraint} = {constraint_value}, L1_size = {L1_size}")
                
                if constraint_value <= L1_size:
                    # 如果违反L1下限约束，创建一个限制这种组合的约束
                    constraint_name = f"rw_L1_lower_" + "_".join([f"{var}_{t}" for var, t in combo])
                    prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                    # print(f"  Added L1 lower bound constraint: {constraint_name}")
            except Exception as e:
                print(f"  Error evaluating read-write L1 constraint for combo {combo}: {e}")
        
        # L2上限约束: 工作集大小 <= L2_size
        for combo in all_combinations:
            # 设置每个变量的分块大小
            eval_vars = {}
            for var, t in combo:
                eval_vars[f"{var}_tile"] = t
            
            # 评估约束
            try:
                locals().update(eval_vars)
                constraint_value = eval(read_write_constraint)
                
                # print(f"  Evaluating combo {combo}: {read_write_constraint} = {constraint_value}, L2_size = {L2_size}")
                
                if constraint_value > L2_size:
                    # 如果违反L2上限约束，创建一个限制这种组合的约束
                    constraint_name = f"rw_L2_upper_" + "_".join([f"{var}_{t}" for var, t in combo])
                    prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                    # print(f"  Added L2 upper bound constraint: {constraint_name}")
            except Exception as e:
                print(f"  Error evaluating read-write L2 constraint for combo {combo}: {e}")
    
    except (NameError, SyntaxError) as e:
        # 如果预处理没有生成有效的约束，使用默认约束
        print(f"Error applying constraints: {e}")
        print("Using default cache constraints...")
        
        # 生成所有分块大小组合
        combinations = []
        for var in loop_vars:
            combinations.append([(var, t) for t in valid_tiles[var]])
        
        all_combinations = list(itertools.product(*combinations))
        
        for combo in all_combinations:
            # 设置每个变量的分块大小
            eval_vars = {}
            for var, t in combo:
                eval_vars[f"{var}_tile"] = t
            
            # 计算工作集大小 (默认假设A、B、C矩阵)
            # 这里需要根据具体算法调整
            working_set_size = sum(t * data_size for var, t in combo)
            
            # L1约束
            if working_set_size > L1_size:
                constraint_name = f"default_L1_" + "_".join([f"{var}_{t}" for var, t in combo])
                prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
            
            # L2约束
            if working_set_size > L2_size:
                constraint_name = f"default_L2_" + "_".join([f"{var}_{t}" for var, t in combo])
                prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
    
    return prob


def apply_openmp_constraints(prob, tile_vars, var_to_size, loop_vars, num_threads):
    """应用OpenMP并行执行相关的约束，对每个计算块的最外层循环变量都进行约束"""
    print(f"Applying OpenMP constraints for {num_threads} threads...")
    
    # 确定所有计算块的最外层循环变量
    block_indices = set()
    for var in loop_vars:
        if '_b' in var:
            # 提取块索引
            block_idx = var.split('_b')[1]
            block_indices.add(block_idx)
    
    # 对每个块找到其最外层循环变量（假设是每个块的第一个变量）
    for block_idx in block_indices:
        # 找到该块的所有变量
        block_vars = [var for var in loop_vars if f"_b{block_idx}" in var]
        
        if not block_vars:
            continue  # 跳过空块
            
        # 假设第一个变量是最外层循环
        parallel_var = block_vars[0]
        
        print(f"Applying thread constraints to block {block_idx}, parallel variable: {parallel_var}")
        
        if parallel_var not in var_to_size:
            print(f"Cannot apply OpenMP constraints: dimension size for {parallel_var} not found")
            continue
        
        dim_size = var_to_size[parallel_var]
        
        # 遍历所有可能的分块大小
        for t in tile_vars[parallel_var]:
            # 计算此分块大小下的块数
            blocks = math.ceil(dim_size / t)
            
            # 约束1：块数必须大于等于线程数
            if blocks < num_threads:
                prob += tile_vars[parallel_var][t] <= 0
                print(f"  Excluding {parallel_var}={t} (produces only {blocks} blocks, less than {num_threads} threads)")
            
            # 约束2：块数应该能被线程数整除
            elif blocks % num_threads != 0:
                prob += tile_vars[parallel_var][t] <= 0
                print(f"  Excluding {parallel_var}={t} (produces {blocks} blocks, not divisible by {num_threads})")
            else:
                print(f"  {parallel_var}={t} produces {blocks} blocks, which is divisible by {num_threads} (acceptable)")
    
    return prob


def optimize_single_block(block_vars, var_to_size, block_idx, matrix_info, global_valid_tiles):
    """针对单个块优化分块大小，使用块特定的约束和目标函数"""
    print(f"\n==== Optimizing Block {block_idx} ====")
    print(f"Variables in this block: {block_vars}")
    
    # 创建LP问题
    prob = pulp.LpProblem(f"Block_{block_idx}_Tiling", pulp.LpMinimize)
    
    # 检查该块是否支持OpenMP并行化及其并行维度
    block_idx_int = int(block_idx)
    is_openmp_block = False
    parallel_dims = []
    global num_threads
    apply_thread_constraints = False  # 初始化变量

    if 'openmp_parallel_blocks' in globals():
        openmp_blocks = globals()['openmp_parallel_blocks']
        if block_idx_int in openmp_blocks and openmp_blocks[block_idx_int]:
            is_openmp_block = True
            print(f"Block {block_idx} supports OpenMP parallelization!")
            
            # 添加：获取并行维度信息
            if 'openmp_parallel_dims' in globals():
                parallel_dims_dict = globals()['openmp_parallel_dims']
                if block_idx_int in parallel_dims_dict:
                    parallel_dims = parallel_dims_dict[block_idx_int]
                    print(f"Parallel dimensions for block {block_idx}: {parallel_dims}")

    # 检查是否有OpenMP线程配置
    apply_thread_constraints = is_openmp_block and 'num_threads' in globals() and globals()['num_threads'] > 1
    if apply_thread_constraints:
        num_threads = globals()['num_threads']
        print(f"OpenMP thread constraints will be applied (num_threads = {num_threads})")
    else:
        print(f"No OpenMP parallelization will be applied for block {block_idx}")

    # 使用并行维度信息来确定哪个变量是并行外层维度
    parallel_outer_var = None
    if apply_thread_constraints:
        # Get non-tileable dimensions for this block
        non_tileable_dims = []
        if 'block_tileable_dims' in globals():
            if block_idx_int in globals()['block_tileable_dims']:
                block_tileable_info = globals()['block_tileable_dims'][block_idx_int]
                # Check which variables can't be tiled
                for var in block_vars:
                    if var in block_tileable_info and block_tileable_info[var] == False:
                        non_tileable_dims.append(var)
        
        # 首先尝试使用预先确定的并行维度
        if parallel_dims:
            for dim in parallel_dims:
                if dim in block_vars:
                    parallel_outer_var = dim
                    print(f"Using detected parallel dimension {parallel_outer_var}")
                    break
        
        # 如果没有找到预定义的并行维度，使用默认规则
        if parallel_outer_var is None:
            # 默认使用第一个可分块的变量
            for var in block_vars:
                if var not in non_tileable_dims:
                    parallel_outer_var = var
                    print(f"Using default parallel dimension {parallel_outer_var}")
                    break
            
            # 如果没有可分块变量，使用第一个变量
            if parallel_outer_var is None and block_vars:
                parallel_outer_var = block_vars[0]
                print(f"Using first variable {parallel_outer_var} as parallel dimension (no better option found)")
    
    # 为这个块的循环变量创建决策变量
    tile_vars = {}  # 循环变量 -> 分块大小变量字典
    block_var_to_size = {}  # 只包含这个块的变量维度大小
    block_vars_sizes = {}  # 循环变量 -> 块数变量
    valid_tiles = {}  # 循环变量 -> 有效分块大小列表

    # 获取不可分块的维度信息
    non_tileable_dims = []
    if 'block_tileable_dims' in globals():
        block_idx_int = int(block_idx)
        if block_idx_int in globals()['block_tileable_dims']:
            block_tileable_info = globals()['block_tileable_dims'][block_idx_int]
            # 检查当前块的每个变量是否可分块
            for var in block_vars:
                if var in block_tileable_info and block_tileable_info[var] == False:
                    non_tileable_dims.append(var)
                    print(f"Variable {var} in block {block_idx} CANNOT be tiled - will use tile size 1")
    
    if non_tileable_dims:
        print(f"Non-tileable dimensions in block {block_idx}: {non_tileable_dims}")

    # 检查是否为列主序块
    column_major_dims = []
    is_column_major = False
    # 从 array_column_major_dims 中读取列主序维度信息
    if 'array_column_major_dims' in globals():
        # 获取全局字典
        array_dims = globals()['array_column_major_dims']
        block_idx_int = int(block_idx)
        
        # 遍历每个数组
        for array_name, dim_info in array_dims.items():
            # 遍历每个维度索引
            for dim_idx, var_list in dim_info.items():
                # 检查当前块的变量是否在列主序维度列表中
                for var_name in var_list:
                    if var_name in block_vars:
                        column_major_dims.append(var_name)
                        print(f"Found column-major dimension {var_name} for array {array_name}")
        
        if column_major_dims:
            is_column_major = True
            print(f"Block {block_idx} has column-major dimensions: {column_major_dims}")
    else:
        print("No array_column_major_dims dictionary found in parameters")
    
    for var in block_vars:
        if var in non_tileable_dims:
            # 如果变量不可分块，则只允许使用分块大小1
            valid_tiles[var] = [1]
            tile_vars[var] = {1: pulp.LpVariable(f"{var}_tile_1", 1, 1, pulp.LpBinary)}
            print(f"Variable {var} is not tileable. Fixed tile size to 1.")
        elif var in global_valid_tiles:
            # 直接使用全局计算得到的有效分块大小列表
            valid_tiles[var] = global_valid_tiles[var]
            
            # 创建分块大小决策变量
            tile_vars[var] = {t: pulp.LpVariable(f"{var}_tile_{t}", 0, 1, pulp.LpBinary) for t in valid_tiles[var]}

            # 更新块变量尺寸信息
            if var in var_to_size:
                block_var_to_size[var] = var_to_size[var]

        else:
            # 如果没有找到维度大小，使用默认值
            valid_tiles[var] = [1]
            tile_vars[var] = {1: pulp.LpVariable(f"{var}_tile_1", 1, 1, pulp.LpBinary)}
            print(f"No dimension size found for {var}, using default tile size 1")
            
        # If no tileable variable found, use the first variable anyway
        if parallel_outer_var is None and block_vars:
            parallel_outer_var = block_vars[0]
            
        print(f"Identified {parallel_outer_var} as the parallel outer dimension for this block")

    # 为每个循环变量创建决策变量和计算有效分块大小
    for var in block_vars:
        if var in non_tileable_dims:
            # 如果变量不可分块，则只允许使用分块大小1
            valid_tiles[var] = [1]
            tile_vars[var] = {1: pulp.LpVariable(f"{var}_tile_1", 1, 1, pulp.LpBinary)}
            print(f"Variable {var} is not tileable. Fixed tile size to 1.")
        elif var in global_valid_tiles:
            # 对于并行块的最外层维度，我们使用重新计算的有效分块大小（不应用缓存行对齐约束）
            if apply_thread_constraints and var == parallel_outer_var:
                # 对于并行的最外层循环变量，我们需要重新计算可用的分块大小
                # 因为全局分块大小可能已经应用了缓存行对齐约束
                if var in var_to_size:
                    dim_size = var_to_size[var]
                    # 找到所有除数
                    original_tiles = find_divisors(dim_size)
                    # 只进行基本过滤，不应用缓存行对齐约束
                    filtered_tiles = [t for t in original_tiles if t >= 1]
                    
                    # 应用分级的线程相关约束
                    tiles_for_parallel = []
                    constraint_applied = "strict"
                    
                    # 第一级：严格约束
                    for t in filtered_tiles:
                        blocks = math.ceil(dim_size / t)
                        if blocks >= num_threads and blocks % num_threads == 0:
                            tiles_for_parallel.append(t)
                    
                    # 第二级：如果严格约束无解，释放整除约束
                    if not tiles_for_parallel:
                        constraint_applied = "relaxed"
                        for t in filtered_tiles:
                            blocks = math.ceil(dim_size / t)
                            if blocks >= num_threads:
                                tiles_for_parallel.append(t)
                    
                    # 第三级：如果仍无解，释放所有线程约束
                    if not tiles_for_parallel:
                        constraint_applied = "none"
                        tiles_for_parallel = filtered_tiles
                    
                    valid_tiles[var] = tiles_for_parallel
                    print(f"Recalculated tile sizes for parallel dimension {var} (constraint level: {constraint_applied}): {valid_tiles[var]}")
                else:
                    # 如果找不到维度大小，使用全局计算的分块大小
                    valid_tiles[var] = global_valid_tiles[var]
            else:
                # 对于非并行块或非最外层维度，使用全局计算的分块大小
                valid_tiles[var] = global_valid_tiles[var]
            
            # 创建分块大小决策变量
            tile_vars[var] = {t: pulp.LpVariable(f"{var}_tile_{t}", 0, 1, pulp.LpBinary) for t in valid_tiles[var]}

            # 更新块变量尺寸信息
            if var in var_to_size:
                block_var_to_size[var] = var_to_size[var]

        else:
            # 如果没有找到维度大小，使用默认值
            valid_tiles[var] = [1]
            tile_vars[var] = {1: pulp.LpVariable(f"{var}_tile_1", 1, 1, pulp.LpBinary)}
            print(f"No dimension size found for {var}, using default tile size 1")

    # 约束：每个维度必须选择一个分块大小
    for var in block_vars:
        prob += pulp.lpSum(tile_vars[var].values()) == 1, f"{var}_dimension_constraint"
    
    # 第1步：应用OpenMP并行化约束（仅当该块支持OpenMP并且有线程配置时）
    if apply_thread_constraints and parallel_outer_var is not None:
        if parallel_outer_var in block_var_to_size:
            dim_size = block_var_to_size[parallel_outer_var]
            
            print(f"Will use thread count: {num_threads}")
            
            # 尝试三级约束释放策略
            valid_for_thread_count = set()
            constraint_level = "strict"  # strict -> divisible_only -> none
            
            # 第一次尝试：严格约束（blocks >= num_threads AND blocks % num_threads == 0）
            for t in valid_tiles[parallel_outer_var]:
                blocks = math.ceil(dim_size / t)
                if blocks >= num_threads and blocks % num_threads == 0:
                    valid_for_thread_count.add(t)
            
            if valid_for_thread_count:
                print(f"Found tile sizes with strict thread constraints: {sorted(list(valid_for_thread_count))}")
            else:
                print(f"No tile sizes satisfy strict thread constraints. Relaxing divisibility constraint...")
                constraint_level = "divisible_only"
                
                # 第二次尝试：只要求blocks >= num_threads
                for t in valid_tiles[parallel_outer_var]:
                    blocks = math.ceil(dim_size / t)
                    if blocks >= num_threads:
                        valid_for_thread_count.add(t)
                
                if valid_for_thread_count:
                    print(f"Found tile sizes with relaxed constraints (>= threads only): {sorted(list(valid_for_thread_count))}")
                else:
                    print(f"No tile sizes satisfy >= thread constraint. Removing all thread constraints...")
                    constraint_level = "none"
                    valid_for_thread_count = set(valid_tiles[parallel_outer_var])
                    print(f"Using all available tile sizes: {sorted(list(valid_for_thread_count))}")
            
            print(f"Applied constraint level: {constraint_level}")
        
    # 打印缓存约束
    print("\n=== Applying cache constraints ===")
    
    # 检查是否有预先定义的块特定约束
    block_specific_ro_var = f"block_{block_idx}_read_only_constraint"
    block_specific_rw_var = f"block_{block_idx}_read_write_constraint"
    block_specific_obj_var = f"block_{block_idx}_objective"
    
    # 打印原始约束
    print("=== Original constraints ===")
    if 'read_only_constraint' in globals() and read_only_constraint is not None:
        print(f"Global read_only_constraint: {read_only_constraint}")
    else:
        print("No global read_only_constraint defined")
        
    if 'read_write_constraint' in globals() and read_write_constraint is not None:
        print(f"Global read_write_constraint: {read_write_constraint}")
    else:
        print("No global read_write_constraint defined")
    
    # 获取块特定约束
    block_ro_constraint = None
    if block_specific_ro_var in globals() and globals()[block_specific_ro_var] is not None:
        block_ro_constraint = globals()[block_specific_ro_var]
        print(f"Found block-specific read-only constraint: {block_ro_constraint}")
    else:
        # 如果没有预定义的块特定约束，则从全局约束中过滤
        if 'read_only_constraint' in globals() and read_only_constraint is not None:
            # 从全局约束中提取与当前块相关的项
            terms = []
            for term in read_only_constraint.split('+'):
                term = term.strip()
                block_relevant = False
                # 检查项是否包含当前块的任何变量
                for var in block_vars:
                    if f"{var}_tile" in term:
                        block_relevant = True
                        break
                
                if block_relevant:
                    terms.append(term)
            
            if terms:
                block_ro_constraint = " + ".join(terms)
                print(f"Found block-specific read-only constraint: {block_ro_constraint}")
            else:
                block_ro_constraint = None
                print("No block-specific read-only constraint found")
    
    block_rw_constraint = None
    if block_specific_rw_var in globals() and globals()[block_specific_rw_var] is not None:
        block_rw_constraint = globals()[block_specific_rw_var]
        print(f"Found block-specific read-write constraint: {block_rw_constraint}")
    else:
        # 如果没有预定义的块特定约束，则从全局约束中过滤
        if 'read_write_constraint' in globals() and read_write_constraint is not None:
            # 从全局约束中提取与当前块相关的项
            terms = []
            for term in read_write_constraint.split('+'):
                term = term.strip()
                block_relevant = False
                # 检查项是否包含当前块的任何变量
                for var in block_vars:
                    if f"{var}_tile" in term:
                        block_relevant = True
                        break
                
                if block_relevant:
                    terms.append(term)
            
            if terms:
                block_rw_constraint = " + ".join(terms)
                print(f"Found block-specific read-write constraint: {block_rw_constraint}")
            else:
                block_rw_constraint = None
                print("No block-specific read-write constraint found")
    
    # 打印过滤后的约束
    print("=== Filtered constraints for this block ===")
    if block_ro_constraint:
        print(f"Filtered read_only_constraint: {block_ro_constraint}")
    else:
        print("No filtered read_only_constraint for this block")
    
    if block_rw_constraint:
        print(f"Filtered read_write_constraint: {block_rw_constraint}")
    else:
        print("No filtered read_write_constraint for this block")
    
    # 生成所有分块大小组合
    combinations = []
    for var in block_vars:
        combinations.append([(var, t) for t in valid_tiles[var]])
    
    all_combinations = list(itertools.product(*combinations))
    print(f"Evaluating {len(all_combinations)} combinations")


    # **** 修改逻辑：直接使用预处理分析的数组信息 ****
    use_l1_optimization = False
    optimization_reason = ""
    
    try:
        # 直接从全局变量中读取已分析的数组信息
        all_arrays_accessed = set()
        read_only_arrays = set()
        read_write_arrays = set()
        
        # 从全局变量中获取预处理的数组分析结果
        if 'all_arrays_accessed' in globals():
            all_arrays_accessed = globals()['all_arrays_accessed']
        if 'read_only_arrays' in globals():
            read_only_arrays = globals()['read_only_arrays']
        if 'read_write_arrays' in globals():
            read_write_arrays = globals()['read_write_arrays']
        
        print(f"\nGlobal array analysis for cache strategy:")
        print(f"  All arrays accessed: {all_arrays_accessed}")
        print(f"  Read-write arrays: {read_write_arrays}")
        print(f"  Read-only arrays: {read_only_arrays}")
        
        # 应用修改后的缓存策略判断逻辑
        if len(all_arrays_accessed) == 1:
            use_l1_optimization = True
            optimization_reason = "Only one array globally"
        elif len(read_only_arrays) == 0 and len(all_arrays_accessed) > 0:
            use_l1_optimization = True
            optimization_reason = "All arrays are read-write globally"
        else:
            use_l1_optimization = False
            optimization_reason = "Mixed array types detected globally"
        
        print(f"=== Cache Strategy Decision ===")
        print(f"Strategy: {'L1 Optimization' if use_l1_optimization else 'Tiered Strategy'}")
        print(f"Reason: {optimization_reason}")
        
    except Exception as e:
        print(f"Error reading global array information: {e}")
        print("Falling back to block-level analysis")
        
        # 回退到原有的块级别分析逻辑
        use_l1_optimization = False
        
        if block_ro_constraint is not None:
            contains_tile_var = False
            for var in block_vars:
                if f"{var}_tile" in block_ro_constraint:
                    contains_tile_var = True
                    break
            
            if not contains_tile_var and block_rw_constraint is not None:
                use_l1_optimization = True
                optimization_reason = "Block-level analysis: Detected constant read-only constraint and read-write arrays"
        elif block_ro_constraint is None and block_rw_constraint is not None:
            use_l1_optimization = True
            optimization_reason = "Block-level analysis: No read-only constraint but has read-write constraint"

    # 评估只读数组的L1缓存约束
    if block_ro_constraint and not use_l1_optimization  :
        print("\n=== Evaluating read-only constraints ===")
        constraint_valid = False
        for combo in all_combinations[:5]:  # 测试前5个组合
            # 设置每个变量的分块大小
            eval_vars = {}
            for var, t in combo:
                eval_vars[f"{var}_tile"] = t
            
            # 评估约束
            try:
                locals().update(eval_vars)
                constraint_value = eval(block_ro_constraint)
                constraint_valid = True
                print(f"Sample evaluation for {combo}: {block_ro_constraint} = {constraint_value}")
                break
            except Exception as e:
                print(f"Error evaluating constraint for {combo}: {e}")
        
        if constraint_valid:
            for combo in all_combinations:
                # 设置每个变量的分块大小
                eval_vars = {}
                for var, t in combo:
                    eval_vars[f"{var}_tile"] = t
                
                # 评估约束
                try:
                    locals().update(eval_vars)
                    constraint_value = eval(block_ro_constraint)
                    
                    if constraint_value > L1_size:
                        # 如果违反约束，创建一个限制这种组合的约束
                        constraint_name = f"ro_L1_" + "_".join([f"{var}_{t}" for var, t in combo])
                        prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                except Exception as e:
                    pass
        else:
            print("Warning: Could not evaluate read-only constraint - skipping")
    
    # 评估读写约束
    if block_rw_constraint:
        print("\n=== Evaluating read-write constraints ===")
        # Check if L1 lower bound constraint might lead to infeasibility
        max_tile_combo = {}
        for var in block_vars:
            if var in valid_tiles and valid_tiles[var]:
                max_tile_combo[f"{var}_tile"] = max(valid_tiles[var])
        
        skip_l1_lower_constraint = False  # 添加这行初始化

        # 冲突检测：检查只读和读写约束是否会产生逻辑冲突
        if block_ro_constraint and not skip_l1_lower_constraint:
            print("\n=== Detecting constraint conflicts ===")
            conflict_detected = False
            feasible_count = 0
            total_checked = 0
            
            # 检查所有组合是否存在同时满足两种约束的解
            # 为了性能考虑，如果组合数过多（>1000），则采用智能采样
            if len(all_combinations) <= 1000:
                # 组合数不多，检查所有组合
                check_combinations = all_combinations
                print(f"Checking all {len(all_combinations)} combinations for conflicts...")
            else:
                # 组合数较多，使用分层采样：小中大分块大小各取一些
                print(f"Large combination space ({len(all_combinations)}), using stratified sampling...")
                check_combinations = []
                sample_var_tiles = {}
                for var in block_vars:
                    if var in valid_tiles:
                        tiles = valid_tiles[var]
                        # 取前几个、中间几个、后几个
                        sample_tiles = tiles[:3] + tiles[len(tiles)//3:len(tiles)//3+3] + tiles[-3:]
                        sample_var_tiles[var] = list(set(sample_tiles))  # 去重
                
                combinations = []
                for var in block_vars:
                    combinations.append([(var, t) for t in sample_var_tiles[var]])
                check_combinations = list(itertools.product(*combinations))
                print(f"Sampling {len(check_combinations)} representative combinations...")
            
            for combo in check_combinations:
                total_checked += 1
                eval_vars = {}
                for var, t in combo:
                    eval_vars[f"{var}_tile"] = t
                
                try:
                    locals().update(eval_vars)
                    rw_value = eval(block_rw_constraint)
                    ro_value = eval(block_ro_constraint)
                    
                    # 检查是否同时满足：L1 < rw_value <= L2 AND ro_value <= L1
                    rw_satisfies = (rw_value > L1_size) and (rw_value <= L2_size)
                    ro_satisfies = ro_value <= L1_size
                    
                    if rw_satisfies and ro_satisfies:
                        feasible_count += 1
                        # 找到可行解，可以提前退出检查
                        if feasible_count >= 5:  # 找到5个就够了
                            break
                except:
                    pass
            
            print(f"Checked {total_checked} combinations, found {feasible_count} feasible")
            
            if feasible_count == 0:
                print("CONFLICT DETECTED: No combinations satisfy both RO and RW constraints!")
                print("Read-write constraint requires working_set > L1_size")
                print("Read-only constraint requires working_set <= L1_size")
                print("Automatically enabling skip_l1_lower_constraint to resolve conflict")
                conflict_detected = True
                skip_l1_lower_constraint = True
            else:
                print(f"Found {feasible_count} potentially feasible combinations")
        # 添加全局检查逻辑
        if not skip_l1_lower_constraint:
            print("\n=== Checking if all combinations violate L1 lower bound ===")
            violated_count = 0
            total_count = len(all_combinations)
            
            for combo in all_combinations:
                eval_vars = {}
                for var, t in combo:
                    eval_vars[f"{var}_tile"] = t
                
                try:
                    locals().update(eval_vars)
                    constraint_value = eval(block_rw_constraint)
                    if constraint_value <= L1_size:
                        violated_count += 1
                except:
                    pass
            
            print(f"L1 lower bound violations: {violated_count}/{total_count} combinations")
            
            # 如果所有或绝大多数组合都违反L1下界，自动跳过这个约束
            if violated_count >= total_count * 0.8:  # 95%以上的组合都违反
                print("WARNING: Nearly all combinations violate L1 lower bound!")
                print("Automatically enabling skip_l1_lower_constraint to avoid infeasibility")
                skip_l1_lower_constraint = True
        
        # **** 修改逻辑：根据全局缓存策略应用约束 ****
        if use_l1_optimization:
            print(f"Using L1 optimization: forcing arrays to fit in L1 cache")
            print(f"Optimization reason: {optimization_reason}")
            skip_l1_lower_constraint = True
            
            # 评估在最大分块大小下的内存使用
            try:
                if max_tile_combo:
                    locals().update(max_tile_combo)
                    max_mem_usage = eval(block_rw_constraint)
                    print(f"Maximum possible memory usage with largest tiles: {max_mem_usage} bytes")
                    print(f"L1 cache size: {L1_size} bytes")
                    
                    if max_mem_usage > L1_size:
                        print(f"WARNING: Even largest tiles exceed L1 cache capacity")
                    else:
                        print(f"L1 optimization feasible: max usage <= L1 size")
            except Exception as e:
                print(f"Error calculating max memory usage: {e}")
        else:
            print(f"Using layered cache strategy: {optimization_reason}")
            print("Read-only arrays -> L1 cache, Read-write arrays -> L2 cache")
            
            # 原有的可行性检查逻辑
            try:
                if max_tile_combo:
                    locals().update(max_tile_combo)
                    max_mem_usage = eval(block_rw_constraint)
                    print(f"Maximum possible memory usage with largest tiles: {max_mem_usage} bytes")
                    print(f"L1 cache size: {L1_size} bytes")
                    
                    if max_mem_usage <= L1_size:
                        print("WARNING: L1 lower bound constraint would make problem infeasible!")
                        print("Skipping L1 lower bound constraint but keeping L2 upper bound constraint")
                        skip_l1_lower_constraint = True
            except Exception as e:
                print(f"Error calculating max memory usage: {e}")
        
        constraint_valid = False
        for combo in all_combinations[:5]:  # 测试前5个组合
            # 设置每个变量的分块大小
            eval_vars = {}
            for var, t in combo:
                eval_vars[f"{var}_tile"] = t
            
            # 评估约束
            try:
                locals().update(eval_vars)
                constraint_value = eval(block_rw_constraint)
                constraint_valid = True
                print(f"Sample evaluation for {combo}: {block_rw_constraint} = {constraint_value}")
                
                # L1下限约束
                if constraint_value <= L1_size:
                    if skip_l1_lower_constraint:
                        print(f"  Ignoring L1_size lower bound violation ({constraint_value} <= {L1_size})")
                    else:
                        print(f"  This violates L1_size lower bound ({constraint_value} <= {L1_size})")
                
                # L2上限约束
                if constraint_value > L2_size:
                    print(f"  This violates L2_size upper bound ({constraint_value} > {L2_size})")
                break
            except Exception as e:
                print(f"Error evaluating constraint for {combo}: {e}")
        
        if constraint_valid:
            for combo in all_combinations:
                # 设置每个变量的分块大小
                eval_vars = {}
                for var, t in combo:
                    eval_vars[f"{var}_tile"] = t
                
                try:
                    locals().update(eval_vars)
                    constraint_value = eval(block_rw_constraint)
                    
                    # **** 修改逻辑：根据全局缓存策略应用约束 ****
                    if use_l1_optimization:
                        # L1优化策略：只限制超过L1缓存大小的组合
                        if constraint_value > L1_size:
                            constraint_name = f"l1_opt_" + "_".join([f"{var}_{t}" for var, t in combo])
                            prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                    else:
                        # 分层策略：保持原有的L1下限和L2上限约束
                        # L1下限约束
                        if constraint_value <= L1_size and not skip_l1_lower_constraint:
                            constraint_name = f"rw_L1_lower_" + "_".join([f"{var}_{t}" for var, t in combo])
                            prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                        
                        # L2上限约束
                        if constraint_value > L2_size:
                            constraint_name = f"rw_L2_upper_" + "_".join([f"{var}_{t}" for var, t in combo])
                            prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                except Exception as e:
                    pass
        else:
            print("Warning: Could not evaluate read-write constraint - skipping")
    # 打印目标函数
    print("\n=== Objective Function ===")
    
    # 获取全局目标函数
    global_objective = None
    if 'objective_function' in globals():
        global_objective = objective_function
        print(f"Original objective function: {global_objective}")
    
    # 获取块特定的目标函数
    block_objective = None
    
    # 检查是否存在预定义的块特定目标函数
    if block_specific_obj_var in globals():
        block_objective = globals()[block_specific_obj_var]
        print(f"Found block-specific objective function: {block_objective}")
        
    elif 'block_objective_functions' in globals() and block_idx in globals()['block_objective_functions']:
        block_objective = globals()['block_objective_functions'][block_idx]
        print(f"Found block-specific objective from dict: {block_objective}")
    else:
        # 如果没有预定义的块特定目标函数，则从全局目标函数中提取
        if global_objective:
            # 分析全局目标函数，尝试提取与当前块相关的项
            terms = []
            for term in global_objective.split('+'):
                term = term.strip()
                block_relevant = False
                # 检查项是否包含当前块的任何变量
                for var in block_vars:
                    if f"{var}_blocks" in term:
                        block_relevant = True
                        break
                
                if block_relevant:
                    terms.append(term)
            
            if terms:
                block_objective = " + ".join(terms)
                print(f"Extracted block-specific objective: {block_objective}")
        
        # 如果仍然没有找到块特定目标函数，使用默认
        if not block_objective:
            if len(block_vars) >= 2:
                var1, var2 = block_vars[:2]
                block_objective = f"{var1}_blocks * {var2}_blocks * T_op{int(block_idx) + 1}"
                print(f"Using default objective: {block_objective}")
            elif len(block_vars) == 1:
                var1 = block_vars[0]
                block_objective = f"{var1}_blocks * T_op{int(block_idx) + 1}"
                print(f"Using default objective: {block_objective}")
            else:
                block_objective = f"T_op{int(block_idx) + 1}"
                print(f"Using default objective: {block_objective}")
    
    # 清理目标函数文本用于评估
    filtered_obj_fn = block_objective
    if isinstance(filtered_obj_fn, str):
        # 移除字典部分(如果存在)
        if ", {" in filtered_obj_fn:
            filtered_obj_fn = filtered_obj_fn.split(", {")[0]
        # 移除元组括号
        filtered_obj_fn = filtered_obj_fn.replace("(", "").replace(")", "")
        # 移除引号
        filtered_obj_fn = filtered_obj_fn.strip("'\"")
    
    # 计算目标函数值
    obj_values = {}  # 用于存储每种分块组合的目标函数值
    z_vars = {}      # 用于表示多个二进制变量的乘积
    
    # 构建用于评估的块数变量
    block_vars_sizes = {}
    for var in block_vars:
        if var in block_var_to_size:
            dim_size = block_var_to_size[var]
            # 计算每个分块大小对应的块数
            block_vars_sizes[var] = {t: math.ceil(dim_size / t) for t in valid_tiles[var]}
        else:
            block_vars_sizes[var] = {1: 1}  # 默认一个块
    
    # 评估样本目标函数
    print("\n=== Sample objective function evaluations (with thread penalties)  ===")
    for combo in all_combinations[:5]:  # 只评估前5个组合
        # 设置评估变量
        eval_vars = {}
        for var, t in combo:
            eval_vars[f"{var}_tile"] = t
            eval_vars[f"{var}_blocks"] = block_vars_sizes[var][t]
            
            # 如果是并行的最外层循环变量，计算每线程块数
            if apply_thread_constraints and var == block_vars[0]:
                blocks = block_vars_sizes[var][t]
                eval_vars[f"{var}_per_thread"] = math.ceil(blocks / num_threads)
            else:
                eval_vars[f"{var}_per_thread"] = block_vars_sizes[var][t]
        
        # 根据并行化情况修改目标函数
        modified_obj_fn = filtered_obj_fn
        if filtered_obj_fn and apply_thread_constraints and block_vars:
            modified_obj_fn = filtered_obj_fn.replace(f"{parallel_outer_var}_blocks", f"{parallel_outer_var}_per_thread")
            print(f"Modified objective for parallelization: {modified_obj_fn}")
        
        # 评估目标函数
        try:
            locals().update(eval_vars)
            base_obj_value = eval(modified_obj_fn)

            # 计算列主序维度的惩罚因子
            column_major_penalty = 0
            for var, t in combo:
                if var in column_major_dims and var in block_var_to_size:
                    dim_size = block_var_to_size[var]
                    tile_ratio = t / dim_size
                    
                    # 对小分块大小的列主序维度施加惩罚
                    if tile_ratio < 0.7:  # 如果分块大小小于维度大小的70%
                        column_major_penalty += 0.2 * base_obj_value * (1 - tile_ratio)
            
            # 将基本目标值和列主序惩罚因子相加
            combo_key = tuple(sorted(combo))
            obj_values[combo_key] = base_obj_value + column_major_penalty 
            
            # 打印样本评估结果
            print(f"Combination {combo}:")
            print(f"  Base objective: {base_obj_value:.2f}")
            if column_major_penalty > 0:
                print(f"  Column-major penalty: +{column_major_penalty:.2f}")
            print(f"  Total: {obj_values[combo_key]:.2f}")
            
        except Exception as e:
            print(f"Error evaluating objective function for {combo}: {e}")
            # 回退方案: 使用块数总和
            combo_key = tuple(sorted(combo))
            if apply_thread_constraints and block_vars:
                # 考虑并行化
                outer_var = block_vars[0]
                blocks_sum = eval_vars.get(f"{outer_var}_per_thread", 1)
                for var in block_vars[1:]:
                    blocks_sum += eval_vars.get(f"{var}_blocks", 1)
            else:
                # 不考虑并行化
                blocks_sum = sum(eval_vars.get(f"{var}_blocks", 1) for var in block_vars)
            
            obj_values[combo_key] = blocks_sum
            print(f"Using fallback objective value: {blocks_sum:.2f}")
    
    # 计算所有组合的目标函数值（包括线程惩罚）
    for combo in all_combinations:
        # 创建组合键
        combo_key = tuple(sorted(combo))
        
        # 如果已经评估过，跳过
        if combo_key in obj_values:
            continue
        
        # 设置评估变量
        eval_vars = {}
        for var, t in combo:
            eval_vars[f"{var}_tile"] = t
            eval_vars[f"{var}_blocks"] = block_vars_sizes[var][t]
            
            # 如果是并行的最外层循环变量，计算每线程块数
            if apply_thread_constraints and var == block_vars[0]:
                blocks = block_vars_sizes[var][t]
                eval_vars[f"{var}_per_thread"] = math.ceil(blocks / num_threads)
            else:
                eval_vars[f"{var}_per_thread"] = block_vars_sizes[var][t]
        
        # 根据并行化情况修改目标函数
        modified_obj_fn = filtered_obj_fn
        if filtered_obj_fn and apply_thread_constraints and block_vars:
            modified_obj_fn = filtered_obj_fn.replace(f"{parallel_outer_var}_blocks", f"{parallel_outer_var}_per_thread")
        
        # 评估目标函数
        try:
            locals().update(eval_vars)
            base_obj_value = eval(modified_obj_fn)

            # 计算列主序维度的惩罚因子
            column_major_penalty = 0
            for var, t in combo:
                if var in column_major_dims and var in block_var_to_size:
                    dim_size = block_var_to_size[var]
                    tile_ratio = t / dim_size
                    
                    # 对小分块大小的列主序维度施加惩罚
                    if tile_ratio < 0.7:  # 如果分块大小小于维度大小的70%
                        column_major_penalty += 0.2 * base_obj_value * (1 - tile_ratio)
            
            # 将基本目标值和列主序惩罚因子相加
            obj_values[combo_key] = base_obj_value + column_major_penalty

        except Exception as e:
            # 回退方案
            if apply_thread_constraints and block_vars:
                # 考虑并行化
                outer_var = block_vars[0]
                blocks_sum = eval_vars.get(f"{outer_var}_per_thread", 1)
                for var in block_vars[1:]:
                    blocks_sum += eval_vars.get(f"{var}_blocks", 1)
            else:
                # 不考虑并行化
                blocks_sum = sum(eval_vars.get(f"{var}_blocks", 1) for var in block_vars)
            
            obj_values[combo_key] = blocks_sum
    
    # 创建组合变量(z变量)
    for combo in all_combinations:
        combo_key = tuple(sorted(combo))
        
        # 创建一个z变量表示此组合
        z_name = "_".join([f"{var}_{t}" for var, t in combo])
        z_vars[combo_key] = pulp.LpVariable(f"z_{z_name}", 0, 1, pulp.LpBinary)
        
        # 添加线性化约束
        # z <= tile_var[var][t] 对所有 (var, t) in combo
        for var, t in combo:
            prob += z_vars[combo_key] <= tile_vars[var][t]
        
        # z >= sum(tile_var[var][t] for (var, t) in combo) - (len(combo) - 1)
        prob += z_vars[combo_key] >= pulp.lpSum(tile_vars[var][t] for var, t in combo) - (len(combo) - 1)
    
    # 定义目标函数
    obj_expr = pulp.lpSum(obj_values[combo_key] * z_vars[combo_key] for combo_key in z_vars)
    prob += obj_expr
    
    # 求解问题
    print(f"\nSolving Block {block_idx} ILP...")
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=1200))
    
    # 提取结果
    print(f"Block {block_idx} Status:", pulp.LpStatus[prob.status])
    
    if prob.status == pulp.LpStatusOptimal:
        # 提取每个变量的最优分块大小
        selected_tiles = {}
        
        for var in block_vars:
            for t in valid_tiles[var]:
                if pulp.value(tile_vars[var][t]) == 1:
                    selected_tiles[var] = t
                    break
            
            if var not in selected_tiles:
                # 如果没有找到，使用默认值
                selected_tiles[var] = valid_tiles[var][0]
                print(f"Warning: No value selected for {var}. Using default of {valid_tiles[var][0]}.")
        
        print(f"Block {block_idx} Tiling Results:")
        for var, tile in selected_tiles.items():
            print(f"  {var}_tile = {tile}")
        
        # 计算块的目标函数值
        eval_vars = {}
        for var, t in selected_tiles.items():
            if var in block_var_to_size:
                dim_size = block_var_to_size[var]
                # 这里dim_size的值可能不正确，可以添加打印语句验证
                print(f"Debug: {var} dimension size = {dim_size}, tile = {t}")
                eval_vars[f"{var}_tile"] = t

                #计算块数
                blocks = math.ceil(dim_size / t)
                print(f"Debug: Computing blocks for {var}: {dim_size} / {t} = {dim_size/t}, ceil = {blocks}")
                eval_vars[f"{var}_blocks"] = blocks

                # 如果是并行的最外层循环且启用了OpenMP，则块数除以线程数
                # 计算每线程块数
                if 'num_threads' in globals() and globals()['num_threads'] > 1 and var == block_vars[0]:
                    eval_vars[f"{var}_per_thread"] = math.ceil(blocks / num_threads)
                else:
                    eval_vars[f"{var}_per_thread"] = blocks
            else:
                eval_vars[f"{var}_tile"] = 1
                eval_vars[f"{var}_blocks"] = 1
                eval_vars[f"{var}_per_thread"] = 1

        # 修改目标函数中的最外层循环变量（如果使用并行化）
        modified_obj_fn = filtered_obj_fn
        if filtered_obj_fn and apply_thread_constraints and block_vars:
            modified_obj_fn = filtered_obj_fn.replace(f"{parallel_outer_var}_blocks", f"{parallel_outer_var}_per_thread")
            print(f"Modified objective function for final evaluation: {modified_obj_fn}")

        # 打印评估变量
        print("\nEvaluation variables for final calculation:")
        for var in block_vars:
            if f"{var}_blocks" in eval_vars:
                print(f"  {var}_blocks = {eval_vars[f'{var}_blocks']}")
            # 只为最外层循环显示per_thread值
            if var == block_vars[0] and apply_thread_constraints and f"{var}_per_thread" in eval_vars:
                print(f"  {var}_per_thread = {eval_vars[f'{var}_per_thread']}")

        # 计算最终的目标函数值
        # 计算最终的目标函数值，包括列主序惩罚
        try:
            locals().update(eval_vars)
            base_obj = eval(modified_obj_fn)
            print(f"Base objective value: {base_obj:.2f}")
            
            # 计算列主序维度的惩罚因子
            column_major_penalty = 0
            for var, t in selected_tiles.items():
                if var in column_major_dims and var in block_var_to_size:
                    dim_size = block_var_to_size[var]
                    tile_ratio = t / dim_size
                    
                    # 应用列主序惩罚因子
                    if tile_ratio < 0.7:  # 如果分块大小小于维度大小的70%
                        this_penalty = 0.2 * base_obj * (1 - tile_ratio)
                        column_major_penalty += this_penalty
                        print(f"Applied column-major penalty for {var}: +{this_penalty:.2f} (ratio: {tile_ratio:.2f})")
            
            # 计算最终的目标函数值
            total_obj = base_obj + column_major_penalty
            if column_major_penalty > 0:
                print(f"Final objective with column-major penalty: {total_obj:.2f} (+{column_major_penalty:.2f})")
            else:
                print(f"Final objective value: {total_obj:.2f} (no column-major penalty)")
            
        except Exception as e:
            print(f"Error calculating final objective for block {block_idx}: {e}")
            # 简单回退方案
            if apply_thread_constraints and block_vars:
                outer_var = block_vars[0]
                blocks_per_thread = eval_vars.get(f"{outer_var}_per_thread", 1)
                total_obj = blocks_per_thread * sum(eval_vars.get(f"{var}_blocks", 1) for var in block_vars[1:])
            else:
                total_obj = sum(eval_vars.get(f"{var}_blocks", 1) for var in block_vars)
            print(f"Using fallback objective value: {total_obj:.2f}")
        
        return selected_tiles, total_obj
    else:
        print(f"No optimal solution found for Block {block_idx}!")
        # 返回默认值并处理特殊情况
        default_tiles = {}
        
        # 为每个变量选择一个默认值，尝试尊重列主序约束和并行约束
        for var in block_vars:
            if not valid_tiles[var]:
                default_tiles[var] = 1
                continue
                
            if var in non_tileable_dims:
                # 不可分块的维度只能使用1
                default_tiles[var] = 1
            elif var in column_major_dims and var in block_var_to_size:
                # 列主序维度默认使用完整维度大小
                default_tiles[var] = block_var_to_size[var]
            elif apply_thread_constraints and var == block_vars[0] and var in block_var_to_size:
                # 对于并行的最外层循环，选择可被线程数整除的分块大小
                valid_parallel_tiles = []
                for t in valid_tiles[var]:
                    blocks = math.ceil(block_var_to_size[var] / t)
                    if blocks >= num_threads and blocks % num_threads == 0:
                        valid_parallel_tiles.append(t)
                
                if valid_parallel_tiles:
                    # 选择最小的有效分块大小（产生更多块以利用并行性）
                    default_tiles[var] = min(valid_parallel_tiles)
                else:
                    # 如果没有可被线程数整除的分块大小，选择最小的分块大小
                    default_tiles[var] = min(valid_tiles[var])
            else:
                # 对于其他维度，选择分块大小列表中值
                default_tiles[var] = valid_tiles[var][len(valid_tiles[var]) // 2]
        
        print("Using default tile sizes:")
        for var, tile in default_tiles.items():
            print(f"  {var}_tile = {tile}")
        
        return default_tiles, float('inf')

def solve_tiling_strategy(matrix_info):
    """
    求解ILP问题以找到最优分块大小
    使用循环变量名称作为分块名称，按块分别优化
    """
    # 获取循环信息
    loop_info = matrix_info.get('loop_info', {})
    
    # 获取循环变量
    loop_vars = list(dict.fromkeys(matrix_info.get('loop_info', {}).get('loop_vars', [])))
    
    # 构建变量到维度大小的映射
    var_to_size = {}
    for var in loop_vars:
        var_size_name = f"{var}_size"
        if var_size_name in globals():
            var_to_size[var] = globals()[var_size_name]
            print(f"Found dimension size for {var}: {var_to_size[var]}")
    
    # 更新矩阵信息
    matrix_info['var_to_size'] = var_to_size
    
    # 识别所有的块
    block_indices = set()
    for var in loop_vars:
        if '_b' in var:
            block_idx = var.split('_b')[1]
            block_indices.add(block_idx)
    
    # 按块分组变量
    block_to_vars = {}
    for block_idx in block_indices:
        block_to_vars[block_idx] = [var for var in loop_vars if f"_b{block_idx}" in var]
    
    # 存储每个块的最优结果
    block_results = {}
    total_objective = 0
    
    # 转换块索引为排序的整数列表（确保按数字大小排序）
    sorted_block_indices = sorted(block_indices, key=lambda x: int(x) if x.isdigit() else float('inf'))
    
    print(f"\n==== Processing blocks in order: {sorted_block_indices} ====")
    
    # 分别优化每个块，按排序后的顺序
    for block_idx in sorted_block_indices:
        block_vars = block_to_vars[block_idx]
        # block_solution, block_objective = optimize_single_block(block_vars, var_to_size, block_idx, matrix_info)
        block_solution, block_objective = optimize_single_block(block_vars, var_to_size, block_idx, matrix_info, valid_tiles)
        block_results[block_idx] = block_solution
        if block_objective != float('inf'):
            total_objective += block_objective
    
    # 合并所有块的结果
    final_solution = {}
    for block_idx, solution in block_results.items():
        final_solution.update(solution)
    
    print("\n==== Combined Results ====")
    print(f"Total objective value: {total_objective:.2f}")
    
    # 计算总块数
    total_blocks = 1
    for var in loop_vars:
        if var in var_to_size and var in final_solution:
            if 'num_threads' in globals() and num_threads > 1 and var == block_to_vars.get(var.split('_b')[1], [''])[0]:
                # 如果是块的最外层循环并且使用OpenMP
                blocks = math.ceil(var_to_size[var] / final_solution[var])
                total_blocks *= math.ceil(blocks / num_threads)
            else:
                total_blocks *= math.ceil(var_to_size[var] / final_solution[var])
    
    print(f"Total number of blocks: {total_blocks}")
    
    return final_solution, total_objective

# Run the analysis
if __name__ == "__main__":
    # 构建矩阵信息字典
    matrix_info = {
        'loop_info': {'loop_vars': loop_vars} if 'loop_vars' in globals() else {},
        'var_to_size': {}
    }   
    start_time = time.time()
    solution, obj_value = solve_tiling_strategy(matrix_info)  
    end_time = time.time()
    print(f"\nTotal ILP optimization time: {end_time - start_time:.2f} seconds")  
    if solution:
        print("\n=== Final Tiling Solution ===")
        for var, tile in solution.items():
            print(f"{var}_tile = {tile}")
            print(f"Estimated execution time: {obj_value:.2f} cycles")
        
        # Generate C code tile size definitions
        print("\nTo use these tile sizes in your code:")
        for var, tile in solution.items():
            print(f"#define {var.upper()}_TILE {tile}")