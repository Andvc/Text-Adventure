# 游戏数据管理模块

data模块提供统一的游戏数据管理功能，包括游戏数据文件的读取、保存和管理。所有数据（包括存档）都通过统一的API进行访问和管理。

## 主要功能

- 数据文件管理
  - 文件路径管理：统一处理不同类型数据文件的路径
  - 数据读取：支持读取各类数据文件
  - 数据保存：支持保存各类数据文件
  - 缓存机制：减少文件I/O操作，提高性能
  - 索引数据：通过索引文件快速访问特定类型的数据
  - 嵌套数据：支持访问嵌套结构的数据

- 数据操作
  - 创建数据：创建新的数据文件或存档
  - 读取数据：读取数据文件或存档内容
  - 更新数据：更新数据文件或存档内容
  - 删除数据：删除数据文件或存档
  - 重命名数据：重命名数据文件或存档
  - 列出数据：获取数据文件或存档列表

## 目录结构

```
data/
├── README.md          # 本文档
├── __init__.py        # 包初始化文件
├── data_manager.py    # 数据管理核心实现
├── text/              # 文本类数据文件
│   ├── items.json     # 物品数据
│   ├── npcs.json      # NPC数据
│   ├── worlds/        # 预设世界观数据
│   │   ├── fantasy_realm.json   # 奇幻大陆世界观
│   │   └── sci_fi_future.json   # 星际纪元世界观
│   └── ...            # 其他文本数据
└── index/             # 数据索引目录
    ├── items_index.json  # 物品索引
    └── ...            # 其他索引文件
```

## 使用说明

### 基本配置

```python
configure_data_system(data_dir=None)
```
配置数据管理系统的基本路径。

**参数**:
- `data_dir`: 数据目录路径，默认为项目根目录下的data文件夹

**示例**:
```python
from data import data_manager
# 使用默认配置
data_manager.configure_data_system()
# 指定自定义目录
data_manager.configure_data_system("/path/to/data")
```

### 数据文件操作

#### 获取文件路径

```python
get_save_path(save_type, save_name)
```
获取保存文件的完整路径。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称

**示例**:
```python
# 获取物品数据文件路径
items_path = data_manager.get_save_path('text', 'items')
# 获取存档文件路径
save_path = data_manager.get_save_path('character', 'test_save')
```

#### 读取数据文件

```python
load_save(save_type, save_name)
```
读取指定的保存文件。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称

**示例**:
```python
# 读取物品数据
items_data = data_manager.load_save('text', 'items')
if items_data:
    for item_id, item_info in items_data.items():
        print(f"{item_id}: {item_info['name']}")

# 读取存档数据
save_data = data_manager.load_save('character', 'test_save')
if save_data:
    print(f"角色名称: {save_data['character']['name']}")
```

#### 保存数据文件

```python
save_data(save_type, save_name, data)
```
保存数据到文件。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称
- `data`: 要保存的数据

**示例**:
```python
# 保存物品数据
items_data = {
    'sword': {
        'name': '铁剑',
        'attack': 5
    }
}
data_manager.save_data('text', 'items', items_data)

# 保存存档数据
save_data = {
    "character": {
        "name": "李逍遥",
        "level": "炼气期"
    }
}
data_manager.save_data('character', 'test_save', save_data)
```

#### 获取特定数据值

```python
get_save_value(save_type, save_name, key, default=None)
```
从保存的数据中获取特定键的值。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称
- `key`: 数据键名
- `default`: 默认值，如果数据不存在则返回此值

**示例**:
```python
# 获取物品数据
sword_attack = data_manager.get_save_value('text', 'items', 'sword.attack', 0)
print(f"剑的攻击力: {sword_attack}")

# 获取存档数据
character_name = data_manager.get_save_value('character', 'test_save', 'character.name')
print(f"角色名称: {character_name}")
```

#### 获取嵌套数据值

