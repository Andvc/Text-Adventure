# 文字冒险游戏引擎

这是一个基于Python的文字冒险游戏引擎，提供角色管理、AI驱动的故事生成和故事线管理等核心功能。

## 项目结构

```
Text Adventure/
├── ai/                # AI模块 - 提示词处理与API交互
├── character/         # 角色模块 - 角色属性管理
├── data/              # 数据模块 - 游戏静态数据管理
│   └── text/          # 文本类数据文件
│       └── worlds/    # 预设世界观数据
├── gameflow/          # 游戏流程模块 - 控制游戏进程
│   └── starting/      # 游戏开局流程
├── storyline/         # 故事线模块 - 故事模板与剧情生成
│   └── templates/     # 故事模板存储目录
├── save/              # 游戏存档目录
├── test/              # 测试文件目录
├── main.py            # 游戏主入口
├── config.py          # 配置文件
├── .env               # 环境变量配置
└── README.md          # 本文档
```

## 主要模块

### AI模块

AI模块提供了构建AI提示词、调用大模型API并解析JSON格式响应的功能。详细文档请参考[AI模块说明](ai/README.md)。

主要功能：
- 提示词构建与处理（`prompt_processor.py`）
- API连接与调用（`api_connector.py`）
- 结果解析与结构化（`output_parsers.py`）

### 角色模块

角色模块负责管理游戏中角色的属性数据，支持创建、读取、修改和删除角色属性。详细文档请参考[角色模块说明](character/README.md)。

主要功能：
- 基本属性操作
- 属性类别管理
- 物品属性管理
- 存档系统配置

### 数据模块

数据模块提供游戏固定数据的读取和管理功能，用于存储和访问游戏的静态数据。详细文档请参考[数据模块说明](data/README.md)。

主要功能：
- 数据文件管理
- 类型分离
- 缓存机制
- 集中式访问

### 游戏流程模块

游戏流程模块负责调度和管理整个游戏流程，包括开局设定、主循环和结局处理。

主要功能：
- 主菜单系统（`core.py`）
- 游戏开局流程
- 世界观设定（`starting/world_setting.py`）
- 角色创建（计划中）
- 游戏存档加载

### 故事线模块

故事线模块管理游戏的主线剧情，提供了创建、编辑和管理故事模板的工具，以及生成基于模板的游戏故事内容的功能。详细文档请参考[故事线模块说明](storyline/README.md)和[故事线模块使用指南](storyline/user_guide.md)。

主要功能：
- 模板管理
- 故事生成
- 分支选择
- 故事状态跟踪

## 游戏流程

游戏通过`main.py`启动，首先显示主菜单，允许玩家开始新游戏或加载已有游戏。游戏流程主要包括：

1. **游戏开局**
   - 世界观设定：选择预设世界观或创建自定义世界观
   - 角色创建：设置角色属性和背景（计划中）

2. **游戏主循环**
   - 故事生成：基于当前状态生成故事内容
   - 选择处理：处理玩家的选择并更新状态
   - 事件触发：基于特定条件触发特殊事件

3. **游戏结束**
   - 结局生成：基于游戏历程生成结局
   - 存档管理：保存游戏状态或开始新游戏

### 启动游戏

通过以下命令启动游戏：

```bash
python main.py
```

## 工具集

### 模板编辑工具

故事线模块提供模板编辑工具：

```bash
python -m storyline  # 直接启动编辑器
# 或者
python -m storyline.tools template_editor
```

**主要特性**:
- 简洁的界面设计，功能集中
- 直接使用角色属性，无需定义输入变量
- 集成的输出格式和存储映射配置
- 提示片段管理（背景信息、内容指令、输出格式）
- 角色属性浏览和引用
- 提示词处理和测试
- JSON预览与验证

## 安装与配置

