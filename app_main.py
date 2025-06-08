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

def render_main_content():
    """渲染主内容区域"""
    if not st.session_state.get('uploaded_file'):
        # 步骤1: 等待文件上传
        st.info("👈 请在左侧上传Excel文件开始分析")
        
    elif not st.session_state.get('sheet_confirmed'):
        # 步骤2: 选择数据源（Sheet）
        handle_sheet_selection()
        
    elif not st.session_state.get('analysis_type') or st.session_state.get('manual_back_to_step2'):
        # 步骤2: 选择分析类型（或手动回退到此步骤）
        if st.session_state.get('manual_back_to_step2'):
            # 清除临时回退标记
            del st.session_state.manual_back_to_step2
        UIComponents.render_analysis_type_selection()
        
    elif not st.session_state.get('dimensions_confirmed'):
        # 步骤4: 数据加载和预览，选择分析维度
        if 'uploaded_file' in st.session_state:
            handle_dimension_selection()
        
    elif not st.session_state.get('analysis_confirmed'):
        # 步骤5: 配置分析参数
        if 'uploaded_file' in st.session_state:
            handle_analysis_configuration()
            
    else:
        # 步骤6: 执行分析
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

def handle_dimension_selection():
    """处理数据加载和分析维度选择"""
    analysis_type = st.session_state.get('analysis_type')
    analysis_name = st.session_state.get('analysis_name')
    
    if analysis_type and analysis_name:
        # 加载数据预览
        uploaded_file = st.session_state.get('uploaded_file')
        selected_sheet = st.session_state.get('selected_sheet')
        
        if uploaded_file and selected_sheet:
            # 加载数据
            sheet_name = str(selected_sheet) if selected_sheet is not None else ""
            if sheet_name:
                df = load_data_cached(uploaded_file, sheet_name)
            else:
                df = pd.DataFrame()
            if not df.empty:
                # 显示数据预览
                st.subheader("📊 数据加载结果")
                UIComponents.render_data_preview(df)
                
                # 选择分析维度
                selected_dimensions = UIComponents.render_dimension_selection(analysis_type, analysis_name)
                
                if selected_dimensions:
                    # 确认按钮
                    if st.button(LANG["next_step"], type="primary"):
                        st.session_state.selected_dimensions = selected_dimensions
                        st.session_state.dimensions_confirmed = True
                        # 添加页面自动滚动到第四步标题位置
                        st.markdown("""
                        <script>
                        setTimeout(function() {
                            // 查找包含"第四步"或"配置分析参数"的标题元素
                            const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                            let targetElement = null;
                            for (let element of elements) {
                                if (element.textContent.includes('第四步') || element.textContent.includes('配置分析参数')) {
                                    targetElement = element;
                                    break;
                                }
                            }
                            
                            if (targetElement) {
                                // 滚动到第四步标题位置，留一些顶部空间
                                const offsetTop = targetElement.offsetTop - 80;
                                window.scrollTo(0, Math.max(0, offsetTop));
                                console.log('滚动到第四步位置:', offsetTop);
                            } else {
                                // 如果找不到第四步标题，则滚动到顶部
                                window.scrollTo(0, 0);
                                console.log('未找到第四步标题，滚动到顶部');
                            }
                        }, 500);
                        </script>
                        """, unsafe_allow_html=True)
                        st.rerun()

