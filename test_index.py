from data.data_manager import get_indexed_save

def print_detail_data(detail_type):
    result = get_indexed_save('basic_detail', detail_type)
    if result is None:
        print(f"无法获取 {detail_type} 的数据")
        return
        
    print(f"\n{detail_type} 数据:")
    for key, value in result.items():
        print(f"{key}: {value}")

# 测试获取 detail1 类型的数据
print_detail_data('detail1')

# 测试获取 detail2 类型的数据
print_detail_data('detail2')

detail_type = "detail1"
result = get_indexed_save('basic_detail', detail_type)
print(f"索引数据 ({detail_type}):", result) 