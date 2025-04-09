# 角色属性管理模块

角色属性管理模块提供游戏内角色属性的创建、读取、修改和删除功能，支持中文属性名和多种数据类型。

## 功能特点

- 简单易用的API接口
- 支持中文属性名和值
- 支持多种数据类型（字符串、数字、布尔值、列表、字典等）
- 属性分类管理功能（按类别组织和检索属性）
- 自动生成属性名功能（快速创建同类属性）
- 物品属性提取和搜索功能（方便管理复杂物品属性）
- 自定义存储位置
- 自动序列化和反序列化
- 错误处理和日志记录

## 主要功能

### 基本属性操作

- `create_attribute(attr_name, attr_value, attr_category=None)` - 创建新属性，可选指定类别
- `get_attribute(attr_name)` - 获取属性值
- `set_attribute(attr_name, attr_value)` - 修改属性值
- `delete_attribute(attr_name)` - 删除属性

### 属性查询

- `list_attributes()` - 列出所有属性名
- `get_all_attributes()` - 获取所有属性及其值

### 属性类别管理

- `set_attribute_category(attr_name, category)` - 设置属性类别
- `get_attribute_category(attr_name)` - 获取属性类别
- `get_attributes_by_category(category)` - 获取指定类别的所有属性
- `count_attributes_by_category(category)` - 计算指定类别的属性数量
- `get_attribute_by_index(category, index)` - 获取特定类别的第N个属性
- `list_categories()` - 列出所有使用过的类别
- `create_category_attribute(attr_value, category)` - 快速创建某类别的新属性（自动生成属性名）

### 物品属性管理（适用于字典存储多个特定属性值的物品）
如：
# 创建带多属性的物品
create_attribute("龙鳞胸甲", {
    "类型": "防具",
    "防御力": 20,
    "品质": "稀有",
    "描述": "由龙鳞制成的胸甲",
    "需求等级": 10
}, "背包物品")

- `get_item_property(item_name, property_name, default=None)` - 提取物品的特定属性值
- `search_items_by_property(category, property_name, property_value)` - 搜索具有特定属性值的物品
- 支持直接修改物品内部属性：获取物品数据 -> 修改属性 -> 保存回系统

### 存储配置

- `configure_save_system(save_dir=None, save_file=None)` - 配置存储位置
- `get_save_location()` - 获取当前存档位置

## 使用示例

```python
# 导入模块
from character.character_manager import *

# 创建基本属性（带类别）
create_attribute("姓名", "李逍遥", "基础属性")
create_attribute("等级", 1, "基础属性")
create_attribute("生命值", 100, "基础属性")

# 创建战斗属性
create_attribute("攻击力", 15, "战斗属性")
create_attribute("防御力", 10, "战斗属性")

# 创建装备
create_attribute("武器", {"名称": "青锋剑", "攻击": 10}, "装备")

# 快速创建多个状态效果（自动生成属性名）
buff1 = create_category_attribute(
    {"持续时间": 3, "效果": "每回合恢复5点生命值"}, 
    "状态效果"
)
buff2 = create_category_attribute(
    {"持续时间": 2, "效果": "攻击力+10"}, 
    "状态效果"
)

# 获取属性及其类别
print(f"角色名称: {get_attribute('姓名')}")
print(f"'攻击力'的类别: {get_attribute_category('攻击力')}")

# 获取所有基础属性
basic_attrs = get_attributes_by_category("基础属性")
print(f"基础属性列表: {basic_attrs}")

# 获取所有状态效果
status_count = count_attributes_by_category("状态效果")
print(f"状态效果数量: {status_count}")

for i in range(status_count):
    effect_name, effect_data = get_attribute_by_index("状态效果", i)
    print(f"状态效果 {i+1}: {effect_data}")

# 创建带多属性的物品
create_attribute("龙鳞胸甲", {
    "类型": "防具",
    "防御力": 20,
    "品质": "稀有",
    "描述": "由龙鳞制成的胸甲",
    "需求等级": 10
}, "背包物品")

# 提取物品特定属性
armor_quality = get_item_property("龙鳞胸甲", "品质")  # 返回 "稀有"
armor_defense = get_item_property("龙鳞胸甲", "防御力")  # 返回 20

# 搜索特定品质的物品
rare_items = search_items_by_property("背包物品", "品质", "稀有")

# 修改物品内部属性
# 1. 获取物品完整数据
item_data = get_attribute("龙鳞胸甲")
# 2. 修改特定属性
item_data["防御力"] += 5  # 增加防御力
# 3. 保存修改后的数据
set_attribute("龙鳞胸甲", item_data)
```

## 数据存储

属性数据默认存储在`save/temp_save.json`文件中，可以通过`configure_save_system`函数自定义存储位置。

存储格式示例：

```json
{
    "角色数据": {
        "姓名": "李逍遥",
        "等级": 1,
        "生命值": 100,
        "攻击力": 15,
        "武器": {
            "名称": "青锋剑",
            "攻击": 10
        },
        "状态效果_1_1634567890": {
            "持续时间": 3,
            "效果": "每回合恢复5点生命值"
        },
        "龙鳞胸甲": {
            "类型": "防具",
            "防御力": 20,
            "品质": "稀有",
            "描述": "由龙鳞制成的胸甲",
            "需求等级": 10
        }
    },
    "属性类别": {
        "姓名": "基础属性",
        "等级": "基础属性",
        "生命值": "基础属性",
        "攻击力": "战斗属性",
        "武器": "装备",
        "状态效果_1_1634567890": "状态效果",
        "龙鳞胸甲": "背包物品"
    }
}
```

## 详细文档

更详细的使用指南，请参考[用户指南](./user_guide.md)。 