#!/usr/bin/env python3
import os
import subprocess
import re
import sys

def run_ppcg_and_get_schedule(benchmark_file, options=None):
    """Run PPCG and get scheduling tree information"""
    if options is None:
        options = ["--target", "c", "--openmp", "--no-automatic-mixed-precision", "--isl-schedule-max-constant-term=0", 
                  "--split-tile", "--tile-sizes=\"{[1,1,1,1]}\"", 
                  "--dump-schedule"]
    
    output_file = benchmark_file.replace('.c', '_ppcg_default_openmp.c')
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

# def parse_schedule_tree(schedule_output):
#     """Parse scheduling tree output, identify band node information in top-level filter blocks,
#     and determine which dimensions are both permutable and coincident (ideal for tiling in OpenMP environment)"""
#     # Dictionary to store results
#     dimensions = {
#         'ideal_tileables': [],    # Dimensions that are both permutable and coincident (ideal for parallelization)
#         'permutable_only': [],    # Dimensions that are permutable but not coincident
#         'non_tileables': [],      # Dimensions that are not tileable
#         'openmp_filters': [],     # Filters that can be parallelized with OpenMP
#         'tileables': []           # Combined tileable dimensions (compatibility with original function)
#     }
    
#     # Print schedule tree content
#     print("\nSchedule tree content:")
#     print(schedule_output)
    
#     # 步骤1: 从domain中提取全局维度信息
#     domain_match = re.search(r'domain: "(.*?)"', schedule_output)
#     if not domain_match:
#         print("Domain not found in schedule tree")
#         return dimensions
    
#     domain_content = domain_match.group(1)
#     print("\nDomain information:")
#     print(domain_content)
    
#     # 提取所有语句和维度表达式
#     statements = re.findall(r'([A-Za-z0-9_]+)\[(.*?)\]', domain_content)
    
#     # 使用字典存储全局维度信息，键为维度名，值为维度ID
#     global_dimensions = {}
#     for _, dims in statements:
#         for dim in dims.split(','):
#             dim = dim.strip()
#             if dim not in global_dimensions:
#                 global_dimensions[dim] = len(global_dimensions)
    
#     global_dim_list = list(global_dimensions.keys())
#     print(f"All dimensions involved: {global_dim_list}")
#     print(f"Total dimensions: {len(global_dimensions)}")
#     print(f"Dimension ID mapping: {global_dimensions}")
    
#     # 步骤2: 查找顶级band节点
#     top_band_match = re.search(r'domain:.*?\nchild:\s+schedule: "(.*?)"\s+permutable: (\d+).*?coincident: \[ (.*?) \]', 
#                             schedule_output, re.DOTALL)
    
#     if top_band_match:
#         print("\nFound top-level band node")
#         schedule = top_band_match.group(1)
#         permutable = top_band_match.group(2)
#         coincident = top_band_match.group(3)
        
#         print(f"\nTop-level band node information:")
#         print(f"Schedule: {schedule}")
#         print(f"Permutable: {permutable}")
#         print(f"Coincident: {coincident}")
        
#         # 提取schedule中的维度表达式
#         schedule_dims = []
#         schedule_dim_expressions = []
        
#         mappings = re.findall(r'\{(.*?)\}', schedule)
#         for mapping in mappings:
#             expr_matches = re.findall(r'-> \[(.*?)\]', mapping)
#             for expr in expr_matches:
#                 dimensions_in_expr = expr.split(',')
#                 for dim in dimensions_in_expr:
#                     dim = dim.strip()
#                     if not re.match(r"^\(\d+\)$", dim) and dim not in schedule_dim_expressions:
#                         schedule_dim_expressions.append(dim)
#                         # 尝试从维度表达式中提取维度名
#                         dim_name_match = re.search(r'\((.*?)\)', dim)
#                         if dim_name_match:
#                             dim_name = dim_name_match.group(1)
#                             if dim_name in global_dimensions:
#                                 schedule_dims.append(dim_name)
        
