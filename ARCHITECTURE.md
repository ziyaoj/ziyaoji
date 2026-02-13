# 系统架构 (System Architecture)

## 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Web 界面 (Streamlit)                  │
│                          app.py                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     路由层 (Router)                          │
│                      router.py                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  复杂度评分 (Complexity Scoring) - utils.py        │   │
│  │  • 问题长度分析                                     │   │
│  │  • 关键词检测                                       │   │
│  │  • 问号数量统计                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────┬──────────────┬──────────────┬─────────────────┘
             │              │              │
    分数 ≤1  │     分数 2-3 │     分数 ≥4  │
             ▼              ▼              ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   FAQ 数据库    │ │  本地小模型   │ │   远程大模型     │
│   faq.json      │ │small_model.py│ │  big_model.py    │
├─────────────────┤ ├──────────────┤ ├──────────────────┤
│ • 关键词匹配    │ │DeepSeek 1.3B │ │ Qwen3 API       │
│ • 即时返回      │ │• CPU推理     │ │ • 阿里云API     │
│ • 零成本        │ │• 懒加载      │ │ • 按量计费      │
│                 │ │• 低内存模式  │ │ • 网络调用      │
└─────────────────┘ └──────┬───────┘ └──────────────────┘
                           │
                    置信度检查
                           │
                    ┌──────▼────────┐
                    │  低置信度？    │
                    └──────┬────────┘
                           │
                         是 │
                           ▼
                    ┌──────────────┐
                    │ 升级到大模型  │
                    │  (Fallback)  │
                    └──────────────┘
```

## 数据流

### 1. 用户请求流程

```
用户输入问题
    ↓
Streamlit 接收
    ↓
router.route_question()
    ↓
utils.complexity_score()
    ↓
路由决策
    ↓
调用相应模型
    ↓
返回答案 + 元数据
    ↓
Streamlit 显示 + 记录日志
```

### 2. 配置加载流程

```
应用启动
    ↓
加载 .env 文件 (python-dotenv)
    ↓
config.py 读取环境变量
    ↓
各模块导入配置
    ↓
首次调用时初始化模型/客户端
```

## 模块依赖关系

```
app.py
  └─ router.py
      ├─ utils.py
      ├─ small_model.py
      │   └─ config.py
      │       └─ .env
      └─ big_model.py
          └─ config.py
              └─ .env
```

## 核心组件详解

### 1. 配置层 (config.py)

```python
.env (环境变量)
    ↓
config.py (统一配置)
    ↓
各模块 (small_model.py, big_model.py)
```

**职责**：
- 加载环境变量
- 提供默认值
- 统一配置接口

### 2. 路由层 (router.py)

```python
输入: question (str)
    ↓
复杂度评分
    ↓
路由决策
    ↓
调用模型
    ↓
返回: (answer, metadata)
```

**职责**：
- 问题复杂度评估
- 路由策略实现
- 日志记录
- 性能统计

### 3. 模型层

#### 本地小模型 (small_model.py)

```python
首次调用
    ↓
_load_model()
    ├─ 下载模型 (如需要)
    ├─ 加载 tokenizer
    └─ 加载 model (CPU, float32)
    ↓
small_model_answer()
    ├─ 构建提示词
    ├─ Tokenize
    ├─ 生成回答
    └─ Decode
    ↓
low_confidence()
    └─ 判断是否需要升级
```

#### 远程大模型 (big_model.py)

```python
首次调用
    ↓
_get_client()
    └─ 创建 OpenAI 客户端
    ↓
big_model_answer()
    ├─ 构建消息
    ├─ API 调用
    └─ 解析响应
```

## 性能优化策略

### 1. 懒加载 (Lazy Loading)

```
应用启动 → 不加载模型
                  ↓
            首次调用时加载
                  ↓
            后续调用复用
```

**优势**：
- 快速启动
- 减少内存占用（未使用功能）
- 按需初始化

### 2. 智能路由

```
简单问题 (70%) → FAQ (0ms, 0成本)
中等问题 (20%) → 小模型 (2-5s, 0成本)
复杂问题 (10%) → 大模型 (1-3s, 有成本)
```

**优势**：
- 降低平均响应时间
- 减少 API 调用成本
- 提升用户体验

### 3. 降级策略

```
正常流程 → 出错 → 降级处理 → 返回基础回答
```

**优势**：
- 提高系统可用性
- 用户友好的错误处理
- 避免系统崩溃

## 扩展性设计

### 1. 添加新路由规则

```python
# router.py
if score <= 1:
    # FAQ
elif score <= 3:
    # Small model
elif score <= 5:  # 新增
    # Medium model
else:
    # Big model
```

### 2. 添加新模型

```python
# medium_model.py
def medium_model_answer(question: str) -> str:
    # 实现逻辑
    pass
```

### 3. 自定义复杂度评分

```python
# utils.py
def complexity_score(question: str) -> int:
    # 自定义评分逻辑
    pass
```

## 监控和日志

```
每次请求
    ↓
记录到 logs.csv
    ├─ timestamp
    ├─ question
    ├─ score
    ├─ route
    ├─ response_time
    └─ cost
```

**用途**：
- 性能分析
- 成本统计
- 路由优化
- 问题分析

## 安全架构

```
用户输入
    ↓
应用层 (无认证信息)
    ↓
配置层 (环境变量)
    ↓
API 层 (安全传输)
    ↓
外部服务 (HTTPS)
```

**安全措施**：
- 环境变量存储密钥
- .gitignore 防止泄露
- HTTPS API 调用
- 错误信息不暴露敏感数据

## 部署架构

```
开发环境                生产环境
    ↓                       ↓
requirements.txt    requirements.txt
    ↓                       ↓
.env (开发配置)      .env (生产配置)
    ↓                       ↓
streamlit run app.py        Docker/服务器
```

## 总结

本系统采用了：
- ✅ 分层架构（界面、路由、模型）
- ✅ 懒加载优化
- ✅ 智能路由降本
- ✅ 降级策略保可用性
- ✅ 环境变量管理配置
- ✅ 详细日志支持分析
