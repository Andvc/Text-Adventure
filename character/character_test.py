"""
角色属性模块测试文件

用于测试character_manager.py中的各项功能
"""

import os
import sys

# 添加父目录到系统路径，以便导入character模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from character.character_manager import (
    create_attribute,
    delete_attribute,
    get_attribute,
    set_attribute,
    list_attributes,
    get_all_attributes,
    configure_save_system,
    get_save_location,
    # 导入新增的属性类别相关函数
    get_attribute_category,
    set_attribute_category,
    get_attributes_by_category,
    count_attributes_by_category,
    get_attribute_by_index,
    list_categories,
    # 导入快速创建属性函数
    create_category_attribute,
    # 导入物品属性提取和搜索函数
    get_item_property,
    search_items_by_property
)

def test_basic_operations():
    """测试基本的属性操作功能"""
    print("=== 测试基本属性操作 ===")
    
    # 创建属性
    print("\n1. 创建属性测试:")
    create_attribute("姓名", "测试角色")
    create_attribute("等级", 1)
    create_attribute("力量", 10)
    create_attribute("敏捷", 8)
    create_attribute("智力", 12)
    
    # 尝试创建已存在的属性（应该失败）
    print("\n2. 创建重复属性测试:")
    result = create_attribute("姓名", "另一个角色")
    print(f"创建重复属性结果: {'失败' if not result else '成功'} (预期结果: 失败)")
    
    # 获取属性
    print("\n3. 获取属性测试:")
    name = get_attribute("姓名")
    strength = get_attribute("力量")
    print(f"获取姓名: {name} (预期结果: 测试角色)")
    print(f"获取力量: {strength} (预期结果: 10)")
    
    # 尝试获取不存在的属性
    print("\n4. 获取不存在属性测试:")
    nonexistent = get_attribute("不存在的属性")
    print(f"获取不存在属性结果: {nonexistent} (预期结果: None)")
    
    # 修改属性
    print("\n5. 修改属性测试:")
    set_attribute("等级", 2)
    set_attribute("力量", 12)
    print(f"修改后等级: {get_attribute('等级')} (预期结果: 2)")
    print(f"修改后力量: {get_attribute('力量')} (预期结果: 12)")
    
    # 列出所有属性
    print("\n6. 列出属性测试:")
    attr_list = list_attributes()
    print(f"属性列表: {attr_list}")
    
    # 获取所有属性及其值
    print("\n7. 获取所有属性及值测试:")
    all_attrs = get_all_attributes()
    print(f"所有属性及值: {all_attrs}")
    
    # 删除属性
    print("\n8. 删除属性测试:")
    delete_result = delete_attribute("敏捷")
    print(f"删除敏捷属性结果: {'成功' if delete_result else '失败'} (预期结果: 成功)")
    after_delete = get_attribute("敏捷")
    print(f"删除后获取敏捷: {after_delete} (预期结果: None)")
    
    # 尝试删除不存在的属性
    print("\n9. 删除不存在属性测试:")
    del_nonexistent = delete_attribute("不存在的属性")
    print(f"删除不存在属性结果: {'成功' if del_nonexistent else '失败'} (预期结果: 失败)")

