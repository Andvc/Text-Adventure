# 游戏数据管理模块

data模块提供游戏固定数据的读取和管理功能，用于存储和访问游戏的静态数据如物品信息、NPC数据、对话内容等。

## 主要功能

- 数据文件管理：读取、保存各类游戏数据文件
- 类型分离：按数据类型（文本、图像等）组织数据
- 缓存机制：减少文件I/O操作，提高性能
- 集中式访问：统一的API访问不同类型的数据

## 目录结构

```
data/
├── README.md          # 本文档
├── __init__.py        # 包初始化文件
├── data_manager.py    # 数据管理核心实现
└── text/              # 文本类数据文件
    ├── items.json     # 物品数据
    ├── npcs.json      # NPC数据
    ├── worlds/        # 预设世界观数据
    │   ├── fantasy_realm.json   # 奇幻大陆世界观
    │   └── sci_fi_future.json   # 星际纪元世界观
    └── ...            # 其他文本数据
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

### 读取数据

#### 读取整个数据文件

```python
read_data_file(data_type, file_name)
```
读取指定的数据文件。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）

**示例**:
```python
# 读取物品数据
items_data = data_manager.read_data_file('text', 'items')
if items_data:
    for item_id, item_info in items_data.items():
        print(f"{item_id}: {item_info['name']}")
```

#### 获取特定数据值

```python
get_data_value(data_type, file_name, key, default=None)
```
从数据文件中获取特定键的值。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）
- `key`: 数据键名
- `default`: 默认值，如果数据不存在则返回此值

**示例**:
```python
# 获取特定物品的信息
sword_data = data_manager.get_data_value('text', 'items', 'sword', {})
print(f"剑的攻击力: {sword_data.get('attack', 0)}")
```

### 保存数据

```python
save_data_file(data_type, file_name, data)
```
保存数据到文件。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）
- `data`: 要保存的数据

**示例**:
```python
# 创建或更新物品数据
items_data = {
    'sword': {
        'name': '铁剑',
        'description': '普通的铁剑，攻击力不高。',
        'attack': 5,
        'value': 100
    },
    'shield': {
        'name': '木盾',
        'description': '简单的木盾，可以抵挡少量伤害。',
        'defense': 3,
        'value': 50
    }
}
data_manager.save_data_file('text', 'items', items_data)
```

### 其他工具函数

#### 获取数据文件路径

```python
get_data_file_path(data_type, file_name)
```
获取数据文件的完整路径。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）

**示例**:
```python
path = data_manager.get_data_file_path('text', 'items')
print(f"物品数据文件路径: {path}")
```

#### 清除缓存

```python
clear_cache(data_type=None, file_name=None)
```
清除数据缓存。

**参数**:
- `data_type`: 数据类型，如果指定则只清除该类型的缓存
- `file_name`: 文件名，如果指定则只清除该文件的缓存

**示例**:
```python
# 清除所有缓存
data_manager.clear_cache()
# 只清除文本类型的缓存
data_manager.clear_cache('text')
# 只清除物品数据缓存
data_manager.clear_cache('text', 'items')
```

## 在character_manager中的使用

character_manager模块提供了两个辅助函数，用于方便地访问游戏数据：

```python
get_data(data_type, file_name, key, default=None)
```
从游戏数据文件中读取特定键的值。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）
- `key`: 数据键名
- `default`: 默认值，如果数据不存在则返回此值

```python
read_data_file(data_type, file_name)
```
读取整个游戏数据文件。

**参数**:
- `data_type`: 数据类型，如'text'、'images'等
- `file_name`: 文件名（不含扩展名）

**示例**:
```python
from character import character_manager

# 获取所有NPC数据
npcs = character_manager.read_data_file('text', 'npcs')

# 获取特定NPC的数据
merchant = character_manager.get_data('text', 'npcs', 'merchant')
```

## 与存档系统的区别

数据管理系统与存档系统的主要区别：

1. **用途不同**：
   - 数据系统：存储游戏固定数据（物品、NPC、对话等）
   - 存档系统：存储玩家进度和角色状态

2. **更新频率不同**：
   - 数据系统：通常只在游戏开发或内容更新时修改
   - 存档系统：随着玩家游戏进程不断变化

3. **存储位置不同**：
   - 数据系统：位于游戏安装目录中，所有玩家共享相同数据
   - 存档系统：通常位于用户目录，针对每个玩家单独存储

## 未来计划

以下功能计划在未来版本中实现：

1. **数据校验**：添加数据模式(Schema)验证，确保数据格式正确
2. **版本控制**：支持数据文件的版本记录和兼容性处理
3. **数据编辑工具**：提供GUI工具，方便游戏开发者编辑数据
4. **多语言支持**：支持国际化，按语言加载不同的数据文件
5. **压缩存储**：支持数据压缩，减少磁盘占用和加载时间 