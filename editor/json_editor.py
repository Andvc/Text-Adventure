"""
JSON编辑器主模块

提供一站式JSON编辑工具，支持编辑游戏数据、存档数据和故事模板
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import traceback
from typing import Dict, Any, List, Optional, Tuple

# 导入编辑器模块
from editor.widgets import JsonTreeview, FileListFrame, StatusBar
import editor.config as config

# 导入数据管理模块
from data.data_manager import list_saves, load_save

class JsonEditor:
    """JSON编辑器主类"""
    
    def __init__(self):
        """初始化JSON编辑器"""
        # 初始化主窗口
        self.root = tk.Tk()
        self.root.title("JSON编辑器")
        self.root.geometry(f"{config.DEFAULT_WINDOW_SIZE[0]}x{config.DEFAULT_WINDOW_SIZE[1]}")
        
        # 当前编辑的文件
        self.current_file: Optional[Path] = None
        self.file_data: Dict[str, Any] = {}
        self.has_changes = False
        
        # 设置UI
        self._setup_ui()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        """设置UI界面"""
        # 主分割面板
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 文件列表
        left_frame = ttk.Frame(main_paned, width=250)
        main_paned.add(left_frame, weight=1)
        
        # 右侧面板 - 编辑区域
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        # 设置左侧文件列表
        self._setup_file_lists(left_frame)
        
        # 设置右侧编辑区域
        self._setup_editor(right_frame)
        
        # 设置状态栏
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.set_status("就绪")
    
    def _setup_file_lists(self, parent):
        """设置文件列表区域
        
        Args:
            parent: 父容器
        """
        # 创建笔记本容器
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 为每个文件类型创建选项卡
        self.file_lists = {}
        
        for file_type, info in config.FILE_TYPES.items():
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"{info['icon']} {info['name']}")
            
            # 创建文件列表
            file_list = FileListFrame(tab, info['name'], info['dir'], info['pattern'])
            file_list.pack(fill=tk.BOTH, expand=True)
            
            # 设置文件选择事件
            file_list.on_file_selected = lambda path, type=file_type: self._load_file(path, type)
            
            # 保存列表引用
            self.file_lists[file_type] = file_list
    
    def _setup_editor(self, parent):
        """设置编辑区域
        
        Args:
            parent: 父容器
        """
        # 编辑器标题和工具栏
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.title_label = ttk.Label(header_frame, text="未打开文件", font=config.HEADER_FONT)
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # 按钮区域
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        # 保存按钮
        self.save_btn = ttk.Button(btn_frame, text="保存", width=8, command=self._save_file)
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        # 重载按钮
        reload_btn = ttk.Button(btn_frame, text="重新加载", width=10, command=self._reload_file)
        reload_btn.pack(side=tk.LEFT, padx=2)
        
        # 验证按钮
        validate_btn = ttk.Button(btn_frame, text="验证", width=8, command=self._validate_json)
        validate_btn.pack(side=tk.LEFT, padx=2)
        
        # 测试模板按钮
        self.test_template_btn = ttk.Button(
            btn_frame, text="测试模板", width=10, 
            command=self._test_template
        )
        self.test_template_btn.pack(side=tk.LEFT, padx=2)
        
        # 文本编辑切换按钮
        self.text_edit_btn = ttk.Button(
            btn_frame, text="文本编辑", width=10, 
            command=self._toggle_text_edit
        )
        self.text_edit_btn.pack(side=tk.LEFT, padx=2)
        
        # 创建JSON树和文本编辑的容器框架
        self.editor_container = ttk.Frame(parent)
        self.editor_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建JSON树形视图
        self.tree_frame = ttk.Frame(self.editor_container)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.json_tree = JsonTreeview(self.tree_frame)
        self.json_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.json_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 设置数据变更回调
        self.json_tree.on_data_changed = self._on_data_changed
        
        # 创建文本编辑器（初始不显示）
        self.text_frame = ttk.Frame(self.editor_container)
        
        self.text_editor = tk.Text(self.text_frame, wrap=tk.NONE, font=config.CODE_FONT)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        text_yscroll = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        text_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor["yscrollcommand"] = text_yscroll.set
        
        text_xscroll = ttk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL, command=self.text_editor.xview)
        text_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_editor["xscrollcommand"] = text_xscroll.set
        
        # 当前编辑模式（树或文本）
        self.text_edit_mode = False
    
    def _load_file(self, file_path, file_type=None):
        """加载文件
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
        """
        # 检查是否有未保存的更改
        if self.has_changes:
            save = messagebox.askyesnocancel("未保存的更改", 
                                           "当前文件有未保存的更改，是否保存？")
            if save is None:  # 取消
                return
            if save:  # 是
                self._save_file()
        
        self.current_file = Path(file_path)
        
        try:
            # 读取文件
            with open(file_path, "r", encoding="utf-8") as f:
                self.file_data = json.load(f)
            
            # 更新UI
            self.title_label.config(text=f"编辑: {self.current_file.name}")
            self.json_tree.load_json(self.file_data)
            self._update_text_editor()
            
            # 更新状态
            self.has_changes = False
            self.status_bar.set_status(f"已加载文件")
            self.status_bar.set_path(file_path)
            
        except Exception as e:
            messagebox.showerror("加载错误", f"无法加载文件 {file_path}:\n{str(e)}")
            traceback.print_exc()
    
    def _save_file(self):
        """保存当前文件"""
        if not self.current_file:
            return
        
        try:
            # 如果在文本编辑模式，先应用更改
            if self.text_edit_mode:
                self._apply_text_changes()
            
            # 写入文件
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.file_data, f, ensure_ascii=False, indent=config.JSON_INDENT)
            
            # 更新状态
            self.has_changes = False
            self.status_bar.set_status(f"已保存文件")
            
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存文件 {self.current_file}:\n{str(e)}")
            traceback.print_exc()
    
    def _reload_file(self):
        """重新加载当前文件"""
        if not self.current_file:
            return
        
        # 检查是否有未保存的更改
        if self.has_changes:
            reload = messagebox.askyesno("未保存的更改", 
                                        "当前文件有未保存的更改，重新加载将丢失这些更改。是否继续？")
            if not reload:
                return
        
        # 重新加载
        self._load_file(self.current_file)
    
    def _validate_json(self):
        """验证JSON结构"""
        if not self.current_file:
            return
        
        # 如果在文本编辑模式，先尝试解析文本
        if self.text_edit_mode:
            try:
                json_str = self.text_editor.get("1.0", tk.END)
                json.loads(json_str)  # 只解析不赋值
                messagebox.showinfo("验证成功", "JSON格式有效")
            except json.JSONDecodeError as e:
                line, col = e.lineno, e.colno
                messagebox.showerror("验证失败", f"JSON格式无效:\n行 {line}, 列 {col}: {str(e)}")
                # 尝试聚焦到错误位置
                self.text_editor.mark_set(tk.INSERT, f"{line}.{col}")
                self.text_editor.see(f"{line}.{col}")
        else:
            # 树形视图模式，JSON总是有效的
            messagebox.showinfo("验证成功", "JSON格式有效")
    
    def _toggle_text_edit(self):
        """切换文本编辑模式"""
        if not self.current_file:
            return
        
        if self.text_edit_mode:
            # 从文本模式切换到树形模式
            try:
                self._apply_text_changes()
                self.text_frame.pack_forget()
                self.tree_frame.pack(fill=tk.BOTH, expand=True)
                self.text_edit_btn.config(text="文本编辑")
                self.text_edit_mode = False
            except Exception as e:
                messagebox.showerror("解析错误", f"无法解析JSON文本:\n{str(e)}")
                # 保持在文本编辑模式
        else:
            # 从树形模式切换到文本模式
            self._update_text_editor()
            self.tree_frame.pack_forget()
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.text_edit_btn.config(text="树形编辑")
            self.text_edit_mode = True
    
    def _update_text_editor(self):
        """更新文本编辑器内容"""
        # 清空文本编辑器
        self.text_editor.delete("1.0", tk.END)
        
        # 格式化并插入JSON
        json_str = json.dumps(self.file_data, ensure_ascii=False, indent=config.JSON_INDENT)
        self.text_editor.insert("1.0", json_str)
    
    def _apply_text_changes(self):
        """应用文本编辑器的更改"""
        try:
            # 获取文本内容
            json_str = self.text_editor.get("1.0", tk.END)
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 更新数据
            self.file_data = data
            
            # 更新树形视图
            self.json_tree.load_json(self.file_data)
            
            # 标记有更改
            self.has_changes = True
            
        except json.JSONDecodeError as e:
            line, col = e.lineno, e.colno
            raise ValueError(f"JSON格式无效，行 {line}, 列 {col}: {str(e)}")
    
    def _on_data_changed(self):
        """数据变更处理"""
        # 标记有未保存的更改
        self.has_changes = True
        
        # 如果在树形模式，同步更新文本编辑器但不显示
        if not self.text_edit_mode:
            self._update_text_editor()
    
    def _on_close(self):
        """窗口关闭处理"""
        # 检查是否有未保存的更改
        if self.has_changes:
            save = messagebox.askyesnocancel("未保存的更改", 
                                           "有未保存的更改，是否保存？")
            if save is None:  # 取消
                return
            if save:  # 是
                self._save_file()
        
        # 关闭窗口
        self.root.destroy()
    
    def _toggle_data_source(self, data_source_var, save_dropdown, data_frame, save_info_frame):
        """切换数据源选择
        
        Args:
            data_source_var: 数据源变量
            save_dropdown: 存档下拉框
            data_frame: 数据编辑框架
            save_info_frame: 存档信息框架
        """
        source = data_source_var.get()
        if source == "default":
            # 使用默认测试数据
            save_dropdown.config(state='disabled')
            data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            save_info_frame.pack_forget()
        else:
            # 使用现有存档
            save_dropdown.config(state='readonly')
            save_info_frame.pack(fill=tk.X, pady=5)
            data_frame.pack_forget()  # 隐藏测试数据编辑框
            save_name = save_dropdown.get()
            if save_name:
                self._update_save_info(save_name, save_info_frame)
    
    def _update_save_info(self, save_name, save_info_frame):
        """更新存档信息
        
        Args:
            save_name: 存档名称
            save_info_frame: 存档信息框架
        """
        # 清空原有信息
        for widget in save_info_frame.winfo_children():
            widget.destroy()
        
        if not save_name or save_name == "无可用存档":
            ttk.Label(save_info_frame, text="没有选择存档").pack(anchor=tk.W, pady=2)
            return
        
        # 加载存档数据
        save_data = load_save("character", save_name)
        if not save_data:
            ttk.Label(save_info_frame, text=f"无法加载存档: {save_name}").pack(anchor=tk.W, pady=2)
            return
        
        # 显示基本信息
        ttk.Label(save_info_frame, text=f"存档ID: {save_data.get('id', '未知')}").pack(anchor=tk.W, pady=2)
        
        # 显示角色信息
        character = save_data.get('character', {})
        if character:
            ttk.Label(save_info_frame, text=f"角色名称: {character.get('name', '未知')}").pack(anchor=tk.W, pady=2)
            ttk.Label(save_info_frame, text=f"种族: {character.get('race', '未知')}").pack(anchor=tk.W, pady=2)
            ttk.Label(save_info_frame, text=f"职业: {character.get('class', '未知')}").pack(anchor=tk.W, pady=2)
        
        # 显示纪元信息
        era = save_data.get('era', {})
        if era:
            ttk.Label(save_info_frame, text=f"纪元: {era.get('name', '未知')}").pack(anchor=tk.W, pady=2)
    
    def _test_template(self):
        """测试当前模板
        
        创建临时存档数据，生成提示词并调用API获取响应
        """
        # 检查是否打开了文件
        if not self.current_file:
            messagebox.showwarning("未打开文件", "请先打开一个模板文件")
            return
        
        # 确保保存当前更改
        if self.has_changes:
            if messagebox.askyesno("未保存的更改", "当前文件有未保存的更改，是否先保存？"):
                if not self._save_file():
                    return  # 保存失败，终止测试
        
        try:
            # 获取当前模板数据
            template_data = self.file_data
            template_id = template_data.get("template_id")
            
            if not template_id:
                messagebox.showerror("无效模板", "当前文件不是有效的模板，缺少template_id字段")
                return
            
            # 显示测试配置对话框
            test_dialog = self._create_test_dialog(template_data)
            
        except Exception as e:
            messagebox.showerror("测试失败", f"测试模板时出错:\n{str(e)}")
            traceback.print_exc()

    def _create_test_dialog(self, template_data):
        """创建测试配置对话框
        
        Args:
            template_data: 模板数据
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(f"测试模板：{template_data.get('name', '未命名')}")
        dialog.geometry("600x500")  # 增加高度以容纳新组件
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示模板基本信息
        info_frame = ttk.LabelFrame(main_frame, text="模板信息")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"ID: {template_data.get('template_id', '未知')}").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text=f"名称: {template_data.get('name', '未知')}").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text=f"描述: {template_data.get('description', '无')}").pack(anchor=tk.W, pady=2)
        
        # 添加数据选择框架
        data_selection_frame = ttk.LabelFrame(main_frame, text="测试数据选择")
        data_selection_frame.pack(fill=tk.X, pady=5)
        
        # 创建单选按钮变量
        data_source_var = tk.StringVar(value="default")  # 默认使用测试数据
        
        # 添加单选按钮
        ttk.Radiobutton(
            data_selection_frame, 
            text="使用默认测试数据", 
            variable=data_source_var,
            value="default",
            command=lambda: self._toggle_data_source(data_source_var, save_dropdown, data_frame, save_info_frame)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            data_selection_frame, 
            text="选择现有存档", 
            variable=data_source_var,
            value="existing",
            command=lambda: self._toggle_data_source(data_source_var, save_dropdown, data_frame, save_info_frame)
        ).pack(anchor=tk.W, pady=2)
        
        # 创建下拉列表框架
        dropdown_frame = ttk.Frame(data_selection_frame)
        dropdown_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dropdown_frame, text="选择存档:").pack(side=tk.LEFT, padx=5)
        
        # 获取存档列表
        saves = list_saves("character")
        if not saves:
            saves = ["无可用存档"]
        
        # 创建下拉菜单
        save_var = tk.StringVar()
        save_dropdown = ttk.Combobox(dropdown_frame, textvariable=save_var, state="readonly")
        save_dropdown['values'] = saves
        save_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        save_dropdown.bind('<<ComboboxSelected>>', lambda e: self._update_save_info(save_var.get(), save_info_frame))
        
        # 默认选择第一个存档
        if saves and saves[0] != "无可用存档":
            save_dropdown.current(0)
        
        # 创建存档信息框架
        save_info_frame = ttk.LabelFrame(main_frame, text="存档信息")
        save_info_frame.pack(fill=tk.X, pady=5)
        
        # 初始时不显示存档信息
        save_info_frame.pack_forget()
        
        # 创建测试数据框架
        data_frame = ttk.LabelFrame(main_frame, text="测试数据")
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建示例存档数据
        sample_data = {
            "id": "template_test",
            "era": {
                "name": "测试纪元",
                "era_number": 1,
                "key_features_joined": "魔法, 科技, 混沌",
                "dominant_races_joined": "人类, 精灵, 矮人",
                "magic_system": "元素魔法",
                "technology_level": "蒸汽朋克",
                "history": "这是一个充满魔法与科技的世界，经历了无数战争与和平..."
            },
            "character": {
                "name": "测试角色",
                "level": "初学者",
                "race": "人类",
                "class": "法师"
            },
            "world": "艾塔莱亚",
            "current_location": "魔法学院",
            "current_state": "学习魔法",
            "inventory": ["魔法书", "药水", "法杖"],
            "story": "角色正在魔法学院学习基础魔法，遇到了一个奇怪的难题...",
            "choice1": "寻求导师帮助",
            "choice2": "自己研究解决",
            "choice3": "放弃这个难题",
            "selected_choice": "自己研究解决",
            "summary": "这是一个关于魔法学徒成长的故事"
        }
        
        # 创建文本编辑框用于编辑测试数据
        data_editor = tk.Text(data_frame, wrap=tk.NONE, height=10, font=config.CODE_FONT)
        data_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加测试数据到编辑框
        data_editor.insert("1.0", json.dumps(sample_data, indent=2, ensure_ascii=False))
        
        # 添加滚动条
        data_scroll = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=data_editor.yview)
        data_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        data_editor["yscrollcommand"] = data_scroll.set
        
        # 按钮框架 - 确保放在底部，更加明显
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        
        # 测试按钮 - 增加宽度使其更加明显
        test_btn = ttk.Button(
            button_frame, text="开始测试", 
            width=15,
            command=lambda: self._run_template_test(
                template_data, 
                data_editor, 
                dialog, 
                data_source_var.get(), 
                save_var.get() if data_source_var.get() == "existing" else None
            )
        )
        test_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, text="取消", 
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # 初始状态设置
        save_dropdown.config(state='disabled')  # 默认禁用存档选择
        
        return dialog

    def _run_template_test(self, template_data, data_editor, dialog, data_source, selected_save=None):
        """运行模板测试
        
        Args:
            template_data: 模板数据
            data_editor: 数据编辑器
            dialog: 对话框
            data_source: 数据来源 ('default' 或 'existing')
            selected_save: 选择的存档名称
        """
        try:
            # 临时保存模板（确保最新版本可用）
            template_id = template_data.get("template_id")
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storyline", "templates")
            temp_path = os.path.join(temp_dir, f"{template_id}.json")
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # 根据数据源获取测试数据
            if data_source == "existing" and selected_save:
                # 使用现有存档
                save_id = selected_save
                test_data = load_save("character", save_id)
                if not test_data:
                    messagebox.showerror("存档错误", f"无法加载存档: {save_id}")
                    return
            else:
                # 使用编辑器中的自定义数据，但不创建临时文件
                save_id = "测试数据"  # 只用于显示，不创建实际存档
                test_data_str = data_editor.get("1.0", tk.END)
                test_data = json.loads(test_data_str)
            
            # 导入必要模块
            from storyline.storyline_manager import StorylineManager
            from ai.prompt_processor import PromptProcessor
            
            # 创建管理器和处理器
            manager = StorylineManager()
            processor = PromptProcessor()
            
            # 获取模板
            template = manager.load_template(template_id)
            if not template:
                messagebox.showerror("模板错误", f"无法加载模板: {template_id}")
                return
            
            # 处理提示片段（使用PromptProcessor而不是StorylineManager的方法）
            prompt_segments = template.get("prompt_segments", [])
            processed_segments = []
            for segment in prompt_segments:
                processed = processor._replace_placeholders(segment, test_data)
                processed_segments.append(processed)
            
            # 生成最终提示词（传递test_data参数）
            if "prompt_template" in template:
                custom_template = template["prompt_template"]
                custom_processor = PromptProcessor(custom_template)
                prompt = custom_processor.build_prompt(processed_segments, test_data)
            else:
                prompt = processor.build_prompt(processed_segments, test_data)
            
            # 创建结果窗口
            self._show_test_results(dialog, prompt, template_id, save_id)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("数据错误", f"测试数据不是有效的JSON格式:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("测试错误", f"测试过程中出错:\n{str(e)}")
            traceback.print_exc()

    def _show_test_results(self, parent_dialog, prompt, template_id, save_id):
        """显示测试结果
        
        Args:
            parent_dialog: 父对话框
            prompt: 生成的提示词
            template_id: 模板ID
            save_id: 存档ID
        """
        # 关闭父对话框
        parent_dialog.destroy()
        
        # 创建结果窗口
        result_dialog = tk.Toplevel(self.root)
        result_dialog.title(f"模板测试结果：{template_id}")
        result_dialog.geometry("900x700")
        result_dialog.transient(self.root)
        
        # 主框架
        main_frame = ttk.Frame(result_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 提示词部分
        prompt_frame = ttk.LabelFrame(main_frame, text="生成的提示词")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=12, font=config.CODE_FONT)
        prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prompt_text.insert("1.0", prompt)
        prompt_text.config(state=tk.DISABLED)  # 设为只读
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=prompt_text.yview)
        prompt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        prompt_text["yscrollcommand"] = prompt_scroll.set
        
        # API响应部分
        response_frame = ttk.LabelFrame(main_frame, text="API响应")
        response_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        response_text = tk.Text(response_frame, wrap=tk.WORD, height=12, font=config.CODE_FONT)
        response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        response_text.insert("1.0", "点击下方的'调用API'按钮获取响应...")
        
        response_scroll = ttk.Scrollbar(response_frame, orient=tk.VERTICAL, command=response_text.yview)
        response_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        response_text["yscrollcommand"] = response_scroll.set
        
        # 解析结果部分
        parsed_frame = ttk.LabelFrame(main_frame, text="解析结果")
        parsed_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        parsed_text = tk.Text(parsed_frame, wrap=tk.WORD, height=12, font=config.CODE_FONT)
        parsed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        parsed_text.insert("1.0", "API响应解析结果将显示在这里...")
        
        parsed_scroll = ttk.Scrollbar(parsed_frame, orient=tk.VERTICAL, command=parsed_text.yview)
        parsed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        parsed_text["yscrollcommand"] = parsed_scroll.set
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 状态标签
        status_label = ttk.Label(button_frame, text="准备就绪")
        status_label.pack(side=tk.LEFT)
        
        # 调用API按钮
        call_api_btn = ttk.Button(
            button_frame, text="调用API", 
            command=lambda: self._call_api_and_show(prompt, response_text, parsed_text, status_label)
        )
        call_api_btn.pack(side=tk.RIGHT, padx=5)
        
        # 关闭按钮
        close_btn = ttk.Button(
            button_frame, text="关闭", 
            command=result_dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _call_api_and_show(self, prompt, response_text, parsed_text, status_label):
        """调用API并显示结果
        
        Args:
            prompt: 提示词
            response_text: 响应文本框
            parsed_text: 解析结果文本框
            status_label: 状态标签
        """
        try:
            # 更新状态
            status_label.config(text="正在调用API...")
            self.root.update()
            
            # 导入API连接器
            from ai.api_connector import AIModelConnector
            from ai.output_parsers import OutputParser
            
            # 创建连接器
            api_connector = AIModelConnector()
            
            # 调用API
            response = api_connector.call_api(prompt)
            
            # 显示原始响应
            response_text.config(state=tk.NORMAL)
            response_text.delete("1.0", tk.END)
            response_text.insert("1.0", response)
            response_text.config(state=tk.DISABLED)
            
            # 解析响应
            result = OutputParser.parse(response, parser_type="json")
            
            # 显示解析结果
            parsed_text.config(state=tk.NORMAL)
            parsed_text.delete("1.0", tk.END)
            
            if result:
                parsed_text.insert("1.0", json.dumps(result, indent=2, ensure_ascii=False))
            else:
                parsed_text.insert("1.0", "解析失败，无法从响应中提取有效JSON")
            
            parsed_text.config(state=tk.DISABLED)
            
            # 更新状态
            status_label.config(text="API调用完成")
            
        except Exception as e:
            # 更新状态
            status_label.config(text=f"错误: {str(e)}")
            # 显示错误信息
            messagebox.showerror("API错误", f"调用API时出错:\n{str(e)}")
            traceback.print_exc()

    def run(self):
        """运行编辑器"""
        # 进入主循环
        self.root.mainloop()


def main():
    """编辑器主函数"""
    editor = JsonEditor()
    editor.run()


if __name__ == "__main__":
    main() 