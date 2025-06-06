import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_test_data():
    """生成包含异常数据的测试数据"""
    np.random.seed(42)
    
    # 生成基础数据
    n_records = 1000
    
    data = {
        '商品编码': [f'SKU{str(i).zfill(5)}' for i in range(1, n_records + 1)],
        '商品名称': [f'商品{i}' for i in range(1, n_records + 1)],
        '库存数量': np.random.randint(0, 1000, n_records),
        '单价': np.round(np.random.uniform(10, 500, n_records), 2),
        '供应商编码': [f'SUP{random.randint(1, 50):03d}' for _ in range(n_records)],
        '入库日期': [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(n_records)],
        '出库数量': np.random.randint(0, 100, n_records),
        '重量': np.round(np.random.uniform(0.1, 50, n_records), 2),
        '类别': [random.choice(['A', 'B', 'C']) for _ in range(n_records)],
        # 添加装箱分析需要的尺寸数据
        '长度cm': np.round(np.random.uniform(5, 80, n_records), 1),
        '宽度cm': np.round(np.random.uniform(5, 60, n_records), 1),
        '高度cm': np.round(np.random.uniform(3, 40, n_records), 1),
    }
    
    # 添加一些异常数据
    # 负库存
    data['库存数量'][10:15] = [-10, -5, -20, -1, -50]
    
    # 异常单价
    data['单价'][20:25] = [0, -10, 9999, -50, 0]
    
    # 异常重量
    data['重量'][30:35] = [0, -5, 999, -1, 0]
    
    # 异常尺寸数据
    data['长度cm'][80:85] = [0, -5, 200, -1, 0]  # 异常长度
    data['宽度cm'][85:90] = [0, -3, 150, -2, 0]  # 异常宽度
    data['高度cm'][90:95] = [0, -1, 100, -5, 0]  # 异常高度
    
    # 特殊的装箱测试案例
    # 超大货物（装不下标准容器）
    data['长度cm'][95:100] = [120, 150, 180, 200, 250]
    data['宽度cm'][95:100] = [100, 120, 140, 150, 180]
    data['高度cm'][95:100] = [80, 90, 100, 120, 150]
    
    # 空值
    data['商品名称'][40:45] = [None, None, '', None, '']
    data['供应商编码'][50:55] = [None, '', None, '', None]
    
    # 重复数据
    data['商品编码'][60:65] = ['SKU00001', 'SKU00001', 'SKU00002', 'SKU00002', 'SKU00003']
    
    # 异常出库数量（大于库存）
    for i in range(70, 80):
        data['出库数量'][i] = data['库存数量'][i] + random.randint(1, 100)
    
    df = pd.DataFrame(data)
    
    # 格式化日期
    df['入库日期'] = df['入库日期'].dt.strftime('%Y-%m-%d')
    
    return df

