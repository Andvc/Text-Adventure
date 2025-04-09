# 角色属性管理模块使用指南

本指南介绍如何使用角色属性管理模块来创建、读取、修改和删除角色属性。

## 基本功能

角色属性管理模块提供以下基本功能：

### 创建属性

```python
create_attribute(attr_name, attr_value, attr_category=None)
```

创建一个新的角色属性。

- **参数**:
  - `attr_name`: 属性名称
  - `attr_value`: 属性值，可以是任何类型（字符串、数字、布尔值、列表、字典等）
  - `attr_category`: (可选) 属性类别，默认为None

- **示例**:
  ```python
  create_attribute("姓名", "李逍遥")
  create_attribute("等级", 1)
  create_attribute("攻击力", 15, "战斗属性")  # 创建带类别的属性
  ```

### 获取属性

```python
get_attribute(attr_name)
```

获取指定属性的值。

- **参数**:
  - `attr_name`: 属性名称

- **返回值**:
  - 如果属性存在，返回属性值
  - 如果属性不存在，返回`None`

- **示例**:
  ```python
  name = get_attribute("姓名")  # 返回 "李逍遥"
  level = get_attribute("等级")  # 返回 1
  ```

### 修改属性

```python
set_attribute(attr_name, attr_value)
```

修改指定属性的值。如果属性不存在，则会创建该属性。

- **参数**:
  - `attr_name`: 属性名称
  - `attr_value`: 新的属性值

- **示例**:
  ```python
  set_attribute("等级", 2)  # 将等级从1修改为2
  set_attribute("经验值", 100)  # 如果"经验值"不存在，则创建该属性
  ```

### 删除属性

```python
delete_attribute(attr_name)
```

删除指定的属性。

- **参数**:
  - `attr_name`: 属性名称

- **返回值**:
  - 删除成功返回`True`
  - 如果属性不存在，返回`False`

- **示例**:
  ```python
  delete_attribute("临时属性")  # 删除"临时属性"
  ```

### 列出所有属性

```python
list_attributes()
```

获取所有已定义的属性名称列表。

- **返回值**:
  - 包含所有属性名称的列表

- **示例**:
  ```python
  all_attrs = list_attributes()  # 返回 ["姓名", "等级", "经验值", ...]
  ```

### 获取所有属性及其值

```python
get_all_attributes()
```

获取所有属性及其对应的值。

- **返回值**:
  - 包含所有属性及其值的字典

- **示例**:
  ```python
  all_data = get_all_attributes()  # 返回 {"姓名": "李逍遥", "等级": 2, ...}
  ```

## 属性类别管理

属性类别功能允许您对属性进行分类管理，例如将属性分为"基础属性"、"战斗属性"、"装备"、"状态效果"等类别。

### 设置属性类别

```python
set_attribute_category(attr_name, category)
```

为指定属性设置类别。

- **参数**:
  - `attr_name`: 属性名称
  - `category`: 类别名称，如"基础属性"、"战斗属性"等

- **示例**:
  ```python
  set_attribute_category("攻击力", "战斗属性")
  set_attribute_category("防御力", "战斗属性")
  set_attribute_category("武器", "装备")
  ```

### 获取属性类别

```python
get_attribute_category(attr_name)
```

获取指定属性的类别。

- **参数**:
  - `attr_name`: 属性名称

- **返回值**:
  - 属性的类别名称，如果属性不存在或没有类别，返回`None`

- **示例**:
  ```python
  category = get_attribute_category("攻击力")  # 返回 "战斗属性"
  ```

### 获取指定类别的所有属性

```python
get_attributes_by_category(category)
```

获取指定类别下的所有属性名称。

- **参数**:
  - `category`: 类别名称

- **返回值**:
  - 该类别下所有属性名称的列表

- **示例**:
  ```python
  combat_attrs = get_attributes_by_category("战斗属性")  # 返回 ["攻击力", "防御力", ...]
  ```

