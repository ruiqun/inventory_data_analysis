# -*- coding: utf-8 -*-
"""
UI组件模块 - 包含所有Streamlit界面组件和展示逻辑
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import *
from core.packing_analysis import PackingAnalyzer
from utils import DataUtils

class UIComponents:
    """UI组件管理器"""
    
    @staticmethod
    def render_analysis_type_selection():
        """渲染分析类型选择界面"""
        st.subheader("🎯 第二步：选择分析类型")
        
        # 配置加载选项
        st.markdown("### 📋 配置选项")
        config_option = st.radio(
            "选择分析方式：",
            ["✨ 新建分析", "🔄 加载上次配置", "📂 加载指定配置"],
            help="选择如何开始分析"
        )
        
        if config_option == "🔄 加载上次配置":
            UIComponents._render_load_last_config()
            return
        elif config_option == "📂 加载指定配置":
            UIComponents._render_load_specific_config()
            return
        
        # 新建分析的类型选择
        st.markdown("### 🎯 选择分析类型")
        
        # 创建三列布局显示分析类型
        col1, col2, col3 = st.columns(3)
        
        # 获取当前选择的分析类型
        current_selection = st.session_state.get('temp_analysis_type', None)
        
        with col1:
            if st.button(f"{ANALYSIS_TYPES[LANG['inventory_analysis']]['icon']} {LANG['inventory_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "inventory" else "secondary"):
                st.session_state.temp_analysis_type = "inventory"
                st.session_state.temp_analysis_name = LANG["inventory_analysis"]
                st.rerun()
        
        with col2:
            if st.button(f"{ANALYSIS_TYPES[LANG['inbound_analysis']]['icon']} {LANG['inbound_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "inbound" else "secondary"):
                st.session_state.temp_analysis_type = "inbound"
                st.session_state.temp_analysis_name = LANG["inbound_analysis"]
                st.rerun()
        
        with col3:
            if st.button(f"{ANALYSIS_TYPES[LANG['outbound_analysis']]['icon']} {LANG['outbound_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "outbound" else "secondary"):
                st.session_state.temp_analysis_type = "outbound"
                st.session_state.temp_analysis_name = LANG["outbound_analysis"]
                st.rerun()
        
        # 显示当前选择
        if current_selection:
            temp_name = st.session_state.get('temp_analysis_name')
            st.success(f"✅ 已选择：**{temp_name}**")
            
            # 确认按钮
            if st.session_state.get('data_loaded', False):
                if st.button("确认分析类型", type="primary", use_container_width=True):
                    st.session_state.analysis_type = st.session_state.temp_analysis_type
                    st.session_state.analysis_name = st.session_state.temp_analysis_name
                    # 清理临时状态
                    del st.session_state.temp_analysis_type
                    del st.session_state.temp_analysis_name
                    # 页面自动滚动到顶部
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.scrollTo(0, 0);
                    }, 100);
                    </script>
                    """, unsafe_allow_html=True)
                    st.rerun()
            else:
                st.button("确认分析类型", type="primary", use_container_width=True, disabled=True)
        else:
            st.info("👆 请选择要执行的分析类型")
    
    @staticmethod
    def render_analysis_type_selection_with_loading():
        """渲染带数据加载状态的分析类型选择界面"""
        st.subheader("🎯 第二步：选择分析类型")
        
        # 配置加载选项
        st.markdown("### 📋 配置选项")
        config_option = st.radio(
            "选择分析方式：",
            ["✨ 新建分析", "🔄 加载上次配置", "📂 加载指定配置"],
            help="选择如何开始分析"
        )
        
        if config_option == "🔄 加载上次配置":
            UIComponents._render_load_last_config()
            return
        elif config_option == "📂 加载指定配置":
            UIComponents._render_load_specific_config()
            return
        
        # 新建分析的类型选择
        st.markdown("### 🎯 选择分析类型")
        
        # 创建三列布局显示分析类型
        col1, col2, col3 = st.columns(3)
        
        # 获取当前选择的分析类型
        current_selection = st.session_state.get('temp_analysis_type', None)
        
        with col1:
            if st.button(f"{ANALYSIS_TYPES[LANG['inventory_analysis']]['icon']} {LANG['inventory_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "inventory" else "secondary"):
                st.session_state.temp_analysis_type = "inventory"
                st.session_state.temp_analysis_name = LANG["inventory_analysis"]
                st.rerun()
        
        with col2:
            if st.button(f"{ANALYSIS_TYPES[LANG['inbound_analysis']]['icon']} {LANG['inbound_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "inbound" else "secondary"):
                st.session_state.temp_analysis_type = "inbound"
                st.session_state.temp_analysis_name = LANG["inbound_analysis"]
                st.rerun()
        
        with col3:
            if st.button(f"{ANALYSIS_TYPES[LANG['outbound_analysis']]['icon']} {LANG['outbound_analysis']}", 
                        use_container_width=True, 
                        type="primary" if current_selection == "outbound" else "secondary"):
                st.session_state.temp_analysis_type = "outbound"
                st.session_state.temp_analysis_name = LANG["outbound_analysis"]
                st.rerun()
        
        # 显示当前选择
        if current_selection:
            temp_name = st.session_state.get('temp_analysis_name')
            st.success(f"✅ 已选择：**{temp_name}**")
            
            # 确认按钮
            if st.session_state.get('data_loaded', False):
                if st.button("确认分析类型", type="primary", use_container_width=True):
                    st.session_state.analysis_type = st.session_state.temp_analysis_type
                    st.session_state.analysis_name = st.session_state.temp_analysis_name
                    # 清理临时状态
                    del st.session_state.temp_analysis_type
                    del st.session_state.temp_analysis_name
                    # 页面自动滚动到顶部
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.scrollTo(0, 0);
                    }, 100);
                    </script>
                    """, unsafe_allow_html=True)
                    st.rerun()
            else:
                st.button("确认分析类型", type="primary", use_container_width=True, disabled=True)
            
            # 显示数据加载状态（放在确认按钮下方）
            UIComponents._render_data_loading_status()
        else:
            st.info("👆 请选择要执行的分析类型")
            # 即使没有选择分析类型，也显示数据加载状态
            UIComponents._render_data_loading_status()
    
    @staticmethod
    def _render_data_loading_status():
        """渲染数据加载状态"""
        if st.session_state.get('data_loaded', False):
            # 数据已加载完成
            df = st.session_state.get('loaded_data')
            if df is not None:
                st.success(f"✅ **数据已就绪**：{len(df):,} 行数据，{len(df.columns)} 列")
        elif st.session_state.get('data_loading_error'):
            # 数据加载错误
            st.error(f"❌ {st.session_state.data_loading_error}")
            if st.button("🔄 重新加载数据", type="secondary"):
                # 清除错误状态并重新加载
                del st.session_state.data_loading_error
                for key in list(st.session_state.keys()):
                    if isinstance(key, str) and key.startswith('loading_'):
                        del st.session_state[key]
                # 重置加载进度
                st.session_state.data_loading_progress = 0
                st.rerun()
        else:
            # 数据加载中
            st.info("📊 **数据加载中...**")
            
            # 创建进度条
            progress_value = st.session_state.get('data_loading_progress', 0)
            
            # 优化的高速加载进度逻辑
            uploaded_file = st.session_state.get('uploaded_file')
            selected_sheet = st.session_state.get('selected_sheet')
            loading_key = f"loading_{selected_sheet}_{uploaded_file.name}" if uploaded_file and selected_sheet else None
            loading_triggered = st.session_state.get(loading_key, False) if loading_key else False
            
            # 检查是否是新的sheet选择，如果是则重置加载状态
            current_sheet_key = f"current_sheet_{uploaded_file.name}" if uploaded_file else None
            if current_sheet_key and st.session_state.get(current_sheet_key) != selected_sheet:
                # 清理旧的loading状态
                for key in list(st.session_state.keys()):
                    if isinstance(key, str) and key.startswith('loading_') and uploaded_file and uploaded_file.name in key:
                        del st.session_state[key]
                # 重置进度
                st.session_state.data_loading_progress = 0
                progress_value = 0
                loading_triggered = False
                # 记录当前sheet
                st.session_state[current_sheet_key] = selected_sheet
            
            # 如果还没开始实际加载，进行快速的假进度
            if not loading_triggered and progress_value < 85:
                if progress_value == 0:
                    # 立即跳到40%，给用户快速响应的感觉
                    st.session_state.data_loading_progress = 40
                    progress_value = 40
                elif progress_value < 85:
                    # 快速递增到85%
                    increment = 25 if progress_value < 60 else 15
                    st.session_state.data_loading_progress = min(progress_value + increment, 85)
                    progress_value = st.session_state.data_loading_progress
                
                # 显示进度条和状态
                st.progress(progress_value / 100)
                if progress_value < 60:
                    st.caption(f"🔍 分析文件结构... {progress_value}%")
                else:
                    st.caption(f"📊 准备加载数据... {progress_value}%")
                
                # 如果达到85%，立即触发实际加载
                if progress_value >= 85 and uploaded_file and selected_sheet and not loading_triggered and loading_key:
                    st.session_state[loading_key] = True
                    # 直接在这里加载数据，避免多次重新渲染
                    UIComponents._trigger_fast_data_loading(uploaded_file, selected_sheet)
                    # 数据加载完成后触发重新渲染
                    st.rerun()
                else:
                    # 立即触发重新渲染，不使用延迟
                    st.rerun()
            else:
                # 如果正在实际加载，显示真实进度
                st.progress(progress_value / 100)
                st.caption(f"⚡ 高速加载中... {progress_value}%")
    
    @staticmethod
    def _trigger_fast_data_loading(uploaded_file, selected_sheet):
        """快速触发数据加载"""
        try:
            # 进入实际加载阶段
            st.session_state.data_loading_progress = 90
            
            # 异步加载数据，使用缓存函数避免UI冲突
            from app_main import load_data_cached
            sheet_name = str(selected_sheet)
            
            # 更新进度到95%
            st.session_state.data_loading_progress = 95
            
            # 实际加载数据（使用缓存函数，避免UI冲突）
            df = load_data_cached(uploaded_file, sheet_name)
            
            if not df.empty:
                # 数据加载成功
                st.session_state.loaded_data = df
                st.session_state.data_loaded = True
                st.session_state.data_loading_progress = 100
                # 不在这里调用rerun，让上层调用者处理
            else:
                st.session_state.data_loading_error = "数据加载失败，请重新选择工作表"
                
        except Exception as e:
            st.session_state.data_loading_error = f"数据加载错误: {str(e)}"

    @staticmethod
    def _trigger_data_loading_direct(uploaded_file, selected_sheet):
        """直接触发数据加载（兼容性保留）"""
        UIComponents._trigger_fast_data_loading(uploaded_file, selected_sheet)
    
    @staticmethod
    def _render_load_last_config():
        """渲染加载上次配置的界面"""
        from utils.config_database import config_db
        
        # 获取最新的配置
        recent_configs = config_db.get_recent_configs(limit=1)
        
        if recent_configs:
            config = recent_configs[0]
            st.success(f"📋 **上次配置**: {config['config_name']}")
            st.info(f"🎯 分析类型: {config['analysis_name']}")
            st.info(f"📄 原文件: {config['file_name'] or '无'}")
            st.info(f"📊 维度数量: {len(config['selected_dimensions'])}个")
            
            if st.button("🚀 加载并应用此配置", type="primary", use_container_width=True):
                UIComponents._apply_config_and_jump_to_step4(config)
        else:
            st.warning("⚠️ 没有找到之前保存的配置")
            st.info("💡 请选择新建分析或上传配置文件")
    
    @staticmethod
    def _render_load_specific_config():
        """渲染加载指定配置的界面"""
        from utils.config_database import config_db
        
        st.markdown("#### 📂 从配置文件加载")
        
        # 上传配置文件
        uploaded_file = st.file_uploader(
            "选择配置文件",
            type=['json'],
            help="上传之前导出的配置JSON文件"
        )
        
        if uploaded_file:
            try:
                import json
                content = uploaded_file.read().decode('utf-8')
                data = json.loads(content)
                
                # 验证配置文件格式
                if 'export_type' in data and data['export_type'] == 'single_config':
                    config = data.get('config', {})
                    
                    # 显示配置信息
                    st.success(f"✅ **配置文件**: {config.get('config_name', '未知')}")
                    st.info(f"🎯 分析类型: {config.get('analysis_name', '未知')}")
                    st.info(f"📄 原文件: {config.get('file_name', '无')}")
                    st.info(f"📊 维度数量: {len(config.get('selected_dimensions', []))}个")
                    
                    if st.button("🚀 应用此配置", type="primary", use_container_width=True):
                        UIComponents._apply_config_and_jump_to_step4(config)
                else:
                    st.error("❌ 无效的配置文件格式")
            except Exception as e:
                st.error(f"❌ 配置文件解析失败: {str(e)}")
        
        st.markdown("#### 📋 从数据库选择配置")
        
        # 从数据库选择配置
        all_configs = config_db.get_recent_configs(limit=20)
        
        if all_configs:
            config_options = {
                f"{config['config_name']} ({config['analysis_name']})": config 
                for config in all_configs
            }
            
            selected_config_name = st.selectbox(
                "选择已保存的配置:",
                options=list(config_options.keys()),
                help="从数据库中选择一个已保存的配置"
            )
            
            if st.button("🚀 应用选中的配置", type="primary", use_container_width=True):
                selected_config = config_options[selected_config_name]
                UIComponents._apply_config_and_jump_to_step4(selected_config)
        else:
            st.info("📝 数据库中暂无保存的配置")
    
    @staticmethod
    def _apply_config_and_jump_to_step4(config):
        """应用配置并跳转到第四步"""
        try:
            # 恢复基本信息
            st.session_state['analysis_type'] = config['analysis_type']
            st.session_state['analysis_name'] = config['analysis_name']
            st.session_state['selected_dimensions'] = config['selected_dimensions']
            st.session_state['dimension_configs'] = config['dimension_configs']
            
            # 恢复容器配置
            if config.get('container_config'):
                for key, value in config['container_config'].items():
                    if value is not None:
                        st.session_state[key] = value
            
            # 恢复维度配置到session_state
            from components.config_manager import restore_dimension_configs_to_session
            restore_dimension_configs_to_session(config['dimension_configs'])
            
            # 直接跳转到第四步
            st.session_state['dimensions_confirmed'] = True
            
            # 清除分析确认状态，让用户在第四步重新确认
            if 'analysis_confirmed' in st.session_state:
                del st.session_state['analysis_confirmed']
            

            
            # 页面自动滚动到顶部
            st.markdown("""
            <script>
            setTimeout(function() {
                window.scrollTo(0, 0);
            }, 100);
            </script>
            """, unsafe_allow_html=True)
            
            st.success(f"✅ 已加载配置: {config['config_name']}")
            st.info("🎯 配置已应用，正在跳转到第四步...")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 配置应用失败: {str(e)}")
    
    @staticmethod
    def render_sheet_selection(uploaded_file):
        """渲染Sheet选择界面（优化版）"""
        st.subheader("📋 第一步：选择数据源")
        
        # 使用新的工具函数获取Excel信息
        excel_info = DataUtils.get_excel_sheets_info(uploaded_file)
        
        if not excel_info['sheet_names']:
            st.error("❌ 无法读取Excel文件的工作表信息")
            return None
        
        sheet_names = excel_info['sheet_names']
        sheets_info = excel_info['sheets_info']
        
        st.write(f"📋 发现 {len(sheet_names)} 个工作表：")
        
        # 展示每个工作表的详细信息
        for sheet_name in sheet_names:
            info = sheets_info.get(sheet_name, {})
            has_data = info.get('has_data', False)
            columns = info.get('columns', 0)
            
            if has_data:
                st.success(f"✅ **{sheet_name}** - {columns} 列数据，包含内容")
                sample_cols = info.get('sample_columns', [])
                if sample_cols:
                    st.caption(f"   前几列：{', '.join(sample_cols)}")
            else:
                st.warning(f"⚠️ **{sheet_name}** - 空工作表或无数据")
        
        # 过滤有数据的工作表作为推荐选项
        valid_sheets = [name for name in sheet_names if sheets_info.get(name, {}).get('has_data', False)]
        
        if valid_sheets:
            # 如果有有效工作表，优先显示
            if len(valid_sheets) == 1:
                st.info(f"💡 推荐选择：**{valid_sheets[0]}** （唯一有数据的工作表）")
                default_index = sheet_names.index(valid_sheets[0])
            else:
                st.info(f"💡 推荐工作表：{', '.join(valid_sheets)}")
                default_index = sheet_names.index(valid_sheets[0])
        else:
            st.warning("⚠️ 所有工作表都没有检测到数据，请检查文件内容")
            default_index = 0
        
        sheet = st.selectbox(
            LANG["select_sheet"], 
            sheet_names,
            index=default_index,
            help="建议选择有数据的工作表进行分析"
        )
        
        if st.button(LANG["confirm_button"], type="primary"):
            st.session_state.sheet_confirmed = True
            st.session_state.selected_sheet = sheet
            # 清理旧的数据缓存
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and key.startswith('data_'):
                    del st.session_state[key]
                    
        return sheet
    
    @staticmethod
    def render_sheet_selection_simple(uploaded_file):
        """渲染简化版Sheet选择界面"""
        st.subheader("📋 第一步：选择数据源")
        
        # 使用快速版本仅获取工作表名称
        excel_info = DataUtils.get_excel_sheets_names_only(uploaded_file)
        
        if not excel_info['sheet_names']:
            st.error("❌ 无法读取Excel文件的工作表信息")
            return None
        
        sheet_names = excel_info['sheet_names']
        
        # 简单显示工作表数量
        st.write(f"📋 发现 {len(sheet_names)} 个工作表")
        
        # 直接显示选择框，不展示详细信息
        sheet = st.selectbox(
            "请选择要分析的工作表：", 
            sheet_names,
            help="选择包含要分析数据的工作表"
        )
        
        if st.button("确认选择", type="primary"):
            st.session_state.sheet_confirmed = True
            st.session_state.selected_sheet = sheet
            # 清理旧的数据缓存和状态
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and (key.startswith('data_') or key == 'data_loaded'):
                    del st.session_state[key]
            # 页面自动滚动到顶部
            st.markdown("""
            <script>
            setTimeout(function() {
                window.scrollTo(0, 0);
            }, 100);
            </script>
            """, unsafe_allow_html=True)
            st.rerun()
                    
        return sheet
    
    @staticmethod
    def render_data_preview(df):
        """渲染数据预览"""
        # 数据基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("数据行数", len(df))
        with col2:
            st.metric("数据列数", len(df.columns))
        with col3:
            st.metric("数据大小", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        st.subheader(LANG["preview"])
        
        # 安全地处理数据预览，避免PyArrow转换问题
        try:
            # 创建预览数据的副本，将category类型转换为string避免PyArrow问题
            preview_df = df.head(10).copy()
            
            # 将category类型的列转换为string
            for col in preview_df.columns:
                if preview_df[col].dtype.name == 'category':
                    preview_df[col] = preview_df[col].astype('string')
            
            st.dataframe(preview_df, use_container_width=True)
            
        except Exception as e:
            # 如果仍然失败，降级使用纯文本显示
            st.warning("⚠️ 数据预览遇到格式问题，使用简化显示模式")
            
            # 创建简化的表格显示
            preview_data = []
            for idx, row in df.head(10).iterrows():
                row_data = {}
                for col in df.columns:
                    # 安全地转换每个值为字符串
                    try:
                        row_data[col] = str(row[col])
                    except:
                        row_data[col] = "数据格式错误"
                preview_data.append(row_data)
            
            import pandas as pd
            simple_df = pd.DataFrame(preview_data)
            st.dataframe(simple_df, use_container_width=True)
    
    @staticmethod
    def render_dimension_selection(analysis_type, analysis_name):
        """渲染分析维度选择界面"""
        st.subheader("🔍 第三步：选择分析维度")
        
        # 安全地获取分析维度，如果analysis_type不存在则使用空列表
        available_dimensions = ANALYSIS_TYPE_DIMENSIONS.get(analysis_type, [])
        
        # 根据分析类型自定义维度选择
        if analysis_type == "outbound":
            # 出库分析：显示出库分析的核心维度
            st.write(f"📊 请勾选要执行的 **{analysis_name}** 维度：")
            analysis_dimensions = ["ABC分析", "订单结构分析"]  # 出库分析默认执行，不在选择列表中
            default_dimensions = ["出库分析"]  # 默认包含的维度
        elif analysis_type == "inbound":
            # 入库分析：显示入库分析的核心维度  
            st.write(f"📊 请勾选要执行的 **{analysis_name}** 维度：")
            analysis_dimensions = ["ABC分析", "订单结构分析"]  # 入库分析默认执行，不在选择列表中
            default_dimensions = ["入库分析"]  # 默认包含的维度
        elif analysis_type == "inventory":
            # 库存分析：只显示装箱分析和ABC分析
            st.write(f"📊 请勾选要执行的 **{analysis_name}** 维度：")
            analysis_dimensions = ["装箱分析", "ABC分析"]  # 只显示这两个
            default_dimensions = []  # 无默认维度
        else:
            # 其他类型保持原来的逻辑
            st.write(f"📊 请勾选要执行的 **{analysis_name}** 维度：")
            analysis_dimensions = available_dimensions
            default_dimensions = []  # 无默认维度
        
        preprocessing_dimensions = list(PREPROCESSING_DIMENSIONS.keys())
        current_selected_dimensions = default_dimensions.copy()  # 先添加默认维度
        
        # 显示前置数据处理步骤
        if preprocessing_dimensions:
            st.write("### 🧹 **前置数据处理**（优先执行）")
            st.caption("⚡ 这些步骤会优先执行，影响后续所有分析的数据基础")
            
            for dimension in preprocessing_dimensions:
                dimension_info = PREPROCESSING_DIMENSIONS[dimension]
                
                is_selected = st.checkbox(
                    f"🔧 **{dimension_info['icon']} {dimension}** (前置步骤)",
                    key=f"preprocessing_{dimension}",
                    help=f"⚡ 前置步骤：{dimension_info['description']}"
                )
                
                if is_selected:
                    current_selected_dimensions.append(dimension)
                    
                    if dimension == "容器选择":
                        # 使用两列布局，将绿色提示放在右侧
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            UIComponents._render_container_selection_compact()
                        with col2:
                            st.success("✅ **容器标准化完成！**")
                            st.caption("")  # 空行保持高度一致
                    elif dimension == "异常数据清洗":
                        # 使用两列布局，将绿色提示放在右侧
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.info("📊 数据清洗配置将在后续步骤中详细设置")
                        with col2:
                            st.success("✅ **数据清洗已启用！**")
                            st.caption("")  # 空行保持高度一致
        
        # 显示分析步骤
        if analysis_dimensions or default_dimensions:
            st.write("### 📊 **数据分析步骤**")
            
            cleaning_selected = "异常数据清洗" in current_selected_dimensions
            container_selected = "容器选择" in current_selected_dimensions
            
            if cleaning_selected and container_selected:
                st.caption("📈 这些分析将基于数据清洗和容器标准化的结果进行")
            elif cleaning_selected:
                st.caption("📈 这些分析将基于数据清洗的结果进行")
            elif container_selected:
                st.caption("📈 这些分析将基于容器标准化进行")
            else:
                st.caption("📈 这些分析将基于原始数据进行")
            
            # 显示默认执行的维度
            if default_dimensions:
                st.write("**📌 默认执行的分析：**")
                for dimension in default_dimensions:
                    dimension_info = ANALYSIS_DIMENSIONS[dimension]
                    st.info(f"✅ {dimension_info['icon']} **{dimension}** - {dimension_info['description']}")
                st.caption("⚡ 上述分析将默认执行，无需勾选")
            
            # 显示可选的维度
            if analysis_dimensions:
                st.write("**📊 可选的附加分析：**")
                col1, col2 = st.columns(2)
                
                for i, dimension in enumerate(analysis_dimensions):
                    dimension_info = ANALYSIS_DIMENSIONS[dimension]
                    
                    with col1 if i % 2 == 0 else col2:
                        is_selected = st.checkbox(
                            f"{dimension_info['icon']} {dimension}",
                            key=f"dim_{dimension}",
                            help=dimension_info['description']
                        )
                        
                        if is_selected:
                            current_selected_dimensions.append(dimension)
        
        return current_selected_dimensions
    
    @staticmethod
    def _render_container_selection():
        """渲染容器选择界面"""
        st.success("📦 **已选择容器标准化**：后续分析将基于选定容器规格进行")
        
        with st.container():
            st.write("**📏 选择标准容器规格：**")
            container_size = st.selectbox(
                "容器尺寸 (长x宽x高 mm)",
                options=list(CONTAINER_SPECS.keys()),
                key="selected_container_size",
                help="选择的容器规格将应用于所有后续分析"
            )
            
            dimensions = CONTAINER_SPECS[container_size]
            length, width, height = dimensions['length'], dimensions['width'], dimensions['height']
            st.info(f"✅ **选定容器规格**：长{length}mm × 宽{width}mm × 高{height}mm")
            
            st.session_state.container_length = length
            st.session_state.container_width = width
            st.session_state.container_height = height

    @staticmethod
    def _render_container_selection_compact():
        """渲染紧凑版容器选择界面"""
        col1, col2 = st.columns(2)
        
        with col1:
            container_size = st.selectbox(
                "容器尺寸 (长x宽x高 mm)",
                options=list(CONTAINER_SPECS.keys()),
                key="selected_container_size",
                help="选择的容器规格将应用于所有后续分析"
            )
            
            dimensions = CONTAINER_SPECS[container_size]
            length, width, height = dimensions['length'], dimensions['width'], dimensions['height']
            
            st.session_state.container_length = length
            st.session_state.container_width = width
            st.session_state.container_height = height
        
        with col2:
            from config import CONTAINER_WEIGHT_LIMITS
            weight_limit = st.selectbox(
                "容器重量限制",
                options=list(CONTAINER_WEIGHT_LIMITS.keys()),
                key="selected_container_weight_limit",
                help="选择容器的最大载重量"
            )
            
            st.session_state.container_weight_limit = CONTAINER_WEIGHT_LIMITS[weight_limit]
        
        # 分隔选择
        st.write("**🔗 容器分隔设置**")
        use_dividers = st.radio(
            "是否使用分隔",
            options=["否", "是"],
            key="use_dividers",
            help="选择是否在容器中使用分隔"
        )
        
        if use_dividers == "是":
            st.warning("⚠️ 隔口功能还在开发中，敬请期待！")
            from config import CONTAINER_DIVIDERS
            selected_dividers = st.multiselect(
                "选择隔口数量（支持多选）",
                options=list(CONTAINER_DIVIDERS.keys()),
                format_func=lambda x: CONTAINER_DIVIDERS[x]["description"],
                key="selected_dividers",
                help="可以选择多种隔口配置进行对比分析"
            )
            
            if selected_dividers:
                st.info(f"✅ 已选择隔口: {', '.join([CONTAINER_DIVIDERS[d]['description'] for d in selected_dividers])}")
    
    @staticmethod
    def render_packing_analysis_config(columns):
        """渲染装箱分析配置界面"""
        st.write("📦 请配置装箱分析参数：")
        
        # 初始化默认值（如果不存在）
        if "装箱分析_data_unit" not in st.session_state:
            st.session_state["装箱分析_data_unit"] = "cm"
        if "装箱分析_weight_unit" not in st.session_state:
            st.session_state["装箱分析_weight_unit"] = "kg"
        if "装箱分析_show_details" not in st.session_state:
            st.session_state["装箱分析_show_details"] = True
        
        # 显示当前选定的容器（如果有）
        if st.session_state.get("container_length"):
            current_container = st.session_state.get("selected_container_size", "600x400x300")
            length = st.session_state.get("container_length")
            width = st.session_state.get("container_width") 
            height = st.session_state.get("container_height")
            weight_limit = st.session_state.get("container_weight_limit", 30)
            st.info(f"✅ 当前货箱规格: {current_container} (长{length}mm × 宽{width}mm × 高{height}mm) | 重量限制: {weight_limit}kg")
        else:
            st.warning("⚠️ 请先在前置处理中选择容器规格和重量限制")
            return False
        
        st.write("**🎯 数据列配置**")
        st.caption("选择数据中对应货物尺寸和库存的列")
        
        # 列选择
        col1, col2 = st.columns(2)
        with col1:
            length_column = st.selectbox(
                "货物长度列",
                options=columns,
                key="装箱分析_length_column",
                help="选择包含货物长度数据的列"
            )
            
            width_column = st.selectbox(
                "货物宽度列", 
                options=columns,
                key="装箱分析_width_column",
                help="选择包含货物宽度数据的列"
            )
            
            height_column = st.selectbox(
                "货物高度列",
                options=columns,
                key="装箱分析_height_column", 
                help="选择包含货物高度数据的列"
            )
        
        with col2:
            inventory_column = st.selectbox(
                "库存件数列",
                options=columns,
                key="装箱分析_inventory_column",
                help="选择包含库存件数的列"
            )
            
            weight_column = st.selectbox(
                "货物重量列",
                options=columns,
                key="装箱分析_weight_column",
                help="选择包含货物重量数据的列"
            )
        
        st.write("**📏 数据单位设置**")
        col_unit1, col_unit2 = st.columns(2)
        
        with col_unit1:
            data_unit = st.selectbox(
                "货物尺寸数据单位",
                options=["mm", "cm", "m"],
                key="装箱分析_data_unit",
                help="选择数据中货物尺寸的单位，系统将自动转换为mm进行计算"
            )
            
            # 单位转换提示
            if data_unit == "cm":
                st.caption("💡 数据将从cm转换为mm（乘以10）")
            elif data_unit == "m":
                st.caption("💡 数据将从m转换为mm（乘以1000）")
            else:
                st.caption("💡 数据已为mm单位，无需转换")
        
        with col_unit2:
            weight_unit = st.selectbox(
                "货物重量数据单位",
                options=["kg", "g"],
                key="装箱分析_weight_unit",
                help="选择数据中货物重量的单位，系统将自动转换为kg进行计算"
            )
            
            # 重量单位转换提示
            if weight_unit == "g":
                st.caption("💡 数据将从g转换为kg（除以1000）")
            else:
                st.caption("💡 数据已为kg单位，无需转换")
        
        st.write("**⚙️ 分析选项**")
        show_details = st.checkbox(
            "显示详细装箱计算过程",
            key="装箱分析_show_details",
            help="显示每个SKU的6种摆放方式计算详情"
        )
        
        st.write("**📊 分析说明**")
        st.info("💡 系统将自动分批处理全量数据，使用完整的6种摆放方式进行最优装箱计算")
        
        return True
    
    @staticmethod
    def render_packing_analysis_results(analyzer, packing_results, summary_stats, data_unit):
        """渲染装箱分析结果界面"""
        # 显示关键指标
        UIComponents._render_packing_metrics(summary_stats)
        
        # 根据数据量选择展示方式
        large_dataset = len(packing_results) > PACKING_CONFIG["large_dataset_threshold"]
        
        if large_dataset:
            UIComponents._render_large_dataset_summary(summary_stats, data_unit)
        else:
            UIComponents._render_small_dataset_details(packing_results, data_unit)
        
        # 导出功能
        UIComponents._render_export_buttons(packing_results, summary_stats, data_unit, analyzer.container_info)
        
        # 优化建议
        suggestions = analyzer.generate_optimization_suggestions(packing_results, summary_stats)
        UIComponents._render_optimization_suggestions(suggestions)
    
    @staticmethod
    def render_abc_analysis_config(columns):
        """渲染ABC分析配置界面"""
        st.write("📊 请配置ABC分析参数：")
        
        # 选择SKU列和数量列
        col1, col2 = st.columns(2)
        with col1:
            sku_column = st.selectbox(
                "选择SKU号列",
                options=columns,
                key="ABC分析_sku_column",
                help="选择包含SKU编号或商品编号的列"
            )
        
        with col2:
            quantity_column = st.selectbox(
                "选择数量列",
                options=columns,
                key="ABC分析_quantity_column",
                help="选择包含出库数量、销售数量等的列"
            )
        
        # 设置ABC类别的百分比
        st.write("**🎯 分类阈值设置**")
        col1, col2 = st.columns(2)
        
        with col1:
            # 检查session_state中是否已有值，避免widget冲突
            if "ABC分析_a_percentage" in st.session_state:
                a_percentage = st.number_input(
                    "A类品占出库数量百分比(%)",
                    min_value=1,
                    max_value=99,
                    step=1,
                    key="ABC分析_a_percentage",
                    help="A类品的累计数量占比阈值"
                )
            else:
                a_percentage = st.number_input(
                    "A类品占出库数量百分比(%)",
                    min_value=1,
                    max_value=99,
                    value=70,
                    step=1,
                    key="ABC分析_a_percentage",
                    help="A类品的累计数量占比阈值"
                )
        
        with col2:
            # 检查session_state中是否已有值，避免widget冲突
            if "ABC分析_b_percentage" in st.session_state:
                b_percentage = st.number_input(
                    "B类品占出库数量百分比(%)",
                    min_value=1,
                    max_value=99,
                    step=1,
                    key="ABC分析_b_percentage",
                    help="B类品的累计数量占比阈值（从A类阈值开始累计）"
                )
            else:
                b_percentage = st.number_input(
                    "B类品占出库数量百分比(%)",
                    min_value=1,
                    max_value=99,
                    value=20,
                    step=1,
                    key="ABC分析_b_percentage",
                    help="B类品的累计数量占比阈值（从A类阈值开始累计）"
                )
        
        # 验证输入
        if a_percentage >= 100:
            st.error("❌ A类品百分比必须小于100%")
            return False
            
        if b_percentage >= 100:
            st.error("❌ B类品百分比必须小于100%")
            return False
            
        if a_percentage <= b_percentage:
            st.error("❌ A类品百分比必须大于B类品百分比")
            return False
        
        # 计算总百分比
        total_ab = a_percentage + b_percentage
        c_percentage = 100 - total_ab
        
        if total_ab >= 100:
            st.error("❌ A类品和B类品百分比总和必须小于100%")
            return False
        
        # 显示分类说明
        st.write("**📋 分类说明**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success(f"🏆 **A类品**\n累计占比 ≤ {a_percentage}%")
        
        with col2:
            st.info(f"📈 **B类品**\n累计占比 {a_percentage}% < x ≤ {a_percentage + b_percentage}%")
        
        with col3:
            st.warning(f"📉 **C类品**\n累计占比 > {a_percentage + b_percentage}%")
        
        # 分析方法说明
        st.write("**🔬 分析方法**")
        st.info("""
        💡 **分析步骤**：
        1. 按数量列对SKU进行降序排序
        2. 计算每个SKU数量占总数量的比例
        3. 计算累计比例
        4. 根据累计比例进行ABC分类
        5. 生成详细分析报告和可视化图表
        """)
        
        return True
    
    @staticmethod
    def render_outbound_analysis_config(columns):
        """渲染出库通用分析配置界面"""
        st.write("📈 请配置出库分析参数：")
        
        # 数据列选择
        st.write("**🗂️ 数据列选择**")
        
        # 日期列单独一行
        date_column = st.selectbox(
            "选择日期列",
            options=columns,
            key="出库分析_date_column",
            help="选择包含出库日期的列"
        )
        
        # 订单相关列选择
        st.write("**📦 订单数据选择**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.radio(
                "选择订单数据源",
                options=["订单号列（原始）", "订单数/天列（聚合）", "无订单数据"],
                key="出库分析_order_data_type",
                help="选择使用原始订单号列还是已聚合的订单数/天列"
            )
        
        with col2:
            order_data_type = st.session_state.get("出库分析_order_data_type", "无订单数据")
            if order_data_type == "订单号列（原始）":
                st.selectbox(
                    "选择订单号列",
                    options=["无数据"] + list(columns),
                    key="出库分析_order_id_column",
                    help="选择包含订单号的列，将自动按日期去重统计"
                )
                st.session_state["出库分析_order_count_column"] = "无数据"
            elif order_data_type == "订单数/天列（聚合）":
                st.selectbox(
                    "选择订单数/天列",
                    options=["无数据"] + list(columns),
                    key="出库分析_order_count_column",
                    help="选择包含每日订单数量的聚合列"
                )
                st.session_state["出库分析_order_id_column"] = "无数据"
            else:  # 无订单数据
                st.session_state["出库分析_order_id_column"] = "无数据"
                st.session_state["出库分析_order_count_column"] = "无数据"
                st.info("📋 不使用订单数据进行分析")
        
        # SKU相关列选择
        st.write("**🏷️ SKU数据选择**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.radio(
                "选择SKU数据源",
                options=["SKU列（原始）", "SKU数/天列（聚合）", "无SKU数据"],
                key="出库分析_sku_data_type",
                help="选择使用原始SKU列还是已聚合的SKU数/天列"
            )
        
        with col2:
            sku_data_type = st.session_state.get("出库分析_sku_data_type", "无SKU数据")
            if sku_data_type == "SKU列（原始）":
                st.selectbox(
                    "选择SKU列",
                    options=["无数据"] + list(columns),
                    key="出库分析_sku_column",
                    help="选择包含SKU编号的列，将自动按日期去重统计"
                )
                st.session_state["出库分析_sku_count_column"] = "无数据"
            elif sku_data_type == "SKU数/天列（聚合）":
                st.selectbox(
                    "选择SKU数/天列",
                    options=["无数据"] + list(columns),
                    key="出库分析_sku_count_column",
                    help="选择包含每日SKU数量的聚合列"
                )
                st.session_state["出库分析_sku_column"] = "无数据"
            else:  # 无SKU数据
                st.session_state["出库分析_sku_column"] = "无数据"
                st.session_state["出库分析_sku_count_column"] = "无数据"
                st.info("📋 不使用SKU数据进行分析")
        
        # 件数相关列选择
        st.write("**🔢 件数数据选择**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.radio(
                "选择件数数据源",
                options=["件数列（原始）", "件数/天列（聚合）", "无件数数据"],
                key="出库分析_item_data_type",
                help="选择使用原始件数列还是已聚合的件数/天列"
            )
        
        with col2:
            item_data_type = st.session_state.get("出库分析_item_data_type", "无件数数据")
            if item_data_type == "件数列（原始）":
                st.selectbox(
                    "选择件数列",
                    options=["无数据"] + list(columns),
                    key="出库分析_item_column",
                    help="选择包含件数的列，将自动按日期求和"
                )
                st.session_state["出库分析_item_count_column"] = "无数据"
            elif item_data_type == "件数/天列（聚合）":
                st.selectbox(
                    "选择件数/天列",
                    options=["无数据"] + list(columns),
                    key="出库分析_item_count_column",
                    help="选择包含每日件数的聚合列"
                )
                st.session_state["出库分析_item_column"] = "无数据"
            else:  # 无件数数据
                st.session_state["出库分析_item_column"] = "无数据"
                st.session_state["出库分析_item_count_column"] = "无数据"
                st.info("📋 不使用件数数据进行分析")
        
        # 日期范围选择
        st.write("**📅 分析时间范围**")
        col1, col2 = st.columns(2)
        
        # 获取日期范围的默认值
        try:
            df = st.session_state.get('loaded_data')
            if df is not None and date_column in df.columns:
                date_series = pd.to_datetime(df[date_column], errors='coerce')
                min_date = date_series.min().date() if not date_series.isna().all() else None
                max_date = date_series.max().date() if not date_series.isna().all() else None
            else:
                min_date = max_date = None
        except:
            min_date = max_date = None
        
        with col1:
            # 智能处理默认值：如果session_state中已有值，不设置value参数
            if "出库分析_start_date" not in st.session_state and min_date:
                start_date = st.date_input(
                    "开始日期",
                    value=min_date,
                    min_value=min_date if min_date else datetime(2020, 1, 1).date(),
                    max_value=max_date if max_date else datetime(2030, 12, 31).date(),
                    key="出库分析_start_date",
                    help="分析的开始日期"
                )
            else:
                # 如果session_state中已有值，检查是否在有效范围内
                if "出库分析_start_date" in st.session_state:
                    # 检查现有值是否在有效范围内，如果不是则重置
                    current_value = st.session_state.get("出库分析_start_date")
                    min_start = min_date if min_date else datetime(2020, 1, 1).date()
                    max_start = max_date if max_date else datetime(2030, 12, 31).date()
                    
                    if current_value and (current_value < min_start or current_value > max_start):
                        # 重置为有效范围内的默认值
                        st.session_state["出库分析_start_date"] = min_start
                    
                    start_date = st.date_input(
                        "开始日期",
                        min_value=min_start,
                        max_value=max_start,
                        key="出库分析_start_date",
                        help="分析的开始日期"
                    )
                else:
                    # 确保默认值在min_value和max_value范围内
                    default_start = min_date if min_date else datetime(2020, 1, 1).date()
                    min_start = min_date if min_date else datetime(2020, 1, 1).date()
                    max_start = max_date if max_date else datetime(2030, 12, 31).date()
                    start_date = st.date_input(
                        "开始日期",
                        value=default_start,
                        min_value=min_start,
                        max_value=max_start,
                        key="出库分析_start_date",
                        help="分析的开始日期"
                    )
        
        with col2:
            # 智能处理默认值：如果session_state中已有值，不设置value参数
            if "出库分析_end_date" not in st.session_state and max_date:
                end_date = st.date_input(
                    "结束日期",
                    value=max_date,
                    min_value=min_date if min_date else datetime(2020, 1, 1).date(),
                    max_value=max_date if max_date else datetime(2030, 12, 31).date(),
                    key="出库分析_end_date",
                    help="分析的结束日期"
                )
            else:
                # 如果session_state中已有值，检查是否在有效范围内
                if "出库分析_end_date" in st.session_state:
                    # 检查现有值是否在有效范围内，如果不是则重置
                    current_value = st.session_state.get("出库分析_end_date")
                    min_end = min_date if min_date else datetime(2020, 1, 1).date()
                    max_end = max_date if max_date else datetime(2030, 12, 31).date()
                    
                    if current_value and (current_value < min_end or current_value > max_end):
                        # 重置为有效范围内的默认值
                        st.session_state["出库分析_end_date"] = max_end
                    
                    end_date = st.date_input(
                        "结束日期",
                        min_value=min_end,
                        max_value=max_end,
                        key="出库分析_end_date",
                        help="分析的结束日期"
                    )
                else:
                    # 确保默认值在min_value和max_value范围内
                    default_end = max_date if max_date else datetime(2030, 12, 31).date()
                    min_end = min_date if min_date else datetime(2020, 1, 1).date()
                    max_end = max_date if max_date else datetime(2030, 12, 31).date()
                    end_date = st.date_input(
                        "结束日期",
                        value=default_end,
                        min_value=min_end,
                        max_value=max_end,
                        key="出库分析_end_date",
                        help="分析的结束日期"
                    )
        
        # 验证配置
        if start_date and end_date and start_date > end_date:
            st.error("❌ 开始日期不能晚于结束日期")
            return False
        
        # 分析说明
        st.write("**🔬 分析说明**")
        
        # 显示当前选择的数据类型
        selected_types = []
        
        # 订单数据分析
        order_data_type = st.session_state.get("出库分析_order_data_type", "无订单数据")
        if order_data_type == "订单号列（原始）":
            selected_types.append("📦 原始订单号数据 → 将按日期聚合计算订单数/天")
        elif order_data_type == "订单数/天列（聚合）":
            selected_types.append("📦 已聚合的订单数/天数据")
            
        # SKU数据分析
        sku_data_type = st.session_state.get("出库分析_sku_data_type", "无SKU数据")
        if sku_data_type == "SKU列（原始）":
            selected_types.append("🏷️ 原始SKU数据 → 将按日期聚合计算SKU数/天")
        elif sku_data_type == "SKU数/天列（聚合）":
            selected_types.append("🏷️ 已聚合的SKU数/天数据")
            
        # 件数数据分析
        item_data_type = st.session_state.get("出库分析_item_data_type", "无件数数据")
        if item_data_type == "件数列（原始）":
            selected_types.append("🔢 原始件数数据 → 将按日期聚合计算件数/天")
        elif item_data_type == "件数/天列（聚合）":
            selected_types.append("🔢 已聚合的件数/天数据")
        
        if selected_types:
            st.success("✅ **已选择的数据类型**：\n" + "\n".join([f"• {t}" for t in selected_types]))
        else:
            st.warning("⚠️ 请至少选择一种数据类型进行分析")
            return False
        
        st.info("""
        💡 **分析流程**：
        1. **数据处理**：根据选择自动聚合原始数据或直接使用聚合数据
        2. **趋势分析**：生成日期趋势折线图（X轴：日期，Y轴：有数据的指标）
        3. **统计分析**：计算波动系数、增长率等关键指标
        4. **优化建议**：基于数据模式提供运营优化建议
        """)
        
        return True
    
    @staticmethod
    def render_inbound_analysis_config(columns):
        """渲染入库分析配置界面"""
        st.write("**📦 入库分析配置**")
        
        # 日期列选择（单独一行）
        st.markdown("### 📅 日期数据配置")
        date_column = st.selectbox(
            "选择日期列",
            options=columns,
            key="入库分析_date_column",
            help="选择包含入库日期的列"
        )
        
        # SKU数据选择
        st.markdown("### 🏷️ SKU数据选择")
        col1, col2 = st.columns(2)
        
        with col1:
            st.radio(
                "选择SKU数据源",
                options=["SKU列（原始）", "SKU数/天列（聚合）", "无SKU数据"],
                key="入库分析_sku_data_type",
                help="选择使用原始SKU列还是已聚合的SKU数/天列"
            )
        
        with col2:
            sku_data_type = st.session_state.get("入库分析_sku_data_type", "无SKU数据")
            if sku_data_type == "SKU列（原始）":
                st.selectbox(
                    "选择SKU列",
                    options=["无数据"] + list(columns),
                    key="入库分析_sku_column",
                    help="选择包含SKU编号的列，将自动按日期去重统计"
                )
                st.session_state["入库分析_sku_count_column"] = "无数据"
            elif sku_data_type == "SKU数/天列（聚合）":
                st.selectbox(
                    "选择SKU数/天列",
                    options=["无数据"] + list(columns),
                    key="入库分析_sku_count_column",
                    help="选择包含每日SKU数量的聚合列"
                )
                st.session_state["入库分析_sku_column"] = "无数据"
            else:  # 无SKU数据
                st.session_state["入库分析_sku_column"] = "无数据"
                st.session_state["入库分析_sku_count_column"] = "无数据"
                st.info("📋 不使用SKU数据进行分析")
        
        # 件数数据选择
        st.markdown("### 🔢 件数数据选择")
        col1, col2 = st.columns(2)
        
        with col1:
            st.radio(
                "选择件数数据源",
                options=["件数列（原始）", "件数/天列（聚合）", "无件数数据"],
                key="入库分析_quantity_data_type",
                help="选择使用原始件数列还是已聚合的件数/天列"
            )
        
        with col2:
            quantity_data_type = st.session_state.get("入库分析_quantity_data_type", "无件数数据")
            if quantity_data_type == "件数列（原始）":
                st.selectbox(
                    "选择件数列",
                    options=["无数据"] + list(columns),
                    key="入库分析_quantity_column",
                    help="选择包含件数的列，将自动按日期求和"
                )
                st.session_state["入库分析_quantity_count_column"] = "无数据"
            elif quantity_data_type == "件数/天列（聚合）":
                st.selectbox(
                    "选择件数/天列",
                    options=["无数据"] + list(columns),
                    key="入库分析_quantity_count_column",
                    help="选择包含每日件数的聚合列"
                )
                st.session_state["入库分析_quantity_column"] = "无数据"
            else:  # 无件数数据
                st.session_state["入库分析_quantity_column"] = "无数据"
                st.session_state["入库分析_quantity_count_column"] = "无数据"
                st.info("📋 不使用件数数据进行分析")
        
        # 日期范围选择
        st.markdown("### 📅 分析时间范围")
        col1, col2 = st.columns(2)
        
        # 获取日期范围的默认值
        try:
            df = st.session_state.get('loaded_data')
            if df is not None and date_column in df.columns:
                date_series = pd.to_datetime(df[date_column], errors='coerce')
                min_date = date_series.min().date() if not date_series.isna().all() else None
                max_date = date_series.max().date() if not date_series.isna().all() else None
            else:
                min_date = max_date = None
        except:
            min_date = max_date = None
        
        with col1:
            # 智能处理默认值：如果session_state中已有值，不设置value参数
            if "入库分析_start_date" not in st.session_state and min_date:
                start_date = st.date_input(
                    "开始日期",
                    value=min_date,
                    min_value=min_date if min_date else datetime(2020, 1, 1).date(),
                    max_value=max_date if max_date else datetime(2030, 12, 31).date(),
                    key="入库分析_start_date",
                    help="分析的开始日期"
                )
            else:
                # 如果session_state中已有值，检查是否在有效范围内
                if "入库分析_start_date" in st.session_state:
                    # 检查现有值是否在有效范围内，如果不是则重置
                    current_value = st.session_state.get("入库分析_start_date")
                    min_start = min_date if min_date else datetime(2020, 1, 1).date()
                    max_start = max_date if max_date else datetime(2030, 12, 31).date()
                    
                    if current_value and (current_value < min_start or current_value > max_start):
                        # 重置为有效范围内的默认值
                        st.session_state["入库分析_start_date"] = min_start
                    
                    start_date = st.date_input(
                        "开始日期",
                        min_value=min_start,
                        max_value=max_start,
                        key="入库分析_start_date",
                        help="分析的开始日期"
                    )
                else:
                    # 确保默认值在min_value和max_value范围内
                    default_start = min_date if min_date else datetime(2020, 1, 1).date()
                    min_start = min_date if min_date else datetime(2020, 1, 1).date()
                    max_start = max_date if max_date else datetime(2030, 12, 31).date()
                    start_date = st.date_input(
                        "开始日期",
                        value=default_start,
                        min_value=min_start,
                        max_value=max_start,
                        key="入库分析_start_date",
                        help="分析的开始日期"
                    )
        
        with col2:
            # 智能处理默认值：如果session_state中已有值，不设置value参数
            if "入库分析_end_date" not in st.session_state and max_date:
                end_date = st.date_input(
                    "结束日期",
                    value=max_date,
                    min_value=min_date if min_date else datetime(2020, 1, 1).date(),
                    max_value=max_date if max_date else datetime(2030, 12, 31).date(),
                    key="入库分析_end_date",
                    help="分析的结束日期"
                )
            else:
                # 如果session_state中已有值，检查是否在有效范围内
                if "入库分析_end_date" in st.session_state:
                    # 检查现有值是否在有效范围内，如果不是则重置
                    current_value = st.session_state.get("入库分析_end_date")
                    min_end = min_date if min_date else datetime(2020, 1, 1).date()
                    max_end = max_date if max_date else datetime(2030, 12, 31).date()
                    
                    if current_value and (current_value < min_end or current_value > max_end):
                        # 重置为有效范围内的默认值
                        st.session_state["入库分析_end_date"] = max_end
                    
                    end_date = st.date_input(
                        "结束日期",
                        min_value=min_end,
                        max_value=max_end,
                        key="入库分析_end_date",
                        help="分析的结束日期"
                    )
                else:
                    # 确保默认值在min_value和max_value范围内
                    default_end = max_date if max_date else datetime(2030, 12, 31).date()
                    min_end = min_date if min_date else datetime(2020, 1, 1).date()
                    max_end = max_date if max_date else datetime(2030, 12, 31).date()
                    end_date = st.date_input(
                        "结束日期",
                        value=default_end,
                        min_value=min_end,
                        max_value=max_end,
                        key="入库分析_end_date",
                        help="分析的结束日期"
                    )
        
        # 验证配置
        if start_date and end_date and start_date > end_date:
            st.error("❌ 开始日期不能晚于结束日期")
            return False
        
        # 配置摘要和验证
        st.markdown("### ✅ 分析说明")
        
        # 收集已选择的数据源
        selected_sources = []
        
        # SKU数据源检查
        sku_original = st.session_state.get("入库分析_sku_column", "无数据")
        sku_aggregated = st.session_state.get("入库分析_sku_count_column", "无数据")
        if sku_original != "无数据":
            selected_sources.append(f"🔹 原始SKU数据：{sku_original}列，将按日期去重计算SKU数/天")
        elif sku_aggregated != "无数据":
            selected_sources.append(f"🔹 聚合SKU数据：{sku_aggregated}列，直接按日期汇总")
        
        # 件数数据源检查
        qty_original = st.session_state.get("入库分析_quantity_column", "无数据")
        qty_aggregated = st.session_state.get("入库分析_quantity_count_column", "无数据")
        if qty_original != "无数据":
            selected_sources.append(f"🔹 原始件数数据：{qty_original}列，将按日期求和计算件数/天")
        elif qty_aggregated != "无数据":
            selected_sources.append(f"🔹 聚合件数数据：{qty_aggregated}列，直接按日期汇总")
        
        if selected_sources:
            st.success("✅ **已选择的数据类型**：\n" + "\n".join(selected_sources))
        else:
            st.warning("⚠️ 至少需要选择一种数据类型（SKU或件数）")
        
        # 分析流程说明
        st.info("""
        📊 **分析流程**：
        1. **数据处理**：根据选择的数据类型进行智能处理（原始数据聚合 vs 聚合数据汇总）
        2. **趋势分析**：生成日入库趋势结果（X轴：日期，Y轴：有数据的指标）
        3. **统计分析**：计算波动性等关键指标  
        4. **优化建议**：基于数据模式提供入库优化建议
        """)
        
        return True
    
    @staticmethod
    def _render_packing_metrics(summary_stats):
        """渲染装箱分析关键指标"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("有效SKU数", summary_stats['total_sku_count'])
        with col2:
            st.metric("总库存件数", f"{summary_stats['total_inventory']:,}")
        with col3:
            st.metric("总需箱子数", f"{summary_stats['total_boxes_needed']:.0f}")
        with col4:
            st.metric("装不下SKU数", summary_stats['cannot_pack_items'])
        with col5:
            st.metric("平均装载率", f"{summary_stats['avg_utilization']:.1%}")
    
    @staticmethod
    def _render_large_dataset_summary(summary_stats, data_unit):
        """渲染大数据集的简化摘要"""

        
        st.write("📊 **装箱分析摘要:**")
        
        # 简化的统计表
        summary_data = {
            "分析项目": ["总SKU数", "可装箱SKU", "装不下SKU", "总库存件数", "总需箱子数", "装箱成功率"],
            "统计结果": [
                f"{summary_stats['total_sku_count']:,} 个",
                f"{summary_stats['can_pack_items']:,} 个",
                f"{summary_stats['cannot_pack_items']:,} 个", 
                f"{summary_stats['total_inventory']:,} 件",
                f"{summary_stats['total_boxes_needed']:.0f} 个",
                f"{summary_stats['success_rate']:.1f}%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        

        
        if summary_stats['avg_boxes_per_sku'] > 10:
            st.write(f"📦 **平均每SKU需要 {summary_stats['avg_boxes_per_sku']:.1f} 个箱子，建议考虑批量装箱策略**")
        

    
    @staticmethod
    def _render_small_dataset_details(packing_results, data_unit):
        """渲染小数据集的详细信息"""
        st.write("📊 **装箱分析结果:**")
        
        try:
            result_data = []
            conversion_factor = PACKING_CONFIG["unit_conversion"][data_unit]
            display_rows = min(len(packing_results), PACKING_CONFIG["preview_rows"])
            
            for result in packing_results[:display_rows]:
                row_data = {
                    'SKU': f"SKU_{result['SKU_index'] + 1}",
                    f'长({data_unit})': f"{result['goods_length_mm'] / conversion_factor:.1f}",
                    f'宽({data_unit})': f"{result['goods_width_mm'] / conversion_factor:.1f}",
                    f'高({data_unit})': f"{result['goods_height_mm'] / conversion_factor:.1f}",
                    '库存': int(result['inventory_qty']),
                    '最大装箱': int(result['max_per_box']) if result['max_per_box'] != float('inf') else '装不下',
                    '需要箱数': f"{result['boxes_needed']:.0f}" if result['boxes_needed'] != float('inf') else '∞'
                }
                
                # 添加重量信息（如果有）
                if result.get('weight_kg') is not None:
                    weight_unit = st.session_state.get("装箱分析_weight_unit", "kg")
                    weight_conversion = PACKING_CONFIG["weight_conversion"][weight_unit]
                    display_weight = result['weight_kg'] / weight_conversion
                    row_data[f'重量({weight_unit})'] = f"{display_weight:.2f}"
                    
                    # 显示重量限制信息
                    if result.get('max_per_box_by_weight') is not None:
                        row_data['重量限制装箱'] = int(result['max_per_box_by_weight'])
                
                result_data.append(row_data)
            
            if result_data:
                result_df = pd.DataFrame(result_data)
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                
                if len(packing_results) > display_rows:
                    st.info(f"💡 仅显示前{display_rows}行，完整数据请使用导出功能（共{len(packing_results)}行）")
        
        except Exception as e:
            st.error(f"表格展示出现问题，跳过详细展示: {str(e)}")
            st.info("💡 请使用下方导出功能获取完整分析结果")
    
    @staticmethod
    def _render_export_buttons(packing_results, summary_stats, data_unit, container_info):
        """渲染导出按钮"""
        st.write("---")
        st.write("**📥 数据导出**")

        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            csv_data = UIComponents._generate_basic_export(packing_results, data_unit)
            st.download_button(
                label="📊 导出基础结果",
                data=csv_data,
                file_name=f"装箱分析_基础结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_basic_safe",
                help="导出SKU信息和装箱结果"
            )
        
        with export_col2:
            csv_data = UIComponents._generate_summary_export(summary_stats, container_info)
            st.download_button(
                label="📈 导出统计摘要",
                data=csv_data,
                file_name=f"装箱分析_统计摘要_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_summary_safe",
                help="导出装箱统计汇总"
            )
        
        with export_col3:
            show_details = st.session_state.get("装箱分析_show_details", True)
            if show_details:
                csv_data = UIComponents._generate_detailed_export(packing_results, data_unit)
                st.download_button(
                    label="📋 导出详细数据",
                    data=csv_data,
                    file_name=f"装箱分析_详细结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_detailed_safe",
                    help="导出包含6种摆放方式的完整数据"
                )
    
    @staticmethod
    def _generate_basic_export(packing_results, data_unit):
        """生成基础导出数据"""
        conversion_factor = PACKING_CONFIG["unit_conversion"][data_unit]
        basic_data = []
        
        for result in packing_results:
            row_data = {
                'SKU行号': result['SKU_index'] + 1,
                f'货物长度({data_unit})': f"{result['goods_length_mm'] / conversion_factor:.2f}",
                f'货物宽度({data_unit})': f"{result['goods_width_mm'] / conversion_factor:.2f}",
                f'货物高度({data_unit})': f"{result['goods_height_mm'] / conversion_factor:.2f}",
                '库存件数': int(result['inventory_qty']),
                '最大装箱数': int(result['max_per_box']) if result['max_per_box'] != float('inf') else 0,
                '需要箱数': f"{result['boxes_needed']:.0f}" if result['boxes_needed'] != float('inf') else '装不下'
            }
            
            # 添加重量信息（如果有）
            if result.get('weight_kg') is not None:
                weight_unit = st.session_state.get("装箱分析_weight_unit", "kg")
                weight_conversion = PACKING_CONFIG["weight_conversion"][weight_unit]
                display_weight = result['weight_kg'] / weight_conversion
                row_data[f'货物重量({weight_unit})'] = f"{display_weight:.3f}"
                
                # 添加重量限制相关信息
                if result.get('max_per_box_by_size') is not None:
                    row_data['尺寸限制装箱'] = int(result['max_per_box_by_size'])
                if result.get('max_per_box_by_weight') is not None:
                    row_data['重量限制装箱'] = int(result['max_per_box_by_weight'])
            
            basic_data.append(row_data)
        
        export_df = pd.DataFrame(basic_data)
        return export_df.to_csv(index=False).encode('utf-8-sig')
    
    @staticmethod
    def _generate_summary_export(summary_stats, container_info):
        """生成统计摘要导出数据"""
        summary_report = {
            "装箱分析摘要": [
                f"容器规格: {container_info['length']}×{container_info['width']}×{container_info['height']} mm",
                f"容器重量限制: {container_info.get('weight_limit', 30)} kg",
                f"总SKU数: {summary_stats['total_sku_count']:,} 个",
                f"可装箱SKU: {summary_stats['can_pack_items']:,} 个",
                f"装不下SKU: {summary_stats['cannot_pack_items']:,} 个",
                f"总库存件数: {summary_stats['total_inventory']:,} 件",
                f"总需箱子数: {summary_stats['total_boxes_needed']:.0f} 个",
                f"装箱成功率: {summary_stats['success_rate']:.1f}%",
                f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
        }
        
        summary_df = pd.DataFrame.from_dict(summary_report, orient='index').T
        return summary_df.to_csv(index=False).encode('utf-8-sig')
    
    @staticmethod
    def _generate_detailed_export(packing_results, data_unit):
        """生成详细导出数据"""
        conversion_factor = PACKING_CONFIG["unit_conversion"][data_unit]
        detailed_data = []
        
        for result in packing_results:
            row_data = {
                'SKU行号': result['SKU_index'] + 1,
                f'货物长度({data_unit})': f"{result['goods_length_mm'] / conversion_factor:.2f}",
                f'货物宽度({data_unit})': f"{result['goods_width_mm'] / conversion_factor:.2f}",
                f'货物高度({data_unit})': f"{result['goods_height_mm'] / conversion_factor:.2f}",
                '库存件数': int(result['inventory_qty']),
                '最大装箱数': int(result['max_per_box']) if result['max_per_box'] != float('inf') else 0,
                '需要箱数': f"{result['boxes_needed']:.0f}" if result['boxes_needed'] != float('inf') else '装不下'
            }
            
            # 添加重量信息（如果有）
            if result.get('weight_kg') is not None:
                weight_unit = st.session_state.get("装箱分析_weight_unit", "kg")
                weight_conversion = PACKING_CONFIG["weight_conversion"][weight_unit]
                display_weight = result['weight_kg'] / weight_conversion
                row_data[f'货物重量({weight_unit})'] = f"{display_weight:.3f}"
                
                # 添加重量限制相关信息
                if result.get('max_per_box_by_size') is not None:
                    row_data['尺寸限制装箱'] = int(result['max_per_box_by_size'])
                if result.get('max_per_box_by_weight') is not None:
                    row_data['重量限制装箱'] = int(result['max_per_box_by_weight'])
            
            # 添加6种摆放方式
            for i, option in enumerate(result['packing_options'], 1):
                row_data[f'摆放方式{i}'] = int(option)
            
            detailed_data.append(row_data)
        
        detailed_df = pd.DataFrame(detailed_data)
        return detailed_df.to_csv(index=False).encode('utf-8-sig')
    
    @staticmethod
    def _render_optimization_suggestions(suggestions):
        """渲染优化建议"""
        st.write("---")
        st.write("💡 **装箱优化建议**")
        
        for suggestion in suggestions:
            st.write(suggestion)
        
        st.write("📋 详细分析和优化建议请查看导出的Excel文件")
    


    @staticmethod
    def render_order_structure_analysis_config(columns):
        """渲染订单结构分析配置界面"""
        try:
            st.markdown("#### 📋 订单结构分析配置")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**📋 选择分析列:**")
                
                # 订单列选择
                order_column = st.selectbox(
                    "📦 订单号列",
                    options=columns,
                    key="订单结构分析_order_column",
                    help="选择标识订单的列，如订单号、单据号等"
                )
                
                # 商品列选择
                item_column = st.selectbox(
                    "🏷️ 商品列",
                    options=columns,
                    key="订单结构分析_item_column",
                    help="选择标识商品的列，如SKU、物料编码等"
                )
                
                # 数量列选择
                quantity_column = st.selectbox(
                    "🔢 数量列",
                    options=columns,
                    key="订单结构分析_quantity_column",
                    help="选择数量列，如出库数量、需求数量等"
                )
                
                # 金额列选择（可选）
                amount_options = ["无金额列"] + columns
                amount_column = st.selectbox(
                    "💰 金额列（可选）",
                    options=amount_options,
                    key="订单结构分析_amount_column",
                    help="选择金额列进行价值分析，可选"
                )
                
                # 分析参数配置
                st.markdown("**⚙️ 分析参数:**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    min_order_items = st.number_input(
                        "最小订单商品数",
                        min_value=1,
                        max_value=100,
                        value=1,
                        key="订单结构分析_min_order_items",
                        help="分析的最小订单商品种类数"
                    )
                    
                    top_items_count = st.number_input(
                        "热门商品数量",
                        min_value=5,
                        max_value=100,
                        value=20,
                        key="订单结构分析_top_items_count",
                        help="显示前N个热门商品"
                    )
                
                with col_b:
                    order_size_threshold = st.number_input(
                        "大订单阈值",
                        min_value=1,
                        max_value=1000,
                        value=10,
                        key="订单结构分析_order_size_threshold",
                        help="区分大小订单的商品数量阈值"
                    )
                    
                    show_detailed_stats = st.checkbox(
                        "显示详细统计",
                        value=True,
                        key="订单结构分析_show_detailed_stats",
                        help="是否显示详细的订单结构统计信息"
                    )
            
            with col2:
                # 配置验证和状态显示
                config_valid = True
                
                if not order_column or not item_column or not quantity_column:
                    config_valid = False
                    st.warning("⚠️ **配置不完整**\n\n请选择必需的订单号、商品和数量列")
                else:
                    st.success("✅ **订单结构分析配置完成**")
                    st.info(f"📦 **订单列**: {order_column}")
                    st.info(f"🏷️ **商品列**: {item_column}")
                    st.info(f"🔢 **数量列**: {quantity_column}")
                    if amount_column != "无金额列":
                        st.info(f"💰 **金额列**: {amount_column}")
                    
                    # 显示分析参数
                    st.markdown("**分析参数:**")
                    st.caption(f"• 最小订单商品数: {min_order_items}")
                    st.caption(f"• 热门商品数量: {top_items_count}")
                    st.caption(f"• 大订单阈值: {order_size_threshold}")
                    st.caption(f"• 详细统计: {'是' if show_detailed_stats else '否'}")
            
            return config_valid
            
        except Exception as e:
            st.error(f"❌ 订单结构分析配置错误: {str(e)}")
            return False

    @staticmethod
    def render_data_cleaning_config(columns):
        """渲染高级异常数据清理配置界面"""
        from config import MATH_OPERATORS, LOGIC_OPERATORS
        
        st.write("### 🔍 异常数据清洗配置")
        st.caption("设置数据筛选和清洗条件，找出符合条件的异常数据进行处理")
        
        # 条件组管理
        st.write("**🎯 条件组设置**")
        st.caption("💡 条件组内的条件之间是 **AND（且）** 关系，条件组之间的关系可以选择")
        
        # 初始化：默认有1个条件组及1个条件
        if "异常数据清洗_group_count" not in st.session_state:
            st.session_state["异常数据清洗_group_count"] = 1
            # 为第一个条件组设置默认1个条件
            st.session_state["condition_count_异常数据清洗_1"] = 1
        
        col1, col2 = st.columns([3, 1])
        with col1:
            current_groups = st.session_state.get('异常数据清洗_group_count', 1)
            st.write(f"当前已设置 {current_groups} 个条件组")
        with col2:
            if st.button("➕ 添加条件组", key="异常数据清洗_add_group"):
                st.session_state["异常数据清洗_group_count"] += 1
                # 新增条件组时，默认增加1个条件
                new_group_id = st.session_state["异常数据清洗_group_count"]
                st.session_state[f"condition_count_异常数据清洗_{new_group_id}"] = 1
                st.rerun()
        
        # 显示条件组
        group_count = st.session_state.get("异常数据清洗_group_count", 1)
        
        # 条件组间的总体逻辑关系（如果有多个条件组）
        if group_count > 1:
            st.write("**🔗 条件组间逻辑关系：**")
            group_logic = st.radio(
                "所有条件组之间的关系",
                options=["OR", "AND"],
                format_func=lambda x: "或 (OR) - 满足任一条件组即为异常" if x == "OR" else "且 (AND) - 必须同时满足所有条件组才为异常",
                key="异常数据清洗_overall_group_logic",
                horizontal=True
            )
            st.session_state["异常数据清洗_overall_logic"] = group_logic
        
        # 显示所有条件组
        all_groups_conditions = []
        for group_id in range(1, group_count + 1):
            # 使用HTML内联布局，让删除按钮紧贴在标题右侧
            col1, col2 = st.columns([11, 1])
            with col1:
                st.markdown(f"#### 📋 条件组 {group_id}")
            with col2:
                # 添加垂直对齐，让按钮与标题水平对齐
                st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"delete_group_异常数据清洗_{group_id}", help=f"删除条件组 {group_id}"):
                    st.session_state["异常数据清洗_group_count"] = max(0, group_count - 1)
                    st.rerun()
            
            group_conditions = UIComponents._render_condition_group_enhanced(f"异常数据清洗_{group_id}", columns, group_id)
            all_groups_conditions.append(group_conditions)
        
        st.session_state["异常数据清洗_all_conditions"] = all_groups_conditions
        
        # 检查是否有有效条件
        if all_groups_conditions and any(all_groups_conditions):
            return True
        
        return False
    
    @staticmethod
    def _render_condition_group_enhanced(group_key, columns, group_id):
        """渲染增强版单个条件组（支持多列选择）"""
        from config import MATH_OPERATORS
        
        if f"condition_count_{group_key}" not in st.session_state:
            st.session_state[f"condition_count_{group_key}"] = 1  # 默认有1个条件
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**条件组 {group_id} 设置**")
            st.caption("🔗 组内条件为 **AND（且）** 关系：所有条件都必须满足")
        with col2:
            if st.button("➕ 添加条件", key=f"add_condition_{group_key}"):
                st.session_state[f"condition_count_{group_key}"] += 1
                st.rerun()
        
        condition_count = st.session_state[f"condition_count_{group_key}"]
        conditions = []
        
        with st.container():
            for i in range(condition_count):
                # 修改列布局：数据列(2) | 运算符(1.2) | 数据类型(1.2) | 值(1.5) | 删除(0.6)
                col1, col2, col3, col4, col5 = st.columns([2, 1.2, 1.2, 1.5, 0.6])
                
                with col1:
                    selected_columns = st.multiselect(
                        f"条件{i+1}-数据列",
                        options=columns,
                        key=f"condition_{group_key}_{i}_columns",
                        help="可以选择多个列，条件将应用到所选的所有列"
                    )
                
                with col2:
                    operator = st.selectbox(
                        f"条件{i+1}-运算符",
                        options=list(MATH_OPERATORS.keys()),
                        key=f"condition_{group_key}_{i}_operator"
                    )
                
                with col3:
                    if operator not in ["contains", "not_contains"]:
                        data_type = st.selectbox(
                            f"条件{i+1}-数据类型",
                            options=["整数", "小数"],
                            key=f"condition_{group_key}_{i}_type",
                            help="选择数值的数据类型"
                        )
                    else:
                        # 对于文本操作，显示占位符但不可选择
                        data_type = st.selectbox(
                            f"条件{i+1}-数据类型",
                            options=["文本"],
                            disabled=True,
                            key=f"condition_{group_key}_{i}_type_placeholder"
                        )
                
                with col4:
                    # 获取现有值以避免重置
                    existing_value_key = f"condition_{group_key}_{i}_value"
                    existing_min_key = f"condition_{group_key}_{i}_min"
                    existing_max_key = f"condition_{group_key}_{i}_max"
                    existing_text_key = f"condition_{group_key}_{i}_text"
                    
                    if operator in ["in_range", "not_in_range"]:
                        # 范围输入：使用两个子列
                        subcol1, subcol2, subcol3 = st.columns([1, 0.2, 1])
                        with subcol1:
                            if data_type == "整数":
                                if existing_min_key in st.session_state:
                                    min_val = st.number_input(f"最小值", key=existing_min_key, step=1)
                                else:
                                    min_val = st.number_input(f"最小值", key=existing_min_key, step=1, value=0)
                            else:
                                if existing_min_key in st.session_state:
                                    min_val = st.number_input(f"最小值", key=existing_min_key, format="%.4f", step=0.0001)
                                else:
                                    min_val = st.number_input(f"最小值", key=existing_min_key, format="%.4f", step=0.0001, value=0.0)
                        with subcol2:
                            st.markdown("<div style='text-align: center; margin-top: 28px;'>~</div>", unsafe_allow_html=True)
                        with subcol3:
                            if data_type == "整数":
                                if existing_max_key in st.session_state:
                                    max_val = st.number_input(f"最大值", key=existing_max_key, step=1, label_visibility="collapsed")
                                else:
                                    max_val = st.number_input(f"最大值", key=existing_max_key, step=1, value=100, label_visibility="collapsed")
                                value = [int(min_val), int(max_val)]
                            else:
                                if existing_max_key in st.session_state:
                                    max_val = st.number_input(f"最大值", key=existing_max_key, format="%.4f", step=0.0001, label_visibility="collapsed")
                                else:
                                    max_val = st.number_input(f"最大值", key=existing_max_key, format="%.4f", step=0.0001, value=100.0, label_visibility="collapsed")
                                value = [round(min_val, 4), round(max_val, 4)]
                    elif operator in ["contains", "not_contains"]:
                        if existing_text_key in st.session_state:
                            value = st.text_input(f"条件{i+1}-文本", key=existing_text_key)
                        else:
                            value = st.text_input(f"条件{i+1}-文本", key=existing_text_key, value="")
                    else:
                        # 单值输入
                        if data_type == "整数":
                            if existing_value_key in st.session_state:
                                input_value = st.number_input(f"条件{i+1}-值", key=existing_value_key, step=1)
                            else:
                                input_value = st.number_input(f"条件{i+1}-值", key=existing_value_key, step=1, value=0)
                            value = int(input_value)
                        elif data_type == "小数":
                            if existing_value_key in st.session_state:
                                input_value = st.number_input(f"条件{i+1}-值", key=existing_value_key, format="%.4f", step=0.0001)
                            else:
                                input_value = st.number_input(f"条件{i+1}-值", key=existing_value_key, format="%.4f", step=0.0001, value=0.0)
                            value = round(input_value, 4)
                        else:
                            # 文本类型，不应该到这里，但为了安全
                            value = ""
                
                with col5:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_condition_{group_key}_{i}", help="删除此条件"):
                        st.session_state[f"condition_count_{group_key}"] = max(0, condition_count - 1)
                        st.rerun()
                
                condition = {
                    "columns": selected_columns,
                    "operator": operator,
                    "value": value
                }
                conditions.append(condition)
                
                if i < condition_count - 1:
                    st.markdown("<center>🔗 <b>且 (AND)</b></center>", unsafe_allow_html=True)
        
        return conditions
    
    @staticmethod
    def render_reset_button():
        """渲染重置按钮"""
        if st.button("🔄 重新选择"):
            keys_to_clear = ['sheet_confirmed', 'analysis_type', 'dimensions_confirmed', 
                           'analysis_confirmed', 'selected_dimensions', 'analysis_name', 'data_loaded']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and key.startswith('data_'):
                    del st.session_state[key]
            
            # 页面自动滚动到顶部
            st.markdown("""
            <script>
            setTimeout(function() {
                window.scrollTo(0, 0);
            }, 100);
            </script>
            """, unsafe_allow_html=True)
            st.rerun() 