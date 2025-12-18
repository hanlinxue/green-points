# 出行模式中英文映射
TRIP_MODE_MAPPING = {
    "步行": "walk",
    "跑步": "run",
    "骑行": "bike",
    "公交": "bus",
    "地铁": "subway",
    "驾车": "car"
}

# 将中文模式转换为英文
def convert_trip_mode(chinese_mode):
    return TRIP_MODE_MAPPING.get(chinese_mode, chinese_mode)

# 测试
print("出行模式映射测试:")
for cn, en in TRIP_MODE_MAPPING.items():
    print(f"{cn} -> {en}")