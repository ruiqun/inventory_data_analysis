# -*- coding: utf-8 -*-
"""
ABC分析模块 - 专门处理ABC分析相关功能
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple
from config import ANALYSIS_DIMENSIONS

class ABCAnalyzer:
    """ABC分析器"""
    
    def __init__(self, analysis_config=None):
        """
        初始化ABC分析器
        
        Args:
            analysis_config: 分析配置字典
        """
        self.config = analysis_config or self._get_default_config()
        
    def _get_default_config(self):
        """获取默认配置"""
        return {
            'classification_method': 'revenue',  # revenue, quantity, frequency
            'a_percentage': 70,  # A类累计百分比
            'b_percentage': 20,  # B类累计百分比
            'c_percentage': 10,   # C类累计百分比
            'sort_order': 'desc'  # desc, asc
        }
    
    def validate_data(self, df: pd.DataFrame, sku_column: str, 
                     quantity_column: str) -> Tuple[bool, List[str]]:
        """
        验证数据有效性
        
        Args:
            df: 数据框
            sku_column: SKU列名
            quantity_column: 数量列名
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查数据框是否为空
        if df.empty:
            errors.append("数据框为空")
            return False, errors
        
        # 检查必需列是否存在
        if sku_column not in df.columns:
            errors.append(f"SKU列 '{sku_column}' 不存在")
        
        if quantity_column not in df.columns:
            errors.append(f"数量列 '{quantity_column}' 不存在")
        
        # 检查SKU列是否有数据
        if sku_column in df.columns:
            if df[sku_column].isnull().all():
                errors.append(f"SKU列 '{sku_column}' 没有有效数据")
        
        # 检查数量列的数据类型
        if quantity_column in df.columns:
            try:
                qty_data = pd.to_numeric(df[quantity_column], errors='coerce')
                if qty_data.isna().all():
                    errors.append(f"数量列 '{quantity_column}' 无法转换为数值")
                elif qty_data.isna().any():
                    na_count = qty_data.isna().sum()
                    errors.append(f"数量列 '{quantity_column}' 有 {na_count} 个无效值")
            except Exception as e:
                errors.append(f"数量列数据验证失败: {str(e)}")
        
        return len(errors) == 0, errors
    
    def calculate_abc_classification(self, df: pd.DataFrame, sku_column: str, 
                                   quantity_column: str) -> pd.DataFrame:
        """
        计算ABC分类（按照用户需求重新设计）
        
        Args:
            df: 数据框
            sku_column: SKU列名
            quantity_column: 数量列名
            
        Returns:
            pd.DataFrame: 包含ABC分类结果的数据框
        """
        # 数据预处理 - 按SKU聚合数量
        result_df = df.groupby(sku_column).agg({
            quantity_column: 'sum'
        }).reset_index()
        
        # 重命名列
        result_df.columns = ['SKU', '出库数量']
        
        # 转换为数值并移除无效数据
        result_df['出库数量'] = pd.to_numeric(result_df['出库数量'], errors='coerce')
        result_df = result_df.dropna(subset=['出库数量'])
        result_df = result_df[result_df['出库数量'] > 0]
        
        if result_df.empty:
            return result_df
        
        # 按数量降序排序
        result_df = result_df.sort_values('出库数量', ascending=False)
        
        # 计算占比和累计占比
        total_quantity = result_df['出库数量'].sum()
        result_df['数量占比(%)'] = (result_df['出库数量'] / total_quantity * 100)
        result_df['累计占比(%)'] = result_df['数量占比(%)'].cumsum()
        
        # ABC分类（基于累计占比）
        result_df['ABC分类'] = 'C'
        a_threshold = self.config['a_percentage']
        ab_threshold = a_threshold + self.config['b_percentage']
        
        result_df.loc[result_df['累计占比(%)'] <= a_threshold, 'ABC分类'] = 'A'
        result_df.loc[(result_df['累计占比(%)'] > a_threshold) & 
                     (result_df['累计占比(%)'] <= ab_threshold), 'ABC分类'] = 'B'
        
        # 添加排名
        result_df['排名'] = range(1, len(result_df) + 1)
        
        # 重新排列列顺序，便于展示
        result_df = result_df[['排名', 'SKU', '出库数量', '数量占比(%)', '累计占比(%)', 'ABC分类']]
        
        return result_df
    
    def generate_summary_statistics(self, abc_results: pd.DataFrame) -> Dict[str, Any]:
        """
        生成ABC分析统计摘要
        
        Args:
            abc_results: ABC分析结果数据框
            
        Returns:
            dict: 统计摘要
        """
        if abc_results.empty:
            return {
                'total_items': 0,
                'total_value': 0,
                'a_items': 0, 'a_value': 0, 'a_percentage': 0,
                'b_items': 0, 'b_value': 0, 'b_percentage': 0,
                'c_items': 0, 'c_value': 0, 'c_percentage': 0
            }
        
        total_items = len(abc_results)
        total_quantity = abc_results['出库数量'].sum()
        
        # A类统计
        a_data = abc_results[abc_results['ABC分类'] == 'A']
        a_items = len(a_data)
        a_quantity = a_data['出库数量'].sum() if not a_data.empty else 0
        a_percentage = (a_quantity / total_quantity * 100) if total_quantity > 0 else 0
        
        # B类统计
        b_data = abc_results[abc_results['ABC分类'] == 'B']
        b_items = len(b_data)
        b_quantity = b_data['出库数量'].sum() if not b_data.empty else 0
        b_percentage = (b_quantity / total_quantity * 100) if total_quantity > 0 else 0
        
        # C类统计
        c_data = abc_results[abc_results['ABC分类'] == 'C']
        c_items = len(c_data)
        c_quantity = c_data['出库数量'].sum() if not c_data.empty else 0
        c_percentage = (c_quantity / total_quantity * 100) if total_quantity > 0 else 0
        
        return {
            'total_items': total_items,
            'total_quantity': total_quantity,
            'a_items': a_items,
            'a_quantity': a_quantity,
            'a_percentage': a_percentage,
            'a_item_percentage': (a_items / total_items * 100) if total_items > 0 else 0,
            'b_items': b_items,
            'b_quantity': b_quantity,
            'b_percentage': b_percentage,
            'b_item_percentage': (b_items / total_items * 100) if total_items > 0 else 0,
            'c_items': c_items,
            'c_quantity': c_quantity,
            'c_percentage': c_percentage,
            'c_item_percentage': (c_items / total_items * 100) if total_items > 0 else 0,
            'analysis_method': self.config.get('classification_method', 'quantity')
        }
    
    def generate_optimization_suggestions(self, abc_results: pd.DataFrame, 
                                        summary_stats: Dict[str, Any]) -> List[str]:
        """
        生成优化建议
        
        Args:
            abc_results: ABC分析结果
            summary_stats: 统计摘要
            
        Returns:
            list: 优化建议列表
        """
        suggestions = []
        
        if abc_results.empty:
            suggestions.append("💡 数据为空，无法生成优化建议")
            return suggestions
        
        # A类建议
        if summary_stats['a_percentage'] > 90:
            suggestions.append("⚠️ A类物品价值占比过高(>90%)，建议检查分类标准")
        elif summary_stats['a_percentage'] < 70:
            suggestions.append("💡 A类物品价值占比较低(<70%)，建议重新评估重要物品")
        else:
            suggestions.append("✅ A类物品价值占比合理，应重点管理和监控")
        
        # B类建议
        if summary_stats['b_percentage'] > 25:
            suggestions.append("💡 B类物品价值占比较高，可考虑部分升级为A类管理")
        else:
            suggestions.append("✅ B类物品需要适度关注，定期审查管理策略")
        
        # C类建议
        if summary_stats['c_percentage'] > 15:
            suggestions.append("⚠️ C类物品价值占比过高，建议简化管理流程")
        else:
            suggestions.append("✅ C类物品可采用简化管理，降低管理成本")
        
        # 物品数量分布建议
        if summary_stats['a_item_percentage'] > 30:
            suggestions.append("💡 A类物品数量占比较高，建议优化分类阈值")
        
        if summary_stats['c_item_percentage'] < 50:
            suggestions.append("💡 C类物品数量占比较低，可考虑放宽C类标准")
        
        return suggestions
    
    def analyze_batch(self, df: pd.DataFrame, sku_column: str, 
                     quantity_column: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        批量执行ABC分析
        
        Args:
            df: 数据框
            sku_column: SKU列名
            quantity_column: 数量列名
            
        Returns:
            tuple: (ABC分析结果, 统计摘要)
        """
        # 数据验证
        is_valid, errors = self.validate_data(df, sku_column, quantity_column)
        if not is_valid:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
        
        # 执行ABC分类
        abc_results = self.calculate_abc_classification(df, sku_column, quantity_column)
        
        # 生成统计摘要
        summary_stats = self.generate_summary_statistics(abc_results)
        
        return abc_results, summary_stats 