# Storyline模块使用指南

Storyline模块是文字冒险游戏的故事线管理系统，用于创建、编辑和管理游戏的故事模板，并根据这些模板生成动态的游戏内容。本指南将帮助您快速上手使用Storyline模块。

## 核心概念

在开始之前，让我们了解Storyline模块的几个核心概念：

1. **模板（Template）**：定义了故事的基本结构、输入参数和输出格式。模板决定了故事的生成方式和可能的分支选择。

2. **故事片段（StorySegment）**：基于模板生成的具体故事内容，包含故事正文、可用选择和选择结果。

3. **故事选择（StoryChoice）**：玩家在故事中可以做出的选择，会影响角色属性和后续故事发展。

4. **模板链接（Template Linking）**：不同模板之间的关联，定义了故事的流程和可能的分支路径。

## 基本用法

### 1. 创建和使用故事模板

```python
from storyline.storyline_manager import StorylineManager

# 初始化故事线管理器
manager = StorylineManager()

# 加载模板
template = manager.load_template("adventure_template")

# 定义变量
variables = {
    "world_setting": "奇幻世界",
    "character.name": "李逍遥",
    "character.background": "自小在山野长大的少年，性格乐观开朗",
    "character.strength": 8,
    "character.agility": 12,
    "character.intelligence": 10,
    "character.constitution": 9,
    "character.charisma": 11,
    "character.skills": ["基础剑法", "轻功", "药理知识"],
    "location": "神秘山洞"
}

# 生成故事
story = manager.generate_story(template, variables)

# 显示故事内容
print(story.content)

# 显示可用选择
for i, choice in enumerate(story.choices):
    print(f"{i+1}. {choice.text}")
```

### 2. 根据玩家选择继续故事

```python
# 玩家选择索引（从0开始）
choice_index = 0  # 对应第一个选择

# 选择特定分支
choice = manager.choose_branch(story, choice_index)
print(f"你选择了: {choice.text}")
print(f"可能的结果: {choice.outcome}")
print(f"属性变化: {choice.stat_changes}")

# 继续生成下一段故事
next_story = manager.continue_story(story, choice_index, variables)

# 显示下一段故事
print(next_story.content)
```

### 3. 保存和加载故事

```python
# 保存故事到文件
manager.save_story_to_file(story, "save/current_story.json")

# 从文件加载故事
loaded_story = manager.load_story_from_file("save/current_story.json")
```

### 4. 直接使用角色属性生成故事（新功能）

Storyline模块现在可以直接从character模块获取角色属性，无需手动构建变量字典：

```python
from storyline.storyline_manager import StorylineManager
from character.character_manager import create_attribute, get_attribute

# 设置角色属性
create_attribute("name", "李逍遥")
create_attribute("background", "自小在山野长大的少年")
create_attribute("strength", 8)
create_attribute("intelligence", 10)
create_attribute("skills", ["剑法", "轻功"])
create_attribute("location", "古道森林")  # 可选的额外属性

# 初始化故事线管理器
manager = StorylineManager()

# 直接使用角色属性生成故事
story = manager.generate_story_from_character("adventure_template")

# 显示故事内容
print(story.content)

# 选择一个分支并继续故事，同时自动更新角色属性
choice_index = 0  # 玩家选择的选项索引
next_story = manager.continue_story_from_character(story, choice_index)
```

这种方式有以下优点：

1. **简化代码**：不需要手动构建变量字典
2. **属性自动更新**：选择后会自动应用属性变化到角色
3. **一致性**：确保故事使用的是最新的角色数据
4. **灵活性**：仍然可以通过extra_variables参数添加额外变量

## 模板结构

模板采用JSON格式，包含以下主要部分：

1. **基本信息**：模板ID、名称、描述、版本等基本信息。

2. **提示片段（prompt_segments）**：用于构建AI提示词的片段列表，包括：
   - 背景信息：以 `(...)` 包围，提供故事的上下文
   - 内容指令：以 `<...>` 包围，指定需要生成的内容
   - 输出格式：以 `{...}` 包围，定义输出的JSON结构

3. **必需输入（required_inputs）**：生成故事时必须提供的变量列表。

4. **输出格式（output_format）**：期望的输出字段及其类型。

5. **标签（tags）**：用于分类和筛选模板的标签。

6. **下一步模板（next_templates）**：定义每个选择可能链接到的下一个模板。

## 使用模板编辑工具

Storyline模块提供了一个模板编辑工具，可以在图形界面中创建和编辑模板：

```python
from storyline.tools.template_editor import TemplateEditor

# 启动编辑器
editor = TemplateEditor()
editor.run()
```

或者通过命令行启动：

```bash
python -m storyline.tools.template_editor
```

此外，还提供了命令行工具用于管理模板：

```bash
# 列出所有模板
python -m storyline.tools.template_builder list

# 显示特定模板详情
python -m storyline.tools.template_builder show adventure_template

# 创建新模板
python -m storyline.tools.template_builder create
```