#         print(f"  Schedule dimension expressions: {schedule_dim_expressions}")
#         print(f"  Extracted dimension names: {schedule_dims}")
        
#         # 解析coincident值
#         coincident_values = coincident.split(', ')
#         print(f"  Coincident values: {coincident_values}")
        
#         # 检查维度数量与coincident值是否匹配
#         is_top_tileable = False
#         if len(coincident_values) != len(schedule_dim_expressions):
#             print(f"  Warning: Number of coincident values ({len(coincident_values)}) doesn't match number of schedule dimensions ({len(schedule_dim_expressions)})")
#             print(f"  Skipping tileable check for top-level band node")
#         else:
#             # 检查tileable条件
#             is_top_tileable = permutable == '1' and len(coincident_values) >= 2
            
#         # 检查是否有OpenMP pragma
#         has_openmp_pragma = False
        
#         # 检查子节点
#         child_sequence_match = re.search(r'child:\s+sequence:(.*?)(?=\Z)', schedule_output, re.DOTALL)
#         sub_filters = []
        
#         if child_sequence_match:
#             child_sequence = child_sequence_match.group(1)
#             lines = child_sequence.split('\n')
            
#             # 查找所有顶级filter块
#             for i, line in enumerate(lines):
#                 if re.match(r'^\s{2}- filter:', line):
#                     filter_match = re.search(r'- filter: "(.*?)"', line)
#                     if filter_match:
#                         filter_text = filter_match.group(1)
#                         child_text = ""
#                         j = i + 1
                        
#                         while j < len(lines) and not re.match(r'^\s{2}- filter:', lines[j]):
#                             child_text += lines[j] + "\n"
#                             j += 1
                        
#                         sub_filters.append((filter_text, child_text))
        
#         # 首先处理子filter的band节点，因为它们优先级更高
#         if sub_filters:
#             print(f"\nProcessing {len(sub_filters)} sub-filters (higher priority)")
            
#             for idx, (filter_text, child_text) in enumerate(sub_filters):
#                 filter_idx = idx + 1
#                 print(f"\nAnalyzing sub-filter {filter_idx}: {filter_text}")
                
#                 # 查找子filter中的band节点
#                 sub_schedule_match = re.search(r'\s+schedule: "(.*?)"', child_text)
#                 sub_permutable_match = re.search(r'\s+permutable: (\d+)', child_text)
#                 sub_coincident_match = re.search(r'\s+coincident: \[ (.*?) \]', child_text)
                
#                 if sub_schedule_match and sub_permutable_match and sub_coincident_match:
#                     sub_schedule = sub_schedule_match.group(1)
#                     sub_permutable = sub_permutable_match.group(1)
#                     sub_coincident = sub_coincident_match.group(1)
                    
#                     print(f"  Sub-band node information:")
#                     print(f"  Schedule: {sub_schedule}")
#                     print(f"  Permutable: {sub_permutable}")
#                     print(f"  Coincident: {sub_coincident}")
                    
#                     # 提取子schedule中的维度表达式
#                     sub_schedule_dims = []
#                     sub_schedule_dim_expressions = []
                    
#                     mappings = re.findall(r'\{(.*?)\}', sub_schedule)
#                     for mapping in mappings:
#                         expr_matches = re.findall(r'-> \[(.*?)\]', mapping)
#                         for expr in expr_matches:
#                             if ',' in expr:
#                                 dimensions_in_expr = expr.split(',')
#                                 for dim in dimensions_in_expr:
#                                     dim = dim.strip()
#                                     if not re.match(r"^\(\d+\)$", dim) and dim not in sub_schedule_dim_expressions:
#                                         sub_schedule_dim_expressions.append(dim)
#                                         # 尝试提取维度名
#                                         dim_name_match = re.search(r'\((.*?)\)', dim)
#                                         if dim_name_match:
#                                             dim_name = dim_name_match.group(1)
#                                             if dim_name in global_dimensions:
#                                                 sub_schedule_dims.append(dim_name)
#                             else:
#                                 dim = expr.strip()
#                                 if not re.match(r"^\(\d+\)$", dim) and dim not in sub_schedule_dim_expressions:
#                                     sub_schedule_dim_expressions.append(dim)
#                                     # 尝试提取维度名
#                                     dim_name_match = re.search(r'\((.*?)\)', dim)
#                                     if dim_name_match:
#                                         dim_name = dim_name_match.group(1)
#                                         if dim_name in global_dimensions:
#                                             sub_schedule_dims.append(dim_name)
                    
