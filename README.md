# 文字冒险游戏引擎

这是一个基于Python的文字冒险游戏引擎，提供角色管理、AI驱动的故事生成和故事线管理等核心功能。

## 项目结构

```
Text Adventure/
├── ai/                # AI模块 - 提示词处理与API交互
├── character/         # 角色模块 - 角色属性管理
├── storyline/         # 故事线模块 - 故事模板与剧情生成
├── save/              # 游戏存档目录
├── .env               # 环境变量配置
├── test_integration.py # 集成测试程序
└── README.md          # 本文档
```

## 主要模块

### AI模块

AI模块提供了构建AI提示词、调用大模型API并解析JSON格式响应的功能。详细文档请参考[AI模块说明](ai/README.md)和[AI模块使用指南](ai/user_guide.md)。

主要功能：
- 提示词构建与处理
- API连接与调用
- 结果解析与结构化

### 角色模块

角色模块负责管理游戏中角色的属性数据，支持创建、读取、修改和删除角色属性。详细文档请参考[角色模块说明](character/README.md)和[角色模块使用指南](character/user_guide.md)。

主要功能：
- 基本属性操作
- 属性类别管理
- 物品属性管理
- 存档系统配置

### 故事线模块

故事线模块管理游戏的主线剧情，提供了创建、编辑和管理故事模板的工具，以及生成基于模板的游戏故事内容的功能。详细文档请参考[故事线模块说明](storyline/README.md)和[故事线模块使用指南](storyline/user_guide.md)。

主要功能：
- 模板管理
- 故事生成
- 分支选择
- 故事状态跟踪

## 工具集

### 模板编辑工具

故事线模块提供了两种模板编辑工具：

1. **图形界面编辑器**：提供可视化界面编辑模板
   ```bash
   python -m storyline.tools.template_editor
   ```

   **主要特性**:
   - 基本信息编辑（ID、名称、描述等）
   - 提示片段管理（背景信息、内容指令、输出格式）
   - 输入/输出字段定义
   - 模板链接配置
   - **角色属性集成**：直接浏览、选择并导入角色属性到模板中
   - **存档管理**：查看、选择、创建和编辑游戏存档
   - **提示词处理**：使用AI模块的提示词处理功能，直接生成和测试提示词
   - **模板专属提示词**：每个模板都可以设置专属的提示词模板，自动保存到模板数据
   - **输出存储映射**：配置模板输出字段到角色属性的自动存储映射
   - JSON预览与验证

2. **命令行工具**（遗留，功能有限）：适合基本的脚本操作
   ```bash
   python -m storyline.tools.template_builder list
   python -m storyline.tools.template_builder create
   python -m storyline.tools.template_builder show adventure_template
   ```
   > **注意**: 该工具不支持最新功能，如输出存储映射、提示词处理等，推荐使用图形界面编辑器

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

运行集成测试程序，体验完整流程：

```bash
python test_integration.py
```

集成测试展示了以下功能：
1. 创建角色属性
2. 使用角色属性构建AI提示词
3. 调用API生成故事和选择
4. 根据选择更新角色属性

## 模块组合示例

### 创建角色并生成故事

```python
# 导入角色模块
from character.character_manager import create_attribute, get_attribute, set_attribute

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

# 创建角色
create_attribute("name", "李逍遥")
create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
create_attribute("strength", 8)
create_attribute("agility", 12)
create_attribute("intelligence", 10)

# 初始化故事线管理器
manager = StorylineManager()

# 使用简化API生成故事（自动读取角色属性）
story_content, choices = manager.run_template("adventure_template")

# 显示故事
print(story_content)

# 显示选择
for choice in choices:
    print(f"{choice['id'] + 1}. {choice['text']}")

# 假设玩家选择了第一个选项
story_id = next(iter(manager.story_segments))  # 获取当前故事ID
next_content, next_choices = manager.make_choice(story_id, 0)

# 显示下一段故事
print(next_content)
```

### 带额外变量的故事生成