def test_attribute_category():
    """测试属性类别功能"""
    print("\n=== 测试属性类别功能 ===")
    
    # 配置存档位置
    configure_save_system(save_file="category_test.json")
    
    # 创建不同类别的属性
    print("\n1. 创建带类别的属性测试:")
    # 玩家基础属性
    create_attribute("名称", "李逍遥", "基础属性")
    create_attribute("等级", 1, "基础属性")
    create_attribute("生命值", 100, "基础属性")
    
    # 战斗属性
    create_attribute("攻击力", 15, "战斗属性")
    create_attribute("防御力", 10, "战斗属性")
    create_attribute("暴击率", 0.05, "战斗属性")
    
    # 装备
    create_attribute("武器", {"名称": "青锋剑", "攻击": 10}, "装备")
    create_attribute("防具", {"名称": "布衣", "防御": 5}, "装备")
    
    # 状态效果
    create_attribute("中毒", {"持续时间": 3, "每回合伤害": 5}, "状态效果")
    create_attribute("加速", {"持续时间": 2, "敏捷提升": 5}, "状态效果")
    
    # 获取属性类别
    print("\n2. 获取属性类别测试:")
    print(f"'名称'的类别: {get_attribute_category('名称')} (预期结果: 基础属性)")
    print(f"'攻击力'的类别: {get_attribute_category('攻击力')} (预期结果: 战斗属性)")
    print(f"'武器'的类别: {get_attribute_category('武器')} (预期结果: 装备)")
    
    # 修改属性类别
    print("\n3. 修改属性类别测试:")
    print(f"修改前'暴击率'的类别: {get_attribute_category('暴击率')}")
    set_attribute_category("暴击率", "高级战斗属性")
    print(f"修改后'暴击率'的类别: {get_attribute_category('暴击率')} (预期结果: 高级战斗属性)")
    
    # 获取特定类别的属性列表
    print("\n4. 获取类别属性列表测试:")
    basic_attrs = get_attributes_by_category("基础属性")
    print(f"基础属性列表: {basic_attrs} (预期包含: 名称, 等级, 生命值)")
    
    equipment_attrs = get_attributes_by_category("装备")
    print(f"装备列表: {equipment_attrs} (预期包含: 武器, 防具)")
    
    # 计算特定类别的属性数量
    print("\n5. 计算类别属性数量测试:")
    basic_count = count_attributes_by_category("基础属性")
    print(f"基础属性数量: {basic_count} (预期结果: 3)")
    
    status_count = count_attributes_by_category("状态效果")
    print(f"状态效果数量: {status_count} (预期结果: 2)")
    
    # 通过索引获取特定类别的属性
    print("\n6. 通过索引获取属性测试:")
    first_equipment = get_attribute_by_index("装备", 0)
    print(f"第一个装备: {first_equipment}")
    
    second_status = get_attribute_by_index("状态效果", 1)
    print(f"第二个状态效果: {second_status}")
    
    # 边界情况测试
    out_of_bound = get_attribute_by_index("装备", 5)
    print(f"越界索引结果: {out_of_bound} (预期结果: (None, None))")
    
    # 列出所有类别
    print("\n7. 列出所有类别测试:")
    all_categories = list_categories()
    print(f"所有类别: {all_categories}")
    
    # 测试删除属性时类别信息也被删除
    print("\n8. 删除属性时类别信息测试:")
    print(f"删除前'中毒'的类别: {get_attribute_category('中毒')}")
    delete_attribute("中毒")
    print(f"删除后'中毒'的类别: {get_attribute_category('中毒')} (预期结果: None)")
    
    # 测试对没有类别的属性进行操作
    print("\n9. 无类别属性操作测试:")
    create_attribute("金币", 1000)  # 创建无类别属性
    print(f"'金币'的类别: {get_attribute_category('金币')} (预期结果: None)")
    
    # 后续添加类别
    set_attribute_category("金币", "资源")
    print(f"设置类别后'金币'的类别: {get_attribute_category('金币')} (预期结果: 资源)")

def test_chinese_support():
    """测试中文支持"""
    print("\n=== 测试中文支持 ===")
    
    # 中文属性名和值
    print("\n1. 中文属性名和值测试:")
    create_attribute("角色姓名", "张三")
    create_attribute("职业", "法师")
    create_attribute("技能", ["火球术", "冰冻术", "雷电术"])
    
    # 中文类别名
    print("\n2. 中文类别名测试:")
    set_attribute_category("角色姓名", "基本信息")
    set_attribute_category("职业", "基本信息")
    set_attribute_category("技能", "战斗技能")
    
    # 获取中文类别的属性
    print("\n3. 获取中文类别属性测试:")
    basic_info = get_attributes_by_category("基本信息")
    print(f"基本信息类别的属性: {basic_info}")
    
    # 获取中文类别数量
    print("\n4. 中文类别数量测试:")
    basic_count = count_attributes_by_category("基本信息")
    print(f"基本信息数量: {basic_count} (预期结果: 2)")