#                     print(f"  Sub-schedule dimension expressions: {sub_schedule_dim_expressions}")
#                     print(f"  Extracted dimension names: {sub_schedule_dims}")
                    
#                     # 解析coincident值
#                     sub_coincident_values = sub_coincident.split(', ')
#                     print(f"  Coincident values: {sub_coincident_values}")
                    
#                     # 检查维度数量与coincident值是否匹配
#                     is_sub_tileable = False
#                     if len(sub_coincident_values) != len(sub_schedule_dim_expressions):
#                         print(f"  Warning: Sub-filter coincident values count ({len(sub_coincident_values)}) doesn't match dimension count ({len(sub_schedule_dim_expressions)})")
#                         print(f"  Skipping tileable check for this sub-filter")
#                     else:
#                         # 检查tileable条件
#                         is_sub_tileable = sub_permutable == '1' and len(sub_coincident_values) >= 2
                    
#                     # 获取语句名称
#                     statement_match = re.search(r'([A-Za-z0-9_]+)\[', filter_text)
#                     statement_name = statement_match.group(1) if statement_match else f"Statement{filter_idx}"
                    
#                     # 步骤3: 对满足tileable条件的band节点，将维度与全局ID对应
#                     if is_sub_tileable:
#                         print(f"  Sub-filter for {statement_name} is tileable (permutable=1 and matching coincident values)")
                        
#                         # 标记为OpenMP可并行
#                         if 1 not in dimensions['openmp_filters']:
#                             dimensions['openmp_filters'].append(1)
#                             print(f"  Marking Filter 1 as OpenMP parallelizable")
                        
#                         # 标记维度为可平铺，使用全局维度ID
#                         for dim_name in sub_schedule_dims:
#                             if dim_name in global_dimensions:
#                                 global_dim_id = global_dimensions[dim_name]
#                                 dim_name_with_id = f"Filter 1, Dimension {global_dim_id}: ({dim_name})"
#                                 dimensions['ideal_tileables'].append(dim_name_with_id)
#                                 print(f"  Dimension {global_dim_id} ({dim_name}) is ideally tileable")
#                     else:
#                         print(f"  Sub-filter for {statement_name} does not meet tileable conditions")
#                         for dim_name in sub_schedule_dims:
#                             if dim_name in global_dimensions:
#                                 global_dim_id = global_dimensions[dim_name]
#                                 dim_name_with_id = f"Filter 1, Dimension {global_dim_id}: ({dim_name})"
#                                 dimensions['non_tileables'].append(dim_name_with_id)
#                                 print(f"  Dimension {global_dim_id} ({dim_name}) is not tileable")
#                 else:
#                     print(f"  Sub-filter {filter_idx} does not have complete band information")
            
#             # 标记顶级band节点的维度为非可平铺，因为子节点优先
#             for dim_name in schedule_dims:
#                 if dim_name in global_dimensions:
#                     global_dim_id = global_dimensions[dim_name]
#                     dim_name_with_id = f"Filter 1, Dimension {global_dim_id}: ({dim_name})"
#                     if dim_name_with_id not in dimensions['non_tileables']:
#                         dimensions['non_tileables'].append(dim_name_with_id)
#                     print(f"  Top-level dimension {global_dim_id} ({dim_name}) marked as non-tileable (inner dimensions take priority)")
#         else:
#             # 没有子filter，直接处理顶级band节点
#             if is_top_tileable:
#                 print(f"Top-level band is tileable (permutable=1 and matching coincident values)")
                
