# 角色属性管理模块

角色属性管理模块提供游戏内角色属性的创建、读取、修改和删除功能，支持中文属性名和多种数据类型。

## 目录

- [功能特点](#功能特点)
- [存储系统和配置](#存储系统和配置)
- [基本属性操作](#基本属性操作)
- [属性类别管理](#属性类别管理)
- [物品属性管理](#物品属性管理)
- [多存档支持](#多存档支持)
- [使用示例](#使用示例)
- [数据存储](#数据存储)
- [模块关系](#模块关系)

## 功能特点

- 简单易用的API接口
- 支持中文属性名和值
- 支持多种数据类型（字符串、数字、布尔值、列表、字典等）
- 属性分类管理功能（按类别组织和检索属性）
- 自动生成属性名功能（快速创建同类属性）
- 物品属性提取和搜索功能（方便管理复杂物品属性）
- 多存档管理功能（创建、加载、删除、重命名存档）
- 自定义存储位置
- 自动序列化和反序列化
- 错误处理和日志记录

## 存储系统和配置

角色属性管理模块使用JSON文件存储数据，包含以下配置功能：

### 配置存档系统

```python
configure_save_system(save_dir=None, save_file=None)
```

配置属性数据的存储位置。

- **参数**:
  - `save_dir`: 存档目录路径，默认为项目根目录下的`save`文件夹
  - `save_file`: 存档文件名称，默认为`character_data.json`
- **返回值**:
  - 配置好的存档管理器实例

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

## 基本属性操作

### 创建属性

```python
create_attribute(attr_name, attr_value, attr_category=None)
```

创建一个新的角色属性，可以同时指定属性类别。

- **参数**:
  - `attr_name`: 属性名称
  - `attr_value`: 属性值，可以是任何类型（字符串、数字、布尔值、列表、字典等）
  - `attr_category`: (可选) 属性类别，默认为None
- **返回值**:
  - 创建成功返回`True`
  - 如果属性已存在，返回`False`
- **行为**:
  - 检查属性是否已存在
  - 存储属性值到"attributes"
  - 如果提供了类别，存储到"attribute_categories"
  - 保存变更到文件

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
- **返回值**:
  - 设置成功返回`True`
  - 失败返回`False`
- **行为**:
  - 更新"attributes"中对应属性的值
  - 保存变更到文件

- **示例**:
  ```python
  set_attribute("等级", 2)  # 将等级从1修改为2
  set_attribute("经验值", 100)  # 如果"经验值"不存在，则创建该属性
  ```

### 删除属性

```python
delete_attribute(attr_name)
```

删除指定的属性及其类别信息。

- **参数**:
  - `attr_name`: 属性名称
- **返回值**:
  - 删除成功返回`True`
  - 如果属性不存在，返回`False`
- **行为**:
  - 检查属性是否存在
  - 从"attributes"删除属性
  - 从"attribute_categories"删除对应的类别信息
  - 保存变更到文件

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
- **返回值**:
  - 设置成功返回`True`
  - 失败返回`False`
- **行为**:
  - 检查属性是否存在
  - 更新"attribute_categories"中对应属性的类别
  - 保存变更到文件

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
- **行为**:
  - 遍历"attribute_categories"，找出所有属于该类别的属性

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
  - 成功时返回元组 `(属性名, 属性值)`
  - 如果索引越界或类别不存在，返回 `(None, None)`
- **行为**:
  - 获取该类别的所有属性
  - 检查索引是否有效
  - 获取对应索引的属性名和值

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
- **行为**:
  - 从"attribute_categories"中提取所有唯一的类别值

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
- **行为**:
  - 确保类别名称非空
  - 生成唯一的属性名（格式：类别_数量_时间戳）
  - 创建属性并设置类别

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

## 物品属性管理

以下功能特别适用于使用字典存储的复杂物品（装备、道具等），方便对其内部属性进行操作。

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
- **行为**:
  - 获取物品数据
  - 检查物品是否存在且为字典类型
  - 从字典中提取指定的特性值

- **示例**:
  ```python
  # 提取物品特性
  quality = get_item_property("青锋剑", "品质")  # 返回 "稀有"
  attack = get_item_property("青锋剑", "攻击力")  # 返回 10
  durability = get_item_property("青锋剑", "耐久度", 100)  # 返回默认值 100
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
- **行为**:
  - 获取指定类别的所有物品
  - 遍历物品，检查是否具有指定特性值
  - 返回所有匹配的物品名称

- **示例**:
  ```python
  # 搜索所有稀有品质的物品
  rare_items = search_items_by_property("背包物品", "品质", "稀有")
  
  # 搜索所有武器类型的物品
  weapons = search_items_by_property("背包物品", "类型", "武器")
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

## 多存档支持

模块提供了多存档管理功能，可以创建、加载、删除和重命名存档。

### 列出存档

```python
list_saves()
```

获取所有可用的存档列表。

- **返回值**:
  - 所有存档名称的列表

- **示例**:
  ```python
  saves = list_saves()
  print(f"可用存档: {saves}")
  ```

### 创建新存档

```python
create_save(save_name, character_name="", description="")
```

创建一个新的存档。

- **参数**:
  - `save_name`: 存档名称
  - `character_name`: 角色名称
  - `description`: 存档描述
- **返回值**:
  - 创建成功返回`True`
  - 失败返回`False`

- **示例**:
  ```python
  create_save("勇者的旅程", "李逍遥", "初始冒险存档")
  ```

### 加载存档

```python
load_save(save_name)
```

加载指定名称的存档。

- **参数**:
  - `save_name`: 存档名称
- **返回值**:
  - 加载成功返回`True`
  - 失败返回`False`

- **示例**:
  ```python
  load_save("勇者的旅程")
  ```

### 删除存档

```python
delete_save(save_name)
```

删除指定名称的存档。

- **参数**:
  - `save_name`: 存档名称
- **返回值**:
  - 删除成功返回`True`
  - 失败返回`False`

- **示例**:
  ```python
  delete_save("旧存档")
  ```

### 重命名存档

```python
rename_save(old_name, new_name)
```

重命名存档。

- **参数**:
  - `old_name`: 原存档名称
  - `new_name`: 新存档名称
- **返回值**:
  - 重命名成功返回`True`
  - 失败返回`False`

- **示例**:
  ```python
  rename_save("旧名称", "新名称")
  ```

### 获取当前存档名称

```python
get_current_save_name()
```

获取当前加载的存档名称。

- **返回值**:
  - 当前存档名称

- **示例**:
  ```python
  name = get_current_save_name()
  print(f"当前存档: {name}")
  ```

### 获取存档元数据

```python
get_save_metadata()
```

获取当前存档的元数据。

- **返回值**:
  - 存档元数据字典

- **示例**:
  ```python
  metadata = get_save_metadata()
  print(f"存档创建时间: {metadata['created_at']}")
  ```

### 更新存档元数据

```python
update_save_metadata(key, value)
```

更新存档元数据的特定字段。

- **参数**:
  - `key`: 元数据字段名
  - `value`: 新的字段值
- **返回值**:
  - 更新成功返回`True`
  - 失败返回`False`

- **示例**:
  ```python
  update_save_metadata("character_name", "新名称")
  ```

### 从指定存档读取属性

```python
get_attribute_from_save(save_name, attr_name, default=None)
```

从指定存档中读取属性值，不改变当前活动存档。这对于需要在不切换当前存档的情况下访问其他存档数据非常有用。

- **参数**:
  - `save_name`: 要读取的存档名称
  - `attr_name`: 要读取的属性名称
  - `default`: (可选) 如果属性不存在时返回的默认值
- **返回值**:
  - 属性值，如不存在则返回默认值

- **示例**:
  ```python
  # 当前活动存档是"角色1"，但想读取"角色2"的某个属性
  level = get_attribute_from_save("角色2", "等级", 0)  # 读取角色2的等级，默认值为0
  print(f"角色2的等级是: {level}")
  
  # 不会改变当前活动存档，后续操作仍在"角色1"存档上进行
  current_name = get_attribute("姓名")  # 返回角色1的姓名
  ```

## 使用示例

### 基本用法

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
```

### 物品管理

```python
# 创建背包物品
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

### 多存档管理

```python
# 创建新存档
create_save("主角", "李逍遥", "主线任务存档")
create_save("支线", "李逍遥", "支线任务存档")

# 列出所有存档
saves = list_saves()
print(f"可用存档: {saves}")

# 在主角存档中添加属性
create_attribute("任务", "拯救世界", "主线")

# 切换到支线存档
load_save("支线")

# 在支线存档中添加属性
create_attribute("任务", "寻找宝藏", "支线")

# 切换回主角存档
load_save("主角")

# 验证任务属性
print(f"当前任务: {get_attribute('任务')}")  # 应该是"拯救世界"

# 重命名存档
rename_save("支线", "支线任务")

# 列出所有存档
saves = list_saves()
print(f"可用存档: {saves}")  # 显示["主角", "支线任务"]
```

### 状态效果管理

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

## 数据存储

属性数据默认存储在`save/characters/default.json`文件中，可以通过`configure_save_system`函数自定义存储位置。

存储格式示例：

```json
{
    "metadata": {
        "version": "1.0",
        "created_at": 1634567890.123,
        "last_modified": 1634567890.456,
        "character_name": "李逍遥",
        "save_name": "default",
        "description": ""
    },
    "attributes": {
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
    "attribute_categories": {
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

## 模块关系

`character_manager`和`save_manager`模块之间存在以下关系：

### 架构设计

`character_manager`是一个高级接口，提供友好易用的角色属性管理功能，而`save_manager`则是底层的存储引擎，负责数据持久化和文件操作。

- **save_manager**: 提供存档的创建、读取、修改、删除等基础功能，不关心数据具体内容和结构
- **character_manager**: 依赖save_manager来存储数据，提供特定于角色属性的业务逻辑和操作

### 调用机制

character_manager中的大多数函数实际上是对save_manager功能的封装和扩展：

1. **直接转发模式**：多存档管理函数（如`list_saves`、`create_save`等）直接转发给save_manager的同名函数
2. **封装模式**：属性操作函数先从save_manager获取数据，进行处理后再通过save_manager保存
3. **扩展模式**：提供save_manager没有的高级功能，如属性分类、物品属性管理等

### 优势

这种设计有以下优势：

1. **关注点分离**：save_manager专注于存储，character_manager专注于业务逻辑
2. **代码复用**：其他模块可以直接使用save_manager提供的存储功能
3. **灵活性**：可以独立更改存储实现而不影响上层业务逻辑
4. **易于维护**：每个模块职责明确，更容易调试和维护

### 跨存档操作

`get_attribute_from_save`功能利用save_manager的`read_save_data`函数，允许在不改变当前活动存档的情况下，读取其他存档的属性。这对于需要比较不同存档数据、从模板存档读取信息或实现游戏内的存档间交互非常有用。

## 游戏数据访问

除了存档系统，角色属性管理模块现在还提供了访问游戏固定数据的功能。这些数据存储在`data`目录下，与玩家存档分离。

### 数据与存档的区别

- **存档数据**：存储玩家游戏进度和角色状态，随游戏进行不断变化
- **游戏数据**：存储游戏内置的固定内容，如物品模板、NPC信息、对话等

### 数据访问函数

```python
get_data(data_type, file_name, key, default=None)
```

从游戏数据文件中读取特定键的值。

- **参数**:
  - `data_type`: 数据类型，如'text'、'images'等
  - `file_name`: 文件名（不含扩展名）
  - `key`: 数据键名
  - `default`: (可选) 默认值，如果数据不存在时返回的默认值
- **返回值**:
  - 数据值，如不存在则返回默认值

- **示例**:
  ```python
  # 获取物品模板数据
  sword_template = get_data('text', 'items', 'sword', {})
  print(f"剑的基础攻击力: {sword_template.get('base_attack', 0)}")
  
  # 获取NPC对话
  merchant_dialogue = get_data('text', 'dialogues', 'merchant_greeting', "欢迎光临！")
  ```

```python
read_data_file(data_type, file_name)
```

读取整个游戏数据文件。

- **参数**:
  - `data_type`: 数据类型，如'text'、'images'等
  - `file_name`: 文件名（不含扩展名）
- **返回值**:
  - 包含整个数据文件内容的字典，读取失败则返回None

- **示例**:
  ```python
  # 读取所有物品模板
  all_items = read_data_file('text', 'items')
  if all_items:
      for item_id, item_data in all_items.items():
          print(f"物品: {item_data['name']}")
          
  # 读取所有对话数据
  all_dialogues = read_data_file('text', 'dialogues')
  ```

### 应用场景

1. **物品系统**：从data中读取物品模板，创建角色实际拥有的物品
2. **NPC交互**：从data中读取NPC信息和对话内容
3. **任务系统**：从data中读取任务模板和奖励信息
4. **游戏设置**：从data中读取游戏配置和平衡参数

### 与data_manager的关系

character_manager模块提供的数据访问函数是对data_manager模块功能的封装，便于在角色属性管理的上下文中使用。完整的数据管理功能请参见data模块的文档。 