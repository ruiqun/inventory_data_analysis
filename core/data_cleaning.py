import pandas as pd
import numpy as np

class DataCleaning:
    """数据清洗类 - 包装现有的数据清洗功能"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化数据清洗器
        
        Args:
            df: 要清洗的数据框
        """
        self.df = df.copy()
        self.original_df = df.copy()
    
    def clean_all_data(self):
        """
        执行所有数据清洗步骤
        
        Returns:
            tuple: (清洗后的数据框, 清洗统计信息)
        """
        cleaned_df = clean_dataframe(self.df)
        
        # 基础清洗统计
        stats = {
            'original_rows': len(self.df),
            'cleaned_rows': len(cleaned_df),
            'columns': len(cleaned_df.columns)
        }
        
        return cleaned_df, stats

def read_and_clean(file, sheet_name=None):
    """
    读取Excel指定Sheet并进行基础数据清洗。
    :param file: 上传的文件对象
    :param sheet_name: Sheet名称
    :return: 清洗后的DataFrame
    """
    df = pd.read_excel(file, sheet_name=sheet_name)
    
    # 数据清洗逻辑
    df = clean_dataframe(df)
    return df

def clean_dataframe(df):
    """
    清洗DataFrame，处理数据类型问题
    :param df: 原始DataFrame
    :return: 清洗后的DataFrame
    """
    # 创建副本避免修改原数据
    df_cleaned = df.copy()
    
    # 处理每一列的数据类型问题
    for col in df_cleaned.columns:
        # 将所有列转换为字符串，避免混合数据类型问题
        df_cleaned[col] = df_cleaned[col].astype(str)
        
        # 将 'nan' 字符串替换为空字符串，更美观
        df_cleaned[col] = df_cleaned[col].replace('nan', '')
    
    return df_cleaned

def apply_condition(df, column, operator, value):
    """
    应用单个条件到DataFrame
    :param df: DataFrame
    :param column: 列名
    :param operator: 运算符
    :param value: 值或值列表
    :return: 布尔索引
    """
    # 尝试将列转换为数值类型（用于数学运算）
    try:
        col_data = pd.to_numeric(df[column], errors='coerce')
        is_numeric = True
    except:
        col_data = df[column].astype(str)
        is_numeric = False
    
    if operator == ">" and is_numeric:
        return col_data > float(value)
    elif operator == ">=" and is_numeric:
        return col_data >= float(value)
    elif operator == "<" and is_numeric:
        return col_data < float(value)
    elif operator == "<=" and is_numeric:
        return col_data <= float(value)
    elif operator == "==":
        if is_numeric:
            return col_data == float(value)
        else:
            return col_data == str(value)
    elif operator == "!=":
        if is_numeric:
            return col_data != float(value)
        else:
            return col_data != str(value)
    elif operator == "in_range" and is_numeric and isinstance(value, list):
        return (col_data >= float(value[0])) & (col_data <= float(value[1]))
    elif operator == "not_in_range" and is_numeric and isinstance(value, list):
        return ~((col_data >= float(value[0])) & (col_data <= float(value[1])))
    elif operator == "contains":
        return col_data.str.contains(str(value), case=False, na=False)
    elif operator == "not_contains":
        return ~col_data.str.contains(str(value), case=False, na=False)
    else:
        # 默认返回False
        return pd.Series([False] * len(df), index=df.index)

def apply_condition_group(df, conditions):
    """
    应用一组条件（组内为AND关系）
    :param df: DataFrame
    :param conditions: 条件列表
    :return: 布尔索引
    """
    if not conditions:
        return pd.Series([False] * len(df), index=df.index)
    
    # 第一个条件
    result = apply_condition(df, conditions[0]['column'], 
                           conditions[0]['operator'], conditions[0]['value'])
    
    # 应用后续条件
    for i, condition in enumerate(conditions[1:], 1):
        current_condition = apply_condition(df, condition['column'], 
                                          condition['operator'], condition['value'])
        
        # 获取前一个条件的逻辑运算符
        prev_logic = conditions[i-1]['logic_op']
        
        if prev_logic == "AND":
            result = result & current_condition
        elif prev_logic == "OR":
            result = result | current_condition
    
    return result

def apply_multiple_condition_groups(df, all_groups_conditions):
    """
    应用多个条件组（组间为OR关系）
    :param df: DataFrame
    :param all_groups_conditions: 所有条件组的列表
    :return: 布尔索引
    """
    if not all_groups_conditions:
        return pd.Series([False] * len(df), index=df.index)
    
    # 第一个条件组
    result = apply_condition_group(df, all_groups_conditions[0])
    
    # 应用后续条件组（OR关系）
    for group_conditions in all_groups_conditions[1:]:
        group_result = apply_condition_group(df, group_conditions)
        result = result | group_result
    
    return result

def advanced_data_cleaning(df, target_columns, all_groups_conditions, action="删除"):
    """
    执行高级数据清洗
    :param df: DataFrame
    :param target_columns: 目标列
    :param all_groups_conditions: 所有条件组
    :param action: 处理方式（删除/标记异常/导出到新文件）
    :return: 处理后的DataFrame或异常数据
    """
    if not all_groups_conditions or not target_columns:
        return df, pd.DataFrame()
    
    # 应用所有条件
    condition_mask = apply_multiple_condition_groups(df, all_groups_conditions)
    
    # 获取符合条件的异常数据
    abnormal_data = df[condition_mask].copy()
    
    if action == "删除":
        # 删除符合条件的数据
        cleaned_df = df[~condition_mask].copy()
        return cleaned_df, abnormal_data
    
    elif action == "标记异常":
        # 标记异常数据
        df_marked = df.copy()
        df_marked['异常标记'] = condition_mask
        return df_marked, abnormal_data
    
    elif action == "导出到新文件":
        # 保留原数据，只返回异常数据用于导出
        return df, abnormal_data
    
    return df, abnormal_data

def basic_data_cleaning(df, basic_rules):
    """
    执行基础数据清洗
    :param df: DataFrame
    :param basic_rules: 基础清洗规则列表
    :return: 清洗后的DataFrame
    """
    df_cleaned = df.copy()
    
    if "删除空值" in basic_rules:
        df_cleaned = df_cleaned.dropna()
    
    if "删除重复值" in basic_rules:
        df_cleaned = df_cleaned.drop_duplicates()
    
    if "标准化格式" in basic_rules:
        # 去除首尾空格
        for col in df_cleaned.select_dtypes(include=['object']).columns:
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
    
    if "数据类型转换" in basic_rules:
        # 尝试将看起来像数字的列转换为数值类型
        for col in df_cleaned.columns:
            try:
                # 尝试转换为数值类型
                numeric_col = pd.to_numeric(df_cleaned[col], errors='coerce')
                # 如果转换成功的比例大于80%，则认为是数值列
                if numeric_col.notna().sum() / len(df_cleaned) > 0.8:
                    df_cleaned[col] = numeric_col
            except:
                continue
    
    return df_cleaned

def detect_abnormal(df):
    """
    检测异常数据（如库存为负等），返回异常数据DataFrame。
    :param df: DataFrame
    :return: 异常数据DataFrame
    """
    # TODO: 实现具体异常检测逻辑
    abnormal = pd.DataFrame()  # 占位
    return abnormal 