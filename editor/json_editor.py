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