def generate_packing_test_data():
    """生成专门的装箱分析测试数据"""
    np.random.seed(123)
    
    n_records = 200
    
    # 常见的货物尺寸范围（cm）
    small_items = 50  # 小件商品
    medium_items = 100  # 中等商品
    large_items = 30   # 大件商品
    oversized_items = 20  # 超大商品
    
    data = {
        '商品编码': [f'PACK{str(i).zfill(4)}' for i in range(1, n_records + 1)],
        '商品名称': [],
        '库存数量': [],
        '长度cm': [],
        '宽度cm': [],
        '高度cm': [],
        '重量kg': [],
        '类别': [],
        '优先级': []
    }
    
    # 生成不同类型的商品
    for i in range(n_records):
        if i < small_items:
            # 小件商品（容易装箱）
            data['商品名称'].append(f'小件商品{i+1}')
            data['长度cm'].append(round(np.random.uniform(5, 25), 1))
            data['宽度cm'].append(round(np.random.uniform(5, 20), 1))
            data['高度cm'].append(round(np.random.uniform(3, 15), 1))
            data['库存数量'].append(np.random.randint(50, 500))
            data['重量kg'].append(round(np.random.uniform(0.1, 2), 2))
            data['类别'].append('小件')
            data['优先级'].append('高')
            
        elif i < small_items + medium_items:
            # 中等商品（需要合理装箱）
            data['商品名称'].append(f'中等商品{i+1}')
            data['长度cm'].append(round(np.random.uniform(20, 50), 1))
            data['宽度cm'].append(round(np.random.uniform(15, 40), 1))
            data['高度cm'].append(round(np.random.uniform(10, 30), 1))
            data['库存数量'].append(np.random.randint(10, 100))
            data['重量kg'].append(round(np.random.uniform(1, 10), 2))
            data['类别'].append('中件')
            data['优先级'].append(random.choice(['高', '中']))
            
        elif i < small_items + medium_items + large_items:
            # 大件商品（装箱挑战）
            data['商品名称'].append(f'大件商品{i+1}')
            data['长度cm'].append(round(np.random.uniform(40, 90), 1))
            data['宽度cm'].append(round(np.random.uniform(30, 70), 1))
            data['高度cm'].append(round(np.random.uniform(20, 50), 1))
            data['库存数量'].append(np.random.randint(1, 20))
            data['重量kg'].append(round(np.random.uniform(5, 30), 2))
            data['类别'].append('大件')
            data['优先级'].append(random.choice(['中', '低']))
            
        else:
            # 超大商品（可能装不下）
            data['商品名称'].append(f'超大商品{i+1}')
            data['长度cm'].append(round(np.random.uniform(80, 150), 1))
            data['宽度cm'].append(round(np.random.uniform(60, 120), 1))
            data['高度cm'].append(round(np.random.uniform(40, 80), 1))
            data['库存数量'].append(np.random.randint(1, 5))
            data['重量kg'].append(round(np.random.uniform(20, 100), 2))
            data['类别'].append('超大')
            data['优先级'].append('低')
    
    # 添加一些异常数据用于测试异常处理
    # 尺寸为0或负数
    data['长度cm'][190:193] = [0, -5, 0]
    data['宽度cm'][190:193] = [-2, 0, -1]
    data['高度cm'][190:193] = [0, -3, 0]
    
    # 库存为0或负数
    data['库存数量'][193:196] = [0, -10, 0]
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    return df

def save_test_data():
    """保存测试数据到Excel文件"""
    df = generate_test_data()
    packing_df = generate_packing_test_data()
    
    # 创建多个Sheet的测试数据
    with pd.ExcelWriter('测试数据.xlsx', engine='openpyxl') as writer:
        # 库存数据
        df.to_excel(writer, sheet_name='库存数据', index=False)
        
        # 入库数据（部分列）
        inbound_df = df[['商品编码', '商品名称', '入库日期', '库存数量', '供应商编码', '重量', '长度cm', '宽度cm', '高度cm']].copy()
        inbound_df.to_excel(writer, sheet_name='入库数据', index=False)
        
        # 出库数据（部分列）
        outbound_df = df[['商品编码', '商品名称', '出库数量', '单价', '类别']].copy()
        outbound_df.to_excel(writer, sheet_name='出库数据', index=False)
        
        # 装箱分析测试数据
        packing_df.to_excel(writer, sheet_name='装箱分析数据', index=False)
    
    print("✅ 测试数据已生成：测试数据.xlsx")
    print(f"📊 数据统计：")
    print(f"  • 总记录数：{len(df)}")
    print(f"  • 负库存记录：{len(df[df['库存数量'] < 0])}")
    print(f"  • 异常单价记录：{len(df[df['单价'] <= 0])}")
    print(f"  • 空值记录：{df.isnull().sum().sum()}")
    print(f"  • 商品编码重复：{df['商品编码'].duplicated().sum()}")
    print(f"")
    print(f"📦 装箱分析数据统计：")
    print(f"  • 装箱测试记录数：{len(packing_df)}")
    print(f"  • 小件商品：{len(packing_df[packing_df['类别'] == '小件'])}")
    print(f"  • 中件商品：{len(packing_df[packing_df['类别'] == '中件'])}")
    print(f"  • 大件商品：{len(packing_df[packing_df['类别'] == '大件'])}")
    print(f"  • 超大商品：{len(packing_df[packing_df['类别'] == '超大'])}")
    print(f"  • 异常尺寸记录：{len(packing_df[(packing_df['长度cm'] <= 0) | (packing_df['宽度cm'] <= 0) | (packing_df['高度cm'] <= 0)])}")
    print(f"")
    print(f"💡 使用说明：")
    print(f"  • 库存数据/入库数据：含有货物尺寸信息，可用于装箱分析")
    print(f"  • 装箱分析数据：专门设计的装箱测试数据，包含多种尺寸类型")
    print(f"  • 建议使用'装箱分析数据'Sheet进行装箱分析功能测试")

if __name__ == "__main__":
    save_test_data() 