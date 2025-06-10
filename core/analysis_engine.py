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
from core.abc_analysis import ABCAnalyzer
from core.eiq_analysis import EIQAnalyzer
from core.outbound_analysis import OutboundAnalyzer
from core.inbound_analysis import InboundAnalyzer
from utils import DataUtils, SessionStateManager, ValidationUtils, ProgressUtils
from config import ANALYSIS_DIMENSIONS, PREPROCESSING_DIMENSIONS, ABC_CONFIG, EIQ_CONFIG

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
            elif dimension == "出库分析":
                return self._execute_outbound_analysis(config)
            elif dimension == "入库分析":
                return self._execute_inbound_analysis(config)
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
                    self._render_abnormal_data_preview(abnormal_data)
                
                # 直接删除异常数据
                result_df = self.df[~final_mask].copy()
                self.df = result_df
                action_text = "删除"
                
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
    
    def _render_abnormal_data_preview(self, abnormal_data):
        """渲染异常数据预览，支持完整查看和下载"""
        abnormal_count = len(abnormal_data)
        
        # 新逻辑：如果数据量<=100条，默认显示全部；>100条时显示预览
        if abnormal_count <= 100:
            # 数据量不大，默认展开显示全部
            st.success(f"✅ **显示全部 {abnormal_count} 条异常数据**")
            st.dataframe(abnormal_data, use_container_width=True)
        else:
            # 数据量较大（>100条），只显示预览
            st.info(f"🔍 **检测到 {abnormal_count} 条异常数据**")
            st.caption(f"数据量较大，显示前10条预览，完整数据请通过下载Excel获取")
            
            st.write(f"📋 **异常数据预览**（前10条，共 {abnormal_count} 条）:")
            preview_data = abnormal_data.head(10)
            st.dataframe(preview_data, use_container_width=True)
            st.warning(f"💡 数据量较大（{abnormal_count} 条），完整数据请点击下方Excel下载按钮获取")
        
        # 添加Excel下载按钮
        col1, col2 = st.columns([6, 2])
        with col2:
            # Excel下载
            from io import BytesIO
            excel_buffer = BytesIO()
            
            try:
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    abnormal_data.to_excel(writer, sheet_name='异常数据', index=False)
                
                excel_buffer.seek(0)
                
                st.download_button(
                    label=f"📊 下载Excel ({abnormal_count}条)",
                    data=excel_buffer.getvalue(),
                    file_name=f"异常数据_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="下载为Excel格式，支持数据分析",
                    use_container_width=True
                )
            except Exception as e:
                st.info("📊 Excel格式暂不可用")
    
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
        
        # 检查重量列（可选）
        weight_column = config.get('weight_column')
        if weight_column:
            required_columns.append(weight_column)
        
        exists, missing = DataUtils.validate_columns_existence(self.df, required_columns)
        if not exists:
            st.error(f"缺少必需的列: {missing}")
            return False
        
        # 创建容器信息
        container_info = {
            'length': config['container_length'],
            'width': config['container_width'], 
            'height': config['container_height'],
            'weight_limit': config.get('container_weight_limit', 30),
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
                config['data_unit'],
                config.get('weight_column'),
                config.get('weight_unit', 'kg')
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
        import matplotlib.pyplot as plt
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        st.write("📊 **正在执行ABC分析...**")
        
        try:
            # 获取配置参数
            sku_column = config.get('sku_column')
            quantity_column = config.get('quantity_column')
            a_percentage = config.get('a_percentage', 70)
            b_percentage = config.get('b_percentage', 20)
            
            if not sku_column or not quantity_column:
                st.error("❌ 请配置SKU列和数量列")
                return False
            
            # 创建ABC分析器
            abc_config = {
                'classification_method': 'quantity',
                'a_percentage': a_percentage,
                'b_percentage': b_percentage,
                'c_percentage': 100 - a_percentage - b_percentage,
                'sort_order': 'desc'
            }
            
            analyzer = ABCAnalyzer(abc_config)
            
            # 执行分析
            with st.spinner("正在执行ABC分析..."):
                abc_results, summary_stats = analyzer.analyze_batch(
                    self.df, sku_column, quantity_column
                )
            
            # 显示结果
            if not abc_results.empty:
                st.success("✅ ABC分析完成！")
                
                # 直接显示出库数量分布，删除顶部SKU统计摘要
                st.subheader("📊 出库数量分布")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("A类出库量", f"{summary_stats['a_quantity']:.0f}", delta=None)
                    st.caption(f"📦 **A类SKU**: {summary_stats['a_items']} 个 ({summary_stats['a_item_percentage']:.1f}%)")
                    st.caption(f"📊 **出库占比**: {summary_stats['a_percentage']:.1f}%")
                with col2:
                    st.metric("B类出库量", f"{summary_stats['b_quantity']:.0f}", delta=None)
                    st.caption(f"📦 **B类SKU**: {summary_stats['b_items']} 个 ({summary_stats['b_item_percentage']:.1f}%)")
                    st.caption(f"📊 **出库占比**: {summary_stats['b_percentage']:.1f}%")
                with col3:
                    st.metric("C类出库量", f"{summary_stats['c_quantity']:.0f}", delta=None)
                    st.caption(f"📦 **C类SKU**: {summary_stats['c_items']} 个 ({summary_stats['c_item_percentage']:.1f}%)")
                    st.caption(f"📊 **出库占比**: {summary_stats['c_percentage']:.1f}%")
                
                # A类品Top10
                st.subheader("🏆 A类品Top10")
                a_top10 = abc_results[abc_results['ABC分类'] == 'A'].head(10)
                if not a_top10.empty:
                    st.dataframe(a_top10, use_container_width=True)
                else:
                    st.info("没有A类品数据")
                
                # 隐藏分析过程表格，只在下载中提供
                # 过程表格已移至下载区域
                
                # 累计比例曲线图
                st.subheader("📈 ABC累计比例曲线图")
                self._render_abc_curve_chart(abc_results, a_percentage, a_percentage + b_percentage)
                
                # 数据导出按钮
                st.subheader("💾 数据导出")
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = abc_results.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📄 导出详细分析数据(CSV)",
                        data=csv_data,
                        file_name=f"ABC分析过程表格_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="包含完整的ABC分析过程表格数据"
                    )
                
                with col2:
                    # 创建摘要数据
                    summary_df = pd.DataFrame([
                        ['A类', summary_stats['a_items'], summary_stats['a_quantity'], summary_stats['a_percentage']],
                        ['B类', summary_stats['b_items'], summary_stats['b_quantity'], summary_stats['b_percentage']],
                        ['C类', summary_stats['c_items'], summary_stats['c_quantity'], summary_stats['c_percentage']]
                    ], columns=['分类', 'SKU数量', '出库数量', '数量占比(%)'])
                    
                    summary_csv = summary_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📊 导出摘要数据(CSV)",
                        data=summary_csv,
                        file_name=f"ABC分析摘要_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # 保存结果
                self.analysis_results["ABC分析"] = {
                    "abc_results": abc_results,
                    "summary_stats": summary_stats,
                    "suggestions": []
                }
                
                return True
            else:
                st.warning("⚠️ ABC分析未产生有效结果")
                return False
                
        except Exception as e:
            st.error(f"❌ ABC分析执行失败: {str(e)}")
            return False
    
    def _render_abc_curve_chart(self, abc_results: pd.DataFrame, a_threshold: float, b_threshold: float):
        """渲染ABC累计比例曲线图"""
        try:
            import plotly.graph_objects as go
            
            # 创建图表
            fig = go.Figure()
            
            # 计算累计比例数据
            x_data = list(range(1, len(abc_results) + 1))
            cumulative_ratio = abc_results['累计占比(%)'].tolist()
            
            # 计算各类别统计数据
            a_count = len(abc_results[abc_results['ABC分类'] == 'A'])
            b_count = len(abc_results[abc_results['ABC分类'] == 'B'])
            c_count = len(abc_results[abc_results['ABC分类'] == 'C'])
            total_sku_count = len(abc_results)  # 总SKU数量
            
            # 安全的数值转换，处理可能的NaN或非数值类型
            try:
                a_qty = float(abc_results[abc_results['ABC分类'] == 'A']['出库数量'].sum()) if a_count > 0 else 0.0
                b_qty = float(abc_results[abc_results['ABC分类'] == 'B']['出库数量'].sum()) if b_count > 0 else 0.0
                c_qty = float(abc_results[abc_results['ABC分类'] == 'C']['出库数量'].sum()) if c_count > 0 else 0.0
                total_qty = a_qty + b_qty + c_qty
                if total_qty == 0:
                    total_qty = 1  # 避免除零错误
            except (ValueError, TypeError):
                a_qty = b_qty = c_qty = total_qty = 0.0
            
            # 主累计曲线 - 带填充面积
            fig.add_trace(go.Scatter(
                x=x_data,
                y=cumulative_ratio,
                mode='lines',
                name='累计占比',
                line=dict(color='#00d4ff', width=3),
                fill='tonexty',
                fillcolor='rgba(0, 212, 255, 0.2)',
                hovertemplate='<b>排名:</b> %{x}<br><b>累计占比:</b> %{y:.2f}%<extra></extra>'
            ))
            
            # A类区域填充和标注
            a_mask = abc_results['ABC分类'] == 'A'
            if a_mask.any():
                a_data = abc_results[a_mask]
                a_x = list(range(1, len(a_data) + 1))
                a_y = a_data['累计占比(%)'].tolist()
                
                # A类区域填充
                fig.add_trace(go.Scatter(
                    x=a_x + [a_x[-1], a_x[0]],
                    y=a_y + [0, 0],
                    fill='toself',
                    fillcolor='rgba(255, 165, 0, 0.3)',
                    line=dict(color='orange', width=4),
                    name='A类',
                    mode='lines',
                    showlegend=True,
                    hovertemplate='<b>A类SKU排名:</b> %{x}<br><b>累计占比:</b> %{y:.2f}%<extra></extra>'
                ))
                
                # A类注释
                fig.add_annotation(
                    x=len(a_data)//2,
                    y=a_threshold//2,
                    text=f"<b>A类区域</b><br>SKU: {a_count}个<br>数量: {a_qty:.0f}<br>占比: {a_count/total_sku_count*100:.1f}%",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="orange",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="orange",
                    borderwidth=2,
                    font=dict(size=10, color="black")
                )
            
            # B类区域填充和标注
            b_mask = abc_results['ABC分类'] == 'B'
            if b_mask.any():
                b_start = a_count + 1
                b_end = a_count + b_count
                b_x = list(range(b_start, b_end + 1))
                b_data = abc_results[b_mask]
                b_y = b_data['累计占比(%)'].tolist()
                
                # B类区域填充
                fig.add_trace(go.Scatter(
                    x=b_x + [b_x[-1], b_x[0]],
                    y=b_y + [a_threshold, a_threshold],
                    fill='toself',
                    fillcolor='rgba(128, 128, 128, 0.3)',
                    line=dict(color='gray', width=4),
                    name='B类',
                    mode='lines',
                    showlegend=True,
                    hovertemplate='<b>B类SKU排名:</b> %{x}<br><b>累计占比:</b> %{y:.2f}%<extra></extra>'
                ))
                
                # B类注释
                fig.add_annotation(
                    x=b_start + b_count//2,
                    y=(a_threshold + b_threshold)//2,
                    text=f"<b>B类区域</b><br>SKU: {b_count}个<br>数量: {b_qty:.0f}<br>占比: {b_count/total_sku_count*100:.1f}%",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="gray",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="gray",
                    borderwidth=2,
                    font=dict(size=10, color="black")
                )
            
            # C类区域填充和标注
            c_mask = abc_results['ABC分类'] == 'C'
            if c_mask.any():
                c_start = a_count + b_count + 1
                c_x = list(range(c_start, len(abc_results) + 1))
                c_data = abc_results[c_mask]
                c_y = c_data['累计占比(%)'].tolist()
                
                # C类区域填充
                fig.add_trace(go.Scatter(
                    x=c_x + [c_x[-1], c_x[0]],
                    y=c_y + [b_threshold, b_threshold],
                    fill='toself',
                    fillcolor='rgba(255, 215, 0, 0.3)',
                    line=dict(color='gold', width=4),
                    name='C类',
                    mode='lines',
                    showlegend=True,
                    hovertemplate='<b>C类SKU排名:</b> %{x}<br><b>累计占比:</b> %{y:.2f}%<extra></extra>'
                ))
                
                # C类注释
                fig.add_annotation(
                    x=c_start + c_count//2,
                    y=(b_threshold + 100)//2,
                    text=f"<b>C类区域</b><br>SKU: {c_count}个<br>数量: {c_qty:.0f}<br>占比: {c_count/total_sku_count*100:.1f}%",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="gold",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="gold",
                    borderwidth=2,
                    font=dict(size=10, color="black")
                )
            
            # A类和B类阈值线
            fig.add_hline(
                y=a_threshold,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"A类阈值 ({a_threshold}%)",
                annotation_position="top right"
            )
            
            fig.add_hline(
                y=b_threshold,
                line_dash="dash", 
                line_color="gray",
                annotation_text=f"B类阈值 ({b_threshold}%)",
                annotation_position="top right"
            )
            
            # 图表样式 - 深色主题
            fig.update_layout(
                title=dict(
                    text="<b>ABC分析 - 出库数量累计占比曲线</b>",
                    x=0.5,
                    font=dict(size=18, color='white')
                ),
                xaxis=dict(
                    title="<b>SKU排名</b>",
                    title_font=dict(size=14, color='white'),
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title="<b>累计占比 (%)</b>",
                    title_font=dict(size=14, color='white'),
                    tickfont=dict(color='white'),
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='white')
                ),
                hovermode='x unified',
                plot_bgcolor='rgba(17, 17, 17, 0.8)',  # 深色背景
                paper_bgcolor='rgba(17, 17, 17, 0.8)',  # 纸张背景也设为深色
                font=dict(color='white'),  # 全局字体颜色
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"图表渲染失败: {str(e)}")
            # 降级到表格展示
            st.dataframe(abc_results[['排名', 'SKU', '累计占比(%)', 'ABC分类']], use_container_width=True)
    
    def _execute_outbound_analysis(self, config: Dict[str, Any]) -> bool:
        """执行出库通用分析"""
        try:
            st.subheader("📈 出库数据趋势分析")
            
            # 获取配置参数
            date_column = config.get("出库分析_date_column")
            
            # 新的配置格式：订单相关
            order_id_column = config.get("出库分析_order_id_column")
            order_count_column = config.get("出库分析_order_count_column")
            
            # 新的配置格式：SKU相关
            sku_column = config.get("出库分析_sku_column")
            sku_count_column = config.get("出库分析_sku_count_column")
            
            # 新的配置格式：件数相关
            item_column = config.get("出库分析_item_column")
            item_count_column = config.get("出库分析_item_count_column")
            
            # 日期范围
            start_date = config.get("出库分析_start_date")
            end_date = config.get("出库分析_end_date")
            
            # 处理"无数据"选项
            if order_id_column == "无数据":
                order_id_column = None
            if order_count_column == "无数据":
                order_count_column = None
            if sku_column == "无数据":
                sku_column = None
            if sku_count_column == "无数据":
                sku_count_column = None
            if item_column == "无数据":
                item_column = None
            if item_count_column == "无数据":
                item_count_column = None
                
            # 验证必需配置
            if not date_column:
                st.error("❌ 请选择日期列")
                return False
                
            # 创建分析器
            analyzer = OutboundAnalyzer(config)
            
            # 执行分析 - 使用新的参数格式
            daily_data, summary = analyzer.analyze_batch_enhanced(
                df=self.df,
                date_column=date_column,
                order_id_column=order_id_column,
                order_count_column=order_count_column,
                sku_column=sku_column,
                sku_count_column=sku_count_column,
                item_column=item_column,
                item_count_column=item_count_column,
                start_date=start_date,
                end_date=end_date
            )
            
            if daily_data.empty:
                st.warning("⚠️ 没有找到有效的出库数据")
                return False
            
            # 渲染趋势图表
            analyzer.render_trend_chart(daily_data, date_column, summary)
            
            # 显示统计摘要
            if summary:
                st.subheader("📊 统计摘要")
                date_info = summary.get('date_range', {})
                st.info(f"📅 分析时间范围：{date_info.get('start_date')} 至 {date_info.get('end_date')}，共 {date_info.get('total_days', 0)} 天")
                
                # 显示各维度统计
                for col, stats in summary.items():
                    if isinstance(stats, dict) and 'total' in stats:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"总{col.replace('日出', '')}", f"{stats['total']:,}")
                        with col2:
                            st.metric(f"日均{col.replace('日出', '')}", f"{stats['daily_avg']:.1f}")
                        with col3:
                            # 显示最高和最低信息（删除绿色箭头）
                            max_val = stats.get('daily_max', 0)
                            min_val = stats.get('daily_min', 0)
                            max_date = stats.get('max_date', '')
                            min_date = stats.get('min_date', '')
                            
                            # 格式化日期显示
                            max_date_str = max_date.strftime('%Y-%m-%d') if hasattr(max_date, 'strftime') else str(max_date)
                            min_date_str = min_date.strftime('%Y-%m-%d') if hasattr(min_date, 'strftime') else str(min_date)
                            
                            st.metric(
                                "最高/最低", 
                                f"{max_val:.0f} / {min_val:.0f}",
                                help=f"最高值: {max_val:.0f} ({max_date_str})\n最低值: {min_val:.0f} ({min_date_str})"
                            )
                
                # 添加EIQ分析比值（如果有足够的维度数据）
                self._add_eiq_ratios_to_summary(summary)
            
            # 提供数据下载
            st.subheader("📥 数据导出")
            csv_data = daily_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 导出出库趋势数据(CSV)",
                data=csv_data,
                file_name=f"出库趋势分析_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="下载完整的出库趋势分析数据"
            )
            
            # 保存分析结果供其他分析使用
            self.analysis_results["出库分析"] = {
                "daily_data": daily_data,
                "summary": summary,
                "suggestions": []  # 不再生成建议
            }
            
            return True
            
        except Exception as e:
            st.error(f"❌ 出库分析执行失败: {str(e)}")
            return False
    
    def _add_eiq_ratios_to_summary(self, summary: Dict[str, Any]) -> None:
        """将EIQ分析比值添加到出库分析统计摘要中"""
        try:
            # 分析可用的数据维度
            available_dimensions = []
            dimension_data = {}
            
            # 检查订单数据
            if "订单数/天" in summary:
                available_dimensions.append("订单")
                dimension_data["订单"] = summary["订单数/天"]
                
            # 检查SKU数据  
            if "SKU数/天" in summary:
                available_dimensions.append("SKU")
                dimension_data["SKU"] = summary["SKU数/天"]
                
            # 检查件数数据
            if "件数/天" in summary:
                available_dimensions.append("件数")
                dimension_data["件数"] = summary["件数/天"]
            
            if len(available_dimensions) < 2:
                return
            
            # 计算EIQ比值
            eiq_ratios = {}
            
            # 行单比 = SKU数/天 ÷ 订单数/天
            if "订单" in available_dimensions and "SKU" in available_dimensions:
                order_avg = float(dimension_data["订单"]["daily_avg_no_outliers"])
                sku_avg = float(dimension_data["SKU"]["daily_avg_no_outliers"])
                
                if order_avg > 0:
                    ratio = sku_avg / order_avg
                    eiq_ratios["行单比"] = {
                        "ratio": ratio,
                        "description": "平均每个订单包含的SKU数量",
                        "interpretation": self._interpret_ratio("行单比", ratio)
                    }
            
            # 件行比 = 件数/天 ÷ SKU数/天  
            if "件数" in available_dimensions and "SKU" in available_dimensions:
                item_avg = float(dimension_data["件数"]["daily_avg_no_outliers"])
                sku_avg = float(dimension_data["SKU"]["daily_avg_no_outliers"])
                
                if sku_avg > 0:
                    ratio = item_avg / sku_avg
                    eiq_ratios["件行比"] = {
                        "ratio": ratio,
                        "description": "平均每个SKU的出库件数",
                        "interpretation": self._interpret_ratio("件行比", ratio)
                    }
            
            # 件单比 = 件数/天 ÷ 订单数/天
            if "件数" in available_dimensions and "订单" in available_dimensions:
                item_avg = float(dimension_data["件数"]["daily_avg_no_outliers"])
                order_avg = float(dimension_data["订单"]["daily_avg_no_outliers"])
                
                if order_avg > 0:
                    ratio = item_avg / order_avg
                    eiq_ratios["件单比"] = {
                        "ratio": ratio,
                        "description": "平均每个订单的件数",
                        "interpretation": self._interpret_ratio("件单比", ratio)
                    }
            
            # 显示EIQ比值
            if eiq_ratios:
                st.markdown("---")
                st.subheader("📊 EIQ分析比值")
                
                # 使用列布局显示比值
                ratio_cols = st.columns(len(eiq_ratios))
                for i, (ratio_name, ratio_data) in enumerate(eiq_ratios.items()):
                    with ratio_cols[i]:
                        st.metric(
                            label=ratio_name,
                            value=f"{ratio_data['ratio']:.2f}",
                            help=f"{ratio_data['description']}\n{ratio_data['interpretation']}"
                        )
                        
        except Exception as e:
            st.warning(f"⚠️ EIQ比值计算失败: {str(e)}")
    
    def _interpret_ratio(self, ratio_type: str, ratio_value: float) -> str:
        """解释比值结果"""
        if ratio_type == "行单比":
            if ratio_value < 1.5:
                return "订单相对简单，多为单品或少品种订单"
            elif ratio_value < 3.0:
                return "订单复杂度适中，平均包含2-3个SKU"
            else:
                return "订单较为复杂，包含多个SKU品种"
                
        elif ratio_type == "件行比":
            if ratio_value < 2.0:
                return "SKU出库量较小，多为单件或少量出库"
            elif ratio_value < 5.0:
                return "SKU出库量适中，平均每个SKU出库2-5件"
            else:
                return "SKU出库量较大，存在批量出库情况"
                
        elif ratio_type == "件单比":
            if ratio_value < 3.0:
                return "订单件数较少，多为小批量订单"
            elif ratio_value < 10.0:
                return "订单件数适中，平均每单3-10件"
            else:
                return "订单件数较多，存在大批量订单"
        
        return f"比值为 {ratio_value:.2f}"
    
    def _execute_container_comparison(self, config: Dict[str, Any]) -> bool:
        """执行容器对比分析"""
        st.write("🔍 **正在执行容器对比分析...**")
        st.info("🔍 容器对比分析功能待完善...")
        return True
    
    def _execute_sku_quantity_analysis(self, config: Dict[str, Any]) -> bool:
        """执行SKU件数分析"""
        st.write("🔢 **正在执行SKU件数分析...**")
        st.info("🔢 SKU件数分析功能待完善...")
        return True
    
    def _execute_inbound_box_analysis(self, config: Dict[str, Any]) -> bool:
        """执行入库箱数分析"""
        st.write("📥 **正在执行入库箱数分析...**")
        st.info("📥 入库箱数分析功能待完善...")
        return True
    
    def _execute_order_structure_analysis(self, config: Dict[str, Any]) -> bool:
        """执行订单结构分析"""
        st.write("📋 **正在执行订单结构分析...**")
        st.info("📋 订单结构分析功能待完善...")
        return True
    
    def _execute_single_multi_analysis(self, config: Dict[str, Any]) -> bool:
        """执行单件多件分析"""
        st.write("🔀 **正在执行单件多件分析...**")
        st.info("🔀 单件多件分析功能待完善...")
        return True
    
    def _execute_hit_rate_analysis(self, config: Dict[str, Any]) -> bool:
        """执行命中率分析"""
        st.write("🎯 **正在执行命中率分析...**")
        st.info("🎯 命中率分析功能待完善...")
        return True
    
    def _execute_inbound_analysis(self, config: Dict[str, Any]) -> bool:
        """执行入库通用分析"""
        try:
            st.subheader("📥 入库数据趋势分析")
            
            # 获取配置参数
            date_column = config.get("入库分析_date_column")
            
            # 新的配置格式：SKU相关
            sku_column = config.get("入库分析_sku_column")
            sku_count_column = config.get("入库分析_sku_count_column")
            
            # 新的配置格式：件数相关
            quantity_column = config.get("入库分析_quantity_column")
            quantity_count_column = config.get("入库分析_quantity_count_column")
            
            # 日期范围
            start_date = config.get("入库分析_start_date")
            end_date = config.get("入库分析_end_date")
            
            # 处理"无数据"选项
            if sku_column == "无数据":
                sku_column = None
            if sku_count_column == "无数据":
                sku_count_column = None
            if quantity_column == "无数据":
                quantity_column = None
            if quantity_count_column == "无数据":
                quantity_count_column = None
                
            # 验证必需配置
            if not date_column:
                st.error("❌ 请选择日期列")
                return False
                
            # 创建分析器
            analyzer = InboundAnalyzer(config)
            
            # 执行增强分析（支持原始和聚合数据）
            daily_data, summary = analyzer.analyze_batch_enhanced(
                df=self.df,
                date_column=date_column,
                sku_column=sku_column,
                sku_count_column=sku_count_column,
                quantity_column=quantity_column,
                quantity_count_column=quantity_count_column,
                start_date=start_date,
                end_date=end_date
            )
            
            if daily_data.empty:
                st.warning("⚠️ 没有找到有效的入库数据")
                return False
            
            # 渲染趋势图表
            analyzer.render_trend_chart(daily_data, date_column, summary)
            
            # 显示统计摘要
            if summary:
                st.subheader("📊 统计摘要")
                date_info = summary.get('date_range', {})
                st.info(f"📅 分析时间范围：{date_info.get('start_date')} 至 {date_info.get('end_date')}，共 {date_info.get('total_days', 0)} 天")
                
                # 显示各维度统计
                for col, stats in summary.items():
                    if isinstance(stats, dict) and 'total' in stats:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"总{col.replace('日入', '')}", f"{stats['total']:,}")
                        with col2:
                            st.metric(f"日均{col.replace('日入', '')}", f"{stats['daily_avg']:.1f}")
                        with col3:
                            # 显示最高和最低信息
                            max_val = stats.get('daily_max', 0)
                            min_val = stats.get('daily_min', 0)
                            max_date = stats.get('max_date', '')
                            min_date = stats.get('min_date', '')
                            
                            # 格式化日期显示
                            max_date_str = max_date.strftime('%Y-%m-%d') if hasattr(max_date, 'strftime') else str(max_date)
                            min_date_str = min_date.strftime('%Y-%m-%d') if hasattr(min_date, 'strftime') else str(min_date)
                            
                            st.metric(
                                "最高/最低", 
                                f"{max_val:.0f} / {min_val:.0f}",
                                help=f"最高值: {max_val:.0f} ({max_date_str})\n最低值: {min_val:.0f} ({min_date_str})"
                            )
            
            # 提供数据下载
            st.subheader("📥 数据导出")
            csv_data = daily_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 导出入库趋势数据(CSV)",
                data=csv_data,
                file_name=f"入库趋势分析_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="下载完整的入库趋势分析数据"
            )
            
            # 保存分析结果供其他分析使用
            self.analysis_results["入库分析"] = {
                "daily_data": daily_data,
                "summary": summary,
                "suggestions": []
            }
            
            return True
            
        except Exception as e:
            st.error(f"❌ 入库分析执行失败: {str(e)}")
            return False
    
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
            "ABC分析": ["value_column"],
    
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
                "weight_unit": "kg",
                "show_details": True,
                "container_length": 600,
                "container_width": 400,
                "container_height": 300,
                "container_weight_limit": 30,
                "use_dividers": False,
                "selected_dividers": []
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