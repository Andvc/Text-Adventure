"""
游戏流程核心控制模块

负责调度和管理整个游戏流程，包括开局和主循环
"""

from typing import Optional

# 导入开局流程控制器
from gameflow.starting.world_setting import WorldSettingFlow
# 后续会导入角色创建和其他流程控制器

class GameFlow:
    """游戏流程控制器，负责管理整个游戏流程"""
    
    def __init__(self):
        """初始化游戏流程控制器"""
        # 初始化各子流程控制器
        self.world_setting = WorldSettingFlow()
        # 后续会初始化角色创建和其他流程控制器
        
    def start_new_game(self) -> bool:
        """开始新游戏
        
        运行完整的游戏开局流程，包括世界设定、角色创建等
        
        Returns:
            bool: 游戏是否成功启动
        """
        print("\n===== 开始新游戏 =====")
        print("欢迎来到文字冒险游戏！")
        
        # 第一步：世界观设定
        if not self.world_setting.start():
            print("世界设定未完成，游戏无法继续。")
            return False
        
        # 第二步：角色创建（待实现）
        # if not self.character_creation.start():
        #     print("角色创建未完成，游戏无法继续。")
        #     return False
        
        # 暂时跳过角色创建
        print("\n角色创建将在未来实现，暂时跳过...")
        
        # 第三步：开始主线故事（待实现）
        print("\n===== 开始冒险 =====")
        print("世界已设定，你的冒险即将开始...")
        
        # 调用主流程（待实现）
        print("主流程将在未来实现，游戏开局完成！")
        
        return True
    
    def load_game(self, save_id: Optional[str] = None) -> bool:
        """加载已有游戏
        
        Args:
            save_id: 存档ID，如果为None则显示存档列表让用户选择
            
        Returns:
            bool: 游戏是否成功加载
        """
        print("\n===== 加载游戏 =====")
        print("加载游戏功能将在未来实现...")
        return False
    
    def run(self) -> None:
        """运行游戏主入口
        
        显示主菜单并执行用户选择的操作
        """
        while True:
            print("\n===== 主菜单 =====")
            print("[1] 开始新游戏")
            print("[2] 加载游戏")
            print("[3] 退出")
            
            try:
                choice = int(input("\n请选择操作: "))
                if choice == 1:
                    self.start_new_game()
                elif choice == 2:
                    self.load_game()
                elif choice == 3:
                    print("\n感谢游玩，再见！")
                    break
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n游戏被中断...")
                break
            except Exception as e:
                print(f"\n发生错误: {str(e)}") 