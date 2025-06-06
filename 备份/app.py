import streamlit as st
import pandas as pd
from data_cleaning import read_and_clean, basic_data_cleaning, advanced_data_cleaning
from report_generator import AnalysisReport

# 多语言支持（初始为中文）
LANG = {
    "title": "库存与出入库分析系统",
    "upload": "上传Excel文件",
    "select_analysis": "请选择分析类型",
    "inventory_analysis": "库存分析",
    "inbound_analysis": "入库分析", 
    "outbound_analysis": "出库分析",
    "select_sheet": "请选择要分析的Sheet",
    "confirm_button": "确认",
    "select_dimensions": "请选择要执行的分析维度",
    "next_step": "下一步：配置分析参数",
    "start_analysis": "开始执行分析",
    "export_pdf": "导出完整PDF报告",
    "preview": "数据前10行预览",
    "data_info": "数据基本信息",
}

# 分析类型配置
ANALYSIS_TYPES = {
    LANG["inventory_analysis"]: {
        "icon": "📦",
        "description": "分析当前库存状态、库存周转率、安全库存等指标",
        "key": "inventory"
    },
    LANG["inbound_analysis"]: {
        "icon": "📥", 
        "description": "分析入库趋势、供应商表现、入库效率等指标",
        "key": "inbound"
    },
    LANG["outbound_analysis"]: {
        "icon": "📤",
        "description": "分析出库趋势、客户需求、出库效率等指标", 
        "key": "outbound"
    }
}

# 分析维度配置
ANALYSIS_DIMENSIONS = {
    "ABC分析": {
        "description": "按照重要性对物品进行分类，识别核心、重要和一般物品",
        "icon": "📊", 
        "method": "abc_analysis",
        "config_type": "abc_analysis"
    },
    "装箱分析": {
        "description": "分析装箱效率、箱型分布和装箱优化建议",
        "icon": "📦",
        "method": "packing_analysis",
        "config_type": "packing_analysis"
    },
    "容器对比分析": {
        "description": "对比不同容器规格的效率和适用性，提供容器选择建议",
        "icon": "🔍",
        "method": "container_comparison_analysis",
        "config_type": "container_comparison"
    },
    "SKU件数分析": {
        "description": "分析SKU入库件数分布、热门SKU识别和库存结构",
        "icon": "🔢",
        "method": "sku_quantity_analysis",
        "config_type": "sku_analysis"
    },
    "入库箱数分析": {
        "description": "分析入库箱数趋势、箱型分布和入库效率",
        "icon": "📥",
        "method": "inbound_box_analysis",
        "config_type": "inbound_analysis"
    },
    "订单结构分析": {
        "description": "分析订单构成、订单类型分布和订单特征",
        "icon": "📋",
        "method": "order_structure_analysis",
        "config_type": "order_analysis"
    },
    "单件多件分析": {
        "description": "分析单件订单与多件订单的比例和特征差异",
        "icon": "🔀",
        "method": "single_multi_analysis",
        "config_type": "single_multi_analysis"
    },
    "命中率分析": {
        "description": "分析拣货命中率、准确率和效率指标",
        "icon": "🎯",
        "method": "hit_rate_analysis",
        "config_type": "hit_rate_analysis"
    }
}

# 分析类型对应的维度
ANALYSIS_TYPE_DIMENSIONS = {
    "inventory": ["ABC分析", "装箱分析", "容器对比分析"],
    "inbound": ["装箱分析", "SKU件数分析", "入库箱数分析", "容器对比分析"],
    "outbound": ["订单结构分析", "ABC分析", "单件多件分析", "命中率分析", "容器对比分析"]
}

# 前置处理维度
PREPROCESSING_DIMENSIONS = {
    "异常数据清洗": {
        "description": "检测并处理数据中的异常值、缺失值和不合理数据",
        "icon": "🧹",
        "method": "clean_abnormal_data",
        "config_type": "abnormal_cleaning"
    },
    "容器选择": {
        "description": "选择标准容器规格，后续分析将基于选定容器进行",
        "icon": "📦",
        "method": "container_selection",
        "config_type": "container_selection"
    }
}

# 数学运算符配置
MATH_OPERATORS = {
    ">": "大于",
    ">=": "大于等于", 
    "<": "小于",
    "<=": "小于等于",
    "==": "等于",
    "!=": "不等于",
    "in_range": "在范围内",
    "not_in_range": "不在范围内",
    "contains": "包含",
    "not_contains": "不包含"
}

# 逻辑运算符配置
LOGIC_OPERATORS = {
    "AND": "且",
    "OR": "或"
}

def load_and_cache_data(uploaded_file, sheet_name):
    """加载并缓存数据，避免重复加载"""
    cache_key = f"data_{sheet_name}"
    
    if cache_key not in st.session_state:
        with st.spinner('正在加载...'):
            df = read_and_clean(uploaded_file, sheet_name=sheet_name)
            st.session_state[cache_key] = df
            st.session_state.data_loaded = True
    
    return st.session_state[cache_key]

def render_advanced_cleaning_config(dimension, columns):
    """渲染统一的条件清洗配置界面"""
    st.write("### 🔍 异常数据清洗配置")
    st.caption("设置数据筛选和清洗条件，找出符合条件的异常数据进行处理")
    
    # 条件组管理
    st.write("**🎯 条件组设置**")
    st.caption("💡 条件组内的条件之间是 **AND（且）** 关系，条件组之间的关系可以选择")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        current_groups = st.session_state.get(f'{dimension}_group_count', 0)
        st.write(f"当前已设置 {current_groups} 个条件组")
    with col2:
        if st.button("➕ 添加条件组", key=f"{dimension}_add_group"):
            if f"{dimension}_group_count" not in st.session_state:
                st.session_state[f"{dimension}_group_count"] = 0
            st.session_state[f"{dimension}_group_count"] += 1
    
    # 显示条件组
    group_count = st.session_state.get(f"{dimension}_group_count", 0)
    all_groups_conditions = []
    
    if group_count == 0:
        st.info("💡 点击上方 **添加条件组** 按钮开始设置清洗条件")
        return
    
    # 条件组间的总体逻辑关系（如果有多个条件组）
    if group_count > 1:
        st.write("**🔗 条件组间逻辑关系：**")
        group_logic = st.radio(
            "所有条件组之间的关系",
            options=["OR", "AND"],
            format_func=lambda x: "或 (OR) - 满足任一条件组即为异常" if x == "OR" else "且 (AND) - 必须同时满足所有条件组才为异常",
            key=f"{dimension}_overall_group_logic",
            horizontal=True
        )
        st.session_state[f"{dimension}_overall_logic"] = group_logic
    
    # 显示所有条件组
    for group_id in range(1, group_count + 1):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"#### 📋 条件组 {group_id}")
        with col2:
            if st.button(f"🗑️ 删除", key=f"delete_group_{dimension}_{group_id}", help=f"删除条件组 {group_id}"):
                st.session_state[f"{dimension}_group_count"] = max(0, group_count - 1)
                st.rerun()
        
        group_conditions = render_condition_group_enhanced(f"{dimension}_{group_id}", columns, group_id)
        all_groups_conditions.append(group_conditions)
    
    st.session_state[f"{dimension}_all_conditions"] = all_groups_conditions
    
    # 选择处理方式
    if all_groups_conditions and any(all_groups_conditions):
        st.write("---")
        st.write("**⚙️ 数据处理方式**")
        action = st.radio(
            "对符合条件的异常数据执行",
            options=["删除", "标记异常", "导出到新文件"],
            key=f"{dimension}_action",
            help="删除：从数据中移除 | 标记异常：添加标记列 | 导出：保存到单独文件"
        )