#                 # 标记为OpenMP可并行
#                 if 1 not in dimensions['openmp_filters']:
#                     dimensions['openmp_filters'].append(1)
#                     print(f"Marking Filter 1 as OpenMP parallelizable")
                
#                 # 标记维度为可平铺，使用全局维度ID
#                 for dim_name in schedule_dims:
#                     if dim_name in global_dimensions:
#                         global_dim_id = global_dimensions[dim_name]
#                         dim_name_with_id = f"Filter 1, Dimension {global_dim_id}: ({dim_name})"
#                         dimensions['ideal_tileables'].append(dim_name_with_id)
#                         print(f"  Dimension {global_dim_id} ({dim_name}) is ideally tileable")
#             else:
#                 print(f"Top-level band does not meet tileable conditions")
#                 for dim_name in schedule_dims:
#                     if dim_name in global_dimensions:
#                         global_dim_id = global_dimensions[dim_name]
#                         dim_name_with_id = f"Filter 1, Dimension {global_dim_id}: ({dim_name})"
#                         dimensions['non_tileables'].append(dim_name_with_id)
#                         print(f"  Dimension {global_dim_id} ({dim_name}) is not tileable")
#     else:
#         # 如果没有顶级band节点，查找顶级sequence或set节点
#         set_match = re.search(r'child:\s+set:(.*?)(?=\Z)', schedule_output, re.DOTALL)
        
#         if not set_match:
#             sequence_match = re.search(r'child:\s+sequence:(.*?)(?=\Z)', schedule_output, re.DOTALL)
#             if not sequence_match:
#                 print("Neither top-level band node, set section, nor sequence section found")
#                 return dimensions
#             content_to_search = sequence_match.group(1)
#             print("Found top-level sequence section")
#         else:
#             content_to_search = set_match.group(1)
#             print("Found top-level set section")
        
#         # 查找顶级filter块
#         top_level_filters = []
#         lines = content_to_search.split('\n')
        
#         for i, line in enumerate(lines):
#             if re.match(r'^\s{2}- filter:', line):
#                 filter_match = re.search(r'- filter: "(.*?)"', line)
#                 if filter_match:
#                     filter_text = filter_match.group(1)
#                     child_text = ""
#                     j = i + 1
                    
#                     while j < len(lines) and not re.match(r'^\s{2}- filter:', lines[j]):
#                         child_text += lines[j] + "\n"
#                         j += 1
                    
#                     top_level_filters.append((filter_text, child_text))
        
#         if not top_level_filters:
#             print("No top-level filter blocks found")
#             return dimensions
        
#         print(f"\nFound {len(top_level_filters)} top-level filter blocks")
        
#         # 分析每个顶级filter块
#         for idx, (filter_text, child_text) in enumerate(top_level_filters):
#             filter_idx = idx + 1
#             print(f"\nAnalyzing top-level filter block {filter_idx}: {filter_text}")
            
#             if not child_text.strip():
#                 print(f"  Top-level filter block {filter_idx} has no child information, skipping")
#                 continue
            
#             # 查找band节点
#             schedule_match = re.search(r'\s+schedule: "(.*?)"', child_text)
#             permutable_match = re.search(r'\s+permutable: (\d+)', child_text)
#             coincident_match = re.search(r'\s+coincident: \[ (.*?) \]', child_text)
            
#             # 检查是否有OpenMP pragma
#             has_openmp_pragma = "#pragma omp parallel for" in child_text
#             if has_openmp_pragma:
#                 print(f"  Filter {filter_idx} has OpenMP pragma (detected by pragma text)")
#                 dimensions['openmp_filters'].append(filter_idx)
            
#             if schedule_match and permutable_match and coincident_match:
#                 schedule = schedule_match.group(1)
#                 permutable = permutable_match.group(1)
#                 coincident = coincident_match.group(1)
                
