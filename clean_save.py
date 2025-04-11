#!/usr/bin/env python3
"""
清理simple_loop存档，删除重复的英文字段，只保留中文字段
"""

import json
import os

def clean_save_file():
    """清理simple_loop.json存档文件"""
    save_path = os.path.join("save", "simple_loop.json")
    
    try:
        # 读取存档文件
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # 删除重复的英文字段
        if "角色数据" in save_data:
            character_data = save_data["角色数据"]
            
            # 要删除的英文字段
            fields_to_remove = ["story_content", "last_choice", "last_story"]
            
            # 删除字段
            for field in fields_to_remove:
                if field in character_data:
                    print(f"删除字段: {field}")
                    del character_data[field]
        
        # 保存回文件
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        
        print(f"存档文件已清理: {save_path}")
        return True
        
    except Exception as e:
        print(f"清理存档出错: {str(e)}")
        return False

if __name__ == "__main__":
    clean_save_file() 