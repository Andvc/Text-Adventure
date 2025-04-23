"""
角色属性管理模块 - 提供角色属性的创建、读取、修改和删除功能
"""

import os
import sys
import json
import time
from collections import defaultdict

# 临时添加父目录到系统路径，以便导入save模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入save_manager和data_manager模块
from save import save_manager
from data import data_manager

# 配置存档系统的函数
def configure_save_system(save_dir=None, save_file=None):
    """
    配置存档系统的存储位置
    
    参数:
        save_dir (str): 存档目录路径
        save_file (str): 存档文件名称
        
    返回:
        SaveManager: 配置好的存档管理器
    """
    return save_manager.configure_save_system(save_dir, save_file)

def create_attribute(attr_name, attr_value, attr_category=None):
    """
    创建一个新的角色属性，可以同时指定属性类别
    
    参数:
        attr_name (str): 属性名称
        attr_value (any): 属性值
        attr_category (str, optional): 属性类别，默认为None
        
    返回:
        bool: 是否创建成功
    """
    try:
        save_data = save_manager.get_current_save_data()
        if attr_name in save_data["attributes"]:
            print(f"属性 '{attr_name}' 已存在，无法创建")
            return False
        
        # 存储属性值
        save_data["attributes"][attr_name] = attr_value
        
        # 存储属性类别（如果提供）
        if attr_category is not None:
            save_data["attribute_categories"][attr_name] = attr_category
            
        return save_manager.update_save_data(save_data)
    except Exception as e:
        print(f"创建属性 '{attr_name}' 失败: {str(e)}")
        return False

def delete_attribute(attr_name):
    """删除一个角色属性"""
    try:
        save_data = save_manager.get_current_save_data()
        if attr_name not in save_data["attributes"]:
            print(f"属性 '{attr_name}' 不存在，无法删除")
            return False
        
        # 删除属性值
        del save_data["attributes"][attr_name]
        
        # 同时删除属性类别（如果存在）
        if attr_name in save_data["attribute_categories"]:
            del save_data["attribute_categories"][attr_name]
            
        return save_manager.update_save_data(save_data)
    except Exception as e:
        print(f"删除属性 '{attr_name}' 失败: {str(e)}")
        return False

def get_attribute(attr_name):
    """获取指定属性的值"""
    try:
        save_data = save_manager.get_current_save_data()
        return save_data["attributes"].get(attr_name, None)
    except Exception as e:
        print(f"获取属性 '{attr_name}' 失败: {str(e)}")
        return None

def set_attribute(attr_name, attr_value):
    """设置指定属性的值"""
    try:
        save_data = save_manager.get_current_save_data()
        save_data["attributes"][attr_name] = attr_value
        return save_manager.update_save_data(save_data)
    except Exception as e:
        print(f"设置属性 '{attr_name}' 失败: {str(e)}")
        return False

def list_attributes():
    """列出所有已定义的属性"""
    try:
        save_data = save_manager.get_current_save_data()
        return list(save_data["attributes"].keys())
    except Exception as e:
        print(f"列出属性失败: {str(e)}")
        return []

def get_all_attributes():
    """获取所有属性及其值"""
    try:
        save_data = save_manager.get_current_save_data()
        return dict(save_data["attributes"])
    except Exception as e:
        print(f"获取所有属性失败: {str(e)}")
        return {}

def get_save_location():
    """获取当前存档文件的位置"""
    return save_manager.get_save_file_path()

# 获取属性类别功能
def get_attribute_category(attr_name):
    """
    获取指定属性的类别
    
    参数:
        attr_name (str): 属性名称
        
    返回:
        str: 属性类别，如果属性不存在或没有设置类别则返回None
    """
    try:
        save_data = save_manager.get_current_save_data()
        return save_data["attribute_categories"].get(attr_name, None)
    except Exception as e:
        print(f"获取属性 '{attr_name}' 的类别失败: {str(e)}")
        return None

# 设置属性类别功能
def set_attribute_category(attr_name, category):
    """
    设置指定属性的类别
    
    参数:
        attr_name (str): 属性名称
        category (str): 类别名称，如"buff"、"inventory"等
        
    返回:
        bool: 是否设置成功
    """
    try:
        save_data = save_manager.get_current_save_data()
        if attr_name not in save_data["attributes"]:
            print(f"属性 '{attr_name}' 不存在，无法设置类别")
            return False
            
        save_data["attribute_categories"][attr_name] = category
        return save_manager.update_save_data(save_data)
    except Exception as e:
        print(f"设置属性 '{attr_name}' 的类别失败: {str(e)}")
        return False

