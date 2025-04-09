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

# TODO: 替换为实际的存档系统导入
# from save import save_manager

# 临时实现的存档系统接口
class TempSaveSystem:
    def __init__(self, save_dir=None, save_file=None):
        # 修改数据结构，添加属性分类
        self._save_data = {
            "角色数据": {},  # 属性值
            "属性类别": {}   # 属性类别
        }
        
        # 设置存档目录和文件位置
        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save")
        
        if save_file is None:
            self._save_file = os.path.join(save_dir, "temp_save.json")
        else:
            self._save_file = os.path.join(save_dir, save_file)
            
        self._load_save()
    
    def _load_save(self):
        try:
            if os.path.exists(self._save_file):
                with open(self._save_file, 'r', encoding='utf-8') as f:
                    self._save_data = json.load(f)
                    if "角色数据" not in self._save_data:
                        self._save_data["角色数据"] = {}
                    # 确保属性类别数据存在
                    if "属性类别" not in self._save_data:
                        self._save_data["属性类别"] = {}
        except Exception as e:
            print(f"加载存档失败: {str(e)}")
            self._save_data = {"角色数据": {}, "属性类别": {}}
    
    def _save_data_to_file(self):
        try:
            os.makedirs(os.path.dirname(self._save_file), exist_ok=True)
            with open(self._save_file, 'w', encoding='utf-8') as f:
                json.dump(self._save_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存存档失败: {str(e)}")
            return False
    
    def get_current_save_data(self):
        return self._save_data
    
    def update_save_data(self, save_data):
        self._save_data = save_data
        return self._save_data_to_file()
    
    def get_save_file_path(self):
        """返回当前使用的存档文件路径"""
        return self._save_file

# 使用临时存档系统
save_system = TempSaveSystem()

# 配置存档系统的函数
def configure_save_system(save_dir=None, save_file=None):
    """
    配置存档系统的存储位置
    
    参数:
        save_dir (str): 存档目录路径
        save_file (str): 存档文件名称
        
    返回:
        TempSaveSystem: 配置好的存档系统实例
    """
    global save_system
    save_system = TempSaveSystem(save_dir, save_file)
    return save_system

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
        save_data = save_system.get_current_save_data()
        if attr_name in save_data["角色数据"]:
            print(f"属性 '{attr_name}' 已存在，无法创建")
            return False
        
        # 存储属性值
        save_data["角色数据"][attr_name] = attr_value
        
        # 存储属性类别（如果提供）
        if attr_category is not None:
            save_data["属性类别"][attr_name] = attr_category
            
        return save_system.update_save_data(save_data)
    except Exception as e:
        print(f"创建属性 '{attr_name}' 失败: {str(e)}")
        return False

def delete_attribute(attr_name):
    """删除一个角色属性"""
    try:
        save_data = save_system.get_current_save_data()
        if attr_name not in save_data["角色数据"]:
            print(f"属性 '{attr_name}' 不存在，无法删除")
            return False
        
        # 删除属性值
        del save_data["角色数据"][attr_name]
        
        # 同时删除属性类别（如果存在）
        if attr_name in save_data["属性类别"]:
            del save_data["属性类别"][attr_name]
            
        return save_system.update_save_data(save_data)
    except Exception as e:
        print(f"删除属性 '{attr_name}' 失败: {str(e)}")
        return False

def get_attribute(attr_name):
    """获取指定属性的值"""
    try:
        save_data = save_system.get_current_save_data()
        return save_data["角色数据"].get(attr_name, None)
    except Exception as e:
        print(f"获取属性 '{attr_name}' 失败: {str(e)}")
        return None

def set_attribute(attr_name, attr_value):
    """设置指定属性的值"""
    try:
        save_data = save_system.get_current_save_data()
        save_data["角色数据"][attr_name] = attr_value
        return save_system.update_save_data(save_data)
    except Exception as e:
        print(f"设置属性 '{attr_name}' 失败: {str(e)}")
        return False

def list_attributes():
    """列出所有已定义的属性"""
    try:
        save_data = save_system.get_current_save_data()
        return list(save_data["角色数据"].keys())
    except Exception as e:
        print(f"列出属性失败: {str(e)}")
        return []

def get_all_attributes():
    """获取所有属性及其值"""
    try:
        save_data = save_system.get_current_save_data()
        return dict(save_data["角色数据"])
    except Exception as e:
        print(f"获取所有属性失败: {str(e)}")
        return {}

def get_save_location():
    """获取当前存档文件的位置"""
    return save_system.get_save_file_path()

# 新增：获取属性类别功能
def get_attribute_category(attr_name):
    """
    获取指定属性的类别
    
    参数:
        attr_name (str): 属性名称
        
    返回:
        str: 属性类别，如果属性不存在或没有设置类别则返回None
    """
    try:
        save_data = save_system.get_current_save_data()
        return save_data["属性类别"].get(attr_name, None)
    except Exception as e:
        print(f"获取属性 '{attr_name}' 的类别失败: {str(e)}")
        return None

# 新增：设置属性类别功能
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
        save_data = save_system.get_current_save_data()
        if attr_name not in save_data["角色数据"]:
            print(f"属性 '{attr_name}' 不存在，无法设置类别")
            return False
            
        save_data["属性类别"][attr_name] = category
        return save_system.update_save_data(save_data)
    except Exception as e:
        print(f"设置属性 '{attr_name}' 的类别失败: {str(e)}")
        return False

# 新增：获取指定类别的所有属性
def get_attributes_by_category(category):
    """
    获取指定类别的所有属性名称
    
    参数:
        category (str): 类别名称
        
    返回:
        list: 该类别下的所有属性名称列表
    """
    try:
        save_data = save_system.get_current_save_data()
        result = []
        
        for attr_name, attr_category in save_data["属性类别"].items():
            if attr_category == category:
                result.append(attr_name)
                
        return result
    except Exception as e:
        print(f"获取类别 '{category}' 的属性失败: {str(e)}")
        return []

# 新增：计算指定类别的属性数量
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

# 新增：获取指定类别的第N个属性
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

# 新增：列出所有可用的属性类别
def list_categories():
    """
    列出所有已使用的属性类别
    
    返回:
        list: 所有使用过的类别名称列表
    """
    try:
        save_data = save_system.get_current_save_data()
        categories = set(save_data["属性类别"].values())
        return list(categories)
    except Exception as e:
        print(f"列出属性类别失败: {str(e)}")
        return []

# 新增：快速创建某类别的新属性（自动生成属性名）
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

# 新增：提取物品特定属性的辅助函数
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

# 新增：搜索特定特性值的物品
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