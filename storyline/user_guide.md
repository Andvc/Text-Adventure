# Storyline模块使用指南 (简化版)

Storyline模块是文字冒险游戏的故事线管理系统，用于创建、编辑和管理游戏的故事模板，并根据这些模板生成动态的游戏内容。本指南介绍了新版简化的Storyline模块的使用方法。

## 重要更新

新版StorylineManager进行了全面重构和简化：

1. **直接使用角色属性**：不再需要内外变量转换，模板可以直接访问和修改角色属性
2. **简化的API**：移除了不必要的复杂性，保留核心功能
3. **自动存储映射**：模板可以自动将生成结果保存到指定的角色属性中
4. **移除了自动导入下一个模板**：更灵活的故事流程控制

## 核心概念

在开始之前，让我们了解Storyline模块的几个核心概念：

1. **模板（Template）**：定义了故事的基本结构和输出格式。

2. **提示片段（Prompt Segments）**：构成模板的文本片段，包括背景信息、内容指令和输出格式。

3. **角色属性（Character Attributes）**：由character模块管理的角色数据，可直接在模板中引用。

4. **存储映射（Storage Mapping）**：定义如何将生成的内容存储到角色属性中。

5. **故事记录（Story History）**：生成的故事内容和选择选项的记录。

## 基本用法

### 1. 初始化和生成故事

```python
from storyline.storyline_manager import StorylineManager
from character.character_manager import create_attribute, set_attribute, get_attribute

# 创建角色属性
create_attribute("name", "李逍遥")
create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
create_attribute("力量", 8)
create_attribute("敏捷", 12)
create_attribute("智力", 10)
create_attribute("location", "古老的森林")

# 初始化故事线管理器
manager = StorylineManager()

# 生成故事（自动使用角色属性）
story_content, choices, story_id = manager.generate_story("adventure_template")

# 显示故事内容
print(story_content)

# 显示可用选择
for i, choice in enumerate(choices):
    print(f"{i+1}. {choice['text']}")
```

### 2. 选择分支

```python
# 选择第一个选项
choice_index = 0

# 执行选择，自动应用属性变化
manager.make_choice(story_id, choice_index)

# 查看属性变化
print(f"力量: {get_attribute('力量')}")
print(f"最后选择: {get_attribute('last_choice')}")
```

### 3. 获取和保存故事记录

```python
# 获取特定故事记录
story_data = manager.get_story(story_id)
if story_data:
    print(f"模板ID: {story_data['template_id']}")
    print(f"生成时间: {story_data['generated_at']}")

# 保存故事历史到文件
manager.save_history_to_file("saves/story_history.json")

# 加载故事历史
manager.load_history_from_file("saves/story_history.json")

# 清除历史记录
manager.clear_history()
```

## 模板结构

模板采用JSON格式，主要部分包括：

```json
{
  "template_id": "adventure_template",
  "name": "冒险模板",
  "description": "生成一段冒险故事，提供三个选择选项",
  "version": "1.0",
  "author": "AI助手",
  "created_at": "2023-06-01",
  "tags": ["冒险", "选择", "示例"],
  "prompt_segments": [
    "(世界设定: {world_setting})",
    "(角色姓名: {name})",
    "(角色背景: {background})",
    "(当前位置: {location})",
    "<请描述{name}在{location}遭遇的一次冒险。角色的力量值为{力量}，敏捷值为{敏捷}，智力值为{智力}。>",
    "<生成一个引人入胜的场景，考验角色的能力，并提供三个不同的选择方向。>",
    "<每个选择应该对应不同的解决方案，分别侧重力量、敏捷和智力的运用。>",
    "<根据选择预设对应的属性变化。>",
    "{story=\"*\"}",
    "{choice1=\"*\"}",
    "{outcome1=\"*\"}",
    "{stat_change1=\"*\"}",
    "{choice2=\"*\"}",
    "{outcome2=\"*\"}",
    "{stat_change2=\"*\"}",
    "{choice3=\"*\"}",
    "{outcome3=\"*\"}",
    "{stat_change3=\"*\"}"
  ],
  "output_format": {
    "story": "string",
    "choice1": "string",
    "outcome1": "string",
    "stat_change1": "string",
    "choice2": "string",
    "outcome2": "string",
    "stat_change2": "string",
    "choice3": "string",
    "outcome3": "string",
    "stat_change3": "string"
  },
  "output_storage": {
    "story": "current_story",
    "choice1": "option1",
    "choice2": "option2",
    "choice3": "option3",
    "content": "story_content"
  },
  "prompt_template": "你是一个高级故事生成AI，请根据以下提示创建故事内容。\n\n## 背景信息\n{background}\n\n## 内容要求\n{content}\n\n## 输出格式\n请严格按照以下JSON格式回复：\n{format}"
}
```

