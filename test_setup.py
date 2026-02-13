#!/usr/bin/env python3
"""
测试配置和基本功能
"""
import sys

def test_config():
    """测试配置是否正确加载"""
    try:
        from config import (
            SMALL_MODEL_PATH, 
            SMALL_MODEL_DEVICE,
            BIG_MODEL_API_KEY,
            BIG_MODEL_API_BASE,
            BIG_MODEL_NAME
        )
        print("✓ 配置模块加载成功")
        print(f"  - 小模型路径: {SMALL_MODEL_PATH}")
        print(f"  - 小模型设备: {SMALL_MODEL_DEVICE}")
        print(f"  - 大模型API地址: {BIG_MODEL_API_BASE}")
        print(f"  - 大模型名称: {BIG_MODEL_NAME}")
        print(f"  - 大模型API密钥: {'已配置' if BIG_MODEL_API_KEY else '未配置（需要在.env中设置）'}")
        return True
    except Exception as e:
        print(f"✗ 配置模块加载失败: {e}")
        return False

def test_imports():
    """测试必要的库是否安装"""
    required_modules = {
        'streamlit': 'streamlit',
        'transformers': 'transformers',
        'torch': 'torch',
        'openai': 'openai',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"✓ {module} 已安装")
        except ImportError:
            print(f"✗ {module} 未安装 (需要: {package})")
            missing.append(package)
    
    if missing:
        print(f"\n请安装缺失的包:")
        print(f"  使用pip: pip install {' '.join(missing)}")
        print(f"  或使用conda: conda env create -f environment.yml")
        return False
    return True

def test_environment():
    """检测是否在conda环境中"""
    import os
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"✓ 当前在conda环境中: {conda_env}")
        if conda_env == 'ziyaoji':
            print("  (推荐的项目环境)")
        return True
    else:
        print("ℹ 当前不在conda环境中（使用系统Python）")
        return False

def main():
    print("=" * 60)
    print("校园问答调度系统 - 环境检查")
    print("=" * 60)
    print()
    
    print("1. 检查运行环境...")
    test_environment()
    
    print("\n2. 检查依赖包...")
    if not test_imports():
        print("\n请先安装所有依赖:")
        print("  使用pip: pip install -r requirements.txt")
        print("  使用conda: conda env create -f environment.yml")
        sys.exit(1)
    
    print("\n3. 检查配置...")
    if not test_config():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("环境检查完成！")
    print("=" * 60)
    print("\n提示:")
    print("  - 如果大模型API密钥未配置，请复制 .env.example 为 .env 并填写")
    print("  - 首次运行会下载小模型（约1.3GB），需要良好的网络连接")
    print("  - 运行应用: streamlit run app.py")

if __name__ == "__main__":
    main()