## 高级用法

### 1. 创建自定义模板

```python
# 创建新模板
new_template = {
    "template_id": "my_custom_template",
    "name": "我的自定义模板",
    "description": "专为特定场景设计的模板",
    "version": "1.0",
    "author": "用户",
    "created_at": "2023-04-09",
    "prompt_segments": [
        # 添加你的提示片段
    ],
    "required_inputs": [
        # 添加必需的输入变量
    ],
    "output_format": {
        # 定义输出格式
    },
    "tags": ["自定义"],
    "next_templates": {
        # 定义下一步模板链接
    }
}

# 保存模板
manager.save_template(new_template)
```

### 2. 复杂的模板链接

您可以创建复杂的模板链接网络，实现故事的非线性分支：

```python
# 模板A链接到模板B和C
template_a = {
    "template_id": "template_a",
    # ...其他属性...
    "next_templates": {
        "choice1": ["template_b"],
        "choice2": ["template_c"]
    }
}

# 模板B链接到模板D和E
template_b = {
    "template_id": "template_b",
    # ...其他属性...
    "next_templates": {
        "choice1": ["template_d"],
        "choice2": ["template_e"]
    }
}

# 保存模板
manager.save_template(template_a)
manager.save_template(template_b)
```

### 3. 动态生成模板

您可以在运行时动态生成或修改模板：

```python
# 加载基础模板
base_template = manager.load_template("base_template")

# 修改模板
modified_template = base_template.copy()
modified_template["template_id"] = "modified_template"
modified_template["name"] = "动态修改的模板"

# 添加新的提示片段
modified_template["prompt_segments"].append("(新增内容: {new_content})")
modified_template["required_inputs"].append("new_content")

# 保存修改后的模板
manager.save_template(modified_template)
```

### 4. 故事线与角色属性集成（新功能）

创建一个完整的游戏循环，使用角色属性生成故事并自动更新属性：

```python
from storyline.storyline_manager import StorylineManager
from character.character_manager import get_attribute, set_attribute

# 初始化
manager = StorylineManager()

# 游戏主循环
def game_loop():
    # 开始游戏，使用初始模板
    current_story = manager.generate_story_from_character("intro_template")
    
    while True:
        # 显示故事
        print(current_story.content)
        
        # 显示选择
        for i, choice in enumerate(current_story.choices, 1):
            print(f"{i}. {choice.text}")
        
        # 获取玩家输入
        choice_index = int(input("请选择 (1-3): ")) - 1
        
        # 继续故事（自动应用属性变化）
        next_story = manager.continue_story_from_character(
            current_story, 
            choice_index
        )
        
        # 更新当前故事
        current_story = next_story
        
        # 检查游戏结束条件
        if not current_story or not current_story.choices:
            print("游戏结束")
            break
```

## 最佳实践

1. **模板设计**：
   - 每个模板专注于一个特定类型的故事场景
   - 提供有意义的选择，每个选择应导致不同的结果
   - 合理设置属性变化，保持游戏平衡性

2. **变量命名**：
   - 对于角色属性，使用 `character.attribute_name` 格式
   - 对于世界设定，使用 `world.setting_name` 格式
   - 对于场景相关变量，使用描述性名称

3. **模板组织**：
   - 为模板添加有意义的标签，便于分类和筛选
   - 使用清晰的模板ID和版本号，便于管理
   - 记录模板的作者和创建日期，便于追踪变更

4. **故事连贯性**：
   - 在模板中引用前序故事和选择
   - 确保不同模板之间的风格和语调一致
   - 使用变量保持角色和世界设定的一致性

5. **角色属性集成**：
   - 在角色属性中定义location和world_setting等常用场景变量
   - 使用generate_story_from_character和continue_story_from_character方法自动处理角色属性
   - 为特殊场景使用extra_variables参数提供额外变量

## 故障排除

如果您在使用Storyline模块时遇到问题：

1. **模板加载失败**：
   - 检查模板文件是否存在
   - 确保模板格式正确的JSON格式
   - 查看错误消息以获取更多信息

2. **故事生成失败**：
   - 检查是否提供了所有必需的输入变量
   - 确保AI模块配置正确
   - 检查API密钥和网络连接

3. **选择分支问题**：
   - 确保模板中定义了正确的下一步模板
   - 检查选择索引是否有效
   - 确保下一个模板存在并可访问

4. **角色属性问题**：
   - 确保角色属性在调用生成故事前已设置
   - 检查角色属性的命名是否与模板中使用的变量名一致
   - 如果某些属性无法更新，检查属性类型是否为数字

## 示例模板

Storyline模块提供了几个预定义的模板：

1. **base_template**：一个基础模板，可以作为自定义模板的起点
2. **adventure_template**：适用于冒险探索类故事
3. **dialogue_template**：适用于对话互动类故事
4. **combat_template**：适用于战斗场景
5. **decision_template**：适用于重要决策场景 