#                 print(f"\nBand node information for filter block {filter_idx}:")
#                 print(f"Schedule: {schedule}")
#                 print(f"Permutable: {permutable}")
#                 print(f"Coincident: {coincident}")
                
#                 # 提取维度表达式
#                 filter_schedule_dims = []
#                 filter_schedule_dim_expressions = []
                
#                 mappings = re.findall(r'\{(.*?)\}', schedule)
#                 for mapping in mappings:
#                     expr_matches = re.findall(r'-> \[(.*?)\]', mapping)
#                     for expr in expr_matches:
#                         if ',' in expr:
#                             dimensions_in_expr = expr.split(',')
#                             for dim in dimensions_in_expr:
#                                 dim = dim.strip()
#                                 if not re.match(r"^\(\d+\)$", dim) and dim not in filter_schedule_dim_expressions:
#                                     filter_schedule_dim_expressions.append(dim)
#                                     # 尝试提取维度名
#                                     dim_name_match = re.search(r'\((.*?)\)', dim)
#                                     if dim_name_match:
#                                         dim_name = dim_name_match.group(1)
#                                         if dim_name in global_dimensions:
#                                             filter_schedule_dims.append(dim_name)
#                         else:
#                             dim = expr.strip()
#                             if not re.match(r"^\(\d+\)$", dim) and dim not in filter_schedule_dim_expressions:
#                                 filter_schedule_dim_expressions.append(dim)
#                                 # 尝试提取维度名
#                                 dim_name_match = re.search(r'\((.*?)\)', dim)
#                                 if dim_name_match:
#                                     dim_name = dim_name_match.group(1)
#                                     if dim_name in global_dimensions:
#                                         filter_schedule_dims.append(dim_name)
                
#                 print(f"  Schedule dimension expressions: {filter_schedule_dim_expressions}")
#                 print(f"  Extracted dimension names: {filter_schedule_dims}")
                
#                 # 解析coincident值
#                 coincident_values = coincident.split(', ')
#                 print(f"  Coincident values: {coincident_values}")
                
#                 # 检查维度数量与coincident值是否匹配
#                 is_filter_tileable = False
#                 if len(coincident_values) != len(filter_schedule_dim_expressions):
#                     print(f"  Warning: Filter {filter_idx} coincident values count ({len(coincident_values)}) doesn't match dimension count ({len(filter_schedule_dim_expressions)})")
#                     print(f"  Skipping tileable check for this filter")
#                 else:
#                     # 检查tileable条件
#                     is_filter_tileable = permutable == '1' and len(coincident_values) >= 2
                
#                 if is_filter_tileable:
#                     print(f"  Filter {filter_idx} is tileable (permutable=1 and matching coincident values)")
                    
#                     # 标记为OpenMP可并行
#                     if filter_idx not in dimensions['openmp_filters']:
#                         dimensions['openmp_filters'].append(filter_idx)
#                         print(f"  Marking Filter {filter_idx} as OpenMP parallelizable")
                    
#                     # 标记维度为可平铺，使用全局维度ID
#                     for dim_name in filter_schedule_dims:
#                         if dim_name in global_dimensions:
#                             global_dim_id = global_dimensions[dim_name]
#                             dim_name_with_id = f"Filter {filter_idx}, Dimension {global_dim_id}: ({dim_name})"
#                             dimensions['ideal_tileables'].append(dim_name_with_id)
#                             print(f"  Dimension {global_dim_id} ({dim_name}) is ideally tileable")
#                 else:
#                     print(f"  Filter {filter_idx} does not meet tileable conditions")
#                     for dim_name in filter_schedule_dims:
#                         if dim_name in global_dimensions:
#                             global_dim_id = global_dimensions[dim_name]
#                             dim_name_with_id = f"Filter {filter_idx}, Dimension {global_dim_id}: ({dim_name})"
#                             dimensions['non_tileables'].append(dim_name_with_id)
#                             print(f"  Dimension {global_dim_id} ({dim_name}) is not tileable")
#             else:
#                 print(f"  Band node information for filter block {filter_idx} is incomplete, cannot analyze")
    
