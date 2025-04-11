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

### 创建角色并生成故事 (简化版API)

```python
# 导入角色模块
from character.character_manager import create_attribute, get_attribute

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

# 创建角色属性
create_attribute("name", "李逍遥")
create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
create_attribute("力量", 8)
create_attribute("敏捷", 12)
create_attribute("智力", 10)

# 初始化故事线管理器
manager = StorylineManager()

# 生成故事（自动使用角色属性）
story_content, choices, story_id = manager.generate_story("adventure_template")

# 显示故事
print(story_content)

# 显示选择
for choice in choices:
    print(f"{choice['id'] + 1}. {choice['text']}")

# 选择一个选项并应用属性变化
manager.make_choice(story_id, 0)  # 选择第一个选项

# 角色属性已自动更新
print(f"力量: {get_attribute('力量')}")
```

### 自动存储映射

使用模板的`output_storage`字段配置自动存储映射：

```json
{
  "template_id": "adventure_template",
  "name": "冒险模板",
  "prompt_segments": ["..."],
  "output_storage": {
    "story": "current_story",
    "choice1": "option1",
    "choice2": "option2",
    "choice3": "option3",
    "content": "story_content"
  }
}
```

使用模板编辑器的"输出存储"选项卡，可以可视化地配置这些映射关系。当模板执行时，系统会自动将输出字段存储到对应的角色属性中。

## 系统简化与改进

## 设计理念的转变

在本次重构中，我们对系统进行了彻底的简化，移除了不必要的复杂性，使得整个故事生成系统更加直观和易于使用。主要改进包括：

1. **直接使用角色属性**：移除了内外变量转换的复杂性，模板直接使用角色属性进行渲染
2. **简化的API设计**：减少API方法数量，让每个方法的功能更加清晰
3. **自包含的模板**：每个模板现在是一个完整的事件单元，包含输出格式、存储映射和属性变化
4. **统一的接口**：提供直观的界面，将相关功能整合到同一选项卡
5. **去除不必要功能**：移除模板链接配置等复杂功能，让用户对故事流程有更直接的控制

## 主要改动

### StorylineManager改进

1. **直接属性访问**：
   - 移除了`required_inputs`和内部变量，直接使用角色属性
   - 使用`_replace_placeholders`方法自动处理属性占位符

2. **简化API**：
   - `generate_story(template_id)` - 直接生成故事，自动应用存储映射
   - `make_choice(story_id, choice_index)` - 执行选择，应用属性变化

3. **存储重设计**：
   - 统一的属性存储系统，每个模板可以定义`output_storage`字段
   - 自动创建或更新角色属性，无需手动调用存储方法

### 模板编辑器重构

1. **重新设计的选项卡**：
   - **基本信息**：常规的模板元数据
   - **提示片段**：直接引用角色属性的提示片段管理
   - **输出和存储**：整合输出格式和存储映射到一个界面
   - **角色属性**：浏览并引用当前角色属性
   - **提示词处理**：测试和定制提示词模板
   - **JSON预览**：查看完整的模板格式

2. **简化的工作流程**：
   - 双击属性可直接插入到片段编辑器
   - 右键菜单提供常用操作
   - 使用提示和帮助说明减少学习成本

3. **模板结构优化**：
   - 移除`required_inputs`字段
   - 移除`next_templates`配置
   - 添加统一的`output_storage`映射

## 使用示例

新系统使用起来更加简单直接：

```python
# 初始化管理器
manager = StorylineManager()

# 直接生成故事，自动使用角色属性
story_content, choices, story_id = manager.generate_story("adventure_template")

# 选择一个选项，自动应用属性变化
manager.make_choice(story_id, 0)  # 选择第一个选项
```

## 总结

这次重构将复杂的变量转换和模板关联转变为直观的属性引用和独立模板，极大地降低了系统的复杂度和学习门槛。新系统提供了更加简洁和一致的用户体验，同时保留了原有系统的核心功能。

## 许可证

本项目使用MIT许可证 - 详情请参阅LICENSE文件。 