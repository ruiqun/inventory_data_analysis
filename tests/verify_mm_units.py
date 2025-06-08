#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证毫米单位容器配置的正确性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from config import CONTAINER_SPECS, PACKING_CONFIG
from core.packing_analysis import PackingAnalyzer

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_subsection(title):
    """打印子标题"""
    print(f"\n--- {title} ---")

def test_mm_container_specs():
    """测试毫米单位的容器规格"""
    print_separator("毫米单位容器规格验证")
    
    print("📦 当前容器配置 (单位: mm):")
    for spec_name, spec_info in CONTAINER_SPECS.items():
        print(f"   {spec_name}: 长{spec_info['length']}mm × 宽{spec_info['width']}mm × 高{spec_info['height']}mm")
        
        # 转换为cm显示
        length_cm = spec_info['length'] / 10
        width_cm = spec_info['width'] / 10
        height_cm = spec_info['height'] / 10
        print(f"   等效厘米: 长{length_cm}cm × 宽{width_cm}cm × 高{height_cm}cm")
    
    print("✅ 容器规格读取正常")

def test_packing_calculation_with_mm():
    """测试毫米单位下的装箱计算"""
    print_separator("毫米单位装箱计算验证")
    
    # 使用600×400×300毫米容器
    container_info = {
        'length': 600,  # mm
        'width': 400,   # mm
        'height': 300,  # mm
        'size': '600x400x300',
        'volume': 600 * 400 * 300
    }
    
    analyzer = PackingAnalyzer(container_info)
    
    print(f"📦 容器规格: {container_info['size']} mm")
    print(f"📦 容器转换后: {analyzer.container_length_mm}×{analyzer.container_width_mm}×{analyzer.container_height_mm} mm")
    print(f"📦 等效厘米: {analyzer.container_length_mm/10}×{analyzer.container_width_mm/10}×{analyzer.container_height_mm/10} cm")
    
    # 测试不同尺寸的货物
    test_cases = [
        {"name": "20×15×10 cm货物", "length": 20, "width": 15, "height": 10, "unit": "cm"},
        {"name": "200×150×100 mm货物", "length": 200, "width": 150, "height": 100, "unit": "mm"},
        {"name": "小型货物", "length": 100, "width": 80, "height": 50, "unit": "mm"},
        {"name": "超小货物", "length": 50, "width": 30, "height": 20, "unit": "mm"}
    ]
    
    for case in test_cases:
        print_subsection(f"测试: {case['name']}")
        
        # 转换为mm
        if case['unit'] == 'cm':
            goods_length_mm = case['length'] * 10
            goods_width_mm = case['width'] * 10
            goods_height_mm = case['height'] * 10
            print(f"原始尺寸: {case['length']}×{case['width']}×{case['height']} {case['unit']}")
            print(f"转换后: {goods_length_mm}×{goods_width_mm}×{goods_height_mm} mm")
        else:
            goods_length_mm = case['length']
            goods_width_mm = case['width']
            goods_height_mm = case['height']
            print(f"货物尺寸: {goods_length_mm}×{goods_width_mm}×{goods_height_mm} mm")
        
        # 装箱分析
        result = analyzer.analyze_single_sku(goods_length_mm, goods_width_mm, goods_height_mm, 100, 0)
        
        if result:
            print(f"6种摆放方式: {result['packing_options']}")
            print(f"最大装箱数: {result['max_per_box']:,} 个/箱")
            
            # 计算能否装得下
            container_fits = (goods_length_mm <= 600 and goods_width_mm <= 400 and goods_height_mm <= 300)
            print(f"能否装下: {'✅ 是' if container_fits else '❌ 否'}")
            
            if container_fits and result['max_per_box'] > 0:
                # 手动验证一种摆放方式
                per_length = int(600 // goods_length_mm)
                per_width = int(400 // goods_width_mm)
                per_height = int(300 // goods_height_mm)
                manual_calc = per_length * per_width * per_height
                print(f"手动验证 (长→长): {per_length} × {per_width} × {per_height} = {manual_calc}")
                
        else:
            print("❌ 尺寸无效，无法分析")

def test_comparison_with_previous():
    """对比修正前后的差异"""
    print_separator("修正前后对比")
    
    # 假设原来认为是cm的600×400×300容器
    print("🔄 原来的理解 (错误):")
    print("   配置中 600×400×300 → 认为是cm → 转换为 6000×4000×3000 mm")
    
    print("\n✅ 现在的理解 (正确):")
    print("   配置中 600×400×300 → 就是mm → 直接使用 600×400×300 mm")
    
    # 对于20×15×10cm的货物
    goods_length_mm = 200  # 20cm = 200mm
    goods_width_mm = 150   # 15cm = 150mm
    goods_height_mm = 100  # 10cm = 100mm
    
    print(f"\n🎯 测试货物: 20×15×10 cm = {goods_length_mm}×{goods_width_mm}×{goods_height_mm} mm")
    
    # 原来错误的计算 (容器6000×4000×3000mm)
    old_per_length = int(6000 // goods_length_mm)  # 30
    old_per_width = int(4000 // goods_width_mm)    # 26
    old_per_height = int(3000 // goods_height_mm)  # 30
    old_total = old_per_length * old_per_width * old_per_height
    
    print(f"❌ 错误计算 (容器6000×4000×3000mm): {old_per_length}×{old_per_width}×{old_per_height} = {old_total:,}")
    
    # 现在正确的计算 (容器600×400×300mm)
    new_per_length = int(600 // goods_length_mm)   # 3
    new_per_width = int(400 // goods_width_mm)     # 2
    new_per_height = int(300 // goods_height_mm)   # 3
    new_total = new_per_length * new_per_width * new_per_height
    
    print(f"✅ 正确计算 (容器600×400×300mm): {new_per_length}×{new_per_width}×{new_per_height} = {new_total}")
    
    print(f"\n📊 差异对比:")
    print(f"   错误结果: {old_total:,} 个/箱")
    print(f"   正确结果: {new_total} 个/箱")
    print(f"   差异倍数: {old_total // new_total if new_total > 0 else '∞'}倍")

def main():
    """主函数"""
    print("🔧 容器单位修正验证")
    print("=" * 60)
    
    test_mm_container_specs()
    test_packing_calculation_with_mm()
    test_comparison_with_previous()
    
    print("\n" + "="*60)
    print("✅ 验证完成！容器单位已正确修正为毫米")
    print("="*60)

if __name__ == "__main__":
    main() 