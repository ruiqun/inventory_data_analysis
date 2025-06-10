# -*- coding: utf-8 -*-
"""
创维数据分析系统 - 主应用入口（重构版）
模块化架构，提高代码可维护性和扩展性
"""

import streamlit as st
import pandas as pd
import sys
import os
from typing import Dict, List, Any

# 添加项目路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入自定义模块
from config import *
from utils import DataUtils, SessionStateManager, FileUtils
from components.ui_components import UIComponents
from components.config_manager import render_sidebar_config_panel
from core.analysis_engine import AnalysisEngine, DimensionConfigManager
from modules.report_generator import AnalysisReport

def main():
    """主应用函数"""
    # 设置页面配置
    st.set_page_config(
        page_title=LANG["title"],
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化Session状态
    SessionStateManager.initialize_session_state()
    
    # 渲染应用界面
    render_app()

def render_app():
    """渲染应用界面"""
    # 页面标题
    st.title(f"📊 {LANG['title']}")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        render_sidebar()
    
    # 主内容区域
    render_main_content()

def render_sidebar():
    """渲染侧边栏"""
    st.header("📋 操作面板")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        LANG["upload"],
        type=['xlsx', 'xls'],
        help="请上传Excel格式的数据文件"
    )
    
    if uploaded_file:
        # 显示文件信息
        file_size = f"{uploaded_file.size / 1024:.1f} KB"
        st.success(f"✅ 文件已上传: {uploaded_file.name}")
        st.caption(f"文件大小: {file_size}")
        
        # 处理文件上传
        handle_file_upload(uploaded_file)
        
        # 存储文件名用于配置保存
        st.session_state['uploaded_file_name'] = uploaded_file.name
    else:
        st.info("👆 请先上传Excel数据文件")
        
    # 回上一步和重置按钮
    st.markdown("---")
    
    # 显示当前步骤状态
    current_step = get_current_step()
    if current_step > 1:
        st.write(f"📍 当前：第{current_step}步")
        if st.button("⬅️ 回上一步", type="secondary", use_container_width=True):
            go_back_one_step()
    
    UIComponents.render_reset_button()
    
    # 配置管理面板
    render_sidebar_config_panel()

def render_main_content():
    """渲染主内容区域"""
    
    if not st.session_state.get('uploaded_file'):
        # 步骤1: 等待文件上传
        st.info("👈 请在左侧上传Excel文件开始分析")
        
    elif not st.session_state.get('sheet_confirmed'):
        # 选择数据源（Sheet）
        handle_sheet_selection()
        
    elif not st.session_state.get('analysis_type') or st.session_state.get('manual_back_to_step2'):
        # 步骤2: 选择分析类型（同时后台加载数据）
        if st.session_state.get('manual_back_to_step2'):
            # 清除临时回退标记
            del st.session_state.manual_back_to_step2
        handle_analysis_type_selection_with_background_loading()
        
    elif not st.session_state.get('dimensions_confirmed'):
        # 步骤3: 数据预览，选择分析维度
        if 'uploaded_file' in st.session_state:
            handle_dimension_selection()
        
    elif not st.session_state.get('analysis_confirmed'):
        # 步骤4: 配置分析参数（包括前置处理、出入库分析和其他分析）
        if 'uploaded_file' in st.session_state:
            handle_analysis_configuration()
            
    else:
        # 步骤5: 执行分析
        if 'uploaded_file' in st.session_state:
            execute_analysis()

def handle_file_upload(uploaded_file):
    """处理文件上传"""
    st.session_state.uploaded_file = uploaded_file
    # 文件上传后自动进入sheet选择步骤，不等待分析类型选择

def handle_sheet_selection():
    """处理Sheet选择"""
    uploaded_file = st.session_state.get('uploaded_file')
    if uploaded_file:
        sheet = UIComponents.render_sheet_selection_simple(uploaded_file)