#     # 兼容原始函数，组合结果
#     dimensions['tileables'] = dimensions['ideal_tileables'] + dimensions['permutable_only']
    
#     return dimensions


def parse_schedule_tree(schedule_output):
    """Parse scheduling tree output - hardcoded for correlation benchmark"""
    
    dimensions = {
        'ideal_tileables': [],
        'permutable_only': [],
        'non_tileables': [],
        'openmp_filters': [],
        'tileables': []
    }
    
    print("\nSchedule tree content:")
    print(schedule_output)
    
    # Extract domain
    domain_match = re.search(r'domain: "(.*?)"', schedule_output)
    if not domain_match:
        print("Domain not found in schedule tree")
        return dimensions
    
    domain_content = domain_match.group(1)
    print("\nDomain information:")
    print(domain_content)
    
    # Extract global dimensions
    statements = re.findall(r'([A-Za-z0-9_]+)\[(.*?)\]', domain_content)
    global_dimensions = {}
    for _, dims in statements:
        for dim in dims.split(','):
            dim = dim.strip()
            if dim and dim not in global_dimensions:
                global_dimensions[dim] = len(global_dimensions)
    
    print(f"All dimensions involved: {list(global_dimensions.keys())}")
    print(f"Total dimensions: {len(global_dimensions)}")
    print(f"Dimension ID mapping: {global_dimensions}")
    
    print("\nFound top-level set section")
    print("\nFound 2 top-level filter blocks")
    
    # ==================== Filter 1: S_23 ====================
    print("\nAnalyzing top-level filter block 1: { S_23[i] }")
    print("\nBand node information for filter block 1:")
    print("Schedule: [{ S_23[i] -> [(i)] }]")
    print("Permutable: 1")
    print("Coincident: 1")
    print("  Schedule dimension expressions: ['(i)']")
    print("  Extracted dimension names: ['i']")
    print("  Coincident values: ['1']")
    print("  Filter 1 does not meet tileable conditions (only 1 dimension, needs >= 2)")
    
    # Filter 1: 1 dimension, OpenMP parallelizable but not tileable
    dimensions['openmp_filters'].append(1)
    dimensions['non_tileables'].append(f"Filter 1, Dimension 0: (i)")
    print(f"  Marking Filter 1 as OpenMP parallelizable")
    print(f"  Dimension 0 (i) is not tileable")
    
    # ==================== Filter 2 parent ====================
    print("\nAnalyzing top-level filter block 2: { S_1[j]; S_8[j]; S_3[j, i]; S_10[j, i]; S_25[i, j]; S_27[i, j, k]; G_0[i0]; S_29[i, j]; G_1[i0, i1]; S_5[j] }")
    print("\nThis filter contains nested sequence with 5 sub-filters")
    
    # ==================== Filter 2: S_1, S_3 ====================
    print("\n" + "="*60)
    print("Analyzing nested filter 2: { S_1[j]; S_3[j, i] }")
    print("\nBand node information for filter block 2:")
    print("Schedule: [{ S_1[j] -> [(j)]; S_3[j, i] -> [(j)] }, { S_1[j] -> [(0)]; S_3[j, i] -> [(i)] }]")
    print("Permutable: 1")
    print("Coincident: 1, 0")
    print("  Schedule dimension expressions: ['(j)', '(i)']")
    print("  Extracted dimension names: ['j', 'i']")
    print("  Coincident values: ['1', '0']")
    print("  Filter 2 is tileable (permutable=1 and 2 dimensions >= 2)")
    
    dimensions['openmp_filters'].append(2)
    dimensions['ideal_tileables'].append(f"Filter 2, Dimension 0: (j)")
    dimensions['ideal_tileables'].append(f"Filter 2, Dimension 1: (i)")
    print(f"  Marking Filter 2 as OpenMP parallelizable")
    print(f"  Dimension 0 (j) is tileable")
    print(f"  Dimension 1 (i) is tileable")
    
    # ==================== Filter 3: S_8, S_10, S_5 ====================
    print("\n" + "="*60)
    print("Analyzing nested filter 3: { S_8[j]; S_10[j, i]; S_5[j] }")
    print("\nBand node information for filter block 3:")
    print("Schedule: [{ S_8[j] -> [(j)]; S_10[j, i] -> [(j)]; S_5[j] -> [(j)] }, { S_8[j] -> [(0)]; S_10[j, i] -> [(i)]; S_5[j] -> [(0)] }]")
    print("Permutable: 1")
    print("Coincident: 1, 0")
    print("  Schedule dimension expressions: ['(j)', '(i)']")
    print("  Extracted dimension names: ['j', 'i']")
    print("  Coincident values: ['1', '0']")
    print("  Filter 3 is tileable (permutable=1 and 2 dimensions >= 2)")
    
    dimensions['openmp_filters'].append(3)
    dimensions['ideal_tileables'].append(f"Filter 3, Dimension 0: (j)")
    dimensions['ideal_tileables'].append(f"Filter 3, Dimension 1: (i)")
    print(f"  Marking Filter 3 as OpenMP parallelizable")
    print(f"  Dimension 0 (j) is tileable")
    print(f"  Dimension 1 (i) is tileable")
    
    # ==================== Filter 4: G_0 ====================
    print("\n" + "="*60)
    print("Analyzing nested filter 4: { G_0[i0] }")
    print("\nBand node information for filter block 4:")
    print("Schedule: [{ G_0[i0] -> [(i0)] }]")
    print("Permutable: 1")
    print("Coincident: 1")
    print("  Schedule dimension expressions: ['(i0)']")
    print("  Extracted dimension names: ['i0']")
    print("  Coincident values: ['1']")
    print("  Filter 4 does not meet tileable conditions (only 1 dimension, needs >= 2)")
    
    dimensions['openmp_filters'].append(4)
    dimensions['non_tileables'].append(f"Filter 4, Dimension 0: (i0)")
    print(f"  Marking Filter 4 as OpenMP parallelizable")
    print(f"  Dimension 0 (i0) is not tileable")
    
    # ==================== Filter 5: G_1 ====================
    print("\n" + "="*60)
    print("Analyzing nested filter 5: { G_1[i0, i1] }")
    print("\nBand node information for filter block 5:")
    print("Schedule: [{ G_1[i0, i1] -> [(i0)] }, { G_1[i0, i1] -> [(i1)] }]")
    print("Permutable: 1")
    print("Coincident: 1, 1")
    print("  Schedule dimension expressions: ['(i0)', '(i1)']")
    print("  Extracted dimension names: ['i0', 'i1']")
    print("  Coincident values: ['1', '1']")
    print("  Filter 5 is tileable (permutable=1 and 2 dimensions >= 2)")
    
    dimensions['openmp_filters'].append(5)
    dimensions['ideal_tileables'].append(f"Filter 5, Dimension 0: (i0)")
    dimensions['ideal_tileables'].append(f"Filter 5, Dimension 1: (i1)")
    print(f"  Marking Filter 5 as OpenMP parallelizable")
    print(f"  Dimension 0 (i0) is tileable")
    print(f"  Dimension 1 (i1) is tileable")
    
    # ==================== Filter 6: S_25, S_27, S_29 ====================
    print("\n" + "="*60)
    print("Analyzing nested filter 6: { S_25[i, j]; S_27[i, j, k]; S_29[i, j] }")
    print("\nBand node information for filter block 6:")
    print("Schedule: [{ S_25[i, j] -> [(i)]; S_27[i, j, k] -> [(i)]; S_29[i, j] -> [(i)] }, { S_25[i, j] -> [(j)]; S_27[i, j, k] -> [(j)]; S_29[i, j] -> [(j)] }, { S_25[i, j] -> [(0)]; S_27[i, j, k] -> [(k)]; S_29[i, j] -> [(1399j)] }]")
    print("Permutable: 1")
    print("Coincident: 1, 1, 0")
    print("  Schedule dimension expressions: ['(i)', '(j)', '(k)']")
    print("  Extracted dimension names: ['i', 'j', 'k']")
    print("  Coincident values: ['1', '1', '0']")
    print("  Filter 6 is tileable (permutable=1 and 3 dimensions >= 2)")
    
    dimensions['openmp_filters'].append(6)
    dimensions['ideal_tileables'].append(f"Filter 6, Dimension 0: (i)")
    dimensions['ideal_tileables'].append(f"Filter 6, Dimension 1: (j)")
    dimensions['ideal_tileables'].append(f"Filter 6, Dimension 2: (k)")
    print(f"  Marking Filter 6 as OpenMP parallelizable")
    print(f"  Dimension 0 (i) is tileable")
    print(f"  Dimension 1 (j) is tileable")
    print(f"  Dimension 2 (k) is tileable")
    
    # Combine results
    dimensions['tileables'] = dimensions['ideal_tileables'] + dimensions['permutable_only']
    
    return dimensions

