"""
简化版故事模板编辑工具

此工具提供图形界面编辑故事模板，适配新版StorylineManager，
直接使用角色属性，无需内外变量转换。
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
    from character.character_manager import get_all_attributes, get_attribute, set_attribute, create_attribute
    CHARACTER_MODULE_AVAILABLE = True
except ImportError:
    CHARACTER_MODULE_AVAILABLE = False
    print("警告：未能导入角色模块，角色属性功能将不可用")

# 导入AI模块
try:
    from ai.prompt_processor import PromptProcessor
    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False
    print("警告：未能导入AI模块，提示词处理功能将不可用")

class SimplifiedTemplateEditor:
    """简化版模板编辑器，提供图形界面编辑模板"""
    
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
        
        # 如果有角色模块，初始化提示词处理器
        if AI_MODULE_AVAILABLE:
            self.prompt_processor = PromptProcessor()
    
    def run(self) -> None:
        """启动模板编辑器图形界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("简化版故事模板编辑器")
        self.root.geometry("1200x800")
        
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
        
        # 输出和存储选项卡
        output_tab = ttk.Frame(self.notebook)
        self.notebook.add(output_tab, text="输出和存储")
        self._setup_output_tab(output_tab)
        
        # 角色属性选项卡
        if CHARACTER_MODULE_AVAILABLE:
            character_tab = ttk.Frame(self.notebook)
            self.notebook.add(character_tab, text="角色属性")
            self._setup_character_tab(character_tab)
            
        # 提示词处理选项卡
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
        
        # 添加使用提示
        ttk.Separator(self.template_info_frame, orient=tk.HORIZONTAL).grid(row=row+1, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        tip_frame = ttk.LabelFrame(self.template_info_frame, text="简化版模板说明")
        tip_frame.grid(row=row+2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        tip_text = (
            "简化版模板直接使用角色属性而不需要定义输入变量。\n"
            "在提示片段中可以直接使用 {属性名} 格式引用角色属性，例如 {name} 或 {力量}。\n"
            "系统会自动从角色属性中读取值并替换到提示词中。"
        )
        
        tip_label = ttk.Label(tip_frame, text=tip_text, justify=tk.LEFT, wraplength=600)
        tip_label.pack(padx=10, pady=10, anchor=tk.W)

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
            "4. 角色属性引用: 使用 {属性名} 格式，例如 {name} 或 {力量}\n"
            "   - 所有角色属性都可以直接引用，无需预定义输入变量"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=400)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
    
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

    def _setup_output_tab(self, parent: ttk.Frame) -> None:
        """设置输出和存储选项卡 - 将输出定义和存储映射整合到一个选项卡
        
        Args:
            parent: 父容器
        """
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 解释文本
        explanation = (
            "在此选项卡中定义模板输出字段的格式以及如何将它们存储到角色属性中。\n"
            "系统会自动将输出字段存储到指定的角色属性，无需额外代码。"
        )
        ttk.Label(output_frame, text=explanation, wraplength=800).pack(anchor=tk.W, pady=(0, 10))
        
        # 特殊字段提示
        special_tip = "注意: 'content'是一个特殊的键，代表格式化后的完整故事内容。"
        ttk.Label(output_frame, text=special_tip, font=("Arial", 9, "italic"), foreground="blue").pack(anchor=tk.W, pady=(0, 10))
        
        # 表格区域 - 输出定义和存储映射
        table_frame = ttk.Frame(output_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表头
        headers_frame = ttk.Frame(table_frame)
        headers_frame.pack(fill=tk.X)
        
        ttk.Label(headers_frame, text="输出字段", width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="数据类型", width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="存储到属性", width=20).pack(side=tk.LEFT, padx=5)
        
        # 编辑区域
        self.output_editor_frame = ttk.Frame(table_frame)
        self.output_editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加默认输出字段和存储映射
        self.output_entries = []
        default_outputs = [
            ("story", "string", "current_story"),
            ("choice1", "string", "option1"),
            ("choice2", "string", "option2"),
            ("choice3", "string", "option3"),
            ("content", "special", "story_content")
        ]
        
        for field_name, data_type, attr_name in default_outputs:
            self._add_output_row(field_name, data_type, attr_name)
        
        # 添加新字段的区域
        add_frame = ttk.Frame(output_frame)
        add_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(add_frame, text="字段名:").pack(side=tk.LEFT, padx=5)
        self.new_field_name = ttk.Entry(add_frame, width=15)
        self.new_field_name.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="类型:").pack(side=tk.LEFT, padx=5)
        self.new_data_type = ttk.Combobox(add_frame, values=["string", "number", "boolean", "array", "object"], width=10)
        self.new_data_type.current(0)
        self.new_data_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="属性名:").pack(side=tk.LEFT, padx=5)
        self.new_attr_name = ttk.Entry(add_frame, width=15)
        self.new_attr_name.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame, text="添加字段", command=self._add_new_output).pack(side=tk.RIGHT, padx=5)
        
        # 帮助文本
        help_frame = ttk.LabelFrame(output_frame, text="使用说明")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "- 输出字段: 定义AI返回的JSON字段名称，例如'story'、'choice1'等\n"
            "- 数据类型: 指定字段的数据类型，如字符串、数字等\n"
            "- 存储到属性: 指定将字段内容存储到哪个角色属性中\n"
            "- 模板执行时会自动将AI输出存储到对应的角色属性中\n"
            "- 如果属性不存在，将自动创建；如果已存在，将被更新"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=800)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
    
    def _add_output_row(self, field_name: str = "", data_type: str = "string", attr_name: str = "") -> None:
        """添加输出字段行
        
        Args:
            field_name: 字段名
            data_type: 数据类型
            attr_name: 存储到的属性名
        """
        row_frame = ttk.Frame(self.output_editor_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        # 字段名
        field_entry = ttk.Entry(row_frame, width=20)
        field_entry.pack(side=tk.LEFT, padx=5)
        if field_name:
            field_entry.insert(0, field_name)
        
        # 数据类型
        type_combo = ttk.Combobox(row_frame, values=["string", "number", "boolean", "array", "object", "special"], width=15)
        type_combo.pack(side=tk.LEFT, padx=5)
        if data_type:
            type_combo.set(data_type)
        else:
            type_combo.current(0)
        
        # 属性名
        attr_entry = ttk.Entry(row_frame, width=20)
        attr_entry.pack(side=tk.LEFT, padx=5)
        if attr_name:
            attr_entry.insert(0, attr_name)
        
        # 保存行信息
        row_info = (field_entry, type_combo, attr_entry, row_frame)
        self.output_entries.append(row_info)
        
        # 删除按钮
        ttk.Button(row_frame, text="删除", command=lambda: self._delete_output_row(row_info)).pack(side=tk.RIGHT, padx=5)
    
    def _delete_output_row(self, row_info) -> None:
        """删除输出字段行
        
        Args:
            row_info: 行信息 (field_entry, type_combo, attr_entry, row_frame)
        """
        field_entry, type_combo, attr_entry, row_frame = row_info
        self.output_entries.remove(row_info)
        row_frame.destroy()
    
    def _add_new_output(self) -> None:
        """添加新的输出字段"""
        field_name = self.new_field_name.get().strip()
        data_type = self.new_data_type.get()
        attr_name = self.new_attr_name.get().strip()
        
        if not field_name:
            messagebox.showwarning("输入错误", "字段名不能为空")
            return
            
        if not attr_name:
            # 如果没有指定属性名，使用与字段名相同的属性名
            attr_name = field_name
        
        # 检查字段名是否已存在
        existing_fields = [entry[0].get() for entry in self.output_entries]
        if field_name in existing_fields:
            messagebox.showwarning("重复输入", f"字段名 {field_name} 已存在")
            return
        
        # 添加新行
        self._add_output_row(field_name, data_type, attr_name)
        
        # 清空输入框
        self.new_field_name.delete(0, tk.END)
        self.new_attr_name.delete(0, tk.END)
        self.new_data_type.current(0)
    
    def _setup_character_tab(self, parent: ttk.Frame) -> None:
        """设置角色属性选项卡 - 用于浏览可用的角色属性
        
        Args:
            parent: 父容器
        """
        character_frame = ttk.Frame(parent)
        character_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题和说明
        ttk.Label(character_frame, text="当前角色属性", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        explanation = (
            "此选项卡显示所有可用的角色属性，可以直接在提示片段中使用 {属性名} 来引用这些属性。"
            "无需预先定义输入变量，系统会自动从角色属性中读取值。"
        )
        ttk.Label(character_frame, text=explanation, wraplength=800).pack(anchor=tk.W, pady=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(character_frame, text="刷新属性列表", command=self._refresh_attributes)
        refresh_btn.pack(anchor=tk.W, pady=5)
        
        # 属性列表区域
        attrs_frame = ttk.Frame(character_frame)
        attrs_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建属性表格
        columns = ("name", "value", "type")
        self.attrs_tree = ttk.Treeview(attrs_frame, columns=columns, show="headings", height=15)
        
        # 设置列
        self.attrs_tree.heading("name", text="属性名")
        self.attrs_tree.heading("value", text="属性值")
        self.attrs_tree.heading("type", text="类型")
        
        self.attrs_tree.column("name", width=150)
        self.attrs_tree.column("value", width=400)
        self.attrs_tree.column("type", width=100)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(attrs_frame, orient=tk.VERTICAL, command=self.attrs_tree.yview)
        scrollbar_x = ttk.Scrollbar(attrs_frame, orient=tk.HORIZONTAL, command=self.attrs_tree.xview)
        self.attrs_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.attrs_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 双击事件 - 复制属性名到剪贴板
        self.attrs_tree.bind("<Double-1>", self._copy_attribute_name)
        
        # 右键菜单
        self._setup_attrs_context_menu()
        
        # 立即加载属性
        self._refresh_attributes()
        
        # 使用提示区域
        tip_frame = ttk.LabelFrame(character_frame, text="使用提示")
        tip_frame.pack(fill=tk.X, pady=10)
        
        tip_text = (
            "- 双击属性可将属性名复制到剪贴板\n"
            "- 在提示片段中使用 {属性名} 格式引用属性值\n"
            "- 对于嵌套属性，可使用点语法，例如 {equipment.weapon}\n"
            "- 特殊属性 character.xxx 也可以直接使用 {xxx} 简化引用"
        )
        
        tip_label = ttk.Label(tip_frame, text=tip_text, justify=tk.LEFT, wraplength=800)
        tip_label.pack(padx=10, pady=10, anchor=tk.W)
    
    def _setup_attrs_context_menu(self) -> None:
        """设置属性列表右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="复制属性名", command=self._copy_selected_attr_name)
        menu.add_command(label="插入到当前片段", command=self._insert_attr_to_segment)
        
        def show_menu(event):
            if self.attrs_tree.selection():
                menu.post(event.x_root, event.y_root)
        
        self.attrs_tree.bind("<Button-3>", show_menu)
    
    def _refresh_attributes(self) -> None:
        """刷新角色属性列表"""
        # 清空现有项
        for item in self.attrs_tree.get_children():
            self.attrs_tree.delete(item)
            
        if not CHARACTER_MODULE_AVAILABLE:
            self.attrs_tree.insert("", tk.END, values=("错误", "角色模块不可用", ""))
            return
            
        # 获取所有角色属性
        try:
            all_attrs = get_all_attributes()
            
            # 添加到表格
            for name, value in all_attrs.items():
                # 处理值的显示
                if isinstance(value, dict):
                    display_value = f"字典 ({len(value)} 项)"
                    value_type = "dict"
                elif isinstance(value, list):
                    display_value = f"列表 ({len(value)} 项)"
                    value_type = "list"
                elif isinstance(value, str) and len(value) > 100:
                    display_value = value[:100] + "..."
                    value_type = "string"
                else:
                    display_value = str(value)
                    value_type = type(value).__name__
                
                self.attrs_tree.insert("", tk.END, values=(name, display_value, value_type))
                
            # 如果没有属性，显示提示
            if not all_attrs:
                self.attrs_tree.insert("", tk.END, values=("无属性", "尚未创建任何角色属性", ""))
                
        except Exception as e:
            self.attrs_tree.insert("", tk.END, values=("错误", f"加载属性失败: {str(e)}", ""))
    
    def _copy_attribute_name(self, event) -> None:
        """复制属性名到剪贴板（双击事件）
        
        Args:
            event: 事件对象
        """
        self._copy_selected_attr_name()
    
    def _copy_selected_attr_name(self) -> None:
        """复制选中的属性名到剪贴板"""
        selection = self.attrs_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        attr_name = self.attrs_tree.item(item, "values")[0]
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(attr_name)
        
        messagebox.showinfo("已复制", f"属性名 '{attr_name}' 已复制到剪贴板")
    
    def _insert_attr_to_segment(self) -> None:
        """将选中的属性插入到当前编辑的片段中"""
        selection = self.attrs_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        attr_name = self.attrs_tree.item(item, "values")[0]
        
        # 创建插入文本
        insert_text = "{" + attr_name + "}"
        
        # 插入到当前片段编辑器
        if hasattr(self, 'segment_text'):
            current_tab = self.notebook.index(self.notebook.select())
            tab_name = self.notebook.tab(current_tab, "text")
            
            if tab_name == "提示片段":
                # 获取当前光标位置
                try:
                    position = self.segment_text.index(tk.INSERT)
                    self.segment_text.insert(position, insert_text)
                except Exception:
                    # 如果无法获取光标位置，则追加到末尾
                    self.segment_text.insert(tk.END, insert_text)
                
                messagebox.showinfo("已插入", f"属性引用 '{insert_text}' 已插入到片段")
            else:
                messagebox.showinfo("提示", "请先切换到'提示片段'选项卡")
        else:
            messagebox.showinfo("提示", "无法找到片段编辑器")

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
        
        # 更新输出和存储
        self._update_output_fields(template)
        
        # 更新提示词模板
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
    
    def _update_output_fields(self, template: Dict[str, Any]) -> None:
        """更新输出和存储字段
        
        Args:
            template: 模板数据
        """
        # 清空现有行
        for _, _, _, row_frame in self.output_entries:
            row_frame.destroy()
        self.output_entries = []
        
        # 准备输出格式和存储映射
        output_format = template.get("output_format", {})
        output_storage = template.get("output_storage", {})
        
        # 添加所有输出字段
        for field, type_info in output_format.items():
            # 查找对应的存储属性
            attr_name = output_storage.get(field, "")
            
            # 添加行
            self._add_output_row(field, type_info, attr_name)
        
        # 如果还有存储映射但没有对应的输出格式，也添加它们
        for field, attr_name in output_storage.items():
            if field not in output_format:
                if field == "content":
                    # 特殊处理content字段
                    self._add_output_row(field, "special", attr_name)
                else:
                    self._add_output_row(field, "string", attr_name)
                    
        # 如果没有任何输出字段，添加默认字段
        if not self.output_entries:
            default_outputs = [
                ("story", "string", "current_story"),
                ("choice1", "string", "option1"),
                ("choice2", "string", "option2"),
                ("choice3", "string", "option3"),
                ("content", "special", "story_content")
            ]
            
            for field_name, data_type, attr_name in default_outputs:
                self._add_output_row(field_name, data_type, attr_name)

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
        if hasattr(self, 'segments_list'):
            prompt_segments = list(self.segments_list.get(0, tk.END))
            template["prompt_segments"] = prompt_segments
        
        # 输出格式和存储映射
        if hasattr(self, 'output_entries'):
            output_format = {}
            output_storage = {}
            
            for field_entry, type_combo, attr_entry, _ in self.output_entries:
                field_name = field_entry.get().strip()
                data_type = type_combo.get()
                attr_name = attr_entry.get().strip()
                
                if field_name:
                    # 添加到输出格式，特殊字段除外
                    if data_type != "special":
                        output_format[field_name] = data_type
                    
                    # 添加到存储映射
                    if attr_name:
                        output_storage[field_name] = attr_name
            
            if output_format:
                template["output_format"] = output_format
                
            if output_storage:
                template["output_storage"] = output_storage
        
        # 提示词模板
        if hasattr(self, 'template_text'):
            prompt_template = self.template_text.get("1.0", tk.END).strip()
            if prompt_template:
                template["prompt_template"] = prompt_template
        
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
        
        # 检查输出存储映射
        if not template.get("output_storage"):
            messagebox.showwarning("警告", "没有定义输出存储映射，模板将无法自动存储输出")
        
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
        
        # 重置输出字段
        for _, _, _, row_frame in self.output_entries:
            row_frame.destroy()
        self.output_entries = []
        
        # 添加默认输出字段
        default_outputs = [
            ("story", "string", "current_story"),
            ("choice1", "string", "option1"),
            ("choice2", "string", "option2"),
            ("choice3", "string", "option3"),
            ("content", "special", "story_content")
        ]
        
        for field_name, data_type, attr_name in default_outputs:
            self._add_output_row(field_name, data_type, attr_name)
        
        # 重置提示词模板
        if hasattr(self, 'template_text'):
            self._reset_template()
        
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

    def _setup_prompt_processor_tab(self, parent: ttk.Frame) -> None:
        """设置提示词处理选项卡
        
        Args:
            parent: 父容器
        """
        prompt_frame = ttk.Frame(parent)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 模板自定义区域
        template_frame = ttk.LabelFrame(prompt_frame, text="自定义提示词模板")
        template_frame.pack(fill=tk.X, pady=5)
        
        self.template_text = scrolledtext.ScrolledText(template_frame, height=8)
        self.template_text.pack(fill=tk.X, padx=10, pady=10)
        
        # 如果没有初始模板，提供默认模板
        default_template = (
            "你是一个高级故事生成AI，请根据以下提示创建故事内容。\n\n"
            "## 背景信息\n{background}\n\n"
            "## 内容要求\n{content}\n\n"
            "## 输出格式\n请严格按照以下JSON格式回复：\n{format}"
        )
        self.template_text.insert(tk.END, default_template)
        
        # 功能按钮
        button_frame = ttk.Frame(prompt_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="重置默认模板", command=self._reset_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="应用模板", command=self._apply_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="生成提示词预览", command=self._generate_prompt).pack(side=tk.RIGHT, padx=5)
        
        # 提示词预览区域
        preview_frame = ttk.LabelFrame(prompt_frame, text="生成的提示词预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(preview_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 复制按钮
        ttk.Button(preview_frame, text="复制到剪贴板", command=self._copy_prompt).pack(anchor=tk.E, padx=10, pady=(0, 10))
        
        # 使用说明
        help_frame = ttk.LabelFrame(prompt_frame, text="提示词模板说明")
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = (
            "- 提示词模板用于控制如何将片段组合成完整提示词\n"
            "- {background} 将被替换为所有背景信息片段\n"
            "- {content} 将被替换为所有内容指令片段\n"
            "- {format} 将被替换为所有输出格式片段\n"
            "- 此处设置的模板会保存在模板JSON中，每个模板可以有自己的专属提示词模板"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=800)
        help_label.pack(padx=10, pady=10, anchor=tk.W)
    
    def _reset_template(self) -> None:
        """重置默认提示词模板"""
        default_template = (
            "你是一个高级故事生成AI，请根据以下提示创建故事内容。\n\n"
            "## 背景信息\n{background}\n\n"
            "## 内容要求\n{content}\n\n"
            "## 输出格式\n请严格按照以下JSON格式回复：\n{format}"
        )
        self.template_text.delete("1.0", tk.END)
        self.template_text.insert(tk.END, default_template)
    
    def _apply_template(self) -> None:
        """应用当前编辑的提示词模板"""
        if not self.current_template:
            messagebox.showwarning("操作错误", "请先加载或创建一个模板")
            return
            
        # 获取模板内容
        template_content = self.template_text.get("1.0", tk.END).strip()
        if not template_content:
            messagebox.showwarning("操作错误", "提示词模板不能为空")
            return
            
        # 更新当前模板
        self.current_template["prompt_template"] = template_content
        messagebox.showinfo("成功", "提示词模板已应用到当前模板")
    
    def _generate_prompt(self) -> None:
        """生成提示词预览"""
        if not self.current_template:
            messagebox.showwarning("操作错误", "请先加载或创建一个模板")
            return
            
        # 获取模板内容
        template_content = self.template_text.get("1.0", tk.END).strip()
        if not template_content:
            messagebox.showwarning("操作错误", "提示词模板不能为空")
            return
            
        # 获取提示片段
        if not hasattr(self, 'segments_list'):
            messagebox.showwarning("操作错误", "无法获取提示片段")
            return
            
        segments = list(self.segments_list.get(0, tk.END))
        if not segments:
            messagebox.showwarning("操作错误", "当前模板没有提示片段")
            return
            
        try:
            # 创建临时提示词处理器
            temp_processor = PromptProcessor(template_content)
            
            # 对片段进行预处理 - 现在使用新的处理方式
            processed_segments = []
            if CHARACTER_MODULE_AVAILABLE:
                # 获取所有角色属性
                all_attributes = get_all_attributes()
                
                # 处理每个片段中的属性占位符
                for segment in segments:
                    processed = segment
                    for attr_name, attr_value in all_attributes.items():
                        placeholder = "{" + attr_name + "}"
                        if placeholder in processed:
                            processed = processed.replace(placeholder, str(attr_value))
                        
                        # 处理character.xxx格式
                        character_placeholder = "{character." + attr_name + "}"
                        if character_placeholder in processed:
                            processed = processed.replace(character_placeholder, str(attr_value))
                    
                    processed_segments.append(processed)
            else:
                processed_segments = segments
            
            # 生成提示词
            prompt = temp_processor.build_prompt(processed_segments)
            
            # 显示预览
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

def run_editor():
    """运行模板编辑器"""
    editor = SimplifiedTemplateEditor()
    editor.run()

if __name__ == "__main__":
    run_editor() 