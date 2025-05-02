from data.data_manager import get_nested_save_value

# 测试获取嵌套数据
result = get_nested_save_value('text', 'worlds/world_background', 'layers.layer1')
print("层级1数据:", result)

# 测试获取深层嵌套数据
result2 = get_nested_save_value('text', 'worlds/world_background', 'layers.layer1.elements.dual_sources.order_source.name')
print("深层嵌套数据:", result2) 