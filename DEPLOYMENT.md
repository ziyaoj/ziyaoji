# 部署说明 (Deployment Guide)

本文档说明如何在集成显卡电脑上部署本系统。

## 快速开始

### 1. 安装依赖

确保已安装 Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制配置模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Qwen API 密钥：

```env
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 3. 验证环境

运行环境检查脚本：

```bash
python test_setup.py
```

### 4. 启动应用

```bash
streamlit run app.py
```

## 常见问题

### Q1: 小模型下载很慢怎么办？

**方案1：使用HuggingFace镜像**
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

**方案2：手动下载模型**
1. 从 https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct 下载模型
2. 将模型保存到本地目录，例如 `/path/to/models/deepseek-coder-1.3b-instruct`
3. 在 `.env` 中设置：`SMALL_MODEL_PATH=/path/to/models/deepseek-coder-1.3b-instruct`

### Q2: 内存不足怎么办？

小模型已配置使用 CPU 和 `low_cpu_mem_usage=True`。如果仍然内存不足：

1. 关闭其他应用程序
2. 考虑使用更小的模型（如 0.5B 版本）
3. 使用量化模型（需要额外配置）

### Q3: 如何获取 Qwen API 密钥？

1. 访问 https://dashscope.aliyun.com/
2. 使用阿里云账号登录
3. 在控制台中创建 API Key
4. 复制 API Key 到 `.env` 文件

### Q4: 大模型 API 调用失败？

检查：
1. API Key 是否正确配置
2. 网络连接是否正常
3. API 配额是否充足（可在阿里云控制台查看）

### Q5: 集成显卡性能如何？

- 小模型在集成显卡的 CPU 上推理速度约 2-5 秒/次
- 大模型通过 API 调用，速度取决于网络和服务端
- 系统会智能路由，简单问题直接用 FAQ 或小模型，复杂问题才用大模型

## 性能优化

### CPU 推理优化

1. **使用 OpenMP 多线程**
```bash
export OMP_NUM_THREADS=4
```

2. **使用 Intel 优化版 PyTorch**（仅 Intel CPU）
```bash
pip install intel-extension-for-pytorch
```

### 成本优化

1. **合理配置路由阈值**
   编辑 `utils.py` 中的 `complexity_score` 函数，调整复杂度判断标准

2. **使用更经济的模型**
   在 `.env` 中设置：
   ```env
   QWEN_MODEL_NAME=qwen-turbo  # 更便宜的模型
   ```

## 系统架构

```
用户问题
    ↓
复杂度评分 (utils.complexity_score)
    ↓
    ├─ 简单 (≤1) → FAQ 直接匹配
    ├─ 中等 (2-3) → 本地小模型
    │                ↓
    │             置信度低？
    │                ↓
    │              是 → 升级到大模型
    │              否 → 返回小模型回答
    └─ 复杂 (≥4) → 远程大模型 API
```

## 故障排除

### 模型加载失败

```python
# 错误: OSError: You are trying to access a gated repo.
# 解决: 需要在 HuggingFace 上接受模型使用协议
```

1. 访问模型页面: https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct
2. 点击 "Agree and access repository"
3. 使用 HuggingFace token 登录：
```bash
huggingface-cli login
```

### API 调用超时

编辑 `big_model.py`，增加超时设置：

```python
client = OpenAI(
    api_key=BIG_MODEL_API_KEY,
    base_url=BIG_MODEL_API_BASE,
    timeout=30.0  # 增加超时时间
)
```

## 监控和日志

系统会自动记录日志到 `logs.csv`，包含：
- 问题内容
- 复杂度评分
- 路由决策
- 响应时间
- 成本（待实现）

可以通过分析日志优化系统配置。

## 安全建议

1. **不要提交 .env 文件到 Git**（已在 .gitignore 中配置）
2. **定期轮换 API 密钥**
3. **设置 API 用量限制**（在阿里云控制台）
4. **不要在日志中记录敏感信息**

## 更新和维护

### 更新依赖
```bash
pip install -r requirements.txt --upgrade
```

### 更新模型
删除模型缓存目录（通常在 `~/.cache/huggingface`），重新启动应用会自动下载最新版本。

## 技术支持

如遇问题，请：
1. 查看日志输出
2. 运行 `python test_setup.py` 检查环境
3. 查阅 README.md
4. 提交 Issue 到 GitHub 仓库
