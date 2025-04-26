"""
世界观设定流程控制模块

负责游戏开局时的世界观选择和创建流程
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 导入data_manager功能
from data.data_manager import load_text_data, save_text_data, list_text_data, get_data_path

# 导入角色系统
from character.character_manager import create_attribute, set_attribute, get_attribute

# 导入故事线系统
from storyline.storyline_manager import StorylineManager

class WorldSettingFlow:
    """
    世界观设定流程控制器
    
    负责:
    1. 展示预设世界观选项
    2. 处理用户自定义世界观输入
    3. 使用AI补全世界设定
    4. 保存世界观到角色属性
    """
    
    def __init__(self):
        """初始化世界观设定流程控制器"""
        self.manager = StorylineManager()
        self.selected_world = None
        
    def start(self) -> bool:
        """启动世界观设定流程
        
        Returns:
            bool: 流程是否成功完成
        """
        print("\n===== 世界观设定 =====")
        print("首先，让我们确定游戏世界的背景设定。")
        
        # 显示选项
        return self.show_world_options()
    
    def show_world_options(self) -> bool:
        """展示世界观选择选项
        
        Returns:
            bool: 是否成功选择世界观
        """
        print("\n你可以选择一个预设的世界背景，或者创建自己的世界。")
        
        # 获取预设世界列表
        worlds = self._get_preset_worlds()
        
        # 显示世界选项
        for i, world in enumerate(worlds):
            print(f"[{i+1}] {world['name']} - {world['short_description']}")
            
        # 自定义选项
        custom_option = len(worlds) + 1
        print(f"[{custom_option}] 创建自定义世界")
        
        # 获取用户选择
        try:
            choice = self._get_user_choice(1, custom_option)
            if choice < custom_option:
                # 选择预设世界
                return self.use_preset_world(worlds[choice-1]["id"])
            else:
                # 创建自定义世界
                return self.create_custom_world()
        except Exception as e:
            print(f"选择世界时出错: {str(e)}")
            return False
    
    def _get_preset_worlds(self) -> List[Dict[str, Any]]:
        """获取预设世界观列表
        
        Returns:
            List[Dict]: 包含id, name, short_description的字典列表
        """
        # 使用data_manager获取世界列表
        world_ids = list_text_data("worlds")
        worlds = []
        
        for world_id in world_ids:
            try:
                # 加载世界数据
                world_data = load_text_data("worlds", world_id)
                worlds.append({
                    "id": world_id,
                    "name": world_data.get("name", "未命名世界"),
                    "short_description": world_data.get("short_description", "")
                })
            except Exception as e:
                print(f"加载世界 {world_id} 时出错: {str(e)}")
        
        return worlds
    
    def _get_user_choice(self, min_value: int, max_value: int) -> int:
        """获取用户选择的数字输入
        
        Args:
            min_value: 最小有效值
            max_value: 最大有效值
            
        Returns:
            int: 用户选择的数字
        """
        while True:
            try:
                choice = int(input(f"\n请输入选项编号 ({min_value}-{max_value}): "))
                if min_value <= choice <= max_value:
                    return choice
                print(f"无效的选择，请输入{min_value}-{max_value}之间的数字")
            except ValueError:
                print("请输入有效的数字")
    
    def use_preset_world(self, world_id: str) -> bool:
        """使用预设世界观
        
        Args:
            world_id: 世界观ID
            
        Returns:
            bool: 是否成功设置世界观
        """
        # 加载世界详情
        world_data = load_text_data("worlds", world_id)
        
        if not world_data:
            print(f"错误：无法加载世界 {world_id}")
            return False
            
        # 显示世界详情
        self._display_world_details(world_data)
        
        # 确认选择
        confirm = input("\n是否使用此世界背景？(y/n): ").lower()
        if confirm != 'y':
            return False
            
        # 将世界观保存到角色属性
        self._save_world_to_attributes(world_data)
        print(f"\n已选择世界: {world_data['name']}")
        return True
    
    def _display_world_details(self, world_data: Dict[str, Any]) -> None:
        """展示世界详情
        
        Args:
            world_data: 世界观数据
        """
        print("\n===== 世界详情 =====")
        print(f"名称: {world_data['name']}")
        print(f"\n描述: {world_data.get('full_description', '')}")
        print(f"\n历史: {world_data.get('history', '')}")
        print(f"\n魔法/科技: {world_data.get('magic_system', '')}")
        
        # 显示种族
        races = world_data.get('races', [])
        if races:
            print(f"\n主要种族: {', '.join(races)}")
        
        # 显示一部分势力
        factions = world_data.get('factions', [])
        if factions:
            print("\n主要势力:")
            for faction in factions[:3]:  # 只显示前3个
                print(f"- {faction.get('name')}: {faction.get('description', '')[:100]}...")
            if len(factions) > 3:
                print(f"...以及其他{len(factions)-3}个势力")
    
    def create_custom_world(self) -> bool:
        """创建自定义世界观
        
        Returns:
            bool: 是否成功创建世界观
        """
        print("\n===== 创建自定义世界 =====")
        print("请描述你想要的世界背景，包括世界类型、特点、主要元素等。")
        print("例如：一个科技与魔法并存的后启示录世界，人类与变异生物共存...")
        user_input = input("\n请输入世界描述: ")
        
        if not user_input.strip():
            print("描述为空，取消创建")
            return False
            
        # 设置用户输入
        create_attribute("user_world_input", user_input)
        create_attribute("world_choice", "custom")
        
        # 使用AI生成完整世界观
        print("\n正在生成世界背景...")
        try:
            # 调用世界设定模板，生成完整世界观
            success = self.manager.generate_story("world_setting")
            if not success:
                print("生成世界设定失败")
                return False
            
            # 获取生成结果
            world_data = self._collect_generated_world_data()
            
            # 显示生成结果
            self._display_world_details(world_data)
            print("\n你可以接受这个世界设定，修改部分内容，或者重新生成。")
            
            # 选择操作
            print("\n[1] 接受此世界设定")
            print("[2] 修改此世界设定")
            print("[3] 重新生成")
            print("[4] 取消创建")
            
            choice = self._get_user_choice(1, 4)
            
            if choice == 1:
                # 接受设定
                print(f"\n已创建世界: {world_data['name']}")
                self._ask_save_as_preset(world_data)
                return True
            elif choice == 2:
                # 修改设定
                return self._modify_world_setting(world_data)
            elif choice == 3:
                # 重新生成
                return self.create_custom_world()
            else:
                # 取消创建
                return False
                
        except Exception as e:
            print(f"生成世界背景时出错: {str(e)}")
            return False
    
    def _collect_generated_world_data(self) -> Dict[str, Any]:
        """从角色属性中收集生成的世界观数据
        
        Returns:
            Dict: 世界观数据
        """
        return {
            "name": get_attribute("世界名称") or "未命名世界",
            "full_description": get_attribute("世界描述") or "",
            "history": get_attribute("世界历史") or "",
            "magic_system": get_attribute("魔法系统") or "",
            "races": [r.strip() for r in (get_attribute("主要种族") or "").split(",") if r.strip()],
            "factions": [
                {"name": f.split(":")[0].strip(), "description": f.split(":", 1)[1].strip() if ":" in f else ""}
                for f in (get_attribute("主要势力") or "").split(";") if f.strip()
            ],
            "key_locations": [
                {"name": l.split(":")[0].strip(), "description": l.split(":", 1)[1].strip() if ":" in l else ""}
                for l in (get_attribute("关键地点") or "").split(";") if l.strip()
            ],
            "themes": [t.strip() for t in (get_attribute("主题元素") or "").split(",") if t.strip()],
            "short_description": (get_attribute("世界描述") or "")[:100] + "..." if len(get_attribute("世界描述") or "") > 100 else (get_attribute("世界描述") or "")
        }
    
    def _modify_world_setting(self, world_data: Dict[str, Any]) -> bool:
        """修改生成的世界设定
        
        Args:
            world_data: 当前世界观数据
            
        Returns:
            bool: 修改是否成功
        """
        print("\n===== 修改世界设定 =====")
        print("请修改各个部分（直接回车保持不变）:")
        
        # 修改名称
        new_name = input(f"世界名称 [{world_data['name']}]: ")
        if new_name.strip():
            set_attribute("世界名称", new_name)
            world_data['name'] = new_name
            
        # 修改描述
        print(f"\n当前描述: {world_data['full_description']}")
        new_desc = input("新描述 (直接回车保持不变): ")
        if new_desc.strip():
            set_attribute("世界描述", new_desc)
            world_data['full_description'] = new_desc
            
        # 修改历史
        print(f"\n当前历史: {world_data['history']}")
        new_history = input("新历史 (直接回车保持不变): ")
        if new_history.strip():
            set_attribute("世界历史", new_history)
            world_data['history'] = new_history
            
        # 修改魔法/科技系统
        print(f"\n当前魔法/科技系统: {world_data['magic_system']}")
        new_magic = input("新魔法/科技系统 (直接回车保持不变): ")
        if new_magic.strip():
            set_attribute("魔法系统", new_magic)
            world_data['magic_system'] = new_magic
            
        # 修改种族
        print(f"\n当前种族: {', '.join(world_data['races'])}")
        new_races = input("新种族列表 (用逗号分隔，直接回车保持不变): ")
        if new_races.strip():
            set_attribute("主要种族", new_races)
            world_data['races'] = [r.strip() for r in new_races.split(",") if r.strip()]
        
        print("\n修改已保存。")
        
        # 询问是否保存为预设
        return self._ask_save_as_preset(world_data)
    
    def _ask_save_as_preset(self, world_data: Dict[str, Any]) -> bool:
        """询问是否将自定义世界保存为预设
        
        Args:
            world_data: 世界观数据
            
        Returns:
            bool: 操作是否成功完成
        """
        save_preset = input("是否将此世界保存为预设，以便将来使用？(y/n): ").lower()
        if save_preset == 'y':
            # 生成唯一ID
            world_id = self._generate_world_id(world_data['name'])
            world_data['id'] = world_id
            
            # 保存为预设
            try:
                save_text_data("worlds", world_id, world_data)
                print(f"世界观 '{world_data['name']}' 已保存为预设")
            except Exception as e:
                print(f"保存世界观预设失败: {str(e)}")
        
        return True
    
    def _generate_world_id(self, name: str) -> str:
        """从名称生成世界ID
        
        Args:
            name: 世界名称
            
        Returns:
            str: 生成的ID
        """
        # 转换为小写，去除特殊字符
        base_id = "".join(c if c.isalnum() else "_" for c in name.lower())
        
        # 如果ID已存在，添加数字后缀
        world_ids = list_text_data("worlds")
        if base_id not in world_ids:
            return base_id
            
        # 添加数字后缀
        counter = 1
        while f"{base_id}_{counter}" in world_ids:
            counter += 1
            
        return f"{base_id}_{counter}"
    
    def _save_world_to_attributes(self, world_data: Dict[str, Any]) -> None:
        """将世界观数据保存到角色属性
        
        Args:
            world_data: 世界观数据字典
        """
        # 保存基本信息
        create_attribute("世界", world_data["name"])
        create_attribute("世界名称", world_data["name"])
        create_attribute("世界描述", world_data.get("full_description", ""))
        create_attribute("世界历史", world_data.get("history", ""))
        create_attribute("魔法系统", world_data.get("magic_system", ""))
        
        # 保存种族
        races = world_data.get("races", [])
        if races:
            create_attribute("主要种族", ", ".join(races))
        
        # 保存势力信息
        factions = world_data.get("factions", [])
        if factions:
            faction_str = "; ".join([f"{f.get('name')}: {f.get('description')}" 
                                  for f in factions])
            create_attribute("主要势力", faction_str)
        
        # 保存地点信息
        locations = world_data.get("key_locations", [])
        if locations:
            location_str = "; ".join([f"{l.get('name')}: {l.get('description')}" 
                                   for l in locations])
            create_attribute("关键地点", location_str)
        
        # 保存主题
        themes = world_data.get("themes", [])
        if themes:
            create_attribute("主题元素", ", ".join(themes))
        
        # 保存世界ID用于引用
        create_attribute("world_id", world_data.get("id", "")) 