import re
import pulp
import math
import numpy as np
import subprocess
import os
import sys
import itertools  # 添加这一行导入itertools模块
import time

# Run benchmark_preprocess.py if parameters file doesn't exist or argument provided
# if not os.path.exists('ilp_params.py') or len(sys.argv) > 1:
#     source_file = sys.argv[1] if len(sys.argv) > 1 else 'gemm.c'
#     print(f"Running benchmark_preprocess.py on {source_file}...")
#     subprocess.run(['python3', 'benchmark_preprocess.py', source_file])

import importlib.util

# Determine which params file to use
params_file = 'ilp_params.py'
if len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
    params_file = sys.argv[1]

# Dynamic import of parameters from the generated file
module_name = os.path.splitext(os.path.basename(params_file))[0]
try:
    spec = importlib.util.spec_from_file_location(module_name, params_file)
    ilp_params = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = ilp_params
    spec.loader.exec_module(ilp_params)
    
    # Inject variables into global scope
    for var in dir(ilp_params):
        if not var.startswith('__'):
            globals()[var] = getattr(ilp_params, var)
            
    print(f"Successfully imported parameters from {params_file}")
    
    # 调试输出
    print("\n=== Debug imported parameters ===")
    if 'objective_function' in globals():
        print(f"Found objective_function: {objective_function}")
    else:
        print("objective_function NOT found in globals()")
    
    print(f"\nAll variables in {module_name} module:")
    for var in dir(ilp_params):
        if not var.startswith('__'):
            print(f"  {var}: {getattr(ilp_params, var)}")

except Exception as e:
    print(f"Could not import {params_file}. Error: {e}")
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
            
#             # 如果是K维度，考虑缓存行对齐
#             if var.lower() == 'k':
#                 tiles = [t for t in tiles if (t * data_size) % cache_line == 0]
                
#             valid_tiles[var] = filter_divisors(tiles)
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
    过滤除数，确保它们与缓存行对齐
    
    参数:
    - divisors: 所有可能的分块大小列表
    - var: 循环变量名
    - data_size: 数据类型大小(字节)
    - cache_line: 缓存行大小(字节)
    - min_size: 最小分块大小
    - max_size: 最大分块大小
    
    返回:
    - 过滤后与缓存行对齐的分块大小列表
    """
    if max_size is None:
        max_size = max(divisors)
    
    # 基本过滤：保留在指定范围内的值
    filtered = [d for d in divisors if min_size <= d <= max_size]
    
    # 缓存行对齐过滤
    # 计算一个缓存行可以容纳的元素数量
    elements_per_line = cache_line // data_size
    
    # 对齐的分块大小列表
    aligned = []
    for d in filtered:
        # 检查这个分块大小是否导致内存访问与缓存行对齐
        if d % elements_per_line == 0 or elements_per_line % d == 0:
            aligned.append(d)
    
    # 如果没有找到对齐的值，返回原始过滤结果
    if not aligned:
        print(f"Warning: No cache-aligned tile sizes found for {var}. Using unaligned sizes.")
        return filtered
    
    return aligned

# 为每个循环变量计算有效的分块大小
valid_tiles = {}
if 'loop_vars' in globals():
    unique_loop_vars = list(dict.fromkeys(loop_vars))
    for var in unique_loop_vars:
        var_size_name = f"{var}_size"
        if var_size_name in globals():
            var_size = globals()[var_size_name]
            tiles = find_divisors(var_size)
            
            # 对所有维度应用缓存行对齐过滤
            valid_tiles[var] = filter_divisors(tiles, var, data_size, cache_line)
            print(f"Valid tile sizes for {var}: {valid_tiles[var]}")
        else:
            # 如果找不到大小，使用默认值[1]
            valid_tiles[var] = [1]
            print(f"No size found for {var}, using default tile size [1]")
else:
    print("No loop variables found, cannot calculate tile sizes")
    sys.exit(1)


# def filter_divisors(divisors, var, data_size, cache_line, min_size=1, max_size=None):
#     """
#     智能筛选tile sizes，包括两类值:
#     1. 维度大小的精选除数（智能筛选）
#     2. 同时满足缓存行倍数和2的幂次的特殊值
    
#     Args:
#         divisors: 所有可能的分块大小列表（维度的除数）
#         var: 循环变量名
#         data_size: 数据类型大小（字节）
#         cache_line: 缓存行大小（字节）
#         min_size: 最小分块大小
#         max_size: 最大分块大小
    
#     Returns:
#         筛选后的有效分块大小列表
#     """
#     if max_size is None:
#         max_size = max(divisors)
    
#     # 基本过滤：保留在指定范围内的除数
#     raw_divisors = [d for d in divisors if min_size <= d <= max_size]
    
#     # 计算一个缓存行可以容纳的元素数量
#     elements_per_line = cache_line // data_size
#     print(f"缓存行可容纳 {elements_per_line} 个元素（每个元素 {data_size} 字节）")
    