1. 克隆仓库
   ```bash
   git clone <仓库地址>
   cd Text\ Adventure
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置API密钥
   ```bash
   # 创建.env文件
   echo "DEEPSEEK_API_KEY=your_api_key" > .env
   ```

## 快速开始

### 使用主程序启动游戏

```bash
python3 main.py
```

游戏将显示主菜单，可以选择开始新游戏或加载已有游戏。

### 运行测试程序

项目包含多个测试文件，用于验证各模块功能：

```bash
# AI模块测试
python3 test/ai_test.py

# 数据访问测试
python3 test/test_data_access.py

# 存档系统测试
python3 test/test_save_system.py

# 存档内存管理测试
python3 test/test_save_memory.py

# 简单循环周期测试
python3 test/test_simple_loop_cycle.py
```

这些测试展示了核心功能，包括：
1. 创建角色属性
2. 使用角色属性构建AI提示词
3. 调用API生成故事和选择
4. 根据选择更新角色属性
5. 数据访问和存档管理

## 模块组合示例

### 创建角色并生成故事

```python
# 导入角色模块
from character.character_manager import get_attribute, set_attribute, configure_save_system

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

# 配置存档系统
configure_save_system()

# 创建基本角色属性
set_attribute("姓名", "李逍遥")
set_attribute("世界", "奇幻大陆")
set_attribute("境界", "炼气期")
set_attribute("故事梗概", "少年李逍遥无意间获得一本古老的功法，开始了修仙之路。")
set_attribute("当前事件", "李逍遥来到了一座神秘的洞穴前，传说里面藏有珍贵的宝物。")
set_attribute("事件选择", "探索洞穴")

# 初始化故事线管理器
manager = StorylineManager()

# 生成故事（会自动使用和更新角色属性）
success = manager.generate_story("simple_loop")

# 显示生成的故事
print("【故事内容】")
print(get_attribute("当前事件"))

# 显示选择
print("\n【可选选项】")
for i, choice in enumerate([get_attribute("选项1"), get_attribute("选项2"), get_attribute("选项3")]):
    print(f"{i+1}. {choice}")

# 进行选择并记录
choice_index = 0  # 选择第一个选项
set_attribute("事件选择", get_attribute("选项1"))

# 再次生成故事，继续情节
success = manager.generate_story("simple_loop")
```

### 模板配置与存储映射

故事模板通过JSON文件定义，包括提示片段、输出格式和存储映射：

```json
{
  "template_id": "simple_loop",
  "name": "简单循环测试模板",
  "prompt_segments": [
    "(主角名称：{姓名})",
    "(背景世界:{世界})",
    "(主角境界:{境界})",
    "(全局故事梗概:{故事梗概})",
    "(当前事件:{当前事件})",
    "(事件选择:{事件选择})",
    "..."
  ],
  "output_storage": {
    "story": "当前事件",
    "content": "故事梗概",
    "choice1": "选项1",
    "choice2": "选项2",
    "choice3": "选项3"
  }
}
```

使用模板编辑器可以可视化地配置这些映射关系。当模板执行时，系统会自动将输出字段存储到对应的角色属性中。

## 设计理念

本引擎的设计遵循以下核心理念：

1. **属性驱动**：系统直接使用角色属性进行模板渲染，简化了变量管理
2. **模块化结构**：各功能模块高度分离，便于维护和扩展
3. **自包含模板**：每个模板是一个完整的事件单元，包含输出格式、存储映射和属性变化
4. **简洁API**：提供直观的接口，让每个方法的功能更加清晰
5. **统一数据流**：属性存储系统统一，模板可定义输出映射到角色属性
6. **易于使用**：编辑工具提供直观界面，包括提示片段管理、输出格式配置等功能

系统支持多种简化的开发工作流程：
- 双击属性可直接插入到片段编辑器
- 右键菜单提供常用操作
- 使用提示和帮助说明减少学习成本

## 总结

文字冒险游戏引擎采用直观的属性引用和独立模板设计，具有简单的API和统一的属性存储系统，为开发者提供了一个高度可定制的故事生成框架。系统具有模块化结构，分离了角色管理、故事生成和游戏流程控制等功能，可以轻松扩展和定制。

## 许可证

本项目使用MIT许可证 - 详情请参阅LICENSE文件。 