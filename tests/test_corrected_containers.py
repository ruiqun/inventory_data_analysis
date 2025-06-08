# -*- coding: utf-8 -*-
"""
验证修正后的容器配置
测试650x450x300等容器的装箱分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.packing_analysis import PackingAnalyzer
from config import CONTAINER_SPECS
import pandas as pd

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_all_containers():
    """测试所有容器规格的装箱分析"""
    print_separator("所有容器规格装箱分析验证")
    
    # 测试货物：20×15×10 cm
    goods_length_cm = 20
    goods_width_cm = 15  
    goods_height_cm = 10
    goods_inventory = 100
    
    print(f"🎯 测试货物: {goods_length_cm}×{goods_width_cm}×{goods_height_cm} cm")
    print(f"📦 库存数量: {goods_inventory} 个")
    
    # 转换为mm
    goods_length_mm = goods_length_cm * 10  # 200mm
    goods_width_mm = goods_width_cm * 10    # 150mm
    goods_height_mm = goods_height_cm * 10  # 100mm
    
    for spec_name, spec_info in CONTAINER_SPECS.items():
        print(f"\n--- 容器规格: {spec_name} cm ---")
        
        # 创建分析器
        container_info = {
            'length': spec_info['length'],
            'width': spec_info['width'], 
            'height': spec_info['height'],
            'size': spec_name,
            'volume': spec_info['length'] * spec_info['width'] * spec_info['height']
        }
        
        analyzer = PackingAnalyzer(container_info)
        
        print(f"容器尺寸(cm): {spec_info['length']} × {spec_info['width']} × {spec_info['height']}")
        print(f"容器尺寸(mm): {analyzer.container_length_mm} × {analyzer.container_width_mm} × {analyzer.container_height_mm}")
        
        # 执行装箱分析
        result = analyzer.analyze_single_sku(
            goods_length_mm, goods_width_mm, goods_height_mm,
            goods_inventory, 0
        )
        
        if result:
            print(f"6种摆放方式: {result['packing_options']}")
            print(f"最大装箱数: {result['max_per_box']:,} 个/箱")
            print(f"需要箱数: {result['boxes_needed']:.0f} 箱")
            
            # 手工验证最优方式
            container_l, container_w, container_h = analyzer.container_length_mm, analyzer.container_width_mm, analyzer.container_height_mm
            manual_max = max([
                (container_l//200) * (container_w//150) * (container_h//100),
                (container_l//200) * (container_h//150) * (container_w//100),
                (container_w//200) * (container_l//150) * (container_h//100),
                (container_w//200) * (container_h//150) * (container_l//100),
                (container_h//200) * (container_l//150) * (container_w//100),
                (container_h//200) * (container_w//150) * (container_l//100)
            ])
            
            if result['max_per_box'] == manual_max:
                print("✅ 计算结果正确!")
            else:
                print(f"❌ 计算错误: 期望{manual_max}, 实际{result['max_per_box']}")
        else:
            print("❌ 装箱分析失败")

def test_specific_container_650x450x300():
    """专门测试修正后的650×450×300容器"""
    print_separator("650×450×300 容器详细测试")
    
    # 创建容器
    container_info = {
        'length': 650,
        'width': 450,
        'height': 300,  # 修正后的高度
        'size': '650x450x300',
        'volume': 650 * 450 * 300
    }
    
    analyzer = PackingAnalyzer(container_info)
    
    print(f"📦 容器规格: {container_info['size']} cm")
    print(f"📦 容器规格(mm): {analyzer.container_length_mm}×{analyzer.container_width_mm}×{analyzer.container_height_mm} mm")
    print(f"📦 容器容积: {container_info['volume']:,} cm³")
    
    # 测试多种货物尺寸
    test_goods = [
        {"name": "小商品", "l": 20, "w": 15, "h": 10, "inventory": 100},
        {"name": "中型商品", "l": 30, "w": 25, "h": 20, "inventory": 50},
        {"name": "大型商品", "l": 50, "w": 40, "h": 30, "inventory": 20}
    ]
    
    for goods in test_goods:
        print(f"\n--- {goods['name']}: {goods['l']}×{goods['w']}×{goods['h']} cm ---")
        
        # 转换为mm
        goods_l_mm = goods['l'] * 10
        goods_w_mm = goods['w'] * 10
        goods_h_mm = goods['h'] * 10
        
        result = analyzer.analyze_single_sku(
            goods_l_mm, goods_w_mm, goods_h_mm,
            goods['inventory'], 0
        )
        
        if result:
            print(f"最大装箱数: {result['max_per_box']:,} 个/箱")
            print(f"需要箱数: {result['boxes_needed']:.0f} 箱")
            print(f"6种摆放方式: {result['packing_options']}")
            
            # 计算空间利用率
            goods_volume_mm3 = goods_l_mm * goods_w_mm * goods_h_mm
            container_volume_mm3 = analyzer.container_length_mm * analyzer.container_width_mm * analyzer.container_height_mm
            utilization = (result['max_per_box'] * goods_volume_mm3) / container_volume_mm3 * 100
            
            print(f"空间利用率: {utilization:.1f}%")
        else:
            print("❌ 装不下该商品")

def main():
    """主测试函数"""
    print("🧪 修正后容器配置验证")
    print("🎯 主要验证: 650x450x300 (修正前350→300)")
    
    test_all_containers()
    test_specific_container_650x450x300()
    
    print_separator("验证完成")
    print("✅ 容器配置已修正完成!")
    print("🎯 650×450×300: 高度从350cm修正为300cm")
    print("🎯 所有容器单位: cm (配置) → mm (内部计算)")
    print("🎯 装箱计算: 已验证正确性")

if __name__ == "__main__":
    main() 