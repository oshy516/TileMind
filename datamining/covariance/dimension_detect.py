#!/usr/bin/env python3
import os
import subprocess
import re
import sys

def run_ppcg_and_get_schedule(benchmark_file, options=None):
    """运行PPCG并获取调度树信息"""
    if options is None:
        options = ["--target", "c","--no-automatic-mixed-precision","--isl-schedule-max-constant-term=0","--isl-schedule-serialize-sccs",
                  "--split-tile", "--tile-sizes=\"{[1,1,1,1]}\"", 
                  "--dump-schedule"]

    
    output_file = benchmark_file.replace('.c', '_ppcg_default.c')
    schedule_file = benchmark_file.replace('.c', '_schedule.txt')
    
    # 构建命令
    cmd_str = f"ppcg {' '.join(options)} {benchmark_file} -o {output_file} 2> {schedule_file}"
    print("Execute a command:", cmd_str)
    
    try:
        # 执行命令，将stderr重定向到schedule_file
        os.system(cmd_str)
        
        # 读取schedule文件内容
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                schedule_output = f.read()
            return schedule_output
        else:
            print(f"Failed to generate the scheduling file: {schedule_file}")
            return None
    except Exception as e:
        print(f"Error while running PPCG: {e}")
        return None

def parse_schedule_tree(schedule_output):
    """解析调度树输出，识别顶级filter块或顶级band节点的信息"""
    # 存储结果的字典
    dimensions = {
        'tileables': [],      # 可平铺维度
        'non_tileables': []   # 不可平铺维度
    }
    
    # 打印调度树内容
    print("\nSchedule tree content:")
    print(schedule_output)
    
    # 首先检查是否有顶级band节点
    top_band_match = re.search(r'domain:.*?\nchild:\s+schedule: "(.*?)"\s+permutable: (\d+)\s+coincident: \[ (.*?) \]', 
                              schedule_output, re.DOTALL)
    
    if top_band_match:
        print("\nFound top-level band node")
        schedule = top_band_match.group(1)
        permutable = top_band_match.group(2)
        coincident = top_band_match.group(3)
        
        print(f"\nTop-level band node information:")
        print(f"Schedule: {schedule}")
        print(f"Permutable: {permutable}")
        print(f"Coincident: {coincident}")
        
        # 提取schedule中的维度表达式
        schedule_dims = []
        
        # 从schedule中提取表达式，可能包含多个映射
        mappings = re.findall(r'\{(.*?)\}', schedule)
        
        for mapping in mappings:
            # 提取右侧的维度表达式
            expr_matches = re.findall(r'-> \[(.*?)\]', mapping)
            for expr in expr_matches:
                # 处理可能存在的多个维度
                dimensions_in_expr = expr.split(',')
                for dim in dimensions_in_expr:
                    dim = dim.strip()
                    # 检查是否是常数（如(0)），如果不是常数且不在列表中，则添加
                    # 使用r"^\(\d+\)$" 正则表达式识别(0)这样的常数
                    if not re.match(r"^\(\d+\)$", dim) and dim not in schedule_dims:
                        schedule_dims.append(dim)
        
        print(f"  Schedule dimension expressions: {schedule_dims}")
        print(f"  Total schedule dimensions: {len(schedule_dims)}")
        
        # 解析coincident值
        coincident_values = coincident.split(', ')
        print(f"  Coincident values: {coincident_values}")
        
        # 检查是否有子序列（nested band nodes）
        child_sequence_match = re.search(r'child:\s+sequence:(.*?)(?=\Z)', schedule_output, re.DOTALL)
        
        if child_sequence_match:
            print("\nFound child sequence section, processing nested band nodes")
            sequence_content = child_sequence_match.group(1)
            
            # 查找所有filter块
            filter_blocks = re.findall(r'\s+- filter: "(.*?)"\s+child:([\s\S]*?)(?=\s+- filter:|\s*$)', 
                                     sequence_content)
            
            # 创建维度名称到索引的映射
            dim_name_to_index = {}
            
            # 从filter blocks中提取所有维度并建立映射关系
            for filter_text, _ in filter_blocks:
                statements = re.findall(r'([A-Za-z0-9_]+)\[(.*?)\]', filter_text)
                for _, dims in statements:
                    dim_names = [d.strip() for d in dims.split(',')]
                    for idx, name in enumerate(dim_names):
                        if name not in dim_name_to_index:
                            dim_name_to_index[name] = idx
            
            # 首先确定内层band节点的维度是否tileable
            inner_tileables = []
            
            for idx, (filter_text, child_text) in enumerate(filter_blocks):
                print(f"\nAnalyzing filter block {idx+1}: {filter_text}")
                
                # 检查该filter块是否有child信息
                if not child_text.strip():
                    print(f"  Filter block {idx+1} has no child information, skipping")
                    continue
                
                # 从filter表达式中提取所有涉及的语句和维度
                statements = re.findall(r'([A-Za-z0-9_]+)\[(.*?)\]', filter_text)
                
                all_dimensions = set()
                for _, dims in statements:
                    for dim in dims.split(','):
                        all_dimensions.add(dim.strip())
                
                print(f"  All dimensions involved: {sorted(list(all_dimensions))}")
                
                # 查找内层band节点
                inner_schedule_match = re.search(r'\s+schedule: "(.*?)"', child_text)
                inner_permutable_match = re.search(r'\s+permutable: (\d+)', child_text)
                inner_coincident_match = re.search(r'\s+coincident: \[ (.*?) \]', child_text)
                
                if inner_schedule_match and inner_permutable_match and inner_coincident_match:
                    inner_schedule = inner_schedule_match.group(1)
                    inner_permutable = inner_permutable_match.group(1)
                    inner_coincident = inner_coincident_match.group(1)
                    
                    print(f"\nInner band node information for filter block {idx+1}:")
                    print(f"Schedule: {inner_schedule}")
                    print(f"Permutable: {inner_permutable}")
                    print(f"Coincident: {inner_coincident}")
                    
                    # 提取inner schedule中的维度表达式
                    inner_schedule_dims = []
                    
                    # 从schedule中提取表达式，可能包含多个映射
                    inner_mappings = re.findall(r'\{(.*?)\}', inner_schedule)
                    
                    for inner_mapping in inner_mappings:
                        # 提取右侧的维度表达式
                        inner_expr_matches = re.findall(r'-> \[(.*?)\]', inner_mapping)
                        for inner_expr in inner_expr_matches:
                            # 处理可能存在的多个维度
                            if ',' in inner_expr:
                                for inner_dim in inner_expr.split(','):
                                    inner_dim = inner_dim.strip()
                                    # 检查是否是常数
                                    if not re.match(r"^\(\d+\)$", inner_dim) and inner_dim not in inner_schedule_dims:
                                        inner_schedule_dims.append(inner_dim)
                            else:
                                inner_dim = inner_expr.strip()
                                # 检查是否是常数
                                if not re.match(r"^\(\d+\)$", inner_dim) and inner_dim not in inner_schedule_dims:
                                    inner_schedule_dims.append(inner_dim)
                    
                    print(f"  Inner schedule dimension expressions: {inner_schedule_dims}")
                    print(f"  Total inner schedule dimensions: {len(inner_schedule_dims)}")
                    
                    # 解析coincident值
                    inner_coincident_values = inner_coincident.split(', ')
                    print(f"  Inner coincident values: {inner_coincident_values}")
                    
                    # 处理内层节点的维度
                    is_band_tileable = inner_permutable == '1' and len(inner_coincident_values) >= 2
                    
                    if not is_band_tileable:
                        print(f"  Inner band of filter block {idx+1} is not permutable or has no coincident values, all dimensions are not tileable")
                    
                    for j, inner_dim in enumerate(inner_schedule_dims):
                        # 从inner_dim中提取原始维度名称，例如从(p)提取p
                        dim_var_match = re.search(r'\((.*?)\)', inner_dim)
                        if dim_var_match:
                            dim_var = dim_var_match.group(1)
                            # 查找该维度在原始维度中的索引
                            global_dim_idx = dim_name_to_index.get(dim_var, len(schedule_dims) + j)
                            
                            filter_prefix = f"Filter 1"  # 使用Filter 1，因为所有子节点都属于Filter 1
                            
                            if is_band_tileable and j < len(inner_coincident_values):
                                if inner_coincident_values[j] == '1':
                                    dim_name = f"{filter_prefix}, Dimension {global_dim_idx}: {inner_dim}"
                                    dimensions['tileables'].append(dim_name)
                                    inner_tileables.append(global_dim_idx)
                                    print(f"  Inner dimension {global_dim_idx} ({inner_dim}) is tileable")
                                else:
                                    dim_name = f"{filter_prefix}, Dimension {global_dim_idx}: {inner_dim}"
                                    dimensions['non_tileables'].append(dim_name)
                                    print(f"  Inner dimension {global_dim_idx} ({inner_dim}) is not tileable")
                            else:
                                dim_name = f"{filter_prefix}, Dimension {global_dim_idx}: {inner_dim}"
                                dimensions['non_tileables'].append(dim_name)
                                if not is_band_tileable:
                                    print(f"  Inner dimension {global_dim_idx} ({inner_dim}) is not tileable")
                                else:
                                    print(f"  Inner dimension {global_dim_idx} ({inner_dim}) has no coincident value, assuming not tileable")
            
            # 内层维度优先于外层维度，所以如果有内层可分割维度，则外层全部标记为不可分割
            if inner_tileables:
                print("\nInner tileable dimensions found, marking all outer dimensions as non-tileable")
                if permutable == '1' and len(coincident_values) >= 2:
                    for j, dim in enumerate(schedule_dims):
                        filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                        dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                        if dim_name not in dimensions['non_tileables']:
                            dimensions['non_tileables'].append(dim_name)
                            print(f"  Outer dimension {j} ({dim}) is marked as not tileable due to inner tileable dimensions")
            else:
                # 如果没有内层可分割维度，则处理外层维度
                print("\nNo inner tileable dimensions found, processing outer dimensions")
                if permutable == '1' and len(coincident_values) >= 2:
                    for j, dim in enumerate(schedule_dims):
                        filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                        if j < len(coincident_values):
                            if coincident_values[j] == '1':
                                dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                                dimensions['tileables'].append(dim_name)
                                print(f"  Dimension {j} ({dim}) is tileable")
                            else:
                                dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                                dimensions['non_tileables'].append(dim_name)
                                print(f"  Dimension {j} ({dim}) is not tileable")
                        else:
                            # 如果没有对应的coincident值，保守地认为不可分割
                            dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                            dimensions['non_tileables'].append(dim_name)
                            print(f"  Dimension {j} ({dim}) has no coincident value, assuming not tileable")
                else:
                    # 如果不可重排，则所有维度都不可分割
                    print(f"  Top-level band node is not permutable or has no coincident values, all dimensions are not tileable")
                    for j, dim in enumerate(schedule_dims):
                        filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                        dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                        dimensions['non_tileables'].append(dim_name)
                        print(f"  Dimension {j} ({dim}) is not tileable")
        else:
            # 没有子序列，直接处理顶级band节点
            print("\nNo child sequence found, processing top-level band node directly")
            if permutable == '1' and len(coincident_values) >= 2:
                for j, dim in enumerate(schedule_dims):
                    filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                    if j < len(coincident_values):
                        if coincident_values[j] == '1':
                            dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                            dimensions['tileables'].append(dim_name)
                            print(f"  Dimension {j} ({dim}) is tileable")
                        else:
                            dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                            dimensions['non_tileables'].append(dim_name)
                            print(f"  Dimension {j} ({dim}) is not tileable")
                    else:
                        # 如果没有对应的coincident值，保守地认为不可分割
                        dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                        dimensions['non_tileables'].append(dim_name)
                        print(f"  Dimension {j} ({dim}) has no coincident value, assuming not tileable")
            else:
                # 如果不可重排，则所有维度都不可分割
                print(f"  Top-level band node is not permutable or has no coincident values, all dimensions are not tileable")
                for j, dim in enumerate(schedule_dims):
                    filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                    dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                    dimensions['non_tileables'].append(dim_name)
                    print(f"  Dimension {j} ({dim}) is not tileable")
        
        return dimensions
    
    # 如果没有顶级band节点，根据格式查找最外层的filter块
    # 首先尝试查找set:部分
    set_match = re.search(r'child:\s+set:(.*?)(?=\Z)', schedule_output, re.DOTALL)
    
    # 如果没有set:部分，尝试查找sequence:部分
    if not set_match:
        sequence_match = re.search(r'child:\s+sequence:(.*?)(?=\Z)', schedule_output, re.DOTALL)
        if not sequence_match:
            print("Neither top-level band node, set section, nor sequence section found")
            return dimensions
        content_to_search = sequence_match.group(1)
        print("Found top-level sequence section")
    else:
        content_to_search = set_match.group(1)
        print("Found top-level set section")
    
    # 使用更准确的正则表达式匹配最外层的filter块
    filter_blocks_regex = r'\s+- filter: "(.*?)"\s+child:([\s\S]*?)(?=\s+- filter:|\s*$)'
    top_level_filters_raw = re.findall(filter_blocks_regex, content_to_search)
    
    # 只保留包含schedule、permutable和coincident字段的完整filter块
    top_level_filters = []
    for filter_text, child_text in top_level_filters_raw:
        if ('schedule:' in child_text and 'permutable:' in child_text and 'coincident:' in child_text):
            top_level_filters.append((filter_text, child_text))
    
    if not top_level_filters:
        print("No top-level filter blocks found with complete information")
        return dimensions
    
    print(f"\nFound {len(top_level_filters)} top-level filter blocks")
    
    # 分析每个顶级filter块
    for idx, (filter_text, child_text) in enumerate(top_level_filters):
        print(f"\nAnalyzing top-level filter block {idx+1}: {filter_text}")
        
        # 检查该filter块是否有child信息
        if not child_text.strip():
            print(f"  Top-level filter block {idx+1} has no child information, skipping")
            continue
            
        print("Its child information:")
        print(child_text)
        
        # 从filter表达式中提取所有涉及的语句和维度
        statements = re.findall(r'([A-Za-z0-9_]+)\[(.*?)\]', filter_text)
        
        all_dimensions = set()
        for _, dims in statements:
            for dim in dims.split(','):
                all_dimensions.add(dim.strip())
        
        print(f"  All dimensions involved: {sorted(list(all_dimensions))}")
        total_dims = len(all_dimensions)
        print(f"  Total dimensions:: {total_dims}")
        
        # 查找最外层band节点（包含schedule和permutable的直接子节点）
        schedule_match = re.search(r'\s+schedule: "(.*?)"', child_text)
        permutable_match = re.search(r'\s+permutable: (\d+)', child_text)
        coincident_match = re.search(r'\s+coincident: \[ (.*?) \]', child_text)
        
        if schedule_match and permutable_match and coincident_match:
            schedule = schedule_match.group(1)
            permutable = permutable_match.group(1)
            coincident = coincident_match.group(1)
            
            print(f"\nBand node information for top-level filter block {idx+1}:")
            print(f"Schedule: {schedule}")
            print(f"Permutable: {permutable}")
            print(f"Coincident: {coincident}")
            
            # 提取schedule中的维度表达式
            schedule_dims = []
            
            # 从schedule中提取表达式，可能包含多个映射
            mappings = re.findall(r'\{(.*?)\}', schedule)
            
            for mapping in mappings:
                # 提取右侧的维度表达式
                expr_matches = re.findall(r'-> \[(.*?)\]', mapping)
                for expr in expr_matches:
                    # 处理可能存在的多个维度
                    if ',' in expr:
                        for dim in expr.split(','):
                            dim = dim.strip()
                            # 检查是否是常数（如(0)），如果不是常数且不在列表中，则添加
                            if not re.match(r"^\(\d+\)$", dim) and dim not in schedule_dims:
                                schedule_dims.append(dim)
                    else:
                        dim = expr.strip()
                        # 检查是否是常数（如(0)），如果不是常数且不在列表中，则添加
                        if not re.match(r"^\(\d+\)$", dim) and dim not in schedule_dims:
                            schedule_dims.append(dim)
            
            print(f"  Schedule dimension expressions: {schedule_dims}")
            print(f"  Total schedule dimensions: {len(schedule_dims)}")
            
            # 解析coincident值
            coincident_values = coincident.split(', ')
            print(f"  Coincident values: {coincident_values}")
            
            # 确保coincident值的数量与维度数量匹配
            if len(coincident_values) != len(schedule_dims):
                print(f"  Warning: Number of coincident values ({len(coincident_values)}) doesn't match number of schedule dimensions ({len(schedule_dims)})")
            
            if permutable == '1' and len(coincident_values) >= 2:
                for j, dim in enumerate(schedule_dims):
                    filter_prefix = f"Filter {idx+1}"
                    if j < len(coincident_values):
                        if coincident_values[j] == '1':
                            dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                            dimensions['tileables'].append(dim_name)
                            print(f"  Dimension {j} ({dim}) is tileable")
                        else:
                            dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                            dimensions['non_tileables'].append(dim_name)
                            print(f"  Dimension {j} ({dim}) is not tileable")
                    else:
                        # 如果没有对应的coincident值，保守地认为不可分割
                        dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                        dimensions['non_tileables'].append(dim_name)
                        print(f"  Dimension {j} ({dim}) has no coincident value, assuming not tileable")
            else:
                # 如果不可重排或coincident值长度 < 2，则所有维度都不可分割
                if permutable != '1':
                    print(f"  Top-level filter block {idx+1} is not permutable, all dimensions are not tileable")
                else:
                    print(f"  Top-level filter block {idx+1} has less than 2 coincident values, all dimensions are not tileable")
                
                for j, dim in enumerate(schedule_dims):
                    filter_prefix = f"Filter {idx+1}"
                    dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                    dimensions['non_tileables'].append(dim_name)
                    print(f"  Dimension {j} ({dim}) is not tileable")
        else:
            print(f"  Band node information for top-level filter block {idx+1} is incomplete, cannot analyze")
    
    return dimensions

def analyze_benchmark(benchmark_file):
    """分析基准测试文件，确定哪些维度可以分割"""
    # 运行PPCG并获取调度树
    schedule_output = run_ppcg_and_get_schedule(benchmark_file)
    
    if not schedule_output:
        print("Unable to get schedule tree information, please check the PPCG command.")

    
    # 解析调度树
    dimensions = parse_schedule_tree(schedule_output)
    
    # 打印结果
    print("\nAnalysis Results:")
    print("Tileable dimensions:")
    for dim in dimensions['tileables']:
        print(f"  - {dim}")
    
    return dimensions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 detect_dimension.py <benchmark_file.c>")
        sys.exit(1)
    
    benchmark_file = sys.argv[1]
    analyze_benchmark(benchmark_file)