### 关键部分说明

1. **提示片段（prompt_segments）**：构建AI提示词的片段，分为：
   - 背景信息：以 `(...)` 包围，如 `(角色姓名: {name})`
   - 内容指令：以 `<...>` 包围，如 `<请描述{name}在{location}遭遇的一次冒险>`
   - 输出格式：以 `{key="*"}` 格式，如 `{story="*"}`

2. **输出格式（output_format）**：指定AI返回的JSON字段及其数据类型。

3. **输出存储（output_storage）**：指定如何将输出字段映射到角色属性。
   - 特殊字段`content`指完整的故事内容

4. **提示词模板（prompt_template）**：自定义的提示词构建模板。

## 主要API

### StorylineManager类

#### 初始化

```python
manager = StorylineManager(templates_dir=None)
```

- `templates_dir`：模板目录路径（可选），默认使用模块的templates目录

#### 模板管理

```python
# 列出所有模板
templates = manager.list_templates()

# 加载模板
template = manager.load_template("adventure_template")

# 保存模板
manager.save_template(template_data)

# 删除模板
manager.delete_template("old_template_id")
```

#### 故事生成

```python
# 生成故事
story_content, choices, story_id = manager.generate_story(
    template_id,             # 模板ID
    use_template_storage=True # 是否应用模板中的存储映射
)
```

返回值：
- `story_content`：故事内容文本
- `choices`：选项列表，每个选项是包含id、text和outcome的字典
- `story_id`：故事ID，用于后续操作

#### 选择分支

```python
# 根据玩家选择应用属性变化
manager.make_choice(story_id, choice_index)
```

- `story_id`：故事ID
- `choice_index`：选择的索引（从0开始）

#### 故事记录管理

```python
# 获取故事记录
story_data = manager.get_story(story_id)

# 清除历史记录
manager.clear_history()

# 保存历史记录到文件
manager.save_history_to_file(filepath)

# 从文件加载历史记录
manager.load_history_from_file(filepath)
```

## 使用模板编辑器

Storyline模块提供了一个图形界面模板编辑器：

```python
from storyline.tools.template_editor import run_editor

# 启动编辑器
run_editor()
```

或通过命令行启动：

```bash
python -m storyline.tools.template_editor
```

编辑器的主要功能：

1. **管理模板**：创建、编辑、删除和导入/导出模板
2. **编辑基本信息**：修改模板ID、名称、描述等基本信息
3. **编辑提示片段**：添加和组织提示片段
4. **设置输出格式**：定义期望的输出字段和类型
5. **配置存储映射**：设置如何将输出映射到角色属性
6. **浏览角色属性**：查看可用的角色属性，方便在模板中引用
7. **提示词处理**：自定义提示词模板，预览生成的提示词

## 完整示例

创建一个简单的文字冒险游戏循环：

