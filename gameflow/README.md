# GameFlow 游戏流程模块

`gameflow` 模块是修仙文字冒险游戏的核心引擎组件，负责处理游戏中的各种流程和生成功能。该模块包含多个组件，用于处理角色背景生成、能力与物品生成、事件选择与处理等功能。

## 模块组件

### 1. BackgroundCreationManager 背景创建管理器

负责生成角色的时代背景和家庭背景，使用随机种子确保生成结果的多样性。

**主要功能**：
- 生成时代背景：创建角色所处的修仙世界时代背景
- 生成家庭背景：创建角色的家族、血脉和出身环境
- 运行背景创建流程：整合生成时代和家庭背景的完整流程

**使用示例**：
```python
from gameflow import BackgroundCreationManager

# 创建背景管理器
bg_manager = BackgroundCreationManager()

# 运行完整背景生成流程
result = bg_manager.run_background_creation_flow()

if result["success"]:
    # 获取生成的背景信息
    background = result["background"]
    era_info = background["era"]
    family_info = background["family"]
    
    print(f"时代背景: {era_info['name']}")
    print(f"家族背景: {family_info['name']}")
else:
    print(f"背景生成失败: {result['error']}")
```

### 2. PowerGenerator 能力生成器

负责生成武器、职业、法术等能力和物品，支持不同等级和类型的生成。

**支持的生成类型**：
- ability: 能力
- item: 物品
- magic: 魔法
- artifact: 法器
- elixir: 丹药
- technique: 功法
- cultivation_role: 修炼角色

**主要功能**：
- 各种类型物品和能力的生成
- 基于7级修仙境界体系的生成控制
- 支持自定义详情提示

**使用示例**：
```python
from gameflow import PowerGenerator

# 创建能力生成器
power_gen = PowerGenerator()

# 为指定存档生成一个3级法器
save_id = "player_save_001"
artifact = power_gen.generate_artifact(save_id, level=3, detail="青玉材质，擅长防御")

print(f"生成的法器: {artifact['name']}")
print(f"法器描述: {artifact['description']}")

# 获取能力等级说明
level_explanation = power_gen.explain_power_level(3)
print(f"三级能力说明: {level_explanation}")
```

### 3. EventSelector 事件选择器

负责根据角色年龄、属性和状态选择合适的事件，支持按年龄段设置不同权重。

**主要功能**：
- 根据角色年龄筛选事件
- 检查事件条件是否满足
- 基于权重随机选择事件
- 处理事件选项和结果

**使用示例**：
```python
from gameflow.event_selector import EventSelector

# 从模板文件加载事件库
event_selector = EventSelector()
event_selector.load_events_from_file("storyline/templates/event_system.json")

# 角色当前状态
character = {
    "age": 15,
    "cultivation_level": 1,
    "intelligence": 25,
    "strength": 20,
    "status": ["meditation_basics"],
    "items": ["basic_sword"],
    "relationships": {"master": 75}
}

# 选择合适的事件
selected_event = event_selector.select_event(character)

if selected_event:
    print(f"触发事件: {selected_event['name']}")
    print(f"事件描述: {selected_event['description']}")
    
    # 显示事件选项
    for option in selected_event.get("options", []):
        print(f"- {option['option_id']}: {option['text']}")
    
    # 处理选择选项1的结果
    updated_character, result_text, follow_ups = event_selector.process_event_option(
        selected_event, "option_1", character
    )
    
    print(f"结果: {result_text}")
    print(f"后续事件: {follow_ups}")
else:
    print("没有找到合适的事件")
```

## 事件系统结构

`event_system.json` 模板定义了事件的基本结构，包括：

1. **事件基本信息**：ID、名称、描述、类型和标签
2. **年龄权重**：不同年龄段事件的出现权重
3. **触发条件**：属性要求、状态要求、概率等
4. **事件内容**：背景、主要文本、图像提示
5. **选项系统**：多个选择及其对应结果
6. **默认结果**：无选项时的处理

示例事件结构：
```json
{
  "event_id": "first_meditation",
  "name": "初次冥想",
  "description": "年幼时的第一次冥想体验",
  "event_type": "修炼",
  "tags": ["入门", "感悟", "启蒙"],
  
  "age_weights": [
    {"min_age": 5, "max_age": 10, "weight": 1.0},
    {"min_age": 11, "max_age": 15, "weight": 0.5},
    {"min_age": 16, "max_age": 999, "weight": 0.1}
  ],
  
  "conditions": {
    "required_attributes": {
      "cultivation_level": {"min": 0, "max": 1}
    },
    "probability": 0.7
  },
  
  "content": {
    "background": "年幼的你被长辈引导，尝试第一次冥想。",
    "main_text": "在一个宁静的傍晚，{character.mentor_name}教导你盘腿而坐，调整呼吸，尝试感知周围的灵气。"
  },
  
  "options": [
    {
      "option_id": "focus_hard",
      "text": "全神贯注，努力感知",
      "results": {
        "attribute_changes": {
          "cultivation_exp": 10,
          "intelligence": 2
        },
        "status_add": ["meditation_basics"],
        "story_text": "你全神贯注，竭尽全力地试图感知周围的灵气。"
      }
    }
  ]
}
```

## 扩展模块

### 添加新的事件类型

1. 在 `storyline/templates/event_system.json` 中的 `example_events` 数组添加新的事件定义
2. 确保设置合适的年龄权重和触发条件
3. 定义事件的选项和结果

### 扩展能力生成器

1. 如需添加新的能力类型，在 `PowerGenerator.SUPPORTED_TYPES` 中添加新类型
2. 在 `data/text/power_levels.json` 中为每个等级添加新类型的示例
3. 在 `PowerGenerator` 类中添加对应的生成方法

## 注意事项

1. 所有生成功能都依赖于 `storyline` 模块中的模板系统
2. 生成结果会自动保存到角色存档中
3. 事件系统应当与角色年龄推进系统结合使用
4. 所有随机生成功能都支持使用固定种子以确保可重现性 