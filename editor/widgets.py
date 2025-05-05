"""
编辑器UI组件模块

包含自定义的UI组件，提供更好的JSON编辑体验
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable

class JsonTreeview(ttk.Treeview):
    """JSON数据树形视图控件"""
    
    def __init__(self, master, **kw):
        """初始化JSON树形视图
        
        Args:
            master: 父容器
            **kw: 传递给Treeview的关键字参数
        """
        # 默认列设置
        columns = kw.pop("columns", ("value", "type"))
        super().__init__(master, columns=columns, **kw)
        
        # 设置列标题
        self.heading("#0", text="键")
        self.heading("value", text="值")
        self.heading("type", text="类型")
        
        # 设置列宽度
        self.column("#0", width=250)
        self.column("value", width=350)
        self.column("type", width=100)
        
        # 创建上下文菜单
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self._edit_selected)
        self.context_menu.add_command(label="添加子项", command=self._add_child)
        self.context_menu.add_command(label="删除", command=self._delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制路径", command=self._copy_path)
        
        # 绑定事件
        self.bind("<Button-3>", self._show_context_menu)
        self.bind("<Double-1>", self._edit_selected)
        
        # 保存当前数据和回调函数
        self.data = {}
        self.on_data_changed = None
    
    def _show_context_menu(self, event):
        """显示上下文菜单"""
        item = self.identify_row(event.y)
        if item:
            self.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _edit_selected(self, event=None):
        """编辑选中的项"""
        if not self.selection():
            return
        
        item_id = self.selection()[0]
        item_path = self._get_item_path(item_id)
        
        # 获取当前值
        item_value = self._get_value_by_path(item_path)
        
        # 编辑窗口
        edit_window = tk.Toplevel(self)
        edit_window.title("编辑值")
        edit_window.geometry("400x300")
        edit_window.resizable(True, True)
        
        # 值类型标签
        type_label = ttk.Label(edit_window, text=f"类型: {type(item_value).__name__}")
        type_label.pack(padx=10, pady=(10, 5), anchor=tk.W)
        
        # 值编辑框
        frame = ttk.Frame(edit_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        if isinstance(item_value, (dict, list)):
            # 复杂类型使用JSON编辑
            text = tk.Text(frame, wrap=tk.NONE, font=("Courier New", 12))
            text.pack(fill=tk.BOTH, expand=True)
            
            # 添加滚动条
            yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
            yscroll.pack(side=tk.RIGHT, fill=tk.Y)
            text['yscrollcommand'] = yscroll.set
            
            # 初始化值
            try:
                json_str = json.dumps(item_value, ensure_ascii=False, indent=2)
                text.insert("1.0", json_str)
            except Exception as e:
                messagebox.showerror("错误", f"无法序列化值: {str(e)}")
                edit_window.destroy()
                return
            
            # 格式化按钮
            format_btn = ttk.Button(edit_window, text="格式化JSON", 
                                   command=lambda: self._format_json(text))
            format_btn.pack(side=tk.LEFT, padx=10, pady=10)
        else:
            # 简单类型使用Entry或Text
            if isinstance(item_value, str) and len(item_value) > 50:
                # 长字符串使用Text
                text = tk.Text(frame, wrap=tk.WORD, height=10, font=("Courier New", 12))
                text.pack(fill=tk.BOTH, expand=True)
                text.insert("1.0", str(item_value))
                
                # 滚动条
                yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
                yscroll.pack(side=tk.RIGHT, fill=tk.Y)
                text['yscrollcommand'] = yscroll.set
            else:
                # 简单值使用Entry
                value_var = tk.StringVar(value=str(item_value))
                entry = ttk.Entry(frame, textvariable=value_var, font=("Courier New", 12))
                entry.pack(fill=tk.X, expand=True)
                text = value_var  # 使text指向StringVar以统一后续处理
        
        # 按钮区域
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 保存按钮
        save_btn = ttk.Button(btn_frame, text="保存", 
                             command=lambda: self._save_edited_value(item_path, text, edit_window, type(item_value)))
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", 
                               command=edit_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _format_json(self, text_widget):
        """格式化JSON文本"""
        try:
            # 获取当前文本
            json_str = text_widget.get("1.0", tk.END)
            # 解析并重新格式化
            data = json.loads(json_str)
            formatted_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 更新文本框
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", formatted_str)
        except Exception as e:
            messagebox.showerror("格式化错误", f"JSON格式错误: {str(e)}")
    
    def _save_edited_value(self, path, text, window, value_type):
        """保存编辑后的值"""
        try:
            # 获取文本内容
            if isinstance(text, tk.StringVar):
                value_str = text.get()
            else:  # Text widget
                value_str = text.get("1.0", tk.END).strip()
            
            # 转换回原始类型
            if value_type == dict or value_type == list:
                try:
                    new_value = json.loads(value_str)
                    if not isinstance(new_value, value_type):
                        raise ValueError(f"值必须是 {value_type.__name__} 类型")
                except json.JSONDecodeError as e:
                    messagebox.showerror("JSON错误", f"无效的JSON格式: {str(e)}")
                    return
            elif value_type == int:
                new_value = int(value_str)
            elif value_type == float:
                new_value = float(value_str)
            elif value_type == bool:
                if value_str.lower() in ('true', 'yes', '1'):
                    new_value = True
                elif value_str.lower() in ('false', 'no', '0'):
                    new_value = False
                else:
                    raise ValueError("布尔值必须是 true/false, yes/no, 或 1/0")
            else:
                new_value = value_str
            
            # 更新数据
            self._set_value_by_path(path, new_value)
            
            # 更新树形视图
            self.refresh()
            
            # 调用变更回调
            if self.on_data_changed:
                self.on_data_changed()
            
            # 关闭窗口
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存值: {str(e)}")
    
    def _add_child(self):
        """添加子项"""
        if not self.selection():
            return
        
        item_id = self.selection()[0]
        item_path = self._get_item_path(item_id)
        
        # 获取当前值
        parent_value = self._get_value_by_path(item_path)
        
        # 只能向字典或列表添加子项
        if not isinstance(parent_value, (dict, list)):
            messagebox.showerror("错误", "只能向对象或数组添加子项")
            return
        
        # 添加新项窗口
        add_window = tk.Toplevel(self)
        add_window.title("添加新项")
        add_window.geometry("400x200")
        
        # 键名输入（只对字典需要）
        key_frame = ttk.Frame(add_window)
        key_frame.pack(fill=tk.X, padx=10, pady=10)
        
        key_var = tk.StringVar()
        if isinstance(parent_value, dict):
            ttk.Label(key_frame, text="键名:").pack(side=tk.LEFT)
            ttk.Entry(key_frame, textvariable=key_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            # 列表项无需键名
            key_var.set("")
            ttk.Label(key_frame, text="添加到数组").pack(side=tk.LEFT)
        
        # 值类型选择
        type_frame = ttk.Frame(add_window)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(type_frame, text="值类型:").pack(side=tk.LEFT)
        
        type_var = tk.StringVar(value="string")
        types = [("字符串", "string"), ("数字", "number"), ("布尔", "boolean"),
                 ("对象", "object"), ("数组", "array")]
        
        for text, value in types:
            ttk.Radiobutton(type_frame, text=text, value=value, 
                          variable=type_var).pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(add_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 确定按钮
        ok_btn = ttk.Button(btn_frame, text="确定", 
                           command=lambda: self._add_new_item(item_path, key_var.get(), 
                                                            type_var.get(), add_window))
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", 
                               command=add_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _add_new_item(self, parent_path, key, value_type, window):
        """添加新项到指定路径"""
        try:
            # 获取父项
            parent_value = self._get_value_by_path(parent_path)
            
            # 创建默认值
            if value_type == "string":
                new_value = ""
            elif value_type == "number":
                new_value = 0
            elif value_type == "boolean":
                new_value = False
            elif value_type == "object":
                new_value = {}
            elif value_type == "array":
                new_value = []
            else:
                new_value = None
            
            # 添加到父项
            if isinstance(parent_value, dict):
                if not key:
                    messagebox.showerror("错误", "对象项必须有键名")
                    return
                
                # 检查键是否已存在
                if key in parent_value:
                    if not messagebox.askyesno("警告", f"键 '{key}' 已存在，是否覆盖?"):
                        return
                
                parent_value[key] = new_value
            elif isinstance(parent_value, list):
                parent_value.append(new_value)
            
            # 更新树形视图
            self.refresh()
            
            # 调用变更回调
            if self.on_data_changed:
                self.on_data_changed()
            
            # 关闭窗口
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("添加错误", f"无法添加新项: {str(e)}")
    
    def _delete_selected(self):
        """删除选中的项"""
        if not self.selection():
            return
        
        item_id = self.selection()[0]
        
        # 根项不能删除
        if item_id == "":
            messagebox.showinfo("提示", "根项不能删除")
            return
        
        # 获取项路径
        item_path = self._get_item_path(item_id)
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除 '{item_path}' 吗?"):
            return
        
        try:
            # 解析路径
            path_parts = item_path.split(".")
            
            # 获取父项和键名
            if len(path_parts) == 1:
                # 顶级项
                key = path_parts[0]
                if key in self.data:
                    del self.data[key]
            else:
                # 嵌套项
                parent_path = ".".join(path_parts[:-1])
                key = path_parts[-1]
                
                parent_value = self._get_value_by_path(parent_path)
                
                if isinstance(parent_value, dict) and key in parent_value:
                    del parent_value[key]
                elif isinstance(parent_value, list) and key.isdigit():
                    index = int(key)
                    if 0 <= index < len(parent_value):
                        del parent_value[index]
            
            # 更新树形视图
            self.refresh()
            
            # 调用变更回调
            if self.on_data_changed:
                self.on_data_changed()
            
        except Exception as e:
            messagebox.showerror("删除错误", f"无法删除项: {str(e)}")
    
    def _copy_path(self):
        """复制选中项的路径"""
        if not self.selection():
            return
        
        item_id = self.selection()[0]
        path = self._get_item_path(item_id)
        
        # 复制到剪贴板
        self.clipboard_clear()
        self.clipboard_append(path)
    
    def _get_item_path(self, item_id):
        """获取树节点的路径"""
        if not item_id:
            return ""
        
        # 构建路径
        path_parts = []
        parent_id = item_id
        
        while parent_id:
            item_text = self.item(parent_id, "text")
            path_parts.insert(0, item_text)
            parent_id = self.parent(parent_id)
        
        return ".".join(path_parts)
    
    def _get_value_by_path(self, path):
        """通过路径获取值"""
        if not path:
            return self.data
        
        current = self.data
        path_parts = path.split(".")
        
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"数组索引 {part} 超出范围")
            else:
                raise KeyError(f"路径 '{path}' 无效")
        
        return current
    
    def _set_value_by_path(self, path, value):
        """通过路径设置值"""
        if not path:
            self.data = value
            return
        
        # 解析路径
        path_parts = path.split(".")
        
        # 单层路径
        if len(path_parts) == 1:
            key = path_parts[0]
            self.data[key] = value
            return
        
        # 多层路径
        parent_path = ".".join(path_parts[:-1])
        key = path_parts[-1]
        
        parent = self._get_value_by_path(parent_path)
        
        if isinstance(parent, dict):
            parent[key] = value
        elif isinstance(parent, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(parent):
                parent[index] = value
            else:
                raise IndexError(f"数组索引 {key} 超出范围")
        else:
            raise TypeError(f"路径 '{parent_path}' 不是有效的父节点")
    
    def load_json(self, data):
        """加载JSON数据到树形视图
        
        Args:
            data: JSON数据（字典或列表）
        """
        self.data = data
        self.refresh()
    
    def refresh(self):
        """刷新树形视图"""
        # 清空现有项
        for item in self.get_children():
            self.delete(item)
        
        # 添加根节点
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                self._add_json_node("", key, value)
        elif isinstance(self.data, list):
            for i, value in enumerate(self.data):
                self._add_json_node("", str(i), value)
    
    def _add_json_node(self, parent, key, value):
        """递归添加JSON节点到树形视图
        
        Args:
            parent: 父节点ID
            key: 键名
            value: 值
        """
        # 确定值类型
        value_type = type(value).__name__
        
        # 值的文本表示
        if isinstance(value, (dict, list)):
            value_text = f"{value_type}: {len(value)}项"
        elif isinstance(value, str):
            # 截断长文本
            value_text = value[:100] + ("..." if len(value) > 100 else "")
        else:
            value_text = str(value)
        
        # 添加节点
        item_id = self.insert(parent, "end", text=key, values=(value_text, value_type))
        
        # 递归添加子节点
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                self._add_json_node(item_id, sub_key, sub_value)
        elif isinstance(value, list):
            for i, sub_value in enumerate(value):
                self._add_json_node(item_id, str(i), sub_value)
                
        return item_id


class FileListFrame(ttk.Frame):
    """文件列表框架"""
    
    def __init__(self, master, title, dir_path, pattern="*.json", **kw):
        """初始化文件列表框架
        
        Args:
            master: 父容器
            title: 框架标题
            dir_path: 文件目录路径
            pattern: 文件匹配模式
            **kw: 传递给Frame的关键字参数
        """
        super().__init__(master, **kw)
        
        self.dir_path = Path(dir_path)
        self.pattern = pattern
        self.on_file_selected = None
        
        # 框架标题
        title_label = ttk.Label(self, text=title, font=("Arial", 12, "bold"))
        title_label.pack(fill=tk.X, pady=(0, 5))
        
        # 文件列表
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_list = tk.Listbox(list_frame, font=("Arial", 11))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list["yscrollcommand"] = scrollbar.set
        
        # 刷新文件列表
        self.refresh()
        
        # 绑定事件
        self.file_list.bind("<<ListboxSelect>>", self._on_select)
        self.file_list.bind("<Double-1>", self._on_double_click)
        
        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 新建按钮
        new_btn = ttk.Button(btn_frame, text="新建", width=8, command=self._create_new)
        new_btn.pack(side=tk.LEFT, padx=2)
        
        # 刷新按钮
        refresh_btn = ttk.Button(btn_frame, text="刷新", width=8, command=self.refresh)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # 删除按钮
        delete_btn = ttk.Button(btn_frame, text="删除", width=8, command=self._delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=2)
    
    def refresh(self):
        """刷新文件列表"""
        # 清空列表
        self.file_list.delete(0, tk.END)
        
        # 添加文件
        for file_path in sorted(self.dir_path.glob(self.pattern)):
            self.file_list.insert(tk.END, file_path.stem)
    
    def _on_select(self, event):
        """文件选择事件处理"""
        if not self.file_list.curselection():
            return
        
        file_name = self.file_list.get(self.file_list.curselection()[0])
        file_path = self.dir_path / f"{file_name}.json"
        
        if self.on_file_selected:
            self.on_file_selected(file_path)
    
    def _on_double_click(self, event):
        """双击文件事件处理"""
        self._on_select(event)  # 直接调用选择处理
    
    def _create_new(self):
        """创建新文件"""
        # 弹出输入窗口
        new_window = tk.Toplevel(self)
        new_window.title("创建新文件")
        new_window.geometry("300x100")
        new_window.resizable(False, False)
        
        # 文件名输入
        name_frame = ttk.Frame(new_window)
        name_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(name_frame, text="文件名:").pack(side=tk.LEFT)
        name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(new_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 确定按钮
        ok_btn = ttk.Button(btn_frame, text="确定", 
                           command=lambda: self._create_file(name_var.get(), new_window))
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", 
                               command=new_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_file(self, name, window):
        """创建新文件
        
        Args:
            name: 文件名
            window: 输入窗口实例
        """
        if not name:
            messagebox.showerror("错误", "文件名不能为空")
            return
        
        # 规范化文件名
        name = name.strip()
        if not name.endswith(".json"):
            file_path = self.dir_path / f"{name}.json"
        else:
            file_path = self.dir_path / name
            name = name[:-5]  # 去除.json后缀
        
        # 检查文件是否已存在
        if file_path.exists():
            if not messagebox.askyesno("警告", f"文件 '{name}.json' 已存在，是否覆盖?"):
                return
        
        try:
            # 创建空JSON文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            
            # 刷新列表
            self.refresh()
            
            # 选择新文件
            items = list(self.file_list.get(0, tk.END))
            if name in items:
                index = items.index(name)
                self.file_list.selection_clear(0, tk.END)
                self.file_list.selection_set(index)
                self.file_list.see(index)
                self._on_select(None)
            
            # 关闭窗口
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("创建错误", f"无法创建文件: {str(e)}")
    
    def _delete_selected(self):
        """删除选中的文件"""
        if not self.file_list.curselection():
            return
        
        file_name = self.file_list.get(self.file_list.curselection()[0])
        file_path = self.dir_path / f"{file_name}.json"
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除 '{file_name}.json' 吗?"):
            return
        
        try:
            # 删除文件
            file_path.unlink()
            
            # 刷新列表
            self.refresh()
            
        except Exception as e:
            messagebox.showerror("删除错误", f"无法删除文件: {str(e)}")


class StatusBar(ttk.Frame):
    """状态栏"""
    
    def __init__(self, master, **kw):
        """初始化状态栏
        
        Args:
            master: 父容器
            **kw: 传递给Frame的关键字参数
        """
        super().__init__(master, **kw)
        
        # 状态消息
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 分隔线
        separator = ttk.Separator(self, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 文件路径
        self.path_var = tk.StringVar()
        path_label = ttk.Label(self, textvariable=self.path_var, anchor=tk.E)
        path_label.pack(side=tk.RIGHT, padx=5)
    
    def set_status(self, message):
        """设置状态消息"""
        self.status_var.set(message)
    
    def set_path(self, path):
        """设置文件路径"""
        self.path_var.set(str(path)) 