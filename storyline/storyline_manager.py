"""
故事线管理器

这个模块负责管理故事线模板、生成故事内容和处理分支选择。
它与AI模块和角色属性模块集成，提供完整的故事生成功能。
"""

import os
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Tuple

# 导入AI模块组件
from ai.prompt_processor import PromptProcessor
from ai.api_connector import AIModelConnector
from ai.output_parsers import OutputParser

# 导入角色模块组件
try:
    from character import character_manager
    CHARACTER_MODULE_AVAILABLE = True
except ImportError:
    CHARACTER_MODULE_AVAILABLE = False
    print("警告：未能导入角色模块，角色属性功能将不可用")

@dataclass
class StoryChoice:
    """故事选择选项"""
    id: str  # 选择ID，例如 "choice1"
    text: str  # 选择文本
    outcome: Optional[str] = None  # 选择结果描述（可选）
    stat_changes: Dict[str, int] = field(default_factory=dict)  # 属性变化，例如 {"strength": 2, "agility": -1}
    next_templates: List[str] = field(default_factory=list)  # 可能的下一个模板ID列表
    
    def __str__(self) -> str:
        return self.text

@dataclass
class StorySegment:
    """故事片段，代表一个生成的故事节点"""
    id: str  # 唯一标识符
    template_id: str  # 使用的模板ID
    content: str  # 主要故事内容
    choices: List[StoryChoice] = field(default_factory=list)  # 可用选择
    metadata: Dict[str, Any] = field(default_factory=dict)  # 其他元数据
    parent_id: Optional[str] = None  # 父节点ID（可选）
    
    def to_dict(self) -> Dict[str, Any]:
        """将故事片段转换为字典格式"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "content": self.content,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "outcome": choice.outcome,
                    "stat_changes": choice.stat_changes,
                    "next_templates": choice.next_templates
                }
                for choice in self.choices
            ],
            "metadata": self.metadata,
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorySegment':
        """从字典创建故事片段"""
        choices = [
            StoryChoice(
                id=choice["id"],
                text=choice["text"],
                outcome=choice.get("outcome"),
                stat_changes=choice.get("stat_changes", {}),
                next_templates=choice.get("next_templates", [])
            )
            for choice in data.get("choices", [])
        ]
        
        return cls(
            id=data["id"],
            template_id=data["template_id"],
            content=data["content"],
            choices=choices,
            metadata=data.get("metadata", {}),
            parent_id=data.get("parent_id")
        )

class StorylineManager:
    """故事线管理器，处理模板加载、故事生成和分支选择"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """初始化故事线管理器
        
        Args:
            templates_dir: 模板目录路径，默认使用模块的templates目录
        """
        # 设置模板目录
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # 使用模块默认目录
            from . import TEMPLATES_PATH
            self.templates_dir = TEMPLATES_PATH
        
        # 确保目录存在
        self.templates_dir.mkdir(exist_ok=True)
        
        # 初始化AI组件
        self.prompt_processor = PromptProcessor()
        self.api_connector = AIModelConnector()
        
        # 加载所有模板
        self._templates_cache = {}
        self._load_all_templates()
        
        # 故事片段存储
        self.story_segments = {}
    
    def _load_all_templates(self) -> None:
        """加载所有可用的模板"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template = json.load(f)
                    
                # 存储到缓存
                template_id = template.get("template_id") or template_file.stem
                self._templates_cache[template_id] = template
                
            except Exception as e:
                print(f"加载模板 {template_file.name} 失败: {str(e)}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有可用的模板
        
        Returns:
            模板概要信息列表
        """
        result = []
        for template_id, template in self._templates_cache.items():
            result.append({
                "id": template_id,
                "name": template.get("name", template_id),
                "description": template.get("description", ""),
                "version": template.get("version", "1.0"),
                "tags": template.get("tags", [])
            })
        return result
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """加载特定ID的模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板内容，如果模板不存在则返回None
        """
        # 首先检查缓存
        if template_id in self._templates_cache:
            return self._templates_cache[template_id]
        
        # 尝试从文件加载
        template_path = self.templates_dir / f"{template_id}.json"
        if template_path.exists():
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template = json.load(f)
                
                # 存储到缓存
                self._templates_cache[template_id] = template
                return template
            except Exception as e:
                print(f"加载模板 {template_id} 失败: {str(e)}")
        
        return None
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """保存模板
        
        Args:
            template: 模板内容
            
        Returns:
            保存是否成功
        """
        # 确保模板有ID
        template_id = template.get("template_id")
        if not template_id:
            return False
        
        # 保存到文件
        template_path = self.templates_dir / f"{template_id}.json"
        try:
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            self._templates_cache[template_id] = template
            return True
        except Exception as e:
            print(f"保存模板 {template_id} 失败: {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            删除是否成功
        """
        # 从缓存中移除
        if template_id in self._templates_cache:
            del self._templates_cache[template_id]
        
        # 从文件系统删除
        template_path = self.templates_dir / f"{template_id}.json"
        if template_path.exists():
            try:
                template_path.unlink()
                return True
            except Exception as e:
                print(f"删除模板 {template_id} 失败: {str(e)}")
        
        return False
    
    def _fill_template_variables(self, prompt_segments: List[str], variables: Dict[str, Any]) -> List[str]:
        """填充模板中的变量
        
        Args:
            prompt_segments: 提示片段列表
            variables: 变量字典
            
        Returns:
            填充后的提示片段列表
        """
        result = []
        for segment in prompt_segments:
            # 替换所有变量
            filled_segment = segment
            for var_name, var_value in variables.items():
                placeholder = "{" + var_name + "}"
                if placeholder in filled_segment:
                    filled_segment = filled_segment.replace(placeholder, str(var_value))
            
            result.append(filled_segment)
        
        return result
    
    def generate_story(self, 
                      template: Union[str, Dict[str, Any]], 
                      variables: Optional[Dict[str, Any]] = None,
                      parent_id: Optional[str] = None) -> Optional[StorySegment]:
        """生成故事片段
        
        Args:
            template: 模板ID或模板内容
            variables: 可选的额外变量字典，优先级高于角色属性
            parent_id: 父节点ID（可选）
            
        Returns:
            生成的故事片段，如果生成失败则返回None
        """
        # 加载模板
        if isinstance(template, str):
            template_id = template
            template = self.load_template(template_id)
            if not template:
                print(f"模板 {template_id} 不存在")
                return None
        else:
            template_id = template.get("template_id", "unknown")
        
        # 准备变量 - 从character_manager直接获取所有属性
        final_variables = {}
        if CHARACTER_MODULE_AVAILABLE:
            try:
                # 获取所有角色属性
                all_attributes = character_manager.get_all_attributes()
                final_variables.update(all_attributes)
                
                # 处理嵌套属性访问（例如character.name）
                for attr_name, attr_value in all_attributes.items():
                    # 处理character.xxx格式的属性引用
                    if attr_name in ["name", "background", "strength", "agility", 
                                    "intelligence", "constitution", "charisma", 
                                    "skills", "gender", "equipment"]:
                        final_variables[f"character.{attr_name}"] = attr_value
                    
                    # 处理复杂结构（如装备）的内部属性
                    if attr_name == "equipment" and isinstance(attr_value, dict):
                        for item_name, item_value in attr_value.items():
                            final_variables[f"equipment.{item_name}"] = item_value
            except Exception as e:
                print(f"获取角色属性失败: {str(e)}")
        
        # 如果提供了额外变量，用它们覆盖或补充
        if variables:
            final_variables.update(variables)
            
        # 检查必需输入 - 如果模板仍然指定了required_inputs，确保它们存在
        required_inputs = template.get("required_inputs", [])
        missing_inputs = [input_name for input_name in required_inputs if input_name not in final_variables]
        if missing_inputs:
            print(f"缺少必需的输入: {', '.join(missing_inputs)}")
            # 添加一些默认值
            for input_name in missing_inputs:
                if input_name == "world_setting":
                    final_variables["world_setting"] = "奇幻世界"
                elif input_name == "location":
                    final_variables["location"] = "神秘之地"
                else:
                    final_variables[input_name] = "未知"
        
        # 填充模板变量
        prompt_segments = template.get("prompt_segments", [])
        filled_segments = self._fill_template_variables(prompt_segments, final_variables)
        
        # 检查是否有自定义的提示词模板
        if "prompt_template" in template:
            # 使用模板中的自定义提示词模板
            custom_template = template["prompt_template"]
            custom_processor = PromptProcessor(custom_template)
            prompt = custom_processor.build_prompt(filled_segments)
        else:
            # 使用默认提示词模板
            prompt = self.prompt_processor.build_prompt(filled_segments)
        
        # 调用AI生成内容
        try:
            response = self.api_connector.call_api(prompt)
            result = OutputParser.parse(response)
        except Exception as e:
            print(f"生成故事失败: {str(e)}")
            return None
        
        # 创建故事片段
        story_id = f"story_{int(time.time())}_{template_id}"
        
        # 提取故事内容和选择
        story_content = result.get("story", "")
        
        # 创建选择列表
        choices = []
        for i in range(1, 10):  # 支持最多9个选择
            choice_key = f"choice{i}"
            outcome_key = f"outcome{i}"
            
            if choice_key not in result:
                break
                
            # 创建选择对象
            choice = StoryChoice(
                id=choice_key,
                text=result[choice_key],
                outcome=result.get(outcome_key)
            )
            
            # 处理属性变化
            stat_change_key = f"stat_change{i}"
            if stat_change_key in result:
                # 尝试提取属性变化，格式:"力量+2（通过激烈的战斗提升力量），敏捷+1（剑法实战经验），体质-1（受伤消耗）"
                stat_changes = {}
                try:
                    stat_text = result[stat_change_key]
                    # 分割不同属性的变化
                    changes = stat_text.split("，")
                    for change in changes:
                        # 提取属性名和变化值
                        for attr_name in ["力量", "敏捷", "智力", "体质", "魅力"]:
                            if attr_name in change:
                                # 找到数值变化（+2或-1这样的格式）
                                parts = change.split(attr_name)
                                if len(parts) > 1:
                                    value_part = parts[1].strip()
                                    if value_part.startswith("+") or value_part.startswith("-"):
                                        try:
                                            value = int(value_part[0:2])  # 提取+2或-1这样的值
                                            stat_changes[attr_name] = value
                                        except ValueError:
                                            pass
                except Exception as e:
                    print(f"处理属性变化失败: {str(e)}")
                
                choice.stat_changes = stat_changes
            
            # 添加下一个模板信息
            if "next_templates" in template:
                choice.next_templates = template["next_templates"].get(choice_key, [])
            
            choices.append(choice)
        
        # 创建故事片段
        story_segment = StorySegment(
            id=story_id,
            template_id=template_id,
            content=story_content,
            choices=choices,
            metadata={
                "generated_at": time.time(),
                "variables": final_variables,
                "raw_result": result
            },
            parent_id=parent_id
        )
        
        # 存储故事片段
        self.story_segments[story_id] = story_segment
        
        # 自动将输出直接存储到角色属性中
        if CHARACTER_MODULE_AVAILABLE:
            try:
                # 1. 直接存储生成的结果
                # 故事内容存储为current_story属性
                if "story" in result:
                    self._set_or_create_attribute("current_story", result["story"])
                
                # 格式化的故事内容存储为story_content属性
                self._set_or_create_attribute("story_content", story_content)
                
                # 存储选项内容
                for i, choice in enumerate(choices, 1):
                    self._set_or_create_attribute(f"option{i}", choice.text)
                
                # 2. 应用模板中的存储映射（如果有）
                if "output_storage" in template:
                    for output_field, attr_name in template["output_storage"].items():
                        if output_field in result:
                            self._set_or_create_attribute(attr_name, result[output_field])
                        elif output_field == "content":
                            self._set_or_create_attribute(attr_name, story_content)
            
            except Exception as e:
                print(f"存储输出到角色属性失败: {str(e)}")
        
        return story_segment
    
    def _set_or_create_attribute(self, attr_name: str, value: Any) -> None:
        """设置或创建角色属性
        
        Args:
            attr_name: 属性名
            value: 属性值
        """
        if not CHARACTER_MODULE_AVAILABLE:
            return
            
        try:
            # 检查属性是否已存在
            current_value = character_manager.get_attribute(attr_name)
            if current_value is not None:
                # 更新现有属性
                character_manager.set_attribute(attr_name, value)
                #print(f"更新属性: {attr_name} = {value}")
            else:
                # 创建新属性
                character_manager.create_attribute(attr_name, value)
                #print(f"创建属性: {attr_name} = {value}")
        except Exception as e:
            print(f"设置属性失败 {attr_name}: {str(e)}")
    
    def choose_branch(self, 
                     story: Union[str, StorySegment], 
                     choice_index: int) -> Optional[StoryChoice]:
        """选择故事分支
        
        Args:
            story: 故事片段或故事ID
            choice_index: 选择的索引（从0开始）
            
        Returns:
            选择的分支，如果选择无效则返回None
        """
        # 获取故事片段
        if isinstance(story, str):
            if story not in self.story_segments:
                print(f"故事片段 {story} 不存在")
                return None
            story_segment = self.story_segments[story]
        else:
            story_segment = story
        
        # 检查选择有效性
        if choice_index < 0 or choice_index >= len(story_segment.choices):
            print(f"无效的选择索引: {choice_index}")
            return None
        
        # 返回所选分支
        return story_segment.choices[choice_index]
    
    def continue_story(self, 
                      story: Union[str, StorySegment], 
                      choice_index: int, 
                      variables: Optional[Dict[str, Any]] = None) -> Optional[StorySegment]:
        """基于选择继续故事
        
        Args:
            story: 故事片段或故事ID
            choice_index: 选择的索引（从0开始）
            variables: 可选的额外变量字典，优先级高于角色属性
            
        Returns:
            生成的下一个故事片段，如果继续失败则返回None
        """
        # 获取故事片段
        if isinstance(story, str):
            if story not in self.story_segments:
                print(f"故事片段 {story} 不存在")
                return None
            story_segment = self.story_segments[story]
        else:
            story_segment = story
        
        # 获取选择
        if choice_index < 0 or choice_index >= len(story_segment.choices):
            print(f"无效的选择索引: {choice_index}")
            return None
            
        choice = story_segment.choices[choice_index]
        
        # 获取下一个模板
        next_templates = choice.next_templates
        if not next_templates:
            print("没有可用的后续模板")
            return None
        
        # 选择第一个可用模板
        next_template_id = next_templates[0]
        next_template = self.load_template(next_template_id)
        if not next_template:
            print(f"模板 {next_template_id} 不存在")
            return None
        
        # 准备额外变量 - 主要是previous_story和previous_choice
        extra_vars = {}
        extra_vars["previous_story"] = story_segment.content
        extra_vars["previous_choice"] = choice.text
        
        # 如果提供了额外变量，将其合并
        if variables:
            extra_vars.update(variables)
        
        # 应用选择的属性变化
        if CHARACTER_MODULE_AVAILABLE and choice.stat_changes:
            for attr_name, change_value in choice.stat_changes.items():
                # 尝试更新角色属性
                try:
                    current_value = character_manager.get_attribute(attr_name)
                    if isinstance(current_value, (int, float)):
                        character_manager.set_attribute(attr_name, current_value + change_value)
                        print(f"更新属性 {attr_name}: {current_value} -> {current_value + change_value}")
                except Exception as e:
                    print(f"无法更新属性 {attr_name}: {str(e)}")
        
        # 记录玩家选择的选项索引(从1开始)
        if CHARACTER_MODULE_AVAILABLE:
            self._set_or_create_attribute("last_choice_index", choice_index + 1)
            
        # 生成下一个故事片段
        return self.generate_story(next_template, extra_vars, parent_id=story_segment.id)
    
    def save_story_to_file(self, story: Union[str, StorySegment], filepath: str) -> bool:
        """将故事片段保存到文件
        
        Args:
            story: 故事片段或故事ID
            filepath: 保存路径
            
        Returns:
            保存是否成功
        """
        # 获取故事片段
        if isinstance(story, str):
            if story not in self.story_segments:
                print(f"故事片段 {story} 不存在")
                return False
            story_segment = self.story_segments[story]
        else:
            story_segment = story
        
        # 转换为字典
        story_dict = story_segment.to_dict()
        
        # 保存到文件
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(story_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存故事失败: {str(e)}")
            return False
    
    def load_story_from_file(self, filepath: str) -> Optional[StorySegment]:
        """从文件加载故事片段
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的故事片段，如果加载失败则返回None
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                story_dict = json.load(f)
            
            # 创建故事片段
            story_segment = StorySegment.from_dict(story_dict)
            
            # 存储到管理器
            self.story_segments[story_segment.id] = story_segment
            
            return story_segment
        except Exception as e:
            print(f"加载故事失败: {str(e)}")
            return None 
    
    def generate_story_from_character(self, 
                                     template: Union[str, Dict[str, Any]],
                                     extra_variables: Optional[Dict[str, Any]] = None,
                                     parent_id: Optional[str] = None) -> Optional[StorySegment]:
        """从角色属性生成故事片段（保留用于向后兼容）
        
        Args:
            template: 模板ID或模板内容
            extra_variables: 额外的变量，会覆盖或补充角色属性
            parent_id: 父节点ID（可选）
            
        Returns:
            生成的故事片段，如果生成失败则返回None
        """
        # 直接调用generate_story，已经会自动从character_manager加载属性
        return self.generate_story(template, extra_variables, parent_id)
    
    def continue_story_from_character(self, 
                                     story: Union[str, StorySegment], 
                                     choice_index: int,
                                     extra_variables: Optional[Dict[str, Any]] = None) -> Optional[StorySegment]:
        """基于角色属性和选择继续故事（保留用于向后兼容）
        
        Args:
            story: 故事片段或故事ID
            choice_index: 选择的索引（从0开始）
            extra_variables: 额外的变量，会覆盖或补充角色属性
            
        Returns:
            生成的下一个故事片段，如果继续失败则返回None
        """
        # 直接调用continue_story，已经会自动处理角色属性
        return self.continue_story(story, choice_index, extra_variables)

    def run_template(self, template_id: str, variables: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """运行模板并返回结果（简化API）
        
        Args:
            template_id: 模板ID
            variables: 可选的额外变量字典，优先级高于角色属性
            
        Returns:
            包含故事内容和选择选项的元组 (story_content, choices)
        """
        # 直接生成故事
        story_segment = self.generate_story(template_id, variables)
        
        if not story_segment:
            return "", []
        
        # 转换选择为简单格式
        choices = []
        for i, choice in enumerate(story_segment.choices):
            choices.append({
                "id": i,  # 使用索引作为ID，便于后续选择
                "text": choice.text,
                "outcome": choice.outcome or ""
            })
        
        return story_segment.content, choices
    
    def make_choice(self, story_id: str, choice_index: int, variables: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """执行选择并继续故事（简化API）
        
        Args:
            story_id: 故事片段ID
            choice_index: 选择的索引
            variables: 可选的额外变量字典，优先级高于角色属性
            
        Returns:
            包含故事内容和选择选项的元组 (story_content, choices)
        """
        # 获取故事片段
        if story_id not in self.story_segments:
            return "", []
        story_segment = self.story_segments[story_id]
        
        # 继续故事
        next_segment = self.continue_story(story_segment, choice_index, variables)
        
        if not next_segment:
            return "", []
        
        # 转换选择为简单格式
        choices = []
        for i, choice in enumerate(next_segment.choices):
            choices.append({
                "id": i,
                "text": choice.text,
                "outcome": choice.outcome or ""
            })
        
        return next_segment.content, choices
        
    def run_template_and_store(self, template_id: str, 
                              variables: Optional[Dict[str, Any]] = None,
                              store_fields: Optional[Dict[str, str]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """运行模板并将结果存储到角色属性中（增强API - 向后兼容）
        
        Args:
            template_id: 模板ID
            variables: 可选的额外变量字典，优先级高于角色属性
            store_fields: 需要存储到角色属性中的字段映射，格式为 {输出字段名: 属性名}
                         例如: {"story": "last_story", "choice1": "last_choice"}
            
        Returns:
            包含故事内容和选择选项的元组 (story_content, choices)
        """
        # 简单调用run_template - 存储已经在generate_story中自动进行
        # 如果提供了store_fields，需要将其应用到模板中
        template = self.load_template(template_id)
        if template and store_fields:
            # 临时更新模板的output_storage字段
            original_storage = template.get("output_storage", {})
            template["output_storage"] = {**original_storage, **store_fields}
            
            # 生成故事
            story_segment = self.generate_story(template, variables)
            
            # 恢复原始模板
            if original_storage:
                template["output_storage"] = original_storage
            else:
                template.pop("output_storage", None)
        else:
            # 正常生成故事
            story_segment = self.generate_story(template_id, variables)
        
        if not story_segment:
            return "", []
            
        # 转换选择为简单格式
        choices = []
        for i, choice in enumerate(story_segment.choices):
            choices.append({
                "id": i,
                "text": choice.text,
                "outcome": choice.outcome or ""
            })
        
        return story_segment.content, choices
    
    def make_choice_and_store(self, story_id: str, choice_index: int, 
                             variables: Optional[Dict[str, Any]] = None,
                             store_fields: Optional[Dict[str, str]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """执行选择并将结果存储到角色属性中（增强API - 向后兼容）
        
        Args:
            story_id: 故事片段ID
            choice_index: 选择的索引
            variables: 可选的额外变量字典，优先级高于角色属性
            store_fields: 需要存储到角色属性中的字段映射，格式为 {输出字段名: 属性名}
            
        Returns:
            包含故事内容和选择选项的元组 (story_content, choices)
        """
        # 获取故事片段
        if story_id not in self.story_segments:
            return "", []
        story_segment = self.story_segments[story_id]
        
        # 获取选择
        if choice_index < 0 or choice_index >= len(story_segment.choices):
            return "", []
        choice = story_segment.choices[choice_index]
        
        # 获取下一个模板
        next_templates = choice.next_templates
        if not next_templates:
            return "", []
        
        # 选择第一个可用模板
        next_template_id = next_templates[0]
        next_template = self.load_template(next_template_id)
        if not next_template:
            return "", []
            
        # 如果提供了store_fields，需要将其应用到模板中
        if store_fields:
            # 临时更新模板的output_storage字段
            original_storage = next_template.get("output_storage", {})
            next_template["output_storage"] = {**original_storage, **store_fields}
            
            # 准备额外变量
            extra_vars = {}
            if variables:
                extra_vars.update(variables)
            extra_vars["previous_story"] = story_segment.content
            extra_vars["previous_choice"] = choice.text
            
            # 应用属性变化
            if CHARACTER_MODULE_AVAILABLE and choice.stat_changes:
                for attr_name, change_value in choice.stat_changes.items():
                    try:
                        current_value = character_manager.get_attribute(attr_name)
                        if isinstance(current_value, (int, float)):
                            character_manager.set_attribute(attr_name, current_value + change_value)
                    except:
                        pass
            
            # 生成下一个故事片段
            next_segment = self.generate_story(next_template, extra_vars, parent_id=story_segment.id)
            
            # 恢复原始模板
            if original_storage:
                next_template["output_storage"] = original_storage
            else:
                next_template.pop("output_storage", None)
        else:
            # 正常继续故事
            next_segment = self.continue_story(story_segment, choice_index, variables)
        
        if not next_segment:
            return "", []
        
        # 转换选择为简单格式
        choices = []
        for i, choice in enumerate(next_segment.choices):
            choices.append({
                "id": i,
                "text": choice.text,
                "outcome": choice.outcome or ""
            })
        
        return next_segment.content, choices

    def get_story_content(self, story_id: str) -> str:
        """获取故事内容（简化API）
        
        Args:
            story_id: 故事片段ID
            
        Returns:
            故事内容
        """
        if story_id in self.story_segments:
            return self.story_segments[story_id].content
        return ""
    
    def get_story_choices(self, story_id: str) -> List[Dict[str, Any]]:
        """获取故事选择（简化API）
        
        Args:
            story_id: 故事片段ID
            
        Returns:
            选择选项列表
        """
        if story_id not in self.story_segments:
            return []
        
        story_segment = self.story_segments[story_id]
        choices = []
        for i, choice in enumerate(story_segment.choices):
            choices.append({
                "id": i,
                "text": choice.text,
                "outcome": choice.outcome or ""
            })
        
        return choices