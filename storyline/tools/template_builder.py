"""
故事模板构建命令行工具

这个工具提供命令行界面，用于创建、编辑和管理故事模板。
适合喜欢命令行操作或需要批量处理模板的用户。
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

# 导入storyline模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from storyline import TEMPLATES_PATH
from storyline.storyline_manager import StorylineManager

class TemplateBuilder:
    """模板构建器类，提供命令行界面创建和管理模板"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """初始化模板构建器
        
        Args:
            templates_dir: 模板目录路径，默认使用模块的templates目录
        """
        # 设置模板目录
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = TEMPLATES_PATH
        
        # 确保目录存在
        self.templates_dir.mkdir(exist_ok=True)
        
        # 初始化故事线管理器
        self.manager = StorylineManager(templates_dir=str(self.templates_dir))
    
    def list_templates(self) -> None:
        """列出所有可用模板"""
        templates = self.manager.list_templates()
        
        if not templates:
            print("没有可用的模板")
            return
        
        # 打印表头
        print(f"{'ID':<20} {'名称':<30} {'版本':<10} {'标签':<30}")
        print("-" * 90)
        
        # 打印模板信息
        for template in templates:
            tags = ", ".join(template.get("tags", []))
            print(f"{template['id']:<20} {template['name']:<30} {template['version']:<10} {tags:<30}")
    
    def show_template(self, template_id: str) -> None:
        """显示模板详情
        
        Args:
            template_id: 模板ID
        """
        template = self.manager.load_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return
        
        # 打印基本信息
        print(f"模板ID: {template['template_id']}")
        print(f"名称: {template['name']}")
        print(f"描述: {template.get('description', '')}")
        print(f"版本: {template.get('version', '1.0')}")
        print(f"作者: {template.get('author', '')}")
        print(f"创建日期: {template.get('created_at', '')}")
        print(f"标签: {', '.join(template.get('tags', []))}")
        
        # 打印提示片段
        print("\n提示片段:")
        for i, segment in enumerate(template.get("prompt_segments", []), 1):
            print(f"  {i}. {segment}")
        
        # 打印必需输入
        print("\n必需输入变量:")
        for i, input_name in enumerate(template.get("required_inputs", []), 1):
            print(f"  {i}. {input_name}")
        
        # 打印输出格式
        print("\n输出格式:")
        for key, type_info in template.get("output_format", {}).items():
            print(f"  {key}: {type_info}")
        
        # 打印下一步模板
        print("\n下一步模板链接:")
        for choice_id, templates in template.get("next_templates", {}).items():
            print(f"  {choice_id}: {', '.join(templates)}")
    
    def create_template(self, output_file: Optional[str] = None) -> None:
        """交互式创建新模板
        
        Args:
            output_file: 输出文件路径，默认为 templates/{template_id}.json
        """
        print("创建新模板")
        print("=========")
        
        # 基本信息
        template_id = input("模板ID: ").strip()
        if not template_id:
            print("模板ID不能为空")
            return
        
        # 检查是否已存在
        if self.manager.load_template(template_id):
            override = input(f"模板 {template_id} 已存在，是否覆盖? (y/N): ").strip().lower()
            if override != 'y':
                print("已取消创建")
                return
        
        # 创建模板
        template = {
            "template_id": template_id,
            "name": input("模板名称: ").strip(),
            "description": input("描述: ").strip(),
            "version": input("版本 (默认 1.0): ").strip() or "1.0",
            "author": input("作者: ").strip(),
            "created_at": input(f"创建日期 (默认 {time.strftime('%Y-%m-%d')}): ").strip() or time.strftime("%Y-%m-%d"),
            "prompt_segments": [],
            "required_inputs": [],
            "output_format": {},
            "next_templates": {}
        }
        
        # 标签
        tags_input = input("标签 (以逗号分隔): ").strip()
        if tags_input:
            template["tags"] = [tag.strip() for tag in tags_input.split(",")]
        
        # 添加提示片段
        print("\n添加提示片段 (输入空行结束)")
        print("提示: 使用 (内容) 表示背景信息，<内容> 表示内容指令，{key=\"*\"} 表示输出格式")
        while True:
            segment = input("片段: ").strip()
            if not segment:
                break
            template["prompt_segments"].append(segment)
        
        # 添加必需输入
        print("\n添加必需输入变量 (输入空行结束)")
        print("提示: 使用点表示层级关系，如 character.name")
        while True:
            input_name = input("输入变量: ").strip()
            if not input_name:
                break
            template["required_inputs"].append(input_name)
        
        # 添加输出格式
        print("\n添加输出格式定义 (输入空行结束)")
        print("提示: 格式为 key:type，如 story:string")
        while True:
            output_def = input("输出定义: ").strip()
            if not output_def:
                break
            
            try:
                key, type_info = output_def.split(":", 1)
                template["output_format"][key.strip()] = type_info.strip()
            except ValueError:
                print("格式错误，应为 key:type")
        
        # 添加下一步模板
        print("\n添加下一步模板链接 (输入空行结束)")
        print("提示: 格式为 choice_id:template1,template2，如 choice1:combat_template,puzzle_template")
        while True:
            link_def = input("模板链接: ").strip()
            if not link_def:
                break
            
            try:
                choice_id, templates_str = link_def.split(":", 1)
                templates = [t.strip() for t in templates_str.split(",")]
                template["next_templates"][choice_id.strip()] = templates
            except ValueError:
                print("格式错误，应为 choice_id:template1,template2")
        
        # 保存模板
        if output_file:
            file_path = output_file
        else:
            file_path = self.templates_dir / f"{template_id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"\n模板已保存到 {file_path}")
        except Exception as e:
            print(f"\n保存模板失败: {str(e)}")
    
    def delete_template(self, template_id: str) -> None:
        """删除模板
        
        Args:
            template_id: 模板ID
        """
        if not self.manager.load_template(template_id):
            print(f"模板 {template_id} 不存在")
            return
        
        confirm = input(f"确定要删除模板 {template_id} 吗? 此操作不可撤销 (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消删除")
            return
        
        if self.manager.delete_template(template_id):
            print(f"模板 {template_id} 已删除")
        else:
            print(f"删除模板 {template_id} 失败")
    
    def export_template(self, template_id: str, output_file: str) -> None:
        """导出模板到文件
        
        Args:
            template_id: 模板ID
            output_file: 输出文件路径
        """
        template = self.manager.load_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"模板已导出到 {output_file}")
        except Exception as e:
            print(f"导出模板失败: {str(e)}")
    
    def import_template(self, input_file: str) -> None:
        """从文件导入模板
        
        Args:
            input_file: 输入文件路径
        """
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            # 验证模板
            if "template_id" not in template or "prompt_segments" not in template:
                print("导入的文件不是有效的模板格式")
                return
            
            # 保存模板
            template_id = template["template_id"]
            
            # 检查是否已存在
            if self.manager.load_template(template_id):
                override = input(f"模板 {template_id} 已存在，是否覆盖? (y/N): ").strip().lower()
                if override != 'y':
                    print("已取消导入")
                    return
            
            if self.manager.save_template(template):
                print(f"模板 {template_id} 已导入")
            else:
                print(f"导入模板失败")
        except Exception as e:
            print(f"导入模板失败: {str(e)}")
    
    def validate_template(self, template_id: str) -> None:
        """验证模板格式
        
        Args:
            template_id: 模板ID
        """
        template = self.manager.load_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return
        
        # 检查必需字段
        required_fields = ["template_id", "name", "prompt_segments"]
        missing_fields = [field for field in required_fields if field not in template]
        
        if missing_fields:
            print(f"模板缺少必需字段: {', '.join(missing_fields)}")
            return
        
        # 检查提示片段
        if not template["prompt_segments"]:
            print("提示片段列表不能为空")
            return
        
        # 检查输出格式
        if not template.get("output_format"):
            print("输出格式不能为空")
            return
        
        # 检查下一步模板
        if "next_templates" in template:
            invalid_choices = []
            for choice_id, templates in template["next_templates"].items():
                if not isinstance(templates, list):
                    invalid_choices.append(choice_id)
            
            if invalid_choices:
                print(f"下一步模板格式错误: {', '.join(invalid_choices)}")
                return
        
        print(f"模板 {template_id} 格式验证通过")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="故事模板构建工具")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出所有模板")
    
    # show命令
    show_parser = subparsers.add_parser("show", help="显示模板详情")
    show_parser.add_argument("template_id", help="模板ID")
    
    # create命令
    create_parser = subparsers.add_parser("create", help="创建新模板")
    create_parser.add_argument("-o", "--output", help="输出文件路径")
    
    # delete命令
    delete_parser = subparsers.add_parser("delete", help="删除模板")
    delete_parser.add_argument("template_id", help="模板ID")
    
    # export命令
    export_parser = subparsers.add_parser("export", help="导出模板到文件")
    export_parser.add_argument("template_id", help="模板ID")
    export_parser.add_argument("output_file", help="输出文件路径")
    
    # import命令
    import_parser = subparsers.add_parser("import", help="从文件导入模板")
    import_parser.add_argument("input_file", help="输入文件路径")
    
    # validate命令
    validate_parser = subparsers.add_parser("validate", help="验证模板格式")
    validate_parser.add_argument("template_id", help="模板ID")
    
    # 通用参数
    parser.add_argument("--templates-dir", help="模板目录路径")
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 创建模板构建器
    builder = TemplateBuilder(templates_dir=args.templates_dir)
    
    # 处理命令
    if args.command == "list":
        builder.list_templates()
    elif args.command == "show":
        builder.show_template(args.template_id)
    elif args.command == "create":
        builder.create_template(args.output)
    elif args.command == "delete":
        builder.delete_template(args.template_id)
    elif args.command == "export":
        builder.export_template(args.template_id, args.output_file)
    elif args.command == "import":
        builder.import_template(args.input_file)
    elif args.command == "validate":
        builder.validate_template(args.template_id)
    else:
        print("请指定命令，使用 -h 或 --help 查看帮助")

if __name__ == "__main__":
    main() 