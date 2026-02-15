# 快速参考 (Quick Reference)

## 一键启动

### 使用 pip

```bash
# 首次使用
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY

# 启动应用
streamlit run app.py
```

### 使用 conda（推荐）

```bash
# 首次使用
conda env create -f environment.yml
conda activate ziyaoji
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY

# 启动应用
streamlit run app.py
```

## 环境变量配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `SMALL_MODEL_PATH` | 小模型路径或名称 | `deepseek-ai/deepseek-coder-1.3b-instruct` | 否 |
| `QWEN_API_KEY` | Qwen API 密钥 | - | **是** |
| `QWEN_API_BASE` | Qwen API 地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 否 |
| `QWEN_MODEL_NAME` | Qwen 模型名称 | `qwen-plus` | 否 |

## 路由规则

| 复杂度 | 条件 | 路由目标 |
|--------|------|----------|
| 0-1 | 简单问题、FAQ关键词匹配 | FAQ 数据库 |
| 2-3 | 中等复杂度 | 本地小模型 → (低置信度) → 大模型 |
| 4+ | 复杂问题、分析、规划类 | 远程大模型 API |

## 复杂度评分规则

- 问题长度 > 30字：+1分
- 包含关键词（分析、对比、规划、设计、为什么、如何）：+1分/词
- 多个问号：+1分

## 常用命令

### pip环境

```bash
# 环境检查
python test_setup.py

# 启动应用
streamlit run app.py

# 查看日志
cat logs.csv

# 更新依赖
pip install -r requirements.txt --upgrade
```

### conda环境

```bash
# 激活环境
conda activate ziyaoji

# 环境检查
python test_setup.py

# 启动应用
streamlit run app.py

# 查看日志
cat logs.csv

# 更新环境
conda env update -f environment.yml --prune

# 停用环境
conda deactivate

# 删除环境
conda env remove -n ziyaoji

# 列出所有环境
conda env list
```

## 文件结构

```
.
├── app.py              # Web 应用入口
├── router.py           # 路由逻辑
├── small_model.py      # 本地小模型
├── big_model.py        # 远程大模型 API
├── config.py           # 配置管理
├── utils.py            # 工具函数
├── faq.json            # FAQ 数据库
├── test_setup.py       # 环境检查脚本
├── requirements.txt    # Python 依赖
├── .env.example        # 配置模板
├── .env                # 配置文件（需自行创建）
├── README.md           # 项目说明
└── DEPLOYMENT.md       # 部署指南
```

## 性能参考

| 场景 | 响应时间 | 成本 |
|------|----------|------|
| FAQ 匹配 | <0.1秒 | 免费 |
| 本地小模型 | 2-5秒 | 免费 |
| 远程大模型 | 1-3秒 | 按调用计费 |

## 资源消耗

| 组件 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| Streamlit | 低 | ~200MB | - |
| 小模型 | 中 | ~2GB | ~1.3GB |
| 大模型API | 极低 | 极低 | - |

## 故障排除速查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 模块未找到 | 依赖未安装 | `pip install -r requirements.txt` |
| API Key 错误 | 未配置或错误 | 检查 `.env` 文件 |
| 模型下载慢 | 网络问题 | 使用镜像或手动下载 |
| 内存不足 | 模型太大 | 已使用 CPU + low_mem 模式 |
| 响应慢 | CPU 性能 | 正常现象，集成显卡预期 2-5秒 |

## 链接

- 阿里云 DashScope: https://dashscope.aliyun.com/
- DeepSeek 模型: https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct
- Streamlit 文档: https://docs.streamlit.io/
