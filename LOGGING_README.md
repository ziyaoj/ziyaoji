# 日志记录功能说明

## 问题：为什么看不到新的日志记录？

### ✅ 答案：日志功能正常，但文件位置已改变

在最近的更新中，我们修复了日志文件路径问题，现在日志文件使用**绝对路径**，而不再是相对路径。

## 📍 日志文件位置

**新位置（固定）：**
```
/home/runner/work/ziyaoji/ziyaoji/logs.csv
```

这个路径是绝对路径，**无论从哪个目录运行程序**，日志都会写入这个固定位置。

## 🔄 与之前的区别

### 之前（使用相对路径）
- 日志文件：`logs.csv`（相对于当前工作目录）
- 问题：如果从不同目录运行程序，日志会写到不同位置
- 结果：日志文件位置不确定，难以查找

### 现在（使用绝对路径）  
- 日志文件：`/home/runner/work/ziyaoji/ziyaoji/logs.csv`（绝对路径）
- 优点：无论从哪里运行，日志位置固定
- 结果：日志文件总在项目根目录下

## ✨ 如何查看日志

### 方法1：直接查看文件
```bash
cd /home/runner/work/ziyaoji/ziyaoji
cat logs.csv
```

### 方法2：使用诊断工具
```bash
cd /home/runner/work/ziyaoji/ziyaoji
python check_logging.py
```

### 方法3：在Python中访问
```python
from utils import LOG_PATH
print(f"日志文件位置: {LOG_PATH}")

# 读取日志
with open(LOG_PATH, 'r', encoding='utf-8') as f:
    print(f.read())
```

## 🧪 验证日志记录是否工作

运行测试脚本：
```bash
python check_logging.py
```

该脚本会：
1. 显示日志文件的确切位置
2. 显示当前日志内容
3. 测试写入功能
4. 检查是否有旧位置的日志文件

## 📝 日志文件格式

日志文件是CSV格式，包含以下字段：
- `timestamp`: 时间戳
- `question`: 用户问题
- `score`: 复杂度评分
- `route`: 路由方式 (faq/small_model/big_model)
- `response_time`: 响应时间（秒）
- `cost`: 成本估算

示例：
```csv
timestamp,question,score,route,response_time,cost
2026-02-18T02:51:06,图书馆几点开门,0,faq,0.05,0.0
2026-02-18T02:51:07,如何分析数据,3,small_model,0.2,0.0
```

## ⚠️ 注意事项

1. **日志文件不再纳入版本控制**  
   `logs.csv` 已添加到 `.gitignore`，不会被 git 跟踪

2. **空问题不会被记录**  
   为了避免污染日志，空字符串或纯空白的问题不会被记录

3. **文件自动创建**  
   首次运行时，如果日志文件不存在会自动创建

4. **并发安全**  
   日志写入使用了并发安全的实现，多个请求同时写入不会出错

## 🔍 故障排查

### 如果看不到新日志：

1. **检查您查看的文件位置是否正确**
   ```bash
   python -c "from utils import LOG_PATH; print(LOG_PATH)"
   ```

2. **确认程序正在运行并处理请求**
   - 空问题不会生成日志
   - 需要有实际的有效问题才会记录

3. **检查文件权限**
   ```bash
   ls -l logs.csv
   ```

4. **运行诊断工具**
   ```bash
   python check_logging.py
   ```

## 💡 常见问题

**Q: 为什么我的旧日志看不到了？**  
A: 旧日志可能在不同的位置。使用 `find` 命令查找：
```bash
find /home/runner/work/ziyaoji -name "logs.csv" -type f
```

**Q: 可以改变日志文件位置吗？**  
A: 可以，修改 `utils.py` 中的 `LOG_PATH` 变量：
```python
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs.csv")
```

**Q: 日志文件会无限增长吗？**  
A: 是的，目前没有自动清理机制。建议定期手动清理或实现日志轮转。

## 🎯 总结

日志记录功能**正常工作**，只是文件位置从相对路径改为了绝对路径。请确保查看正确的位置：

```
/home/runner/work/ziyaoji/ziyaoji/logs.csv
```

如有疑问，运行 `python check_logging.py` 进行诊断。
