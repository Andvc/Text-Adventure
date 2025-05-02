# 存档系统模块

save模块提供游戏存档的创建、读取、修改和删除功能，支持多存档管理和元数据存储。

## 主要功能

- 多存档管理：创建、加载、删除、重命名存档
- 元数据支持：记录存档的创建时间、修改时间、角色名称等信息
- 兼容旧版：自动转换旧版本存档格式
- 分层存储：将存档文件分类存放在不同目录

## 目录结构

```
save/
├── README.md          # 本文档
├── __init__.py        # 包初始化文件
├── save_manager.py    # 存档管理核心实现
├── characters/        # 存放角色存档的目录
└── backups/           # 存放备份文件的目录
```

## 函数使用说明

### 基本配置

```python
configure_save_system(save_dir=None, save_name=None)
```
配置存档系统的基本路径和当前使用的存档。

**参数**:
- `save_dir`: 存档目录路径
- `save_name`: 存档名称

**示例**:
```python
from save import save_manager
# 配置默认存档
save_manager.configure_save_system()
# 配置特定存档
save_manager.configure_save_system(save_name="我的角色1")
```

### 存档管理

#### 列出存档

```python
list_saves()
```
获取所有可用的存档列表。

**示例**:
```python
saves = save_manager.list_saves()
print(f"可用存档: {saves}")
```

#### 创建新存档

```python
create_save(save_name, character_name="", description="")
```
创建一个新的存档。

**参数**:
- `save_name`: 存档名称
- `character_name`: 角色名称
- `description`: 存档描述

**示例**:
```python
save_manager.create_save("勇者的旅程", "张三", "初始冒险存档")
```

#### 加载存档

```python
load_save(save_name)
```
加载指定名称的存档。

**参数**:
- `save_name`: 存档名称

**示例**:
```python
save_manager.load_save("勇者的旅程")
```

#### 删除存档

```python
delete_save(save_name)
```
删除指定名称的存档。

**参数**:
- `save_name`: 存档名称

**示例**:
```python
save_manager.delete_save("旧存档")
```

#### 重命名存档

```python
rename_save(old_name, new_name)
```
重命名存档。

**参数**:
- `old_name`: 原存档名称
- `new_name`: 新存档名称

**示例**:
```python
save_manager.rename_save("旧名称", "新名称")
```

### 数据操作

#### 获取当前存档数据

```python
get_current_save_data()
```
获取当前存档的完整数据。

**示例**:
```python
data = save_manager.get_current_save_data()
```

#### 更新存档数据

```python
update_save_data(save_data)
```
更新当前存档的数据。

**参数**:
- `save_data`: 新的存档数据

**示例**:
```python
# 更新存档数据
save_data = load_save("勇者的旅程")
save_data['character']['level'] = 2
save_data("勇者的旅程", save_data, save_type="character")
```

#### 读取指定存档数据

```python
read_save_data(save_name)
```
读取指定存档的数据，不改变当前活动存档。

**参数**:
- `save_name`: 存档名称

**返回值**:
- 存档数据字典，读取失败则返回None

**示例**:
```python
# 不切换当前存档，直接读取其他存档数据
other_save_data = save_manager.read_save_data("其他存档")
if other_save_data:
    # 处理其他存档的数据
    print(f"其他存档的属性数量: {len(other_save_data['attributes'])}")
```

### 元数据操作

#### 获取存档元数据

```python
get_save_metadata()
```
获取当前存档的元数据。

**示例**:
```python
metadata = save_manager.get_save_metadata()
print(f"存档创建时间: {metadata['created_at']}")
```

#### 更新元数据字段

```python
update_save_metadata(key, value)
```
更新存档元数据的特定字段。

**参数**:
- `key`: 元数据字段名
- `value`: 新的字段值

**示例**:
```python
save_manager.update_save_metadata("character_name", "新名称")
```

### 工具函数

#### 获取当前存档名称

```python
get_current_save_name()
```
获取当前加载的存档名称。

**示例**:
```python
name = save_manager.get_current_save_name()
print(f"当前存档: {name}")
```

#### 获取存档文件路径

```python
get_save_file_path()
```
获取当前存档文件的完整路径。

**示例**:
```python
path = save_manager.get_save_file_path()
print(f"存档文件路径: {path}")
```

## 与其他模块的集成

save模块设计为底层存储服务，可被多个上层模块使用：

- `character_manager`模块：使用save_manager存储角色属性数据
  - 大部分功能是对save_manager接口的封装或扩展
  - `get_attribute_from_save`函数使用`read_save_data`实现跨存档数据访问
  - 提供了针对角色数据的特定业务逻辑（属性分类、物品管理等）
- 未来可能的其他模块：任务系统、成就系统等

### 模块间关系

save_manager作为底层存储引擎，主要负责：
1. 文件操作（读/写/删除）
2. 数据序列化和反序列化
3. 存档元数据管理
4. 多存档管理

而上层模块（如character_manager）则关注：
1. 特定数据结构的操作（如属性CRUD操作）
2. 业务逻辑实现
3. 用户友好的接口提供

这种分层设计使得系统更加模块化，每个部分专注于自身职责。

### 存档记忆功能

save_manager模块提供了存档记忆功能，能够记住上次使用的存档，并在下次启动时自动加载：

```python
load_previous_save()
```
加载上次使用的存档。

**示例**:
```python
# 程序启动时加载上次使用的存档
save_manager.load_previous_save()
```

**工作原理**:
- 在创建、加载或重命名存档时，系统会自动记录当前存档名称到配置文件
- 配置文件存储在`save/save_config.json`
- 加载上次存档时，系统会从配置文件读取上次使用的存档名称，然后尝试加载该存档

**character_manager接口**:
```python
load_previous_game()
```
加载上次使用的游戏存档，是对`save_manager.load_previous_save()`的封装。

**示例**:
```python
# 程序启动时加载上次游戏
from character import character_manager
character_manager.load_previous_game()
```

## 未来计划

以下功能计划在未来版本中实现：

### 1. 性能优化
- 懒加载：只在需要时读取数据
- 缓存系统：减少文件IO操作
- 增量保存：只保存修改过的部分

### 2. 安全性增强
- 数据校验：添加校验和机制确保数据完整性
- 加密支持：可选的数据加密功能
- 错误恢复：自动备份和崩溃恢复

### 3. 高级功能
- 事件系统：在数据变化时触发回调
- 自动备份：定期创建自动备份
- 压缩存储：减少存档文件体积
- 云存储支持：同步到云端服务

### 4. 模块化设计
- 存储引擎抽象：支持不同的后端存储（JSON, SQLite, 云存储等）
- 插件系统：允许扩展存档系统功能 