### 计算指定类别的属性数量

```python
count_attributes_by_category(category)
```

计算指定类别下的属性数量。

- **参数**:
  - `category`: 类别名称

- **返回值**:
  - 该类别下的属性数量

- **示例**:
  ```python
  count = count_attributes_by_category("装备")  # 返回装备类别的属性数量
  ```

### 获取指定类别的第N个属性

```python
get_attribute_by_index(category, index)
```

获取指定类别下的第N个属性及其值。

- **参数**:
  - `category`: 类别名称
  - `index`: 索引值（从0开始）

- **返回值**:
  - 一个元组 `(属性名, 属性值)`
  - 如果索引越界或类别不存在，返回 `(None, None)`

- **示例**:
  ```python
  first_equipment = get_attribute_by_index("装备", 0)  # 返回装备类别的第一个属性
  ```

### 列出所有属性类别

```python
list_categories()
```

获取所有已使用过的属性类别。

- **返回值**:
  - 所有类别名称的列表

- **示例**:
  ```python
  categories = list_categories()  # 返回 ["基础属性", "战斗属性", "装备", ...]
  ```

### 快速创建类别属性

```python
create_category_attribute(attr_value, category)
```

快速创建一个属于指定类别的新属性，自动生成属性名称。

- **参数**:
  - `attr_value`: 属性值，可以是任何类型（字符串、数字、布尔值、列表、字典等）
  - `category`: 类别名称

- **返回值**:
  - 成功时返回自动生成的属性名
  - 失败时返回`None`

- **示例**:
  ```python
  # 创建一个新的生命值属性
  hp_attr = create_category_attribute(100, "生命值")
  print(hp_attr)  # 输出类似 "生命值_1_1634567890"
  
  # 创建一个状态效果
  buff_attr = create_category_attribute(
      {"持续时间": 3, "效果": "每回合恢复5点生命值"}, 
      "增益效果"
  )
  ```

- **说明**:
  - 自动生成的属性名格式为：`类别_计数_时间戳`
  - 这允许您快速创建多个同类属性而无需手动命名
  - 自动生成的名称确保唯一性
  - 适用于需要动态创建多个同类属性的场景，如状态效果、物品等

## 复杂物品属性管理

以下功能特别适用于使用字典存储的复杂物品（装备、道具等），方便对其内部属性进行操作。

### 创建复杂物品

复杂物品通常使用字典结构，包含多个特性：

```python
# 创建一个武器物品
create_attribute("青锋剑", {
    "类型": "武器",
    "攻击力": 10,
    "品质": "稀有",
    "描述": "一把锋利的长剑",
    "需求等级": 5
}, "背包物品")

# 创建一个消耗品
create_attribute("治疗药水", {
    "类型": "消耗品",
    "效果": "恢复50点生命值",
    "品质": "普通",
    "数量": 5
}, "背包物品")
```

### 提取物品特定属性

```python
get_item_property(item_name, property_name, default=None)
```

提取物品的特定属性值，适用于使用字典存储多个特性的物品。

- **参数**:
  - `item_name`: 物品属性名
  - `property_name`: 要提取的特性名称，如"品质"、"攻击力"等
  - `default`: (可选) 如果物品或特性不存在时返回的默认值

- **返回值**:
  - 如果物品存在且具有该特性，返回特性值
  - 如果物品不存在或没有该特性，返回默认值

- **示例**:
  ```python
  # 提取物品特性
  quality = get_item_property("青锋剑", "品质")  # 返回 "稀有"
  attack = get_item_property("青锋剑", "攻击力")  # 返回 10
  durability = get_item_property("青锋剑", "耐久度", 100)  # 返回默认值 100
  ```

### 修改物品特定属性

可以通过获取物品完整数据、修改特定属性、然后保存回去的方式修改物品的特定属性：

```python
# 获取物品完整数据
potion_data = get_attribute("治疗药水")

# 修改特定属性
potion_data["数量"] -= 1  # 减少药水数量

# 保存修改后的数据
set_attribute("治疗药水", potion_data)
```