```python
from storyline.storyline_manager import StorylineManager
from character.character_manager import create_attribute, get_attribute, get_all_attributes

def setup_character():
    """初始化角色属性"""
    create_attribute("name", "李逍遥")
    create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
    create_attribute("力量", 8)
    create_attribute("敏捷", 12)
    create_attribute("智力", 10)
    create_attribute("体质", 9)
    create_attribute("魅力", 11)
    create_attribute("location", "神秘森林")
    create_attribute("world_setting", "东方奇幻世界")

def main():
    """游戏主循环"""
    # 初始化角色
    setup_character()
    
    # 初始化故事管理器
    manager = StorylineManager()
    
    # 欢迎信息
    print("===== 文字冒险游戏 =====")
    print(f"欢迎，{get_attribute('name')}！你的冒险即将开始...\n")
    
    # 游戏循环
    while True:
        # 生成故事
        story_content, choices, story_id = manager.generate_story("adventure_template")
        
        # 显示故事
        print("\n" + "="*50)
        print(story_content)
        print("="*50 + "\n")
        
        # 显示选项
        print("你可以:")
        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice['text']}")
        print("0. 退出游戏")
        
        # 获取玩家输入
        try:
            choice = int(input("\n请选择> "))
            if choice == 0:
                print("你结束了冒险。再见！")
                break
                
            if choice < 1 or choice > len(choices):
                print("无效的选择，请重试。")
                continue
                
            # 执行选择
            manager.make_choice(story_id, choice-1)
            
            # 显示角色属性变化
            print("\n你的属性:")
            print(f"力量: {get_attribute('力量')}")
            print(f"敏捷: {get_attribute('敏捷')}")
            print(f"智力: {get_attribute('智力')}")
            
            # 按任意键继续
            input("\n按Enter继续...")
            
        except ValueError:
            print("请输入有效的数字。")
            continue
        except Exception as e:
            print(f"发生错误: {str(e)}")
            continue

if __name__ == "__main__":
    main()
```

## 最佳实践

1. **模板设计**：
   - 在提示片段中直接使用`{属性名}`格式引用角色属性
   - 提供有意义的选择，每个选择导致不同结果
   - 合理设置属性变化，保持游戏平衡性

2. **存储映射**：
   - 为重要输出设置存储映射，自动保存到角色属性
   - 使用`content`特殊字段存储完整格式化的故事内容

3. **角色属性**：
   - 预先创建所有必要的角色属性
   - 使用合适的数据类型（数字、字符串、列表、字典）
   - 使用合适的属性名称，便于在模板中引用

4. **故事连贯性**：
   - 在提示片段中引用`last_story`和`last_choice`等历史属性
   - 确保不同模板之间的风格一致
   - 记录和引用重要的剧情节点

## 故障排除

### 常见问题

1. **属性占位符无法替换**：
   - 检查角色属性是否已创建
   - 确认属性名称拼写正确
   - 占位符格式应为`{属性名}`

2. **选择无法应用属性变化**：
   - 检查`stat_change`格式是否正确，应为"属性名+/-值"
   - 确保属性值是数字类型
   - 查看调试输出有无错误信息

3. **故事生成失败**：
   - 确保模板ID正确且模板文件存在
   - 检查AI模块配置和API密钥
   - 查看提示词是否符合AI的要求

### 调试提示

1. 启用详细日志输出查看内部处理流程
2. 测试时使用`test_adventure_template.py`等示例脚本
3. 检查生成的故事历史记录，了解属性变化情况

## 扩展和自定义

### 创建自定义模板

使用模板编辑器或手动创建JSON文件：

1. 定义基本信息（ID、名称、描述等）
2. 创建提示片段，引用角色属性
3. 设置输出格式和存储映射
4. 自定义提示词模板（可选）
5. 保存到templates目录

### 集成到游戏系统

1. 创建游戏主循环，管理故事流程
2. 设计UI显示故事内容和选择选项
3. 处理玩家输入，调用`make_choice`
4. 根据角色属性更新游戏状态
5. 保存和加载游戏进度

## 示例模板

Storyline模块提供了几个预定义的模板：

1. **adventure_template**：冒险探索类故事
2. **combat_template**：战斗场景
3. **simple_loop**：简单循环故事
4. **base_template**：基础模板，可作为自定义模板的起点 