def test_custom_save_location():
    """测试自定义存档位置功能"""
    print("\n=== 测试自定义存档位置 ===")
    
    # 获取当前存档位置
    original_location = get_save_location()
    print(f"默认存档位置: {original_location}")
    
    # 创建临时测试目录
    test_save_dir = os.path.join(os.path.dirname(parent_dir), "test_saves")
    
    # 配置新的存档位置
    configure_save_system(test_save_dir, "custom_save.json")
    
    # 获取新的存档位置
    new_location = get_save_location()
    print(f"自定义存档位置: {new_location}")
    
    # 测试在新位置创建和读取属性
    create_attribute("测试属性", "测试值", "测试类别")
    print(f"在自定义位置读取属性: {get_attribute('测试属性')}")
    print(f"在自定义位置读取属性类别: {get_attribute_category('测试属性')}")
    
    # 检查文件是否存在
    if os.path.exists(new_location):
        print(f"自定义存档文件已成功创建: {new_location}")
    else:
        print(f"错误: 自定义存档文件未创建")
    
    # 恢复原来的存档位置
    configure_save_system(os.path.dirname(original_location), os.path.basename(original_location))
    print(f"已恢复默认存档位置: {get_save_location()}")

def test_quick_create_category_attribute():
    """测试快速创建类别属性的功能"""
    print("\n=== 测试快速创建类别属性 ===")
    
    # 配置存档位置
    configure_save_system(save_file="quick_create_test.json")
    
    # 测试快速创建不同类型的属性
    print("\n1. 快速创建普通数值属性:")
    hp_attr_name = create_category_attribute(120, "生命值")
    print(f"创建的属性名: {hp_attr_name}")
    print(f"属性值: {get_attribute(hp_attr_name)}")
    print(f"属性类别: {get_attribute_category(hp_attr_name)}")
    
    print("\n2. 快速创建字典属性:")
    buff_attr_name = create_category_attribute(
        {"持续时间": 5, "效果": "每回合回复10点生命值"}, 
        "增益效果"
    )
    print(f"创建的属性名: {buff_attr_name}")
    print(f"属性值: {get_attribute(buff_attr_name)}")
    print(f"属性类别: {get_attribute_category(buff_attr_name)}")
    
    print("\n3. 快速创建列表属性:")
    items_attr_name = create_category_attribute(
        ["小型生命药水", "魔法卷轴", "随机传送符"], 
        "背包物品"
    )
    print(f"创建的属性名: {items_attr_name}")
    print(f"属性值: {get_attribute(items_attr_name)}")
    print(f"属性类别: {get_attribute_category(items_attr_name)}")
    
    # 创建多个同类别属性，测试唯一性
    print("\n4. 测试同类别多个属性的唯一性:")
    buff1_name = create_category_attribute(
        {"持续时间": 3, "效果": "攻击力+5"}, 
        "增益效果"
    )
    buff2_name = create_category_attribute(
        {"持续时间": 2, "效果": "防御力+10"}, 
        "增益效果"
    )
    print(f"第一个属性名: {buff1_name}")
    print(f"第二个属性名: {buff2_name}")
    
    # 验证类别数量计数
    buff_count = count_attributes_by_category("增益效果")
    print(f"增益效果类别的属性数量: {buff_count} (预期结果: 3)")
    
    # 测试空类别名
    print("\n5. 测试空类别名:")
    empty_cat_result = create_category_attribute(100, "")
    print(f"空类别名结果: {empty_cat_result} (预期结果: None)")