def handle_analysis_type_selection_with_background_loading():
    """处理分析类型选择，同时后台加载数据"""
    
    # 显示分析类型选择界面（内部包含数据加载逻辑）
    UIComponents.render_analysis_type_selection_with_loading()



def handle_dimension_selection():
    """处理数据预览和分析维度选择"""
    analysis_type = st.session_state.get('analysis_type')
    analysis_name = st.session_state.get('analysis_name')
    
    if analysis_type and analysis_name:
        # 使用已加载的数据
        df = st.session_state.get('loaded_data')
        
        if df is not None and not df.empty:
            # 显示数据预览
            st.subheader("📊 第三步：数据预览")
            UIComponents.render_data_preview(df)
            
            # 选择分析维度
            selected_dimensions = UIComponents.render_dimension_selection(analysis_type, analysis_name)
            
            # 检查数据是否加载完成
            if not st.session_state.get('data_loaded', False):
                st.warning("⏳ 数据仍在加载中，请稍候...")
                st.button(LANG["next_step"], type="primary", disabled=True)
            else:
                # 为所有分析类型显示确认按钮
                st.markdown("---")
                if selected_dimensions:
                    st.success(f"✅ 已选择 {len(selected_dimensions)} 个分析维度")
                    if st.button(LANG["next_step"], type="primary", use_container_width=True):
                        # 过滤掉已删除的EIQ分析，防止历史数据引起错误
                        filtered_dimensions = [dim for dim in selected_dimensions 
                                             if dim in ANALYSIS_DIMENSIONS or dim in PREPROCESSING_DIMENSIONS]
                        st.session_state.selected_dimensions = filtered_dimensions
                        st.session_state.dimensions_confirmed = True
                        # 标记需要滚动到第四步
                        st.session_state.scroll_to_step4 = True
                        
                        # 添加自动滚动到第四步的逻辑
                        st.markdown("""
                        <script>
                        setTimeout(function() {
                            // 查找第四步标题元素
                            const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                            let targetElement = null;
                            for (let element of elements) {
                                if (element.textContent.includes('第四步')) {
                                    targetElement = element;
                                    break;
                                }
                            }
                            
                            if (targetElement) {
                                // 滚动到目标位置，留80px顶部空间
                                const offsetTop = targetElement.offsetTop - 80;
                                window.scrollTo(0, offsetTop);
                            } else {
                                // 回退到顶部滚动
                                window.scrollTo(0, 0);
                            }
                        }, 200);
                        </script>
                        """, unsafe_allow_html=True)
                        
                        st.rerun()
                else:
                    st.warning("⚠️ 请至少选择一个分析维度")
                    st.button(LANG["next_step"], type="primary", disabled=True)
        else:
            st.error("❌ 数据未正确加载，请重新选择工作表")
            if st.button("⬅️ 重新选择工作表", type="secondary"):
                st.session_state.sheet_confirmed = False
                st.session_state.selected_sheet = None
                st.session_state.need_data_loading = False
                st.session_state.data_loaded = False
                st.rerun()