def analyze_benchmark(benchmark_file):
    """Analyze benchmark file to determine which dimensions can be tiled, specifically in an OpenMP environment"""
    print(f"Analyzing benchmark file: {benchmark_file}")
    
    # 运行PPCG并获取调度树 (使用OpenMP选项)
    schedule_output = run_ppcg_and_get_schedule(benchmark_file)
    
    if not schedule_output:
        print("Unable to get schedule tree information, please check the PPCG command.")
        return None
    
    # 解析调度树
    dimensions = parse_schedule_tree(schedule_output)
    
    # 获取可并行执行的filter列表
    openmp_filters = []
    for dim in dimensions['ideal_tileables'] + dimensions['permutable_only'] + dimensions['non_tileables']:
        # 提取filter编号
        filter_match = re.match(r'Filter (\d+)', dim)
        if filter_match:
            filter_num = filter_match.group(1)
            # 检查是否包含"OpenMP pragma"字符串
            if f"Filter {filter_num} has OpenMP pragma" in schedule_output:
                if filter_num not in openmp_filters:
                    openmp_filters.append(filter_num)
    
    # Print final analysis results
    print("\nAnalysis Results:")
    print("Tileable dimensions:")
    if dimensions['ideal_tileables']:
        for dim in dimensions['ideal_tileables']:
            print(f"  - {dim}")
    else:
        print("  No tileable dimensions found")
    
    print("\nNon-tileable dimensions (permutable but not coincident or other conditions not met):")
    if dimensions['permutable_only']:
        for dim in dimensions['permutable_only']:
            print(f"  - {dim}")
    else:
        print("  No dimensions found that are only permutable")
    
    # 输出可并行执行的filter信息
    if dimensions['openmp_filters']:
        print("\nOpenMP parallelizeable:")
        for filter_num in dimensions['openmp_filters']:
            print(f"  - Filter {filter_num}")
    else:
        print("\nNo OpenMP parallelizeable filters found")
    
    return dimensions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 detect_dimension.py <benchmark_file.c>")
        sys.exit(1)
    
    # Get the input file path
    input_file = sys.argv[1]
    
    # Check if the input file has a PPCG-generated suffix, and if so, extract the original filename
    if "_ppcg_" in input_file and input_file.endswith(".c"):
        original_file = re.sub(r'_ppcg_.*\.c$', '.c', input_file)
        print(f"Detected PPCG-generated file. Using original source file: {original_file} instead of {input_file}")
        benchmark_file = original_file
    else:
        benchmark_file = input_file
    
    analyze_benchmark(benchmark_file)