#!/usr/bin/env python3
import os
import subprocess
import re
import sys

def run_ppcg_and_get_schedule(benchmark_file, options=None):
    """运行PPCG并获取调度树信息"""
    if options is None:
        options = ["--target", "c", "--no-automatic-mixed-precision", 
                  "--split-tile", "--tile-size=1", 
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
        
        # 确保coincident值的数量与维度数量匹配
        if len(coincident_values) != len(schedule_dims):
            print(f"  Warning: Number of coincident values ({len(coincident_values)}) doesn't match number of schedule dimensions ({len(schedule_dims)})")
        
        # 分析哪些维度可以被划分
        if permutable == '1':
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
            print(f"  Top-level band node is not permutable, all dimensions are not tileable")
            for j, dim in enumerate(schedule_dims):
                filter_prefix = "Filter 1"  # 使用Filter 1替代Top-level band
                dim_name = f"{filter_prefix}, Dimension {j}: {dim}"
                dimensions['non_tileables'].append(dim_name)
                print(f"  Dimension {j} ({dim}) is not tileable")
        
        return dimensions
    
    # 如果没有顶级band节点，则继续尝试查找顶级sequence中的filter块
    sequence_match = re.search(r'child:\s+sequence:(.*?)(?=\Z)', schedule_output, re.DOTALL)
    
    if not sequence_match:
        print("Neither top-level band node nor sequence found")
        return dimensions
    
    sequence_content = sequence_match.group(1)
    
    # 使用缩进级别来匹配顶级filter块
    # 顶级filter应该有固定的缩进格式，比如"  - filter:"
    top_level_filters = re.findall(r'[ ]{2}- filter: "(.*?)"(?:\s+child:(.*?))?(?=\n[ ]{2}-|\Z)', 
                                    sequence_content, re.DOTALL)
    
    if not top_level_filters:
        print("No top-level filter blocks found")
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
            
            # 分析哪些维度可以被划分
            if permutable == '1':
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
                # 如果不可重排，则所有维度都不可分割
                print(f"  Top-level filter block {idx+1} is not permutable, all dimensions are not tileable")
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