def render_condition_group_enhanced(group_key, columns, group_id):
    """渲染增强版单个条件组（支持多列选择）"""
    
    if f"condition_count_{group_key}" not in st.session_state:
        st.session_state[f"condition_count_{group_key}"] = 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**条件组 {group_id} 设置**")
        st.caption("🔗 组内条件为 **AND（且）** 关系：所有条件都必须满足")
    with col2:
        if st.button("➕ 添加条件", key=f"add_condition_{group_key}"):
            st.session_state[f"condition_count_{group_key}"] += 1
    
    condition_count = st.session_state[f"condition_count_{group_key}"]
    conditions = []
    
    if condition_count == 0:
        st.info("💡 点击 **添加条件** 按钮开始设置")
        return conditions
    
    with st.container():
        for i in range(condition_count):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
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
                    format_func=lambda x: MATH_OPERATORS[x],
                    key=f"condition_{group_key}_{i}_operator"
                )
            
            with col3:
                if operator in ["in_range", "not_in_range"]:
                    min_val = st.number_input(f"条件{i+1}-最小值", key=f"condition_{group_key}_{i}_min")
                    max_val = st.number_input(f"条件{i+1}-最大值", key=f"condition_{group_key}_{i}_max")
                    value = [min_val, max_val]
                elif operator in ["contains", "not_contains"]:
                    value = st.text_input(f"条件{i+1}-文本", key=f"condition_{group_key}_{i}_text")
                else:
                    value = st.number_input(f"条件{i+1}-值", key=f"condition_{group_key}_{i}_value")
            
            with col4:
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