#     # 获取变量尺寸（如果可用）
#     var_size_name = f"{var}_size"
#     var_size = 0
#     if var_size_name in globals():
#         var_size = globals()[var_size_name]
#     else:
#         # 如果找不到变量尺寸，使用最大除数作为近似
#         var_size = max(raw_divisors) if raw_divisors else max_size
    
#     max_val = min(var_size, max_size) if var_size > 0 else max_size
    
#     # 智能筛选除数（而不是使用所有除数）
#     filtered_divisors = smart_select_divisors(raw_divisors, var_size, elements_per_line)
    
#     # 打印详细的过滤信息
#     filtered_out = set(raw_divisors) - set(filtered_divisors)
#     print(f"\n过滤详情（{var}）:")
#     print(f"  原始除数列表（{len(raw_divisors)}个）: {raw_divisors}")
#     print(f"  智能筛选后的除数（{len(filtered_divisors)}个）: {filtered_divisors}")
#     print(f"  被过滤掉的除数（{len(filtered_out)}个）: {sorted(list(filtered_out))}")
    
#     # 生成所有可能的2的幂次值（直到max_val）
#     all_powers_of_2 = []
#     power = 1
#     while power <= max_val:
#         all_powers_of_2.append(power)
#         power *= 2
    
#     # 生成所有可能的缓存行倍数（直到max_val）
#     all_cache_multiples = []
#     for i in range(1, (max_val // elements_per_line) + 1):
#         val = i * elements_per_line
#         if val <= max_val:
#             all_cache_multiples.append(val)
    
#     # 找出同时是缓存行倍数和2的幂次的特殊值
#     special_tiles = set(all_cache_multiples) & set(all_powers_of_2)
#     special_tiles_list = sorted(list(special_tiles))
    
#     # 记录特殊值中哪些是新增的（不在原始除数中）
#     new_special_tiles = special_tiles - set(raw_divisors)
#     existing_special_tiles = special_tiles & set(raw_divisors)
    
#     print(f"  特殊值（同时是缓存行倍数和2的幂次）（{len(special_tiles_list)}个）: {special_tiles_list}")
#     print(f"  新增的特殊值（不在原始除数中）（{len(new_special_tiles)}个）: {sorted(list(new_special_tiles))}")
#     print(f"  已存在的特殊值（也是原始除数）（{len(existing_special_tiles)}个）: {sorted(list(existing_special_tiles))}")
    
#     # 合并两个集合：智能筛选的除数和特殊值
#     all_tiles = set(filtered_divisors) | special_tiles
    
#     # 与原始除数对比，看增加了哪些值，减少了哪些值
#     added_values = all_tiles - set(raw_divisors)
#     removed_values = set(raw_divisors) - all_tiles
    
#     print(f"  最终结果与原始除数对比:")
#     print(f"  - 新增值（{len(added_values)}个）: {sorted(list(added_values))}")
#     print(f"  - 移除值（{len(removed_values)}个）: {sorted(list(removed_values))}")
    
#     # 转换为排序列表
#     result = sorted(list(all_tiles))
    
#     # 打印统计信息
#     print(f"\n{var} 的分块大小统计:")
#     print(f"  - 原始除数: {len(raw_divisors)} 个")
#     print(f"  - 智能筛选后的除数: {len(filtered_divisors)} 个")
#     print(f"  - 2的幂次值: {len(all_powers_of_2)} 个")
#     print(f"  - 缓存行倍数: {len(all_cache_multiples)} 个")
#     print(f"  - 特殊值（同时是缓存行倍数和2的幂次）: {len(special_tiles_list)} 个")
#     print(f"  - 合并后总计: {len(result)} 个有效分块大小")
    
#     # 突出显示特殊值
#     if special_tiles_list:
#         print(f"  - 特殊值（同时是缓存行倍数和2的幂次）: {special_tiles_list}")
    
#     # 如果没有找到有效的分块大小，使用合理的默认值
#     if not result:
#         print(f"警告: 没有找到 {var} 的有效分块大小。使用默认值。")
#         # 尝试找到合理的默认值 - 优先使用缓存行大小
#         if elements_per_line <= max_size:
#             return [elements_per_line]
#         else:
#             return [min(raw_divisors)] if raw_divisors else [1]
    
#     return result

# def smart_select_divisors(divisors, dim_size, elements_per_line):
#     """
#     智能筛选除数，保留最有价值的选项
    
#     策略:
#     1. 总是保留小的除数（1-16）因为它们对于小的分块很重要
#     2. 总是保留大的除数（dim_size/2, dim_size/4）因为它们对于减少块数很重要
#     3. 优先保留接近缓存行倍数的除数
#     4. 优先保留2的幂次或其附近的值
#     5. 对于中等大小的除数，通过对数间隔进行抽样
    
#     最多返回约20个值
#     """
#     if len(divisors) <= 20:
#         return divisors  # 如果除数已经很少，则全部保留
    
#     selected = set()
    
#     # 记录每个策略选择的除数，用于调试
#     small_divisors = [d for d in divisors if d <= 16]
#     print(f"\n智能筛选过程细节:")
#     print(f"  策略1 - 保留小除数: {small_divisors}")
#     selected.update(small_divisors)
    
