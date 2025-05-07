# 新的模板格式指南

本文档介绍了文字冒险游戏中模板系统的新格式设计，这种设计提供了更清晰、更直观的方式来定义输出字段和内容要求。

## 主要变更

1. **移除独立的 output_format 字段**：
   - 字段类型信息直接集成到提示片段中
   - 减少了模板中的冗余信息

2. **在[]标记中直接指定字段类型**：
   - 使用 `[字段名="类型"]` 的格式
   - 例如：`[story="string"]`, `[choices="array"]`

3. **使用三引号描述来分离字段说明**：
   - 字段描述不再嵌入到JSON值中
   - 而是以清晰分离的三引号块形式展示

## 新旧格式对比

### 旧格式

```json
{
  "prompt_segments": [
    "<描述一次冒险>",
    "[adventure=\"*\"]"
  ],
  "output_format": {
    "adventure": "string"
  }
}
```

### 新格式

```json
{
  "prompt_segments": [
    "<描述一次冒险>",
    "[adventure=\"string\"]"
  ]
  // 不再需要output_format字段
}
```

## 提示词处理结果

使用旧格式，生成的JSON模板部分是：

```json
{
  "adventure": "请在这里填入中文-描述一次冒险"
}
```

使用新格式，生成的JSON模板部分是：

```
{
  "adventure": "string"
  """
  描述一次冒险
  """
}
```

## 新格式的优势

1. **减少冗余**：字段类型只需要在一个地方定义，减少了信息重复

2. **提高可读性**：
   - 指令与输出格式更紧密地关联在一起
   - 三引号描述使内容要求与字段类型清晰分离

3. **更灵活的字段描述**：
   - 内容指令可以是多行的，三引号格式保持了描述的可读性
   - 指令与类型信息的分离更清晰地表达了"字段应该包含什么"和"字段是什么类型"

4. **简化模板维护**：
   - 减少了模板中需要同步更新的地方
   - 添加新字段时只需要编辑一处

## 使用指南

### 字段类型定义

在[]标记中定义字段及其类型：

```
[field1="string", field2="array", field3="object"]
```

支持的类型包括：
- `string`: 字符串值
- `number`: 数值
- `boolean`: 布尔值
- `array`: 数组
- `object`: 对象

### 内容配对

维持<>和[]的配对关系，确保指令和字段定义相邻：

```
<描述角色的外貌特征和性格特点>
[appearance="string", personality="string"]
```

### 使用示例

完整的模板示例：

```json
{
  "template_id": "adventure_template",
  "name": "冒险模板",
  "prompt_segments": [
    "(主角名称: {name})",
    "(所在位置: {location})",
    "<描述{name}在{location}遇到的一个意外事件>",
    "[event=\"string\", danger_level=\"number\"]",
    "<提供三个不同的解决方案，分别对应不同的技能>",
    "[solution1=\"string\", solution2=\"string\", solution3=\"string\"]"
  ],
  "output_storage": {
    "event": "current_event",
    "danger_level": "current_danger",
    "solution1": "option1",
    "solution2": "option2",
    "solution3": "option3"
  }
}
```

## 迁移指南

从旧格式迁移到新格式，只需要两个简单步骤：

1. 从output_format中提取字段类型，并将它们集成到[]标记中：
   - 将 `[field="*"]` 改为 `[field="具体类型"]`

2. 删除output_format字段：
   - 整个output_format对象可以安全移除
   - 确保output_storage保持不变，以维持正确的存储映射

## 注意事项

1. 当同一个内容描述适用于多个字段时，可以在一个[]标记中定义多个字段：
   ```
   <生成三个不同的选择>
   [choice1="string", choice2="string", choice3="string"]
   ```

2. 模板处理器已兼容旧版格式，但推荐尽快迁移到新格式以获得更好的可维护性。

3. 新格式的三引号描述在最终的AI提示词中更加清晰，有助于模型更好地理解要求。 