def render_dimension_config(dimension, columns):
    """渲染分析维度的配置选项"""
    
    # 检查是否是前置处理维度
    if dimension in PREPROCESSING_DIMENSIONS:
        dimension_info = PREPROCESSING_DIMENSIONS[dimension]
        config_type = dimension_info["config_type"]
        
        st.write(f"**{dimension_info['icon']} {dimension}** 配置")
        st.caption(dimension_info['description'])
        
        if config_type == "abnormal_cleaning":
            render_advanced_cleaning_config(dimension, columns)
        
        elif config_type == "container_selection":
            st.write("📦 容器选择已在前置步骤配置完成")
            
            container_size = st.session_state.get("selected_container_size", "600x400x300")
            length = st.session_state.get("container_length", 600)
            width = st.session_state.get("container_width", 400) 
            height = st.session_state.get("container_height", 300)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("容器长度", f"{length} cm")
            with col2:
                st.metric("容器宽度", f"{width} cm")
            with col3:
                st.metric("容器高度", f"{height} cm")
            
            st.info("✅ 后续所有分析将基于此容器规格进行计算和优化")
        
        return
    
    # 原有的分析维度配置
    dimension_info = ANALYSIS_DIMENSIONS[dimension]
    config_type = dimension_info["config_type"]
    
    st.write(f"**{dimension_info['icon']} {dimension}** 配置")
    st.caption(dimension_info['description'])
    
    # 显示容器信息（如果已选择容器）
    if st.session_state.get("container_length"):
        length = st.session_state.get("container_length")
        width = st.session_state.get("container_width") 
        height = st.session_state.get("container_height")
        st.caption(f"📦 基于选定容器规格: {length}×{width}×{height} cm")
    
    if config_type == "abc_analysis":
        # ABC分析配置
        st.write("📊 请配置ABC分析参数：")
        
        col1, col2 = st.columns(2)
        with col1:
            analysis_column = st.selectbox(
                "选择分析列",
                options=columns,
                key=f"{dimension}_analysis_column"
            )
        
        with col2:
            abc_thresholds = st.selectbox(
                "ABC分类阈值",
                options=["标准(A:80%, B:15%, C:5%)", "自定义"],
                key=f"{dimension}_thresholds"
            )
        
        if abc_thresholds == "自定义":
            col1, col2, col3 = st.columns(3)
            with col1:
                a_threshold = st.slider("A类阈值(%)", 50, 90, 80, key=f"{dimension}_a_threshold")
            with col2:
                b_threshold = st.slider("B类阈值(%)", 10, 30, 15, key=f"{dimension}_b_threshold")
            with col3:
                c_threshold = st.slider("C类阈值(%)", 1, 20, 5, key=f"{dimension}_c_threshold")
    
    elif config_type == "packing_analysis":
        # 装箱分析配置
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
            return
        
        st.write("**🎯 数据列配置**")
        st.caption("选择数据中对应货物尺寸和库存的列")
        
        # 列选择
        col1, col2 = st.columns(2)
        with col1:
            length_column = st.selectbox(
                "货物长度列",
                options=columns,
                key=f"{dimension}_length_column",
                help="选择包含货物长度数据的列"
            )
            
            width_column = st.selectbox(
                "货物宽度列", 
                options=columns,
                key=f"{dimension}_width_column",
                help="选择包含货物宽度数据的列"
            )
        
        with col2:
            height_column = st.selectbox(
                "货物高度列",
                options=columns,
                key=f"{dimension}_height_column", 
                help="选择包含货物高度数据的列"
            )
            
            inventory_column = st.selectbox(
                "库存件数列",
                options=columns,
                key=f"{dimension}_inventory_column",
                help="选择包含库存件数的列"
            )
        
        st.write("**📏 数据单位设置**")
        data_unit = st.selectbox(
            "货物尺寸数据单位",
            options=["mm", "cm", "m"],
            index=1,  # 默认选择cm
            key=f"{dimension}_data_unit",
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
        show_details = st.checkbox(
            "显示详细装箱计算过程",
            value=True,
            key=f"{dimension}_show_details",
            help="显示每个SKU的6种摆放方式计算详情"
        )
        
        export_results = st.checkbox(
            "导出装箱分析结果",
            value=False,
            key=f"{dimension}_export_results",
            help="将分析结果导出为Excel文件"
        )
        
        st.write("**📊 分析说明**")
        st.info("💡 系统将自动分批处理全量数据，使用完整的6种摆放方式进行最优装箱计算")
    
    elif config_type == "container_comparison":
        # 容器对比分析配置
        st.write("🔍 请配置容器对比分析参数：")
        
        # 显示当前选定的容器（如果有）
        if st.session_state.get("container_length"):
            current_container = st.session_state.get("selected_container_size", "600x400x300")
            st.info(f"✅ 当前选定容器: {current_container}")
        
        # 选择要对比的容器规格
        comparison_containers = st.multiselect(
            "选择要对比的容器规格",
            options=["600x400x300", "650x450x350", "700x500x400", "800x600x450"],
            default=["600x400x300", "650x450x350"],
            key=f"{dimension}_comparison_containers",
            help="将对比这些容器规格的装载效率、空间利用率等指标"
        )
        
        # 对比指标选择
        comparison_metrics = st.multiselect(
            "选择对比指标",
            options=["装载效率", "空间利用率", "运输成本", "操作便利性", "标准化程度"],
            default=["装载效率", "空间利用率"],
            key=f"{dimension}_comparison_metrics",
            help="选择要对比分析的具体指标"
        )
        
        # 分析深度
        analysis_depth = st.selectbox(
            "分析深度",
            options=["基础对比", "详细分析", "优化建议"],
            key=f"{dimension}_analysis_depth",
            help="基础对比：简单指标对比 | 详细分析：深入分析各项指标 | 优化建议：提供具体优化方案"
        )
    
    else:
        # 其他分析类型的基本配置
        st.write("⚙️ 基础配置选项：")
        include_charts = st.checkbox(
            "生成图表",
            value=True,
            key=f"{dimension}_include_charts"
        )
        
        export_results = st.checkbox(
            "导出分析结果",
            value=False,
            key=f"{dimension}_export_results"
        ) 

def generate_pdf_report():
    """生成PDF报告"""
    try:
        report = AnalysisReport()
        
        for dimension in st.session_state.get('selected_dimensions', []):
            if dimension in PREPROCESSING_DIMENSIONS:
                dimension_info = PREPROCESSING_DIMENSIONS[dimension]
            elif dimension in ANALYSIS_DIMENSIONS:
                dimension_info = ANALYSIS_DIMENSIONS[dimension]
            else:
                continue
                
            result_data = {
                "description": dimension_info['description'],
                "method": dimension_info['method'],
                "status": "已完成",
                "config": "用户配置已应用"
            }
            report.add_analysis_result(dimension, result_data)
        
        report.add_summary_stats({
            "分析类型": st.session_state.get('analysis_name', 'N/A'),
            "数据源": st.session_state.get('selected_sheet', 'N/A'),
            "维度数量": len(st.session_state.get('selected_dimensions', [])),
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        analysis_info = {
            'analysis_name': st.session_state.get('analysis_name', 'N/A'),
            'selected_sheet': st.session_state.get('selected_sheet', 'N/A'),
            'selected_dimensions': st.session_state.get('selected_dimensions', []),
            'data_rows': len(st.session_state.get(f"data_{st.session_state.get('selected_sheet', '')}", pd.DataFrame())),
            'data_cols': len(st.session_state.get(f"data_{st.session_state.get('selected_sheet', '')}", pd.DataFrame()).columns)
        }
        
        return report.generate_pdf_report(analysis_info)
        
    except Exception as e:
        st.error(f"❌ PDF生成失败: {str(e)}")
        return None

def advanced_data_cleaning_enhanced(df, all_conditions, dimension, action):
    """增强版高级数据清洗函数"""
    try:
        import pandas as pd
        import numpy as np
        
        result_df = df.copy()
        group_results = []
        
        for group_id, group_conditions in enumerate(all_conditions, 1):
            if not group_conditions:
                continue
                
            group_mask = pd.Series([True] * len(df), index=df.index)
            
            for condition in group_conditions:
                columns = condition.get('columns', [])
                operator = condition.get('operator', '')
                value = condition.get('value', '')
                
                if not columns:
                    continue
                
                condition_mask = pd.Series([False] * len(df), index=df.index)
                
                for column in columns:
                    if column not in df.columns:
                        continue
                    
                    col_data = df[column]
                    
                    if operator == ">":
                        mask = pd.to_numeric(col_data, errors='coerce') > float(value)
                    elif operator == ">=":
                        mask = pd.to_numeric(col_data, errors='coerce') >= float(value)
                    elif operator == "<":
                        mask = pd.to_numeric(col_data, errors='coerce') < float(value)
                    elif operator == "<=":
                        mask = pd.to_numeric(col_data, errors='coerce') <= float(value)
                    elif operator == "==":
                        if isinstance(value, (int, float)):
                            mask = pd.to_numeric(col_data, errors='coerce') == float(value)
                        else:
                            mask = col_data.astype(str) == str(value)
                    elif operator == "!=":
                        if isinstance(value, (int, float)):
                            mask = pd.to_numeric(col_data, errors='coerce') != float(value)
                        else:
                            mask = col_data.astype(str) != str(value)
                    elif operator == "in_range":
                        if isinstance(value, list) and len(value) == 2:
                            numeric_data = pd.to_numeric(col_data, errors='coerce')
                            mask = (numeric_data >= float(value[0])) & (numeric_data <= float(value[1]))
                        else:
                            mask = pd.Series([False] * len(df), index=df.index)
                    elif operator == "not_in_range":
                        if isinstance(value, list) and len(value) == 2:
                            numeric_data = pd.to_numeric(col_data, errors='coerce')
                            mask = (numeric_data < float(value[0])) | (numeric_data > float(value[1]))
                        else:
                            mask = pd.Series([False] * len(df), index=df.index)
                    elif operator == "contains":
                        mask = col_data.astype(str).str.contains(str(value), na=False)
                    elif operator == "not_contains":
                        mask = ~col_data.astype(str).str.contains(str(value), na=False)
                    else:
                        mask = pd.Series([False] * len(df), index=df.index)
                    
                    mask = mask.fillna(False)
                    condition_mask = condition_mask | mask
                
                group_mask = group_mask & condition_mask
            
            group_results.append(group_mask)
        
        if group_results:
            overall_logic = st.session_state.get(f"{dimension}_overall_logic", "OR")
            final_mask = group_results[0]
            
            for i in range(1, len(group_results)):
                if overall_logic == "OR":
                    final_mask = final_mask | group_results[i]
                else:
                    final_mask = final_mask & group_results[i]
        else:
            final_mask = pd.Series([False] * len(df), index=df.index)
        
        abnormal_data = df[final_mask].copy()
        
        if action == "删除":
            result_df = df[~final_mask].copy()
        elif action == "标记异常":
            result_df = df.copy()
            result_df['异常标记'] = final_mask
        else:
            result_df = df.copy()
        
        return result_df, abnormal_data
        
    except Exception as e:
        st.error(f"❌ 高级清洗执行失败: {str(e)}")
        return df, pd.DataFrame()

def execute_analysis_dimension_with_container(df, dimension, container_info):
    """执行具体的分析维度（支持容器信息）"""
    dimension_info = ANALYSIS_DIMENSIONS[dimension]
    
    st.write(f"🔧 正在执行 **{dimension}**...")
    st.write(f"📝 描述: {dimension_info['description']}")
    
    if container_info:
        st.write(f"📦 容器规格: {container_info['size']} (容积: {container_info['volume']:,} cm³)")
    
    results = {}
    
    if dimension == "装箱分析":
        # 装箱分析逻辑
        length_column = st.session_state.get(f"{dimension}_length_column")
        width_column = st.session_state.get(f"{dimension}_width_column") 
        height_column = st.session_state.get(f"{dimension}_height_column")
        inventory_column = st.session_state.get(f"{dimension}_inventory_column")
        data_unit = st.session_state.get(f"{dimension}_data_unit", "cm")
        show_details = st.session_state.get(f"{dimension}_show_details", True)
        
        if not all([length_column, width_column, height_column, inventory_column]):
            results = {"error": "请先配置货物尺寸和库存列"}
        elif not container_info:
            results = {"error": "请先选择容器规格"}
        else:
            st.write(f"📦 基于容器规格 {container_info['size']} 执行装箱分析...")
            
            try:
                import pandas as pd
                import numpy as np
                
                # 单位转换系数
                unit_conversion = {"mm": 1, "cm": 10, "m": 1000}
                conversion_factor = unit_conversion[data_unit]
                
                # 容器尺寸（转换为mm）
                container_length_mm = container_info['length'] * 10
                container_width_mm = container_info['width'] * 10
                container_height_mm = container_info['height'] * 10
                
                # 提取并转换货物尺寸数据
                goods_length = pd.to_numeric(df[length_column], errors='coerce') * conversion_factor
                goods_width = pd.to_numeric(df[width_column], errors='coerce') * conversion_factor  
                goods_height = pd.to_numeric(df[height_column], errors='coerce') * conversion_factor
                inventory_qty = pd.to_numeric(df[inventory_column], errors='coerce')
                
                # 过滤掉无效数据
                valid_mask = ~(goods_length.isna() | goods_width.isna() | goods_height.isna() | inventory_qty.isna())
                
                # 数据质量检查
                quality_issues = []
                
                # 检查异常小的尺寸（可能单位错误）
                very_small = (goods_length < 10) | (goods_width < 10) | (goods_height < 10)  # 小于1cm
                if very_small.sum() > 0:
                    quality_issues.append(f"发现 {very_small.sum()} 个商品尺寸小于1cm，可能存在单位错误")
                
                # 检查异常大的尺寸
                very_large = (goods_length > 50000) | (goods_width > 50000) | (goods_height > 50000)  # 大于5m
                if very_large.sum() > 0:
                    quality_issues.append(f"发现 {very_large.sum()} 个商品尺寸大于5m，可能存在数据错误")
                
                # 检查负数或零值
                invalid_size = (goods_length <= 0) | (goods_width <= 0) | (goods_height <= 0)
                if invalid_size.sum() > 0:
                    quality_issues.append(f"发现 {invalid_size.sum()} 个商品尺寸为负数或零")
                
                if quality_issues:
                    st.warning("⚠️ 数据质量警告：")
                    for issue in quality_issues:
                        st.write(f"• {issue}")
                    st.info("💡 系统将自动过滤异常数据，只分析有效数据")
                
                if valid_mask.sum() == 0:
                    results = {"error": "没有有效的尺寸和库存数据"}
                else:
                    # 获取有效数据
                    valid_data_count = valid_mask.sum()
                    valid_indices = df[valid_mask].index
                    
                    st.info(f"🔄 开始分析 {valid_data_count} 行有效数据...")
                    
                    # 创建进度条
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    packing_results = []
                    total_boxes_needed = 0
                    
                    # 默认使用分批处理，自动处理全量数据
                    batch_size = 50  # 每批处理50行数据
                    
                    try:
                        for batch_start in range(0, valid_data_count, batch_size):
                            batch_end = min(batch_start + batch_size, valid_data_count)
                            batch_indices = valid_indices[batch_start:batch_end]
                            
                            # 更新进度
                            progress = batch_end / valid_data_count
                            progress_bar.progress(progress)
                            status_text.text(f"正在处理第 {batch_start + 1}-{batch_end} 行数据... ({progress:.1%})")
                            
                            for idx in batch_indices:
                                try:
                                    # 获取当前货物尺寸
                                    g_length = goods_length[idx]
                                    g_width = goods_width[idx] 
                                    g_height = goods_height[idx]
                                    qty = inventory_qty[idx]
                                    
                                    # 检查货物尺寸是否有效（大于0且不是无穷大）
                                    if g_length <= 0 or g_width <= 0 or g_height <= 0:
                                        continue
                                    
                                    # 添加尺寸合理性检查，防止异常数据
                                    if g_length < 1 or g_width < 1 or g_height < 1:  # 小于1mm的数据视为异常
                                        continue
                                    
                                    if g_length > 10000 or g_width > 10000 or g_height > 10000:  # 大于10m的数据视为异常
                                        continue
                                    
                                    # 完整模式：6种摆放方式计算
                                    packing_options = []
                                    
                                    try:
                                        # 方式1: 长→长，宽→宽，高→高
                                        if g_length <= container_length_mm and g_width <= container_width_mm and g_height <= container_height_mm:
                                            option1 = int(container_length_mm // g_length) * int(container_width_mm // g_width) * int(container_height_mm // g_height)
                                            # 限制单个摆放方式的最大装箱数，防止异常值
                                            option1 = min(option1, 10000)  # 限制最大10000个/箱
                                        else:
                                            option1 = 0
                                        packing_options.append(option1)
                                        
                                        # 方式2: 长→长，宽→高，高→宽
                                        if g_length <= container_length_mm and g_width <= container_height_mm and g_height <= container_width_mm:
                                            option2 = int(container_length_mm // g_length) * int(container_height_mm // g_width) * int(container_width_mm // g_height)
                                            option2 = min(option2, 10000)
                                        else:
                                            option2 = 0
                                        packing_options.append(option2)
                                        
                                        # 方式3: 长→宽，宽→长，高→高
                                        if g_length <= container_width_mm and g_width <= container_length_mm and g_height <= container_height_mm:
                                            option3 = int(container_width_mm // g_length) * int(container_length_mm // g_width) * int(container_height_mm // g_height)
                                            option3 = min(option3, 10000)
                                        else:
                                            option3 = 0
                                        packing_options.append(option3)
                                        
                                        # 方式4: 长→宽，宽→高，高→长
                                        if g_length <= container_width_mm and g_width <= container_height_mm and g_height <= container_length_mm:
                                            option4 = int(container_width_mm // g_length) * int(container_height_mm // g_width) * int(container_length_mm // g_height)
                                            option4 = min(option4, 10000)
                                        else:
                                            option4 = 0
                                        packing_options.append(option4)
                                        
                                        # 方式5: 长→高，宽→长，高→宽
                                        if g_length <= container_height_mm and g_width <= container_length_mm and g_height <= container_width_mm:
                                            option5 = int(container_height_mm // g_length) * int(container_length_mm // g_width) * int(container_width_mm // g_height)
                                            option5 = min(option5, 10000)
                                        else:
                                            option5 = 0
                                        packing_options.append(option5)
                                        
                                        # 方式6: 长→高，宽→宽，高→长
                                        if g_length <= container_height_mm and g_width <= container_width_mm and g_height <= container_length_mm:
                                            option6 = int(container_height_mm // g_length) * int(container_width_mm // g_width) * int(container_length_mm // g_height)
                                            option6 = min(option6, 10000)
                                        else:
                                            option6 = 0
                                        packing_options.append(option6)
                                        
                                    except (OverflowError, ValueError):
                                        # 如果计算过程中出现错误，所有方式都设为0
                                        packing_options = [0, 0, 0, 0, 0, 0]
                                    
                                    # 取最大值
                                    max_per_box = max(packing_options) if packing_options else 0
                                    
                                    # 计算需要的箱子数
                                    if max_per_box > 0 and qty > 0:
                                        boxes_needed = np.ceil(qty / max_per_box)
                                    else:
                                        boxes_needed = float('inf')  # 装不下的情况
                                    
                                    # 只有当箱子数不是无穷大时才加到总数中
                                    if boxes_needed != float('inf'):
                                        total_boxes_needed += boxes_needed
                                    
                                    # 保存结果
                                    sku_result = {
                                        'SKU_index': idx,
                                        'goods_length_mm': g_length,
                                        'goods_width_mm': g_width,
                                        'goods_height_mm': g_height,
                                        'inventory_qty': qty,
                                        'packing_options': packing_options,
                                        'max_per_box': max_per_box,
                                        'boxes_needed': boxes_needed
                                    }
                                    packing_results.append(sku_result)
                                    
                                except Exception as e:
                                    # 单个SKU计算失败时跳过，不影响整体分析
                                    continue
                        
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ 分析过程中出现错误: {str(e)}")
                        return {"error": f"分析中断: {str(e)}"}
                    
                    # 完成进度
                    progress_bar.progress(1.0)
                    status_text.text("✅ 装箱分析计算完成！")
                    
                    # 显示结果
                    st.success(f"✅ 装箱分析完成，已处理 {valid_data_count} 行数据")
                    
                    # 计算总需箱子数（排除装不下的）
                    total_boxes_finite = sum([r['boxes_needed'] for r in packing_results if r['boxes_needed'] != float('inf')])
                    
                    # 总结果
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("有效SKU数", len(packing_results))
                    with col2:
                        st.metric("总库存件数", int(inventory_qty[valid_mask].sum()))
                    with col3:
                        # 显示能装下的货物需要的总箱子数
                        st.metric("总需箱子数", f"{total_boxes_finite:.0f}")
                    with col4:
                        # 处理无穷大值的显示
                        cannot_pack_count = len([r for r in packing_results if r['boxes_needed'] == float('inf')])
                        st.metric("装不下SKU数", cannot_pack_count)
                    with col5:
                        if packing_results:
                            # 计算平均装载率，排除装不下的货物
                            valid_results = [r for r in packing_results if r['max_per_box'] > 0 and r['boxes_needed'] != float('inf')]
                            if valid_results:
                                total_capacity = sum([r['boxes_needed'] * r['max_per_box'] for r in valid_results])
                                total_inventory = sum([r['inventory_qty'] for r in valid_results])
                                avg_utilization = total_inventory / total_capacity if total_capacity > 0 else 0
                                st.metric("平均装载率", f"{avg_utilization:.1%}")
                            else:
                                st.metric("平均装载率", "N/A")
                        else:
                            st.metric("平均装载率", "N/A")
                    
                    # 为了避免卡死，大幅简化展示逻辑
                    large_dataset = len(packing_results) > 50  # 降低阈值
                    
                    if large_dataset:
                        st.warning(f"⚠️ 数据量较大({len(packing_results)} 行)，为确保系统稳定，将只显示统计摘要")
                        
                        # 只显示统计摘要，不显示详细表格
                        st.write("📊 **装箱分析摘要:**")
                        
                        # 统计数据
                        total_items = len(packing_results)
                        can_pack_items = len([r for r in packing_results if r['max_per_box'] > 0])
                        cannot_pack_items = total_items - can_pack_items
                        
                        # 简化的统计表
                        summary_data = {
                            "分析项目": ["总SKU数", "可装箱SKU", "装不下SKU", "总库存件数", "总需箱子数", "装箱成功率"],
                            "统计结果": [
                                f"{total_items:,} 个",
                                f"{can_pack_items:,} 个",
                                f"{cannot_pack_items:,} 个", 
                                f"{int(inventory_qty[valid_mask].sum()):,} 件",
                                f"{total_boxes_finite:.0f} 个",
                                f"{(can_pack_items/total_items*100):.1f}%" if total_items > 0 else "0%"
                            ]
                        }
                        
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)
                        
                        # 简化的问题分析
                        if cannot_pack_items > 0:
                            st.write(f"⚠️ **发现 {cannot_pack_items} 个SKU无法装入当前容器，建议：**")
                            st.write("• 考虑使用更大规格的容器")
                            st.write("• 检查货物尺寸数据是否正确")
                            st.write("• 考虑拆分大件货物")
                        
                        if can_pack_items > 0:
                            avg_boxes = total_boxes_finite / can_pack_items
                            if avg_boxes > 10:
                                st.write(f"📦 **平均每SKU需要 {avg_boxes:.1f} 个箱子，建议考虑批量装箱策略**")
                        
                        st.info("💡 详细数据可通过下方导出功能获取，避免前端展示导致系统卡顿")
                    
                    else:
                        # 小数据量时的简化展示
                        st.write("📊 **装箱分析结果:**")
                        
                        # 构建简化的结果数据框（移除复杂计算）
                        try:
                            result_data = []
                            for i, result in enumerate(packing_results[:30]):  # 最多显示30行
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
                                
                                if len(packing_results) > 30:
                                    st.info(f"💡 仅显示前30行，完整数据请使用导出功能（共{len(packing_results)}行）")
                        
                        except Exception as e:
                            st.error(f"表格展示出现问题，跳过详细展示: {str(e)}")
                            st.info("💡 请使用下方导出功能获取完整分析结果")
                    
                    # 简化的导出功能
                    st.write("---")
                    st.write("**📥 数据导出**")
                    st.info("💡 推荐使用导出功能获取完整分析结果，避免前端展示导致的性能问题")
                    
                    export_col1, export_col2, export_col3 = st.columns(3)
                    
                    with export_col1:
                        if st.button("📊 导出基础结果", help="导出SKU信息和装箱结果"):
                            # 构建基础导出数据（简化版）
                            try:
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
                                csv = export_df.to_csv(index=False).encode('utf-8-sig')
                                
                                st.download_button(
                                    label="📥 下载基础装箱结果",
                                    data=csv,
                                    file_name=f"装箱分析_基础结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    key="download_basic_safe"
                                )
                                st.success("✅ 基础结果导出准备完成！")
                            except Exception as e:
                                st.error(f"导出失败: {str(e)}")
                    
                    with export_col2:
                        if st.button("📈 导出统计摘要", help="导出装箱统计汇总"):
                            try:
                                # 统计数据
                                total_items = len(packing_results)
                                can_pack_items = len([r for r in packing_results if r['max_per_box'] > 0])
                                cannot_pack_items = total_items - can_pack_items
                                
                                # 创建统计报表
                                summary_report = {
                                    "装箱分析摘要": [
                                        f"容器规格: {container_info['length']}×{container_info['width']}×{container_info['height']} cm",
                                        f"总SKU数: {total_items:,} 个",
                                        f"可装箱SKU: {can_pack_items:,} 个",
                                        f"装不下SKU: {cannot_pack_items:,} 个",
                                        f"总库存件数: {int(inventory_qty[valid_mask].sum()):,} 件",
                                        f"总需箱子数: {total_boxes_finite:.0f} 个",
                                        f"装箱成功率: {(can_pack_items/total_items*100):.1f}%",
                                        f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    ]
                                }
                                
                                summary_df = pd.DataFrame.from_dict(summary_report, orient='index').T
                                csv = summary_df.to_csv(index=False).encode('utf-8-sig')
                                
                                st.download_button(
                                    label="📥 下载统计摘要",
                                    data=csv,
                                    file_name=f"装箱分析_统计摘要_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    key="download_summary_safe"
                                )
                                st.success("✅ 统计摘要导出准备完成！")
                            except Exception as e:
                                st.error(f"导出失败: {str(e)}")
                    
                    with export_col3:
                        if show_details and st.button("📋 导出详细数据", help="导出包含6种摆放方式的完整数据"):
                            try:
                                # 详细数据构建
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
                                csv = detailed_df.to_csv(index=False).encode('utf-8-sig')
                                
                                st.download_button(
                                    label="📥 下载详细装箱数据",
                                    data=csv,
                                    file_name=f"装箱分析_详细结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    key="download_detailed_safe"
                                )
                                st.success("✅ 详细数据导出准备完成！")
                            except Exception as e:
                                st.error(f"导出失败: {str(e)}")
                    
                    # 保存结果到session state（简化版）
                    results = {
                        "container_length": container_info['length'],
                        "container_width": container_info['width'],
                        "container_height": container_info['height'],
                        "total_sku_count": len(packing_results),
                        "total_inventory": int(inventory_qty[valid_mask].sum()),
                        "total_boxes_needed": total_boxes_finite,
                        "cannot_pack_count": len([r for r in packing_results if r['boxes_needed'] == float('inf')]),
                        "analysis_type": "装箱分析（简化展示）"
                    }
                    
                    # 移除可视化图表（避免卡死）
                    st.write("---")
                    st.info("💡 为确保系统稳定运行，已简化数据展示。完整分析结果请通过导出功能获取。")
                    
                    # 简化的优化建议
                    if len(packing_results) > 0:
                        st.write("💡 **装箱优化建议**")
                        
                        problem_items = [r for r in packing_results if r['max_per_box'] == 0]
                        
                        if problem_items:
                            st.write(f"⚠️ 有 {len(problem_items)} 个SKU无法装入当前容器")
                        
                        if can_pack_items > 0 and total_boxes_finite > 0:
                            avg_boxes = total_boxes_finite / can_pack_items
                            if avg_boxes > 10:
                                st.write(f"📦 平均每SKU需要 {avg_boxes:.1f} 个箱子，建议优化装箱策略")
                            else:
                                st.write(f"✅ 装箱效率良好，平均每SKU需要 {avg_boxes:.1f} 个箱子")
                        
                        st.write("📋 详细分析和优化建议请查看导出的Excel文件")
            
            except Exception as e:
                st.error(f"❌ 装箱分析计算失败: {str(e)}")
                results = {"error": f"计算失败: {str(e)}"}
    
    else:
        # 其他分析维度的占位符
        if container_info:
            results = {
                "container_info": container_info,
                "message": f"基于容器规格的{dimension}功能开发中"
            }
        else:
            results = {
                "message": f"{dimension} 功能开发中"
            }
    
    return results

# 页面配置和主界面
st.set_page_config(page_title=LANG["title"], layout="wide")
st.title(LANG["title"])

uploaded_file = st.file_uploader(LANG["upload"], type=["xlsx"])
if uploaded_file:
    # 第一步：选择分析类型
    st.subheader("🎯 第一步：选择分析类型")
    
    # 创建三列布局显示分析类型
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"{ANALYSIS_TYPES[LANG['inventory_analysis']]['icon']} {LANG['inventory_analysis']}", 
                    use_container_width=True, type="secondary"):
            st.session_state.analysis_type = "inventory"
            st.session_state.analysis_name = LANG["inventory_analysis"]
    
    with col2:
        if st.button(f"{ANALYSIS_TYPES[LANG['inbound_analysis']]['icon']} {LANG['inbound_analysis']}", 
                    use_container_width=True, type="secondary"):
            st.session_state.analysis_type = "inbound"
            st.session_state.analysis_name = LANG["inbound_analysis"]
    
    with col3:
        if st.button(f"{ANALYSIS_TYPES[LANG['outbound_analysis']]['icon']} {LANG['outbound_analysis']}", 
                    use_container_width=True, type="secondary"):
            st.session_state.analysis_type = "outbound"
            st.session_state.analysis_name = LANG["outbound_analysis"]
    
    # 显示选择的分析类型
    if st.session_state.get('analysis_type'):
        analysis_name = st.session_state.analysis_name
        analysis_info = ANALYSIS_TYPES[analysis_name]
        
        st.success(f"✅ 已选择分析类型: **{analysis_info['icon']} {analysis_name}**")
        st.info(f"💡 {analysis_info['description']}")
        
        # 第二步：选择Sheet
        st.subheader("📋 第二步：选择数据源")
        
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        st.write(f"📋 检测到 {len(sheet_names)} 个Sheet: {', '.join(sheet_names)}")
        
        sheet = st.selectbox(LANG["select_sheet"], sheet_names)
        
        if st.button(LANG["confirm_button"], type="primary"):
            st.session_state.sheet_confirmed = True
            st.session_state.selected_sheet = sheet
            for key in list(st.session_state.keys()):
                if key.startswith('data_'):
                    del st.session_state[key]
        
        # 只有确认后才显示数据和第三步
        if st.session_state.get('sheet_confirmed', False):
            st.success(f"✅ 已选择Sheet: **{st.session_state.selected_sheet}**")
            
            df = load_and_cache_data(uploaded_file, st.session_state.selected_sheet)
            
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
            
            # 第三步：选择分析维度
            st.subheader("🔍 第三步：选择分析维度")
            
            available_dimensions = ANALYSIS_TYPE_DIMENSIONS[st.session_state.analysis_type]
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
                            st.success("📦 **已选择容器标准化**：后续分析将基于选定容器规格进行")
                            
                            with st.container():
                                st.write("**📏 选择标准容器规格：**")
                                container_size = st.selectbox(
                                    "容器尺寸 (长x宽x高 cm)",
                                    options=["600x400x300", "650x450x350"],
                                    key="selected_container_size",
                                    help="选择的容器规格将应用于所有后续分析"
                                )
                                
                                dimensions = container_size.split('x')
                                length, width, height = dimensions[0], dimensions[1], dimensions[2]
                                st.info(f"✅ **选定容器规格**：长{length}cm × 宽{width}cm × 高{height}cm")
                                
                                st.session_state.container_length = int(length)
                                st.session_state.container_width = int(width)
                                st.session_state.container_height = int(height)
                        
                        elif dimension == "异常数据清洗":
                            st.success("🔄 **已选择前置处理**：后续分析将基于清洗后的数据进行")
            
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
            
            # 显示选中的维度并提供下一步按钮
            if current_selected_dimensions:
                st.write("---")
                
                selected_preprocessing = [dim for dim in current_selected_dimensions if dim in preprocessing_dimensions]
                selected_analysis = [dim for dim in current_selected_dimensions if dim in analysis_dimensions]
                
                if selected_preprocessing:
                    st.write(f"✅ **已选择前置处理** ({len(selected_preprocessing)} 个): {', '.join(selected_preprocessing)}")
                    
                    if "容器选择" in selected_preprocessing:
                        container_size = st.session_state.get("selected_container_size", "600x400x300")
                        st.caption(f"📦 容器规格: {container_size}")
                
                if selected_analysis:
                    if selected_preprocessing:
                        st.write(f"✅ **已选择数据分析** ({len(selected_analysis)} 个): {', '.join(selected_analysis)}")
                        
                        preprocessing_info = []
                        if "异常数据清洗" in selected_preprocessing:
                            preprocessing_info.append("数据清洗")
                        if "容器选择" in selected_preprocessing:
                            preprocessing_info.append("容器标准化")
                        
                        preprocessing_str = " + ".join(preprocessing_info)
                        st.info(f"🔄 **执行顺序**：{preprocessing_str} → 数据分析（基于处理后数据/标准）")
                    else:
                        st.write(f"✅ **已选择数据分析** ({len(selected_analysis)} 个): {', '.join(selected_analysis)}")
                        st.info("📊 **执行方式**：直接基于原始数据进行分析")
                
                if st.button(LANG["next_step"], type="primary"):
                    st.session_state.dimensions_confirmed = True
                    st.session_state.selected_dimensions = current_selected_dimensions
            
            # 第四步：配置分析参数
            if st.session_state.get('dimensions_confirmed', False):
                st.subheader("⚙️ 第四步：配置分析参数")
                
                for dimension in st.session_state.selected_dimensions:
                    with st.expander(f"🔧 配置 {dimension}", expanded=True):
                        render_dimension_config(dimension, df.columns.tolist())
                
                if st.button(LANG["start_analysis"], type="primary"):
                    st.session_state.analysis_confirmed = True
            
            # 执行分析
            if st.session_state.get('analysis_confirmed', False):
                st.subheader(f"📈 {analysis_name}结果")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button(LANG["export_pdf"], type="secondary"):
                        pdf_data = generate_pdf_report()
                        if pdf_data:
                            st.download_button(
                                label="📄 下载PDF报告",
                                data=pdf_data,
                                file_name=f"数据分析报告_{st.session_state.analysis_name}_{st.session_state.selected_sheet}.pdf",
                                mime="application/pdf"
                            )
                
                # 数据流控制：确保前置处理优先执行
                current_df = df.copy()
                container_info = None
                
                preprocessing_steps = [dim for dim in st.session_state.selected_dimensions if dim in PREPROCESSING_DIMENSIONS]
                analysis_steps = [dim for dim in st.session_state.selected_dimensions if dim in ANALYSIS_DIMENSIONS]
                
                # 第一步：执行前置处理
                if preprocessing_steps:
                    st.info("🔄 **数据处理流程：先执行前置处理，其他分析将基于处理结果进行**")
                    
                    # 执行异常数据清洗
                    if "异常数据清洗" in preprocessing_steps:
                        dimension_info = PREPROCESSING_DIMENSIONS["异常数据清洗"]
                        with st.expander(f"{dimension_info['icon']} 异常数据清洗", expanded=True):
                            st.write("🧹 **正在执行数据清洗（优先执行）...**")
                            
                            all_conditions = st.session_state.get("异常数据清洗_all_conditions", [])
                            action = st.session_state.get("异常数据清洗_action", "删除")
                            
                            if all_conditions and any(all_conditions):
                                try:
                                    cleaned_df, abnormal_data = advanced_data_cleaning_enhanced(current_df, all_conditions, "异常数据清洗", action)
                                    
                                    # 详细的清洗统计信息
                                    st.write("### 📊 **数据清洗统计结果**")
                                    
                                    # 基础统计
                                    original_count = len(current_df)
                                    abnormal_count = len(abnormal_data)
                                    normal_count = original_count - abnormal_count
                                    cleaned_count = len(cleaned_df)
                                    
                                    # 创建统计展示
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.metric(
                                            label="原始数据总数", 
                                            value=f"{original_count:,} 行",
                                            help="清洗前的原始数据总行数"
                                        )
                                    
                                    with col2:
                                        st.metric(
                                            label="检测到异常数据", 
                                            value=f"{abnormal_count:,} 行",
                                            delta=f"-{(abnormal_count/original_count*100):.1f}%" if original_count > 0 else "0%",
                                            delta_color="inverse",
                                            help="符合设定条件的异常数据行数"
                                        )
                                    
                                    with col3:
                                        st.metric(
                                            label="正常数据", 
                                            value=f"{normal_count:,} 行",
                                            delta=f"{(normal_count/original_count*100):.1f}%" if original_count > 0 else "0%",
                                            delta_color="normal",
                                            help="未被标记为异常的正常数据行数"
                                        )
                                    
                                    with col4:
                                        if action == "删除":
                                            st.metric(
                                                label="清洗后数据", 
                                                value=f"{cleaned_count:,} 行",
                                                delta=f"减少 {original_count - cleaned_count:,} 行",
                                                delta_color="inverse",
                                                help="删除异常数据后的剩余数据行数"
                                            )
                                        elif action == "标记异常":
                                            st.metric(
                                                label="标记后数据", 
                                                value=f"{cleaned_count:,} 行",
                                                delta="添加异常标记列",
                                                help="添加异常标记列后的数据行数"
                                            )
                                        else:
                                            st.metric(
                                                label="导出数据", 
                                                value=f"{cleaned_count:,} 行",
                                                delta="原始数据不变",
                                                help="导出异常数据，原始数据保持不变"
                                            )
                                    
                                    # 清洗效果总结
                                    if abnormal_count > 0:
                                        st.write("**🎯 清洗效果总结：**")
                                        
                                        if action == "删除":
                                            cleaning_rate = (abnormal_count / original_count * 100) if original_count > 0 else 0
                                            retention_rate = (normal_count / original_count * 100) if original_count > 0 else 0
                                            
                                            effect_col1, effect_col2 = st.columns(2)
                                            with effect_col1:
                                                st.info(f"✂️ **数据清洗率**: {cleaning_rate:.1f}% ({abnormal_count:,} 行被删除)")
                                            with effect_col2:
                                                st.success(f"✅ **数据保留率**: {retention_rate:.1f}% ({normal_count:,} 行保留)")
                                            
                                            if cleaning_rate > 20:
                                                st.warning("⚠️ 清洗掉的数据比例较高，请确认清洗条件设置是否合理")
                                            elif cleaning_rate < 1:
                                                st.info("💡 清洗比例较低，如需清洗更多数据请调整条件设置")
                                        
                                        elif action == "标记异常":
                                            marking_rate = (abnormal_count / original_count * 100) if original_count > 0 else 0
                                            st.info(f"🏷️ **异常标记率**: {marking_rate:.1f}% ({abnormal_count:,} 行被标记为异常)")
                                            st.success("✅ 所有数据都被保留，异常数据已添加标记列")
                                        
                                        else:  # 导出到新文件
                                            export_rate = (abnormal_count / original_count * 100) if original_count > 0 else 0
                                            st.info(f"📤 **异常数据导出率**: {export_rate:.1f}% ({abnormal_count:,} 行将被导出)")
                                            st.success("✅ 原始数据保持不变，异常数据单独导出")
                                    
                                    else:
                                        st.success("🎉 **清洗结果**: 未发现符合条件的异常数据，所有数据都是正常的！")
                                    
                                    # 后续处理说明
                                    if action != "导出到新文件":
                                        current_df = cleaned_df
                                        st.write("---")
                                        if action == "删除":
                                            st.info(f"📊 **后续分析将基于清洗后的数据进行**（{len(current_df):,} 行数据）")
                                        else:
                                            st.info(f"📊 **后续分析将基于标记后的数据进行**（{len(current_df):,} 行数据，包含异常标记列）")
                                    else:
                                        st.write("---")
                                        st.info("📊 **后续分析仍使用原始数据**（异常数据已单独导出）")
                                        
                                    st.success("✅ 异常数据清洗完成")
                                    
                                    if len(abnormal_data) > 0:
                                        st.write("---")
                                        st.write("⚠️ **检测到的异常数据详情:**")
                                        
                                        # 异常数据预览（如果数据量大则只显示前10行）
                                        if len(abnormal_data) > 10:
                                            st.write(f"📋 显示前10行异常数据（共 {len(abnormal_data)} 行）:")
                                            preview_abnormal = abnormal_data.head(10)
                                            st.dataframe(preview_abnormal, use_container_width=True)
                                            st.caption(f"💡 仅显示前10行，完整异常数据可通过下方下载按钮获取")
                                        else:
                                            st.dataframe(abnormal_data, use_container_width=True)
                                        
                                        # 导出异常数据
                                        csv = abnormal_data.to_csv(index=False).encode('utf-8-sig')
                                        st.download_button(
                                            label=f"📥 下载异常数据 ({len(abnormal_data)} 行)",
                                            data=csv,
                                            file_name=f"异常数据_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv",
                                            help="下载完整的异常数据列表"
                                        )
                                    else:
                                        st.write("---")
                                        st.info("✅ 未发现符合条件的异常数据")
                                        
                                except Exception as e:
                                    st.error(f"❌ 数据清洗处理失败: {str(e)}")
                                    current_df = df.copy()
                            else:
                                st.info("💡 未设置清洗条件，跳过数据清洗")
                    
                    # 执行容器选择
                    if "容器选择" in preprocessing_steps:
                        dimension_info = PREPROCESSING_DIMENSIONS["容器选择"]
                        with st.expander(f"{dimension_info['icon']} 容器选择", expanded=True):
                            st.write("📦 **正在执行容器标准化（优先执行）...**")
                            
                            length = st.session_state.get("container_length", 600)
                            width = st.session_state.get("container_width", 400)
                            height = st.session_state.get("container_height", 300)
                            container_size = st.session_state.get("selected_container_size", "600x400x300")
                            
                            container_info = {
                                "length": length,
                                "width": width, 
                                "height": height,
                                "size": container_size,
                                "volume": length * width * height
                            }
                            
                            st.success("✅ 容器标准化完成")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("长度", f"{length} cm")
                            with col2:
                                st.metric("宽度", f"{width} cm")
                            with col3:
                                st.metric("高度", f"{height} cm")
                            with col4:
                                st.metric("容积", f"{container_info['volume']:,} cm³")
                            
                            st.info(f"📊 **后续分析将基于容器规格进行**（{container_size}）")
                
                # 第二步：执行其他分析维度
                if analysis_steps:
                    if preprocessing_steps:
                        st.write("---")
                        st.write("🔍 **基于前置处理结果的分析：**")
                    
                    for dimension in analysis_steps:
                        dimension_info = ANALYSIS_DIMENSIONS[dimension]
                        with st.expander(f"{dimension_info['icon']} {dimension}", expanded=True):
                            info_parts = []
                            if "异常数据清洗" in preprocessing_steps:
                                info_parts.append(f"清洗后数据（{len(current_df)} 行）")
                            if "容器选择" in preprocessing_steps and container_info:
                                info_parts.append(f"标准容器（{container_info['size']}）")
                            
                            if info_parts:
                                st.caption(f"📊 基于 {' + '.join(info_parts)} 进行分析")
                            
                            analysis_results = execute_analysis_dimension_with_container(current_df, dimension, container_info)
                            
                            if 'error' in analysis_results:
                                st.error(f"❌ 分析失败: {analysis_results['error']}")
                            else:
                                st.success(f"✅ {dimension} 分析完成")
                                
                                if analysis_results:
                                    st.write("📊 **分析结果详情:**")
                                    for key, value in analysis_results.items():
                                        if isinstance(value, dict):
                                            st.write(f"**{key}:**")
                                            for sub_key, sub_value in value.items():
                                                st.write(f"  • {sub_key}: {sub_value}")
                                        else:
                                            st.write(f"• {key}: {value}")
                
                # 如果没有选择前置处理，直接执行分析
                elif not preprocessing_steps:
                    st.info("📊 **使用原始数据进行分析**")
                    
                    for dimension in analysis_steps:
                        dimension_info = ANALYSIS_DIMENSIONS[dimension]
                        with st.expander(f"{dimension_info['icon']} {dimension}", expanded=True):
                            analysis_results = execute_analysis_dimension_with_container(current_df, dimension, None)
                            
                            if 'error' in analysis_results:
                                st.error(f"❌ 分析失败: {analysis_results['error']}")
                            else:
                                st.success(f"✅ {dimension} 分析完成")
                                
                                if analysis_results:
                                    st.write("📊 **分析结果详情:**")
                                    for key, value in analysis_results.items():
                                        if isinstance(value, dict):
                                            st.write(f"**{key}:**")
                                            for sub_key, sub_value in value.items():
                                                st.write(f"  • {sub_key}: {sub_value}")
                                        else:
                                            st.write(f"• {key}: {value}")
            
            # 重新选择按钮
            if st.button("🔄 重新选择"):
                keys_to_clear = ['sheet_confirmed', 'analysis_type', 'dimensions_confirmed', 
                               'analysis_confirmed', 'selected_dimensions', 'analysis_name', 'data_loaded']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                for key in list(st.session_state.keys()):
                    if key.startswith('data_'):
                        del st.session_state[key]
                
                st.rerun() 