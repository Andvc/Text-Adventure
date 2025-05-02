"""
游戏数据管理模块 - 提供游戏数据的统一管理功能
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
        self._saves_dir = os.path.join(os.path.dirname(self._data_dir), "save", "characters")
        
        # 确保目录存在
        os.makedirs(self._text_dir, exist_ok=True)
        os.makedirs(self._saves_dir, exist_ok=True)
        
        # 缓存已加载的数据
        self._data_cache = {}
    
    def get_save_path(self, save_type, save_name):
        """
        获取保存文件的完整路径
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            
        返回:
            str: 保存文件的完整路径
        """
        if save_type == 'text':
            return os.path.join(self._text_dir, f"{save_name}.json")
        elif save_type == 'character':
            return os.path.join(self._saves_dir, f"{save_name}.json")
        else:
            # 未来可扩展其他类型
            return None
    
    def load_save(self, save_type, save_name):
        """
        加载保存的数据
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            
        返回:
            dict: 数据内容，读取失败则返回None
        """
        # 检查缓存
        cache_key = f"{save_type}:{save_name}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        try:
            save_path = self.get_save_path(save_type, save_name)
            if not save_path or not os.path.exists(save_path):
                print(f"保存文件 '{save_name}' 不存在于 '{save_type}' 目录")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 缓存数据
                self._data_cache[cache_key] = data
                return data
        except Exception as e:
            print(f"读取保存文件 '{save_name}' 失败: {str(e)}")
            return None
    
    def get_save_value(self, save_type, save_name, key, default=None):
        """
        从保存的数据中获取特定键的值
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            key (str): 数据键名
            default: 默认值，如果数据不存在则返回此值
            
        返回:
            任意类型: 数据值或默认值
        """
        data = self.load_save(save_type, save_name)
        if data is None:
            return default
        
        return data.get(key, default)
    
    def save_data(self, save_type, save_name, data):
        """
        保存数据
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            data (dict): 要保存的数据
            
        返回:
            bool: 是否保存成功
        """
        try:
            save_path = self.get_save_path(save_type, save_name)
            if not save_path:
                print(f"无法确定保存类型 '{save_type}' 的文件路径")
                return False
            
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 写入文件
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 更新缓存
            cache_key = f"{save_type}:{save_name}"
            self._data_cache[cache_key] = data
            
            return True
        except Exception as e:
            print(f"保存数据 '{save_name}' 失败: {str(e)}")
            return False
    
    def clear_cache(self, save_type=None, save_name=None):
        """
        清除数据缓存
        
        参数:
            save_type (str, optional): 保存类型，如果指定则只清除该类型的缓存
            save_name (str, optional): 保存名称，如果指定则只清除该保存的缓存
            
        返回:
            int: 清除的缓存条目数量
        """
        count = 0
        if save_type and save_name:
            cache_key = f"{save_type}:{save_name}"
            if cache_key in self._data_cache:
                del self._data_cache[cache_key]
                count = 1
        elif save_type:
            keys_to_remove = [k for k in self._data_cache.keys() if k.startswith(f"{save_type}:")]
            for key in keys_to_remove:
                del self._data_cache[key]
                count += 1
        else:
            count = len(self._data_cache)
            self._data_cache.clear()
        
        return count

    def get_nested_save_value(self, save_type, save_name, path, default=None):
        """
        从保存的数据中获取嵌套路径的值
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            path (str): 数据路径，使用点号分隔，如 'layers.layer1.name'
            default: 默认值，如果数据不存在则返回此值
            
        返回:
            任意类型: 数据值或默认值
        """
        data = self.load_save(save_type, save_name)
        if data is None:
            return default
        
        try:
            # 分割路径
            keys = path.split('.')
            result = data
            
            # 逐层访问
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key, default)
                else:
                    return default
                
            return result
        except Exception as e:
            print(f"获取嵌套数据 '{path}' 失败: {str(e)}")
            return default

    def get_indexed_save(self, index_file, detail_type):
        """
        根据索引文件获取指定类型的所有数据
        
        参数:
            index_file (str): 索引文件名（不含扩展名）
            detail_type (str): 数据类型，如 'detail1', 'detail2'
            
        返回:
            dict: 包含所有请求字段的数据字典
        """
        try:
            # 读取索引文件
            index_path = os.path.join(self._data_dir, "index", f"{index_file}.json")
            if not os.path.exists(index_path):
                print(f"索引文件 '{index_path}' 不存在")
                return None
            
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 获取指定类型的配置
            detail_config = index_data.get(detail_type)
            if detail_config is None:
                print(f"类型 '{detail_type}' 在索引文件中不存在")
                return None
            
            # 获取文件路径和字段列表
            file_path = detail_config.get('file_path')
            fields = detail_config.get('fields', [])
            
            if not file_path or not fields:
                print(f"索引配置不完整: {detail_config}")
                return None
            
            # 读取目标文件
            target_data = self.load_save('text', file_path)
            if target_data is None:
                print(f"目标文件 '{file_path}' 不存在")
                return None
            
            # 提取数据
            result = {}
            for field in fields:
                if '.' in field:
                    # 使用嵌套数据获取函数
                    value = self.get_nested_save_value('text', file_path, field)
                else:
                    # 使用普通数据获取函数
                    value = self.get_save_value('text', file_path, field)
                result[field] = value
            
            return result
        except Exception as e:
            print(f"获取索引数据失败: {str(e)}")
            return None

    def list_saves(self, save_type=None):
        """
        列出所有保存的数据
        
        参数:
            save_type (str, optional): 保存类型，如果指定则只列出该类型的保存
            
        返回:
            list: 保存名称列表
        """
        saves = []
        if save_type == 'text' or save_type is None:
            for file in os.listdir(self._text_dir):
                if file.endswith('.json'):
                    saves.append(os.path.splitext(file)[0])
        if save_type == 'character' or save_type is None:
            for file in os.listdir(self._saves_dir):
                if file.endswith('.json'):
                    saves.append(os.path.splitext(file)[0])
        return saves
    
    def create_save(self, save_type, save_name, save_data=None):
        """
        创建新的保存
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            save_data (dict, optional): 初始数据，默认为空字典
            
        返回:
            bool: 是否创建成功
        """
        if save_data is None:
            save_data = {}
        return self.save_data(save_type, save_name, save_data)
    
    def delete_save(self, save_type, save_name):
        """
        删除保存
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            save_name (str): 保存名称
            
        返回:
            bool: 是否删除成功
        """
        try:
            save_path = self.get_save_path(save_type, save_name)
            if not save_path or not os.path.exists(save_path):
                print(f"保存文件 '{save_name}' 不存在")
                return False
            
            os.remove(save_path)
            
            # 清除缓存
            self.clear_cache(save_type, save_name)
            
            return True
        except Exception as e:
            print(f"删除保存 '{save_name}' 失败: {str(e)}")
            return False
    
    def rename_save(self, save_type, old_name, new_name):
        """
        重命名保存的数据
        
        参数:
            save_type (str): 保存类型，如'text'、'character'等
            old_name (str): 原保存名称
            new_name (str): 新保存名称
            
        返回:
            bool: 是否重命名成功
        """
        try:
            old_path = self.get_save_path(save_type, old_name)
            new_path = self.get_save_path(save_type, new_name)
            
            if not old_path or not os.path.exists(old_path):
                print(f"原保存文件 '{old_name}' 不存在")
                return False
            
            if os.path.exists(new_path):
                print(f"新保存名称 '{new_name}' 已存在")
                return False
            
            os.rename(old_path, new_path)
            
            # 更新缓存
            old_cache_key = f"{save_type}:{old_name}"
            if old_cache_key in self._data_cache:
                self._data_cache[f"{save_type}:{new_name}"] = self._data_cache[old_cache_key]
                del self._data_cache[old_cache_key]
            
            return True
        except Exception as e:
            print(f"重命名保存 '{old_name}' 失败: {str(e)}")
            return False

# 全局函数
def configure_data_system(data_dir=None):
    """
    配置数据管理系统
    
    参数:
        data_dir (str, optional): 数据目录路径
    """
    global data_manager
    data_manager = DataManager(data_dir)

def get_save_path(save_type, save_name):
    """
    获取保存文件的完整路径
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
    """
    return data_manager.get_save_path(save_type, save_name)

def load_save(save_type, save_name):
    """
    加载保存的数据
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
    """
    return data_manager.load_save(save_type, save_name)

def get_save_value(save_type, save_name, key, default=None):
    """
    从保存的数据中获取特定键的值
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
        key (str): 数据键名
        default: 默认值
    """
    return data_manager.get_save_value(save_type, save_name, key, default)

def save_data(save_type, save_name, data):
    """
    保存数据
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
        data (dict): 要保存的数据
    """
    return data_manager.save_data(save_type, save_name, data)

def clear_cache(save_type=None, save_name=None):
    """
    清除数据缓存
    
    参数:
        save_type (str, optional): 保存类型
        save_name (str, optional): 保存名称
    """
    return data_manager.clear_cache(save_type, save_name)

def get_nested_save_value(save_type, save_name, path, default=None):
    """
    从保存的数据中获取嵌套路径的值
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
        path (str): 数据路径
        default: 默认值
    """
    return data_manager.get_nested_save_value(save_type, save_name, path, default)

def get_indexed_save(index_file, detail_type):
    """
    根据索引文件获取指定类型的所有数据
    
    参数:
        index_file (str): 索引文件名
        detail_type (str): 数据类型
    """
    return data_manager.get_indexed_save(index_file, detail_type)

def list_saves(save_type=None):
    """
    列出所有保存的数据
    
    参数:
        save_type (str, optional): 保存类型
    """
    return data_manager.list_saves(save_type)

def create_save(save_type, save_name, save_data=None):
    """
    创建新的保存
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
        save_data (dict, optional): 初始数据
    """
    return data_manager.create_save(save_type, save_name, save_data)

def rename_save(save_type, old_name, new_name):
    """
    重命名保存
    
    参数:
        save_type (str): 保存类型
        old_name (str): 原名称
        new_name (str): 新名称
    """
    return data_manager.rename_save(save_type, old_name, new_name)

def delete_save(save_type, save_name):
    """
    删除保存
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
    """
    return data_manager.delete_save(save_type, save_name)

def update_save(save_type, save_name, save_data):
    """
    更新保存
    
    参数:
        save_type (str): 保存类型
        save_name (str): 保存名称
        save_data (dict): 新的保存数据
    """
    return data_manager.update_save(save_type, save_name, save_data)

# 初始化数据管理器
configure_data_system() 