#     # 2. 总是保留大的除数
#     large_divisors = []
#     if dim_size > 0:
#         large_vals = [dim_size//4, dim_size//3, dim_size//2, dim_size]
#         large_divisors = [d for d in divisors if d in large_vals or d >= dim_size/4]
#         print(f"  策略2 - 保留大除数 (大于{dim_size}/4={dim_size/4}): {large_divisors}")
#     else:
#         # 如果不知道维度大小，保留最大的几个除数
#         large_divisors = sorted(divisors)[-4:]
#         print(f"  策略2 - 保留最大的几个除数: {large_divisors}")
    
#     selected.update(large_divisors)
    
#     # 3. 优先保留接近缓存行倍数的除数
#     cache_related = []
#     for i in range(1, 6):  # 检查前5个缓存行倍数
#         cache_val = elements_per_line * i
#         # 找出最接近的除数
#         closest = min(divisors, key=lambda x: abs(x - cache_val))
#         cache_related.append((closest, f"接近{cache_val}"))
        
#         # 同时检查这个缓存行倍数的一半和两倍
#         half_val = cache_val // 2
#         double_val = cache_val * 2
        
#         closest_half = min(divisors, key=lambda x: abs(x - half_val))
#         cache_related.append((closest_half, f"接近{half_val}"))
        
#         closest_double = min(divisors, key=lambda x: abs(x - double_val) if x <= dim_size else float('inf'))
#         if closest_double <= dim_size:
#             cache_related.append((closest_double, f"接近{double_val}"))
    
#     print(f"  策略3 - 保留接近缓存行倍数的值: {cache_related}")
#     selected.update([x[0] for x in cache_related])
    
#     # 4. 优先保留2的幂次或其附近的值
#     power_related = []
#     power = 1
#     while power <= max(divisors):
#         # 找出最接近的除数
#         closest = min(divisors, key=lambda x: abs(x - power))
#         power_related.append((closest, f"接近2^{int(math.log2(power))}={power}"))
#         power *= 2
    
#     print(f"  策略4 - 保留接近2的幂次的值: {power_related}")
#     selected.update([x[0] for x in power_related])
    
#     # 5. 对于中等大小的除数，通过对数间隔进行抽样
#     samples = []
#     if len(selected) < 20:
#         remaining = [d for d in divisors if d not in selected]
#         remaining.sort()
        
#         # 计算需要多少额外的值
#         extra_needed = min(20 - len(selected), len(remaining))
        
#         if extra_needed > 0 and remaining:
#             if extra_needed == 1:
#                 # 如果只需要一个额外的值，选择中间的元素
#                 samples.append(remaining[len(remaining) // 2])
#             else:
#                 # 对数间隔抽样
#                 indices = [int(i * (len(remaining) - 1) / (extra_needed - 1)) for i in range(extra_needed)]
#                 for idx in indices:
#                     if idx < len(remaining):
#                         samples.append(remaining[idx])
    
#     print(f"  策略5 - 对数间隔抽样: {samples}")
#     selected.update(samples)
    
#     # 确保结果是排序的列表
#     return sorted(list(selected))

# # 更新调用filter_divisors的代码部分
# valid_tiles = {}
# if 'loop_vars' in globals():
#     unique_loop_vars = list(dict.fromkeys(loop_vars))
#     for var in unique_loop_vars:
#         var_size_name = f"{var}_size"
#         if var_size_name in globals():
#             var_size = globals()[var_size_name]
#             # 首先生成所有除数
#             tiles = find_divisors(var_size)
            
#             # 应用我们的组合筛选方法
#             valid_tiles[var] = filter_divisors(tiles, var, data_size, cache_line)
            
#             # 增强输出以便更好地理解结果
#             print(f"\n{var} 的有效分块大小: {valid_tiles[var]}")
            
#             # 检查除数
#             divisor_tiles = [t for t in valid_tiles[var] if var_size % t == 0]
#             print(f"  除数: {divisor_tiles}")
            
#             # 检查缓存行倍数
#             elements_per_line = cache_line // data_size
#             cache_tiles = [t for t in valid_tiles[var] if t % elements_per_line == 0]
#             print(f"  缓存行倍数: {cache_tiles}")
            
#             # 检查2的幂次值
#             power_tiles = []
#             for tile in valid_tiles[var]:
#                 power = math.log2(tile)
#                 if power.is_integer():
#                     power_tiles.append((tile, int(power)))
            
#             print(f"  2的幂次: {[p[0] for p in power_tiles]}")
            
#             # 检查特殊值（同时是缓存行倍数和2的幂次）
#             special_tiles = [t for t in cache_tiles if math.log2(t).is_integer()]
#             if special_tiles:
#                 print(f"  ★ 特殊值（同时是缓存行倍数和2的幂次）: {special_tiles}")
            
