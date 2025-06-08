# -*- coding: utf-8 -*-
"""
分析引擎核心模块 - 包含所有分析维度的执行逻辑
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional
from core.packing_analysis import PackingAnalyzer
from core.data_cleaning import DataCleaning
from utils import DataUtils, SessionStateManager, ValidationUtils, ProgressUtils
from config import ANALYSIS_DIMENSIONS, PREPROCESSING_DIMENSIONS

class AnalysisEngine:
    """分析引擎核心类"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化分析引擎
        
        Args:
            df: 要分析的数据框
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.analysis_results = {}
        self.data_cleaning = DataCleaning(df)
        
    def execute_preprocessing_step(self, step: str, config: Dict[str, Any]) -> bool:
        """
        执行单个前置处理步骤
        
        Args:
            step: 前置处理步骤名称
            config: 配置参数
            
        Returns:
            bool: 是否执行成功
        """
        try:
            if step == "异常数据清洗":
                return self._execute_data_cleaning_with_config(config)
            elif step == "容器选择":
                return self._execute_container_selection()
            else:
                st.warning(f"未知的前置处理步骤: {step}")
                return False
        except Exception as e:
            st.error(f"{step}执行失败: {str(e)}")
            return False
    
    def execute_analysis_dimension(self, dimension: str, config: Dict[str, Any]) -> bool:
        """
        执行分析维度
        
        Args:
            dimension: 分析维度名称
            config: 配置参数
            
        Returns:
            bool: 是否执行成功
        """
        try:
            if dimension == "装箱分析":
                return self._execute_packing_analysis(config)
            elif dimension == "ABC分析":
                return self._execute_abc_analysis(config)
            elif dimension == "容器对比分析":
                return self._execute_container_comparison(config)
            elif dimension == "SKU件数分析":
                return self._execute_sku_quantity_analysis(config)
            elif dimension == "入库箱数分析":
                return self._execute_inbound_box_analysis(config)
            elif dimension == "订单结构分析":
                return self._execute_order_structure_analysis(config)
            elif dimension == "单件多件分析":
                return self._execute_single_multi_analysis(config)
            elif dimension == "命中率分析":
                return self._execute_hit_rate_analysis(config)
            else:
                st.warning(f"未知的分析维度: {dimension}")
                return False
                
        except Exception as e:
            st.error(f"{dimension}执行失败: {str(e)}")
            return False
    
    def _execute_data_cleaning_with_config(self, config: Dict[str, Any]) -> bool:
        """根据配置执行高级异常数据清洗"""
        all_conditions = config.get('all_conditions', [])
        overall_logic = config.get('overall_logic', 'OR')
        action = config.get('action', '删除')
        
        if not all_conditions or not any(all_conditions):
            st.error("❌ 未配置任何清洗条件")
            return False
        
        st.write("🧹 **正在执行高级异常数据清洗...**")
        st.write(f"📋 条件组数: {len(all_conditions)}")
        st.write(f"🔗 组间逻辑: {overall_logic}")
        
        with st.spinner("清洗数据中..."):
            try:
                import pandas as pd
                import numpy as np
                
                result_df = self.df.copy()
                group_results = []
                
                # 处理每个条件组
                for group_id, group_conditions in enumerate(all_conditions, 1):
                    if not group_conditions:
                        continue
                        
                    group_mask = pd.Series([True] * len(self.df), index=self.df.index)
                    
                    # 处理组内的每个条件（AND关系）
                    for condition in group_conditions:
                        columns = condition.get('columns', [])
                        operator = condition.get('operator', '')
                        value = condition.get('value', '')
                        
                        if not columns:
                            continue
                        
                        condition_mask = pd.Series([False] * len(self.df), index=self.df.index)
                        
                        # 对每个选择的列应用条件
                        for column in columns:
                            if column not in self.df.columns:
                                continue
                            
                            col_data = self.df[column]
                            
                            # 根据运算符执行判断
                            if operator == ">":
                                mask = pd.to_numeric(col_data, errors='coerce') > float(value)
                            elif operator == ">=":
                                mask = pd.to_numeric(col_data, errors='coerce') >= float(value)
                            elif operator == "<":
                                mask = pd.to_numeric(col_data, errors='coerce') < float(value)
                            elif operator == "<=":
                                mask = pd.to_numeric(col_data, errors='coerce') <= float(value)
                            elif operator == "==":
                                if isinstance(value, (int, float)):
                                    mask = pd.to_numeric(col_data, errors='coerce') == float(value)
                                else:
                                    mask = col_data.astype(str) == str(value)
                            elif operator == "!=":
                                if isinstance(value, (int, float)):
                                    mask = pd.to_numeric(col_data, errors='coerce') != float(value)
                                else:
                                    mask = col_data.astype(str) != str(value)
                            elif operator == "in_range":
                                if isinstance(value, list) and len(value) == 2:
                                    numeric_data = pd.to_numeric(col_data, errors='coerce')
                                    mask = (numeric_data >= float(value[0])) & (numeric_data <= float(value[1]))
                                else:
                                    mask = pd.Series([False] * len(self.df), index=self.df.index)
                            elif operator == "not_in_range":
                                if isinstance(value, list) and len(value) == 2:
                                    numeric_data = pd.to_numeric(col_data, errors='coerce')
                                    mask = (numeric_data < float(value[0])) | (numeric_data > float(value[1]))
                                else:
                                    mask = pd.Series([False] * len(self.df), index=self.df.index)
                            elif operator == "contains":
                                mask = col_data.astype(str).str.contains(str(value), na=False)
                            elif operator == "not_contains":
                                mask = ~col_data.astype(str).str.contains(str(value), na=False)
                            else:
                                mask = pd.Series([False] * len(self.df), index=self.df.index)
                            
                            mask = mask.fillna(False)
                            condition_mask = condition_mask | mask
                        
                        # 组内条件使用AND关系
                        group_mask = group_mask & condition_mask
                    
                    group_results.append(group_mask)
                
                # 组合所有条件组的结果
                if group_results:
                    final_mask = group_results[0]
                    
                    for i in range(1, len(group_results)):
                        if overall_logic == "OR":
                            final_mask = final_mask | group_results[i]
                        else:  # AND
                            final_mask = final_mask & group_results[i]
                else:
                    final_mask = pd.Series([False] * len(self.df), index=self.df.index)
                
                abnormal_data = self.df[final_mask].copy()
                abnormal_count = final_mask.sum()
                
                # 显示检测结果
                if abnormal_count == 0:
                    st.info("✨ 未检测到符合条件的异常数据")
                    return True
                
                st.write(f"🚨 检测到 {abnormal_count} 条异常数据")
                
                # 显示异常数据预览
                if abnormal_count > 0:
                    st.write("**异常数据预览：**")
                    preview_data = abnormal_data.head(10)
                    st.dataframe(preview_data, use_container_width=True)
                
                # 执行处理
                if action == "删除":
                    result_df = self.df[~final_mask].copy()
                    self.df = result_df
                    action_text = "删除"
                elif action == "标记异常":
                    self.df['异常标记'] = final_mask
                    result_df = self.df.copy()
                    action_text = "标记"
                else:  # 导出到新文件
                    result_df = self.df.copy()
                    action_text = "导出"
                    # 这里可以添加导出异常数据的功能
                
                # 保存清洗结果
                self.analysis_results["异常数据清洗"] = {
                    "original_count": len(self.original_df),
                    "cleaned_count": len(result_df),
                    "abnormal_count": abnormal_count,
                    "abnormal_data": abnormal_data,
                    "conditions": all_conditions,
                    "overall_logic": overall_logic,
                    "action": action_text
                }
                
                # 显示清洗结果
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("原始数据", f"{len(self.original_df):,}")
                with col2:
                    st.metric("处理后数据", f"{len(result_df):,}")
                with col3:
                    st.metric("异常数据", f"{abnormal_count:,}")
                with col4:
                    st.metric("处理方式", action_text)
                
                st.success(f"✅ 高级异常数据清洗完成！{action_text}了 {abnormal_count} 条异常数据")
                return True
                
            except Exception as e:
                st.error(f"❌ 高级清洗执行失败: {str(e)}")
                return False
    
    def _execute_container_selection(self):
        """执行容器选择"""
        # 容器信息已在UI组件中处理并保存到session_state
        container_info = {
            'length': st.session_state.get("container_length", 600),
            'width': st.session_state.get("container_width", 400),
            'height': st.session_state.get("container_height", 300)
        }
        
        self.analysis_results["容器选择"] = container_info
        st.success(f"✅ 容器标准化完成！选定规格: {container_info['length']}×{container_info['width']}×{container_info['height']} mm")
        return True
    
    def _execute_packing_analysis(self, config: Dict[str, Any]) -> bool:
        """执行装箱分析"""
        st.write("📦 **正在执行装箱分析...**")
        
        # 验证必需的列是否存在
        required_columns = [
            config['length_column'], 
            config['width_column'], 
            config['height_column'], 
            config['inventory_column']
        ]
        
        exists, missing = DataUtils.validate_columns_existence(self.df, required_columns)
        if not exists:
            st.error(f"缺少必需的列: {missing}")
            return False
        
        # 创建容器信息
        container_info = {
            'length': config['container_length'],
            'width': config['container_width'], 
            'height': config['container_height'],
            'size': f"{config['container_length']}x{config['container_width']}x{config['container_height']}",
            'volume': config['container_length'] * config['container_width'] * config['container_height']
        }
        
        # 创建装箱分析器
        analyzer = PackingAnalyzer(container_info)
        
        # 数据预处理 - 计算总库存
        inventory_data = pd.to_numeric(self.df[config['inventory_column']], errors='coerce')
        total_inventory = int(inventory_data.sum()) if not inventory_data.isna().all() else 0
        
        with st.spinner("分析装箱数据中..."):
            # 执行装箱分析
            packing_results, processed_count = analyzer.analyze_batch(
                self.df,
                config['length_column'],
                config['width_column'], 
                config['height_column'],
                config['inventory_column'],
                config['data_unit']
            )
            
            # 生成统计摘要
            summary_stats = analyzer.generate_summary_statistics(packing_results, total_inventory)
            
            # 保存分析结果
            self.analysis_results["装箱分析"] = {
                "packing_results": packing_results,
                "summary_stats": summary_stats,
                "container_info": container_info,
                "config": config,
                "processed_count": processed_count
            }
        
        # 显示结果（委托给UI组件）
        from components.ui_components import UIComponents
        UIComponents.render_packing_analysis_results(
            analyzer, packing_results, summary_stats, config['data_unit']
        )
        
        st.success("✅ 装箱分析完成！")
        return True
    
    def _execute_abc_analysis(self, config: Dict[str, Any]) -> bool:
        """执行ABC分析"""
        st.write("📊 **正在执行ABC分析...**")
        
        # ABC分析的实现逻辑
        # 这里可以根据需要实现具体的ABC分析算法
        
        st.info("📊 ABC分析功能待完善...")
        return True
    
    def _execute_container_comparison(self, config: Dict[str, Any]) -> bool:
        """执行容器对比分析"""
        st.write("🔍 **正在执行容器对比分析...**")
        
        # 容器对比分析的实现逻辑
        # 这里可以根据需要实现容器对比算法
        
        st.info("🔍 容器对比分析功能待完善...")
        return True
    
    def _execute_sku_quantity_analysis(self, config: Dict[str, Any]) -> bool:
        """执行SKU件数分析"""
        st.write("🔢 **正在执行SKU件数分析...**")
        
        # SKU件数分析的实现逻辑
        
        st.info("🔢 SKU件数分析功能待完善...")
        return True
    
    def _execute_inbound_box_analysis(self, config: Dict[str, Any]) -> bool:
        """执行入库箱数分析"""
        st.write("📥 **正在执行入库箱数分析...**")
        
        # 入库箱数分析的实现逻辑
        
        st.info("📥 入库箱数分析功能待完善...")
        return True
    
    def _execute_order_structure_analysis(self, config: Dict[str, Any]) -> bool:
        """执行订单结构分析"""
        st.write("📋 **正在执行订单结构分析...**")
        
        # 订单结构分析的实现逻辑
        
        st.info("📋 订单结构分析功能待完善...")
        return True
    
    def _execute_single_multi_analysis(self, config: Dict[str, Any]) -> bool:
        """执行单件多件分析"""
        st.write("🔀 **正在执行单件多件分析...**")
        
        # 单件多件分析的实现逻辑
        
        st.info("🔀 单件多件分析功能待完善...")
        return True
    
    def _execute_hit_rate_analysis(self, config: Dict[str, Any]) -> bool:
        """执行命中率分析"""
        st.write("🎯 **正在执行命中率分析...**")
        
        # 命中率分析的实现逻辑
        
        st.info("🎯 命中率分析功能待完善...")
        return True
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        获取分析摘要
        
        Returns:
            dict: 分析摘要信息
        """
        summary = {
            "total_dimensions": len(self.analysis_results),
            "data_info": {
                "original_rows": len(self.original_df),
                "current_rows": len(self.df),
                "columns": len(self.df.columns)
            },
            "executed_steps": list(self.analysis_results.keys())
        }
        
        return summary
    
    def export_all_results(self) -> Dict[str, pd.DataFrame]:
        """
        导出所有分析结果
        
        Returns:
            dict: 包含各个分析结果的字典
        """
        export_data = {}
        
        for dimension, results in self.analysis_results.items():
            if dimension == "装箱分析":
                # 装箱分析结果
                packing_results = results["packing_results"]
                summary_stats = results["summary_stats"]
                
                # 基础结果
                basic_data = []
                for result in packing_results:
                    basic_data.append({
                        'SKU行号': result['SKU_index'] + 1,
                        '货物长度(mm)': result['goods_length_mm'],
                        '货物宽度(mm)': result['goods_width_mm'],
                        '货物高度(mm)': result['goods_height_mm'],
                        '库存件数': result['inventory_qty'],
                        '最大装箱数': result['max_per_box'],
                        '需要箱数': result['boxes_needed'] if result['boxes_needed'] != float('inf') else '装不下'
                    })
                
                export_data[f"{dimension}_基础结果"] = pd.DataFrame(basic_data)
                
                # 统计摘要
                summary_data = {
                    "统计项目": ["总SKU数", "可装箱SKU", "装不下SKU", "总库存件数", "总需箱子数", "装箱成功率"],
                    "统计结果": [
                        f"{summary_stats['total_sku_count']:,}",
                        f"{summary_stats['can_pack_items']:,}", 
                        f"{summary_stats['cannot_pack_items']:,}",
                        f"{summary_stats['total_inventory']:,}",
                        f"{summary_stats['total_boxes_needed']:.0f}",
                        f"{summary_stats['success_rate']:.1f}%"
                    ]
                }
                export_data[f"{dimension}_统计摘要"] = pd.DataFrame(summary_data)
                
            elif dimension == "数据清洗":
                # 数据清洗结果
                cleaning_stats = results["stats"]
                cleaning_data = {
                    "清洗项目": ["原始数据量", "清洗后数据量", "移除异常数据", "清洗率"],
                    "统计结果": [
                        f"{results['original_count']:,}",
                        f"{results['cleaned_count']:,}",
                        f"{results['removed_count']:,}",
                        f"{results['cleaning_rate'] * 100:.1f}%"
                    ]
                }
                export_data[f"{dimension}_统计"] = pd.DataFrame(cleaning_data)
                
        return export_data

class DimensionConfigManager:
    """分析维度配置管理器"""
    
    @staticmethod
    def get_config_requirements(dimension: str) -> List[str]:
        """
        获取分析维度的配置要求
        
        Args:
            dimension: 分析维度名称
            
        Returns:
            list: 配置要求列表
        """
        requirements = {
            "装箱分析": ["length_column", "width_column", "height_column", "inventory_column", "data_unit"],
            "ABC分析": ["value_column", "quantity_column"],
            "容器对比分析": ["length_column", "width_column", "height_column"],
            "SKU件数分析": ["sku_column", "quantity_column"],
            "入库箱数分析": ["date_column", "box_column"],
            "订单结构分析": ["order_column", "item_column"],
            "单件多件分析": ["order_column", "quantity_column"],
            "命中率分析": ["target_column", "actual_column"]
        }
        
        return requirements.get(dimension, [])
    
    @staticmethod
    def validate_config(dimension: str, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证分析维度配置
        
        Args:
            dimension: 分析维度名称
            config: 配置字典
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        requirements = DimensionConfigManager.get_config_requirements(dimension)
        
        for req in requirements:
            if req not in config or config[req] is None:
                errors.append(f"缺少必需配置: {req}")
            elif isinstance(config[req], str) and not config[req].strip():
                errors.append(f"配置不能为空: {req}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_default_config(dimension: str) -> Dict[str, Any]:
        """
        获取分析维度的默认配置
        
        Args:
            dimension: 分析维度名称
            
        Returns:
            dict: 默认配置
        """
        defaults = {
            "装箱分析": {
                "data_unit": "cm",
                "show_details": True,
                "container_length": 600,
                "container_width": 400,
                "container_height": 300
            },
            "ABC分析": {
                "classification_method": "revenue",
                "a_percentage": 20,
                "b_percentage": 30
            },
            "容器对比分析": {
                "compare_containers": ["600x400x300", "650x450x350", "700x500x400"]
            }
        }
        
        return defaults.get(dimension, {}) 