```python
get_nested_save_value(save_type, save_name, path, default=None)
```
从保存的数据中获取嵌套路径的值。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称
- `path`: 数据路径，使用点号分隔，如 'layers.layer1.name'
- `default`: 默认值，如果数据不存在则返回此值

**示例**:
```python
# 获取嵌套的物品数据
sword_description = data_manager.get_nested_save_value('text', 'items', 'sword.description')
print(f"剑的描述: {sword_description}")

# 获取嵌套的存档数据
character_level = data_manager.get_nested_save_value('character', 'test_save', 'character.level')
print(f"角色等级: {character_level}")
```

#### 获取索引数据

```python
get_indexed_save(index_file, detail_type)
```
根据索引文件获取指定类型的所有数据。

**参数**:
- `index_file`: 索引文件名（不含扩展名）
- `detail_type`: 数据类型，如 'detail1', 'detail2'

**示例**:
```python
# 获取物品索引数据
items_index = data_manager.get_indexed_save('items_index', 'weapons')
if items_index:
    for item in items_index:
        print(f"武器: {item['name']}, 攻击力: {item['attack']}")
```

### 数据管理工具

#### 创建数据

```python
create_save(save_type, save_name, save_data=None)
```
创建新的保存。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称
- `save_data`: 保存数据，默认为空字典

**示例**:
```python
# 创建存档
save_data = {
    "character": {
        "name": "李逍遥",
        "level": "炼气期"
    }
}
data_manager.create_save("character", "test_save", save_data)
```

#### 更新数据

```python
save_data(save_type, save_name, data)
```
更新保存的数据。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称
- `data`: 新的保存数据

**示例**:
```python
# 更新存档
save_data = data_manager.load_save('character', 'test_save')
save_data['character']['level'] = 2
data_manager.save_data("character", "test_save", save_data)
```

#### 删除数据

```python
delete_save(save_type, save_name)
```
删除保存的数据。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `save_name`: 保存名称

**示例**:
```python
data_manager.delete_save("character", "test_save")
```

#### 重命名数据

```python
rename_save(save_type, old_name, new_name)
```
重命名保存的数据。

**参数**:
- `save_type`: 保存类型，如'text'、'character'等
- `old_name`: 原保存名称
- `new_name`: 新保存名称

**示例**:
```python
data_manager.rename_save("character", "test_save", "new_save")
```

#### 列出数据

```python
list_saves(save_type=None)
```
获取所有保存的列表。

**参数**:
- `save_type`: 保存类型，如果指定则只列出该类型的保存

**示例**:
```python
# 列出所有保存
saves = data_manager.list_saves()
print("所有保存:")
for save in saves:
    print(f"- {save}")

# 只列出角色存档
character_saves = data_manager.list_saves('character')
print("角色存档:")
for save in character_saves:
    print(f"- {save}")
```

#### 清除缓存

```python
clear_cache(save_type=None, save_name=None)
```
清除数据缓存。

**参数**:
- `save_type`: 保存类型，如果指定则只清除该类型的缓存
- `save_name`: 保存名称，如果指定则只清除该保存的缓存

**示例**:
```python
# 清除所有缓存
data_manager.clear_cache()
# 只清除文本类型的缓存
data_manager.clear_cache('text')
# 只清除特定文件的缓存
data_manager.clear_cache('text', 'items')
```

## 文本数据引用系统

### 概述

文本数据引用系统允许在游戏流程中直接访问`data/text`目录下的配置文件，提供了一种统一、灵活的方式来引用游戏中的静态数据，如世界设定、物品数据、NPC信息等。

### 使用方法

在占位符中使用以下格式引用文本数据：

```
{text;file_name;path}
```

其中：
- `text`: 固定前缀，表示这是一个文本数据引用
- `file_name`: 文件名（不含扩展名），对应data/text目录下的JSON文件
- `path`: 数据访问路径，使用点号分隔层级，如'worlds[0].name'

