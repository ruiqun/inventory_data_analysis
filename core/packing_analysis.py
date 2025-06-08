# -*- coding: utf-8 -*-
"""
装箱分析模块 - 专门处理装箱分析相关功能
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import PACKING_CONFIG

class PackingAnalyzer:
    """装箱分析器"""
    
    def __init__(self, container_info):
        """
        初始化装箱分析器
        
        Args:
            container_info: 容器信息字典，包含length, width, height, size, volume
        """
        self.container_info = container_info
        # 容器配置中的尺寸已经是mm单位，无需转换
        self.container_length_mm = container_info['length']
        self.container_width_mm = container_info['width']  
        self.container_height_mm = container_info['height']
        
    def validate_goods_size(self, length, width, height):
        """
        验证货物尺寸是否有效
        
        Args:
            length, width, height: 货物尺寸(mm)
            
        Returns:
            bool: 是否有效
        """
        # 检查是否大于0
        if length <= 0 or width <= 0 or height <= 0:
            return False
            
        # 检查尺寸合理性
        min_size = PACKING_CONFIG["size_limits"]["min_size_mm"]
        max_size = PACKING_CONFIG["size_limits"]["max_size_mm"]
        
        if (length < min_size or width < min_size or height < min_size or
            length > max_size or width > max_size or height > max_size):
            return False
            
        return True
        
    def calculate_packing_options(self, goods_length, goods_width, goods_height):
        """
        计算6种摆放方式的装箱数量
        
        Args:
            goods_length, goods_width, goods_height: 货物尺寸(mm)
            
        Returns:
            list: 6种摆放方式的装箱数量
        """
        packing_options = []
        max_items = PACKING_CONFIG["max_items_per_box"]
        
        try:
            # 方式1: 长→长，宽→宽，高→高
            if (goods_length <= self.container_length_mm and 
                goods_width <= self.container_width_mm and 
                goods_height <= self.container_height_mm):
                option1 = (int(self.container_length_mm // goods_length) * 
                          int(self.container_width_mm // goods_width) * 
                          int(self.container_height_mm // goods_height))
                option1 = min(option1, max_items)
            else:
                option1 = 0
            packing_options.append(option1)
            
            # 方式2: 长→长，宽→高，高→宽
            if (goods_length <= self.container_length_mm and 
                goods_width <= self.container_height_mm and 
                goods_height <= self.container_width_mm):
                option2 = (int(self.container_length_mm // goods_length) * 
                          int(self.container_height_mm // goods_width) * 
                          int(self.container_width_mm // goods_height))
                option2 = min(option2, max_items)
            else:
                option2 = 0
            packing_options.append(option2)
            
            # 方式3: 长→宽，宽→长，高→高
            if (goods_length <= self.container_width_mm and 
                goods_width <= self.container_length_mm and 
                goods_height <= self.container_height_mm):
                option3 = (int(self.container_width_mm // goods_length) * 
                          int(self.container_length_mm // goods_width) * 
                          int(self.container_height_mm // goods_height))
                option3 = min(option3, max_items)
            else:
                option3 = 0
            packing_options.append(option3)
            
            # 方式4: 长→宽，宽→高，高→长
            if (goods_length <= self.container_width_mm and 
                goods_width <= self.container_height_mm and 
                goods_height <= self.container_length_mm):
                option4 = (int(self.container_width_mm // goods_length) * 
                          int(self.container_height_mm // goods_width) * 
                          int(self.container_length_mm // goods_height))
                option4 = min(option4, max_items)
            else:
                option4 = 0
            packing_options.append(option4)
            
            # 方式5: 长→高，宽→长，高→宽
            if (goods_length <= self.container_height_mm and 
                goods_width <= self.container_length_mm and 
                goods_height <= self.container_width_mm):
                option5 = (int(self.container_height_mm // goods_length) * 
                          int(self.container_length_mm // goods_width) * 
                          int(self.container_width_mm // goods_height))
                option5 = min(option5, max_items)
            else:
                option5 = 0
            packing_options.append(option5)
            
            # 方式6: 长→高，宽→宽，高→长
            if (goods_length <= self.container_height_mm and 
                goods_width <= self.container_width_mm and 
                goods_height <= self.container_length_mm):
                option6 = (int(self.container_height_mm // goods_length) * 
                          int(self.container_width_mm // goods_width) * 
                          int(self.container_length_mm // goods_height))
                option6 = min(option6, max_items)
            else:
                option6 = 0
            packing_options.append(option6)
            
        except (OverflowError, ValueError):
            # 如果计算过程中出现错误，所有方式都设为0
            packing_options = [0, 0, 0, 0, 0, 0]
            
        return packing_options
        
    def analyze_single_sku(self, goods_length, goods_width, goods_height, inventory_qty, sku_index):
        """
        分析单个SKU的装箱情况
        
        Args:
            goods_length, goods_width, goods_height: 货物尺寸(mm)
            inventory_qty: 库存数量
            sku_index: SKU索引
            
        Returns:
            dict: 装箱分析结果
        """
        # 验证尺寸
        if not self.validate_goods_size(goods_length, goods_width, goods_height):
            return None
            
        # 计算6种摆放方式
        packing_options = self.calculate_packing_options(goods_length, goods_width, goods_height)
        
        # 取最大值
        max_per_box = max(packing_options) if packing_options else 0
        
        # 计算需要的箱子数
        if max_per_box > 0 and inventory_qty > 0:
            boxes_needed = np.ceil(inventory_qty / max_per_box)
        else:
            boxes_needed = float('inf')  # 装不下的情况
            
        return {
            'SKU_index': sku_index,
            'goods_length_mm': goods_length,
            'goods_width_mm': goods_width,
            'goods_height_mm': goods_height,
            'inventory_qty': inventory_qty,
            'packing_options': packing_options,
            'max_per_box': max_per_box,
            'boxes_needed': boxes_needed
        }
        
    def analyze_batch(self, df, length_column, width_column, height_column, 
                     inventory_column, data_unit="cm"):
        """
        批量分析装箱情况
        
        Args:
            df: 数据框
            length_column, width_column, height_column: 尺寸列名
            inventory_column: 库存列名
            data_unit: 数据单位
            
        Returns:
            tuple: (装箱结果列表, 处理的数据行数)
        """
        # 单位转换
        conversion_factor = PACKING_CONFIG["unit_conversion"][data_unit]
        
        # 提取并转换货物尺寸数据
        goods_length = pd.to_numeric(df[length_column], errors='coerce') * conversion_factor
        goods_width = pd.to_numeric(df[width_column], errors='coerce') * conversion_factor  
        goods_height = pd.to_numeric(df[height_column], errors='coerce') * conversion_factor
        inventory_qty = pd.to_numeric(df[inventory_column], errors='coerce')
        
        # 过滤掉无效数据
        valid_mask = ~(goods_length.isna() | goods_width.isna() | goods_height.isna() | inventory_qty.isna())
        valid_indices = df[valid_mask].index
        
        packing_results = []
        batch_size = PACKING_CONFIG["batch_size"]
        
        # 分批处理
        for i in range(0, len(valid_indices), batch_size):
            batch_indices = valid_indices[i:i + batch_size]
            
            for idx in batch_indices:
                try:
                    result = self.analyze_single_sku(
                        goods_length[idx], goods_width[idx], goods_height[idx],
                        inventory_qty[idx], idx
                    )
                    if result:
                        packing_results.append(result)
                except Exception:
                    continue  # 跳过错误的数据
                    
        return packing_results, len(valid_indices)
        
    def generate_summary_statistics(self, packing_results, total_inventory):
        """
        生成装箱分析统计摘要
        
        Args:
            packing_results: 装箱结果列表
            total_inventory: 总库存数量
            
        Returns:
            dict: 统计摘要
        """
        if not packing_results:
            return {
                'total_sku_count': 0,
                'can_pack_items': 0,
                'cannot_pack_items': 0,
                'total_inventory': total_inventory,
                'total_boxes_needed': 0,
                'success_rate': 0,
                'avg_utilization': 0,
                'avg_boxes_per_sku': 0
            }
            
        total_items = len(packing_results)
        can_pack_items = len([r for r in packing_results if r['max_per_box'] > 0])
        cannot_pack_items = total_items - can_pack_items
        
        # 计算总需箱子数（排除装不下的）
        total_boxes_finite = sum([r['boxes_needed'] for r in packing_results 
                                if r['boxes_needed'] != float('inf')])
        
        # 计算平均装载率
        valid_results = [r for r in packing_results 
                        if r['max_per_box'] > 0 and r['boxes_needed'] != float('inf')]
        
        avg_utilization = 0
        if valid_results:
            total_capacity = sum([r['boxes_needed'] * r['max_per_box'] for r in valid_results])
            total_inventory_valid = sum([r['inventory_qty'] for r in valid_results])
            avg_utilization = total_inventory_valid / total_capacity if total_capacity > 0 else 0
            
        return {
            'total_sku_count': total_items,
            'can_pack_items': can_pack_items,
            'cannot_pack_items': cannot_pack_items,
            'total_inventory': total_inventory,
            'total_boxes_needed': total_boxes_finite,
            'success_rate': (can_pack_items / total_items * 100) if total_items > 0 else 0,
            'avg_utilization': avg_utilization,
            'avg_boxes_per_sku': total_boxes_finite / can_pack_items if can_pack_items > 0 else 0
        }
        
    def check_data_quality(self, goods_length, goods_width, goods_height):
        """
        检查数据质量，识别异常数据
        
        Args:
            goods_length, goods_width, goods_height: 货物尺寸Series
            
        Returns:
            list: 质量问题列表
        """
        quality_issues = []
        
        # 检查异常小的尺寸（可能单位错误）
        very_small = (goods_length < 10) | (goods_width < 10) | (goods_height < 10)
        if very_small.sum() > 0:
            quality_issues.append(f"发现 {very_small.sum()} 个商品尺寸小于1cm，可能存在单位错误")
        
        # 检查异常大的尺寸
        very_large = (goods_length > 50000) | (goods_width > 50000) | (goods_height > 50000)
        if very_large.sum() > 0:
            quality_issues.append(f"发现 {very_large.sum()} 个商品尺寸大于5m，可能存在数据错误")
        
        # 检查负数或零值
        invalid_size = (goods_length <= 0) | (goods_width <= 0) | (goods_height <= 0)
        if invalid_size.sum() > 0:
            quality_issues.append(f"发现 {invalid_size.sum()} 个商品尺寸为负数或零")
            
        return quality_issues
        
    def generate_optimization_suggestions(self, packing_results, summary_stats):
        """
        生成装箱优化建议
        
        Args:
            packing_results: 装箱结果列表
            summary_stats: 统计摘要
            
        Returns:
            list: 优化建议列表
        """
        suggestions = []
        
        # 分析问题货物
        problem_items = [r for r in packing_results if r['max_per_box'] == 0]
        if problem_items:
            suggestions.append(f"⚠️ 有 {len(problem_items)} 个SKU无法装入当前容器")
            suggestions.append("• 考虑使用更大规格的容器")
            suggestions.append("• 检查货物尺寸数据是否正确")
            suggestions.append("• 考虑拆分大件货物")
        
        # 分析装箱效率
        if summary_stats.get('avg_boxes_per_sku', 0) > 10:
            avg_boxes = summary_stats['avg_boxes_per_sku']
            suggestions.append(f"📦 平均每SKU需要 {avg_boxes:.1f} 个箱子，建议优化装箱策略")
        elif summary_stats.get('can_pack_items', 0) > 0:
            avg_boxes = summary_stats['avg_boxes_per_sku']
            suggestions.append(f"✅ 装箱效率良好，平均每SKU需要 {avg_boxes:.1f} 个箱子")
        
        # 容积利用率建议
        avg_utilization = summary_stats.get('avg_utilization', 0)
        if avg_utilization < 0.5:
            suggestions.append("📏 整体容积利用率较低，可考虑使用更小规格的容器")
        elif avg_utilization > 0.9:
            suggestions.append("✅ 容积利用率很高，当前容器规格匹配度良好")
            
        if not suggestions:
            suggestions.append("✅ 装箱方案整体表现良好，无明显优化点")
            
        return suggestions 