**工作原理**:
- `get_attribute()` 返回字典的引用，可以直接修改其内部属性
- 修改后需要使用 `set_attribute()` 保存回属性系统
- 这种模式适合需要执行多个修改或复杂操作的场景

**示例**:
```python
# 使用物品并检查是否用完
def use_potion(potion_name):
    # 获取完整的物品数据
    potion = get_attribute(potion_name)
    
    if not potion or not isinstance(potion, dict):
        print(f"{potion_name} 不存在或不是有效的物品")
        return False
    
    # 检查数量
    if "数量" not in potion or potion["数量"] <= 0:
        print(f"{potion_name} 数量不足")
        return False
    
    # 使用物品（减少数量）
    potion["数量"] -= 1
    
    # 应用物品效果
    effect = potion.get("效果", "无效果")
    print(f"使用 {potion_name}，效果: {effect}")
    
    # 保存更新后的物品数据
    set_attribute(potion_name, potion)
    
    # 检查是否用完，如果用完则删除
    if potion["数量"] <= 0:
        delete_attribute(potion_name)
        print(f"{potion_name} 已用完")
    else:
        print(f"{potion_name} 剩余数量: {potion['数量']}")
    
    return True
```

### 搜索特定特性的物品

```python
search_items_by_property(category, property_name, property_value)
```

在指定类别中搜索具有特定特性值的物品。

- **参数**:
  - `category`: 物品类别，如"背包物品"、"装备"等
  - `property_name`: 特性名称，如"品质"、"类型"等
  - `property_value`: 要搜索的特性值

- **返回值**:
  - 匹配条件的物品名称列表

- **示例**:
  ```python
  # 搜索所有稀有品质的物品
  rare_items = search_items_by_property("背包物品", "品质", "稀有")
  
  # 搜索所有武器类型的物品
  weapons = search_items_by_property("背包物品", "类型", "武器")
  ```

### 高级搜索和过滤示例

可以结合Python的列表推导式进行更复杂的物品搜索和过滤：

```python
# 搜索所有需求等级小于5的物品
low_level_items = [
    item_name for item_name in get_attributes_by_category("背包物品")
    if get_item_property(item_name, "需求等级", 999) < 5
]

# 搜索攻击力大于5的武器
strong_weapons = [
    item_name for item_name in search_items_by_property("背包物品", "类型", "武器")
    if get_item_property(item_name, "攻击力", 0) > 5
]

# 查找数量低于2的消耗品（需要补充）
low_stock_consumables = [
    item_name for item_name in search_items_by_property("背包物品", "类型", "消耗品")
    if get_item_property(item_name, "数量", 0) < 2
]
```

## 存储位置配置

### 配置存档系统

```python
configure_save_system(save_dir=None, save_file=None)
```

配置属性数据的存储位置。

- **参数**:
  - `save_dir`: 存档目录路径，默认为项目根目录下的`save`文件夹
  - `save_file`: 存档文件名称，默认为`temp_save.json`

- **示例**:
  ```python
  # 使用默认位置
  configure_save_system()
  
  # 指定自定义存档文件
  configure_save_system(save_file="my_character.json")
  
  # 完全自定义存储位置
  configure_save_system("/path/to/saves", "character.json")
  ```

### 获取当前存档位置

```python
get_save_location()
```

获取当前使用的存档文件的完整路径。

- **返回值**:
  - 存档文件的完整路径

- **示例**:
  ```python
  location = get_save_location()  # 返回类似 "/path/to/save/my_character.json" 的路径
  ```

## 实际应用示例

### 创建角色基本属性与分类