### 示例

#### 1. 引用世界设定

假设`data/text/worlds.json`内容如下：

```json
{
  "worlds": [
    {
      "name": "魔法大陆",
      "era": "魔法纪元",
      "regions": ["北部山脉", "中央平原", "南方沙漠"]
    },
    {
      "name": "科技帝国",
      "era": "蒸汽纪元",
      "regions": ["工业区", "商业中心", "研究基地"]
    }
  ],
  "current_world_index": 0
}
```

可以通过以下方式引用：

```python
# 获取第一个世界的名称
world_name = "{text;worlds;worlds[0].name}"  # 结果: 魔法大陆

# 获取当前世界（使用索引）
current_world_index = "{text;worlds;current_world_index}"  # 结果: 0
current_world = "{text;worlds;worlds[{text;worlds;current_world_index}].name}"  # 结果: 魔法大陆

# 获取地区列表
regions = "{text;worlds;worlds[0].regions}"  # 结果: ['北部山脉', '中央平原', '南方沙漠']
```

#### 2. 引用物品数据

假设`data/text/items.json`内容如下：

```json
{
  "weapons": {
    "sword": {
      "name": "铁剑",
      "damage": 10,
      "value": 100
    },
    "bow": {
      "name": "猎弓",
      "damage": 8,
      "value": 120
    }
  },
  "armors": {
    "leather": {
      "name": "皮甲",
      "defense": 5,
      "value": 80
    }
  }
}
```

可以通过以下方式引用：

```python
# 获取武器名称
sword_name = "{text;items;weapons.sword.name}"  # 结果: 铁剑

# 获取防具防御值
leather_defense = "{text;items;armors.leather.defense}"  # 结果: 5
```

### 嵌套使用

文本数据引用可以与其他占位符格式相结合，实现更复杂的数据访问模式：

```python
# 假设存档中有一个变量指定当前装备
save_data = {
  "current_weapon": "sword"
}

# 使用存档中的变量作为物品索引
weapon_name = "{text;items;weapons.{current_weapon}.name}"  # 结果: 铁剑
```

### 最佳实践

1. **数据组织**：按功能将数据文件分类存放，如`worlds.json`、`items.json`、`npcs.json`等
2. **路径使用**：使用规范的路径格式，避免过于复杂的嵌套
3. **错误处理**：提供默认值或错误提示，处理数据不存在的情况
4. **缓存考虑**：频繁访问的数据考虑使用`get_save_value`预先获取，减少解析开销
5. **版本管理**：更新文本数据时，考虑向下兼容性，避免破坏现有引用

## 变更日志

### 2024-05-21

- **文本数据引用系统**：
  - 添加`{text;file_name;path}`格式的占位符支持，允许从data/text目录下的JSON文件中读取数据
  - 支持嵌套路径访问和数组索引
  - 与嵌套占位符系统集成，支持动态路径和索引
  - 添加错误处理和日志记录
  
- **数组处理改进**：
  - 支持完整数组引用，当索引不存在时返回整个数组
  - 添加变量索引支持，允许使用`{index}`格式动态指定数组索引
  - 优化边界检查，提供更友好的错误信息

- **内部优化**：
  - 改进缓存系统，减少文件IO操作
  - 增强路径解析逻辑，提高性能和稳定性
  - 统一错误处理流程

## 未来计划

以下功能计划在未来版本中实现：

1. **数据校验**：添加数据模式(Schema)验证，确保数据格式正确
2. **版本控制**：支持数据文件的版本记录和兼容性处理
3. **数据编辑工具**：提供GUI工具，方便游戏开发者编辑数据
4. **多语言支持**：支持国际化，按语言加载不同的数据文件
5. **压缩存储**：支持数据压缩，减少磁盘占用和加载时间
6. **数据备份**：自动备份重要数据文件
7. **数据同步**：支持多设备间的数据同步 