# 获取指定类别的所有属性
def get_attributes_by_category(category):
    """
    获取指定类别的所有属性名称
    
    参数:
        category (str): 类别名称
        
    返回:
        list: 该类别下的所有属性名称列表
    """
    try:
        save_data = save_manager.get_current_save_data()
        result = []
        
        for attr_name, attr_category in save_data["attribute_categories"].items():
            if attr_category == category:
                result.append(attr_name)
                
        return result
    except Exception as e:
        print(f"获取类别 '{category}' 的属性失败: {str(e)}")
        return []

# 计算指定类别的属性数量
def count_attributes_by_category(category):
    """
    计算指定类别的属性数量
    
    参数:
        category (str): 类别名称
        
    返回:
        int: 该类别下的属性数量
    """
    try:
        attrs = get_attributes_by_category(category)
        return len(attrs)
    except Exception as e:
        print(f"计算类别 '{category}' 的属性数量失败: {str(e)}")
        return 0

# 获取指定类别的第N个属性
def get_attribute_by_index(category, index):
    """
    获取指定类别的第N个属性值
    
    参数:
        category (str): 类别名称
        index (int): 索引值（从0开始）
        
    返回:
        tuple: (属性名, 属性值)，如果索引越界或类别不存在则返回(None, None)
    """
    try:
        attrs = get_attributes_by_category(category)
        if 0 <= index < len(attrs):
            attr_name = attrs[index]
            attr_value = get_attribute(attr_name)
            return attr_name, attr_value
        else:
            print(f"索引 {index} 超出类别 '{category}' 的属性范围")
            return None, None
    except Exception as e:
        print(f"获取类别 '{category}' 的第 {index} 个属性失败: {str(e)}")
        return None, None

# 列出所有可用的属性类别
def list_categories():
    """
    列出所有已使用的属性类别
    
    返回:
        list: 所有使用过的类别名称列表
    """
    try:
        save_data = save_manager.get_current_save_data()
        categories = set(save_data["attribute_categories"].values())
        return list(categories)
    except Exception as e:
        print(f"列出属性类别失败: {str(e)}")
        return []

# 快速创建某类别的新属性（自动生成属性名）
def create_category_attribute(attr_value, category):
    """
    快速创建某类别的新属性，自动生成属性名
    
    参数:
        attr_value (any): 属性值
        category (str): 属性类别
        
    返回:
        str: 成功时返回生成的属性名，失败时返回None
    """
    try:
        # 确保类别名称非空
        if not category:
            print("属性类别不能为空")
            return None
            
        # 获取当前时间戳作为唯一标识符的一部分
        timestamp = int(time.time() * 1000)
        
        # 获取该类别下的已有属性数量
        category_count = count_attributes_by_category(category)
        
        # 生成属性名：类别_数量_时间戳
        attr_name = f"{category}_{category_count + 1}_{timestamp}"
        
        # 创建属性
        success = create_attribute(attr_name, attr_value, category)
        
        if success:
            print(f"已创建类别 '{category}' 的新属性: '{attr_name}'")
            return attr_name
        else:
            print(f"创建类别 '{category}' 的新属性失败")
            return None
    except Exception as e:
        print(f"快速创建类别 '{category}' 的新属性失败: {str(e)}")
        return None

# 提取物品特定属性的辅助函数
def get_item_property(item_name, property_name, default=None):
    """
    提取物品的特定属性值，支持嵌套字典
    
    参数:
        item_name (str): 物品属性名
        property_name (str): 要获取的物品特性名称
        default (any, optional): 若物品或特性不存在时返回的默认值
        
    返回:
        any: 物品的特定特性值，如不存在则返回默认值
    """
    try:
        # 获取物品数据
        item_data = get_attribute(item_name)
        
        # 检查物品是否存在
        if item_data is None:
            print(f"物品 '{item_name}' 不存在")
            return default
            
        # 检查物品数据是否为字典类型
        if not isinstance(item_data, dict):
            print(f"物品 '{item_name}' 的数据不是字典类型，无法提取特性")
            return default
            
        # 获取特性值
        if property_name in item_data:
            return item_data[property_name]
        else:
            print(f"物品 '{item_name}' 没有 '{property_name}' 特性")
            return default
            
    except Exception as e:
        print(f"提取物品 '{item_name}' 的 '{property_name}' 特性失败: {str(e)}")
        return default

