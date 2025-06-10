# -*- coding: utf-8 -*-
"""
EIQ分析模块 - 专门处理EIQ分析相关功能
EIQ (Entry, Item, Quantity) 分析出入库订单结构和特征
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional
from config import ANALYSIS_DIMENSIONS

class EIQAnalyzer:
    """EIQ分析器"""
    
    def __init__(self, analysis_config: Optional[Dict[str, Any]] = None):
        """
        初始化EIQ分析器
        
        Args:
            analysis_config: 分析配置字典
        """
        self.config = analysis_config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'analysis_period': 'monthly',  # daily, weekly, monthly, quarterly
            'entry_threshold': 10,  # 订单数量阈值
            'item_threshold': 5,   # 单品数量阈值  
            'quantity_threshold': 100,  # 数量阈值
            'include_charts': True,  # 是否生成图表
            'group_small_entries': True  # 是否合并小订单
        }
    
    def validate_data(self, df: pd.DataFrame, entry_column: str, 
                     item_column: str, quantity_column: str, 
                     date_column: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        验证数据有效性
        
        Args:
            df: 数据框
            entry_column: 订单列名（Entry）
            item_column: 商品列名（Item）
            quantity_column: 数量列名（Quantity）
            date_column: 日期列名（可选）
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查数据框是否为空
        if df.empty:
            errors.append("数据框为空")
            return False, errors
        
        # 检查必需列是否存在
        required_columns = [entry_column, item_column, quantity_column]
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"必需列 '{col}' 不存在")
        
        if date_column and date_column not in df.columns:
            errors.append(f"日期列 '{date_column}' 不存在")
        
        # 检查数据类型
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
        
        # 检查日期列
        if date_column and date_column in df.columns:
            try:
                pd.to_datetime(df[date_column], errors='coerce')
            except Exception as e:
                errors.append(f"日期列数据验证失败: {str(e)}")
        
        return len(errors) == 0, errors
    
    def analyze_entry_patterns(self, df: pd.DataFrame, entry_column: str, 
                              item_column: str, quantity_column: str) -> Dict[str, Any]:
        """
        分析Entry（订单）模式
        
        Args:
            df: 数据框
            entry_column: 订单列名
            item_column: 商品列名  
            quantity_column: 数量列名
            
        Returns:
            dict: Entry分析结果
        """
        # 按订单分组统计
        entry_stats = df.groupby(entry_column).agg({
            item_column: 'nunique',  # 不同商品数量
            quantity_column: ['sum', 'mean', 'count']  # 总数量、平均数量、行数
        }).round(2)
        
        # 重命名列
        entry_stats.columns = ['商品种类数', '总数量', '平均数量', '行数']
        entry_stats['订单编号'] = entry_stats.index
        
        # 计算订单特征
        entry_stats['订单规模'] = pd.cut(entry_stats['商品种类数'], 
                                      bins=[0, 1, 5, 10, float('inf')], 
                                      labels=['单品订单', '小订单', '中订单', '大订单'])
        
        entry_stats['数量规模'] = pd.cut(entry_stats['总数量'], 
                                      bins=[0, 10, 50, 200, float('inf')], 
                                      labels=['小量', '中量', '大量', '超大量'])
        
        # 订单分布统计
        order_distribution = {
            'total_entries': len(entry_stats),
            'single_item_orders': len(entry_stats[entry_stats['商品种类数'] == 1]),
            'multi_item_orders': len(entry_stats[entry_stats['商品种类数'] > 1]),
            'avg_items_per_order': entry_stats['商品种类数'].mean(),
            'avg_quantity_per_order': entry_stats['总数量'].mean(),
            'max_items_per_order': entry_stats['商品种类数'].max(),
            'max_quantity_per_order': entry_stats['总数量'].max()
        }
        
        return {
            'entry_details': entry_stats.reset_index(drop=True),
            'entry_distribution': order_distribution
        }
    
    def analyze_item_patterns(self, df: pd.DataFrame, entry_column: str, 
                             item_column: str, quantity_column: str) -> Dict[str, Any]:
        """
        分析Item（商品）模式
        
        Args:
            df: 数据框
            entry_column: 订单列名
            item_column: 商品列名
            quantity_column: 数量列名
            
        Returns:
            dict: Item分析结果
        """
        # 按商品分组统计
        item_stats = df.groupby(item_column).agg({
            entry_column: 'nunique',  # 出现在多少个订单中
            quantity_column: ['sum', 'mean', 'count']  # 总数量、平均数量、出现次数
        }).round(2)
        
        # 重命名列
        item_stats.columns = ['订单频次', '总需求量', '平均需求量', '出现次数']
        item_stats['商品编号'] = item_stats.index
        
        # 计算商品特征
        item_stats['需求频率'] = pd.cut(item_stats['订单频次'], 
                                     bins=[0, 1, 5, 20, float('inf')], 
                                     labels=['低频', '中低频', '中高频', '高频'])
        
        item_stats['需求量级'] = pd.cut(item_stats['总需求量'], 
                                     bins=[0, 10, 100, 500, float('inf')], 
                                     labels=['小量', '中量', '大量', '超大量'])
        
        # 商品分布统计  
        item_distribution = {
            'total_items': len(item_stats),
            'high_frequency_items': len(item_stats[item_stats['订单频次'] >= 10]),
            'low_frequency_items': len(item_stats[item_stats['订单频次'] == 1]),
            'avg_orders_per_item': item_stats['订单频次'].mean(),
            'avg_quantity_per_item': item_stats['总需求量'].mean(),
            'top_items_quantity': item_stats['总需求量'].nlargest(10).sum()
        }
        
        return {
            'item_details': item_stats.reset_index(drop=True),
            'item_distribution': item_distribution
        }
    
    def analyze_quantity_patterns(self, df: pd.DataFrame, entry_column: str, 
                                 item_column: str, quantity_column: str) -> Dict[str, Any]:
        """
        分析Quantity（数量）模式
        
        Args:
            df: 数据框
            entry_column: 订单列名
            item_column: 商品列名
            quantity_column: 数量列名
            
        Returns:
            dict: Quantity分析结果
        """
        # 数量统计
        quantities = pd.to_numeric(df[quantity_column], errors='coerce').dropna()
        
        quantity_stats = {
            'total_quantity': quantities.sum(),
            'avg_quantity': quantities.mean(),
            'median_quantity': quantities.median(),
            'std_quantity': quantities.std(),
            'min_quantity': quantities.min(),
            'max_quantity': quantities.max(),
            'quantity_records': len(quantities)
        }
        
        # 数量分布
        quantity_distribution = pd.cut(quantities, 
                                     bins=[0, 1, 5, 10, 50, float('inf')], 
                                     labels=['1件', '2-5件', '6-10件', '11-50件', '50件以上'])
        
        quantity_dist_counts = quantity_distribution.value_counts().to_dict()
        
        # 按订单和商品的数量分析
        entry_item_qty = df.groupby([entry_column, item_column])[quantity_column].sum().reset_index()
        entry_item_qty['数量类别'] = pd.cut(pd.to_numeric(entry_item_qty[quantity_column], errors='coerce'), 
                                        bins=[0, 1, 5, 20, float('inf')], 
                                        labels=['单件', '少量', '中量', '大量'])
        
        return {
            'quantity_statistics': quantity_stats,
            'quantity_distribution': quantity_dist_counts,
            'entry_item_quantities': entry_item_qty
        }
    
    def generate_eiq_summary(self, entry_analysis: Dict[str, Any], 
                           item_analysis: Dict[str, Any], 
                           quantity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成EIQ综合分析摘要
        
        Args:
            entry_analysis: Entry分析结果
            item_analysis: Item分析结果  
            quantity_analysis: Quantity分析结果
            
        Returns:
            dict: EIQ综合摘要
        """
        entry_dist = entry_analysis['entry_distribution']
        item_dist = item_analysis['item_distribution']
        qty_stats = quantity_analysis['quantity_statistics']
        
        # 计算关键指标
        single_item_ratio = (entry_dist['single_item_orders'] / entry_dist['total_entries'] * 100) if entry_dist['total_entries'] > 0 else 0
        high_freq_item_ratio = (item_dist['high_frequency_items'] / item_dist['total_items'] * 100) if item_dist['total_items'] > 0 else 0
        
        summary = {
            # Entry维度摘要
            'entry_summary': {
                'total_orders': entry_dist['total_entries'],
                'single_item_order_ratio': single_item_ratio,
                'avg_items_per_order': entry_dist['avg_items_per_order'],
                'avg_quantity_per_order': entry_dist['avg_quantity_per_order']
            },
            
            # Item维度摘要
            'item_summary': {
                'total_items': item_dist['total_items'],
                'high_frequency_item_ratio': high_freq_item_ratio,
                'avg_orders_per_item': item_dist['avg_orders_per_item'],
                'item_concentration': (item_dist['top_items_quantity'] / qty_stats['total_quantity'] * 100) if qty_stats['total_quantity'] > 0 else 0
            },
            
            # Quantity维度摘要
            'quantity_summary': {
                'total_quantity': qty_stats['total_quantity'],
                'avg_quantity_per_record': qty_stats['avg_quantity'],
                'quantity_variability': qty_stats['std_quantity'] / qty_stats['avg_quantity'] if qty_stats['avg_quantity'] > 0 else 0,
                'max_single_quantity': qty_stats['max_quantity']
            }
        }
        
        return summary
    
    def generate_optimization_suggestions(self, eiq_summary: Dict[str, Any]) -> List[str]:
        """
        生成EIQ优化建议
        
        Args:
            eiq_summary: EIQ分析摘要
            
        Returns:
            list: 优化建议列表
        """
        suggestions = []
        
        entry_summary = eiq_summary['entry_summary']
        item_summary = eiq_summary['item_summary']
        quantity_summary = eiq_summary['quantity_summary']
        
        # Entry（订单）维度建议
        if entry_summary['single_item_order_ratio'] > 70:
            suggestions.append("📦 单品订单占比较高(>70%)，建议优化拣货流程，采用单品拣货策略")
        elif entry_summary['single_item_order_ratio'] < 30:
            suggestions.append("📦 多品订单较多，建议采用批量拣货和分拣策略")
        
        if entry_summary['avg_items_per_order'] > 10:
            suggestions.append("🎯 订单平均品种数较多，建议优化存储布局，将常用商品集中放置")
        
        # Item（商品）维度建议
        if item_summary['high_frequency_item_ratio'] < 20:
            suggestions.append("🔥 高频商品占比较低，建议识别核心商品并优化其存储位置")
        
        if item_summary['item_concentration'] > 80:
            suggestions.append("⚡ 商品需求集中度高，建议对热门商品实施重点管理")
        elif item_summary['item_concentration'] < 50:
            suggestions.append("📊 商品需求较为分散，建议采用ABC分析进一步细化管理")
        
        # Quantity（数量）维度建议
        if quantity_summary['quantity_variability'] > 2:
            suggestions.append("📈 数量变异性较大，建议优化库存策略，增强需求预测")
        
        if quantity_summary['avg_quantity_per_record'] < 2:
            suggestions.append("🔢 平均单次需求量较小，建议考虑小包装策略")
        elif quantity_summary['avg_quantity_per_record'] > 20:
            suggestions.append("📦 平均单次需求量较大，建议优化包装和运输方式")
        
        return suggestions
    
    def analyze_batch(self, df: pd.DataFrame, entry_column: str, 
                     item_column: str, quantity_column: str, 
                     date_column: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        批量执行EIQ分析
        
        Args:
            df: 数据框
            entry_column: 订单列名
            item_column: 商品列名
            quantity_column: 数量列名
            date_column: 日期列名（可选）
            
        Returns:
            tuple: (EIQ分析结果, 综合摘要)
        """
        # 数据验证
        is_valid, errors = self.validate_data(df, entry_column, item_column, quantity_column, date_column)
        if not is_valid:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
        
        # 执行各维度分析
        entry_analysis = self.analyze_entry_patterns(df, entry_column, item_column, quantity_column)
        item_analysis = self.analyze_item_patterns(df, entry_column, item_column, quantity_column)
        quantity_analysis = self.analyze_quantity_patterns(df, entry_column, item_column, quantity_column)
        
        # 生成综合摘要
        eiq_summary = self.generate_eiq_summary(entry_analysis, item_analysis, quantity_analysis)
        
        # 组合完整结果
        eiq_results = {
            'entry_analysis': entry_analysis,
            'item_analysis': item_analysis, 
            'quantity_analysis': quantity_analysis,
            'eiq_summary': eiq_summary
        }
        
        return eiq_results, eiq_summary 