def test_item_properties():
    """测试物品属性提取和搜索功能"""
    print("\n=== 测试物品属性提取和搜索 ===")
    
    # 配置存档位置
    configure_save_system(save_file="item_test.json")
    
    # 创建带属性的物品
    print("\n1. 创建带多种属性的物品:")
    # 创建武器
    create_attribute("青锋剑", {
        "类型": "武器",
        "攻击力": 10,
        "品质": "稀有",
        "描述": "一把锋利的长剑",
        "需求等级": 5
    }, "背包物品")
    
    create_attribute("木棒", {
        "类型": "武器",
        "攻击力": 3,
        "品质": "普通",
        "描述": "普通的木棒",
        "需求等级": 1
    }, "背包物品")
    
    # 创建防具
    create_attribute("皮甲", {
        "类型": "防具",
        "防御力": 5,
        "品质": "普通",
        "描述": "简单的皮甲",
        "需求等级": 3
    }, "背包物品")
    
    create_attribute("龙鳞胸甲", {
        "类型": "防具",
        "防御力": 20,
        "品质": "稀有",
        "描述": "由龙鳞制成的胸甲",
        "需求等级": 10
    }, "背包物品")
    
    # 创建消耗品
    create_attribute("治疗药水", {
        "类型": "消耗品",
        "效果": "恢复50点生命值",
        "品质": "普通",
        "数量": 5
    }, "背包物品")
    
    create_attribute("魔法药水", {
        "类型": "消耗品",
        "效果": "恢复30点魔法值",
        "品质": "普通",
        "数量": 3
    }, "背包物品")
    
    # 测试提取物品特定属性
    print("\n2. 提取物品特定属性测试:")
    # 提取青锋剑的品质
    sword_quality = get_item_property("青锋剑", "品质")
    print(f"青锋剑的品质: {sword_quality} (预期结果: 稀有)")
    
    # 提取皮甲的防御力
    armor_defense = get_item_property("皮甲", "防御力")
    print(f"皮甲的防御力: {armor_defense} (预期结果: 5)")
    
    # 提取治疗药水的数量
    potion_count = get_item_property("治疗药水", "数量")
    print(f"治疗药水的数量: {potion_count} (预期结果: 5)")
    
    # 测试提取不存在的物品特性
    print("\n3. 提取不存在的物品特性测试:")
    # 提取不存在的物品
    missing_item = get_item_property("不存在的物品", "品质", "未找到")
    print(f"不存在物品的品质: {missing_item} (预期结果: 未找到)")
    
    # 提取存在的物品的不存在特性
    missing_property = get_item_property("青锋剑", "耐久度", 100)
    print(f"青锋剑的耐久度: {missing_property} (预期结果: 100)")
    
    # 提取非字典类型物品的特性
    create_attribute("金币", 1000, "背包物品")
    coin_property = get_item_property("金币", "数量")
    print(f"金币的数量: {coin_property} (预期结果: None)")
    
    # 测试搜索特定特性的物品
    print("\n4. 搜索特定特性物品测试:")
    # 搜索稀有品质的物品
    rare_items = search_items_by_property("背包物品", "品质", "稀有")
    print(f"稀有品质的物品: {rare_items} (预期包含: 青锋剑, 龙鳞胸甲)")
    
    # 搜索武器类型的物品
    weapons = search_items_by_property("背包物品", "类型", "武器")
    print(f"武器类型的物品: {weapons} (预期包含: 青锋剑, 木棒)")
    
    # 搜索消耗品
    consumables = search_items_by_property("背包物品", "类型", "消耗品")
    print(f"消耗品类型的物品: {consumables} (预期包含: 治疗药水, 魔法药水)")
    
    # 搜索不存在的特性值
    no_items = search_items_by_property("背包物品", "品质", "传说")
    print(f"传说品质的物品: {no_items} (预期结果: 空列表)")
    
    # 测试更新物品特性
    print("\n5. 更新物品特性测试:")
    # 获取当前治疗药水数据
    potion_data = get_attribute("治疗药水")
    print(f"更新前治疗药水: {potion_data}")
    
    # 更新数量
    potion_data["数量"] -= 1
    set_attribute("治疗药水", potion_data)
    
    # 获取更新后的数据
    updated_potion = get_attribute("治疗药水")
    print(f"更新后治疗药水: {updated_potion}")
    
    # 通过辅助函数获取更新后的数量
    updated_count = get_item_property("治疗药水", "数量")
    print(f"更新后药水数量: {updated_count} (预期结果: 4)")

if __name__ == "__main__":
    print("===== 开始测试角色属性模块 =====\n")
    
    # 设置一个专用的测试存档文件
    configure_save_system(save_file="test_attributes.json")
    
    # 运行各项测试
    test_basic_operations()
    test_attribute_category()
    test_chinese_support()
    test_custom_save_location()
    test_quick_create_category_attribute()
    test_item_properties()  # 添加新测试
    
    print("\n===== 测试完成 =====") 