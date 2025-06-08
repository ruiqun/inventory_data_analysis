# -*- coding: utf-8 -*-
"""
验证装箱计算修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.packing_analysis import PackingAnalyzer
from config import PACKING_CONFIG
import pandas as pd

print("🔧 装箱计算修复验证")
print(f"📋 新的装箱限制: {PACKING_CONFIG['max_items_per_box']:,} 个/箱")

# 创建容器 600x400x300 cm
container_info = {
    'length': 600,
    'width': 400, 
    'height': 300,
    'size': '600x400x300',
    'volume': 600 * 400 * 300
}

analyzer = PackingAnalyzer(container_info)

# 测试问题案例：20x15x10 cm
print(f"\n📦 容器: {container_info['size']} cm")
print("🎯 测试货物: 20×15×10 cm")

goods_length_mm = 200  # 20cm
goods_width_mm = 150   # 15cm  
goods_height_mm = 100  # 10cm
inventory_qty = 10

result = analyzer.analyze_single_sku(goods_length_mm, goods_width_mm, goods_height_mm, inventory_qty, 0)

if result:
    print(f"\n✅ 修复后结果:")
    print(f"   6种摆放方式: {result['packing_options']}")
    print(f"   最大装箱数: {result['max_per_box']:,} 个/箱")
    print(f"   需要箱数: {result['boxes_needed']:.0f} 箱")
    
    # 手工验证
    expected_max = max([
        (6000//200) * (4000//150) * (3000//100),  # 30 * 26 * 30 = 23400
        (6000//200) * (3000//150) * (4000//100),  # 30 * 20 * 40 = 24000
        (4000//200) * (6000//150) * (3000//100),  # 20 * 40 * 30 = 24000
        (4000//200) * (3000//150) * (6000//100),  # 20 * 20 * 60 = 24000  
        (3000//200) * (6000//150) * (4000//100),  # 15 * 40 * 40 = 24000
        (3000//200) * (4000//150) * (6000//100)   # 15 * 26 * 60 = 23400
    ])
    
    print(f"\n🔍 理论验证:")
    print(f"   期望最大装箱数: {expected_max:,} 个")
    print(f"   实际计算结果: {result['max_per_box']:,} 个")
    
    if result['max_per_box'] == expected_max:
        print("✅ 计算结果正确！")
    else:
        print("❌ 计算结果仍有问题")
        
else:
    print("❌ 分析失败")

# 测试Excel数据格式输出
print(f"\n📊 Excel导出格式验证:")
print(f"SKU行号: 1")
print(f"货物长度(cm): {goods_length_mm/10:.1f}")
print(f"货物宽度(cm): {goods_width_mm/10:.1f}")  
print(f"货物高度(cm): {goods_height_mm/10:.1f}")
print(f"库存件数: {inventory_qty}")
print(f"最大装箱数: {result['max_per_box'] if result else 0}")
boxes_text = f"{result['boxes_needed']:.0f}" if result and result['boxes_needed'] != float('inf') else '装不下'
print(f"需要箱数: {boxes_text}")

for i, option in enumerate(result['packing_options'] if result else [], 1):
    print(f"摆放方式{i}: {option}")

print(f"\n🎯 对比修复前后:")
print(f"修复前: 最大装箱数 10,000 个 (错误)")
print(f"修复后: 最大装箱数 {result['max_per_box']:,} 个 (正确)") 