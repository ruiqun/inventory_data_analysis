# -*- coding: utf-8 -*-
"""
配置管理组件 - 提供配置保存、加载、删除的界面
"""

import streamlit as st
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
from utils.config_database import config_db

def render_config_manager():
    """渲染配置管理界面"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 配置管理")
    
    # 获取最近的配置
    recent_configs = config_db.get_recent_configs(limit=5)
    
    if recent_configs:
        st.sidebar.markdown("**🔄 最近使用的配置**")
        
        for config in recent_configs:
            with st.sidebar.container():
                # 配置信息展示
                col1, col2 = st.sidebar.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{config['config_name']}**")
                    st.caption(f"{config['analysis_name']} | 使用{config['use_count']}次")
                
                with col2:
                    if st.button("🔄", key=f"load_{config['id']}", help="加载此配置"):
                        load_configuration(config['id'])
                        st.rerun()
    
    else:
        st.sidebar.info("📝 还没有保存的配置")
    
    # 配置搜索和管理
    with st.sidebar.expander("🔍 配置搜索与管理"):
        render_config_search()
    
    # 配置导入导出
    with st.sidebar.expander("📤 配置导入导出"):
        render_import_export_section()

def render_import_export_section():
    """渲染配置导入导出界面"""
    # 导出配置
    st.markdown("**📤 导出配置**")
    
    # 选择要导出的配置
    all_configs = config_db.get_recent_configs(limit=50)  # 获取所有配置
    
    if all_configs:
        config_options = {
            f"{config['config_name']} ({config['analysis_name']})": config['id'] 
            for config in all_configs
        }
        
        selected_config_name = st.selectbox(
            "选择要导出的配置",
            options=list(config_options.keys()),
            help="选择一个配置导出为JSON文件"
        )
        
        if st.button("📤 导出选中配置", use_container_width=True):
            config_id = config_options[selected_config_name]
            export_config(config_id)
        
        if st.button("📤 导出所有配置", use_container_width=True):
            export_all_configs()
    else:
        st.info("没有可导出的配置")
    
    st.markdown("---")
    
    # 导入配置
    st.markdown("**📥 导入配置**")
    
    uploaded_config = st.file_uploader(
        "选择配置文件",
        type=['json'],
        help="上传之前导出的配置JSON文件"
    )
    
    if uploaded_config:
        if st.button("📥 导入配置", use_container_width=True):
            import_config(uploaded_config)

def export_config(config_id: int):
    """导出单个配置"""
    try:
        config = config_db.load_config(config_id)
        if config:
            # 准备导出数据
            export_data = {
                'export_type': 'single_config',
                'export_time': datetime.now().isoformat(),
                'config': config
            }
            
            # 生成文件名
            safe_name = config['config_name'].replace(' ', '_').replace('/', '_')
            filename = f"配置_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 提供下载
            st.download_button(
                label=f"💾 下载 {config['config_name']}",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )
            
            st.success("✅ 配置已准备好下载！")
        else:
            st.error("❌ 配置不存在")
    except Exception as e:
        st.error(f"❌ 导出失败: {str(e)}")

def export_all_configs():
    """导出所有配置"""
    try:
        all_configs = config_db.get_recent_configs(limit=1000)  # 获取所有配置
        
        if all_configs:
            # 准备导出数据
            export_data = {
                'export_type': 'all_configs',
                'export_time': datetime.now().isoformat(),
                'total_count': len(all_configs),
                'configs': all_configs
            }
            
            # 生成文件名
            filename = f"所有配置_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 提供下载
            st.download_button(
                label=f"💾 下载所有配置 ({len(all_configs)}个)",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )
            
            st.success(f"✅ {len(all_configs)} 个配置已准备好下载！")
        else:
            st.warning("⚠️ 没有可导出的配置")
    except Exception as e:
        st.error(f"❌ 导出失败: {str(e)}")

def import_config(uploaded_file):
    """导入配置"""
    try:
        # 读取文件内容
        content = uploaded_file.read().decode('utf-8')
        data = json.loads(content)
        
        # 验证文件格式
        if 'export_type' not in data:
            st.error("❌ 无效的配置文件格式")
            return
        
        export_type = data['export_type']
        imported_count = 0
        
        if export_type == 'single_config':
            # 导入单个配置
            config = data.get('config', {})
            if import_single_config(config):
                imported_count = 1
        
        elif export_type == 'all_configs':
            # 导入多个配置
            configs = data.get('configs', [])
            for config in configs:
                if import_single_config(config):
                    imported_count += 1
        
        else:
            st.error("❌ 不支持的导出类型")
            return
        
        if imported_count > 0:
            st.success(f"✅ 成功导入 {imported_count} 个配置！")
            st.rerun()  # 刷新界面
        else:
            st.warning("⚠️ 没有成功导入任何配置")
            
    except json.JSONDecodeError:
        st.error("❌ 配置文件格式错误")
    except Exception as e:
        st.error(f"❌ 导入失败: {str(e)}")

def import_single_config(config: Dict[str, Any]) -> bool:
    """导入单个配置"""
    try:
        # 检查必需字段
        required_fields = ['config_name', 'analysis_type', 'analysis_name']
        for field in required_fields:
            if field not in config:
                st.warning(f"⚠️ 配置 {config.get('config_name', '未知')} 缺少必需字段: {field}")
                return False
        
        # 生成新的配置名（避免重复）
        original_name = config['config_name']
        new_name = f"{original_name}_导入_{datetime.now().strftime('%m%d_%H%M')}"
        
        # 保存配置
        config_id = config_db.save_config(
            config_name=new_name,
            file_name=config.get('file_name'),
            sheet_name=config.get('sheet_name'),
            analysis_type=config['analysis_type'],
            analysis_name=config['analysis_name'],
            selected_dimensions=config.get('selected_dimensions', []),
            dimension_configs=config.get('dimension_configs', {}),
            container_config=config.get('container_config', {})
        )
        
        return config_id > 0
        
    except Exception as e:
        st.warning(f"⚠️ 导入配置失败: {str(e)}")
        return False

def render_config_search():
    """渲染配置搜索界面"""
    # 搜索条件
    search_keyword = st.text_input("🔍 搜索配置", placeholder="输入配置名称或文件名")
    
    analysis_types = ["", "装箱分析", "异常数据清洗"]
    selected_type = st.selectbox("🎯 分析类型", options=analysis_types)
    
    # 搜索按钮
    if st.button("🔍 搜索配置") or search_keyword:
        search_type = selected_type if selected_type else None
        configs = config_db.search_configs(
            keyword=search_keyword if search_keyword else None,
            analysis_type=search_type
        )
        
        if configs:
            st.markdown(f"**找到 {len(configs)} 个配置：**")
            
            for config in configs:
                with st.container():
                    # 配置详细信息
                    st.markdown(f"**{config['config_name']}**")
                    st.caption(f"""
                    📄 文件: {config['file_name'] or '未知'}  
                    📋 工作表: {config['sheet_name'] or '未知'}  
                    🎯 分析: {config['analysis_name']}  
                    📅 最后使用: {config['last_used']}  
                    📊 使用次数: {config['use_count']}
                    """)
                    
                    # 操作按钮
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔄 加载", key=f"search_load_{config['id']}"):
                            load_configuration(config['id'])
                            st.rerun()
                    
                    with col2:
                        if st.button("📋 详情", key=f"detail_{config['id']}"):
                            show_config_detail(config)
                    
                    with col3:
                        if st.button("🗑️ 删除", key=f"delete_{config['id']}"):
                            if config_db.delete_config(config['id']):
                                st.success("配置已删除！")
                                st.rerun()
                            else:
                                st.error("删除失败！")
                    
                    st.markdown("---")
        else:
            st.info("未找到匹配的配置")

def show_config_detail(config: Dict[str, Any]):
    """显示配置详情"""
    st.markdown(f"### 📋 配置详情: {config['config_name']}")
    
    # 基本信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 基本信息**")
        st.write(f"📝 配置名称: {config['config_name']}")
        st.write(f"📄 文件名: {config['file_name'] or '未指定'}")
        st.write(f"📋 工作表: {config['sheet_name'] or '未指定'}")
        st.write(f"🎯 分析类型: {config['analysis_type']}")
        st.write(f"📊 分析名称: {config['analysis_name']}")
    
    with col2:
        st.markdown("**📊 使用统计**")
        st.write(f"📅 创建时间: {config['created_at']}")
        st.write(f"🕒 最后使用: {config['last_used']}")
        st.write(f"📊 使用次数: {config['use_count']}")
    
    # 维度信息
    if config['selected_dimensions']:
        st.markdown("**📐 选择的维度**")
        st.write(", ".join(config['selected_dimensions']))
    
    # 详细配置
    if config['dimension_configs']:
        st.markdown("**⚙️ 维度配置**")
        st.json(config['dimension_configs'])
    
    if config['container_config']:
        st.markdown("**📦 容器配置**")
        st.json(config['container_config'])

def save_current_config():
    """保存当前配置"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 保存当前配置")
    
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
                'container_height': st.session_state.get('container_height')
            }
        
        # 保存到数据库
        config_id = config_db.save_config(
            config_name=config_name,
            file_name=st.session_state.get('uploaded_file_name'),
            sheet_name=st.session_state.get('selected_sheet'),
            analysis_type=st.session_state.get('analysis_type'),
            analysis_name=st.session_state.get('analysis_name'),
            selected_dimensions=st.session_state.get('selected_dimensions'),
            dimension_configs=st.session_state.get('dimension_configs'),
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
        
        # 设置当前步骤 - 跳转到维度选择步骤，用户需要重新上传数据
        st.session_state['current_step'] = 'step_3_dimensions'
        # 清除文件相关状态，需要重新上传
        for key in ['uploaded_file', 'sheet_confirmed', 'dimensions_confirmed', 'analysis_confirmed']:
            if key in st.session_state:
                del st.session_state[key]
        
        # 显示成功信息
        st.success(f"✅ 已加载配置: {config['config_name']}")
        st.info(f"📄 原文件: {config['file_name'] or '未知'} | 📋 工作表: {config['sheet_name'] or '未知'}")
        st.warning("⚠️ 请重新上传数据文件以应用此配置")
        
        return True
        
    except Exception as e:
        st.error(f"加载配置失败: {str(e)}")
        return False

def restore_dimension_configs_to_session(dimension_configs: Dict[str, Any]):
    """将维度配置恢复到session_state中"""
    analysis_type = st.session_state.get('analysis_type')
    
    if analysis_type == '装箱分析':
        restore_packing_configs(dimension_configs)
    elif analysis_type == '异常数据清洗':
        restore_cleaning_configs(dimension_configs)

def restore_packing_configs(dimension_configs: Dict[str, Any]):
    """恢复装箱分析配置"""
    prefix = '装箱分析_'
    
    # 映射配置键
    key_mapping = {
        'length_column': f'{prefix}length_column',
        'width_column': f'{prefix}width_column',
        'height_column': f'{prefix}height_column',
        'quantity_column': f'{prefix}quantity_column',
        'data_unit': f'{prefix}data_unit',
        'use_weight': f'{prefix}use_weight',
        'weight_column': f'{prefix}weight_column'
    }
    
    for config_key, session_key in key_mapping.items():
        if config_key in dimension_configs:
            st.session_state[session_key] = dimension_configs[config_key]

def restore_cleaning_configs(dimension_configs: Dict[str, Any]):
    """恢复异常数据清洗配置"""
    # 恢复条件组数量
    if 'group_count' in dimension_configs:
        st.session_state['group_count'] = dimension_configs['group_count']
    
    # 恢复每组的条件
    if 'groups' in dimension_configs:
        groups = dimension_configs['groups']
        
        for group_idx, group_config in enumerate(groups):
            if group_idx < len(groups):
                group_key = f'group_{group_idx + 1}'
                
                # 恢复条件数量
                if 'condition_count' in group_config:
                    st.session_state[f'{group_key}_condition_count'] = group_config['condition_count']
                
                # 恢复条件详情
                if 'conditions' in group_config:
                    conditions = group_config['conditions']
                    
                    for cond_idx, condition in enumerate(conditions):
                        if cond_idx < len(conditions):
                            cond_prefix = f'{group_key}_condition_{cond_idx + 1}_'
                            
                            # 恢复基本条件信息
                            for key in ['column', 'operator', 'data_type']:
                                if key in condition:
                                    st.session_state[f'{cond_prefix}{key}'] = condition[key]
                            
                            # 恢复条件值（根据操作符类型）
                            operator = condition.get('operator', '')
                            if operator in ['范围内', '范围外']:
                                if 'min_value' in condition:
                                    st.session_state[f'{cond_prefix}min'] = condition['min_value']
                                if 'max_value' in condition:
                                    st.session_state[f'{cond_prefix}max'] = condition['max_value']
                            elif operator in ['包含', '不包含', '开头是', '结尾是']:
                                if 'text_value' in condition:
                                    st.session_state[f'{cond_prefix}text'] = condition['text_value']
                            else:
                                if 'value' in condition:
                                    st.session_state[f'{cond_prefix}value'] = condition['value']

def render_config_stats():
    """显示配置统计信息"""
    stats = config_db.get_config_stats()
    
    if stats['total_configs'] > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 配置统计**")
        st.sidebar.metric("配置总数", stats['total_configs'])
        
        if stats['type_stats']:
            st.sidebar.markdown("**按类型统计:**")
            for analysis_type, count in stats['type_stats'].items():
                st.sidebar.write(f"• {analysis_type}: {count}")
        
        if stats['most_used']:
            st.sidebar.markdown(f"**最常用配置:** {stats['most_used'][0]} ({stats['most_used'][1]}次)")

def render_sidebar_config_panel():
    """渲染侧边栏配置面板"""
    # 配置管理
    render_config_manager()
    
    # 保存当前配置
    save_current_config()
    
    # 配置统计
    render_config_stats() 