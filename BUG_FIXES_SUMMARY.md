# Bug Fixes Summary

本文档总结了修复的所有8个bug及其解决方案。

## 修复的Bug列表

### 🔴 Bug 1（严重）：小模型异常降级会静默触发大模型回退

**问题描述**：
- `small_model_answer()` 的异常处理返回包含 `"不太确定"` 关键词的消息
- 这会被 `low_confidence()` 检测为低置信度
- 导致在 `router.py` 中静默触发大模型 API 调用，产生额外成本

**修复方案**：
- 修改异常处理消息为 `"[小模型] 暂时繁忙，请稍后再试"`
- 该消息不会触发 `low_confidence` 检测

**影响文件**：`small_model.py`

---

### 🔴 Bug 2（严重）：`complexity_score` 空问题检查位置错误

**问题描述**：
- 空问题保护 `if not q: return 0` 放在函数末尾
- 应该在开头 early return

**修复方案**：
- 将空问题检查移到函数最开头
- 在任何计算之前进行检查

**影响文件**：`utils.py`

---

### 🟡 Bug 3：`cost` 永远为 0

**问题描述**：
- 无论走 FAQ、小模型、还是大模型，`cost` 始终硬编码为 `0`
- 大模型调用应该有成本估算

**修复方案**：
- 让 `big_model_answer` 返回 `(answer, usage_info)` 元组
- 在 `router.py` 中根据路由结果设置合理的 cost
- FAQ 和小模型为 0，大模型根据 token 估算
- 添加 `COST_PER_TOKEN` 命名常量便于维护

**影响文件**：`big_model.py`, `router.py`

---

### 🟡 Bug 4：`faq_answer` 每次都重新读取文件

**问题描述**：
- 每次调用 `faq_answer()` 都打开并解析 `faq.json`
- 造成不必要的 I/O

**修复方案**：
- 在模块级别加载 FAQ 数据一次
- 使用 `_faq_cache` 缓存
- 通过 `_load_faq()` 懒加载

**影响文件**：`router.py`

---

### 🟡 Bug 5：FAQ 关键词匹配存在歧义

**问题描述**：
- 多个 FAQ 条目共用 `"时间"` 关键词
- 顺序匹配导致可能返回错误答案
- 例如用户问 `"食堂什么时间开？"` 可能匹配到图书馆

**修复方案**：
- 改为加权匹配
- 计算每个 FAQ 条目匹配的关键词数量
- 返回匹配度最高的答案

**影响文件**：`router.py`

---

### 🟡 Bug 6：`low_confidence` 误判

**问题描述**：
- `"无法"` 会误匹配 `"无法避免"` 等正面表述
- `len(answer) < 10` 对合理的简短回答也会误判

**修复方案**：
- 提高最短长度阈值到 5
- 添加异常短语列表（如 `"无法避免"`, `"不能说"`, `"不能否认"`）
- 改进关键词匹配逻辑，检查异常短语是否存在

**影响文件**：`small_model.py`

---

### 🟡 Bug 7：`log_event` 并发竞态

**问题描述**：
- `os.path.exists()` 和 `open()` 之间存在 TOCTOU 竞态条件

**修复方案**：
- 使用 `'a+'` 模式打开文件
- 使用 `f.tell()` 高效检查文件是否为空
- 避免 TOCTOU 问题

**影响文件**：`utils.py`

---

### 🟢 Bug 8：`faq.json` 使用相对路径

**问题描述**：
- `FAQ_PATH = "faq.json"` 使用相对路径
- 如果工作目录不是项目根目录就会出错

**修复方案**：
- 使用 `os.path.dirname(__file__)` 构建绝对路径
- `FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.json")`

**影响文件**：`router.py`

---

## 测试

创建了 `test_bugfixes.py` 文件，包含：
- 代码级别的验证（检查代码是否包含正确的修复）
- 运行时测试（在依赖可用时测试功能）
- 所有测试均通过

## 代码审查

经过多轮代码审查，所有反馈均已解决：
- ✅ 测试路径使用相对路径提高可移植性
- ✅ 文件空检查使用高效的 `f.tell()`
- ✅ 异常短语处理使用可维护的列表方式
- ✅ 成本计算使用命名常量 `COST_PER_TOKEN`
- ✅ 测试断言更灵活，不依赖精确格式

## 变更统计

```
big_model.py     |  17 +++--
router.py        |  52 ++++++++++---
small_model.py   |  23 ++++--
test_bugfixes.py | 353 ++++++++++++++++++++++++++++++++++++++++++++
utils.py         |  32 ++++++---
5 files changed, 449 insertions(+), 28 deletions(-)
```

## 验证结果

所有Bug修复已验证通过：
- ✓ Bug 1: 小模型异常处理
- ✓ Bug 2: 空问题检查位置  
- ✓ Bug 3: 成本追踪
- ✓ Bug 4: FAQ缓存
- ✓ Bug 5: 加权匹配
- ✓ Bug 6: low_confidence误判
- ✓ Bug 7: log_event竞态条件
- ✓ Bug 8: FAQ绝对路径
