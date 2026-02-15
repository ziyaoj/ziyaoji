# Conda环境配置指南 (Conda Environment Setup Guide)

本文档详细说明如何使用conda配置和管理本项目的Python环境。

## 为什么选择Conda？

### Conda的优势

1. **环境隔离**：完全独立的Python环境，不影响系统Python
2. **依赖管理**：自动处理复杂的依赖关系，特别是PyTorch等科学计算库
3. **跨平台**：Windows、macOS、Linux统一的环境管理方式
4. **易于切换**：可以同时维护多个项目的不同环境
5. **快速回滚**：环境出问题可以快速删除重建

### 适用场景

✅ **推荐使用conda**：
- 新手用户（conda更容易管理依赖）
- 需要同时维护多个Python项目
- 使用Windows系统（conda对Windows支持更好）
- 需要频繁切换Python版本
- 使用深度学习相关库（如PyTorch、TensorFlow）

❌ **可以使用pip**：
- 已有Python虚拟环境
- 熟悉pip和virtualenv
- 系统资源有限（Anaconda较大）
- 仅需要纯Python包

## 安装Conda

### 选择1：Miniconda（推荐）

Miniconda是最小化安装，占用空间小（约400MB）。

**下载地址**：
- 官方：https://docs.conda.io/en/latest/miniconda.html
- 清华镜像：https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/

**安装步骤**：
```bash
# Linux/macOS
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# 或使用清华镜像（国内更快）
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

**Windows**：
下载安装程序（.exe），双击安装。

### 选择2：Anaconda（完整版）

Anaconda包含大量科学计算包，占用空间较大（约3GB）。

**下载地址**：
- 官方：https://www.anaconda.com/products/distribution
- 清华镜像：https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

## 配置本项目环境

### 方法1：使用environment.yml（推荐）

这是最简单的方法，一条命令创建完整环境。

```bash
# 克隆项目
git clone https://github.com/ziyaoj/ziyaoji.git
cd ziyaoji

# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate ziyaoji
```

### 方法2：手动创建环境

如果需要自定义配置，可以手动创建。

```bash
# 创建Python 3.10环境
conda create -n ziyaoji python=3.10

# 激活环境
conda activate ziyaoji

# 安装PyTorch (CPU版本)
conda install pytorch cpuonly -c pytorch

# 安装其他依赖
pip install -r requirements.txt
```

## 常用命令

### 环境管理

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate ziyaoji

# 停用环境
conda deactivate

# 列出所有环境
conda env list

# 删除环境
conda env remove -n ziyaoji

# 更新环境
conda env update -f environment.yml --prune

# 导出环境（用于备份或分享）
conda env export > environment_backup.yml

# 从指定环境文件创建
conda env create -f environment_backup.yml
```

### 包管理

```bash
# 在当前环境中安装包
conda install package_name

# 从特定渠道安装
conda install -c conda-forge package_name

# 使用pip安装（在conda环境中）
pip install package_name

# 列出已安装的包
conda list

# 搜索包
conda search package_name

# 更新包
conda update package_name

# 更新所有包
conda update --all

# 卸载包
conda remove package_name
```

## 配置conda镜像（加速下载）

如果在国内，建议配置清华镜像加速下载。

### 配置方法

```bash
# 创建/编辑 ~/.condarc 文件
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2/
conda config --set show_channel_urls yes

# PyTorch镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
```

### 查看配置

```bash
conda config --show channels
```

### 恢复默认镜像

```bash
conda config --remove-key channels
```

## 项目环境说明

### environment.yml文件解析

```yaml
name: ziyaoji                    # 环境名称
channels:                        # 软件源
  - pytorch                      # PyTorch官方源
  - conda-forge                  # 社区维护的包
  - defaults                     # Anaconda默认源
dependencies:
  - python>=3.8                  # Python版本
  - pip>=21.0                    # pip版本
  - pytorch>=2.0.0               # PyTorch（CPU版本）
  - cpuonly                      # CPU专用，不安装CUDA
  - pip:                         # 通过pip安装的包
      - streamlit>=1.30.0
      - transformers>=4.36.0
      - openai>=1.0.0
      - python-dotenv>=1.0.0
      - accelerate>=0.25.0
```

