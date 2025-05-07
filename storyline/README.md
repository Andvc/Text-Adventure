# Storyline模块

这个模块负责管理文字冒险游戏的主线剧情。它提供了一系列工具来创建、编辑和管理故事模板，以及生成基于这些模板的游戏故事情节。

## 目录结构

```
storyline/
├── README.md                # 本文档
├── __init__.py              # 模块初始化文件
├── storyline_manager.py     # 故事线管理核心功能
└── templates/               # 存放故事模板的目录
```

## 核心概念

### 1. 模板（Template）
- 定义了故事的基本结构和输出格式
- 包含背景信息、内容指令和输出格式
- 支持自定义提示词模板

### 2. 提示片段（Prompt Segments）
- `(...)`: 背景信息，如`(主角名称：{character.name})`
- `<...>`: 内容指令，如`<请生成故事>`
- `[key="*"]`: 输出格式声明，如`[story="*"]`

### 3. 存储映射（Storage Mapping）
- 定义如何将生成的内容存储到存档数据中
- 支持嵌套数据结构的映射
- 自动处理数组类型的存储

### 4. 提示词处理（Prompt Processing）
- 智能解析和分类提示片段
- 支持内容和格式的配对
- 提供灵活的模板替换机制

## 主要功能

### 1. 模板管理
```python
# 初始化管理器
manager = StorylineManager()

# 列出所有模板
templates = manager.list_templates()

# 加载特定模板
template = manager.load_template("simple_loop")

# 保存模板
manager.save_template(template_data)

# 删除模板
manager.delete_template("old_template")
```

### 2. 故事生成
```python
# 生成故事
success = manager.generate_story("save_name", "template_id")

# 生成时不应用存储映射
success = manager.generate_story("save_name", "template_id", use_template_storage=False)
```

### 3. 存档数据访问
```python
from data.data_manager import (
    get_save_value,
    get_nested_save_value,
    get_indexed_save,
    load_save,
    save_data
)

# 获取存档数据
save_data = load_save("save_name", "character")

# 获取特定值
value = get_save_value("key", save_data)

# 获取嵌套值
nested_value = get_nested_save_value("parent.child", save_data)

# 获取数组元素
array_item = get_indexed_save("array", 0, save_data)
```

## 模板格式

```json
{
  "template_id": "simple_loop",
  "name": "魔法世界冒险模板",
  "description": "适用于魔法世界背景的循环故事生成",
  "version": "1.1",
  "author": "Andvc",
  "created_at": "2025-04-11",
  "tags": ["魔法", "冒险", "测试"],
  "prompt_segments": [
    "## 角色信息",
    "(主角名称：{character.name})",
    "(主角身份：{character.level})",
    "(所处世界：{world})",
    "",
    "## 故事背景",
    "(故事概要：{summary})",
    "",
    "## 当前情况",
    "(当前事件：{story})",
    "(玩家选择了：{selected_choice})",
    "",
    "## 生成要求",
    "<基于玩家的选择 '{selected_choice}'，描述接下来发生的新事件...>",
    "[story=\"*\"]",
    "",
    "<根据新发生的事件，生成三个不同的选择...>",
    "[choice1=\"*\",choice2=\"*\",choice3=\"*\"]",
    "",
    "<根据新的事件发展，更新故事梗概...>",
    "[summary=\"*\"]"
  ],
  "output_format": {
    "story": "string",
    "summary": "string",
    "choice1": "string",
    "choice2": "string",
    "choice3": "string"
  },
  "output_storage": {
    "story": "story",
    "summary": "summary",
    "choice1": "choice1",
    "choice2": "choice2",
    "choice3": "choice3"
  },
  "prompt_template": "你是一个专业的魔法世界故事生成AI...\n\n{background}\n\n请严格按照以下JSON格式回复：\n{format}"
}
```

### 模板关键部分

1. **prompt_segments**: 提示片段列表
   - 支持多级标题和分组
   - 可以引用存档数据中的任何字段
   - 支持内容和格式的配对

2. **output_format**: 定义输出字段和类型
   - 支持字符串、数字、布尔等基本类型
   - 支持嵌套数据结构

3. **output_storage**: 定义存储映射
   - 支持直接映射到存档字段
   - 支持嵌套路径映射
   - 支持数组索引映射

4. **prompt_template**: 自定义提示词模板
   - 支持背景信息替换 `{background}`
   - 支持内容指令替换 `{content}`
   - 支持输出格式替换 `{format}`
   - 支持输入信息替换 `{input_info}`
   - 支持JSON格式替换 `{json_format}`

## 使用示例

### 1. 创建新模板
```python
template = {
    "template_id": "new_template",
    "name": "新模板",
    "description": "测试模板",
    "prompt_segments": [
        "(背景信息：{background})",
        "<生成内容>",
        "[content=\"*\"]"
    ],
    "output_format": {
        "content": "string"
    },
    "output_storage": {
        "content": "story"
    }
}

manager.save_template(template)
```

### 2. 生成故事
```python
# 加载存档
save_data = load_save("player1", "character")

# 生成新故事
success = manager.generate_story("player1", "simple_loop")

if success:
    # 获取生成的内容
    story = get_save_value("story", save_data)
    choices = [
        get_save_value("choice1", save_data),
        get_save_value("choice2", save_data),
        get_save_value("choice3", save_data)
    ]
```

## 最佳实践

1. **模板设计**
   - 使用清晰的标题和分组
   - 提供详细的背景信息
   - 明确指定输出格式
   - 合理设计存储映射

2. **提示词编写**
   - 使用具体的指令和要求
   - 提供足够的上下文信息
   - 明确指定输出格式
   - 添加必要的约束条件

3. **存档管理**
   - 使用有意义的字段名
   - 保持数据结构的一致性
   - 合理组织嵌套数据
   - 及时保存更新

## 注意事项

1. 模板ID必须是唯一的
2. 所有占位符必须存在于存档数据中
3. 存储映射的字段必须与输出格式匹配
4. 生成失败时会返回False，需要检查错误信息
5. 建议在生成前备份存档数据 