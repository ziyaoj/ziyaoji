# 变更总结 (Changes Summary)

## 概述

本次更新实现了在集成显卡电脑上部署 DeepSeek 1.3B 本地模型，并通过远程 API 连接 Qwen3 大模型的功能。

## 主要变更

### 1. 新增文件

#### 配置相关
- **config.py** - 统一的配置管理，支持环境变量
- **.env.example** - 环境变量配置模板
- **.gitignore** - Git 忽略规则，防止提交敏感信息

#### 依赖管理
- **requirements.txt** - Python 依赖包列表

#### 文档
- **README.md** - 完整的项目说明和使用指南
- **DEPLOYMENT.md** - 详细的部署指南和故障排除
- **QUICKREF.md** - 快速参考指南

#### 工具
- **test_setup.py** - 环境检查脚本

### 2. 修改文件

#### small_model.py
- 原功能：返回模拟的小模型回答
- 新功能：使用 transformers 加载 DeepSeek Coder 1.3B 模型
- 关键特性：
  - 懒加载机制（首次调用时加载）
  - CPU 推理（适配集成显卡）
  - 使用 float32 确保兼容性
  - 低内存模式（low_cpu_mem_usage）
  - 错误处理和降级策略

#### big_model.py
- 原功能：返回模拟的大模型回答
- 新功能：通过 OpenAI 兼容 API 调用 Qwen3
- 关键特性：
  - 使用阿里云 DashScope API
  - 懒加载 OpenAI 客户端
  - 错误处理和降级策略
  - 支持环境变量配置

### 3. 未修改文件

以下文件保持原样，无需修改：
- **app.py** - Streamlit Web 应用入口
- **router.py** - 智能路由逻辑
- **utils.py** - 工具函数
- **faq.json** - FAQ 数据库
- **logs.csv** - 日志文件

## 技术栈

- **前端**: Streamlit
- **小模型**: DeepSeek Coder 1.3B (transformers + PyTorch)
- **大模型**: Qwen3 (阿里云 DashScope API)
- **配置管理**: python-dotenv

## 关键特性

### 1. 智能路由
系统根据问题复杂度自动选择处理方式：
- 简单问题 → FAQ
- 中等问题 → 本地小模型（低置信度时升级到大模型）
- 复杂问题 → 远程大模型

### 2. 集成显卡优化
- CPU 推理模式
- float32 数据类型
- 低内存占用模式
- 懒加载机制

### 3. 成本优化
- FAQ 优先，零成本
- 本地模型次之，零 API 成本
- 大模型按需调用，控制成本

### 4. 可靠性
- 多层降级策略
- 异常处理
- 详细的错误日志

## 部署要求

### 最低要求
- Python 3.8+
- 4GB RAM（8GB 推荐）
- 5GB 磁盘空间（用于模型缓存）
- 网络连接（用于下载模型和 API 调用）

### 推荐配置
- Python 3.10+
- 8GB+ RAM
- SSD 存储
- 稳定的网络连接

## 使用流程

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 填入 QWEN_API_KEY
   ```

3. **验证环境**
   ```bash
   python test_setup.py
   ```

4. **启动应用**
   ```bash
   streamlit run app.py
   ```

## 性能参考

| 场景 | 响应时间 | 成本 |
|------|----------|------|
| FAQ 匹配 | <0.1秒 | 免费 |
| 本地小模型 | 2-5秒 | 免费 |
| 远程大模型 | 1-3秒 | 按调用计费 |

## 注意事项

1. **首次运行**：会自动下载 DeepSeek 模型（约 1.3GB），需要良好的网络连接
2. **API 密钥**：必须配置有效的 Qwen API 密钥才能使用大模型功能
3. **内存使用**：小模型运行时占用约 2GB 内存
4. **推理速度**：集成显卡使用 CPU 推理，速度较慢但可接受（2-5秒）

## 后续优化建议

1. **性能优化**
   - 使用模型量化（INT8/INT4）减少内存占用
   - 使用 ONNX Runtime 加速推理
   - 实现请求缓存机制

2. **功能增强**
   - 添加对话历史管理
   - 支持多轮对话
   - 添加用户反馈机制

3. **成本控制**
   - 实现 API 调用次数限制
   - 添加成本统计和报警
   - 优化路由策略

## 安全考虑

- API 密钥通过环境变量管理
- .env 文件已加入 .gitignore
- 错误信息不暴露敏感数据
- CodeQL 安全扫描通过（0 告警）

## 支持与维护

- 详细文档：README.md、DEPLOYMENT.md、QUICKREF.md
- 环境检查：test_setup.py
- 日志记录：logs.csv
- 版本控制：Git

## 总结

本次更新成功实现了题目要求：
✅ 本地部署 DeepSeek 小模型（1.3B 蒸馏版本）
✅ 远程 API 连接 Qwen3 大模型
✅ 适配集成显卡电脑（CPU 推理）
✅ 完善的文档和工具支持
✅ 安全性和可靠性保障
