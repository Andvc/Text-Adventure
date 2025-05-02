"""
故事模板编辑工具

此工具提供图形界面编辑故事模板，适配StorylineManager，
直接使用数据模块API，实现模板管理功能。
"""

import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import re

# 导入数据模块API
from data.data_manager import (
    load_save,
    save_data,
    list_saves,
    get_save_value,
    get_nested_save_value
)

# 导入storyline模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from storyline import TEMPLATES_PATH
from storyline.storyline_manager import StorylineManager

# 导入AI模块
try:
    from ai.prompt_processor import PromptProcessor
    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False
    print("警告：未能导入AI模块，提示词处理功能将不可用")

# 定义全局变量
DATA_MODULE_AVAILABLE = True  # 数据模块已集成

class TemplateEditor:
    """模板编辑器，提供图形界面编辑模板"""
    
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
        
        # 如果有AI模块，初始化提示词处理器
        if AI_MODULE_AVAILABLE:
            self.prompt_processor = PromptProcessor()
            
        # 初始化存档管理相关变量
        self.save_type = "character"
        # 确保存档目录存在
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(Path(__file__).parent)), "save", "characters"), exist_ok=True)
    
    def run(self) -> None:
        """启动模板编辑器图形界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("故事模板编辑器")
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
        # 标题和模板列表
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ttk.Label(header_frame, text="模板列表", font=("Arial", 11, "bold"))
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # 模板列表区域
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "name", "version")
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=16)
        
        # 设置列标题和宽度
        self.template_tree.heading("id", text="ID")
        self.template_tree.heading("name", text="名称")
        self.template_tree.heading("version", text="版本")
        
        # 设置合理的列宽比例
        self.template_tree.column("id", width=90)
        self.template_tree.column("name", width=140)
        self.template_tree.column("version", width=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        self.template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域 - 底部工具栏
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 使用Grid布局实现三行按钮
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # 第一行：新建和删除按钮
        new_btn = ttk.Button(buttons_frame, text="新建", width=10, command=self._create_new_template)
        new_btn.grid(row=0, column=0, sticky=tk.EW, padx=3, pady=2)
        
        delete_btn = ttk.Button(buttons_frame, text="删除", width=10, command=self._delete_template)
        delete_btn.grid(row=0, column=1, sticky=tk.EW, padx=3, pady=2)
        
        # 第二行：保存和刷新按钮
        self.save_btn = ttk.Button(buttons_frame, text="保存", width=10, command=self._save_template_new)
        self.save_btn.grid(row=1, column=0, sticky=tk.EW, padx=3, pady=2)
        
        refresh_btn = ttk.Button(buttons_frame, text="刷新", width=10, command=self._refresh_template_list)
        refresh_btn.grid(row=1, column=1, sticky=tk.EW, padx=3, pady=2)
        
        # 绑定事件
        self.template_tree.bind("<<TreeviewSelect>>", self._on_template_select)
        self.template_tree.bind("<Double-1>", lambda e: self._edit_selected_template())
    
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
        
        # 存档管理选项卡
        if DATA_MODULE_AVAILABLE:
            save_tab = ttk.Frame(self.notebook)
            self.notebook.add(save_tab, text="存档数据")
            self._setup_save_tab(save_tab)
            
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
        
        # 移除这里的保存按钮，已经移到左侧工具栏
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
            # 标签
            label = ttk.Label(self.template_info_frame, text=label_text)
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            
            # 输入框
            if field_id == "description":
                entry = tk.Text(self.template_info_frame, height=4, width=40)
                entry.insert("1.0", default_value)
            else:
                entry = ttk.Entry(self.template_info_frame, width=40)
                entry.insert(0, default_value)
            
            entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
            self.info_entries[field_id] = entry
            
            row += 1
        
        # 标签输入
        label = ttk.Label(self.template_info_frame, text="标签(逗号分隔):")
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.tags_entry = ttk.Entry(self.template_info_frame, width=40)
        self.tags_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 设置列权重，使输入框可以随窗口调整
        self.template_info_frame.columnconfigure(1, weight=1)
        
        # 添加使用提示
        ttk.Separator(self.template_info_frame, orient=tk.HORIZONTAL).grid(row=row+1, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        tip_frame = ttk.LabelFrame(self.template_info_frame, text="模板说明")
        tip_frame.grid(row=row+2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        tip_text = (
            "模板直接使用角色属性而不需要定义输入变量。\n"
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
        # 创建分隔面板：左侧列表，右侧编辑
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧列表
        left_frame = ttk.Frame(paned, width=200)
        paned.add(left_frame, weight=1)
        
        # 右侧编辑
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # 列表区域
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 片段列表
        columns = ("index", "segment")
        self.segments_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        self.segments_tree.heading("index", text="#")
        self.segments_tree.heading("segment", text="片段内容")
        
        self.segments_tree.column("index", width=30, anchor=tk.CENTER)
        self.segments_tree.column("segment", width=170)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.segments_tree.yview)
        self.segments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.segments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 使用Grid布局按钮
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # 上下移动按钮
        up_btn = ttk.Button(buttons_frame, text="上移", width=8, command=lambda: self._move_segment(-1))
        up_btn.grid(row=0, column=0, sticky=tk.EW, padx=3, pady=2)
        
        down_btn = ttk.Button(buttons_frame, text="下移", width=8, command=lambda: self._move_segment(1))
        down_btn.grid(row=0, column=1, sticky=tk.EW, padx=3, pady=2)
        
        # 添加和删除按钮
        add_btn = ttk.Button(buttons_frame, text="添加", width=8, command=self._add_update_segment)
        add_btn.grid(row=1, column=0, sticky=tk.EW, padx=3, pady=2)
        
        delete_btn = ttk.Button(buttons_frame, text="删除", width=8, command=self._delete_segment)
        delete_btn.grid(row=1, column=1, sticky=tk.EW, padx=3, pady=2)
        
        # 右侧编辑区域
        edit_frame = ttk.LabelFrame(right_frame, text="编辑片段")
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 片段类型选择
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        type_label = ttk.Label(type_frame, text="片段类型:")
        type_label.pack(side=tk.LEFT, padx=5)
        
        self.segment_type_var = tk.StringVar(value="info")
        
        info_radio = ttk.Radiobutton(type_frame, text="背景信息 ()", 
                                    variable=self.segment_type_var, value="info")
        info_radio.pack(side=tk.LEFT, padx=10)
        
        content_radio = ttk.Radiobutton(type_frame, text="内容指令 <>", 
                                       variable=self.segment_type_var, value="content")
        content_radio.pack(side=tk.LEFT, padx=10)
        
        format_radio = ttk.Radiobutton(type_frame, text="输出格式 []", 
                                      variable=self.segment_type_var, value="format")
        format_radio.pack(side=tk.LEFT, padx=10)
        
        # 片段内容编辑
        content_frame = ttk.Frame(edit_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.segment_text = tk.Text(content_frame, height=10, width=50, wrap=tk.WORD)
        self.segment_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 滚动条
        text_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.segment_text.yview)
        self.segment_text.configure(yscrollcommand=text_scrollbar.set)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 提示区域
        hint_label = ttk.Label(edit_frame, text="提示: 使用 {变量名} 引用存档数据，如 {character.name}", 
                              font=("Arial", 9, "italic"))
        hint_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # 应用按钮
        apply_btn = ttk.Button(edit_frame, text="应用", command=self._add_update_segment)
        apply_btn.pack(anchor=tk.E, padx=10, pady=10)
        
        # 绑定事件
        self.segments_tree.bind("<<TreeviewSelect>>", self._on_segment_select)
    
    def _on_segment_select(self, event) -> None:
        """当选择片段时触发"""
        selection = self.segments_tree.selection()
        if not selection:
            return
        
        # 获取选择的片段
        item_id = selection[0]
        item_data = self.segments_tree.item(item_id)
        segment_idx = int(item_data["values"][0]) - 1  # 索引从0开始
        
        # 获取原始片段文本
        if self.current_template and "prompt_segments" in self.current_template:
            segments = self.current_template["prompt_segments"]
            if 0 <= segment_idx < len(segments):
                segment = segments[segment_idx]
                
                # 设置类型
                segment_type = "info"
                content = segment
                
                if segment.startswith("(") and segment.endswith(")"):
                    segment_type = "info"
                    content = segment[1:-1]
                elif segment.startswith("<") and segment.endswith(">"):
                    segment_type = "content"
                    content = segment[1:-1]
                elif segment.startswith("[") and segment.endswith("]"):
                    segment_type = "format"
                    content = segment[1:-1]
                
                # 更新UI
                self.segment_type_var.set(segment_type)
                self.segment_text.delete("1.0", tk.END)
                self.segment_text.insert("1.0", content)
    
    def _add_update_segment(self) -> None:
        """添加或更新片段"""
        if not self.current_template:
            messagebox.showwarning("警告", "没有选择模板")
            return
        
        # 获取片段内容
        content = self.segment_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "片段内容不能为空")
            return
        
        # 根据类型添加包围符号
        segment_type = self.segment_type_var.get()
        if segment_type == "info":
            segment = f"({content})"
        elif segment_type == "content":
            segment = f"<{content}>"
        elif segment_type == "format":
            segment = f"[{content}]"
        else:
            segment = content
        
        # 检查是更新还是添加
        selection = self.segments_tree.selection()
        if selection:
            # 更新现有片段
            item_id = selection[0]
            item_data = self.segments_tree.item(item_id)
            segment_idx = int(item_data["values"][0]) - 1
            
            if "prompt_segments" not in self.current_template:
                self.current_template["prompt_segments"] = []
            
            if 0 <= segment_idx < len(self.current_template["prompt_segments"]):
                self.current_template["prompt_segments"][segment_idx] = segment
        else:
            # 添加新片段
            if "prompt_segments" not in self.current_template:
                self.current_template["prompt_segments"] = []
            
            self.current_template["prompt_segments"].append(segment)
        
        # 刷新显示
        self._refresh_segments_tree()
        
        # 清空编辑区
        self.segment_text.delete("1.0", tk.END)
    
    def _move_segment(self, direction: int) -> None:
        """移动片段
        
        Args:
            direction: 移动方向，-1上移，1下移
        """
        if not self.current_template or "prompt_segments" not in self.current_template:
            return
        
        selection = self.segments_tree.selection()
        if not selection:
            return
        
        # 获取选择的片段索引
        item_id = selection[0]
        item_data = self.segments_tree.item(item_id)
        segment_idx = int(item_data["values"][0]) - 1
        
        # 计算新位置
        new_idx = segment_idx + direction
        
        # 确保在有效范围内
        if 0 <= new_idx < len(self.current_template["prompt_segments"]):
            # 交换位置
            segments = self.current_template["prompt_segments"]
            segments[segment_idx], segments[new_idx] = segments[new_idx], segments[segment_idx]
            
            # 刷新显示
            self._refresh_segments_tree()
            
            # 选择移动后的项
            for child in self.segments_tree.get_children():
                values = self.segments_tree.item(child)["values"]
                if values[0] == new_idx + 1:  # 显示的索引从1开始
                    self.segments_tree.selection_set(child)
                    self.segments_tree.focus(child)
                    self.segments_tree.see(child)
                    break
    
    def _delete_segment(self) -> None:
        """删除选择的片段"""
        if not self.current_template or "prompt_segments" not in self.current_template:
            return
        
        selection = self.segments_tree.selection()
        if not selection:
            return
        
        # 获取选择的片段索引
        item_id = selection[0]
        item_data = self.segments_tree.item(item_id)
        segment_idx = int(item_data["values"][0]) - 1
        
        # 删除片段
        if 0 <= segment_idx < len(self.current_template["prompt_segments"]):
            del self.current_template["prompt_segments"][segment_idx]
            
            # 刷新显示
            self._refresh_segments_tree()
    
    def _setup_output_tab(self, parent: ttk.Frame) -> None:
        """设置输出和存储选项卡
        
        Args:
            parent: 父容器
        """
        # 创建分隔面板：上面输出格式，下面存储映射
        paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 输出格式区域
        output_frame = ttk.LabelFrame(paned, text="输出字段格式")
        paned.add(output_frame, weight=1)
        
        # 存储映射区域
        storage_frame = ttk.LabelFrame(paned, text="输出存储映射")
        paned.add(storage_frame, weight=1)
        
        # 设置输出格式区域
        output_format_frame = ttk.Frame(output_frame)
        output_format_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 输出格式提示
        hint_label = ttk.Label(output_format_frame, 
                             text="定义模型输出的字段和类型，例如：story:string,choices:array",
                             font=("Arial", 9, "italic"))
        hint_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 输出格式编辑
        self.output_format_text = tk.Text(output_format_frame, height=5, width=50, wrap=tk.WORD)
        self.output_format_text.pack(fill=tk.BOTH, expand=True)
        
        # 设置存储映射区域
        storage_mapping_frame = ttk.Frame(storage_frame)
        storage_mapping_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 映射表格
        columns = ("field", "type", "path")
        self.storage_tree = ttk.Treeview(storage_mapping_frame, columns=columns, show="headings", height=10)
        
        self.storage_tree.heading("field", text="输出字段")
        self.storage_tree.heading("type", text="数据类型")
        self.storage_tree.heading("path", text="存储路径")
        
        self.storage_tree.column("field", width=100)
        self.storage_tree.column("type", width=80)
        self.storage_tree.column("path", width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(storage_mapping_frame, orient=tk.VERTICAL, command=self.storage_tree.yview)
        self.storage_tree.configure(yscrollcommand=scrollbar.set)
        
        self.storage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 编辑区域
        edit_frame = ttk.Frame(storage_frame)
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 字段
        field_label = ttk.Label(edit_frame, text="输出字段:")
        field_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.field_entry = ttk.Entry(edit_frame, width=15)
        self.field_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 类型
        type_label = ttk.Label(edit_frame, text="数据类型:")
        type_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.type_var = tk.StringVar(value="string")
        type_combo = ttk.Combobox(edit_frame, textvariable=self.type_var, width=10,
                                 values=["string", "number", "boolean", "array", "object"])
        type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # 存储路径
        path_label = ttk.Label(edit_frame, text="存储路径:")
        path_label.grid(row=0, column=4, padx=5, pady=5)
        
        self.path_entry = ttk.Entry(edit_frame, width=25)
        self.path_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 按钮
        buttons_frame = ttk.Frame(storage_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_btn = ttk.Button(buttons_frame, text="添加/更新", width=12, command=self._add_output_row)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(buttons_frame, text="删除", width=8, command=lambda: self._delete_output_row(None))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(buttons_frame, text="提取", width=8, command=self._add_new_output)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 绑定事件
        self.storage_tree.bind("<<TreeviewSelect>>", self._on_storage_select)
        self.storage_tree.bind("<Delete>", self._delete_output_row)
    
    def _add_output_row(self, field_name: str = "", data_type: str = "string", attr_name: str = "") -> None:
        """添加或更新输出映射行
        
        Args:
            field_name: 字段名称
            data_type: 数据类型
            attr_name: 属性存储路径
        """
        # 使用输入框的值（如果参数为空）
        field = field_name or self.field_entry.get().strip()
        data_type = data_type or self.type_var.get()
        path = attr_name or self.path_entry.get().strip()
        
        if not field or not path:
            messagebox.showwarning("警告", "字段名和存储路径不能为空")
            return
            
        # 更新模板数据
        if not self.current_template:
            messagebox.showwarning("警告", "没有选择模板")
            return
            
        # 确保存在output_storage
        if "output_storage" not in self.current_template:
            self.current_template["output_storage"] = {}
        
        # 添加或更新映射
        self.current_template["output_storage"][field] = path
        
        # 更新输出格式（如果存在）
        if "output_format" not in self.current_template:
            self.current_template["output_format"] = {}
        
        self.current_template["output_format"][field] = data_type
        
        # 刷新存储树
        self._refresh_storage_tree()
        
        # 清空输入框
        self.field_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
    
    def _delete_output_row(self, row_info) -> None:
        """删除输出映射行
        
        Args:
            row_info: 行信息或事件
        """
        if not self.current_template:
                return
                
        selection = self.storage_tree.selection()
        if not selection:
            return
            
        # 获取选择的项
        item_id = selection[0]
        field = self.storage_tree.item(item_id)["values"][0]
        
        # 从模板中删除
        if "output_storage" in self.current_template and field in self.current_template["output_storage"]:
            del self.current_template["output_storage"][field]
        
        if "output_format" in self.current_template and field in self.current_template["output_format"]:
            del self.current_template["output_format"][field]
        
        # 刷新显示
        self._refresh_storage_tree()
    
    def _add_new_output(self) -> None:
        """从提示片段中提取输出格式"""
        if not self.current_template or "prompt_segments" not in self.current_template:
            messagebox.showwarning("警告", "没有选择模板或模板没有提示片段")
            return
            
        # 查找格式化片段
        format_segments = []
        for segment in self.current_template["prompt_segments"]:
            if segment.startswith("[") and segment.endswith("]"):
                format_segments.append(segment[1:-1])
        
        if not format_segments:
            messagebox.showwarning("警告", "未找到格式化片段")
            return
            
        # 解析格式
        for format_str in format_segments:
            # 查找字段定义
            fields = re.findall(r'([^=,\s]+)=', format_str)
            
            for field in fields:
                # 推断类型
                data_type = "string"
                if "*" in format_str:
                    data_type = "string"  # 默认为字符串
                
                # 添加到存储映射
                self._add_output_row(field, data_type, field)
                
        # 显示消息
        messagebox.showinfo("成功", f"从片段中提取了 {len(fields)} 个输出字段")
        
        # 更新输出格式文本
        self._refresh_output_format_text()

    def _setup_save_tab(self, parent: ttk.Frame) -> None:
        """设置存档数据选项卡
        
        Args:
            parent: 父容器
        """
        # 创建分隔面板：左侧存档列表，右侧属性树
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧存档列表区域
        left_frame = ttk.Frame(paned, width=200)
        paned.add(left_frame, weight=1)
        
        # 右侧属性树区域
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # 设置左侧存档列表
        saves_label = ttk.Label(left_frame, text="存档列表", font=("Arial", 11, "bold"))
        saves_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.saves_list = tk.Listbox(left_frame, height=20, width=30)
        self.saves_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.saves_list.bind("<<ListboxSelect>>", self._on_save_select)
        
        # 刷新按钮
        refresh_btn = ttk.Button(left_frame, text="刷新存档列表", command=self._refresh_saves_list)
        refresh_btn.pack(fill=tk.X, pady=5)
        
        # 设置右侧属性树
        attrs_label = ttk.Label(right_frame, text="数据结构", font=("Arial", 11, "bold"))
        attrs_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建树形控件显示属性
        self.attrs_tree = ttk.Treeview(right_frame, height=20)
        self.attrs_tree.heading("#0", text="存档数据结构")
        self.attrs_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 设置属性树的上下文菜单
        self._setup_attrs_context_menu()
        
        # 提示标签
        tip_label = ttk.Label(right_frame, text="提示: 双击属性复制引用路径", font=("Arial", 9, "italic"))
        tip_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 初始加载
        self._refresh_saves_list()
    
    def _on_save_select(self, event) -> None:
        """处理存档选择事件"""
        if not self.saves_list.curselection():
            return
            
        index = self.saves_list.curselection()[0]
        save_name = self.saves_list.get(index)
            
            # 加载存档
        save_data = load_save(self.save_type, save_name)
        if save_data:
            self._refresh_save_data_tree(save_data, save_name)
    
    def _refresh_save_data_tree(self, save_data: Dict[str, Any], save_name: str) -> None:
        """刷新存档数据树形显示
        
        Args:
            save_data: 存档数据
            save_name: 存档名称
        """
        # 清空树
        for item in self.attrs_tree.get_children():
            self.attrs_tree.delete(item)
        
        # 添加根节点
        root_id = self.attrs_tree.insert("", "end", text=save_name, open=True, values=(save_name, ""))
        
        # 递归添加数据结构
        self._add_data_to_tree(root_id, save_data, "")
    
    def _add_data_to_tree(self, parent_id: str, data: Any, path: str) -> None:
        """递归添加数据到树形控件
        
        Args:
            parent_id: 父节点ID
            data: 数据
            path: 当前路径
        """
        # 处理字典类型
        if isinstance(data, dict):
            for key, value in data.items():
                # 构建完整路径
                new_path = f"{path}.{key}" if path else key
                
                if isinstance(value, (dict, list)):
                    # 复杂类型，创建子节点
                    node_id = self.attrs_tree.insert(
                        parent_id, 
                        "end", 
                        text=key, 
                        open=False, 
                        values=(new_path, type(value).__name__)
                    )
                    # 递归处理子节点
                    self._add_data_to_tree(node_id, value, new_path)
                else:
                    # 简单类型，直接显示值
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    
                    self.attrs_tree.insert(
                        parent_id, 
                        "end", 
                        text=f"{key}: {value_str}", 
                        values=(new_path, type(value).__name__)
                    )
        
        # 处理列表类型
        elif isinstance(data, list):
            for i, item in enumerate(data):
                # 构建完整路径
                new_path = f"{path}[{i}]"
                
                if isinstance(item, (dict, list)):
                    # 复杂类型，创建子节点
                    node_id = self.attrs_tree.insert(
                        parent_id, 
                        "end", 
                        text=f"[{i}]", 
                        open=False, 
                        values=(new_path, type(item).__name__)
                    )
                    # 递归处理子节点
                    self._add_data_to_tree(node_id, item, new_path)
                else:
                    # 简单类型，直接显示值
                    value_str = str(item)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    
                    self.attrs_tree.insert(
                        parent_id, 
                        "end", 
                        text=f"[{i}]: {value_str}", 
                        values=(new_path, type(item).__name__)
                    )
    
    def _setup_attrs_context_menu(self) -> None:
        """设置属性树的上下文菜单"""
        self.attrs_context_menu = tk.Menu(self.attrs_tree, tearoff=0)
        self.attrs_context_menu.add_command(label="复制引用路径", command=self._copy_attribute_path)
        self.attrs_context_menu.add_separator()
        self.attrs_context_menu.add_command(label="插入到提示片段", command=self._insert_to_segment)
        
        def show_menu(event):
            # 显示上下文菜单
            self.attrs_context_menu.post(event.x_root, event.y_root)
        
        # 绑定右键菜单
        self.attrs_tree.bind("<Button-3>", show_menu)
        # 绑定双击事件
        self.attrs_tree.bind("<Double-1>", self._insert_to_segment)
    
    def _copy_attribute_path(self) -> None:
        """复制选中的属性路径到剪贴板"""
        selection = self.attrs_tree.selection()
        if not selection:
            return
            
        # 获取选择的项
        item_id = selection[0]
        path = self.attrs_tree.item(item_id)["values"][0]
        
        # 如果有路径就复制到剪贴板
        if path:
            self.root.clipboard_clear()
            self.root.clipboard_append("{" + path + "}")
            messagebox.showinfo("复制成功", f"已复制 {{{path}}} 到剪贴板")
    
    def _insert_to_segment(self, event=None) -> None:
        """插入属性引用到当前编辑的片段"""
        selection = self.attrs_tree.selection()
        if not selection:
            return
            
        # 获取选择的项
        item_id = selection[0]
        path = self.attrs_tree.item(item_id)["values"][0]
        if path:
            # 只有当提示片段选项卡处于活动状态时才插入
            current_tab = self.notebook.index(self.notebook.select())
            tab_name = self.notebook.tab(current_tab, "text")
            
            if tab_name == "提示片段":
                # 插入到当前编辑的片段
                self.segment_text.insert(tk.INSERT, "{" + path + "}")
            elif tab_name == "输出和存储":
                # 插入到存储路径
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, path)
    
    def _refresh_saves_list(self) -> None:
        """刷新存档列表"""
        # 清空列表
        self.saves_list.delete(0, tk.END)
        
        # 获取所有存档
        saves = list_saves(self.save_type)
        
        # 添加到列表
        for save in saves:
            self.saves_list.insert(tk.END, save)

    def _setup_prompt_processor_tab(self, parent: ttk.Frame) -> None:
        """设置提示词处理选项卡
        
        Args:
            parent: 父容器
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(frame, text="提示词处理器", font=("Arial", 12, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 选择模板
        template_frame = ttk.Frame(frame)
        template_frame.pack(fill=tk.X, pady=5)
        
        template_label = ttk.Label(template_frame, text="当前模板:")
        template_label.pack(side=tk.LEFT, padx=5)
        
        self.template_name_var = tk.StringVar()
        template_name = ttk.Label(template_frame, textvariable=self.template_name_var, font=("Arial", 10, "bold"))
        template_name.pack(side=tk.LEFT, padx=5)
        
        # 构建按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        build_btn = ttk.Button(button_frame, text="构建提示词", command=self._build_prompt)
        build_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = ttk.Button(button_frame, text="复制到剪贴板", command=self._copy_prompt)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # 预览区域
        preview_label = ttk.Label(frame, text="提示词预览:")
        preview_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.prompt_preview = tk.Text(frame, height=20, width=80, wrap=tk.WORD)
        self.prompt_preview.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        preview_scroll = ttk.Scrollbar(self.prompt_preview, orient=tk.VERTICAL, command=self.prompt_preview.yview)
        self.prompt_preview.configure(yscrollcommand=preview_scroll.set)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _build_prompt(self) -> None:
        """构建模板提示词"""
        if not self.current_template or "prompt_segments" not in self.current_template:
            messagebox.showwarning("警告", "没有选择模板或模板没有提示片段")
            return
            
        # 获取模板片段
        segments = self.current_template.get("prompt_segments", [])
        
        # 构建提示词
        try:
            prompt = self.prompt_processor.build_prompt(segments)
            
            # 显示到预览区域
            self.prompt_preview.delete("1.0", tk.END)
            self.prompt_preview.insert("1.0", prompt)
            
        except Exception as e:
            messagebox.showerror("错误", f"构建提示词失败: {str(e)}")
    
    def _copy_prompt(self) -> None:
        """复制提示词到剪贴板"""
        prompt = self.prompt_preview.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("警告", "没有可复制的提示词")
            return
            
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        
        messagebox.showinfo("复制成功", "提示词已复制到剪贴板")
    
    def _setup_preview_tab(self, parent: ttk.Frame) -> None:
        """设置JSON预览选项卡
        
        Args:
            parent: 父容器
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题和提示
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="JSON预览", font=("Arial", 12, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        format_btn = ttk.Button(button_frame, text="格式化", command=self._format_json)
        format_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = ttk.Button(button_frame, text="复制", command=self._copy_json)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(button_frame, text="编辑", command=self._apply_json_edits)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # JSON预览区域
        self.json_preview = tk.Text(frame, height=25, width=80, wrap=tk.NONE)
        self.json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.json_preview.xview)
        h_scroll.pack(fill=tk.X)
        self.json_preview.configure(xscrollcommand=h_scroll.set)
        
        v_scroll = ttk.Scrollbar(self.json_preview, orient=tk.VERTICAL, command=self.json_preview.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_preview.configure(yscrollcommand=v_scroll.set)
    
    def _edit_json_dialog(self, title: str, json_str: str) -> Optional[str]:
        """显示JSON编辑对话框
        
        Args:
            title: 对话框标题
            json_str: JSON字符串
            
        Returns:
            编辑后的JSON字符串，取消则返回None
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 编辑区域
        edit_frame = ttk.Frame(dialog)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        json_text = tk.Text(edit_frame, height=25, width=80, wrap=tk.NONE)
        json_text.pack(fill=tk.BOTH, expand=True)
        json_text.insert("1.0", json_str)
        
        # 添加滚动条
        h_scroll = ttk.Scrollbar(edit_frame, orient=tk.HORIZONTAL, command=json_text.xview)
        h_scroll.pack(fill=tk.X)
        json_text.configure(xscrollcommand=h_scroll.set)
        
        v_scroll = ttk.Scrollbar(json_text, orient=tk.VERTICAL, command=json_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        json_text.configure(yscrollcommand=v_scroll.set)
        
        # 格式化按钮
        def format_json():
            try:
                content = json_text.get("1.0", tk.END).strip()
                data = json.loads(content)
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                
                json_text.delete("1.0", tk.END)
                json_text.insert("1.0", formatted)
            except Exception as e:
                messagebox.showerror("格式化错误", f"JSON格式错误: {str(e)}")
                
        format_btn = ttk.Button(dialog, text="格式化", command=format_json)
        format_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 结果变量
        result = {"json": None}
        
        # 确定和取消按钮
        def on_ok():
            try:
                content = json_text.get("1.0", tk.END).strip()
                # 验证JSON格式
                json.loads(content)
                result["json"] = content
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("JSON错误", f"JSON格式错误: {str(e)}")
        
        def on_cancel():
            result["json"] = None
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ok_btn = ttk.Button(btn_frame, text="确定", command=on_ok)
        ok_btn.pack(side=tk.RIGHT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # 等待对话框关闭
        dialog.wait_window()
        
        return result["json"]

def run_editor():
    """运行模板编辑器"""
    editor = TemplateEditor()
    editor.run()

if __name__ == "__main__":
    run_editor() 