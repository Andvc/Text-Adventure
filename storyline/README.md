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

## 占位符系统

StorylineManager利用ai模块的强大占位符系统，在故事模板中可以使用多种占位符格式引用数据：

### 1. 基本占位符

基本占位符格式用于引用存档数据：

```
{key} - 直接引用存档中的顶级字段
{key.subkey} - 引用嵌套对象中的字段
```

示例：
```json
"prompt_segments": [
  "(角色名称：{character.name})",
  "(所在位置：{location.name})",
  "(当前任务：{quests.active[0].title})"
]
```

### 2. 嵌套占位符

新增嵌套占位符支持，可以在占位符内部嵌入其他占位符，实现动态引用：

```
{character.{active_stat}} - 通过变量引用不同属性
{locations[{current_location_index}].name} - 使用变量作为索引
```

嵌套占位符的工作原理：系统先解析内部占位符，然后再解析外部占位符，支持多达20层的嵌套。

示例：
```json
"prompt_segments": [
  "(当前关注属性：{active_stat})",  
  "(该属性的值：{character.stats.{active_stat}})",
  "(当前位置索引：{current_location_index})",
  "(当前位置：{locations[{current_location_index}].name})"
]
```

如果存档包含：
```json
{
  "active_stat": "intelligence",
  "character": {
    "stats": {
      "strength": 10,
      "dexterity": 8,
      "intelligence": 15
    }
  },
  "current_location_index": 2,
  "locations": [
    {"name": "森林"},
    {"name": "山洞"},
    {"name": "魔法塔"}
  ]
}
```

那么处理后的结果为：
```
(当前关注属性：intelligence)
(该属性的值：15)
(当前位置索引：2)
(当前位置：魔法塔)
```

### 3. 文本数据引用

可以直接引用game/text目录下的JSON文件中的数据：

```
{text;file_name;path} - 从data/text/file_name.json文件中引用指定路径的数据
```

这对于引用共享的游戏世界设定非常有用，避免重复定义数据。

示例：
```json
"prompt_segments": [
  "(世界观：{text;worlds;current_world.description})",
  "(主要种族：{text;races;races[0].name})",
  "(流行语言：{text;languages;languages.common.name})"
]
```

### 4. 数组处理

改进的数组处理功能：

```
{key.array[0]} - 引用数组的特定索引
{key.array} - 引用整个数组
{key.array[{index}]} - 使用变量作为索引
```

当引用数组但没有提供索引时，会返回整个数组，可用于提供完整列表。

示例：
```json
"prompt_segments": [
  "(所有技能：{character.skills})",
  "(主要技能：{character.skills[0]})",
  "(当前技能：{character.skills[{active_skill_index}]})"
]
```

## 实际应用示例

### 动态引用示例

这个模板使用嵌套占位符根据当前情境生成不同类型的事件：

```json
{
  "template_id": "dynamic_event",
  "name": "动态情境事件生成",
  "prompt_segments": [
    "(当前情境：{current_situation})",
    "(可用事件类型：{text;event_types;types})",
    "(选择的事件类型：{text;event_types;types[{situation_to_event_map.{current_situation}}]})",
    "<根据情境 '{current_situation}' 和事件类型 '{text;event_types;types[{situation_to_event_map.{current_situation}}].name}' 生成相应事件>",
    "[event=\"*\"]"
  ],
  "output_storage": {
    "event": "current_event"
  }
}
```

在这个例子中：
1. 首先引用当前情境 `{current_situation}`
2. 从文本数据文件引用所有可用事件类型
3. 使用嵌套引用`{situation_to_event_map.{current_situation}}`获取适合当前情境的事件类型索引
4. 根据该索引从事件类型列表中选择适当的事件类型名称

### 世界探索示例

利用文本数据引用和嵌套占位符创建动态探索体验：

```json
{
  "template_id": "world_exploration",
  "name": "世界探索系统",
  "prompt_segments": [
    "(当前位置：{current_region})",
    "(该地区信息：{text;world_regions;regions.{current_region}})",
    "(毗邻地区：{text;world_regions;regions.{current_region}.connected_regions})",
    "(天气系统：{text;weather;regions.{current_region}.weather_patterns[{current_season}]})",
    "<描述角色在 '{current_region}' 地区的探索经历，考虑当前季节 '{current_season}' 的天气特点>",
    "[exploration_event=\"*\"]",
    "<提供三个可能的探索选择，包括探索周边地区 {text;world_regions;regions.{current_region}.connected_regions}>",
    "[option1=\"*\",option2=\"*\",option3=\"*\"]"
  ],
  "output_storage": {
    "exploration_event": "current_exploration",
    "option1": "exploration_options[0]",
    "option2": "exploration_options[1]",
    "option3": "exploration_options[2]"
  }
}
```

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

### 1. 模板设计
- 使用清晰的标题和分组
- 提供详细的背景信息
- 明确指定输出格式
- 合理设计存储映射

### 2. 提示词编写
- 使用具体的指令和要求
- 提供足够的上下文信息
- 明确指定输出格式
- 添加必要的约束条件

### 3. 占位符使用
- 合理使用嵌套占位符，避免过度复杂的结构
- 将共享数据放在text文件夹，通过文本数据引用访问
- 提供合理的变量索引和默认值
- 测试复杂占位符组合，确保正确解析

### 4. 存档管理
- 使用有意义的字段名
- 保持数据结构的一致性
- 合理组织嵌套数据
- 及时保存更新

## 注意事项

1. 模板ID必须是唯一的
2. 所有占位符必须存在于存档数据或text文件中
3. 存储映射的字段必须与输出格式匹配
4. 生成失败时会返回False，需要检查错误信息
5. 建议在生成前备份存档数据
6. 嵌套占位符最多支持20层递归，以防止无限循环
7. 复杂的占位符结构可能影响性能，请适度使用

## 变更日志

### 2024-05-21

- **增强的占位符系统**：
  - 添加嵌套占位符支持，允许在占位符内部使用其他占位符，实现动态引用
  - 添加文本数据引用功能，支持从data/text目录下的JSON文件中读取数据
  - 改进数组处理，支持变量索引和完整数组引用
  - 统一占位符处理逻辑，确保在editor和storyline模块中一致的行为
  - 限制嵌套层级最多20层，防止无限递归

- **模板功能增强**：
  - 支持更复杂的动态数据引用
  - 优化模板处理流程，提高生成效率
  - 增强错误处理和日志记录
  - 添加模板测试工具，方便开发者验证模板有效性

- **示例更新**：
  - 添加`dynamic_event`示例模板，展示嵌套占位符的应用
  - 添加`world_exploration`示例模板，展示文本数据引用功能
  - 更新`simple_loop`模板，适配新的占位符功能 