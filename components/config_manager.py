# -*- coding: utf-8 -*-
"""
配置管理组件 - 简化版，只保留保存功能
"""

import streamlit as st
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
from utils.config_database import config_db

def render_config_manager():
    """渲染配置管理界面 - 简化版，只保留保存功能"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 保存配置")
    
    # 保存当前配置
    save_current_config()

def save_current_config():
    """保存当前配置"""
    # 检查是否有可保存的配置
    if not check_saveable_config():
        st.sidebar.info("📝 请先完成配置才能保存")
        return
    
    config_name = st.sidebar.text_input(
        "🏷️ 配置名称", 
        placeholder="输入配置名称",
        value=generate_default_config_name()
    )
    
    if st.sidebar.button("💾 保存配置"):
        if config_name.strip():
            save_configuration(config_name.strip())
            st.sidebar.success("✅ 配置已保存！")
        else:
            st.sidebar.error("⚠️ 请输入配置名称")

def check_saveable_config() -> bool:
    """检查当前是否有可保存的配置"""
    required_keys = [
        'analysis_type', 'analysis_name', 
        'selected_dimensions', 'dimension_configs'
    ]
    
    for key in required_keys:
        if key not in st.session_state or not st.session_state.get(key):
            return False
    
    return True

def generate_default_config_name() -> str:
    """生成默认配置名称"""
    if not check_saveable_config():
        return ""
    
    analysis_name = st.session_state.get('analysis_name', '分析')
    file_name = st.session_state.get('uploaded_file_name', '')
    
    if file_name:
        # 提取文件名（不含扩展名）
        base_name = file_name.split('.')[0] if '.' in file_name else file_name
        return f"{analysis_name}_{base_name}_{datetime.now().strftime('%m%d_%H%M')}"
    else:
        return f"{analysis_name}_{datetime.now().strftime('%m%d_%H%M')}"

def save_configuration(config_name: str):
    """保存配置到数据库"""
    try:
        # 获取容器配置
        container_config = {}
        if st.session_state.get('analysis_type') == '装箱分析':
            container_config = {
                'container_length': st.session_state.get('container_length'),
                'container_width': st.session_state.get('container_width'),
                'container_height': st.session_state.get('container_height'),
                'container_weight_limit': st.session_state.get('container_weight_limit'),
                'selected_container_size': st.session_state.get('selected_container_size'),
                'selected_container_weight_limit': st.session_state.get('selected_container_weight_limit'),
                'use_dividers': st.session_state.get('use_dividers') == "是",
                'selected_dividers': st.session_state.get('selected_dividers', [])
            }
        
        # 处理维度配置中的日期对象
        dimension_configs = st.session_state.get('dimension_configs', {}).copy()
        for dimension, config in dimension_configs.items():
            if isinstance(config, dict):
                for key, value in config.items():
                    # 将日期对象转换为字符串
                    if hasattr(value, 'strftime'):  # 检查是否是日期对象
                        dimension_configs[dimension][key] = value.strftime('%Y-%m-%d')
        
        # 保存到数据库
        config_id = config_db.save_config(
            config_name=config_name,
            file_name=st.session_state.get('uploaded_file_name'),
            sheet_name=st.session_state.get('selected_sheet'),
            analysis_type=st.session_state.get('analysis_type'),
            analysis_name=st.session_state.get('analysis_name'),
            selected_dimensions=st.session_state.get('selected_dimensions'),
            dimension_configs=dimension_configs,
            container_config=container_config
        )
        
        # 记录保存信息
        st.session_state['last_saved_config_id'] = config_id
        st.session_state['last_saved_config_name'] = config_name
        
        return config_id
        
    except Exception as e:
        st.error(f"保存配置失败: {str(e)}")
        return None

def load_configuration(config_id: int):
    """从数据库加载配置"""
    try:
        config = config_db.load_config(config_id)
        
        if not config:
            st.error("配置不存在")
            return False
        
        # 恢复基本信息
        st.session_state['analysis_type'] = config['analysis_type']
        st.session_state['analysis_name'] = config['analysis_name']
        st.session_state['selected_dimensions'] = config['selected_dimensions']
        st.session_state['dimension_configs'] = config['dimension_configs']
        
        # 恢复容器配置
        if config['container_config']:
            for key, value in config['container_config'].items():
                if value is not None:
                    st.session_state[key] = value
        
        # 恢复维度配置到session_state
        restore_dimension_configs_to_session(config['dimension_configs'])
        
        # 设置正确的状态：如果有文件，直接进入配置参数步骤；如果没有文件，让用户上传文件
        if st.session_state.get('uploaded_file') and st.session_state.get('selected_sheet'):
            # 如果已有文件和sheet，直接进入配置参数步骤
            st.session_state['sheet_confirmed'] = True
            st.session_state['dimensions_confirmed'] = True
            # 清除分析确认状态，让用户重新确认配置
            if 'analysis_confirmed' in st.session_state:
                del st.session_state['analysis_confirmed']
        else:
            # 如果没有文件，清除相关状态，让用户重新上传
            for key in ['sheet_confirmed', 'dimensions_confirmed', 'analysis_confirmed']:
                if key in st.session_state:
                    del st.session_state[key]
        

        
        # 显示成功信息
        st.success(f"✅ 已加载配置: {config['config_name']}")
        st.info(f"📄 原文件: {config['file_name'] or '未知'} | 📋 工作表: {config['sheet_name'] or '未知'}")
        
        # 根据当前状态给出不同的提示
        if st.session_state.get('uploaded_file'):
            st.info("🎯 配置已应用，您可以直接查看配置参数或开始分析")
        else:
            st.warning("⚠️ 请上传数据文件以应用此配置")
        
        return True
        
    except Exception as e:
        st.error(f"加载配置失败: {str(e)}")
        return False

def restore_dimension_configs_to_session(dimension_configs: Dict[str, Any]):
    """将维度配置恢复到session_state中"""
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    
    # 先清除可能存在的装箱分析配置键，避免widget冲突
    packing_keys = [
        "装箱分析_length_column", "装箱分析_width_column", 
        "装箱分析_height_column", "装箱分析_inventory_column",
        "装箱分析_weight_column", "装箱分析_data_unit", 
        "装箱分析_weight_unit", "装箱分析_show_details"
    ]
    for key in packing_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 清除异常数据清洗相关的配置键
    cleaning_keys = [
        "异常数据清洗_all_conditions", "异常数据清洗_overall_logic",
        "异常数据清洗_overall_group_logic", "异常数据清洗_group_count"
    ]
    for key in cleaning_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 清除出库分析相关的配置键
    outbound_keys = [
        "出库分析_date_column", "出库分析_order_data_type", "出库分析_order_id_column",
        "出库分析_order_count_column", "出库分析_sku_data_type", "出库分析_sku_column",
        "出库分析_sku_count_column", "出库分析_item_data_type", "出库分析_item_column",
        "出库分析_item_count_column", "出库分析_start_date", "出库分析_end_date"
    ]
    for key in outbound_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 清除入库分析相关的配置键
    inbound_keys = [
        "入库分析_date_column", "入库分析_sku_data_type", "入库分析_sku_column",
        "入库分析_sku_count_column", "入库分析_quantity_data_type", "入库分析_quantity_column",
        "入库分析_quantity_count_column", "入库分析_start_date", "入库分析_end_date"
    ]
    for key in inbound_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 清除ABC分析相关的配置键
    abc_keys = [
        "ABC分析_sku_column", "ABC分析_quantity_column", 
        "ABC分析_a_percentage", "ABC分析_b_percentage"
    ]
    for key in abc_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 清除所有条件相关的键
    for key in list(st.session_state.keys()):
        if isinstance(key, str) and key.startswith("condition_") and "异常数据清洗" in key:
            del st.session_state[key]
    
    # 遍历每个维度的配置
    for dimension, config in dimension_configs.items():
        if dimension == '装箱分析':
            # 恢复装箱分析的配置
            if config.get('length_column'):
                st.session_state["装箱分析_length_column"] = config.get('length_column')
            if config.get('width_column'):
                st.session_state["装箱分析_width_column"] = config.get('width_column')
            if config.get('height_column'):
                st.session_state["装箱分析_height_column"] = config.get('height_column')
            if config.get('inventory_column'):
                st.session_state["装箱分析_inventory_column"] = config.get('inventory_column')
            if config.get('weight_column'):
                st.session_state["装箱分析_weight_column"] = config.get('weight_column')
            # 为数据单位和详细显示设置值，避免widget冲突
            st.session_state["装箱分析_data_unit"] = config.get('data_unit', 'cm')
            st.session_state["装箱分析_weight_unit"] = config.get('weight_unit', 'kg')
            st.session_state["装箱分析_show_details"] = config.get('show_details', True)
        elif dimension == '出库分析':
            # 恢复出库分析的配置 - 修复方式，恢复所有已保存的值（包括"无数据"）
            for key in ['出库分析_date_column', '出库分析_order_data_type', 
                       '出库分析_order_id_column', '出库分析_order_count_column',
                       '出库分析_sku_data_type', '出库分析_sku_column', 
                       '出库分析_sku_count_column', '出库分析_item_data_type',
                       '出库分析_item_column', '出库分析_item_count_column']:
                if key in config:  # 只要配置中存在这个键，就恢复（包括"无数据"值）
                    st.session_state[key] = config[key]
            
            # 特殊处理日期配置
            for date_key in ['出库分析_start_date', '出库分析_end_date']:
                if config.get(date_key):
                    date_value = config.get(date_key)
                    if isinstance(date_value, str):
                        from datetime import datetime
                        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                    st.session_state[date_key] = date_value
        elif dimension == '入库分析':
            # 恢复入库分析的配置 - 修复方式，恢复所有已保存的值（包括"无数据"）
            for key in ['入库分析_date_column', '入库分析_sku_data_type', 
                       '入库分析_sku_column', '入库分析_sku_count_column',
                       '入库分析_quantity_data_type', '入库分析_quantity_column', 
                       '入库分析_quantity_count_column']:
                if key in config:  # 只要配置中存在这个键，就恢复（包括"无数据"值）
                    st.session_state[key] = config[key]
            
            # 特殊处理日期配置
            for date_key in ['入库分析_start_date', '入库分析_end_date']:
                if config.get(date_key):
                    date_value = config.get(date_key)
                    if isinstance(date_value, str):
                        from datetime import datetime
                        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                    st.session_state[date_key] = date_value
        elif dimension == 'ABC分析':
            # 恢复ABC分析的配置
            for key in ['sku_column', 'quantity_column', 'a_percentage', 'b_percentage']:
                config_key = f"ABC分析_{key}"
                if key in config:  # 从配置中恢复值
                    st.session_state[config_key] = config[key]
        elif dimension == '异常数据清洗':
            # 恢复异常数据清洗的配置
            st.session_state["异常数据清洗_all_conditions"] = config.get('all_conditions', [])
            st.session_state["异常数据清洗_overall_logic"] = config.get('overall_logic', 'OR')
            st.session_state["异常数据清洗_overall_group_logic"] = config.get('overall_logic', 'OR')
            
            # 恢复条件组的详细配置
            all_conditions = config.get('all_conditions', [])
            if all_conditions:
                st.session_state["异常数据清洗_group_count"] = len(all_conditions)
                for group_idx, group_conditions in enumerate(all_conditions, 1):
                    if group_conditions:
                        st.session_state[f"condition_count_异常数据清洗_{group_idx}"] = len(group_conditions)
                        for cond_idx, condition in enumerate(group_conditions):
                            prefix = f"condition_异常数据清洗_{group_idx}_{cond_idx}"
                            st.session_state[f"{prefix}_columns"] = condition.get('columns', [])
                            operator = condition.get('operator', '>')
                            st.session_state[f"{prefix}_operator"] = operator
                            value = condition.get('value', 0)
                            
                            # 根据操作符类型，恢复对应的值键
                            if operator in ["in_range", "not_in_range"] and isinstance(value, list) and len(value) == 2:
                                st.session_state[f"{prefix}_min"] = value[0]
                                st.session_state[f"{prefix}_max"] = value[1]
                                st.session_state[f"{prefix}_type"] = "整数" if isinstance(value[0], int) else "小数"
                            elif operator in ["contains", "not_contains"]:
                                st.session_state[f"{prefix}_text"] = str(value)
                            else:
                                st.session_state[f"{prefix}_value"] = value
                                st.session_state[f"{prefix}_type"] = "整数" if isinstance(value, int) else "小数"

def render_sidebar_config_panel():
    """渲染侧边栏配置面板"""
    # 配置管理
    render_config_manager() 