```python
# 配置存档文件
configure_save_system(save_file="my_character.json")

# 创建基础属性
create_attribute("姓名", "李逍遥", "基础属性")
create_attribute("等级", 1, "基础属性")
create_attribute("生命值", 100, "基础属性")
create_attribute("魔法值", 80, "基础属性")

# 创建战斗属性
create_attribute("攻击力", 15, "战斗属性")
create_attribute("防御力", 10, "战斗属性")
create_attribute("暴击率", 0.05, "战斗属性")

# 创建装备
create_attribute("武器", {"名称": "青锋剑", "攻击": 10}, "装备")
create_attribute("防具", {"名称": "布衣", "防御": 5}, "装备")

# 查看基础属性
basic_attrs = get_attributes_by_category("基础属性")
print(f"基础属性: {basic_attrs}")

# 获取并使用装备信息
weapon_name = get_attribute("武器")["名称"]
weapon_attack = get_attribute("武器")["攻击"]
print(f"武器: {weapon_name}, 攻击力: {weapon_attack}")
```

### 管理状态效果

```python
# 创建状态效果
create_attribute("中毒", {"持续时间": 3, "每回合伤害": 5}, "状态效果")
create_attribute("加速", {"持续时间": 2, "敏捷提升": 5}, "状态效果")

# 获取所有状态效果
status_effects = get_attributes_by_category("状态效果")
print(f"当前状态效果: {status_effects}")

# 处理状态效果
for i in range(count_attributes_by_category("状态效果")):
    effect_name, effect_data = get_attribute_by_index("状态效果", i)
    if effect_name and effect_data:
        print(f"处理状态效果: {effect_name}, 持续时间: {effect_data['持续时间']}")
        
        # 减少持续时间
        effect_data['持续时间'] -= 1
        
        # 更新或移除状态效果
        if effect_data['持续时间'] <= 0:
            print(f"状态效果 {effect_name} 已结束")
            delete_attribute(effect_name)
        else:
            set_attribute(effect_name, effect_data)
```

### 物品管理系统示例

```python
# 创建背包物品
create_attribute("青锋剑", {
    "类型": "武器",
    "攻击力": 10,
    "品质": "稀有",
    "描述": "一把锋利的长剑",
    "需求等级": 5
}, "背包物品")

create_attribute("治疗药水", {
    "类型": "消耗品",
    "效果": "恢复50点生命值",
    "品质": "普通",
    "数量": 5
}, "背包物品")

# 定义使用物品的函数
def use_item(item_name):
    item = get_attribute(item_name)
    
    if not item or not isinstance(item, dict):
        print(f"{item_name} 不存在或不是有效物品")
        return False
    
    item_type = item.get("类型")
    
    if item_type == "消耗品":
        # 使用消耗品
        if "数量" not in item or item["数量"] <= 0:
            print(f"{item_name} 数量不足")
            return False
        
        # 应用效果
        print(f"使用 {item_name}，效果: {item.get('效果', '无效果')}")
        
        # 减少数量
        item["数量"] -= 1
        
        # 保存更新
        if item["数量"] <= 0:
            delete_attribute(item_name)
            print(f"{item_name} 已用完")
        else:
            set_attribute(item_name, item)
            print(f"{item_name} 剩余数量: {item['数量']}")
        
        return True
    
    elif item_type == "武器" or item_type == "防具":
        # 装备物品
        print(f"装备 {item_name}，品质: {item.get('品质', '普通')}")
        # 这里可以添加装备逻辑...
        return True
    
    else:
        print(f"无法使用 {item_name}，未知物品类型")
        return False

# 物品使用示例
use_item("治疗药水")  # 使用一次药水
use_item("治疗药水")  # 再次使用
use_item("青锋剑")    # 装备武器

# 物品筛选示例
rare_items = search_items_by_property("背包物品", "品质", "稀有")
print(f"稀有物品: {rare_items}")

# 高级筛选 - 低于特定等级的武器
low_level_weapons = [
    item for item in search_items_by_property("背包物品", "类型", "武器")
    if get_item_property(item, "需求等级", 999) < 10
]
print(f"低等级武器: {low_level_weapons}")
``` 