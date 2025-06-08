# -*- coding: utf-8 -*-
"""
装箱分析详细测试用例
专门测试装箱分析功能，并详细展示计算过程
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.packing_analysis import PackingAnalyzer
from config import PACKING_CONFIG

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_subsection(title):
    """打印子标题"""
    print(f"\n--- {title} ---")

def test_single_sku_detailed():
    """测试单个SKU的详细装箱计算过程"""
    print_separator("单个SKU装箱分析详细测试")
    
    # 容器信息 (cm)
    container_info = {
        'length': 600,  # 60cm
        'width': 400,   # 40cm  
        'height': 300,  # 30cm
        'size': '600x400x300',
        'volume': 600 * 400 * 300
    }
    
    print(f"📦 容器规格: {container_info['length']}×{container_info['width']}×{container_info['height']} cm")
    print(f"📦 容器体积: {container_info['volume']:,} cm³")
    
    # 创建分析器
    analyzer = PackingAnalyzer(container_info)
    print(f"📦 容器尺寸(mm): {analyzer.container_length_mm}×{analyzer.container_width_mm}×{analyzer.container_height_mm}")
    
    # 测试用例数据 (cm)
    test_cases = [
        {"name": "小商品", "length": 15, "width": 10, "height": 7.5, "inventory": 100},
        {"name": "中型商品", "length": 30, "width": 20, "height": 15, "inventory": 50},
        {"name": "大型商品", "length": 50, "width": 30, "height": 25, "inventory": 20},
        {"name": "细长商品", "length": 80, "width": 5, "height": 5, "inventory": 30},
        {"name": "扁平商品", "length": 40, "width": 35, "height": 2, "inventory": 200},
        {"name": "超大商品", "length": 70, "width": 50, "height": 40, "inventory": 5}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print_subsection(f"测试用例 {i}: {case['name']}")
        
        # 转换为mm
        goods_length_mm = case['length'] * 10
        goods_width_mm = case['width'] * 10  
        goods_height_mm = case['height'] * 10
        inventory_qty = case['inventory']
        
        print(f"🎯 货物尺寸: {case['length']}×{case['width']}×{case['height']} cm")
        print(f"🎯 货物尺寸(mm): {goods_length_mm}×{goods_width_mm}×{goods_height_mm}")
        print(f"🎯 库存数量: {inventory_qty} 件")
        
        # 手动计算6种摆放方式
        print("\n🔢 6种摆放方式计算:")
        container_l, container_w, container_h = analyzer.container_length_mm, analyzer.container_width_mm, analyzer.container_height_mm
        
        packing_options = []
        method_names = [
            "长→长，宽→宽，高→高",
            "长→长，宽→高，高→宽", 
            "长→宽，宽→长，高→高",
            "长→宽，宽→高，高→长",
            "长→高，宽→长，高→宽",
            "长→高，宽→宽，高→长"
        ]
        
        calculations = [
            (container_l, goods_length_mm, container_w, goods_width_mm, container_h, goods_height_mm),
            (container_l, goods_length_mm, container_h, goods_width_mm, container_w, goods_height_mm),
            (container_w, goods_length_mm, container_l, goods_width_mm, container_h, goods_height_mm),
            (container_w, goods_length_mm, container_h, goods_width_mm, container_l, goods_height_mm),
            (container_h, goods_length_mm, container_l, goods_width_mm, container_w, goods_height_mm),
            (container_h, goods_length_mm, container_w, goods_width_mm, container_l, goods_height_mm)
        ]
        
        for j, (c1, g1, c2, g2, c3, g3) in enumerate(calculations):
            # 检查是否能装下
            if g1 <= c1 and g2 <= c2 and g3 <= c3:
                qty1 = int(c1 // g1)
                qty2 = int(c2 // g2)  
                qty3 = int(c3 // g3)
                total = qty1 * qty2 * qty3
                total = min(total, PACKING_CONFIG["max_items_per_box"])
                
                print(f"  方式{j+1} ({method_names[j]}):")
                print(f"    ({c1}//{g1}) × ({c2}//{g2}) × ({c3}//{g3}) = {qty1}×{qty2}×{qty3} = {total} 个")
            else:
                total = 0
                print(f"  方式{j+1} ({method_names[j]}): 装不下 (0 个)")
            
            packing_options.append(total)
        
        # 计算最大装箱数
        max_per_box = max(packing_options) if packing_options else 0
        print(f"\n✅ 最大装箱数: {max_per_box} 个/箱")
        
        # 计算需要的箱子数
        if max_per_box > 0 and inventory_qty > 0:
            boxes_needed = np.ceil(inventory_qty / max_per_box)
            utilization = inventory_qty / (boxes_needed * max_per_box)
            print(f"✅ 需要箱子数: {boxes_needed:.0f} 箱")
            print(f"✅ 容积利用率: {utilization:.2%}")
        else:
            boxes_needed = float('inf')
            print(f"❌ 无法装箱")
        
        # 使用分析器验证
        print("\n🔍 分析器验证:")
        result = analyzer.analyze_single_sku(goods_length_mm, goods_width_mm, goods_height_mm, inventory_qty, i-1)
        
        if result:
            print(f"✅ 分析器结果: 最大装箱数 {result['max_per_box']} 个/箱, 需要 {result['boxes_needed']:.0f} 箱")
            print(f"✅ 6种方式结果: {result['packing_options']}")
            
            # 验证结果一致性
            if result['max_per_box'] == max_per_box:
                print("✅ 手工计算与分析器结果一致！")
            else:
                print(f"❌ 结果不一致！手工: {max_per_box}, 分析器: {result['max_per_box']}")
        else:
            print("❌ 分析器返回None（可能尺寸验证失败）")

def test_batch_analysis_detailed():
    """测试批量装箱分析"""
    print_separator("批量装箱分析测试")
    
    # 创建测试数据集
    test_data = {
        '商品名称': ['商品A', '商品B', '商品C', '商品D', '商品E'],
        '长度(cm)': [15, 30, 50, 8, 40],
        '宽度(cm)': [10, 20, 30, 5, 35], 
        '高度(cm)': [7.5, 15, 25, 5, 2],
        '库存数量': [100, 50, 20, 300, 200]
    }
    
    df = pd.DataFrame(test_data)
    print("📊 测试数据集:")
    print(df.to_string(index=False))
    
    # 容器信息
    container_info = {
        'length': 600,
        'width': 400, 
        'height': 300,
        'size': '600x400x300',
        'volume': 600 * 400 * 300
    }
    
    # 创建分析器
    analyzer = PackingAnalyzer(container_info)
    
    print(f"\n📦 使用容器: {container_info['size']} cm")
    
    # 执行批量分析
    packing_results, processed_count = analyzer.analyze_batch(
        df, '长度(cm)', '宽度(cm)', '高度(cm)', '库存数量', 'cm'
    )
    
    print(f"\n📋 分析结果摘要:")
    print(f"处理数据行数: {processed_count}")
    print(f"成功分析SKU数: {len(packing_results)}")
    
    # 详细结果
    print("\n📋 详细分析结果:")
    total_inventory = 0
    total_boxes = 0
    successful_items = 0
    
    for result in packing_results:
        name = df.iloc[result['SKU_index']]['商品名称']
        inventory = result['inventory_qty']
        max_per_box = result['max_per_box']
        boxes_needed = result['boxes_needed']
        
        total_inventory += inventory
        
        print(f"\n🎯 {name} (行 {result['SKU_index']+1}):")
        print(f"   尺寸: {result['goods_length_mm']/10:.1f}×{result['goods_width_mm']/10:.1f}×{result['goods_height_mm']/10:.1f} cm")
        print(f"   库存: {inventory} 件")
        print(f"   最大装箱数: {max_per_box} 个/箱")
        
        if boxes_needed != float('inf'):
            total_boxes += boxes_needed
            successful_items += 1
            utilization = inventory / (boxes_needed * max_per_box)
            print(f"   需要箱数: {boxes_needed:.0f} 箱")
            print(f"   容积利用率: {utilization:.2%}")
            print(f"   6种摆放方式: {result['packing_options']}")
        else:
            print(f"   状态: ❌ 无法装箱")
    
    # 生成统计摘要
    summary_stats = analyzer.generate_summary_statistics(packing_results, total_inventory)
    
    print(f"\n📊 整体统计:")
    print(f"总SKU数: {summary_stats['total_sku_count']}")
    print(f"可装箱SKU: {summary_stats['can_pack_items']}")
    print(f"无法装箱SKU: {summary_stats['cannot_pack_items']}")
    print(f"总库存: {summary_stats['total_inventory']} 件")
    print(f"总需箱数: {summary_stats['total_boxes_needed']:.0f} 箱")
    print(f"装箱成功率: {summary_stats['success_rate']:.1f}%")
    print(f"平均容积利用率: {summary_stats['avg_utilization']:.2%}")
    print(f"平均每SKU箱数: {summary_stats['avg_boxes_per_sku']:.1f} 箱")

def test_edge_cases():
    """测试边界情况"""
    print_separator("边界情况测试")
    
    container_info = {'length': 600, 'width': 400, 'height': 300, 'size': '600x400x300', 'volume': 72000000}
    analyzer = PackingAnalyzer(container_info)
    
    edge_cases = [
        {"name": "完全匹配", "length": 600, "width": 400, "height": 300, "inventory": 1},
        {"name": "刚好装不下", "length": 601, "width": 400, "height": 300, "inventory": 1}, 
        {"name": "超小商品", "length": 0.1, "width": 0.1, "height": 0.1, "inventory": 1000000},
        {"name": "零库存", "length": 10, "width": 10, "height": 10, "inventory": 0},
        {"name": "负尺寸", "length": -10, "width": 10, "height": 10, "inventory": 10}
    ]
    
    for case in edge_cases:
        print_subsection(f"边界测试: {case['name']}")
        
        goods_length_mm = case['length'] * 10
        goods_width_mm = case['width'] * 10
        goods_height_mm = case['height'] * 10
        
        print(f"商品尺寸: {case['length']}×{case['width']}×{case['height']} cm")
        print(f"库存数量: {case['inventory']} 件")
        
        # 尺寸验证
        is_valid = analyzer.validate_goods_size(goods_length_mm, goods_width_mm, goods_height_mm)
        print(f"尺寸验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        if is_valid:
            result = analyzer.analyze_single_sku(goods_length_mm, goods_width_mm, goods_height_mm, case['inventory'], 0)
            if result:
                boxes_text = f"{result['boxes_needed']:.0f}" if result['boxes_needed'] != float('inf') else '∞'
                print(f"分析结果: 最大装箱数 {result['max_per_box']}, 需要箱数 {boxes_text}")
            else:
                print("分析结果: None")
        else:
            print("跳过分析（尺寸验证失败）")

if __name__ == "__main__":
    print("🧪 装箱分析详细测试开始")
    print(f"📋 配置信息: 最大装箱限制 {PACKING_CONFIG['max_items_per_box']} 个/箱")
    
    try:
        # 运行所有测试
        test_single_sku_detailed()
        test_batch_analysis_detailed() 
        test_edge_cases()
        
        print_separator("测试完成")
        print("✅ 所有测试执行完毕！")
        
    except Exception as e:
        print_separator("测试错误")
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc() 