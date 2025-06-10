# -*- coding: utf-8 -*-
"""
入库通用分析模块 - 专门处理入库数据的时间序列分析
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class InboundAnalyzer:
    """入库通用分析器"""
    
    def __init__(self, config: Dict):
        """
        初始化入库分析器
        
        Args:
            config: 分析配置参数
        """
        self.config = config
        
    def clean_date_column(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        清理日期列，保持为datetime格式以便后续处理
        
        Args:
            df: 数据框
            date_column: 日期列名
            
        Returns:
            pd.DataFrame: 清理后的数据框
        """
        df_clean = df.copy()
        
        try:
            # 尝试转换为日期时间格式
            df_clean[date_column] = pd.to_datetime(df_clean[date_column], errors='coerce')
            
            # 删除无法解析的日期行
            df_clean = df_clean.dropna(subset=[date_column])
            
            st.info(f"📅 日期列已清理：保留 {len(df_clean)} 行有效日期数据")
            
        except Exception as e:
            st.error(f"❌ 日期列清理失败: {str(e)}")
            return df
            
        return df_clean
        
    def aggregate_daily_data(self, df: pd.DataFrame, date_column: str, 
                           sku_column: Optional[str] = None,
                           quantity_column: Optional[str] = None) -> pd.DataFrame:
        """
        按日期聚合入库数据
        
        Args:
            df: 数据框
            date_column: 日期列名
            sku_column: SKU数列名（可选）
            quantity_column: 件数列名（可选）
            
        Returns:
            pd.DataFrame: 聚合后的日期数据
        """
        try:
            # 准备聚合字典
            agg_dict = {}
                
            # 如果有SKU列，计算每日入库SKU数（去重）
            if sku_column and sku_column in df.columns:
                agg_dict[f'日入SKU数'] = (sku_column, 'nunique')
                
            # 如果有数量列，计算每日入库件数总和
            if quantity_column and quantity_column in df.columns:
                agg_dict[f'日入件数'] = (quantity_column, 'sum')
            
            if not agg_dict:
                st.warning("⚠️ 没有可聚合的数据列")
                return pd.DataFrame()
            
            # 按日期分组聚合
            daily_data = df.groupby(date_column).agg(agg_dict).reset_index()
            
            # 处理列名（处理pandas聚合后的多级索引）
            if isinstance(daily_data.columns, pd.MultiIndex):
                # 处理多级索引：保留第一列(日期列)，其他列使用聚合字典的键名
                new_columns = [daily_data.columns[0][0]]  # 日期列
                new_columns.extend(list(agg_dict.keys()))  # 聚合指标名
                daily_data.columns = new_columns
            else:
                # 如果不是多级索引，检查列名长度
                if len(daily_data.columns) != len(agg_dict) + 1:
                    new_columns = [daily_data.columns[0]]  # 保留第一列(日期列)
                    new_columns.extend(list(agg_dict.keys()))  # 添加聚合指标名
                    daily_data.columns = new_columns
            
            # 按日期排序
            daily_data = daily_data.sort_values(date_column)
            
            st.success(f"✅ 数据聚合完成：共 {len(daily_data)} 天的入库数据")
                
            return daily_data
            
        except Exception as e:
            st.error(f"❌ 数据聚合失败: {str(e)}")
            # 添加调试信息
            st.error(f"调试信息：date_column={date_column}, agg_dict={agg_dict}")
            if 'df' in locals():
                st.error(f"数据框列名: {list(df.columns)}")
            return pd.DataFrame()
    
    def filter_date_range(self, df: pd.DataFrame, date_column: str, 
                         start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        根据日期范围过滤数据
        
        Args:
            df: 数据框
            date_column: 日期列名
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        try:

            
            # 转换输入的日期参数
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date).date()
            elif hasattr(start_date, 'date'):
                start_date = start_date.date()
                
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date).date()
            elif hasattr(end_date, 'date'):
                end_date = end_date.date()
            
            # 确保日期列是datetime类型
            df[date_column] = pd.to_datetime(df[date_column])
            
            # 转换为日期进行比较
            df_dates = df[date_column].dt.date
            
            # 过滤日期范围
            mask = (df_dates >= start_date) & (df_dates <= end_date)
            filtered_df = df[mask]
            
            st.info(f"📊 日期过滤：{start_date} 至 {end_date}，共 {len(filtered_df)} 条记录")
            
            return filtered_df
            
        except Exception as e:
            st.error(f"❌ 日期过滤失败: {str(e)}")

            return df
    
    def analyze_batch(self, df: pd.DataFrame, date_column: str,
                     sku_column: Optional[str] = None,
                     quantity_column: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        批量分析入库数据
        
        Args:
            df: 原始数据框
            date_column: 日期列名
            sku_column: SKU数列名
            quantity_column: 件数列名
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Tuple[pd.DataFrame, Dict]: (聚合后的日期数据, 统计摘要)
        """
        try:
            # 1. 清理日期列
            df_cleaned = self.clean_date_column(df, date_column)
            
            if df_cleaned.empty:
                return pd.DataFrame(), {}
            
            # 2. 日期过滤
            if start_date and end_date:
                df_cleaned = self.filter_date_range(df_cleaned, date_column, start_date, end_date)
            
            # 3. 按日聚合数据
            daily_data = self.aggregate_daily_data(
                df_cleaned, date_column, sku_column, quantity_column
            )
            
            if daily_data.empty:
                return pd.DataFrame(), {}
            
            # 4. 生成统计摘要
            summary = self.generate_summary_statistics(daily_data, date_column)
            
            return daily_data, summary
            
        except Exception as e:
            st.error(f"❌ 入库分析失败: {str(e)}")
            return pd.DataFrame(), {}
    
    def calculate_average_without_outliers(self, data: pd.Series) -> float:
        """
        计算剔除离群值后的平均数
        
        Args:
            data: 数据序列
            
        Returns:
            float: 剔除离群值后的平均数
        """
        try:
            if len(data) < 4:  # 数据点太少，直接返回平均数
                return data.mean()
            
            # 使用IQR方法检测离群值
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            # 定义离群值范围
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # 过滤离群值
            filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]
            
            # 如果过滤后数据太少，使用原始数据
            if len(filtered_data) < len(data) * 0.5:  # 如果剔除了超过50%的数据，使用原始数据
                return data.mean()
            
            return filtered_data.mean()
            
        except Exception as e:
            return data.mean()  # 出错时返回普通平均数
    
    def filter_outliers_98_percentile(self, data: pd.Series) -> pd.Series:
        """
        单向过滤：只过滤异常低值，保留所有高值
        特别针对：订单数、SKU数、件数等业务指标中的异常低值（如1-2）
        
        Args:
            data: 数据序列
            
        Returns:
            pd.Series: 过滤后的数据序列
        """
        try:
            if len(data) < 10:  # 数据点太少，返回原始数据
                return data
            
            # 🔍 第一步：分析数据的基本统计特征
            median = data.median()
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            mean_val = data.mean()
            
            print(f"数据分析 - 中位数: {median:.1f}, Q1: {q1:.1f}, Q3: {q3:.1f}, 均值: {mean_val:.1f}")
            
            # 🔍 第二步：识别异常低值（业务逻辑判断）
            # 对于订单数、SKU数、件数等业务指标，小于10的值通常是异常的
            if median > 50:  # 正常业务数据的中位数应该比较大
                min_business_value = max(10, q1 * 0.1)  # 业务最小值不应小于Q1的10%，且不小于10
                print(f"业务最小值阈值: {min_business_value:.1f}")
            else:
                min_business_value = max(1, median * 0.1)  # 对于较小的数据，允许更小的值
                print(f"业务最小值阈值（小数据）: {min_business_value:.1f}")
            
            # 🔍 第三步：不设置上边界，保留所有高值
            # 注释掉上边界计算，只保留下边界过滤
            # 这样可以保留业务中的所有高峰值数据
            
            # 🔍 第四步：只应用下边界过滤，保留所有高值
            filtered_data = data[data >= min_business_value]
            
            # 🔍 第五步：安全检查
            if len(filtered_data) < len(data) * 0.3:  # 如果过滤掉超过70%的数据
                print("过滤过于严格，使用备用方案")
                # 使用更宽松的5%分位数作为下边界
                lower_backup = data.quantile(0.05)
                filtered_data = data[data >= lower_backup]
            
            print(f"单向过滤结果 - 原始: {len(data)}个, 过滤后: {len(filtered_data)}个, 移除低值: {len(data) - len(filtered_data)}个")
            print(f"过滤后范围: {filtered_data.min():.1f} ~ {filtered_data.max():.1f} (保留所有高值)")
            
            return filtered_data if len(filtered_data) >= 5 else data
            
        except Exception as e:
            print(f"过滤出错: {str(e)}")
            return data  # 出错时返回原始数据

    def generate_summary_statistics(self, daily_data: pd.DataFrame, date_column: str) -> Dict:
        """
        生成统计摘要
        
        Args:
            daily_data: 日聚合数据
            date_column: 日期列名
            
        Returns:
            Dict: 统计摘要
        """
        try:
            summary = {
                'date_range': {
                    'start_date': daily_data[date_column].min(),
                    'end_date': daily_data[date_column].max(),
                    'total_days': len(daily_data)
                }
            }
            
            # 计算各维度的统计信息
            for col in daily_data.columns:
                if col != date_column and daily_data[col].dtype in ['int64', 'float64']:
                    avg_without_outliers = self.calculate_average_without_outliers(daily_data[col])
                    
                    # 使用98%分位数过滤离群值，然后计算真正的最大最小值
                    filtered_data = self.filter_outliers_98_percentile(daily_data[col])
                    
                    # 在过滤后的数据中找到最高和最低点
                    if len(filtered_data) > 0:
                        filtered_max = filtered_data.max()
                        filtered_min = filtered_data.min()
                        
                        # 找到对应的日期（在原始数据中）
                        max_mask = daily_data[col] == filtered_max
                        min_mask = daily_data[col] == filtered_min
                        
                        # 如果有多个相同的最大/最小值，取第一个
                        max_date = daily_data.loc[max_mask, date_column].iloc[0] if max_mask.any() else daily_data.loc[daily_data[col].idxmax(), date_column]
                        min_date = daily_data.loc[min_mask, date_column].iloc[0] if min_mask.any() else daily_data.loc[daily_data[col].idxmin(), date_column]
                    else:
                        # 如果过滤后没有数据，使用原始数据
                        filtered_max = daily_data[col].max()
                        filtered_min = daily_data[col].min()
                        max_date = daily_data.loc[daily_data[col].idxmax(), date_column]
                        min_date = daily_data.loc[daily_data[col].idxmin(), date_column]
                    
                    summary[col] = {
                        'total': daily_data[col].sum(),
                        'daily_avg': daily_data[col].mean(),
                        'daily_avg_no_outliers': avg_without_outliers,  # 剔除离群值后的平均数
                        'daily_max': filtered_max,  # 使用过滤后的最大值
                        'daily_min': filtered_min,  # 使用过滤后的最小值
                        'max_date': max_date,  # 最高点日期
                        'min_date': min_date,  # 最低点日期
                        'trend': 'increasing' if daily_data[col].iloc[-1] > daily_data[col].iloc[0] else 'decreasing'
                    }
            
            return summary
            
        except Exception as e:
            st.error(f"❌ 统计摘要生成失败: {str(e)}")
            return {}
    
    def render_trend_chart(self, daily_data: pd.DataFrame, date_column: str, summary: Dict = None) -> None:
        """
        渲染趋势折线图
        
        Args:
            daily_data: 日聚合数据
            date_column: 日期列名
            summary: 统计摘要（包含平均数信息）
        """
        try:
            if daily_data.empty:
                st.warning("⚠️ 没有数据可供绘图")
                return
            
            # 🚀 性能优化：对大数据集进行智能采样
            sample_data = daily_data.copy()
            original_count = len(daily_data)
            
            if len(daily_data) > 1000:  # 超过1000个点时进行采样
                # 计算采样比例，最多保留1000个点
                sample_ratio = min(1000 / len(daily_data), 1.0)
                sample_data = daily_data.sample(frac=sample_ratio, random_state=42).sort_values(date_column)
                st.info(f"📊 图表性能优化：从 {original_count:,} 个数据点采样 {len(sample_data):,} 个点以提升交互性能")
            
            # 创建图表
            fig = go.Figure()
            
            # 优化的颜色和样式配置 - 避免颜色重叠
            colors = ['#ff6b35', '#004e89', '#009ffd', '#00d4aa', '#ffbc42']
            line_styles = ['solid', 'dash', 'dot', 'dashdot']
            marker_symbols = ['circle', 'square', 'diamond', 'triangle-up', 'star']
            
            color_idx = 0
            
            for col in sample_data.columns:
                if col != date_column and sample_data[col].dtype in ['int64', 'float64']:
                    # 调整线条样式，避免重叠
                    line_width = 3 if color_idx == 0 else 2  # 第一条线更粗
                    marker_size = 6 if color_idx == 0 else 4  # 第一条线的点更大
                    opacity = 0.9 if color_idx == 0 else 0.8  # 第一条线更不透明
                    
                    fig.add_trace(go.Scatter(
                        x=sample_data[date_column],
                        y=sample_data[col],
                        mode='lines+markers',
                        name=col,
                        line=dict(
                            color=colors[color_idx % len(colors)], 
                            width=line_width,
                            dash=line_styles[color_idx % len(line_styles)] if color_idx > 0 else 'solid'
                        ),
                        marker=dict(
                            size=marker_size,
                            symbol=marker_symbols[color_idx % len(marker_symbols)],
                            opacity=opacity
                        ),
                        opacity=opacity,
                        hovertemplate=f'<b>{col}</b><br>日期: %{{x}}<br>数量: %{{y:,.0f}}<extra></extra>'
                    ))
                    color_idx += 1
            
            # 🔹 添加最高最低点标注
            if summary:
                point_color_idx = 0
                for col in sample_data.columns:
                    if col != date_column and sample_data[col].dtype in ['int64', 'float64']:
                        col_summary = summary.get(col, {})
                        line_color = colors[point_color_idx % len(colors)]
                        
                        # 添加最高点标注
                        if 'daily_max' in col_summary and 'max_date' in col_summary:
                            max_value = col_summary['daily_max']
                            max_date = col_summary['max_date']
                            
                            fig.add_annotation(
                                x=max_date,
                                y=max_value,
                                xref="x", 
                                yref="y",
                                text=f"🔴 最高: {max_value:.0f}",
                                font=dict(color=line_color, size=10, family="Arial"),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor=line_color,
                                borderwidth=1,
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor=line_color,
                                ax=0,
                                ay=-25  # 标注在点上方
                            )
                        
                        # 添加最低点标注
                        if 'daily_min' in col_summary and 'min_date' in col_summary:
                            min_value = col_summary['daily_min']
                            min_date = col_summary['min_date']
                            
                            fig.add_annotation(
                                x=min_date,
                                y=min_value,
                                xref="x", 
                                yref="y",
                                text=f"🔵 最低: {min_value:.0f}",
                                font=dict(color=line_color, size=10, family="Arial"),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor=line_color,
                                borderwidth=1,
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor=line_color,
                                ax=0,
                                ay=25   # 标注在点下方
                            )
                        point_color_idx += 1
            
            # 🔹 添加平均数线（剔除离群值）- 颜色匹配数据线，带数值标注
            if summary:
                avg_color_idx = 0
                avg_texts = []  # 收集所有平均值文本，统一显示在右上角
                
                for col in sample_data.columns:
                    if col != date_column and sample_data[col].dtype in ['int64', 'float64']:
                        col_summary = summary.get(col, {})
                        avg_no_outliers = col_summary.get('daily_avg_no_outliers')
                        
                        if avg_no_outliers is not None:
                            # 使用与数据线相同的颜色
                            line_color = colors[avg_color_idx % len(colors)]
                            
                            # 添加水平平均线
                            fig.add_hline(
                                y=avg_no_outliers,
                                line_dash="dot",
                                line_width=1.5,  # 线条变细
                                line_color=line_color,
                                opacity=0.8
                            )
                            
                            # 收集平均值文本，用于右上角显示
                            avg_texts.append(f"<span style='color:{line_color}'>●</span> {col} 平均: {avg_no_outliers:.1f}")
                            avg_color_idx += 1
                
                # 📊 在右上角统一显示所有平均值
                if avg_texts:
                    avg_text_combined = "<br>".join(avg_texts)
                    fig.add_annotation(
                        x=1,  # 右侧
                        y=1,  # 顶部
                        xref="paper",  # 使用纸张坐标
                        yref="paper",
                        text=avg_text_combined,
                        font=dict(color='white', size=11),
                        bgcolor="rgba(17,17,17,0.9)",  # 与图表背景一致的深色
                        bordercolor="rgba(128,128,128,0.5)",
                        borderwidth=1,
                        showarrow=False,
                        xanchor="right",
                        yanchor="top",
                        align="left"
                    )
            
            # 🔧 计算Y轴的合适范围
            y_min_overall = float('inf')
            y_max_overall = 0
            
            for col in sample_data.columns:
                if col != date_column and sample_data[col].dtype in ['int64', 'float64']:
                    col_min = sample_data[col].min()
                    col_max = sample_data[col].max()
                    y_min_overall = min(y_min_overall, col_min)
                    y_max_overall = max(y_max_overall, col_max)
            
            # 计算合适的Y轴边界，留10%的空间用于视觉效果
            if y_min_overall != float('inf'):
                y_range = y_max_overall - y_min_overall
                margin = y_range * 0.1  # 10%的边距
                y_axis_min = max(0, y_min_overall - margin)  # 不低于0
                y_axis_max = y_max_overall + margin
                
    
            else:
                y_axis_min = None
                y_axis_max = None
            
            # 图表样式设置
            fig.update_layout(
                title=dict(
                    text="<b>入库数据趋势分析</b>",
                    x=0.5,
                    font=dict(size=18, color='white')
                ),
                xaxis=dict(
                    title="<b>日期</b>",
                    title_font=dict(size=14, color='white'),
                    tickfont=dict(color='white'),
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)'
                ),
                yaxis=dict(
                    title="<b>数量</b>",
                    title_font=dict(size=14, color='white'),
                    tickfont=dict(color='white'),
                    type="linear",  # 使用线性刻度而不是对数刻度
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.3)',
                    range=[y_axis_min, y_axis_max] if y_axis_min is not None else None,  # 设置Y轴范围
                    autorange=False if y_axis_min is not None else True  # 禁用自动范围
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='white'),
                    bgcolor='rgba(0,0,0,0.5)'  # 图例背景
                ),
                plot_bgcolor='rgba(17, 17, 17, 0.8)',
                paper_bgcolor='rgba(17, 17, 17, 0.8)',
                font=dict(color='white'),
                height=500,
                hovermode='x unified'
            )
            
            # 🚀 性能优化：减少渲染复杂度
            fig.update_traces(
                connectgaps=False,  # 不连接缺失数据的间隙
                line_smoothing=0.5  # 适度平滑
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ 图表渲染失败: {str(e)}")
    
    def generate_optimization_suggestions(self, daily_data: pd.DataFrame, summary: Dict) -> List[str]:
        """
        生成优化建议（包含详细统计数据）
        
        Args:
            daily_data: 日聚合数据
            summary: 统计摘要
            
        Returns:
            List[str]: 优化建议列表
        """
        suggestions = []
        
        try:
            # 📊 添加数据统计摘要
            date_range = summary.get('date_range', {})
            if date_range:
                start_date = date_range.get('start_date', '未知')
                end_date = date_range.get('end_date', '未知')
                total_days = date_range.get('total_days', 0)
                suggestions.append(f"📅 **分析周期**: {start_date} 至 {end_date}，共 {total_days} 天")
            
            # 📈 添加各维度的详细统计信息
            for col, stats in summary.items():
                if isinstance(stats, dict) and 'daily_avg_no_outliers' in stats:
                    avg_no_outliers = stats.get('daily_avg_no_outliers', 0)
                    daily_max = stats.get('daily_max', 0)
                    daily_min = stats.get('daily_min', 0)
                    max_date = stats.get('max_date', '未知')
                    min_date = stats.get('min_date', '未知')
                    
                    suggestions.append(
                        f"📊 **{col}**: "
                        f"平均 {avg_no_outliers:.1f}/天 | "
                        f"最高 {daily_max:.0f} ({max_date}) | "
                        f"最低 {daily_min:.0f} ({min_date})"
                    )
                    
                    # 趋势分析建议
                    if stats.get('trend') == 'increasing':
                        suggestions.append(f"📈 {col}呈上升趋势，建议关注库存容量规划")
                    elif daily_max > avg_no_outliers * 2:
                        suggestions.append(f"⚠️ {col}波动较大，建议分析入库高峰期的处理能力")
            
            # 基于数据分布的建议
            if len(daily_data) >= 7:
                suggestions.append("📅 建议按周/月维度分析入库规律，优化收货计划")
            
            if len([s for s in suggestions if not s.startswith("📊") and not s.startswith("📅")]) == 0:
                suggestions.append("💡 入库数据表现平稳，建议持续监控库存周转率")
                
        except Exception as e:
            suggestions.append(f"⚠️ 建议生成过程中出现错误: {str(e)}")
            
        return suggestions
    
    def aggregate_daily_data_enhanced(self, df: pd.DataFrame, date_column: str,
                                    sku_column: Optional[str] = None,
                                    sku_count_column: Optional[str] = None,
                                    quantity_column: Optional[str] = None,
                                    quantity_count_column: Optional[str] = None) -> pd.DataFrame:
        """
        增强的按日期聚合入库数据，支持原始数据和聚合数据
        
        Args:
            df: 数据框
            date_column: 日期列名
            sku_column: SKU列名（原始）
            sku_count_column: SKU数/天列名（聚合）
            quantity_column: 件数列名（原始）
            quantity_count_column: 件数/天列名（聚合）
            
        Returns:
            pd.DataFrame: 聚合后的日期数据
        """
        try:
            # 准备聚合字典
            agg_dict = {}
            data_sources = []
            
            # SKU数据处理
            if sku_column and sku_column in df.columns:
                agg_dict['SKU数/天'] = (sku_column, 'nunique')
                data_sources.append(f"🔹 原始SKU数据：{sku_column}列，按日期去重计算SKU数/天")
            elif sku_count_column and sku_count_column in df.columns:
                agg_dict['SKU数/天'] = (sku_count_column, 'sum')
                data_sources.append(f"🔹 聚合SKU数据：{sku_count_column}列，直接按日期汇总")
            
            # 件数数据处理
            if quantity_column and quantity_column in df.columns:
                agg_dict['件数/天'] = (quantity_column, 'sum')
                data_sources.append(f"🔹 原始件数数据：{quantity_column}列，按日期求和计算件数/天")
            elif quantity_count_column and quantity_count_column in df.columns:
                agg_dict['件数/天'] = (quantity_count_column, 'sum')
                data_sources.append(f"🔹 聚合件数数据：{quantity_count_column}列，直接按日期汇总")
            
            if not agg_dict:
                st.warning("⚠️ 没有可聚合的数据列")
                return pd.DataFrame()
            
            # 显示数据处理方式
            st.success("✅ **数据处理方式**：\n" + "\n".join(data_sources))
            
            # 验证源列是否存在
            missing_columns = []
            for metric_name, (col_name, agg_func) in agg_dict.items():
                if col_name not in df.columns:
                    missing_columns.append(col_name)
            
            if missing_columns:
                st.error(f"❌ 缺失的源列: {missing_columns}")
                return pd.DataFrame()
            
            # 执行聚合 - 使用简单有效的方法（参考出库分析）
            try:
                # 先按现有列名聚合，后续重命名
                simple_agg_dict = {}
                target_column_names = []
                
                for target_name, (source_column, agg_func) in agg_dict.items():
                    simple_agg_dict[source_column] = agg_func
                    target_column_names.append(target_name)
                
                # 🔧 重要修复：将日期时间转换为日期，确保按日聚合
                df_for_grouping = df.copy()
                df_for_grouping[date_column] = pd.to_datetime(df_for_grouping[date_column]).dt.date
                
                # 执行分组聚合（按日期聚合）
                grouped = df_for_grouping.groupby(date_column)
                
                # 执行聚合操作
                daily_data = grouped.agg(simple_agg_dict)
                
                # 重置索引
                daily_data = daily_data.reset_index()
                
                # 重命名列名
                if len(daily_data.columns) == len(target_column_names) + 1:  # +1 for date column
                    new_columns = [date_column] + target_column_names
                    daily_data.columns = new_columns
                
                # 将日期列转换回datetime格式以便图表显示
                daily_data[date_column] = pd.to_datetime(daily_data[date_column])
                
            except Exception as e:
                st.error(f"❌ pandas聚合操作失败: {str(e)}")
                return pd.DataFrame()
            
            # 检查日期列是否存在
            if date_column not in daily_data.columns:
                st.error(f"❌ 日期列 '{date_column}' 不在最终数据中")
                return pd.DataFrame()
            
            # 按日期排序
            daily_data = daily_data.sort_values(date_column)
            
            # 显示处理结果统计
            result_summary = []
            for col in daily_data.columns:
                if col != date_column and daily_data[col].dtype in ['int64', 'float64']:
                    total = daily_data[col].sum()
                    avg = daily_data[col].mean()
                    result_summary.append(f"📊 {col}：总计 {total:,}，日均 {avg:.1f}")
            
            if result_summary:
                st.info("📈 **处理结果统计**：\n" + "\n".join(result_summary))
            
            st.success(f"✅ 数据聚合完成：共 {len(daily_data)} 天的入库数据")
            
            return daily_data
            
        except Exception as e:
            st.error(f"❌ 数据聚合失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_batch_enhanced(self, df: pd.DataFrame, date_column: str,
                             sku_column: Optional[str] = None,
                             sku_count_column: Optional[str] = None,
                             quantity_column: Optional[str] = None,
                             quantity_count_column: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        增强的批量分析入库数据，支持原始数据和聚合数据
        
        Args:
            df: 原始数据框
            date_column: 日期列名
            sku_column: SKU列名（原始）
            sku_count_column: SKU数/天列名（聚合）
            quantity_column: 件数列名（原始）
            quantity_count_column: 件数/天列名（聚合）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Tuple[pd.DataFrame, Dict]: (聚合后的日期数据, 统计摘要)
        """
        try:
            # 1. 清理日期列
            df_cleaned = self.clean_date_column(df, date_column)
            
            if df_cleaned.empty:
                return pd.DataFrame(), {}
            
            # 2. 日期过滤
            if start_date and end_date:
                df_cleaned = self.filter_date_range(df_cleaned, date_column, start_date, end_date)
            
            # 3. 按日聚合数据（增强版）
            daily_data = self.aggregate_daily_data_enhanced(
                df_cleaned, date_column, sku_column, sku_count_column,
                quantity_column, quantity_count_column
            )
            
            if daily_data.empty:
                return pd.DataFrame(), {}
            
            # 4. 生成统计摘要
            summary = self.generate_summary_statistics(daily_data, date_column)
            
            return daily_data, summary
            
        except Exception as e:
            st.error(f"❌ 入库分析失败: {str(e)}")
            return pd.DataFrame(), {} 