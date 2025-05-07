#!/usr/bin/env python3
"""
游戏流程核心模块

提供游戏流程控制和管理的基本类
"""

class GameFlow:
    """游戏流程管理类
    
    负责管理和控制游戏的整体流程，包括初始化、状态转换等
    """
    
    def __init__(self):
        """初始化游戏流程管理器"""
        self.current_state = None
        self.states = {}
        
    def add_state(self, name, state_handler):
        """添加一个游戏状态
        
        Args:
            name (str): 状态名称
            state_handler (callable): 状态处理函数或对象
        """
        self.states[name] = state_handler
        
    def set_state(self, name):
        """设置当前游戏状态
        
        Args:
            name (str): 状态名称
        
        Returns:
            bool: 是否成功设置状态
        """
        if name in self.states:
            self.current_state = name
            return True
        return False
    
    def run_current_state(self, *args, **kwargs):
        """运行当前状态
        
        Args:
            *args: 传递给状态处理函数的位置参数
            **kwargs: 传递给状态处理函数的关键字参数
            
        Returns:
            any: 状态处理函数的返回值
        """
        if self.current_state and self.current_state in self.states:
            return self.states[self.current_state](*args, **kwargs)
        return None
    
    def transition(self, next_state, *args, **kwargs):
        """从当前状态转换到下一个状态
        
        Args:
            next_state (str): 下一个状态名称
            *args: 传递给下一个状态的位置参数
            **kwargs: 传递给下一个状态的关键字参数
            
        Returns:
            any: 下一个状态处理函数的返回值，如果状态不存在则返回None
        """
        if self.set_state(next_state):
            return self.run_current_state(*args, **kwargs)
        return None 