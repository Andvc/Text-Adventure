from data.data_manager import get_nested_data_value

# 测试读取 world_background.json 文件的嵌套数据
result = get_nested_data_value('text', 'worlds/world_background', 'layers.layer1')
print(f"读取结果: {result}")

# 测试读取更深层的数据
result2 = get_nested_data_value('text', 'worlds/world_background', 'layers.layer1.elements.dual_sources.order_source.name')
print(f"读取结果2: {result2}") 