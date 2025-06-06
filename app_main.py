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
        
    # 重置按钮
    st.markdown("---")
    UIComponents.render_reset_button()

def render_main_content():
    """渲染主内容区域"""
    if not st.session_state.get('analysis_type'):
        # 步骤1: 选择分析类型
        UIComponents.render_analysis_type_selection()
        
    elif not st.session_state.get('sheet_confirmed'):
        st.info("👈 请在左侧上传Excel文件并选择Sheet")
        
    elif not st.session_state.get('dimensions_confirmed'):
        # 步骤3: 选择分析维度
        if 'uploaded_file' in st.session_state:
            handle_dimension_selection()
        
    elif not st.session_state.get('analysis_confirmed'):
        # 步骤4: 配置分析参数
        if 'uploaded_file' in st.session_state:
            handle_analysis_configuration()
            
    else:
        # 步骤5: 执行分析
        if 'uploaded_file' in st.session_state:
            execute_analysis()

def handle_file_upload(uploaded_file):
    """处理文件上传"""
    st.session_state.uploaded_file = uploaded_file
    
    if st.session_state.get('analysis_type') and not st.session_state.get('sheet_confirmed'):
        # 显示Sheet选择
        sheet = UIComponents.render_sheet_selection(uploaded_file)

def handle_dimension_selection():
    """处理分析维度选择"""
    analysis_type = st.session_state.get('analysis_type')
    analysis_name = st.session_state.get('analysis_name')
    
    if analysis_type and analysis_name:
        # 加载数据预览
        uploaded_file = st.session_state.get('uploaded_file')
        selected_sheet = st.session_state.get('selected_sheet')
        
        if uploaded_file and selected_sheet:
            # 加载数据
            df = load_data_cached(uploaded_file, selected_sheet)
            if not df.empty:
                # 显示数据预览
                UIComponents.render_data_preview(df)
                
                # 选择分析维度
                selected_dimensions = UIComponents.render_dimension_selection(analysis_type, analysis_name)
                
                if selected_dimensions:
                    # 确认按钮
                    if st.button(LANG["next_step"], type="primary"):
                        st.session_state.selected_dimensions = selected_dimensions
                        st.session_state.dimensions_confirmed = True
                        st.rerun()

def handle_analysis_configuration():
    """处理分析配置"""
    st.subheader("⚙️ 第四步：配置分析参数")
    
    # 添加页面置顶JavaScript
    st.markdown("""
    <script>
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    uploaded_file = st.session_state.get('uploaded_file')
    selected_sheet = st.session_state.get('selected_sheet')
    
    if not selected_dimensions:
        st.error("❌ 未找到选择的分析维度")
        return
    
    # 加载数据
    df = load_data_cached(uploaded_file, selected_sheet)
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
            st.rerun()
    else:
        st.warning("⚠️ 请完成所有必需的配置项")

def execute_analysis():
    """执行分析"""
    st.subheader("🚀 正在执行分析...")
    
    # 获取数据和配置
    uploaded_file = st.session_state.get('uploaded_file')
    selected_sheet = st.session_state.get('selected_sheet')
    selected_dimensions = st.session_state.get('selected_dimensions', [])
    dimension_configs = st.session_state.get('dimension_configs', {})
    
    # 加载数据
    df = load_data_cached(uploaded_file, selected_sheet)
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