#         else:
#             # 如果找不到大小，使用默认值[1]
#             valid_tiles[var] = [1]
#             print(f"未找到 {var} 的大小，使用默认分块大小 [1]")
# else:
#     print("未找到循环变量，无法计算分块大小")
#     sys.exit(1)



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

def optimize_single_block(block_vars, var_to_size, block_idx, matrix_info):
    """针对单个块优化分块大小"""
    print(f"\n==== Optimizing Block {block_idx} ====")
    print(f"Variables in this block: {block_vars}")
    
    # 创建LP问题
    prob = pulp.LpProblem(f"Block_{block_idx}_Tiling", pulp.LpMinimize)
    
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
    is_column_major = False
    column_major_dims = []
    
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
        elif var in var_to_size:
            # 获取该维度的大小
            dim_size = var_to_size[var]
            block_var_to_size[var] = dim_size
            
            # 计算该维度的所有可能分块大小
            tiles = find_divisors(dim_size)
            
            valid_tiles[var] = tiles
            
            # 创建分块大小决策变量
            tile_vars[var] = {t: pulp.LpVariable(f"{var}_tile_{t}", 0, 1, pulp.LpBinary) for t in tiles}
        else:
            # 如果没有找到维度大小，使用默认值
            valid_tiles[var] = [1]
            tile_vars[var] = {1: pulp.LpVariable(f"{var}_tile_1", 1, 1, pulp.LpBinary)}
            print(f"No dimension size found for {var}, using default tile size 1")
    
    # 约束：每个维度必须选择一个分块大小
    for var in block_vars:
        prob += pulp.lpSum(tile_vars[var].values()) == 1, f"{var}_dimension_constraint"
    
    # 在约束之后，打印每个维度的有效分块大小
    print("\n=== Valid tile sizes for this block ===")
    var_to_active_tiles = {}
    for var in block_vars:
        # 收集所有未被约束排除的分块大小
        active_tiles = []
        for t in valid_tiles[var]:
            # 找出直接约束此变量为0的约束
            excluded = False
            for name, constraint in prob.constraints.items():
                if len(constraint.keys()) == 1 and tile_vars[var][t] in constraint and constraint.sense == pulp.LpConstraintLE:
                    if constraint.constant == 0:
                        excluded = True
                        break
            
            if not excluded:
                active_tiles.append(t)
        
        var_to_active_tiles[var] = active_tiles
        print(f"{var}: {active_tiles[:10]}...")
    
    # 应用缓存约束
    print("\n=== Applying cache constraints ===")
    
    # 获取块特定的约束（如果存在）
    block_specific_ro_constraint = None
    block_specific_rw_constraint = None
    try:
        # 尝试获取特定于块的约束
        ro_var_name = f"block_{block_idx}_read_only_constraint"
        rw_var_name = f"block_{block_idx}_read_write_constraint"
        
        if ro_var_name in globals():
            block_specific_ro_constraint = globals()[ro_var_name]
            print(f"Found block-specific read-only constraint: {block_specific_ro_constraint}")
        
        if rw_var_name in globals():
            block_specific_rw_constraint = globals()[rw_var_name]
            print(f"Found block-specific read-write constraint: {block_specific_rw_constraint}")
    except Exception as e:
        print(f"Error checking for block-specific constraints: {e}")
    
    # 打印原始约束，用于调试
    print("\n=== Original constraints ===")
    if 'read_only_constraint' in globals() and read_only_constraint is not None:
        print(f"Global read_only_constraint: {read_only_constraint}")
    else:
        print("No global read_only_constraint found")
    
    if 'read_write_constraint' in globals() and read_write_constraint is not None:
        print(f"Global read_write_constraint: {read_write_constraint}")
    else:
        print("No global read_write_constraint found")
    
    # 为此块创建筛选后的约束表达式
    filtered_ro_constraint = None
    filtered_rw_constraint = None
    
    # 处理只读约束条件
    if block_specific_ro_constraint:
        # 使用块特定的只读约束
        filtered_ro_constraint = block_specific_ro_constraint
    elif 'read_only_constraint' in globals() and read_only_constraint is not None:
        try:
            # 按加号分割约束条件为独立项
            ro_terms = read_only_constraint.split(" + ")
            relevant_terms = []
            
            # 只保留包含当前块变量的项，并且替换其他块的变量
            for term in ro_terms:
                is_relevant = False
                for var in block_vars:
                    if f"{var}_tile" in term:
                        is_relevant = True
                        break
                
                if is_relevant:
                    # 替换其他块的变量
                    modified_term = term
                    for var in loop_vars:
                        if var not in block_vars and f"{var}_tile" in modified_term:
                            pattern = r'\b' + re.escape(var) + r'_tile\b'
                            modified_term = re.sub(pattern, "0", modified_term)
                    
                    # 如果替换后的项还有意义（不全是0），则添加
                    if not any(x in modified_term for x in ["0 *", "* 0"]):
                        relevant_terms.append(modified_term)
            
            # 重新组合相关项
            if relevant_terms:
                filtered_ro_constraint = " + ".join(relevant_terms)
            else:
                filtered_ro_constraint = None
                print("No relevant terms found in read-only constraint for this block")
        except Exception as e:
            print(f"Error filtering read-only constraint: {e}")
            filtered_ro_constraint = None
    
    # 处理读写约束条件
    if block_specific_rw_constraint:

        # 使用块特定的读写约束
        filtered_rw_constraint = block_specific_rw_constraint
    elif 'read_write_constraint' in globals() and read_write_constraint is not None:
        try:
            # 按加号分割约束条件为独立项
            rw_terms = read_write_constraint.split(" + ")
            relevant_terms = []
            
            # 只保留包含当前块变量的项，并且替换其他块的变量
            for term in rw_terms:
                is_relevant = False
                for var in block_vars:
                    if f"{var}_tile" in term:
                        is_relevant = True
                        break
                
                if is_relevant:
                    # 替换其他块的变量
                    modified_term = term
                    for var in loop_vars:
                        if var not in block_vars and f"{var}_tile" in modified_term:
                            pattern = r'\b' + re.escape(var) + r'_tile\b'
                            modified_term = re.sub(pattern, "0", modified_term)
                    
                    # 清理表达式，去除含0的乘积
                    while " * 0" in modified_term or "0 * " in modified_term:
                        modified_term = re.sub(r'[^+]*\*\s*0[^+]*', "0", modified_term)
                        modified_term = re.sub(r'0\s*\*\s*[^+]*', "0", modified_term)
                    
                    # 过滤掉变成0的项
                    if modified_term != "0" and modified_term != "0 " and not modified_term.startswith("0 +") and not modified_term.endswith("+ 0"):
                        # 进一步清理，去除"+ 0"和"0 +"
                        modified_term = re.sub(r'\+\s*0\b', "", modified_term)
                        modified_term = re.sub(r'\b0\s*\+', "", modified_term)
                        if modified_term and modified_term.strip() and modified_term.strip() != "0":
                            relevant_terms.append(modified_term)
            
            # 重新组合相关项
            if relevant_terms:
                filtered_rw_constraint = " + ".join(relevant_terms)
                # 最后清理一下可能残留的"+ +"或"+ 空格 +"
                filtered_rw_constraint = re.sub(r'\+\s*\+', "+", filtered_rw_constraint)
                filtered_rw_constraint = filtered_rw_constraint.strip()
                # 如果以+开头或结尾，去掉
                if filtered_rw_constraint.startswith("+"):
                    filtered_rw_constraint = filtered_rw_constraint[1:].strip()
                if filtered_rw_constraint.endswith("+"):
                    filtered_rw_constraint = filtered_rw_constraint[:-1].strip()
            else:
                filtered_rw_constraint = None
                print("No relevant terms found in read-write constraint for this block")
        except Exception as e:
            print(f"Error filtering read-write constraint: {e}")
            filtered_rw_constraint = None
    
    # 打印过滤后的约束，用于调试
    print("\n=== Filtered constraints for this block ===")
    print(f"Filtered read_only_constraint: {filtered_ro_constraint}")
    print(f"Filtered read_write_constraint: {filtered_rw_constraint}")
    
    # 生成所有分块大小组合
    combinations = []
    for var in block_vars:
        combinations.append([(var, t) for t in var_to_active_tiles[var]])
    
    all_combinations = list(itertools.product(*combinations))
    print(f"\nEvaluating {len(all_combinations)} combinations")
    
    # 评估只读数组的L1缓存约束
    if filtered_ro_constraint:
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
                constraint_value = eval(filtered_ro_constraint)
                constraint_valid = True
                print(f"Sample evaluation for {combo}: {filtered_ro_constraint} = {constraint_value}")
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
                    constraint_value = eval(filtered_ro_constraint)
                    
                    if constraint_value > L1_size:
                        # 如果违反约束，创建一个限制这种组合的约束
                        constraint_name = f"ro_L1_" + "_".join([f"{var}_{t}" for var, t in combo])
                        prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                except Exception as e:
                    pass
        else:
            print("Warning: Could not evaluate read-only constraint - skipping")
    
    # 评估读写约束
    if filtered_rw_constraint:
        print("\n=== Evaluating read-write constraints ===")
        # Check if L1 lower bound constraint might lead to infeasibility
        max_tile_combo = {}
        for var in block_vars:
            if var in var_to_active_tiles and var_to_active_tiles[var]:
                max_tile_combo[f"{var}_tile"] = max(var_to_active_tiles[var])
        
        # Check if even the maximum possible memory usage is less than L1 size
        skip_l1_lower_constraint = False
        try:
            if max_tile_combo:
                locals().update(max_tile_combo)
                max_mem_usage = eval(filtered_rw_constraint)
                print(f"Maximum possible memory usage with largest tiles: {max_mem_usage} bytes")
                print(f"L1 cache size: {L1_size} bytes")
                
                # If max possible memory usage is less than L1 size, L1 lower bound cannot be satisfied
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
                constraint_value = eval(filtered_rw_constraint)
                constraint_valid = True
                print(f"Sample evaluation for {combo}: {filtered_rw_constraint} = {constraint_value}")
                
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
                    constraint_value = eval(filtered_rw_constraint)
                    # L1下限约束 - 如果需要跳过，则不添加这个约束
                    if constraint_value <= L1_size and not skip_l1_lower_constraint:
                        constraint_name = f"rw_L1_lower_" + "_".join([f"{var}_{t}" for var, t in combo])
                        prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                    elif constraint_value <= L1_size and skip_l1_lower_constraint:
                        # 可以添加详细记录，但为了减少输出，这里可以省略
                        pass
                    
                    # L2上限约束 - 始终添加
                    if constraint_value > L2_size:
                        constraint_name = f"rw_L2_upper_" + "_".join([f"{var}_{t}" for var, t in combo])
                        prob += pulp.lpSum(tile_vars[var][t] for var, t in combo) <= len(combo) - 1, constraint_name
                except Exception as e:
                    pass
        else:
            print("Warning: Could not evaluate read-write constraint - skipping")
    
    # 应用变量间的分块大小约束
    if 'tile_size_constraints' in globals() and tile_size_constraints:
        print("\n=== Applying tile size relationship constraints ===")
        
        for var1, op, var2 in tile_size_constraints:
            # 检查这两个变量是否都在当前块中
            if var1 not in block_vars or var2 not in block_vars:
                print(f"Skipping constraint {var1} {op} {var2} - variables not in current block")
                continue
            
            print(f"Adding constraint: {var1}_tile {op} {var2}_tile")
            
            # 获取两个变量的有效分块大小
            tiles1 = var_to_active_tiles[var1]
            tiles2 = var_to_active_tiles[var2]
            
            # 根据比较运算符添加约束
            violation_count = 0
            for t1 in tiles1:
                for t2 in tiles2:
                    violates = False
                    
                    if op == '>':
                        violates = (t1 <= t2)
                    elif op == '>=':
                        violates = (t1 < t2)
                    elif op == '<':
                        violates = (t1 >= t2)
                    elif op == '<=':
                        violates = (t1 > t2)
                    elif op == '==':
                        violates = (t1 != t2)
                    elif op == '!=':
                        violates = (t1 == t2)
                    
                    if violates:
                        # 添加约束：不允许这种组合同时发生
                        # tile_vars[var1][t1] + tile_vars[var2][t2] <= 1
                        constraint_name = f"tile_rel_{var1}_{t1}_{op.replace('>', 'gt').replace('<', 'lt').replace('=', 'eq')}_{var2}_{t2}"
                        prob += tile_vars[var1][t1] + tile_vars[var2][t2] <= 1, constraint_name
                        violation_count += 1
            
            print(f"  Added {violation_count} constraints for {var1} {op} {var2}")


    # 获取块特定的目标函数（如果存在）
    block_specific_obj_fn = None
    try:
        # 尝试获取特定于块的目标函数
        obj_var_name = f"block_{block_idx}_objective"
        if obj_var_name in globals():
            block_specific_obj_fn = globals()[obj_var_name]
            print(f"\nFound block-specific objective function: {block_specific_obj_fn}")
    except Exception as e:
        print(f"Error checking for block-specific objective function: {e}")
    
    # Print global objective function
    if 'objective_function' in globals():
        print(f"\nGlobal objective function: {objective_function}")
    else:
        print("\nNo global objective function found")
    
    # Fix: Properly handle the objective function
    filtered_obj_fn = None
    
    # 处理目标函数
    if block_specific_obj_fn:
        # 使用块特定的目标函数
        filtered_obj_fn = block_specific_obj_fn
    elif 'objective_function' in globals():
        try:
            # 目标函数可能是加法形式的组合
            if " + " in objective_function:
                # 按加号分割为独立项
                obj_terms = objective_function.split(" + ")
                relevant_terms = []
                
                # 确定每个项是否与当前块相关
                for term in obj_terms:
                    is_relevant = False
                    for var in block_vars:
                        if f"{var}_blocks" in term:
                            is_relevant = True
                            break
                    
                    if is_relevant:
                        # 检查这个项是否还包含其他块的变量
                        modified_term = term
                        for var in loop_vars:
                            if var not in block_vars and f"{var}_blocks" in modified_term:
                                # 项中包含其他块的变量，用"1"替换
                                pattern = r'\b' + re.escape(var) + r'_blocks\b'
                                modified_term = re.sub(pattern, "1", modified_term)
                        
                        relevant_terms.append(modified_term)
                
                # 重新组合相关项
                if relevant_terms:
                    filtered_obj_fn = " + ".join(relevant_terms)
                else:
                    # 如果没有相关项，使用默认目标函数
                    filtered_obj_fn = None
            else:
                # 如果目标函数不是加法形式，检查它是否与当前块相关
                is_relevant = False
                for var in block_vars:
                    if f"{var}_blocks" in objective_function:
                        is_relevant = True
                        break
                
                if is_relevant:
                    # 替换不在当前块的变量
                    filtered_obj_fn = objective_function
                    for var in loop_vars:
                        if var not in block_vars and f"{var}_blocks" in filtered_obj_fn:
                            pattern = r'\b' + re.escape(var) + r'_blocks\b'
                            filtered_obj_fn = re.sub(pattern, "1", filtered_obj_fn)
                else:
                    filtered_obj_fn = None
        except Exception as e:
            print(f"Error filtering objective function: {e}")
            filtered_obj_fn = None
    
    # 如果没有得到有效的目标函数，使用默认目标函数
    if not filtered_obj_fn:
        # 使用默认目标函数
        if len(block_vars) >= 2:
            var1, var2 = block_vars[:2]
            filtered_obj_fn = f"{var1}_blocks * {var2}_blocks * T_op1"
        elif len(block_vars) == 1:
            var1 = block_vars[0]
            filtered_obj_fn = f"{var1}_blocks * T_op1"
        else:
            filtered_obj_fn = "T_op1"
        print(f"Using default objective function: {filtered_obj_fn}")
    
    print(f"\nFiltered objective function for block {block_idx}: {filtered_obj_fn}")
    
    # Calculate objective function values
    obj_values = {}  # To store objective function values for each combination
    z_vars = {}      # For representing products of binary variables

    # Build variables for evaluation
    block_vars_sizes = {}
    for var in block_vars:
        if var in block_var_to_size:
            dim_size = block_var_to_size[var]
            # Calculate blocks for each tile size
            block_vars_sizes[var] = {t: math.ceil(dim_size / t) for t in var_to_active_tiles[var]}
        else:
            block_vars_sizes[var] = {1: 1}  # Default one block

    # Clean up the objective function for evaluation
    eval_obj_fn = filtered_obj_fn
    if isinstance(eval_obj_fn, str):
        # Remove dictionary part if present
        if ", {" in eval_obj_fn:
            eval_obj_fn = eval_obj_fn.split(", {")[0]
        # Remove tuple parentheses
        eval_obj_fn = eval_obj_fn.replace("(", "").replace(")", "")
        # Remove quotes
        eval_obj_fn = eval_obj_fn.strip("'\"")

    # Evaluate sample objective functions
    print("\n=== Sample objective function evaluations ===")
    for combo in all_combinations[:5]:  # Only evaluate first 5 combinations
        # Set variables for evaluation
        eval_vars = {}
        for var, t in combo:
            eval_vars[f"{var}_tile"] = t
            eval_vars[f"{var}_blocks"] = block_vars_sizes[var][t]
        
        # Evaluate objective function
        try:
            locals().update(eval_vars)
            obj_value = eval(eval_obj_fn)
            
            # 计算列主序维度的优化因子
            column_major_factor = 0
            for var, t in combo:
                if var in column_major_dims and var in block_var_to_size:
                    dim_size = block_var_to_size[var]
                    tile_ratio = t / dim_size
                    
                    # 添加惩罚因子：对小分块大小的列主序维度施加惩罚
                    # 分块大小越小，惩罚越大
                    if tile_ratio < 0.5:  # 如果分块大小小于维度大小的70%
                        column_major_factor += 0.2 * obj_value * (1 - tile_ratio)
            
            # 将基本目标值和列主序惩罚因子相加
            combo_key = tuple(sorted(combo))
            obj_values[combo_key] = obj_value + column_major_factor
            
            # 打印样本评估结果
            print(f"Combination {combo}: {eval_obj_fn} = {obj_value:.2f}")
            if column_major_factor > 0:
                print(f"  With column-major penalty: {obj_values[combo_key]:.2f} (+{column_major_factor:.2f})")
        except Exception as e:
            print(f"Error evaluating objective function for {combo}: {e}")
            # Fallback: use sum of blocks
            combo_key = tuple(sorted(combo))
            obj_value = sum(eval_vars[f"{var}_blocks"] for var in block_vars)
            obj_values[combo_key] = obj_value
            print(f"Using fallback objective value: {obj_value:.2f}")
    
    # Calculate values for all combinations
    for combo in all_combinations:
        # Create key for the combination
        combo_key = tuple(sorted(combo))
        
        # Set up variables for evaluation
        eval_vars = {}
        for var, t in combo:
            eval_vars[f"{var}_tile"] = t
            eval_vars[f"{var}_blocks"] = block_vars_sizes[var][t]
        
        # Skip if already evaluated
        if combo_key in obj_values:
            continue
            
        # Evaluate objective function
        try:
            locals().update(eval_vars)
            base_obj_value = eval(eval_obj_fn)
            
            # 计算列主序维度的优化因子
            column_major_factor = 0
            for var, t in combo:
                if var in column_major_dims and var in block_var_to_size:
                    dim_size = block_var_to_size[var]
                    tile_ratio = t / dim_size
                    
                    # 对小分块大小的列主序维度施加惩罚
                    if tile_ratio < 0.5:
                        column_major_factor += 0.2 * base_obj_value * (1 - tile_ratio)
            
            # 将基本目标值和列主序惩罚因子相加
            obj_values[combo_key] = base_obj_value + column_major_factor
            
        except Exception as e:
            # Use fallback if evaluation fails
            obj_values[combo_key] = sum(eval_vars[f"{var}_blocks"] for var in block_vars)
    
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
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=300))
    
    # 提取结果
    print(f"Block {block_idx} Status:", pulp.LpStatus[prob.status])
    
    if prob.status == pulp.LpStatusOptimal:
        # 提取每个变量的最优分块大小
        selected_tiles = {}
        
        for var in block_vars:
            for t in var_to_active_tiles[var]:
                if pulp.value(tile_vars[var][t]) == 1:
                    selected_tiles[var] = t
                    break
            
            if var not in selected_tiles:
                # 如果没有找到，使用默认值
                selected_tiles[var] = var_to_active_tiles[var][0]
                print(f"Warning: No value selected for {var}. Using default of {var_to_active_tiles[var][0]}.")
        
        print(f"Block {block_idx} Tiling Results:")
        for var, tile in selected_tiles.items():
            print(f"  {var}_tile = {tile}")

            # 添加以下代码：打印列主序维度的相关信息
            if var in column_major_dims:
                dim_size = block_var_to_size[var]
                utilization = (tile / dim_size) * 100
                print(f"  {var} is a column-major dimension: tile size {tile}/{dim_size} ({utilization:.1f}% utilization)")
        
        # 计算块的目标函数值
        eval_vars = {}
        for var, t in selected_tiles.items():
            if var in block_var_to_size:
                dim_size = block_var_to_size[var]
                eval_vars[f"{var}_tile"] = t
                eval_vars[f"{var}_blocks"] = math.ceil(dim_size / t)
            else:
                eval_vars[f"{var}_tile"] = 1
                eval_vars[f"{var}_blocks"] = 1
        
        # 计算最终的目标函数值
        try:
            locals().update(eval_vars)
            total_obj = eval(filtered_obj_fn)
        except Exception as e:
            print(f"Error calculating final objective for block {block_idx}: {e}")
            # 简单回退方案
            total_obj = sum(eval_vars[f"{var}_blocks"] for var in block_vars)
        
        print(f"Block {block_idx} objective value: {total_obj:.2f}")
        
        return selected_tiles, total_obj
    else:
        print(f"No optimal solution found for Block {block_idx}!")
        # 返回默认值
        default_tiles = {var: var_to_active_tiles[var][0] for var in block_vars}
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
    
    print(f"\n=== Found {len(block_indices)} blocks to optimize ===")
    # Sort block indices to process in numerical order
    sorted_block_indices = sorted(block_indices, key=int)
    for block_idx in sorted_block_indices:
        print(f"Block {block_idx}: {block_to_vars[block_idx]}")
    
    # 存储每个块的最优结果
    block_results = {}
    total_objective = 0
    
    # 分别优化每个块 - now in sorted order
    for block_idx in sorted_block_indices:
        block_vars = block_to_vars[block_idx]
        block_solution, block_objective = optimize_single_block(block_vars, var_to_size, block_idx, matrix_info)
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
    total_blocks = 0
    for block_idx in sorted_block_indices:
        block_vars = block_to_vars[block_idx]
        block_blocks = 1
        for var in block_vars:
            if var in var_to_size and var in final_solution:
                block_blocks *= math.ceil(var_to_size[var] / final_solution[var])
        print(f"Block {block_idx}: {block_blocks} blocks")
        total_blocks += block_blocks
    
    print(f"Total number of blocks across all loops: {total_blocks}")
    
    return final_solution, total_objective


