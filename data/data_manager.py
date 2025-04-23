"""
游戏数据管理模块 - 提供游戏固定数据的读取和管理功能
"""

import os
import sys
import json
import time
from collections import defaultdict

# 全局数据管理器实例
data_manager = None

class DataManager:
    def __init__(self, data_dir=None):
        """
        初始化数据管理器
        
        参数:
            data_dir (str): 数据目录路径，默认为项目根目录下的data文件夹
        """
        # 设置基本路径
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        
        self._data_dir = data_dir
        self._text_dir = os.path.join(self._data_dir, "text")
        
        # 确保目录存在
        os.makedirs(self._text_dir, exist_ok=True)
        
        # 缓存已加载的数据
        self._data_cache = {}
    
    def get_data_file_path(self, data_type, file_name):
        """
        获取数据文件的完整路径
        
        参数:
            data_type (str): 数据类型，如'text'、'images'等
            file_name (str): 文件名
            
        返回:
            str: 数据文件的完整路径
        """
        if data_type == 'text':
            return os.path.join(self._text_dir, f"{file_name}.json")
        else:
            # 未来可扩展其他类型
            return None
    
    def read_data_file(self, data_type, file_name):
        """
        读取指定的数据文件
        
        参数:
            data_type (str): 数据类型，如'text'、'images'等
            file_name (str): 文件名（不含扩展名）
            
        返回:
            dict: 数据内容，读取失败则返回None
        """
        # 检查缓存
        cache_key = f"{data_type}:{file_name}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        try:
            file_path = self.get_data_file_path(data_type, file_name)
            if not file_path or not os.path.exists(file_path):
                print(f"数据文件 '{file_name}' 不存在于 '{data_type}' 目录")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 缓存数据
                self._data_cache[cache_key] = data
                return data
        except Exception as e:
            print(f"读取数据文件 '{file_name}' 失败: {str(e)}")
            return None
    
    def get_data_value(self, data_type, file_name, key, default=None):
        """
        从数据文件中获取特定键的值
        
        参数:
            data_type (str): 数据类型，如'text'、'images'等
            file_name (str): 文件名（不含扩展名）
            key (str): 数据键名
            default: 默认值，如果数据不存在则返回此值
            
        返回:
            任意类型: 数据值或默认值
        """
        data = self.read_data_file(data_type, file_name)
        if data is None:
            return default
        
        return data.get(key, default)
    
    def save_data_file(self, data_type, file_name, data):
        """
        保存数据到文件
        
        参数:
            data_type (str): 数据类型，如'text'、'images'等
            file_name (str): 文件名（不含扩展名）
            data (dict): 要保存的数据
            
        返回:
            bool: 是否保存成功
        """
        try:
            file_path = self.get_data_file_path(data_type, file_name)
            if not file_path:
                print(f"无法确定数据类型 '{data_type}' 的文件路径")
                return False
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 更新缓存
            cache_key = f"{data_type}:{file_name}"
            self._data_cache[cache_key] = data
            
            return True
        except Exception as e:
            print(f"保存数据文件 '{file_name}' 失败: {str(e)}")
            return False
    
    def clear_cache(self, data_type=None, file_name=None):
        """
        清除数据缓存
        
        参数:
            data_type (str, optional): 数据类型，如果指定则只清除该类型的缓存
            file_name (str, optional): 文件名，如果指定则只清除该文件的缓存
            
        返回:
            int: 清除的缓存条目数量
        """
        count = 0
        if data_type and file_name:
            cache_key = f"{data_type}:{file_name}"
            if cache_key in self._data_cache:
                del self._data_cache[cache_key]
                count = 1
        elif data_type:
            keys_to_remove = [k for k in self._data_cache.keys() if k.startswith(f"{data_type}:")]
            for key in keys_to_remove:
                del self._data_cache[key]
                count += 1
        else:
            count = len(self._data_cache)
            self._data_cache.clear()
        
        return count

# 公共接口函数

def configure_data_system(data_dir=None):
    """
    配置数据管理系统
    
    参数:
        data_dir (str): 数据目录路径
        
    返回:
        DataManager: 配置好的数据管理器
    """
    global data_manager
    data_manager = DataManager(data_dir)
    return data_manager

def get_data_file_path(data_type, file_name):
    """
    获取数据文件的完整路径
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名
        
    返回:
        str: 数据文件的完整路径
    """
    return data_manager.get_data_file_path(data_type, file_name)

def read_data_file(data_type, file_name):
    """
    读取指定的数据文件
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名（不含扩展名）
        
    返回:
        dict: 数据内容，读取失败则返回None
    """
    return data_manager.read_data_file(data_type, file_name)

def get_data_value(data_type, file_name, key, default=None):
    """
    从数据文件中获取特定键的值
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名（不含扩展名）
        key (str): 数据键名
        default: 默认值，如果数据不存在则返回此值
        
    返回:
        任意类型: 数据值或默认值
    """
    return data_manager.get_data_value(data_type, file_name, key, default)

def save_data_file(data_type, file_name, data):
    """
    保存数据到文件
    
    参数:
        data_type (str): 数据类型，如'text'、'images'等
        file_name (str): 文件名（不含扩展名）
        data (dict): 要保存的数据
        
    返回:
        bool: 是否保存成功
    """
    return data_manager.save_data_file(data_type, file_name, data)

def clear_cache(data_type=None, file_name=None):
    """
    清除数据缓存
    
    参数:
        data_type (str, optional): 数据类型，如果指定则只清除该类型的缓存
        file_name (str, optional): 文件名，如果指定则只清除该文件的缓存
        
    返回:
        int: 清除的缓存条目数量
    """
    return data_manager.clear_cache(data_type, file_name)

# 初始化数据管理器
configure_data_system() 