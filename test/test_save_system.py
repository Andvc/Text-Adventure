"""
测试存档系统功能
"""

from data import data_manager as dm
from save import save_manager

def test_basic_save_functions():
    print("=== 测试基本存档功能 ===")
    
    # 测试创建存档
    print("\n创建测试存档...")
    result = dm.create_save("test_save", "测试角色", "用于测试的存档")
    print(f"创建存档结果: {result}")
    
    # 测试列出存档
    print("\n列出所有存档:")
    saves = dm.list_saves()
    for save in saves:
        print(f"- {save}")
    
    # 测试读取存档元数据
    print("\n读取存档元数据:")
    metadata = dm.get_save_metadata()
    for key, value in metadata.items():
        print(f"- {key}: {value}")
    
    # 测试创建属性
    print("\n创建属性...")
    dm.create_attribute("姓名", "张三", "基础属性")
    dm.create_attribute("等级", 1, "基础属性")
    dm.create_attribute("生命值", 100, "基础属性")
    dm.create_attribute("攻击力", 15, "战斗属性")
    
    # 测试获取属性
    print("\n获取属性:")
    print(f"姓名: {dm.get_attribute('姓名')}")
    print(f"等级: {dm.get_attribute('等级')}")
    
    # 测试获取所有属性
    print("\n获取所有属性:")
    attrs = dm.get_all_attributes()
    for name, value in attrs.items():
        print(f"- {name}: {value}")
    
    # 测试按类别获取属性
    print("\n按类别获取属性:")
    basic_attrs = dm.get_attributes_by_category("基础属性")
    print(f"基础属性: {basic_attrs}")
    
    # 测试创建第二个存档
    print("\n创建第二个存档...")
    dm.create_save("test_save2", "测试角色2", "第二个测试存档")
    
    # 测试在第二个存档中创建属性
    print("\n在第二个存档中创建属性...")
    dm.create_attribute("姓名", "李四", "基础属性")
    dm.create_attribute("等级", 5, "基础属性")
    
    # 测试切换回第一个存档
    print("\n切换回第一个存档...")
    dm.load_save("test_save")
    
    # 验证第一个存档的数据
    print("\n验证第一个存档的数据:")
    print(f"姓名: {dm.get_attribute('姓名')}")  # 应该是"张三"
    
    # 测试重命名存档
    print("\n重命名test_save2为new_save...")
    dm.rename_save("test_save2", "new_save")
    
    # 测试列出存档
    print("\n列出所有存档:")
    saves = dm.list_saves()
    for save in saves:
        print(f"- {save}")
    
    # 测试删除存档
    print("\n删除new_save存档...")
    dm.delete_save("new_save")
    
    # 再次列出存档
    print("\n列出所有存档:")
    saves = dm.list_saves()
    for save in saves:
        print(f"- {save}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_basic_save_functions() 