```python
# 使用额外变量和自定义提示词模板生成故事
variables = {
    "location": "古老的图书馆",
    "goal": "寻找失落的典籍",
    "obstacle": "神秘的禁制"
}

# 生成故事
story_content, choices = manager.run_template("library_template", variables)
```

### 将模板输出存储到角色属性

```python
# 定义要存储的输出字段映射
store_fields = {
    "story": "current_story",    # 将story字段存储到current_story属性
    "choice1": "option1",        # 将choice1字段存储到option1属性
    "choice2": "option2",        # 将choice2字段存储到option2属性
    "content": "story_content"   # 将格式化的故事内容存储到story_content属性
}

# 运行模板并存储输出到角色属性
story_content, choices = manager.run_template_and_store(
    "adventure_template", 
    store_fields=store_fields
)

# 执行选择并存储下一段故事的输出
story_id = next(iter(manager.story_segments))
next_content, next_choices = manager.make_choice_and_store(
    story_id, 
    0,  # 选择第一个选项
    store_fields={"story": "next_story", "choice1": "next_option1"}
)

# 现在可以从角色属性中获取存储的内容
current_story = get_attribute("current_story")
next_story = get_attribute("next_story")
```

## 最近更新

### 模板变量处理优化
- 优化了模板变量处理机制，模板现在可以直接引用和修改角色属性，无需中间转换
- 移除了冗余的变量传递过程，自动从character_manager加载所有可用属性
- 执行模板后直接将输出存储到角色属性中，简化了存储逻辑
- 优化API调用流程，同时保持向后兼容性
- 减少了数据复制和转换，提高了执行效率

### 模板自动存储功能
- 新增"单模板自动存储"功能，使模板能够自动应用存储映射，将输出存储到角色属性
- 无需手动调用`run_template_and_store`，`generate_story`方法会自动检查并应用模板中的`output_storage`字段
- 模板可以自动应用输出存储、属性变化和事件处理，成为一个完整的游戏事件单元
- 每次`continue_story`也会自动应用下一个模板中的`output_storage`设置
- 模板编辑器中的"输出存储"选项卡现在能完整加载和编辑模板中的存储映射设置

### 模板输出存储功能
- 新增`run_template_and_store`和`make_choice_and_store`方法，可以将模板执行结果直接存储到角色属性
- 支持将原始输出字段和格式化后的故事内容存储为属性
- 自动处理属性的创建和更新，避免重复代码
- 添加了示例脚本`examples/store_output_example.py`展示如何使用这些功能
- 可以与已有的角色属性系统无缝集成，便于游戏状态管理

### 模板专属提示词模板和简化API
- 每个模板现在可以设置专属的提示词处理模板，自动保存在模板JSON中
- StorylineManager提供了简化的API，使调用更加简单直观：
  - `run_template(template_id, variables=None)` - 一步运行模板生成故事
  - `make_choice(story_id, choice_index, variables=None)` - 执行选择并生成下一段故事
  - `get_story_content(story_id)` - 获取故事内容
  - `get_story_choices(story_id)` - 获取选择选项
- 简化的API能自动处理角色属性读取，使集成更加容易
- 查看 `examples/simple_story_api.py` 了解如何使用简化API

### 提示词处理功能集成
- 新增"提示词处理"选项卡，直接在模板编辑器中访问AI模块的提示词功能
- 提供自定义提示词模板的能力，可编辑和保存模板
- 支持一键从当前编辑的模板片段生成完整的提示词
- 预览生成的提示词并直接复制到剪贴板，方便测试

### 存档管理功能
- 新增"存档管理"选项卡，直接在编辑器中管理游戏存档
- 显示当前使用的存档文件路径
- 支持选择其他存档文件或创建新存档
- 提供属性编辑器，可以直接查看、添加、修改和删除存档中的属性
- 支持所有数据类型的编辑，包括数字、字符串、布尔值和复杂JSON数据

### 角色属性集成到模板编辑器
- 新增"角色属性"选项卡，直接浏览现有角色属性
- 支持按类别组织显示属性
- 双击属性可预览并插入到模板中
- 支持将属性作为输入变量或提示片段内容使用

## 许可证

本项目使用MIT许可证 - 详情请参阅LICENSE文件。 