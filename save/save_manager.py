"""
存档管理模块 - 提供游戏存档的创建、读取、修改和删除功能
"""

import os
import sys
import json
import time
from collections import defaultdict

class SaveManager:
    def __init__(self, save_dir=None, save_name=None):
        """
        初始化存档管理器
        
        参数:
            save_dir (str): 存档目录路径
            save_name (str): 存档名称，默认为"default"
        """
        # 设置基本路径
        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self._save_dir = save_dir
        self._characters_dir = os.path.join(save_dir, "save", "characters")
        self._backups_dir = os.path.join(save_dir, "save", "backups")
        
        # 确保目录存在
        for directory in [self._characters_dir, self._backups_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # 设置当前存档
        self._current_save_name = save_name or "default"
        self._save_file = os.path.join(self._characters_dir, f"{self._current_save_name}.json")
        
        # 初始化数据结构
        self._save_data = {
            "metadata": {
                "version": "1.0",
                "created_at": time.time(),
                "last_modified": time.time(),
                "character_name": "",
                "save_name": self._current_save_name,
                "description": ""
            },
            "attributes": {},
            "attribute_categories": {}
        }
        
        # 加载存档
        self._load_save()
    
    def _load_save(self):
        """
        从文件加载存档数据
        
        返回:
            bool: 是否加载成功
        """
        try:
            if os.path.exists(self._save_file):
                with open(self._save_file, 'r', encoding='utf-8') as f:
                    self._save_data = json.load(f)
                    
                    # 兼容旧版数据结构
                    if "角色数据" in self._save_data:
                        self._save_data["attributes"] = self._save_data.pop("角色数据")
                    if "属性类别" in self._save_data:
                        self._save_data["attribute_categories"] = self._save_data.pop("属性类别")
                    
                    # 确保元数据存在
                    if "metadata" not in self._save_data:
                        self._save_data["metadata"] = {
                            "version": "1.0",
                            "created_at": time.time(),
                            "last_modified": time.time(),
                            "character_name": "",
                            "save_name": self._current_save_name,
                            "description": ""
                        }
                    
                    # 确保基本结构完整
                    if "attributes" not in self._save_data:
                        self._save_data["attributes"] = {}
                    if "attribute_categories" not in self._save_data:
                        self._save_data["attribute_categories"] = {}
                    
                    return True
            return False
        except Exception as e:
            print(f"加载存档失败: {str(e)}")
            return False
    
    def _save_data_to_file(self):
        """
        将数据保存到文件
        
        返回:
            bool: 是否保存成功
        """
        try:
            # 更新最后修改时间
            self._save_data["metadata"]["last_modified"] = time.time()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self._save_file), exist_ok=True)
            
            # 写入文件
            with open(self._save_file, 'w', encoding='utf-8') as f:
                json.dump(self._save_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存存档失败: {str(e)}")
            return False
    
    def get_current_save_data(self):
        """
        获取当前存档数据
        
        返回:
            dict: 当前存档数据
        """
        return self._save_data
    
    def update_save_data(self, save_data):
        """
        更新存档数据
        
        参数:
            save_data (dict): 新的存档数据
        
        返回:
            bool: 是否更新成功
        """
        # 保留元数据
        metadata = self._save_data.get("metadata", {})
        
        self._save_data = save_data
        
        # 确保元数据存在
        if "metadata" not in self._save_data:
            self._save_data["metadata"] = metadata
        
        # 更新修改时间
        self._save_data["metadata"]["last_modified"] = time.time()
        
        return self._save_data_to_file()
    
    def get_save_file_path(self):
        """
        获取当前存档文件路径
        
        返回:
            str: 存档文件路径
        """
        return self._save_file
    
    def get_current_save_name(self):
        """
        获取当前存档名称
        
        返回:
            str: 当前存档名称
        """
        return self._current_save_name
    
    def get_save_metadata(self):
        """
        获取当前存档的元数据
        
        返回:
            dict: 存档元数据
        """
        return dict(self._save_data.get("metadata", {}))
    
    def update_metadata(self, key, value):
        """
        更新存档元数据的特定字段
        
        参数:
            key (str): 元数据字段名
            value: 字段值
        
        返回:
            bool: 是否更新成功
        """
        try:
            if "metadata" not in self._save_data:
                self._save_data["metadata"] = {}
            
            self._save_data["metadata"][key] = value
            self._save_data["metadata"]["last_modified"] = time.time()
            
            return self._save_data_to_file()
        except Exception as e:
            print(f"更新元数据失败: {str(e)}")
            return False
    
    def list_saves(self):
        """
        列出所有可用的存档
        
        返回:
            list: 存档名称列表
        """
        saves = []
        try:
            for file in os.listdir(self._characters_dir):
                if file.endswith(".json"):
                    saves.append(os.path.splitext(file)[0])
            return saves
        except Exception as e:
            print(f"列出存档失败: {str(e)}")
            return []
    
    def create_save(self, save_name, character_name="", description=""):
        """
        创建新存档
        
        参数:
            save_name (str): 存档名称
            character_name (str): 角色名称
            description (str): 存档描述
        
        返回:
            bool: 是否创建成功
        """
        try:
            # 检查是否存在同名存档
            if save_name in self.list_saves():
                print(f"存档 '{save_name}' 已存在")
                return False
            
            # 保存当前存档
            if self._save_data["attributes"]:
                self._save_data_to_file()
            
            # 创建新存档
            self._current_save_name = save_name
            self._save_file = os.path.join(self._characters_dir, f"{save_name}.json")
            
            # 初始化新存档数据
            self._save_data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": time.time(),
                    "last_modified": time.time(),
                    "character_name": character_name,
                    "save_name": save_name,
                    "description": description
                },
                "attributes": {},
                "attribute_categories": {}
            }
            
            # 保存新存档
            return self._save_data_to_file()
        except Exception as e:
            print(f"创建存档 '{save_name}' 失败: {str(e)}")
            return False
    
    def load_save(self, save_name):
        """
        加载指定的存档
        
        参数:
            save_name (str): 存档名称
        
        返回:
            bool: 是否加载成功
        """
        try:
            # 检查存档是否存在
            if save_name not in self.list_saves():
                print(f"存档 '{save_name}' 不存在")
                return False
            
            # 保存当前存档
            if self._save_data["attributes"]:
                self._save_data_to_file()
            
            # 设置新的存档文件
            self._current_save_name = save_name
            self._save_file = os.path.join(self._characters_dir, f"{save_name}.json")
            
            # 加载新存档
            return self._load_save()
        except Exception as e:
            print(f"加载存档 '{save_name}' 失败: {str(e)}")
            return False
    
    def delete_save(self, save_name):
        """
        删除指定的存档
        
        参数:
            save_name (str): 存档名称
        
        返回:
            bool: 是否删除成功
        """
        try:
            # 检查存档是否存在
            if save_name not in self.list_saves():
                print(f"存档 '{save_name}' 不存在")
                return False
            
            # 如果删除的是当前存档，先切换到默认存档
            if save_name == self._current_save_name:
                if "default" not in self.list_saves() or "default" == save_name:
                    self.create_save("default")
                self.load_save("default")
            
            # 删除存档文件
            os.remove(os.path.join(self._characters_dir, f"{save_name}.json"))
            return True
        except Exception as e:
            print(f"删除存档 '{save_name}' 失败: {str(e)}")
            return False
    
    def rename_save(self, old_name, new_name):
        """
        重命名存档
        
        参数:
            old_name (str): 原存档名称
            new_name (str): 新存档名称
        
        返回:
            bool: 是否重命名成功
        """
        try:
            # 检查原存档是否存在
            old_save_path = os.path.join(self._characters_dir, f"{old_name}.json")
            if not os.path.exists(old_save_path):
                print(f"存档 '{old_name}' 不存在")
                return False
                
            # 检查新名称是否已被使用
            new_save_path = os.path.join(self._characters_dir, f"{new_name}.json")
            if os.path.exists(new_save_path):
                print(f"存档名称 '{new_name}' 已被使用")
                return False
                
            # 重命名文件
            os.rename(old_save_path, new_save_path)
            
            # 如果当前存档就是被重命名的存档，更新当前存档路径
            if self._current_save_name == old_name:
                self._current_save_name = new_name
                self._save_file = new_save_path
                
                # 更新存档内的名称
                self._save_data["metadata"]["save_name"] = new_name
                self._save_data_to_file()
                
            print(f"已将存档 '{old_name}' 重命名为 '{new_name}'")
            return True
            
        except Exception as e:
            print(f"重命名存档失败: {str(e)}")
            return False
    
    def read_save_data(self, save_name):
        """
        读取指定存档的数据，不改变当前活动存档
        
        参数:
            save_name (str): 存档名称
            
        返回:
            dict: 存档数据，读取失败则返回None
        """
        try:
            save_file = os.path.join(self._characters_dir, f"{save_name}.json")
            
            if not os.path.exists(save_file):
                print(f"存档 '{save_name}' 不存在")
                return None
                
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
                # 兼容旧版数据结构
                if "角色数据" in save_data:
                    save_data["attributes"] = save_data.pop("角色数据")
                if "属性类别" in save_data:
                    save_data["attribute_categories"] = save_data.pop("属性类别")
                
                # 确保基本结构完整
                if "attributes" not in save_data:
                    save_data["attributes"] = {}
                if "attribute_categories" not in save_data:
                    save_data["attribute_categories"] = {}
                if "metadata" not in save_data:
                    save_data["metadata"] = {
                        "version": "1.0",
                        "created_at": time.time(),
                        "last_modified": time.time(),
                        "character_name": "",
                        "save_name": save_name,
                        "description": ""
                    }
                    
                return save_data
        except Exception as e:
            print(f"读取存档 '{save_name}' 失败: {str(e)}")
            return None


