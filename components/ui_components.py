# -*- coding: utf-8 -*-
"""
UI组件模块 - 包含所有Streamlit界面组件和展示逻辑
"""

import streamlit as st
import pandas as pd
from config import *
from core.packing_analysis import PackingAnalyzer
from utils import DataUtils

class UIComponents:
    """UI组件管理器"""
    
    @staticmethod
    def render_analysis_type_selection():
        """渲染分析类型选择界面"""
        st.subheader("🎯 第二步：选择分析类型")
        
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
            st.info("👆 请选择要执行的分析类型")
    
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
        
        # 使用工具函数获取Excel信息
        excel_info = DataUtils.get_excel_sheets_info(uploaded_file)
        
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
            # 清理旧的数据缓存
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
        st.dataframe(df.head(10), use_container_width=True)
    
    @staticmethod
    def render_dimension_selection(analysis_type, analysis_name):
        """渲染分析维度选择界面"""
        st.subheader("🔍 第三步：选择分析维度")
        
        available_dimensions = ANALYSIS_TYPE_DIMENSIONS[analysis_type]
        st.write(f"📊 请勾选要执行的 **{analysis_name}** 维度：")
        
        preprocessing_dimensions = list(PREPROCESSING_DIMENSIONS.keys())
        analysis_dimensions = available_dimensions
        
        current_selected_dimensions = []
        
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
                        col1, col2 = st.columns([3, 2])
                        with col1:
                            UIComponents._render_container_selection_compact()
                        with col2:
                            st.success("✅ **容器标准化完成！**")
                            st.caption("")  # 空行保持高度一致
                    elif dimension == "异常数据清洗":
                        # 使用两列布局，将绿色提示放在右侧
                        col1, col2 = st.columns([3, 2])
                        with col1:
                            st.info("📊 数据清洗配置将在后续步骤中详细设置")
                        with col2:
                            st.success("✅ **数据清洗已启用！**")
                            st.caption("")  # 空行保持高度一致
        
        # 显示分析步骤
        if analysis_dimensions:
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
        container_size = st.selectbox(
            "容器尺寸 (长x宽x高 mm)",
            options=list(CONTAINER_SPECS.keys()),
            key="selected_container_size",
            help="选择的容器规格将应用于所有后续分析"
        )
        
        dimensions = CONTAINER_SPECS[container_size]
        length, width, height = dimensions['length'], dimensions['width'], dimensions['height']
        st.caption("")  # 添加空行保持与右侧绿色框高度一致
        
        st.session_state.container_length = length
        st.session_state.container_width = width
        st.session_state.container_height = height
    
    @staticmethod
    def render_packing_analysis_config(columns):
        """渲染装箱分析配置界面"""
        st.write("📦 请配置装箱分析参数：")
        
        # 显示当前选定的容器（如果有）
        if st.session_state.get("container_length"):
            current_container = st.session_state.get("selected_container_size", "600x400x300")
            length = st.session_state.get("container_length")
            width = st.session_state.get("container_width") 
            height = st.session_state.get("container_height")
            st.info(f"✅ 当前货箱规格: {current_container} (长{length}mm × 宽{width}mm × 高{height}mm)")
        else:
            st.warning("⚠️ 请先在前置处理中选择容器规格")
            return False
        
        st.write("**🎯 数据列配置**")
        st.caption("选择数据中对应货物尺寸和库存的列")
        
        # 列选择
        col1, col2 = st.columns(2)
        with col1:
            # 获取已保存的选择，如果没有则使用第一个选项作为默认值
            saved_length = st.session_state.get("装箱分析_length_column")
            length_index = 0
            if saved_length and saved_length in columns:
                length_index = columns.index(saved_length)
            
            length_column = st.selectbox(
                "货物长度列",
                options=columns,
                index=length_index,
                key="装箱分析_length_column",
                help="选择包含货物长度数据的列"
            )
            
            saved_width = st.session_state.get("装箱分析_width_column")
            width_index = 0
            if saved_width and saved_width in columns:
                width_index = columns.index(saved_width)
            
            width_column = st.selectbox(
                "货物宽度列", 
                options=columns,
                index=width_index,
                key="装箱分析_width_column",
                help="选择包含货物宽度数据的列"
            )
        
        with col2:
            saved_height = st.session_state.get("装箱分析_height_column")
            height_index = 0
            if saved_height and saved_height in columns:
                height_index = columns.index(saved_height)
            
            height_column = st.selectbox(
                "货物高度列",
                options=columns,
                index=height_index,
                key="装箱分析_height_column", 
                help="选择包含货物高度数据的列"
            )
            
            saved_inventory = st.session_state.get("装箱分析_inventory_column")
            inventory_index = 0
            if saved_inventory and saved_inventory in columns:
                inventory_index = columns.index(saved_inventory)
            
            inventory_column = st.selectbox(
                "库存件数列",
                options=columns,
                index=inventory_index,
                key="装箱分析_inventory_column",
                help="选择包含库存件数的列"
            )
        
        st.write("**📏 数据单位设置**")
        # 获取已保存的数据单位选择
        saved_unit = st.session_state.get("装箱分析_data_unit", "cm")
        unit_options = ["mm", "cm", "m"]
        unit_index = 1  # 默认选择cm
        if saved_unit in unit_options:
            unit_index = unit_options.index(saved_unit)
        
        data_unit = st.selectbox(
            "货物尺寸数据单位",
            options=unit_options,
            index=unit_index,
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
        
        st.write("**⚙️ 分析选项**")
        # 获取已保存的详细显示选择
        saved_details = st.session_state.get("装箱分析_show_details", True)
        
        show_details = st.checkbox(
            "显示详细装箱计算过程",
            value=saved_details,
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
        st.warning(f"⚠️ 数据量较大({summary_stats['total_sku_count']} 行)，为确保系统稳定，将只显示统计摘要")
        
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
        
        # 简化的问题分析
        if summary_stats['cannot_pack_items'] > 0:
            st.write(f"⚠️ **发现 {summary_stats['cannot_pack_items']} 个SKU无法装入当前容器，建议：**")
            st.write("• 考虑使用更大规格的容器")
            st.write("• 检查货物尺寸数据是否正确")
            st.write("• 考虑拆分大件货物")
        
        if summary_stats['avg_boxes_per_sku'] > 10:
            st.write(f"📦 **平均每SKU需要 {summary_stats['avg_boxes_per_sku']:.1f} 个箱子，建议考虑批量装箱策略**")
        
        st.info("💡 详细数据可通过下方导出功能获取，避免前端展示导致系统卡顿")
    
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
        st.info("💡 推荐使用导出功能获取完整分析结果，避免前端展示导致的性能问题")
        
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
            basic_data.append({
                'SKU行号': result['SKU_index'] + 1,
                f'货物长度({data_unit})': f"{result['goods_length_mm'] / conversion_factor:.2f}",
                f'货物宽度({data_unit})': f"{result['goods_width_mm'] / conversion_factor:.2f}",
                f'货物高度({data_unit})': f"{result['goods_height_mm'] / conversion_factor:.2f}",
                '库存件数': int(result['inventory_qty']),
                '最大装箱数': int(result['max_per_box']) if result['max_per_box'] != float('inf') else 0,
                '需要箱数': f"{result['boxes_needed']:.0f}" if result['boxes_needed'] != float('inf') else '装不下'
            })
        
        export_df = pd.DataFrame(basic_data)
        return export_df.to_csv(index=False).encode('utf-8-sig')
    
    @staticmethod
    def _generate_summary_export(summary_stats, container_info):
        """生成统计摘要导出数据"""
        summary_report = {
            "装箱分析摘要": [
                f"容器规格: {container_info['length']}×{container_info['width']}×{container_info['height']} mm",
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
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"#### 📋 条件组 {group_id}")
            with col2:
                if st.button(f"🗑️ 删除", key=f"delete_group_异常数据清洗_{group_id}", help=f"删除条件组 {group_id}"):
                    st.session_state["异常数据清洗_group_count"] = max(0, group_count - 1)
                    st.rerun()
            
            group_conditions = UIComponents._render_condition_group_enhanced(f"异常数据清洗_{group_id}", columns, group_id)
            all_groups_conditions.append(group_conditions)
        
        st.session_state["异常数据清洗_all_conditions"] = all_groups_conditions
        
        # 选择处理方式
        if all_groups_conditions and any(all_groups_conditions):
            st.write("---")
            st.write("**⚙️ 数据处理方式**")
            action = st.radio(
                "对符合条件的异常数据执行",
                options=["删除", "标记异常", "导出到新文件"],
                key="异常数据清洗_action",
                help="删除：从数据中移除 | 标记异常：添加标记列 | 导出：保存到单独文件"
            )
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
                # 修改列布局：数据列(2.5) | 运算符(1) | 数据类型(1) | 值(2) | 删除(0.5)
                col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 2, 0.5])
                
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