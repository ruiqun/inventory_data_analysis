# 项目目录结构说明

## 📁 整理后的目录结构

```
创维数据分析/
├── 📄 app_main.py              # 主应用入口（推荐使用）
├── 📄 config.py                # 全局配置文件
├── 📄 requirements.txt         # 依赖包列表
├── 📄 README.md               # 项目说明
├── 📄 .cursorrules            # Cursor规则配置
│
├── 📁 备份/                   # 🗄️ 备份文件
│   ├── 📄 app.py              # 原始主应用（完整版备份）
│   ├── 📄 app_legacy.py       # 旧版应用（重构版备份）
│   ├── 📄 ARCHITECTURE.md     # 旧版架构文档
│   └── 📄 README_备份说明.md  # 备份文件说明
│
├── 📁 core/                   # 🔥 核心业务逻辑
│   ├── 📄 __init__.py
│   ├── 📄 analysis_engine.py   # 分析引擎核心
│   ├── 📄 packing_analysis.py  # 装箱分析模块
│   └── 📄 data_cleaning.py     # 数据清洗模块
│
├── 📁 components/             # 🎨 UI组件
│   ├── 📄 __init__.py
│   └── 📄 ui_components.py     # Streamlit界面组件
│
├── 📁 modules/                # 📦 功能模块
│   ├── 📄 __init__.py
│   └── 📄 report_generator.py  # 报告生成模块
│
├── 📁 utils/                  # 🔧 工具函数
│   ├── 📄 __init__.py
│   └── 📄 utils.py            # 通用工具函数
│
├── 📁 tests/                  # 🧪 测试相关
│   ├── 📄 __init__.py
│   └── 📄 test_data.py        # 测试数据生成
│
├── 📁 docs/                   # 📚 文档
│   ├── 📄 ARCHITECTURE.md     # 架构说明
│   └── 📄 PROJECT_STRUCTURE.md # 项目结构说明
│
├── 📁 assets/                 # 🖼️ 静态资源
│
├── 📁 __pycache__/           # Python缓存文件
└── 📄 测试数据.xlsx           # 测试数据文件
```

## 📋 文件功能说明

### 🏠 根目录文件
- **app_main.py**: 主应用入口，推荐使用的版本
- **config.py**: 全局配置，包含所有常量和配置信息

### 🗄️ 备份/ - 备份文件
- **app.py**: 原始主应用文件（完整版备份）
- **app_legacy.py**: 旧版应用文件（重构版备份）
- **ARCHITECTURE.md**: 旧版架构文档
- **README_备份说明.md**: 备份文件使用说明

### 🔥 core/ - 核心业务逻辑
- **analysis_engine.py**: 分析引擎，协调各种分析维度的执行
- **packing_analysis.py**: 装箱分析的核心算法实现
- **data_cleaning.py**: 数据清洗和预处理逻辑

### 🎨 components/ - UI组件
- **ui_components.py**: 所有Streamlit界面组件和展示逻辑

### 📦 modules/ - 功能模块
- **report_generator.py**: PDF报告生成功能

### 🔧 utils/ - 工具函数
- **utils.py**: 通用工具函数，包含数据处理、文件操作、验证等

### 🧪 tests/ - 测试
- **test_data.py**: 测试数据生成器

## 🚀 使用建议

### 启动应用
```bash
streamlit run app_main.py
```

### 开发新功能
1. **核心算法**: 在 `core/` 目录下添加新的分析模块
2. **UI界面**: 在 `components/ui_components.py` 中添加新的界面组件
3. **工具函数**: 在 `utils/utils.py` 中添加通用工具函数
4. **配置项**: 在 `config.py` 中添加新的配置常量

### Import规范
```python
# 从根目录导入
from config import ANALYSIS_DIMENSIONS
from utils import DataUtils
from components.ui_components import UIComponents
from core.analysis_engine import AnalysisEngine
from modules.report_generator import AnalysisReport
```

## 🔄 迁移说明

### 已处理的文件
- ✅ **移动到core/**: analysis_engine.py, packing_analysis.py, data_cleaning.py
- ✅ **移动到components/**: ui_components.py  
- ✅ **移动到modules/**: report_generator.py
- ✅ **移动到utils/**: utils.py
- ✅ **移动到tests/**: test_data.py
- ✅ **移动到备份/**: app.py, app_legacy.py, ARCHITECTURE.md (旧版本)
- ✅ **删除重复文件**: analysis.py, plot.py (功能简单且已有替代)
- ✅ **重命名应用文件**: app_new.py → app_legacy.py, app_structured.py → app_main.py

### 更新的Import路径
所有文件的import语句已更新以反映新的目录结构，确保模块间的正确引用。

## 💡 优势

1. **模块化**: 清晰的功能分离，便于维护和扩展
2. **标准化**: 符合Python项目的标准目录结构
3. **可维护性**: 相关功能集中管理，减少代码重复
4. **可扩展性**: 新功能可以按类型添加到对应目录
5. **团队协作**: 清晰的结构便于多人协作开发

---

**文档版本**: v2.0  
**更新日期**: 2024年12月  
**维护团队**: 创维数据分析团队 