# Run the analysis
if __name__ == "__main__":
    # 构建矩阵信息字典
    matrix_info = {
        'loop_info': {'loop_vars': loop_vars} if 'loop_vars' in globals() else {},
        'var_to_size': {}
    }
    
    print("\n==== Starting Tiling Optimization ====")
    
    # 检查是否包含多个循环块
    has_multiple_blocks = False
    block_indices = set()
    
    if 'loop_vars' in globals():
        for var in loop_vars:
            if '_b' in var:
                has_multiple_blocks = True
                block_idx = var.split('_b')[1]
                block_indices.add(block_idx)
    
    if has_multiple_blocks:
        print(f"Detected {len(block_indices)} separate loop blocks. Will optimize each block individually.")
        start_time = time.time()
        solution, obj_value = solve_tiling_strategy(matrix_info)
        end_time = time.time()
        print(f"\nTotal ILP optimization time: {end_time - start_time:.2f} seconds")
    else:
        print("Using traditional single-block optimization.")
        # 使用原来的单块优化方法
        from ilp_params import *
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
            # 如果是块变量，截取块标识符前的部分
            if '_b' in var:
                base_var = var.split('_b')[0]
                block_id = var.split('_b')[1]
                # print(f"// Block {block_id}")
                print(f"#define {base_var.upper()}_TILE {tile}")
            else:
                print(f"#define {var.upper()}_TILE {tile}")