# -*- coding: utf-8 -*-
"""
工具函数模块 - 包含通用的工具函数和辅助方法
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def load_excel_data(uploaded_file, sheet_name: str) -> pd.DataFrame:
        """
        加载Excel数据
        
        Args:
            uploaded_file: 上传的文件对象
            sheet_name: Sheet名称
            
        Returns:
            pd.DataFrame: 数据框
        """
        try:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name)
        except Exception as e:
            st.error(f"读取Excel文件失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def validate_columns_existence(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        验证数据框中是否存在必需的列
        
        Args:
            df: 数据框
            required_columns: 必需的列名列表
            
        Returns:
            tuple: (是否全部存在, 缺失的列名列表)
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns
    
    @staticmethod 
    def clean_numeric_column(series: pd.Series, column_name: str = "数据") -> pd.Series:
        """
        清理数值列，转换为数值类型并处理异常值
        
        Args:
            series: 数据序列
            column_name: 列名（用于日志）
            
        Returns:
            pd.Series: 清理后的数据序列
        """
        original_count = len(series)
        
        # 转换为数值类型
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # 统计转换失败的数量
        failed_count = numeric_series.isna().sum() - series.isna().sum()
        if failed_count > 0:
            st.warning(f"{column_name}列有 {failed_count} 个值无法转换为数值")
            
        return numeric_series
    
    @staticmethod
    def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取数据框的列信息
        
        Args:
            df: 数据框
            
        Returns:
            dict: 列信息统计
        """
        info = {
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'text_columns': len(df.select_dtypes(include=['object', 'string']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
            'columns_with_nulls': df.isnull().any().sum(),
            'total_null_values': df.isnull().sum().sum()
        }
        return info
    
    @staticmethod
    def filter_valid_rows(df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """
        过滤掉包含必需列中有空值的行
        
        Args:
            df: 数据框
            required_columns: 必需的列名列表
            
        Returns:
            pd.DataFrame: 过滤后的数据框
        """
        before_count = len(df)
        
        # 过滤空值
        mask = df[required_columns].notna().all(axis=1)
        filtered_df = df[mask].copy()
        
        after_count = len(filtered_df)
        if before_count != after_count:
            st.info(f"过滤掉 {before_count - after_count} 行包含空值的数据，剩余 {after_count} 行")
            
        return filtered_df

class SessionStateManager:
    """Session状态管理器"""
    
    @staticmethod
    def initialize_session_state():
        """初始化Session状态"""
        default_states = {
            'analysis_type': None,
            'analysis_name': None,
            'sheet_confirmed': False,
            'selected_sheet': None,
            'dimensions_confirmed': False,
            'selected_dimensions': [],
            'analysis_confirmed': False,
            'data_loaded': False,
            'container_length': 600,
            'container_width': 400,
            'container_height': 300
        }
        
        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def clear_session_data(keys_to_clear: List[str] = None):
        """
        清理Session数据
        
        Args:
            keys_to_clear: 要清理的键列表，如果为None则清理所有数据缓存
        """
        if keys_to_clear is None:
            keys_to_clear = ['sheet_confirmed', 'analysis_type', 'dimensions_confirmed', 
                           'analysis_confirmed', 'selected_dimensions', 'analysis_name', 'data_loaded']
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 清理数据缓存
        for key in list(st.session_state.keys()):
            if key.startswith('data_'):
                del st.session_state[key]
    
    @staticmethod
    def get_analysis_config(dimension: str) -> Dict[str, Any]:
        """
        获取特定维度的分析配置
        
        Args:
            dimension: 分析维度名称
            
        Returns:
            dict: 配置信息
        """
        config = {}
        
        # 装箱分析配置
        if dimension == "装箱分析":
            config = {
                'length_column': st.session_state.get("装箱分析_length_column"),
                'width_column': st.session_state.get("装箱分析_width_column"),
                'height_column': st.session_state.get("装箱分析_height_column"),
                'inventory_column': st.session_state.get("装箱分析_inventory_column"),
                'data_unit': st.session_state.get("装箱分析_data_unit", "cm"),
                'show_details': st.session_state.get("装箱分析_show_details", True),
                'container_length': st.session_state.get("container_length", 600),
                'container_width': st.session_state.get("container_width", 400),
                'container_height': st.session_state.get("container_height", 300)
            }
        
        # 异常数据清洗配置
        elif dimension == "异常数据清洗":
            config = {
                'all_conditions': st.session_state.get("异常数据清洗_all_conditions", []),
                'overall_logic': st.session_state.get("异常数据清洗_overall_logic", "OR"),
                'action': st.session_state.get("异常数据清洗_action", "删除")
            }
        
        return config

class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def generate_filename(prefix: str, analysis_type: str = "", extension: str = "csv") -> str:
        """
        生成文件名
        
        Args:
            prefix: 文件名前缀
            analysis_type: 分析类型
            extension: 文件扩展名
            
        Returns:
            str: 生成的文件名
        """
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        if analysis_type:
            filename = f"{prefix}_{analysis_type}_{timestamp}.{extension}"
        else:
            filename = f"{prefix}_{timestamp}.{extension}"
            
        return filename
    
    @staticmethod
    def convert_df_to_csv(df: pd.DataFrame, include_index: bool = False) -> bytes:
        """
        将DataFrame转换为CSV字节数据
        
        Args:
            df: 数据框
            include_index: 是否包含索引
            
        Returns:
            bytes: CSV字节数据
        """
        return df.to_csv(index=include_index).encode('utf-8-sig')
    
    @staticmethod
    def prepare_download_data(data: Dict[str, Any], format_type: str = "csv") -> bytes:
        """
        准备下载数据
        
        Args:
            data: 要导出的数据字典
            format_type: 格式类型
            
        Returns:
            bytes: 格式化后的数据
        """
        if format_type == "csv":
            # 如果是字典，转换为DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data]).T
                df.columns = ['数值']
                return FileUtils.convert_df_to_csv(df, include_index=True)
            elif isinstance(data, pd.DataFrame):
                return FileUtils.convert_df_to_csv(data)
            else:
                # 其他类型转为文本
                text_data = str(data)
                return text_data.encode('utf-8-sig')
        
        return b""

class ValidationUtils:
    """数据验证工具类"""
    
    @staticmethod
    def validate_positive_number(value: Any, field_name: str = "数值") -> Tuple[bool, str]:
        """
        验证是否为正数
        
        Args:
            value: 要验证的值
            field_name: 字段名称
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        try:
            num_value = float(value)
            if num_value <= 0:
                return False, f"{field_name}必须大于0"
            return True, ""
        except (ValueError, TypeError):
            return False, f"{field_name}必须是有效数字"
    
    @staticmethod
    def validate_dimension_data(length: Any, width: Any, height: Any) -> Tuple[bool, List[str]]:
        """
        验证尺寸数据
        
        Args:
            length, width, height: 长宽高数据
            
        Returns:
            tuple: (是否全部有效, 错误信息列表)
        """
        errors = []
        
        # 验证长度
        is_valid, error = ValidationUtils.validate_positive_number(length, "长度")
        if not is_valid:
            errors.append(error)
            
        # 验证宽度
        is_valid, error = ValidationUtils.validate_positive_number(width, "宽度")
        if not is_valid:
            errors.append(error)
            
        # 验证高度
        is_valid, error = ValidationUtils.validate_positive_number(height, "高度")
        if not is_valid:
            errors.append(error)
            
        return len(errors) == 0, errors
    
    @staticmethod
    def check_data_reasonableness(df: pd.DataFrame, dimension_columns: List[str], 
                                unit: str = "cm") -> List[str]:
        """
        检查数据合理性
        
        Args:
            df: 数据框
            dimension_columns: 尺寸列名列表
            unit: 数据单位
            
        Returns:
            list: 警告信息列表
        """
        warnings = []
        
        # 单位转换因子
        unit_factors = {"mm": 1, "cm": 10, "m": 1000}
        factor = unit_factors.get(unit, 10)
        
        for col in dimension_columns:
            if col in df.columns:
                data = pd.to_numeric(df[col], errors='coerce')
                data_mm = data * factor
                
                # 检查异常小的值
                too_small = (data_mm < 1).sum()
                if too_small > 0:
                    warnings.append(f"列'{col}'有{too_small}个值小于1mm，可能存在数据问题")
                
                # 检查异常大的值
                too_large = (data_mm > 10000).sum()  # 大于10米
                if too_large > 0:
                    warnings.append(f"列'{col}'有{too_large}个值大于10米，可能存在数据问题")
                
                # 检查零值或负值
                invalid = (data_mm <= 0).sum()
                if invalid > 0:
                    warnings.append(f"列'{col}'有{invalid}个无效值（≤0）")
        
        return warnings

class ProgressUtils:
    """进度显示工具类"""
    
    @staticmethod
    def create_progress_bar(total_steps: int, description: str = "处理中..."):
        """
        创建进度条
        
        Args:
            total_steps: 总步数
            description: 描述文字
            
        Returns:
            streamlit progress object
        """
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text(f"{description} (0/{total_steps})")
        
        return progress_bar, status_text
    
    @staticmethod
    def update_progress(progress_bar, status_text, current_step: int, 
                       total_steps: int, description: str = "处理中..."):
        """
        更新进度条
        
        Args:
            progress_bar: 进度条对象
            status_text: 状态文本对象
            current_step: 当前步数
            total_steps: 总步数
            description: 描述文字
        """
        progress = current_step / total_steps
        progress_bar.progress(progress)
        status_text.text(f"{description} ({current_step}/{total_steps})")
    
    @staticmethod
    def complete_progress(progress_bar, status_text, description: str = "完成！"):
        """
        完成进度显示
        
        Args:
            progress_bar: 进度条对象
            status_text: 状态文本对象
            description: 完成描述
        """
        progress_bar.progress(1.0)
        status_text.text(description)

class FormatUtils:
    """格式化工具类"""
    
    @staticmethod
    def format_number(value: float, decimal_places: int = 2, use_separator: bool = True) -> str:
        """
        格式化数字
        
        Args:
            value: 数值
            decimal_places: 小数位数
            use_separator: 是否使用千分位分隔符
            
        Returns:
            str: 格式化后的字符串
        """
        if pd.isna(value) or value == float('inf') or value == float('-inf'):
            return "N/A"
            
        if use_separator:
            return f"{value:,.{decimal_places}f}"
        else:
            return f"{value:.{decimal_places}f}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """
        格式化百分比
        
        Args:
            value: 数值（0-1之间）
            decimal_places: 小数位数
            
        Returns:
            str: 格式化后的百分比字符串
        """
        if pd.isna(value):
            return "N/A"
        
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 字节数
            
        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB" 