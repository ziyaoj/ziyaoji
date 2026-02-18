#!/usr/bin/env python3
"""
诊断脚本：检查日志记录功能
用于帮助用户理解日志文件的位置和状态
"""
import os
import sys

print("=" * 70)
print("日志记录诊断工具")
print("=" * 70)

# 导入模块
try:
    from utils import LOG_PATH, log_event
    print("✓ 成功导入 utils 模块")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 显示关键信息
print(f"\n【关键信息】")
print(f"  当前工作目录: {os.getcwd()}")
print(f"  脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
print(f"  日志文件路径: {LOG_PATH}")
print(f"  日志文件绝对路径: {os.path.abspath(LOG_PATH)}")

# 检查日志文件状态
print(f"\n【日志文件状态】")
if os.path.exists(LOG_PATH):
    print(f"  ✓ 日志文件存在")
    print(f"  文件大小: {os.path.getsize(LOG_PATH)} 字节")
    
    # 读取并显示内容
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"  总行数: {len(lines)}")
        print(f"  数据行数: {len(lines) - 1 if lines else 0}")
    
    print(f"\n  最近5条记录:")
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 显示表头
        if lines:
            print(f"    {lines[0].rstrip()}")
        # 显示最后5条数据
        for line in lines[-5:]:
            if line != lines[0]:  # 跳过表头
                print(f"    {line.rstrip()}")
else:
    print(f"  ✗ 日志文件不存在")
    print(f"  这是正常的，文件会在第一次记录日志时自动创建")

# 测试日志记录功能
print(f"\n【功能测试】")
try:
    log_event("诊断测试", 0, "test", 0.001, 0.0)
    print(f"  ✓ 成功写入测试日志")
    
    # 验证
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if any("诊断测试" in line for line in lines):
            print(f"  ✓ 确认测试日志已写入")
        else:
            print(f"  ✗ 警告: 未找到测试日志")
except Exception as e:
    print(f"  ✗ 写入失败: {e}")

# 检查可能的旧日志文件
print(f"\n【检查其他位置】")
old_locations = [
    "logs.csv",  # 相对路径
    os.path.join(os.getcwd(), "logs.csv"),  # 当前目录
]

for loc in old_locations:
    abs_loc = os.path.abspath(loc)
    if abs_loc != os.path.abspath(LOG_PATH) and os.path.exists(abs_loc):
        print(f"  ! 发现旧日志文件: {abs_loc}")
        print(f"    (这可能是您之前看到的日志文件)")

# 给出建议
print(f"\n【使用建议】")
print(f"  1. 日志文件位置固定在: {LOG_PATH}")
print(f"  2. 无论从哪个目录运行程序，日志都会写入这个位置")
print(f"  3. 如果需要查看日志，请访问上述路径")
print(f"  4. 日志文件不再纳入版本控制（已添加到 .gitignore）")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