### 为什么使用CPU版本PyTorch？

1. 项目需求：本项目针对集成显卡电脑优化
2. 体积更小：CPU版本约200MB，GPU版本可达数GB
3. 安装更快：不需要配置CUDA
4. 兼容性好：所有电脑都能运行

如果你有独立显卡且想使用GPU，可以修改environment.yml：

```yaml
# 替换这两行：
  - pytorch>=2.0.0
  - cpuonly

# 为：
  - pytorch>=2.0.0
  - pytorch-cuda=11.8  # 根据你的CUDA版本调整
```

## 故障排除

### 问题1：conda命令未找到

**解决方案**：
1. 检查conda是否安装：`which conda`
2. 重新打开终端或运行：`source ~/.bashrc`（Linux/macOS）
3. Windows: 使用"Anaconda Prompt"而不是普通cmd

### 问题2：创建环境很慢

**解决方案**：
1. 配置国内镜像（见上文）
2. 使用代理
3. 减少依赖：先创建基础环境，再逐步安装

### 问题3：环境冲突

**解决方案**：
```bash
# 删除旧环境
conda env remove -n ziyaoji

# 清理缓存
conda clean --all

# 重新创建
conda env create -f environment.yml
```

### 问题4：某个包安装失败

**解决方案**：
```bash
# 激活环境
conda activate ziyaoji

# 使用pip单独安装失败的包
pip install package_name

# 或从conda-forge安装
conda install -c conda-forge package_name
```

## 与pip虚拟环境对比

| 特性 | Conda | pip + venv |
|------|-------|------------|
| 环境隔离 | ✅ 完全隔离 | ✅ 完全隔离 |
| Python版本管理 | ✅ 支持 | ❌ 需手动安装 |
| 二进制包 | ✅ 提供编译好的包 | ⚠️ 部分包需编译 |
| 非Python依赖 | ✅ 自动处理 | ❌ 需手动安装 |
| 跨平台 | ✅ 统一命令 | ⚠️ Windows稍有不同 |
| 磁盘占用 | 较大（每个环境独立） | 较小（共享系统库） |
| 创建速度 | 较慢 | 较快 |
| 包数量 | 较少但精选 | 更多 |

## 最佳实践

### 1. 为每个项目创建独立环境

```bash
# 不要：在base环境安装所有东西
# 要：为每个项目创建独立环境
conda create -n project1 python=3.10
conda create -n project2 python=3.9
```

### 2. 定期导出环境配置

```bash
# 每次安装新包后导出
conda env export > environment_backup.yml
```

### 3. 使用requirements.txt保持兼容

```bash
# 为pip用户提供requirements.txt
pip freeze > requirements.txt
```

### 4. 环境命名规范

- 使用项目名作为环境名
- 避免使用特殊字符
- 小写字母，用连字符分隔

### 5. 及时清理

```bash
# 定期清理未使用的包和缓存
conda clean --all

# 删除不再需要的环境
conda env remove -n old_project
```

## 参考资源

- [Conda官方文档](https://docs.conda.io/)
- [Conda速查表](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)
- [清华镜像使用帮助](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)
- [PyTorch安装指南](https://pytorch.org/get-started/locally/)

## 总结

使用conda管理本项目环境的完整流程：

```bash
# 1. 安装Miniconda（如果还没有）
# 2. 配置镜像（可选，国内推荐）
# 3. 克隆项目
git clone https://github.com/ziyaoj/ziyaoji.git
cd ziyaoji

# 4. 创建环境
conda env create -f environment.yml

# 5. 激活环境
conda activate ziyaoji

# 6. 配置API密钥
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY

# 7. 验证环境
python test_setup.py

# 8. 运行应用
streamlit run app.py
```

环境配置完成！🎉