# 初始化保存管理器
save_manager = SaveManager()

# 下面是公共接口函数，提供给外部模块使用

def configure_save_system(save_dir=None, save_name=None):
    """
    配置存档系统
    
    参数:
        save_dir (str): 存档目录路径
        save_name (str): 存档名称
    
    返回:
        SaveManager: 配置好的存档管理器
    """
    global save_manager
    save_manager = SaveManager(save_dir, save_name)
    return save_manager

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
    return save_manager.update_metadata(key, value)

def get_current_save_data():
    """
    获取当前存档数据
    
    返回:
        dict: 当前存档数据
    """
    return save_manager.get_current_save_data()

def update_save_data(save_data):
    """
    更新存档数据
    
    参数:
        save_data (dict): 新的存档数据
    
    返回:
        bool: 是否更新成功
    """
    return save_manager.update_save_data(save_data)

def get_save_file_path():
    """
    获取当前存档文件的位置
    
    返回:
        str: 存档文件的完整路径
    """
    return save_manager.get_save_file_path()

def read_save_data(save_name):
    """
    读取指定存档的数据，不改变当前活动存档
    
    参数:
        save_name (str): 存档名称
        
    返回:
        dict: 存档数据，读取失败则返回None
    """
    return save_manager.read_save_data(save_name) 