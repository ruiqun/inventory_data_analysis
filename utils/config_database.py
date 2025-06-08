# -*- coding: utf-8 -*-
"""
配置数据库模块 - 存储和管理用户的分析配置
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import streamlit as st

class ConfigDatabase:
    """配置数据库管理器"""
    
    def __init__(self, db_path: str = "data/analysis_configs.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_name TEXT NOT NULL,
                    file_name TEXT,
                    sheet_name TEXT,
                    analysis_type TEXT NOT NULL,
                    analysis_name TEXT NOT NULL,
                    selected_dimensions TEXT NOT NULL,
                    dimension_configs TEXT NOT NULL,
                    container_config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
    
    def save_config(self, 
                    config_name: str,
                    file_name: Optional[str] = None,
                    sheet_name: Optional[str] = None,
                    analysis_type: Optional[str] = None,
                    analysis_name: Optional[str] = None,
                    selected_dimensions: Optional[List[str]] = None,
                    dimension_configs: Optional[Dict[str, Any]] = None,
                    container_config: Optional[Dict[str, Any]] = None) -> int:
        """
        保存配置到数据库
        
        Args:
            config_name: 配置名称
            file_name: 文件名
            sheet_name: 工作表名
            analysis_type: 分析类型
            analysis_name: 分析名称
            selected_dimensions: 选择的维度
            dimension_configs: 维度配置
            container_config: 容器配置
            
        Returns:
            int: 配置ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在相同名称的配置
            cursor.execute('SELECT id FROM analysis_configs WHERE config_name = ?', (config_name,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有配置
                cursor.execute('''
                    UPDATE analysis_configs 
                    SET file_name = ?, sheet_name = ?, analysis_type = ?, analysis_name = ?,
                        selected_dimensions = ?, dimension_configs = ?, container_config = ?,
                        last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                    WHERE config_name = ?
                ''', (
                    file_name, sheet_name, analysis_type, analysis_name,
                    json.dumps(selected_dimensions) if selected_dimensions else None, 
                    json.dumps(dimension_configs) if dimension_configs else None,
                    json.dumps(container_config) if container_config else None, 
                    config_name
                ))
                config_id = existing[0]
            else:
                # 插入新配置
                cursor.execute('''
                    INSERT INTO analysis_configs 
                    (config_name, file_name, sheet_name, analysis_type, analysis_name,
                     selected_dimensions, dimension_configs, container_config)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config_name, file_name, sheet_name, analysis_type, analysis_name,
                    json.dumps(selected_dimensions) if selected_dimensions else None,
                    json.dumps(dimension_configs) if dimension_configs else None,
                    json.dumps(container_config) if container_config else None
                ))
                config_id = cursor.lastrowid
            
            conn.commit()
            return int(config_id) if config_id else 0
    
    def load_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """
        从数据库加载配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            Dict: 配置信息，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_configs WHERE id = ?
            ''', (config_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 更新最后使用时间和使用次数
            cursor.execute('''
                UPDATE analysis_configs 
                SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                WHERE id = ?
            ''', (config_id,))
            conn.commit()
            
            return self._row_to_dict(row)
    
    def get_recent_configs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近使用的配置列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 配置列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_configs 
                ORDER BY last_used DESC 
                LIMIT ?
            ''', (limit,))
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def search_configs(self, keyword: Optional[str] = None, analysis_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索配置
        
        Args:
            keyword: 关键词（搜索配置名称和文件名）
            analysis_type: 分析类型过滤
            
        Returns:
            List[Dict]: 配置列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM analysis_configs WHERE 1=1'
            params = []
            
            if keyword:
                query += ' AND (config_name LIKE ? OR file_name LIKE ?)'
                params.extend([f'%{keyword}%', f'%{keyword}%'])
            
            if analysis_type:
                query += ' AND analysis_type = ?'
                params.append(analysis_type)
            
            query += ' ORDER BY last_used DESC'
            
            cursor.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def delete_config(self, config_id: int) -> bool:
        """
        删除配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            bool: 是否成功删除
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM analysis_configs WHERE id = ?', (config_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        if not row:
            return {}
        
        return {
            'id': row[0],
            'config_name': row[1],
            'file_name': row[2],
            'sheet_name': row[3],
            'analysis_type': row[4],
            'analysis_name': row[5],
            'selected_dimensions': json.loads(row[6]) if row[6] else [],
            'dimension_configs': json.loads(row[7]) if row[7] else {},
            'container_config': json.loads(row[8]) if row[8] else {},
            'created_at': row[9],
            'last_used': row[10],
            'use_count': row[11]
        }
    
    def get_config_stats(self) -> Dict[str, Any]:
        """获取配置统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总配置数
            cursor.execute('SELECT COUNT(*) FROM analysis_configs')
            total_configs = cursor.fetchone()[0]
            
            # 按分析类型统计
            cursor.execute('''
                SELECT analysis_type, COUNT(*) 
                FROM analysis_configs 
                GROUP BY analysis_type
            ''')
            type_stats = dict(cursor.fetchall())
            
            # 最常用的配置
            cursor.execute('''
                SELECT config_name, use_count 
                FROM analysis_configs 
                ORDER BY use_count DESC 
                LIMIT 1
            ''')
            most_used = cursor.fetchone()
            
            return {
                'total_configs': total_configs,
                'type_stats': type_stats,
                'most_used': most_used
            }

# 全局数据库实例
config_db = ConfigDatabase() 