def handle_analysis_configuration():
    """处理所有分析配置（合并第四步和第五步）"""
    st.subheader("⚙️ 第四步：配置分析参数")
    st.markdown("<div id='step4'></div>", unsafe_allow_html=True)
    
    # 检查是否需要滚动到第四步
    if st.session_state.get('scroll_to_step4', False):
        st.session_state.scroll_to_step4 = False  # 清除标记
        st.markdown("""
        <script>
        setTimeout(function() {
            var target = document.getElementById('step4');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    df = st.session_state.get('loaded_data')
    
    if not selected_dimensions:
        st.error("❌ 未找到选择的分析维度")
        return
    
    # 使用已加载的数据
    if df is None or df.empty:
        st.error("❌ 数据未正确加载")
        return
    
    # 获取列名
    columns = list(df.columns)
    
    # 处理所有配置
    all_configs_valid = True
    dimension_configs = {}
    
    # 1. 首先处理前置处理步骤
    preprocessing_dimensions = [dim for dim in selected_dimensions if dim in PREPROCESSING_DIMENSIONS]
    if preprocessing_dimensions:
        st.write("## 🧹 前置数据处理配置")
        
        for dimension in preprocessing_dimensions:
            st.write(f"### {PREPROCESSING_DIMENSIONS[dimension]['icon']} {dimension}")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if dimension == "异常数据清洗":
                    config_valid = UIComponents.render_data_cleaning_config(columns)
                    if config_valid:
                        config = SessionStateManager.get_analysis_config(dimension)
                        dimension_configs[dimension] = config
                    else:
                        all_configs_valid = False
                elif dimension == "容器选择":
                    st.info("📦 容器选择已在前置步骤配置完成")
                    config = {
                        'container_length': st.session_state.get("container_length", 600),
                        'container_width': st.session_state.get("container_width", 400),
                        'container_height': st.session_state.get("container_height", 300),
                        'container_weight_limit': st.session_state.get("container_weight_limit", 30),
                        'use_dividers': st.session_state.get("use_dividers") == "是",
                        'selected_dividers': st.session_state.get("selected_dividers", [])
                    }
                    dimension_configs[dimension] = config
            
            with col2:
                if dimension == "异常数据清洗" and config_valid:
                    st.success("✅ **数据清洗配置完成**")
                elif dimension == "容器选择":
                    st.success("✅ **容器选择配置完成**")

    # 2. 然后处理出入库分析配置
    inout_dimensions = [dim for dim in selected_dimensions if dim in ["出库分析", "入库分析"]]
    if inout_dimensions:
        st.write("## 📈📥 出入库分析配置")
        
        for dimension in inout_dimensions:
            st.write(f"### {ANALYSIS_DIMENSIONS[dimension]['icon']} {dimension}")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if dimension == "出库分析":
                    config_valid = UIComponents.render_outbound_analysis_config(columns)
                    if config_valid:
                        config = SessionStateManager.get_analysis_config(dimension)
                        dimension_configs[dimension] = config
                    else:
                        all_configs_valid = False
                elif dimension == "入库分析":
                    config_valid = UIComponents.render_inbound_analysis_config(columns)
                    if config_valid:
                        config = SessionStateManager.get_analysis_config(dimension)
                        dimension_configs[dimension] = config
                    else:
                        all_configs_valid = False
            
            with col2:
                if config_valid:
                    st.success("✅ **分析配置完成**")

    # 3. 最后处理其他分析配置
    other_dimensions = [dim for dim in selected_dimensions 
                      if dim not in PREPROCESSING_DIMENSIONS and dim not in ["出库分析", "入库分析"]
                      and dim in ANALYSIS_DIMENSIONS]  # 添加安全检查，只处理存在的维度
    if other_dimensions:
        st.write("## 📊 其他分析配置")
        
        for dimension in other_dimensions:
            st.write(f"### {ANALYSIS_DIMENSIONS[dimension]['icon']} {dimension}")
            
            # 根据维度类型渲染配置界面
            if dimension == "装箱分析":
                config_valid = UIComponents.render_packing_analysis_config(columns)
                if config_valid:
                    config = SessionStateManager.get_analysis_config(dimension)
                    dimension_configs[dimension] = config
                else:
                    all_configs_valid = False
            elif dimension == "ABC分析":
                config_valid = UIComponents.render_abc_analysis_config(columns)
                if config_valid:
                    config = SessionStateManager.get_analysis_config(dimension)
                    dimension_configs[dimension] = config
                else:
                    all_configs_valid = False

            elif dimension == "订单结构分析":
                config_valid = UIComponents.render_order_structure_analysis_config(columns)
                if config_valid:
                    config = SessionStateManager.get_analysis_config(dimension)
                    dimension_configs[dimension] = config
                else:
                    all_configs_valid = False
            else:
                # 其他维度的配置界面
                st.info(f"💡 {dimension} 配置界面待完善...")
                # 暂时使用默认配置
                config = DimensionConfigManager.get_default_config(dimension)
                dimension_configs[dimension] = config
    
    # 显示开始分析按钮
    if all_configs_valid:
        st.markdown("---")
        if st.button(LANG["start_analysis"], type="primary", use_container_width=True):
            st.session_state.dimension_configs = dimension_configs
            st.session_state.analysis_confirmed = True
            # 标记需要滚动到第五步
            st.session_state.scroll_to_step5 = True
            
            # 自动保存当前配置
            try:
                from components.config_manager import save_configuration, generate_default_config_name
                auto_config_name = f"自动保存_{generate_default_config_name()}"
                save_configuration(auto_config_name)
                st.toast("💾 配置已自动保存", icon="✅")
            except Exception as e:
                pass  # 静默失败，不影响主流程
            
            st.rerun()
    else:
        st.warning("⚠️ 请完成所有必需的配置项")

def execute_analysis():
    """执行分析"""
    st.subheader("🚀 第五步：正在执行分析...")
    st.markdown("<div id='step5'></div>", unsafe_allow_html=True)
    
    # 检查是否需要滚动到第五步
    if st.session_state.get('scroll_to_step5', False):
        st.session_state.scroll_to_step5 = False  # 清除标记
        st.markdown("""
        <script>
        setTimeout(function() {
            var target = document.getElementById('step5');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    # 获取数据和配置
    uploaded_file = st.session_state.get('uploaded_file')
    selected_sheet = st.session_state.get('selected_sheet')
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    dimension_configs = st.session_state.get('dimension_configs', {})
    
    # 加载数据
    if selected_sheet is None:
        st.error("❌ 未找到选择的工作表")
        return
    
    sheet_name = str(selected_sheet)
    df = load_data_cached(uploaded_file, sheet_name)  # 使用快速缓存函数，无UI干扰
    if df.empty:
        st.error("❌ 数据加载失败")
        return
    
    # 创建分析引擎
    analysis_engine = AnalysisEngine(df)
    
    # 分离前置处理和分析步骤（添加安全检查，确保维度存在）
    preprocessing_steps = [dim for dim in selected_dimensions if dim in PREPROCESSING_DIMENSIONS]
    analysis_steps = [dim for dim in selected_dimensions if dim in ANALYSIS_DIMENSIONS]
    
    try:
        # 执行前置处理
        if preprocessing_steps:
            st.write("## 🧹 前置数据处理")
            
            for step in preprocessing_steps:
                st.write(f"### {PREPROCESSING_DIMENSIONS[step]['icon']} {step}")
                
                # 获取配置
                config = dimension_configs.get(step, {})
                
                # 执行前置处理
                success = analysis_engine.execute_preprocessing_step(step, config)
                if not success:
                    st.warning(f"⚠️ {step} 处理失败，继续执行其他步骤...")
                    continue
                
                st.write("---")
        
        # 执行分析步骤
        if analysis_steps:
            st.write("## 📊 数据分析")
            
            for dimension in analysis_steps:
                st.write(f"### {ANALYSIS_DIMENSIONS[dimension]['icon']} {dimension}")
                
                # 获取配置
                config = dimension_configs.get(dimension, {})
                
                # 执行分析
                success = analysis_engine.execute_analysis_dimension(dimension, config)
                if not success:
                    st.warning(f"⚠️ {dimension} 分析失败，继续执行其他分析...")
                    continue
                
                st.write("---")
        
        # 显示分析摘要
        render_analysis_summary(analysis_engine)
        
    except Exception as e:
        st.error(f"❌ 分析过程中发生错误: {str(e)}")
        st.exception(e)

def render_analysis_summary(analysis_engine: AnalysisEngine):
    """渲染分析摘要"""
    st.write("## 📋 分析摘要")
    
    summary = analysis_engine.get_analysis_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("执行维度数", summary["total_dimensions"])
    with col2:
        st.metric("数据行数", f"{summary['data_info']['current_rows']:,}")
    with col3:
        st.metric("数据列数", summary['data_info']['columns'])
    
    # 显示执行的步骤
    if summary["executed_steps"]:
        st.write("**已完成的分析步骤：**")
        for i, step in enumerate(summary["executed_steps"], 1):
            st.write(f"{i}. ✅ {step}")
    
    # 添加PDF报告生成按钮
    st.markdown("---")
    if st.button("📄 生成PDF报告", help="生成包含分析结果的PDF报告", type="primary"):
        generate_pdf_report(analysis_engine)



def generate_pdf_report(analysis_engine: AnalysisEngine):
    """生成PDF报告"""
    try:
        st.info("📄 PDF报告生成功能开发中...")
        
        # TODO: 实现PDF报告生成
        # 可以使用report_generator.py中的功能
        
    except Exception as e:
        st.error(f"❌ PDF报告生成失败: {str(e)}")

def get_current_step():
    """获取当前步骤"""
    if not st.session_state.get('uploaded_file'):
        return 1  # 等待文件上传
    elif not st.session_state.get('sheet_confirmed'):
        return 1  # 选择数据源
    elif not st.session_state.get('analysis_type'):
        return 2  # 选择分析类型
    elif not st.session_state.get('dimensions_confirmed'):
        return 3  # 选择分析维度
    elif not st.session_state.get('analysis_confirmed'):
        return 4  # 配置分析参数
    else:
        return 5  # 执行分析

def go_back_one_step():
    """回上一步 - 保持已有选择"""
    # 根据当前状态判断回退到哪一步
    if st.session_state.get('analysis_confirmed'):
        # 如果在第六步（执行分析），回退到第五步
        st.session_state.analysis_confirmed = False
        # 保持dimension_configs，用户可能想修改配置
        # BUGFIX: 显式地将保存的配置恢复，以便UI组件可以加载它们
        if 'dimension_configs' in st.session_state:
            # 先清除可能存在的widget键，避免冲突
            packing_keys = [
                "装箱分析_length_column", "装箱分析_width_column", 
                "装箱分析_height_column", "装箱分析_inventory_column",
                "装箱分析_weight_column", "装箱分析_data_unit", 
                "装箱分析_weight_unit", "装箱分析_show_details"
            ]
            for key in packing_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            for dimension, config in st.session_state.dimension_configs.items():
                # 根据维度类型，恢复相应的session_state键值
                if dimension == "装箱分析":
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
                elif dimension == "异常数据清洗":
                    # 恢复异常数据清洗的配置
                    st.session_state["异常数据清洗_all_conditions"] = config.get('all_conditions', [])
                    st.session_state["异常数据清洗_overall_logic"] = config.get('overall_logic', 'OR')
                    st.session_state["异常数据清洗_overall_group_logic"] = config.get('overall_logic', 'OR')
                    st.session_state["异常数据清洗_action"] = config.get('action', '删除')
                    
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
                                        # 文本操作符不需要type键，但UI会创建placeholder
                                    else:
                                        st.session_state[f"{prefix}_value"] = value
                                        st.session_state[f"{prefix}_type"] = "整数" if isinstance(value, int) else "小数"
        st.success("✅ 已回退到第四步：配置分析参数")
    elif st.session_state.get('dimensions_confirmed'):
        # 如果在第四步（配置参数），回退到第三步
        st.session_state.dimensions_confirmed = False
        # 回到维度选择，旧的配置可能不再适用，因此清除它们
        if 'dimension_configs' in st.session_state:
            del st.session_state['dimension_configs']
        st.success("✅ 已回退到第三步：选择分析维度")
    elif st.session_state.get('analysis_type') and st.session_state.get('sheet_confirmed'):
        # 如果已选择分析类型且sheet已确认，说明在第三步（选择维度），回退到第二步
        # 保持analysis_type和analysis_name的选择
        # 只清除维度相关的确认状态
        if 'dimensions_confirmed' in st.session_state:
            del st.session_state.dimensions_confirmed
        if 'selected_dimensions' in st.session_state:
            del st.session_state.selected_dimensions
        # 添加一个临时标记，表示用户手动回退到第二步，避免直接跳转到第三步
        st.session_state.manual_back_to_step2 = True
        st.success("✅ 已回退到第二步：选择分析类型")
    elif st.session_state.get('sheet_confirmed'):
        # 如果在第二步（选择分析类型），回退到第一步
        st.session_state.sheet_confirmed = False
        # 保持selected_sheet的选择，用户可能只想重新选择分析类型
        st.success("✅ 已回退到第一步：选择数据源")
    else:
        st.info("💡 已经是第一步，无法继续回退")
    
    # 添加页面自动滚动到顶部
    st.markdown("""
    <script>
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    st.rerun()

def reset_analysis():
    """重置分析流程"""
    # 清理session state
    SessionStateManager.clear_session_data()
    
    # 清除配置加载状态提示
    for key in ['last_loaded_config_name', 'last_loaded_config_id']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ 已重置，请重新开始分析")
    st.rerun()

@st.cache_data
def load_data_cached(uploaded_file, sheet_name: str) -> pd.DataFrame:
    """高性能缓存数据加载函数（无UI元素，纯数据处理）"""
    try:
        # 使用优化的读取参数，无UI提示
        try:
            # 先读取少量数据检查格式
            sample_df = pd.read_excel(
                uploaded_file, 
                sheet_name=sheet_name, 
                nrows=5,
                engine='openpyxl'
            )
            
            if sample_df.empty:
                return pd.DataFrame()
            
            # 使用优化参数读取完整数据
            df = pd.read_excel(
                uploaded_file,
                sheet_name=sheet_name,
                engine='openpyxl',  # 使用更快的引擎
                na_values=['', 'NULL', 'null', 'N/A', 'n/a', '#N/A', 'nan'],
                keep_default_na=True
            )
            
            # 安全的数据类型优化，避免PyArrow转换问题
            for col in df.select_dtypes(include=['object']).columns:
                try:
                    # 只对非ID类型的重复字符串列进行category优化
                    if (df[col].nunique() / len(df) < 0.3 and 
                        not any(keyword in col.lower() for keyword in ['id', '号', 'code', 'sku', 'number'])):
                        df[col] = df[col].astype('category')
                except:
                    # 如果转换失败，保持原始类型
                    pass
            
            return df
            
        except Exception as load_error:
            # 如果优化加载失败，使用基本方式
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            return df
            
    except Exception as e:
        # 返回空DataFrame而不是显示错误
        return pd.DataFrame()

def load_data_with_progress(uploaded_file, sheet_name: str) -> pd.DataFrame:
    """带进度显示的数据加载函数"""
    # 创建进度提示容器
    progress_container = st.empty()
    
    try:
        # 第一步：检查文件格式
        progress_container.info("🔍 正在检查文件格式...")
        
        # 第二步：快速加载数据
        progress_container.info("📊 正在快速加载数据...")
        
        # 调用缓存的数据加载函数
        df = load_data_cached(uploaded_file, sheet_name)
        
        if df.empty:
            progress_container.warning(f"⚠️ 工作表 {sheet_name} 为空")
            return df
        
        # 第三步：完成加载
        progress_container.info("⚡ 正在优化数据类型...")
        
        # 短暂延迟以显示进度（优化：减少延迟时间）
        import time
        time.sleep(0.2)
        
        # 清除进度提示
        progress_container.empty()
        
        # 显示最终结果
        rows, cols = df.shape
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.success(f"✅ 高速加载完成！{rows:,} 行 × {cols} 列，内存占用: {memory_mb:.2f} MB")
        
        return df
        
    except Exception as e:
        progress_container.empty()
        st.error(f"❌ 数据加载失败: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    main() 