def handle_analysis_configuration():
    """处理分析配置"""
    st.subheader("⚙️ 第四步：配置分析参数")
    
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    uploaded_file = st.session_state.get('uploaded_file')
    selected_sheet = st.session_state.get('selected_sheet')
    
    if not selected_dimensions:
        st.error("❌ 未找到选择的分析维度")
        return
    
    # 加载数据
    if selected_sheet is None:
        st.error("❌ 未找到选择的工作表")
        return
    
    sheet_name = str(selected_sheet)
    df = load_data_cached(uploaded_file, sheet_name)
    if df.empty:
        st.error("❌ 数据加载失败")
        return
    
    # 获取列名
    columns = list(df.columns)
    
    # 配置各个维度
    all_configs_valid = True
    dimension_configs = {}
    
    for dimension in selected_dimensions:
        # 为前置处理维度也添加配置界面
        if dimension in PREPROCESSING_DIMENSIONS:
            st.write(f"### {PREPROCESSING_DIMENSIONS[dimension]['icon']} {dimension}")
            
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
                    'container_height': st.session_state.get("container_height", 300)
                }
                dimension_configs[dimension] = config
            continue
            
        st.write(f"### {ANALYSIS_DIMENSIONS[dimension]['icon']} {dimension}")
        
        # 根据维度类型渲染配置界面
        if dimension == "装箱分析":
            config_valid = UIComponents.render_packing_analysis_config(columns)
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
            # 页面自动滚动到第五步位置
            st.markdown("""
            <script>
            setTimeout(function() {
                // 查找包含"第五步"或"正在执行分析"的标题元素
                const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                let targetElement = null;
                for (let element of elements) {
                    if (element.textContent.includes('第五步') || element.textContent.includes('正在执行分析')) {
                        targetElement = element;
                        break;
                    }
                }
                
                if (targetElement) {
                    // 滚动到执行分析标题位置，留一些顶部空间
                    const offsetTop = targetElement.offsetTop - 80;
                    window.scrollTo(0, offsetTop);
                } else {
                    // 如果找不到目标标题，则滚动到顶部
                    window.scrollTo(0, 0);
                }
            }, 200);
            </script>
            """, unsafe_allow_html=True)
            st.rerun()
    else:
        st.warning("⚠️ 请完成所有必需的配置项")

def execute_analysis():
    """执行分析"""
    st.subheader("🚀 第五步：正在执行分析...")
    
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
    df = load_data_cached(uploaded_file, sheet_name)
    if df.empty:
        st.error("❌ 数据加载失败")
        return
    
    # 创建分析引擎
    analysis_engine = AnalysisEngine(df)
    
    # 分离前置处理和分析步骤
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
        
        # 生成报告
        render_report_section(analysis_engine)
        
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

def render_report_section(analysis_engine: AnalysisEngine):
    """渲染报告生成区域"""
    st.write("## 📄 分析报告")
    
    # 导出数据按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 导出Excel数据", help="导出所有分析结果的Excel文件"):
            export_excel_data(analysis_engine)
    
    with col2:
        if st.button("📄 生成PDF报告", help="生成包含分析结果的PDF报告"):
            generate_pdf_report(analysis_engine)
    
    with col3:
        if st.button("🔄 重新分析", help="重新开始整个分析流程"):
            reset_analysis()

def export_excel_data(analysis_engine: AnalysisEngine):
    """导出Excel数据"""
    try:
        with st.spinner("正在准备Excel数据..."):
            export_data = analysis_engine.export_all_results()
            
            if not export_data:
                st.warning("⚠️ 没有可导出的数据")
                return
            
            # 创建Excel文件
            from io import BytesIO
            import xlsxwriter
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for sheet_name, df in export_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            buffer.seek(0)
            
            # 生成文件名
            filename = FileUtils.generate_filename("分析结果", st.session_state.get('analysis_name', ''), "xlsx")
            
            st.download_button(
                label="📥 下载Excel文件",
                data=buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Excel文件准备完成！点击上方按钮下载")
            
    except Exception as e:
        st.error(f"❌ Excel导出失败: {str(e)}")

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
        # 如果在第五步（执行分析），回退到第四步
        st.session_state.analysis_confirmed = False
        # 保持dimension_configs，用户可能想修改配置
        # BUGFIX: 显式地将保存的配置恢复，以便UI组件可以加载它们
        if 'dimension_configs' in st.session_state:
            for dimension, config in st.session_state.dimension_configs.items():
                # 根据维度类型，恢复相应的session_state键值
                if dimension == "装箱分析":
                    # 恢复装箱分析的配置
                    st.session_state["装箱分析_length_column"] = config.get('length_column')
                    st.session_state["装箱分析_width_column"] = config.get('width_column')
                    st.session_state["装箱分析_height_column"] = config.get('height_column')
                    st.session_state["装箱分析_inventory_column"] = config.get('inventory_column')
                    st.session_state["装箱分析_data_unit"] = config.get('data_unit', 'cm')
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
    st.success("✅ 已重置，请重新开始分析")
    st.rerun()

@st.cache_data
def load_data_cached(uploaded_file, sheet_name: str) -> pd.DataFrame:
    """缓存数据加载函数"""
    try:
        return DataUtils.load_excel_data(uploaded_file, sheet_name)
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    main() 