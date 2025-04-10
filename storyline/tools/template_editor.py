"""
故事模板编辑工具

这个工具提供了图形界面和命令行界面，
用于创建、编辑和管理故事模板。
"""

import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

# 导入storyline模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from storyline import TEMPLATES_PATH
from storyline.storyline_manager import StorylineManager

# 导入character模块
try:
    from character.character_manager import get_all_attributes, list_attributes, get_attribute, list_categories, get_attributes_by_category, get_attribute_category
    from character.character_manager import set_attribute, delete_attribute, create_attribute, configure_save_system, get_save_location
    CHARACTER_MODULE_AVAILABLE = True
except ImportError:
    CHARACTER_MODULE_AVAILABLE = False
    print("警告：未能导入角色模块，角色属性功能将不可用")

# 导入AI模块
try:
    from ai.prompt_processor import PromptProcessor
    from ai.config import DEFAULT_PROMPT_TEMPLATE
    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False
    print("警告：未能导入AI模块，提示词处理功能将不可用")

class TemplateEditor:
    """模板编辑器类，提供图形界面编辑模板"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """初始化模板编辑器
        
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
        
        # 当前编辑的模板
        self.current_template: Optional[Dict[str, Any]] = None
        self.current_template_path: Optional[Path] = None
        
        # GUI组件
        self.root: Optional[tk.Tk] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.template_tree: Optional[ttk.Treeview] = None
        self.template_info_frame: Optional[ttk.Frame] = None
        self.segments_frame: Optional[ttk.Frame] = None
        self.segments_list: Optional[tk.Listbox] = None
        self.inputs_list: Optional[tk.Listbox] = None
        self.outputs_list: Optional[tk.Listbox] = None
        self.save_button: Optional[ttk.Button] = None
        self.character_attributes_tree: Optional[ttk.Treeview] = None
        
        # 存档相关
        self.save_file_var = None
        self.attribute_editor_tree = None
    
    def run(self) -> None:
        """启动模板编辑器图形界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("故事模板编辑器")
        self.root.geometry("1200x800")
        
        # 初始化Tkinter变量
        self.save_file_var = tk.StringVar(self.root)
        
        # 创建主分割面板
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 模板列表
        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)
        
        # 右侧面板 - 模板编辑
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # 设置左侧模板列表
        self._setup_template_list(left_frame)
        
        # 设置右侧编辑区域
        self._setup_editor(right_frame)
        
        # 加载模板
        self._refresh_template_list()
        
        # 更新当前存档信息
        if CHARACTER_MODULE_AVAILABLE:
            self._update_current_save_info()
        
        # 运行主循环
        self.root.mainloop()
    
    def _setup_template_list(self, parent: ttk.Frame) -> None:
        """设置模板列表区域
        
        Args:
            parent: 父容器
        """
        # 标题
        title_label = ttk.Label(parent, text="可用模板", font=("Arial", 12, "bold"))
        title_label.pack(pady=5, anchor=tk.W)
        
        # 操作按钮
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        new_btn = ttk.Button(buttons_frame, text="新建", command=self._create_new_template)
        new_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_btn = ttk.Button(buttons_frame, text="刷新", command=self._refresh_template_list)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        import_btn = ttk.Button(buttons_frame, text="导入", command=self._import_template)
        import_btn.pack(side=tk.LEFT, padx=2)
        
        # 模板列表
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("id", "name", "version")
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列
        self.template_tree.heading("id", text="ID")
        self.template_tree.heading("name", text="名称")
        self.template_tree.heading("version", text="版本")
        
        self.template_tree.column("id", width=100)
        self.template_tree.column("name", width=150)
        self.template_tree.column("version", width=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        self.template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.template_tree.bind("<<TreeviewSelect>>", self._on_template_select)
        
        # 右键菜单
        self._setup_context_menu()
    
    def _setup_context_menu(self) -> None:
        """设置右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="编辑", command=self._edit_selected_template)
        menu.add_command(label="复制", command=self._duplicate_template)
        menu.add_command(label="导出", command=self._export_template)
        menu.add_separator()
        menu.add_command(label="删除", command=self._delete_template)
        
        def show_menu(event):
            if self.template_tree.selection():
                menu.post(event.x_root, event.y_root)
        
        self.template_tree.bind("<Button-3>", show_menu)
    
    def _setup_editor(self, parent: ttk.Frame) -> None:
        """设置编辑区域
        
        Args:
            parent: 父容器
        """
        # 创建选项卡
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息选项卡
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="基本信息")
        self._setup_info_tab(info_tab)
        
        # 提示片段选项卡
        segments_tab = ttk.Frame(self.notebook)
        self.notebook.add(segments_tab, text="提示片段")
        self._setup_segments_tab(segments_tab)
        
        # 输入/输出选项卡
        io_tab = ttk.Frame(self.notebook)
        self.notebook.add(io_tab, text="输入/输出")
        self._setup_io_tab(io_tab)
        
        # 链接选项卡
        links_tab = ttk.Frame(self.notebook)
        self.notebook.add(links_tab, text="模板链接")
        self._setup_links_tab(links_tab)
        
        # 输出存储选项卡 (新增)
        if CHARACTER_MODULE_AVAILABLE:
            storage_tab = ttk.Frame(self.notebook)
            self.notebook.add(storage_tab, text="输出存储")
            self._setup_storage_tab(storage_tab)
        
        # 角色属性选项卡 (新增)
        if CHARACTER_MODULE_AVAILABLE:
            character_tab = ttk.Frame(self.notebook)
            self.notebook.add(character_tab, text="角色属性")
            self._setup_character_tab(character_tab)
            
            # 存档管理选项卡 (新增)
            save_tab = ttk.Frame(self.notebook)
            self.notebook.add(save_tab, text="存档管理")
            self._setup_save_tab(save_tab)
            
        # 提示词处理选项卡 (新增)
        if AI_MODULE_AVAILABLE:
            prompt_tab = ttk.Frame(self.notebook)
            self.notebook.add(prompt_tab, text="提示词处理")
            self._setup_prompt_processor_tab(prompt_tab)
        
        # 预览选项卡
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="JSON预览")
        self._setup_preview_tab(preview_tab)
        
        # 底部按钮
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.save_button = ttk.Button(buttons_frame, text="保存模板", command=self._save_template)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        self.save_button.configure(state=tk.DISABLED)
        
        validate_btn = ttk.Button(buttons_frame, text="验证模板", command=self._validate_template)
        validate_btn.pack(side=tk.RIGHT, padx=5)
    
    def _setup_info_tab(self, parent: ttk.Frame) -> None:
        """设置基本信息选项卡
        
        Args:
            parent: 父容器
        """
        self.template_info_frame = ttk.Frame(parent)
        self.template_info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建字段
        fields = [
            ("template_id", "模板ID:", ""),
            ("name", "模板名称:", ""),
            ("description", "描述:", ""),
            ("version", "版本:", "1.0"),
            ("author", "作者:", ""),
            ("created_at", "创建日期:", time.strftime("%Y-%m-%d"))
        ]
        
        # 动态创建输入框和标签
        self.info_entries = {}
        row = 0
        
        for field_id, label_text, default_value in fields:
            # 创建标签
            label = ttk.Label(self.template_info_frame, text=label_text)
            label.grid(row=row, column=0, sticky=tk.W, pady=5)
            
            # 创建输入框
            if field_id == "description":
                entry = scrolledtext.ScrolledText(self.template_info_frame, height=4, width=40)
                entry.insert(tk.END, default_value)
                entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
            else:
                entry = ttk.Entry(self.template_info_frame, width=40)
                entry.insert(0, default_value)
                entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
            
            self.info_entries[field_id] = entry
            row += 1
        
        # 标签输入
        label = ttk.Label(self.template_info_frame, text="标签:")
        label.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        self.tags_entry = ttk.Entry(self.template_info_frame, width=40)
        self.tags_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        ttk.Label(self.template_info_frame, text="多个标签请用逗号分隔").grid(row=row, column=2, sticky=tk.W, padx=5)
        
        # 配置列宽
        self.template_info_frame.columnconfigure(1, weight=1)
    
    def _setup_segments_tab(self, parent: ttk.Frame) -> None:
        """设置提示片段选项卡
        
        Args:
            parent: 父容器
        """
        self.segments_frame = ttk.Frame(parent)
        self.segments_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧 - 片段列表
        left_frame = ttk.Frame(self.segments_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="提示片段列表:").pack(anchor=tk.W, pady=(0, 5))
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.segments_list = tk.Listbox(list_frame, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.segments_list.yview)
        self.segments_list.configure(yscrollcommand=scrollbar.set)
        
        self.segments_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.segments_list.bind("<<ListboxSelect>>", self._on_segment_select)
        
        # 按钮
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="上移", command=lambda: self._move_segment(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="下移", command=lambda: self._move_segment(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="删除", command=self._delete_segment).pack(side=tk.LEFT, padx=2)
        
        # 右侧 - 编辑区域
        right_frame = ttk.Frame(self.segments_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="编辑片段:").pack(anchor=tk.W, pady=(0, 5))
        
        # 片段类型选择
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="片段类型:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.segment_type = tk.StringVar(value="background")
        
        ttk.Radiobutton(type_frame, text="背景信息", variable=self.segment_type, 
                        value="background").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="内容指令", variable=self.segment_type, 
                        value="content").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="输出格式", variable=self.segment_type, 
                        value="format").pack(side=tk.LEFT, padx=5)
        
        # 片段内容编辑
        ttk.Label(right_frame, text="片段内容:").pack(anchor=tk.W, pady=(5, 0))
        
        self.segment_text = scrolledtext.ScrolledText(right_frame, height=10)
        self.segment_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加片段按钮
        ttk.Button(right_frame, text="添加/更新片段", command=self._add_update_segment).pack(anchor=tk.E, pady=5)
        
        # 帮助文本
        help_frame = ttk.LabelFrame(right_frame, text="模板语法帮助")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "1. 背景信息: 使用 (内容) 格式，例如 (世界设定: {world_setting})\n"
            "2. 内容指令: 使用 <内容> 格式，例如 <描述一段在{location}的冒险>\n"
            "3. 输出格式: 使用 {key=\"*\"} 格式，例如 {story=\"*\"}\n"
            "4. 变量占位符: 使用 {变量名} 格式，例如 {character.name}"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
    
    def _setup_io_tab(self, parent: ttk.Frame) -> None:
        """设置输入/输出选项卡
        
        Args:
            parent: 父容器
        """
        io_frame = ttk.Frame(parent)
        io_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 分成左右两部分
        paned = ttk.PanedWindow(io_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 必需输入
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="必需输入变量:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        inputs_frame = ttk.Frame(left_frame)
        inputs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.inputs_list = tk.Listbox(inputs_frame)
        scrollbar = ttk.Scrollbar(inputs_frame, orient=tk.VERTICAL, command=self.inputs_list.yview)
        self.inputs_list.configure(yscrollcommand=scrollbar.set)
        
        self.inputs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 输入变量操作
        input_ops_frame = ttk.Frame(left_frame)
        input_ops_frame.pack(fill=tk.X, pady=5)
        
        self.input_var = ttk.Entry(input_ops_frame)
        self.input_var.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(input_ops_frame, text="添加", command=self._add_input).pack(side=tk.LEFT)
        ttk.Button(input_ops_frame, text="删除", command=self._delete_input).pack(side=tk.LEFT, padx=5)
        
        # 输入变量提示
        ttk.Label(left_frame, text="提示: 使用点表示层级关系，如 character.name").pack(anchor=tk.W, pady=5)
        
        # 右侧 - 输出格式
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="输出格式定义:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        outputs_frame = ttk.Frame(right_frame)
        outputs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.outputs_list = tk.Listbox(outputs_frame)
        scrollbar = ttk.Scrollbar(outputs_frame, orient=tk.VERTICAL, command=self.outputs_list.yview)
        self.outputs_list.configure(yscrollcommand=scrollbar.set)
        
        self.outputs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 输出字段操作
        output_ops_frame = ttk.Frame(right_frame)
        output_ops_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_ops_frame, text="字段:").pack(side=tk.LEFT)
        self.output_key = ttk.Entry(output_ops_frame, width=15)
        self.output_key.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(output_ops_frame, text="类型:").pack(side=tk.LEFT)
        self.output_type = ttk.Combobox(output_ops_frame, values=["string", "number", "boolean", "array", "object"], width=10)
        self.output_type.current(0)
        self.output_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(output_ops_frame, text="添加", command=self._add_output).pack(side=tk.LEFT)
        ttk.Button(output_ops_frame, text="删除", command=self._delete_output).pack(side=tk.LEFT, padx=5)
    
    def _setup_links_tab(self, parent: ttk.Frame) -> None:
        """设置模板链接选项卡
        
        Args:
            parent: 父容器
        """
        links_frame = ttk.Frame(parent)
        links_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(links_frame, text="下一步模板链接设置:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 解释文本
        explanation = "在这里设置每个选择可能链接到的下一个模板。例如，choice1可以链接到combat_template或puzzle_template。"
        ttk.Label(links_frame, text=explanation, wraplength=600).pack(anchor=tk.W, pady=(0, 10))
        
        # 选择和模板链接表格
        self.links_frame = ttk.Frame(links_frame)
        self.links_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表头
        headers_frame = ttk.Frame(self.links_frame)
        headers_frame.pack(fill=tk.X)
        
        ttk.Label(headers_frame, text="选择ID", width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="可能的下一步模板 (用逗号分隔多个模板)").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 链接编辑区
        self.links_editor_frame = ttk.Frame(self.links_frame)
        self.links_editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加三个默认选择链接
        self.link_entries = {}
        for i in range(1, 4):
            choice_id = f"choice{i}"
            self._add_link_row(choice_id)
        
        # 添加链接按钮
        buttons_frame = ttk.Frame(links_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.new_choice_id = ttk.Entry(buttons_frame, width=15)
        self.new_choice_id.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="添加选择链接", command=self._add_new_link).pack(side=tk.LEFT)
    
    def _add_link_row(self, choice_id: str, templates: List[str] = None) -> None:
        """添加模板链接行
        
        Args:
            choice_id: 选择ID
            templates: 链接模板列表
        """
        row_frame = ttk.Frame(self.links_editor_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(row_frame, text=choice_id, width=15).pack(side=tk.LEFT, padx=5)
        
        entry = ttk.Entry(row_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        if templates:
            entry.insert(0, ", ".join(templates))
        
        self.link_entries[choice_id] = entry
        
        ttk.Button(row_frame, text="删除", command=lambda: self._delete_link_row(choice_id, row_frame)).pack(side=tk.RIGHT, padx=5)
    
    def _delete_link_row(self, choice_id: str, row_frame: ttk.Frame) -> None:
        """删除模板链接行
        
        Args:
            choice_id: 选择ID
            row_frame: 行框架
        """
        if choice_id in self.link_entries:
            del self.link_entries[choice_id]
        row_frame.destroy()
    
    def _add_new_link(self) -> None:
        """添加新的选择链接"""
        choice_id = self.new_choice_id.get().strip()
        if not choice_id:
            messagebox.showwarning("输入错误", "请输入选择ID")
            return
        
        if choice_id in self.link_entries:
            messagebox.showwarning("重复输入", f"选择 {choice_id} 已存在")
            return
        
        self._add_link_row(choice_id)
        self.new_choice_id.delete(0, tk.END)
    
    def _setup_preview_tab(self, parent: ttk.Frame) -> None:
        """设置JSON预览选项卡
        
        Args:
            parent: 父容器
        """
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(preview_frame, text="模板JSON预览:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # 预览文本框
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=30)
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 刷新按钮
        ttk.Button(preview_frame, text="刷新预览", command=self._refresh_preview).pack(anchor=tk.E, pady=5)
    
    def _refresh_template_list(self) -> None:
        """刷新模板列表"""
        # 清空当前列表
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # 加载模板列表
        templates = self.manager.list_templates()
        
        for template in templates:
            self.template_tree.insert(
                "",
                tk.END,
                values=(template["id"], template["name"], template["version"])
            )
    
    def _on_template_select(self, event) -> None:
        """处理模板选择事件
        
        Args:
            event: 事件对象
        """
        selection = self.template_tree.selection()
        if not selection:
            return
        
        # 获取选中的模板ID
        item = selection[0]
        template_id = self.template_tree.item(item, "values")[0]
        
        # 加载模板
        self._load_template(template_id)
    
    def _load_template(self, template_id: str) -> None:
        """加载模板到编辑器
        
        Args:
            template_id: 模板ID
        """
        template = self.manager.load_template(template_id)
        if not template:
            messagebox.showerror("错误", f"无法加载模板 {template_id}")
            return
        
        # 保存当前模板
        self.current_template = template
        
        # 更新基本信息
        self._update_info_fields(template)
        
        # 更新提示片段
        self._update_segments_list(template)
        
        # 更新输入/输出
        self._update_io_fields(template)
        
        # 更新模板链接
        self._update_links(template)
        
        # 更新存储映射（如果存在）
        if hasattr(self, 'storage_entries'):
            self._update_storage_mapping(template)
        
        # 更新提示词模板（如果存在）
        if hasattr(self, 'template_text') and "prompt_template" in template:
            self.template_text.delete("1.0", tk.END)
            self.template_text.insert(tk.END, template["prompt_template"])
        
        # 更新预览
        self._refresh_preview()
        
        # 启用保存按钮
        self.save_button.configure(state=tk.NORMAL)
    
    def _update_info_fields(self, template: Dict[str, Any]) -> None:
        """更新基本信息字段
        
        Args:
            template: 模板数据
        """
        # 清空现有数据
        for field_id, entry in self.info_entries.items():
            if isinstance(entry, scrolledtext.ScrolledText):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
        
        # 填充数据
        for field_id, entry in self.info_entries.items():
            if field_id in template:
                if isinstance(entry, scrolledtext.ScrolledText):
                    entry.insert(tk.END, template[field_id])
                else:
                    entry.insert(0, template[field_id])
        
        # 更新标签
        self.tags_entry.delete(0, tk.END)
        if "tags" in template:
            self.tags_entry.insert(0, ", ".join(template["tags"]))
    
    def _update_segments_list(self, template: Dict[str, Any]) -> None:
        """更新提示片段列表
        
        Args:
            template: 模板数据
        """
        # 清空片段列表
        self.segments_list.delete(0, tk.END)
        
        # 添加片段
        if "prompt_segments" in template:
            for segment in template["prompt_segments"]:
                self.segments_list.insert(tk.END, segment)
    
    def _update_io_fields(self, template: Dict[str, Any]) -> None:
        """更新输入/输出字段
        
        Args:
            template: 模板数据
        """
        # 清空输入列表
        self.inputs_list.delete(0, tk.END)
        
        # 添加输入
        if "required_inputs" in template:
            for input_name in template["required_inputs"]:
                self.inputs_list.insert(tk.END, input_name)
        
        # 清空输出列表
        self.outputs_list.delete(0, tk.END)
        
        # 添加输出
        if "output_format" in template:
            for key, type_info in template["output_format"].items():
                self.outputs_list.insert(tk.END, f"{key}: {type_info}")
    
    def _update_links(self, template: Dict[str, Any]) -> None:
        """更新模板链接
        
        Args:
            template: 模板数据
        """
        # 清空现有链接
        for widget in self.links_editor_frame.winfo_children():
            widget.destroy()
        self.link_entries = {}
        
        # 添加链接
        if "next_templates" in template:
            for choice_id, templates in template["next_templates"].items():
                self._add_link_row(choice_id, templates)
        else:
            # 添加三个默认选择
            for i in range(1, 4):
                self._add_link_row(f"choice{i}")
    
    def _on_segment_select(self, event) -> None:
        """处理片段选择事件
        
        Args:
            event: 事件对象
        """
        selection = self.segments_list.curselection()
        if not selection:
            return
        
        # 获取选择的片段
        index = selection[0]
        segment = self.segments_list.get(index)
        
        # 更新编辑区域
        self.segment_text.delete("1.0", tk.END)
        self.segment_text.insert(tk.END, segment)
        
        # 设置片段类型
        if segment.startswith("(") and segment.endswith(")"):
            self.segment_type.set("background")
        elif segment.startswith("<") and segment.endswith(">"):
            self.segment_type.set("content")
        elif segment.startswith("{") and segment.endswith("}"):
            self.segment_type.set("format")
    
    def _add_update_segment(self) -> None:
        """添加或更新提示片段"""
        # 获取片段内容
        segment_text = self.segment_text.get("1.0", tk.END).strip()
        if not segment_text:
            messagebox.showwarning("输入错误", "片段内容不能为空")
            return
        
        # 根据类型添加包装符号
        segment_type = self.segment_type.get()
        
        if segment_type == "background":
            if not segment_text.startswith("("):
                segment_text = "(" + segment_text
            if not segment_text.endswith(")"):
                segment_text = segment_text + ")"
        elif segment_type == "content":
            if not segment_text.startswith("<"):
                segment_text = "<" + segment_text
            if not segment_text.endswith(">"):
                segment_text = segment_text + ">"
        elif segment_type == "format":
            if not segment_text.startswith("{"):
                segment_text = "{" + segment_text
            if not segment_text.endswith("}"):
                segment_text = segment_text + "}"
        
        # 检查是新增还是更新
        selection = self.segments_list.curselection()
        if selection:
            # 更新现有片段
            index = selection[0]
            self.segments_list.delete(index)
            self.segments_list.insert(index, segment_text)
            self.segments_list.selection_set(index)
        else:
            # 添加新片段
            self.segments_list.insert(tk.END, segment_text)
            self.segments_list.selection_set(tk.END)
        
        # 清空编辑框
        self.segment_text.delete("1.0", tk.END)
    
    def _move_segment(self, direction: int) -> None:
        """移动提示片段
        
        Args:
            direction: 移动方向，-1表示上移，1表示下移
        """
        selection = self.segments_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        new_index = index + direction
        
        # 检查边界
        if new_index < 0 or new_index >= self.segments_list.size():
            return
        
        # 获取片段
        segment = self.segments_list.get(index)
        
        # 删除原片段并插入到新位置
        self.segments_list.delete(index)
        self.segments_list.insert(new_index, segment)
        
        # 选中新位置
        self.segments_list.selection_clear(0, tk.END)
        self.segments_list.selection_set(new_index)
    
    def _delete_segment(self) -> None:
        """删除选中的提示片段"""
        selection = self.segments_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.segments_list.delete(index)
    
    def _add_input(self) -> None:
        """添加输入变量"""
        input_name = self.input_var.get().strip()
        if not input_name:
            messagebox.showwarning("输入错误", "输入变量名不能为空")
            return
        
        # 检查是否已存在
        existing_inputs = self.inputs_list.get(0, tk.END)
        if input_name in existing_inputs:
            messagebox.showwarning("重复输入", f"输入变量 {input_name} 已存在")
            return
        
        # 添加到列表
        self.inputs_list.insert(tk.END, input_name)
        
        # 清空输入框
        self.input_var.delete(0, tk.END)
    
    def _delete_input(self) -> None:
        """删除选中的输入变量"""
        selection = self.inputs_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.inputs_list.delete(index)
    
    def _add_output(self) -> None:
        """添加输出字段"""
        key = self.output_key.get().strip()
        type_info = self.output_type.get()
        
        if not key:
            messagebox.showwarning("输入错误", "输出字段名不能为空")
            return
        
        # 检查是否已存在
        existing_outputs = [item.split(":")[0].strip() for item in self.outputs_list.get(0, tk.END)]
        if key in existing_outputs:
            messagebox.showwarning("重复输入", f"输出字段 {key} 已存在")
            return
        
        # 添加到列表
        self.outputs_list.insert(tk.END, f"{key}: {type_info}")
        
        # 清空输入框
        self.output_key.delete(0, tk.END)
    
    def _delete_output(self) -> None:
        """删除选中的输出字段"""
        selection = self.outputs_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.outputs_list.delete(index)
    
    def _refresh_preview(self) -> None:
        """刷新JSON预览"""
        # 构建模板数据
        template = self._build_template_data()
        
        # 更新预览
        self.preview_text.delete("1.0", tk.END)
        
        if template:
            # 格式化JSON
            try:
                json_text = json.dumps(template, indent=2, ensure_ascii=False)
                self.preview_text.insert(tk.END, json_text)
            except Exception as e:
                self.preview_text.insert(tk.END, f"JSON格式错误: {str(e)}")
    
    def _build_template_data(self) -> Dict[str, Any]:
        """从编辑器构建模板数据
        
        Returns:
            模板数据字典
        """
        # 基本信息
        template = {}
        
        for field_id, entry in self.info_entries.items():
            if isinstance(entry, scrolledtext.ScrolledText):
                value = entry.get("1.0", tk.END).strip()
            else:
                value = entry.get().strip()
            
            if value:
                template[field_id] = value
        
        # 标签
        tags_text = self.tags_entry.get().strip()
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(",")]
            template["tags"] = tags
        
        # 提示片段
        prompt_segments = list(self.segments_list.get(0, tk.END))
        template["prompt_segments"] = prompt_segments
        
        # 必需输入
        required_inputs = list(self.inputs_list.get(0, tk.END))
        template["required_inputs"] = required_inputs
        
        # 输出格式
        output_format = {}
        for item in self.outputs_list.get(0, tk.END):
            key, type_info = item.split(":", 1)
            output_format[key.strip()] = type_info.strip()
        
        template["output_format"] = output_format
        
        # 下一步模板
        next_templates = {}
        for choice_id, entry in self.link_entries.items():
            templates_text = entry.get().strip()
            if templates_text:
                templates = [template.strip() for template in templates_text.split(",")]
                next_templates[choice_id] = templates
        
        template["next_templates"] = next_templates
        
        # 添加提示词模板（如果存在）
        if hasattr(self, 'template_text'):
            prompt_template = self.template_text.get("1.0", tk.END).strip()
            if prompt_template:
                template["prompt_template"] = prompt_template
        
        # 添加输出存储映射（如果存在）
        if hasattr(self, 'storage_entries') and self.storage_entries:
            storage_mapping = {}
            for output_entry, attr_entry, _ in self.storage_entries:
                output_field = output_entry.get().strip()
                attr_name = attr_entry.get().strip()
                if output_field and attr_name:
                    storage_mapping[output_field] = attr_name
            
            if storage_mapping:
                template["output_storage"] = storage_mapping
        
        return template
    
    def _save_template(self) -> None:
        """保存当前模板"""
        # 构建模板数据
        template = self._build_template_data()
        
        # 验证模板
        if not self._validate_template_data(template):
            return
        
        # 保存模板
        if self.manager.save_template(template):
            messagebox.showinfo("成功", f"模板 {template['template_id']} 已保存")
            
            # 刷新模板列表
            self._refresh_template_list()
        else:
            messagebox.showerror("错误", f"保存模板 {template['template_id']} 失败")
    
    def _validate_template(self) -> None:
        """验证当前模板"""
        # 构建模板数据
        template = self._build_template_data()
        
        # 验证模板
        if self._validate_template_data(template):
            messagebox.showinfo("验证成功", "模板格式正确")
    
    def _validate_template_data(self, template: Dict[str, Any]) -> bool:
        """验证模板数据
        
        Args:
            template: 模板数据
            
        Returns:
            验证是否通过
        """
        # 检查必需字段
        required_fields = ["template_id", "name", "prompt_segments"]
        for field in required_fields:
            if field not in template or not template[field]:
                messagebox.showerror("验证失败", f"缺少必需字段: {field}")
                return False
        
        # 检查提示片段
        if not template["prompt_segments"]:
            messagebox.showerror("验证失败", "提示片段列表不能为空")
            return False
        
        # 检查输出格式
        if not template.get("output_format"):
            messagebox.showerror("验证失败", "输出格式不能为空")
            return False
        
        return True
    
    def _create_new_template(self) -> None:
        """创建新模板"""
        # 重置所有字段
        for field_id, entry in self.info_entries.items():
            if isinstance(entry, scrolledtext.ScrolledText):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
                
                # 设置默认值
                if field_id == "version":
                    entry.insert(0, "1.0")
                elif field_id == "created_at":
                    entry.insert(0, time.strftime("%Y-%m-%d"))
        
        # 清空标签
        self.tags_entry.delete(0, tk.END)
        
        # 清空片段列表
        self.segments_list.delete(0, tk.END)
        
        # 清空输入/输出列表
        self.inputs_list.delete(0, tk.END)
        self.outputs_list.delete(0, tk.END)
        
        # 重置链接
        for widget in self.links_editor_frame.winfo_children():
            widget.destroy()
        self.link_entries = {}
        
        # 添加三个默认选择
        for i in range(1, 4):
            self._add_link_row(f"choice{i}")
            
        # 重置存储映射
        if hasattr(self, 'storage_entries'):
            for _, _, row_frame in self.storage_entries:
                row_frame.destroy()
            self.storage_entries = []
            
            # 添加默认映射
            default_mappings = [
                ("story", "current_story"),
                ("choice1", "option1"),
                ("choice2", "option2"),
                ("choice3", "option3"),
                ("content", "story_content")
            ]
            
            for output_field, attr_name in default_mappings:
                self._add_storage_row(output_field, attr_name)
        
        # 清空预览
        self.preview_text.delete("1.0", tk.END)
        
        # 启用保存按钮
        self.save_button.configure(state=tk.NORMAL)
        
        # 重置当前模板
        self.current_template = None
    
    def _import_template(self) -> None:
        """导入模板文件"""
        file_path = filedialog.askopenfilename(
            title="导入模板",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            # 验证模板
            required_fields = ["template_id", "name", "prompt_segments"]
            for field in required_fields:
                if field not in template:
                    raise ValueError(f"导入的模板缺少必需字段: {field}")
            
            # 保存模板
            if self.manager.save_template(template):
                messagebox.showinfo("成功", f"模板 {template['template_id']} 已导入")
                
                # 刷新模板列表
                self._refresh_template_list()
                
                # 加载导入的模板
                self._load_template(template["template_id"])
            else:
                messagebox.showerror("错误", f"导入模板失败")
            
        except Exception as e:
            messagebox.showerror("导入错误", f"导入模板失败: {str(e)}")
    
    def _export_template(self) -> None:
        """导出模板到文件"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个模板")
            return
        
        # 获取选中的模板ID
        item = selection[0]
        template_id = self.template_tree.item(item, "values")[0]
        
        # 加载模板
        template = self.manager.load_template(template_id)
        if not template:
            messagebox.showerror("错误", f"无法加载模板 {template_id}")
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="导出模板",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialfile=f"{template_id}.json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"模板已导出到 {file_path}")
            
        except Exception as e:
            messagebox.showerror("导出错误", f"导出模板失败: {str(e)}")
    
    def _duplicate_template(self) -> None:
        """复制模板"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个模板")
            return
        
        # 获取选中的模板ID
        item = selection[0]
        template_id = self.template_tree.item(item, "values")[0]
        
        # 加载模板
        template = self.manager.load_template(template_id)
        if not template:
            messagebox.showerror("错误", f"无法加载模板 {template_id}")
            return
        
        # 创建副本
        copy_template = template.copy()
        
        # 修改ID和名称
        new_id = f"{template_id}_copy"
        copy_template["template_id"] = new_id
        copy_template["name"] = f"{copy_template.get('name', template_id)} 副本"
        
        # 保存副本
        if self.manager.save_template(copy_template):
            messagebox.showinfo("成功", f"模板已复制为 {new_id}")
            
            # 刷新模板列表
            self._refresh_template_list()
            
            # 加载新模板
            self._load_template(new_id)
        else:
            messagebox.showerror("错误", f"复制模板失败")
    
    def _delete_template(self) -> None:
        """删除模板"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个模板")
            return
        
        # 获取选中的模板ID
        item = selection[0]
        template_id = self.template_tree.item(item, "values")[0]
        
        # 确认删除
        confirm = messagebox.askyesno("确认删除", f"确定要删除模板 {template_id} 吗？\n此操作不可撤销。")
        if not confirm:
            return
        
        # 删除模板
        if self.manager.delete_template(template_id):
            messagebox.showinfo("成功", f"模板 {template_id} 已删除")
            
            # 刷新模板列表
            self._refresh_template_list()
            
            # 清空编辑器
            self._create_new_template()
        else:
            messagebox.showerror("错误", f"删除模板 {template_id} 失败")
    
    def _edit_selected_template(self) -> None:
        """编辑选中的模板"""
        selection = self.template_tree.selection()
        if not selection:
            return
        
        # 获取选中的模板ID
        item = selection[0]
        template_id = self.template_tree.item(item, "values")[0]
        
        # 加载模板
        self._load_template(template_id)

    def _setup_character_tab(self, parent: ttk.Frame) -> None:
        """设置角色属性选项卡
        
        Args:
            parent: 父容器
        """
        character_frame = ttk.Frame(parent)
        character_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部区域 - 操作按钮
        top_frame = ttk.Frame(character_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="可用角色属性:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, pady=5)
        
        refresh_btn = ttk.Button(top_frame, text="刷新属性列表", command=self._refresh_character_attributes)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # 拆分为左右两部分
        paned = ttk.PanedWindow(character_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 属性树状结构
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # 创建属性树
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "value", "category")
        self.character_attributes_tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
        
        # 设置列
        self.character_attributes_tree.heading("name", text="属性名称")
        self.character_attributes_tree.heading("value", text="属性值")
        self.character_attributes_tree.heading("category", text="类别")
        
        self.character_attributes_tree.column("#0", width=150)
        self.character_attributes_tree.column("name", width=150)
        self.character_attributes_tree.column("value", width=200)
        self.character_attributes_tree.column("category", width=100)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.character_attributes_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.character_attributes_tree.xview)
        self.character_attributes_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.character_attributes_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 双击事件绑定
        self.character_attributes_tree.bind("<Double-1>", self._on_attribute_double_click)
        
        # 右侧 - 使用说明和导入预览
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # 使用说明
        help_frame = ttk.LabelFrame(right_frame, text="使用说明")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = """1. 双击左侧树中的属性将其导入到您的模板中

2. 属性名称格式: character.attribute_name

3. 模板中使用格式: {character.attribute_name}

4. 点击"刷新属性列表"获取最新角色属性"""
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=300)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(right_frame, text="导入预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.attribute_preview = scrolledtext.ScrolledText(preview_frame, height=10, wrap=tk.WORD)
        self.attribute_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入按钮
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.target_combo = ttk.Combobox(buttons_frame, values=["提示片段", "输入变量"], width=15)
        self.target_combo.current(0)
        self.target_combo.pack(side=tk.LEFT, padx=5)
        
        insert_btn = ttk.Button(buttons_frame, text="插入到选中位置", command=self._insert_attribute_to_target)
        insert_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始化加载属性
        self._refresh_character_attributes()
    
    def _refresh_character_attributes(self) -> None:
        """刷新角色属性列表"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法获取属性列表")
            return
            
        # 清空当前树
        for item in self.character_attributes_tree.get_children():
            self.character_attributes_tree.delete(item)
            
        try:
            # 获取所有属性
            all_attributes = get_all_attributes()
            
            # 获取所有类别
            categories = list_categories()
            
            # 先添加分类节点
            category_nodes = {}
            
            # 创建"未分类"节点
            uncategorized_node = self.character_attributes_tree.insert("", "end", text="未分类属性", open=True)
            category_nodes["未分类"] = uncategorized_node
            
            # 添加其他类别节点
            for category in categories:
                if category:  # 跳过空类别
                    node = self.character_attributes_tree.insert("", "end", text=category, open=True)
                    category_nodes[category] = node
            
            # 添加属性到对应类别下
            for attr_name, attr_value in all_attributes.items():
                # 获取属性类别
                category = get_attribute_category(attr_name)
                
                # 格式化显示的属性值
                if isinstance(attr_value, (dict, list)):
                    value_display = str(type(attr_value).__name__)
                else:
                    value_display = str(attr_value)
                    
                # 防止值太长
                if len(value_display) > 50:
                    value_display = value_display[:47] + "..."
                
                # 决定插入到哪个节点下
                parent_node = category_nodes.get(category or "未分类", uncategorized_node)
                
                # 插入属性
                self.character_attributes_tree.insert(
                    parent_node, 
                    "end", 
                    text=attr_name,
                    values=(f"character.{attr_name}", value_display, category or "")
                )
                
            # 展开所有节点
            for node in category_nodes.values():
                self.character_attributes_tree.item(node, open=True)
                
            messagebox.showinfo("成功", "角色属性列表已刷新")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新角色属性失败: {str(e)}")
    
    def _on_attribute_double_click(self, event) -> None:
        """处理属性双击事件"""
        # 获取选中的项
        item = self.character_attributes_tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # 检查是否为叶子节点（属性节点）
        children = self.character_attributes_tree.get_children(item)
        if children:  # 如果有子节点，说明点击的是类别节点
            return
            
        # 获取属性详情
        values = self.character_attributes_tree.item(item, "values")
        if not values:
            return
            
        attr_path = values[0]  # character.attr_name 格式
        
        # 显示在预览区域
        self.attribute_preview.delete("1.0", tk.END)
        self.attribute_preview.insert(tk.END, f"{{{attr_path}}}")
    
    def _insert_attribute_to_target(self) -> None:
        """将属性插入到目标区域"""
        # 获取预览中的内容
        attr_text = self.attribute_preview.get("1.0", tk.END).strip()
        if not attr_text:
            messagebox.showwarning("提示", "请先双击选择一个属性")
            return
            
        # 确定目标
        target = self.target_combo.get()
        
        if target == "提示片段":
            # 插入到当前选中的片段编辑框
            if hasattr(self, 'segment_text'):
                current_text = self.segment_text.get("1.0", tk.END)
                self.segment_text.insert(tk.INSERT, attr_text)
            else:
                messagebox.showwarning("提示", "片段编辑区域不可用")
        elif target == "输入变量":
            # 从属性路径中提取变量名 (character.attr_name)
            if attr_text.startswith("{") and attr_text.endswith("}"):
                attr_name = attr_text[1:-1]  # 去掉大括号
                
                # 检查是否已存在
                existing_inputs = self.inputs_list.get(0, tk.END)
                if attr_name in existing_inputs:
                    messagebox.showinfo("提示", f"输入变量 {attr_name} 已存在")
                    return
                    
                # 添加到输入变量列表
                self.inputs_list.insert(tk.END, attr_name)
            else:
                messagebox.showwarning("格式错误", "属性格式不正确")
        else:
            messagebox.showwarning("未知目标", f"未知的目标区域: {target}")

    def _setup_save_tab(self, parent: ttk.Frame) -> None:
        """设置存档管理选项卡
        
        Args:
            parent: 父容器
        """
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部区域 - 当前存档信息
        top_frame = ttk.LabelFrame(save_frame, text="当前存档")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 当前存档信息
        save_info_frame = ttk.Frame(top_frame)
        save_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(save_info_frame, text="存档文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(save_info_frame, textvariable=self.save_file_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 存档操作按钮
        save_buttons_frame = ttk.Frame(top_frame)
        save_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(save_buttons_frame, text="选择存档", 
                  command=self._select_save_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_buttons_frame, text="创建新存档", 
                  command=self._create_new_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_buttons_frame, text="刷新数据", 
                  command=self._refresh_attribute_editor).pack(side=tk.LEFT, padx=5)
        
        # 中间区域 - 属性编辑器
        # 使用PanedWindow分割属性列表和编辑区域
        paned = ttk.PanedWindow(save_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧 - 属性列表
        left_frame = ttk.LabelFrame(paned, text="属性列表")
        paned.add(left_frame, weight=1)
        
        # 属性树视图
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("name", "value", "category")
        self.attribute_editor_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # 设置列
        self.attribute_editor_tree.heading("name", text="属性名称")
        self.attribute_editor_tree.heading("value", text="属性值")
        self.attribute_editor_tree.heading("category", text="类别")
        
        self.attribute_editor_tree.column("name", width=150)
        self.attribute_editor_tree.column("value", width=250)
        self.attribute_editor_tree.column("category", width=100)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.attribute_editor_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.attribute_editor_tree.xview)
        self.attribute_editor_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.attribute_editor_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 双击事件绑定 - 编辑属性
        self.attribute_editor_tree.bind("<Double-1>", self._edit_attribute_value)
        
        # 右侧 - 属性编辑区域
        right_frame = ttk.LabelFrame(paned, text="属性操作")
        paned.add(right_frame, weight=1)
        
        # 添加新属性
        add_frame = ttk.Frame(right_frame)
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="添加新属性", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        attr_frame = ttk.Frame(add_frame)
        attr_frame.pack(fill=tk.X, pady=2)
        ttk.Label(attr_frame, text="属性名:").pack(side=tk.LEFT, padx=5)
        self.new_attr_name = ttk.Entry(attr_frame, width=20)
        self.new_attr_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        attr_value_frame = ttk.Frame(add_frame)
        attr_value_frame.pack(fill=tk.X, pady=2)
        ttk.Label(attr_value_frame, text="属性值:").pack(side=tk.LEFT, padx=5)
        self.new_attr_value = ttk.Entry(attr_value_frame, width=20)
        self.new_attr_value.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        attr_category_frame = ttk.Frame(add_frame)
        attr_category_frame.pack(fill=tk.X, pady=2)
        ttk.Label(attr_category_frame, text="类别:").pack(side=tk.LEFT, padx=5)
        self.new_attr_category = ttk.Combobox(attr_category_frame, width=20)
        self.new_attr_category.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 添加按钮
        ttk.Button(add_frame, text="添加属性", 
                  command=self._add_new_attribute).pack(anchor=tk.E, pady=5)
        
        # 分隔线
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        # 删除属性
        delete_frame = ttk.Frame(right_frame)
        delete_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(delete_frame, text="删除属性", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(delete_frame, text="删除选中属性", 
                  command=self._delete_selected_attribute).pack(anchor=tk.E, pady=5)
        
        # 初始化加载属性列表
        self._refresh_attribute_editor()
    
    def _update_current_save_info(self) -> None:
        """更新当前存档信息"""
        if CHARACTER_MODULE_AVAILABLE:
            save_path = get_save_location()
            self.save_file_var.set(save_path)
    
    def _select_save_file(self) -> None:
        """选择存档文件"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法选择存档")
            return
            
        # 选择存档目录
        save_dir = filedialog.askdirectory(title="选择存档目录")
        if not save_dir:
            return
            
        # 选择存档文件
        save_file = filedialog.askopenfilename(
            title="选择存档文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialdir=save_dir
        )
        
        if not save_file:
            return
            
        try:
            # 更改当前存档
            filename = os.path.basename(save_file)
            directory = os.path.dirname(save_file)
            configure_save_system(save_dir=directory, save_file=filename)
            
            # 更新显示
            self._update_current_save_info()
            self._refresh_attribute_editor()
            
            messagebox.showinfo("成功", f"已切换到存档: {save_file}")
        except Exception as e:
            messagebox.showerror("错误", f"切换存档失败: {str(e)}")
    
    def _create_new_save(self) -> None:
        """创建新存档"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法创建存档")
            return
            
        # 选择存档目录
        save_dir = filedialog.askdirectory(title="选择存档目录")
        if not save_dir:
            return
            
        # 输入新存档名称
        new_save_name = simpledialog.askstring("新存档", "请输入新存档名称", 
                                             initialvalue="save_" + time.strftime("%Y%m%d%H%M%S") + ".json")
        if not new_save_name:
            return
            
        # 确保有.json后缀
        if not new_save_name.endswith(".json"):
            new_save_name += ".json"
            
        try:
            # 配置新存档
            configure_save_system(save_dir=save_dir, save_file=new_save_name)
            
            # 更新显示
            self._update_current_save_info()
            self._refresh_attribute_editor()
            
            messagebox.showinfo("成功", f"已创建并切换到新存档: {os.path.join(save_dir, new_save_name)}")
        except Exception as e:
            messagebox.showerror("错误", f"创建存档失败: {str(e)}")
    
    def _refresh_attribute_editor(self) -> None:
        """刷新属性编辑器"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法加载属性")
            return
            
        # 清空当前列表
        for item in self.attribute_editor_tree.get_children():
            self.attribute_editor_tree.delete(item)
            
        try:
            # 获取所有属性
            all_attributes = get_all_attributes()
            
            # 获取所有类别
            categories = list_categories()
            self.new_attr_category["values"] = [""] + categories
            
            # 添加属性到列表
            for attr_name, attr_value in all_attributes.items():
                # 获取属性类别
                category = get_attribute_category(attr_name)
                
                # 格式化显示的属性值
                if isinstance(attr_value, (dict, list)):
                    value_display = json.dumps(attr_value, ensure_ascii=False)[:50]
                    if len(value_display) > 50:
                        value_display = value_display[:47] + "..."
                else:
                    value_display = str(attr_value)
                    
                # 防止值太长
                if len(value_display) > 50:
                    value_display = value_display[:47] + "..."
                
                # 插入属性
                self.attribute_editor_tree.insert(
                    "", 
                    "end", 
                    text=attr_name,
                    values=(attr_name, value_display, category or "")
                )
        except Exception as e:
            messagebox.showerror("错误", f"刷新属性列表失败: {str(e)}")
    
    def _edit_attribute_value(self, event) -> None:
        """编辑属性值"""
        # 获取选中的项
        selection = self.attribute_editor_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.attribute_editor_tree.item(item, "values")
        if not values:
            return
            
        attr_name = values[0]
        current_value = get_attribute(attr_name)
        
        if current_value is None:
            messagebox.showwarning("错误", f"属性 '{attr_name}' 不存在")
            return
            
        # 根据属性值类型创建不同的编辑对话框
        if isinstance(current_value, bool):
            # 布尔值选项
            new_value = messagebox.askyesno("编辑布尔值", f"设置 '{attr_name}' 的值", 
                                          initialvalue=current_value)
        elif isinstance(current_value, int):
            # 整数输入
            new_value = simpledialog.askinteger("编辑整数", f"设置 '{attr_name}' 的值", 
                                              initialvalue=current_value)
        elif isinstance(current_value, float):
            # 浮点数输入
            new_value = simpledialog.askfloat("编辑数值", f"设置 '{attr_name}' 的值", 
                                            initialvalue=current_value)
        elif isinstance(current_value, (dict, list)):
            # 复杂数据类型编辑
            self._edit_complex_attribute(attr_name, current_value)
            return
        else:
            # 字符串输入
            new_value = simpledialog.askstring("编辑文本", f"设置 '{attr_name}' 的值", 
                                             initialvalue=str(current_value))
            
        # 确认用户没有取消编辑
        if new_value is not None:
            try:
                # 更新属性值
                set_attribute(attr_name, new_value)
                
                # 刷新显示
                self._refresh_attribute_editor()
                messagebox.showinfo("成功", f"属性 '{attr_name}' 已更新")
            except Exception as e:
                messagebox.showerror("错误", f"更新属性失败: {str(e)}")
    
    def _edit_complex_attribute(self, attr_name: str, value: Any) -> None:
        """编辑复杂类型的属性值"""
        # 创建编辑对话框
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑复杂属性: {attr_name}")
        edit_window.geometry("600x400")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # 创建编辑区域
        frame = ttk.Frame(edit_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"编辑属性 '{attr_name}' (JSON格式):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # JSON编辑器
        text_editor = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        text_editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 填充当前JSON
        try:
            json_text = json.dumps(value, indent=2, ensure_ascii=False)
            text_editor.insert(tk.END, json_text)
        except Exception as e:
            text_editor.insert(tk.END, str(value))
            messagebox.showwarning("格式化错误", f"无法格式化当前值: {str(e)}")
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_complex_value():
            try:
                # 获取编辑后的JSON
                json_text = text_editor.get("1.0", tk.END).strip()
                new_value = json.loads(json_text)
                
                # 更新属性值
                set_attribute(attr_name, new_value)
                
                # 刷新显示
                self._refresh_attribute_editor()
                messagebox.showinfo("成功", f"属性 '{attr_name}' 已更新")
                
                # 关闭窗口
                edit_window.destroy()
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON错误", f"JSON格式错误: {str(e)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存属性失败: {str(e)}")
        
        ttk.Button(button_frame, text="保存", command=save_complex_value).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=edit_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _add_new_attribute(self) -> None:
        """添加新属性"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法添加属性")
            return
            
        # 获取输入值
        attr_name = self.new_attr_name.get().strip()
        attr_value_str = self.new_attr_value.get().strip()
        attr_category = self.new_attr_category.get().strip()
        
        if not attr_name:
            messagebox.showwarning("输入错误", "属性名不能为空")
            return
            
        # 尝试解析值
        try:
            # 首先尝试解析为JSON
            try:
                attr_value = json.loads(attr_value_str)
            except json.JSONDecodeError:
                # 如果不是JSON，按照简单类型处理
                if attr_value_str.lower() == "true":
                    attr_value = True
                elif attr_value_str.lower() == "false":
                    attr_value = False
                elif attr_value_str.isdigit():
                    attr_value = int(attr_value_str)
                elif attr_value_str.replace(".", "", 1).isdigit() and attr_value_str.count(".") <= 1:
                    attr_value = float(attr_value_str)
                else:
                    attr_value = attr_value_str
            
            # 创建属性
            if attr_category:
                success = create_attribute(attr_name, attr_value, attr_category)
            else:
                success = create_attribute(attr_name, attr_value)
                
            if success:
                # 清除输入框
                self.new_attr_name.delete(0, tk.END)
                self.new_attr_value.delete(0, tk.END)
                self.new_attr_category.set("")
                
                # 刷新显示
                self._refresh_attribute_editor()
                messagebox.showinfo("成功", f"属性 '{attr_name}' 已添加")
            else:
                messagebox.showerror("错误", f"创建属性 '{attr_name}' 失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"添加属性失败: {str(e)}")
    
    def _delete_selected_attribute(self) -> None:
        """删除选中的属性"""
        if not CHARACTER_MODULE_AVAILABLE:
            messagebox.showwarning("模块错误", "角色模块未加载，无法删除属性")
            return
            
        # 获取选中的项
        selection = self.attribute_editor_tree.selection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个属性")
            return
            
        item = selection[0]
        values = self.attribute_editor_tree.item(item, "values")
        if not values:
            return
            
        attr_name = values[0]
        
        # 确认删除
        confirm = messagebox.askyesno("确认删除", f"确定要删除属性 '{attr_name}' 吗？\n此操作不可撤销。")
        if not confirm:
            return
            
        try:
            # 删除属性
            success = delete_attribute(attr_name)
            
            if success:
                # 刷新显示
                self._refresh_attribute_editor()
                messagebox.showinfo("成功", f"属性 '{attr_name}' 已删除")
            else:
                messagebox.showerror("错误", f"删除属性 '{attr_name}' 失败")
        except Exception as e:
            messagebox.showerror("错误", f"删除属性失败: {str(e)}")

    def _setup_prompt_processor_tab(self, parent: ttk.Frame) -> None:
        """设置提示词处理选项卡
        
        Args:
            parent: 父容器
        """
        if not AI_MODULE_AVAILABLE:
            # 如果AI模块不可用，显示提示信息
            ttk.Label(parent, text="AI模块未加载，无法使用提示词处理功能", 
                     font=("Arial", 12)).pack(expand=True, padx=20, pady=20)
            return
            
        prompt_frame = ttk.Frame(parent)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建提示词处理器
        self.prompt_processor = PromptProcessor()
        
        # 顶部区域 - 说明
        ttk.Label(prompt_frame, text="提示词处理功能", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
                 
        ttk.Label(prompt_frame, 
                 text="该功能可以将当前编辑的模板片段组合成完整的提示词，便于测试和验证。每个模板都有自己专属的提示词模板。", 
                 wraplength=800).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建分割面板
        paned = ttk.PanedWindow(prompt_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 上部分 - 提示词模板设置
        top_frame = ttk.LabelFrame(paned, text="提示词模板设置")
        paned.add(top_frame, weight=1)
        
        template_frame = ttk.Frame(top_frame)
        template_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(template_frame, text="自定义提示词模板:").pack(anchor=tk.W, pady=(0, 5))
        
        self.template_text = scrolledtext.ScrolledText(template_frame, height=8, wrap=tk.WORD)
        self.template_text.pack(fill=tk.X, expand=True, pady=5)
        
        # 模板按钮
        template_buttons = ttk.Frame(template_frame)
        template_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(template_buttons, text="重置为默认模板", 
                  command=self._reset_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_buttons, text="应用模板", 
                  command=self._apply_template).pack(side=tk.LEFT, padx=5)
        
        # 下部分 - 生成结果
        bottom_frame = ttk.LabelFrame(paned, text="生成的提示词")
        paned.add(bottom_frame, weight=2)
        
        result_frame = ttk.Frame(bottom_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 操作按钮
        action_frame = ttk.Frame(result_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(action_frame, text="从当前模板生成提示词", 
                  command=self._generate_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="复制到剪贴板", 
                  command=self._copy_prompt).pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 从当前模板加载提示词模板（如果存在）
        if self.current_template and "prompt_template" in self.current_template:
            self.template_text.delete("1.0", tk.END)
            self.template_text.insert(tk.END, self.current_template["prompt_template"])
        else:
            self._reset_template()
    
    def _reset_template(self) -> None:
        """重置提示词模板为默认值"""
        self.template_text.delete("1.0", tk.END)
        self.template_text.insert(tk.END, DEFAULT_PROMPT_TEMPLATE)
    
    def _apply_template(self) -> None:
        """应用自定义提示词模板"""
        template = self.template_text.get("1.0", tk.END).strip()
        if not template:
            messagebox.showwarning("输入错误", "提示词模板不能为空")
            return
            
        try:
            # 更新提示词处理器的模板
            self.prompt_processor.set_template(template)
            
            # 更新当前编辑的模板中的提示词模板
            if self.current_template:
                self.current_template["prompt_template"] = template
                # 刷新预览
                self._refresh_preview()
                
            messagebox.showinfo("成功", "提示词模板已应用并保存到当前模板")
        except Exception as e:
            messagebox.showerror("错误", f"应用模板失败: {str(e)}")
    
    def _generate_prompt(self) -> None:
        """从当前模板生成提示词"""
        if not self.current_template:
            messagebox.showwarning("操作错误", "请先加载或创建一个模板")
            return
            
        # 获取提示片段
        segments = self.current_template.get("prompt_segments", [])
        if not segments:
            messagebox.showwarning("操作错误", "当前模板没有提示片段")
            return
            
        try:
            # 如果当前模板有自定义的提示词模板，先应用它
            if "prompt_template" in self.current_template:
                self.prompt_processor.set_template(self.current_template["prompt_template"])
            
            # 生成提示词
            prompt = self.prompt_processor.build_prompt(segments)
            
            # 显示结果
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, prompt)
        except Exception as e:
            messagebox.showerror("错误", f"生成提示词失败: {str(e)}")
    
    def _copy_prompt(self) -> None:
        """复制生成的提示词到剪贴板"""
        prompt = self.result_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("操作错误", "没有可复制的提示词")
            return
            
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        
        messagebox.showinfo("成功", "提示词已复制到剪贴板")

    def _setup_storage_tab(self, parent: ttk.Frame) -> None:
        """设置输出存储选项卡
        
        Args:
            parent: 父容器
        """
        storage_frame = ttk.Frame(parent)
        storage_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(storage_frame, text="输出字段到角色属性的映射:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 解释文本
        explanation = (
            "在这里设置模板执行后将输出字段自动存储为角色属性的映射关系。"
            "例如，可以将story字段存储为current_story属性，将choice1字段存储为option1属性等。"
            "这样，模板执行后会自动将输出结果存储到指定的角色属性中，无需额外代码。"
        )
        ttk.Label(storage_frame, text=explanation, wraplength=800).pack(anchor=tk.W, pady=(0, 10))
        
        # 特殊字段提示
        special_tip = "注意: 'content'是一个特殊的键，用于存储格式化后的完整故事内容，而不是原始JSON字段。"
        ttk.Label(storage_frame, text=special_tip, font=("Arial", 9, "italic"), foreground="blue").pack(anchor=tk.W, pady=(0, 10))
        
        # 映射表格区域
        self.storage_frame = ttk.Frame(storage_frame)
        self.storage_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表头
        headers_frame = ttk.Frame(self.storage_frame)
        headers_frame.pack(fill=tk.X)
        
        ttk.Label(headers_frame, text="输出字段", width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="存储到属性", width=20).pack(side=tk.LEFT, padx=5)
        
        # 存储映射编辑区
        self.storage_editor_frame = ttk.Frame(self.storage_frame)
        self.storage_editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加常用映射
        self.storage_entries = []
        default_mappings = [
            ("story", "current_story"),
            ("choice1", "option1"),
            ("choice2", "option2"),
            ("choice3", "option3"),
            ("content", "story_content")
        ]
        
        for output_field, attr_name in default_mappings:
            self._add_storage_row(output_field, attr_name)
        
        # 添加映射按钮
        add_frame = ttk.Frame(storage_frame)
        add_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(add_frame, text="输出字段:").pack(side=tk.LEFT, padx=5)
        self.storage_output_field = ttk.Entry(add_frame, width=15)
        self.storage_output_field.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="属性名:").pack(side=tk.LEFT, padx=5)
        self.storage_attr_name = ttk.Entry(add_frame, width=15)
        self.storage_attr_name.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame, text="添加映射", command=self._add_new_storage).pack(side=tk.RIGHT, padx=5)
        
        # 帮助提示
        help_frame = ttk.LabelFrame(storage_frame, text="使用说明")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "- 在运行模板时，输出字段的值会自动存储到对应的角色属性中\n"
            "- 如果属性不存在，将自动创建；如果已存在，将被更新\n"
            "- 建议与输出格式选项卡中定义的字段保持一致\n"
            "- 删除一行可以点击该行右侧的'删除'按钮\n"
            "- 这些映射信息会保存在模板中，每次执行模板时自动应用"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=800)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
    
    def _add_storage_row(self, output_field: str = "", attr_name: str = "") -> None:
        """添加存储映射行
        
        Args:
            output_field: 输出字段
            attr_name: 属性名
        """
        row_frame = ttk.Frame(self.storage_editor_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        # 输出字段
        output_entry = ttk.Entry(row_frame, width=20)
        output_entry.pack(side=tk.LEFT, padx=5)
        if output_field:
            output_entry.insert(0, output_field)
        
        # 属性名
        attr_entry = ttk.Entry(row_frame, width=20)
        attr_entry.pack(side=tk.LEFT, padx=5)
        if attr_name:
            attr_entry.insert(0, attr_name)
        
        # 保存行信息
        row_info = (output_entry, attr_entry, row_frame)
        self.storage_entries.append(row_info)
        
        # 删除按钮
        ttk.Button(row_frame, text="删除", command=lambda: self._delete_storage_row(row_info)).pack(side=tk.RIGHT, padx=5)
    
    def _delete_storage_row(self, row_info) -> None:
        """删除存储映射行
        
        Args:
            row_info: 行信息 (output_entry, attr_entry, row_frame)
        """
        output_entry, attr_entry, row_frame = row_info
        self.storage_entries.remove(row_info)
        row_frame.destroy()
    
    def _add_new_storage(self) -> None:
        """添加新的存储映射"""
        output_field = self.storage_output_field.get().strip()
        attr_name = self.storage_attr_name.get().strip()
        
        if not output_field or not attr_name:
            messagebox.showwarning("输入错误", "输出字段和属性名不能为空")
            return
        
        # 添加新行
        self._add_storage_row(output_field, attr_name)
        
        # 清空输入框
        self.storage_output_field.delete(0, tk.END)
        self.storage_attr_name.delete(0, tk.END)

    def _update_storage_mapping(self, template: Dict[str, Any]) -> None:
        """更新存储映射表格
        
        Args:
            template: 模板数据
        """
        # 清空现有映射
        for _, _, row_frame in self.storage_entries:
            row_frame.destroy()
        self.storage_entries = []
        
        # 添加映射
        if "output_storage" in template and template["output_storage"]:
            for output_field, attr_name in template["output_storage"].items():
                # 添加行
                self._add_storage_row(output_field, attr_name)
        else:
            # 添加默认映射
            default_mappings = [
                ("story", "current_story"),
                ("choice1", "option1"),
                ("choice2", "option2"),
                ("choice3", "option3"),
                ("content", "story_content")
            ]
            
            for output_field, attr_name in default_mappings:
                self._add_storage_row(output_field, attr_name)

def run_editor():
    """运行模板编辑器"""
    editor = TemplateEditor()
    editor.run()

if __name__ == "__main__":
    run_editor() 