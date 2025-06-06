# -*- coding: utf-8 -*-
"""
配置文件 - 包含所有常量和配置信息
"""

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

# 容器规格配置
CONTAINER_SPECS = {
    "600x400x300": {"length": 600, "width": 400, "height": 300},
    "650x450x350": {"length": 650, "width": 450, "height": 350},
    "700x500x400": {"length": 700, "width": 500, "height": 400},
    "800x600x450": {"length": 800, "width": 600, "height": 450}
}

# 装箱分析配置
PACKING_CONFIG = {
    "max_items_per_box": 10000,  # 单个摆放方式最大装箱数限制
    "large_dataset_threshold": 50,  # 大数据集阈值
    "preview_rows": 30,  # 预览行数
    "batch_size": 50,  # 分批处理大小
    "unit_conversion": {"mm": 1, "cm": 10, "m": 1000},  # 单位转换系数
    "size_limits": {
        "min_size_mm": 1,  # 最小尺寸(mm)
        "max_size_mm": 10000  # 最大尺寸(mm)
    }
}

# 数据清洗配置
CLEANING_CONFIG = {
    "preview_rows": 10,  # 异常数据预览行数
    "large_dataset_threshold": 100  # 大数据集阈值
} 