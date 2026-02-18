# 校园问答调度系统 (Campus Q&A Routing System)

这是一个智能问答路由系统，结合了FAQ、本地小模型和远程大模型，实现高效的问答服务。

## 特性

- **FAQ快速匹配**：常见问题直接返回预设答案
- **本地小模型**：使用Qwen2 1.5B Instruct模型（CPU推理，适合集成显卡电脑）
- **远程大模型**：通过API调用Qwen3大模型处理复杂问题
- **智能路由**：根据问题复杂度自动选择合适的处理方式

## 安装

### 方式一：使用 pip（推荐用于已有Python环境）

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 方式二：使用 conda（推荐用于隔离环境）

#### 1. 创建并激活conda环境

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate ziyaoji
```

如果需要更新已有环境：
```bash
conda env update -f environment.yml --prune
```

### 2. 配置环境变量

复制`.env.example`为`.env`并配置：

```bash
cp .env.example .env
```

编辑`.env`文件：

```env
# 小模型配置（可使用默认值）
SMALL_MODEL_PATH=Qwen/Qwen2-1.5B-Instruct

# 大模型配置（必须配置）
QWEN_API_KEY=你的阿里云DashScope API密钥
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=qwen-plus
```

### 3. 获取Qwen API密钥

1. 访问[阿里云DashScope](https://dashscope.aliyun.com/)
2. 注册并创建API密钥
3. 将API密钥填入`.env`文件的`QWEN_API_KEY`

## 运行

```bash
# 如果使用conda，确保已激活环境
conda activate ziyaoji

# 启动应用
streamlit run app.py
```

应用将在浏览器中打开（默认地址：http://localhost:8501）

## 系统架构

系统根据问题复杂度智能路由：

1. **简单问题（复杂度≤1）**：直接匹配FAQ
2. **中等问题（复杂度2-3）**：使用本地小模型，置信度低时升级到大模型
3. **复杂问题（复杂度≥4）**：直接使用远程大模型

## 模型说明

### 本地小模型
- 使用Qwen2 1.5B Instruct模型（阿里通义千问系列）
- 专为中文对话优化，适合日常问答场景
- CPU推理，适合集成显卡电脑
- 首次运行会自动下载模型（约1.5GB）

### 远程大模型
- 使用Qwen3大模型API
- 按使用量计费，具体参考阿里云定价

## 注意事项

- 首次运行时，小模型会自动从HuggingFace下载，需要网络连接
- 如果网络受限，可以手动下载模型后设置`SMALL_MODEL_PATH`为本地路径
- 确保已配置有效的Qwen API密钥，否则大模型功能无法使用
- 集成显卡电脑建议使用CPU推理（已默认配置）

## 文件说明

- `app.py` - Streamlit Web应用入口
- `router.py` - 问题路由逻辑
- `small_model.py` - 本地小模型实现
- `big_model.py` - 远程大模型API调用
- `utils.py` - 工具函数（复杂度评分、日志记录）
- `config.py` - 配置文件
- `faq.json` - FAQ数据库