# 搜索特定特性值的物品
def search_items_by_property(category, property_name, property_value):
    """
    在指定类别中搜索具有特定特性值的物品
    
    参数:
        category (str): 物品类别，如"背包物品"、"装备"等
        property_name (str): 特性名称，如"品质"、"类型"等
        property_value (any): 要搜索的特性值
        
    返回:
        list: 匹配条件的物品名称列表
    """
    try:
        # 获取指定类别的所有物品
        items = get_attributes_by_category(category)
        matching_items = []
        
        # 遍历每个物品，检查特性值
        for item_name in items:
            item_data = get_attribute(item_name)
            
            # 检查物品数据是否为字典类型
            if isinstance(item_data, dict) and property_name in item_data:
                # 检查特性值是否匹配
                if item_data[property_name] == property_value:
                    matching_items.append(item_name)
                    
        return matching_items
    except Exception as e:
        print(f"搜索特性为 '{property_name}={property_value}' 的物品失败: {str(e)}")
        return []

# 多存档管理功能
def list_saves():
    """
    列出所有可用的存档
    
    返回:
        list: 存档名称列表
    """
    return save_manager.list_saves()

def create_save(save_name, character_name="", description=""):
    """
    创建新存档
    
    参数:
        save_name (str): 存档名称
        character_name (str): 角色名称
        description (str): 存档描述
    
    返回:
        bool: 是否创建成功
    """
    return save_manager.create_save(save_name, character_name, description)

def load_save(save_name):
    """
    加载指定的存档
    
    参数:
        save_name (str): 存档名称
    
    返回:
        bool: 是否加载成功
    """
    return save_manager.load_save(save_name)

def delete_save(save_name):
    """
    删除指定的存档
    
    参数:
        save_name (str): 存档名称
    
    返回:
        bool: 是否删除成功
    """
    return save_manager.delete_save(save_name)

def rename_save(old_name, new_name):
    """
    重命名存档
    
    参数:
        old_name (str): 原存档名称
        new_name (str): 新存档名称
    
    返回:
        bool: 是否重命名成功
    """
    return save_manager.rename_save(old_name, new_name)

def get_current_save_name():
    """
    获取当前存档名称
    
    返回:
        str: 当前存档名称
    """
    return save_manager.get_current_save_name()

def get_save_metadata():
    """
    获取当前存档的元数据
    
    返回:
        dict: 存档元数据
    """
    return save_manager.get_save_metadata()

def update_save_metadata(key, value):
    """
    更新存档元数据的特定字段
    
    参数:
        key (str): 元数据字段名
        value: 字段值
    
    返回:
        bool: 是否更新成功
    """
    return save_manager.update_save_metadata(key, value)

def get_attribute_from_save(save_name, attr_name, default=None):
    """
    从指定存档中读取属性值，不改变当前活动存档
    
    参数:
        save_name (str): 要读取的存档名称
        attr_name (str): 要读取的属性名称
        default (any, optional): 如果属性不存在时返回的默认值
        
    返回:
        any: 属性值，如不存在则返回默认值
    """
    try:
        save_data = save_manager.read_save_data(save_name)
        if save_data is None:
            return default
            
        return save_data["attributes"].get(attr_name, default)
    except Exception as e:
        print(f"从存档 '{save_name}' 读取属性 '{attr_name}' 失败: {str(e)}")
        return default

def load_previous_game():
    """
    加载上次使用的游戏存档
    
    返回:
        bool: 是否加载成功
    """
    return save_manager.load_previous_save()

def get_data(data_type, file_name, key, default=None):
    """
    从游戏数据文件中读取特定键的值
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名（不含扩展名）
        key (str): 数据键名
        default: 默认值，如果数据不存在则返回此值
        
    返回:
        任意类型: 数据值或默认值
    """
    try:
        return data_manager.get_data_value(data_type, file_name, key, default)
    except Exception as e:
        print(f"从数据文件 '{file_name}' 读取键 '{key}' 失败: {str(e)}")
        return default

def read_data_file(data_type, file_name):
    """
    读取整个游戏数据文件
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名（不含扩展名）
        
    返回:
        dict: 数据内容，读取失败则返回None
    """
    try:
        return data_manager.read_data_file(data_type, file_name)
    except Exception as e:
        print(f"读取数据文件 '{file_name}' 失败: {str(e)}")
        return None 