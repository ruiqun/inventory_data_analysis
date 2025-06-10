# -*- coding: utf-8 -*-
"""
工具函数模块 - 包含通用的工具函数和辅助方法
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional, Union

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def load_excel_data(uploaded_file, sheet_name: str) -> pd.DataFrame:
        """
        高性能加载Excel数据（优化版 - 支持缓存和性能优化）
        
        Args:
            uploaded_file: 上传的文件对象
            sheet_name: Sheet名称
            
        Returns:
            pd.DataFrame: 数据框
        """
        try:
            # 创建文件缓存键
            file_key = f"{uploaded_file.name}_{uploaded_file.size}_{sheet_name}"
            cache_key = f"data_{file_key}"
            
            # 检查缓存
            if cache_key in st.session_state:
                return st.session_state[cache_key]
            
            # 性能优化的Excel读取
            with st.spinner(f"📊 正在高速加载数据表：{sheet_name}..."):
                # 第一步：快速检查文件格式和数据量
                try:
                    # 使用openpyxl引擎，性能更好
                    sample_df = pd.read_excel(
                        uploaded_file, 
                        sheet_name=sheet_name, 
                        nrows=10,
                        engine='openpyxl'  # 明确指定引擎
                    )
                    
                    if sample_df.empty:
                        st.warning(f"⚠️ 工作表 {sheet_name} 为空")
                        return pd.DataFrame()
                    
                except Exception as e:
                    st.error(f"❌ 文件格式检查失败: {str(e)}")
                    return pd.DataFrame()
                
                # 第二步：优化参数读取完整数据
                try:
                    # 使用优化参数加载
                    df = pd.read_excel(
                        uploaded_file,
                        sheet_name=sheet_name,
                        engine='openpyxl',  # 使用openpyxl引擎，通常比xlrd更快
                        na_values=['', 'NULL', 'null', 'N/A', 'n/a', '#N/A'],  # 明确指定NA值
                        keep_default_na=True  # 保持默认NA处理
                    )
                    
                    # 第三步：数据类型优化（减少内存使用）
                    df = DataUtils._optimize_dataframe_dtypes(df)
                    
                    # 缓存数据
                    st.session_state[cache_key] = df
                    
                    # 显示加载结果
                    rows, cols = df.shape
                    file_size = f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"
                    
                    return df
                    
                except Exception as e:
                    # 如果优化参数失败，回退到基本参数
                    st.warning(f"⚠️ 使用基本模式加载...")
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    st.session_state[cache_key] = df
                    return df
                
        except Exception as e:
            st.error(f"❌ 读取Excel文件失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def _optimize_dataframe_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """
        优化DataFrame的数据类型以减少内存使用
        
        Args:
            df: 原始DataFrame
            
        Returns:
            pd.DataFrame: 优化后的DataFrame
        """
        try:
            # 优化数值列
            for col in df.select_dtypes(include=['int64']).columns:
                col_min = df[col].min()
                col_max = df[col].max()
                
                # 选择最小的整数类型
                if col_min >= -128 and col_max <= 127:
                    df[col] = df[col].astype('int8')
                elif col_min >= -32768 and col_max <= 32767:
                    df[col] = df[col].astype('int16')
                elif col_min >= -2147483648 and col_max <= 2147483647:
                    df[col] = df[col].astype('int32')
            
            # 优化浮点列
            for col in df.select_dtypes(include=['float64']).columns:
                # 检查是否可以转换为float32而不丢失精度
                original_values = df[col].dropna()
                if len(original_values) > 0:
                    converted = original_values.astype('float32')
                    if original_values.equals(converted.astype('float64')):
                        df[col] = df[col].astype('float32')
            
            # 优化字符串列
            for col in df.select_dtypes(include=['object']).columns:
                # 如果是字符串且重复值很多，转换为category
                if df[col].dtype == 'object':
                    num_unique_values = df[col].nunique()
                    num_total_values = len(df[col])
                    if num_total_values > 0 and num_unique_values / num_total_values < 0.5:
                        df[col] = df[col].astype('category')
            
            return df
            
        except Exception:
            # 如果优化失败，返回原始DataFrame
            return df
    
    @staticmethod
    def get_excel_sheets_info(uploaded_file) -> Dict[str, Any]:
        """
        获取Excel文件的工作表信息（缓存版）
        
        Args:
            uploaded_file: 上传的文件对象
            
        Returns:
            dict: 工作表信息
        """
        try:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            info_key = f"excel_info_{file_key}"
            
            # 检查缓存
            if info_key in st.session_state:
                return st.session_state[info_key]
            
                                    # 读取Excel文件信息
            with st.spinner("🔍 正在分析Excel文件结构..."):
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                
                # 获取每个sheet的基本信息
                sheets_info = {}
                for sheet_name in sheet_names:
                    try:
                        # 只读取前几行来获取基本信息
                        sample_df = pd.read_excel(uploaded_file, sheet_name=sheet_name, nrows=10)
                        sheets_info[sheet_name] = {
                            'columns': len(sample_df.columns),
                            'has_data': not sample_df.empty,
                            'sample_columns': list(sample_df.columns)[:5] if not sample_df.empty else []  # 前5列
                        }
                    except Exception:
                        sheets_info[sheet_name] = {
                            'columns': 0,
                            'has_data': False,
                            'sample_columns': []
                        }
                    
                info = {
                    'sheet_names': sheet_names,
                    'sheet_count': len(sheet_names),
                    'sheets_info': sheets_info
                }
                
                # 缓存信息
                st.session_state[info_key] = info
                
                return info
                
        except Exception as e:
            st.error(f"❌ Excel文件分析失败: {str(e)}")
            return {'sheet_names': [], 'sheet_count': 0, 'sheets_info': {}}
    
    @staticmethod
    def get_excel_sheets_names_only(uploaded_file) -> Dict[str, Any]:
        """
        仅获取Excel文件的工作表名称（快速版本）
        
        Args:
            uploaded_file: 上传的文件对象
            
        Returns:
            dict: 仅包含工作表名称的信息
        """
        try:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            names_key = f"excel_names_{file_key}"
            
            # 检查缓存
            if names_key in st.session_state:
                return st.session_state[names_key]
            
            # 仅读取工作表名称，不读取任何内容
            with st.spinner("🔍 正在读取工作表名称..."):
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                
                info = {
                    'sheet_names': sheet_names,
                    'sheet_count': len(sheet_names)
                }
                
                # 缓存信息
                st.session_state[names_key] = info
                
                return info
                
        except Exception as e:
            st.error(f"❌ 读取Excel工作表名称失败: {str(e)}")
            return {'sheet_names': [], 'sheet_count': 0}
    
    @staticmethod
    def load_data_in_background(uploaded_file, sheet_name: str, progress_placeholder=None):
        """
        在后台加载数据（带进度提示）
        
        Args:
            uploaded_file: 上传的文件对象
            sheet_name: Sheet名称
            progress_placeholder: 进度显示占位符
            
        Returns:
            pd.DataFrame: 数据框
        """
        try:
            # 创建文件缓存键
            file_key = f"{uploaded_file.name}_{uploaded_file.size}_{sheet_name}"
            cache_key = f"data_{file_key}"
            
            # 检查缓存
            if cache_key in st.session_state:
                if progress_placeholder:
                    progress_placeholder.success("📋 使用缓存数据，加载完成！")
                return st.session_state[cache_key]
            
            # 显示详细的加载进度
            if progress_placeholder:
                progress_placeholder.info(f"🔄 正在读取工作表：{sheet_name}")
            
            # 先尝试读取少量数据检查文件格式
            try:
                sample_df = pd.read_excel(uploaded_file, sheet_name=sheet_name, nrows=5)
                if sample_df.empty:
                    if progress_placeholder:
                        progress_placeholder.warning(f"⚠️ 工作表 {sheet_name} 为空")
                    return pd.DataFrame()
                
                total_rows = len(pd.read_excel(uploaded_file, sheet_name=sheet_name))
                
                if progress_placeholder:
                    progress_placeholder.info(f"📊 检测到 {total_rows:,} 行数据，正在加载...")
                
            except Exception as e:
                if progress_placeholder:
                    progress_placeholder.error(f"❌ 文件格式检查失败: {str(e)}")
                return pd.DataFrame()
            
            # 读取完整数据
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # 缓存数据
            st.session_state[cache_key] = df
            
            # 显示加载结果
            rows, cols = df.shape
            file_size = f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"
            
            if progress_placeholder:
                progress_placeholder.success(f"✅ 数据加载完成！{rows:,} 行 × {cols} 列，占用内存: {file_size}")
            
            return df
                
        except Exception as e:
            error_msg = f"❌ 数据加载失败: {str(e)}"
            if progress_placeholder:
                progress_placeholder.error(error_msg)
            else:
                st.error(error_msg)
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
    def clear_session_data(keys_to_clear: Optional[List[str]] = None):
        """
        清理Session数据
        
        Args:
            keys_to_clear: 要清理的键列表，如果为None则清理所有数据缓存
        """
        if keys_to_clear is None:
            keys_to_clear = [
                'sheet_confirmed', 'analysis_type', 'dimensions_confirmed', 
                'analysis_confirmed', 'selected_dimensions', 'analysis_name', 
                'data_loaded', 'loaded_data', 'need_data_loading', 'data_loading_progress',
                'selected_sheet', 'uploaded_file', 'dimension_configs',
                'data_loading_error', 'data_loading_triggered', 'loading_triggered'
            ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
                # 清理数据缓存（所有以data_开头的键）
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and key.startswith('data_'):
                del st.session_state[key]
        
        # 清理加载状态相关的键
        loading_keys = [key for key in st.session_state.keys() if 'loading' in str(key).lower() or 'current_sheet' in str(key).lower()]
        for key in loading_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # 清理分析配置相关的键
        config_keys = [
            key for key in st.session_state.keys() 
            if any(prefix in str(key) for prefix in ['装箱分析_', 'ABC分析_', '异常数据清洗_', '出库分析_', '入库分析_'])
        ]
        for key in config_keys:
            if key in st.session_state:
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
                'weight_column': st.session_state.get("装箱分析_weight_column"),
                'data_unit': st.session_state.get("装箱分析_data_unit", "cm"),
                'weight_unit': st.session_state.get("装箱分析_weight_unit", "kg"),
                'show_details': st.session_state.get("装箱分析_show_details", True),
                'container_length': st.session_state.get("container_length", 600),
                'container_width': st.session_state.get("container_width", 400),
                'container_height': st.session_state.get("container_height", 300),
                'container_weight_limit': st.session_state.get("container_weight_limit", 30),
                'use_dividers': st.session_state.get("use_dividers") == "是",
                'selected_dividers': st.session_state.get("selected_dividers", [])
            }
        
        # 异常数据清洗配置
        elif dimension == "异常数据清洗":
            config = {
                'all_conditions': st.session_state.get("异常数据清洗_all_conditions", []),
                'overall_logic': st.session_state.get("异常数据清洗_overall_logic", "OR")
            }
        
        # ABC分析配置
        elif dimension == "ABC分析":
            config = {
                'sku_column': st.session_state.get("ABC分析_sku_column"),
                'quantity_column': st.session_state.get("ABC分析_quantity_column"),
                'a_percentage': st.session_state.get("ABC分析_a_percentage", 80),
                'b_percentage': st.session_state.get("ABC分析_b_percentage", 15)
            }
        
        # 出库分析配置
        elif dimension == "出库分析":
            config = {
                '出库分析_date_column': st.session_state.get("出库分析_date_column"),
                '出库分析_order_data_type': st.session_state.get("出库分析_order_data_type"),
                '出库分析_order_id_column': st.session_state.get("出库分析_order_id_column"),
                '出库分析_order_count_column': st.session_state.get("出库分析_order_count_column"),
                '出库分析_sku_data_type': st.session_state.get("出库分析_sku_data_type"),
                '出库分析_sku_column': st.session_state.get("出库分析_sku_column"),
                '出库分析_sku_count_column': st.session_state.get("出库分析_sku_count_column"),
                '出库分析_item_data_type': st.session_state.get("出库分析_item_data_type"),
                '出库分析_item_column': st.session_state.get("出库分析_item_column"),
                '出库分析_item_count_column': st.session_state.get("出库分析_item_count_column"),
                '出库分析_start_date': st.session_state.get("出库分析_start_date"),
                '出库分析_end_date': st.session_state.get("出库分析_end_date")
            }
        
        # 入库分析配置
        elif dimension == "入库分析":
            config = {
                '入库分析_date_column': st.session_state.get("入库分析_date_column"),
                '入库分析_sku_data_type': st.session_state.get("入库分析_sku_data_type"),
                '入库分析_sku_column': st.session_state.get("入库分析_sku_column"),
                '入库分析_sku_count_column': st.session_state.get("入库分析_sku_count_column"),
                '入库分析_quantity_data_type': st.session_state.get("入库分析_quantity_data_type"),
                '入库分析_quantity_column': st.session_state.get("入库分析_quantity_column"),
                '入库分析_quantity_count_column': st.session_state.get("入库分析_quantity_count_column"),
                '入库分析_start_date': st.session_state.get("入库分析_start_date"),
                '入库分析_end_date': st.session_state.get("入库分析_end_date")
            }
        

        
        # 订单结构分析配置
        elif dimension == "订单结构分析":
            config = {
                '订单结构分析_order_column': st.session_state.get("订单结构分析_order_column"),
                '订单结构分析_item_column': st.session_state.get("订单结构分析_item_column"),
                '订单结构分析_quantity_column': st.session_state.get("订单结构分析_quantity_column"),
                '订单结构分析_amount_column': st.session_state.get("订单结构分析_amount_column")
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